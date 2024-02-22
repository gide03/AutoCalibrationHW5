import pyvisa as visa
import os
import logging
import serial
import pathlib
import time

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()

from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalibrationData import CalibrationRegister


METER_USB_PORT = "com4"


if not os.path.exists(f'{CURRENT_PATH}/logs'):
    os.mkdir(f'{CURRENT_PATH}/logs')

print('Please input meter ID. If empty program will terminated')
meterId = input('Meter ID: ')
if len(meterId) == 0:
    exit('Calibration Canceled')

#
# Logger setup    
#
filename = f'{CURRENT_PATH}/logs/{meterId} rtc_calibration.log' 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.DEBUG)
# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# End of LOGGER  Configuration

class FrequencyCounterInstrument:
    INIT_COMMAND = (
        "*RST\n"
        "*CLS\n"
        # ":INP:IMP 1E6\n",
        # ":INP:LEV:AUTO ON\n",
        ":INP:COUP DC\n",
        ":INP:NREJ ON\n"
        # ":INP2:IMP 1E6\n",
        # ":INP2:LEV:AUTO ON\n",
        # ":INP2:COUP DC\n",
    )
    
    def __init__(self):
        self.rm = visa.ResourceManager()
        print('searching instrument')
        self.instrument_list = self.rm.list_resources()
        # print(f'instrument list: {self.instrument_list}')
        
        self.selectedInstrument = ''
        for instrument in self.instrument_list:
            if 'USB' in instrument:
                print('Found instrument')
                print(f'Applying {instrument}')
                self.selectedInstrument = self.rm.open_resource(instrument)
                break
        if self.selectedInstrument == '':
            raise Exception('No instrument detected. Please check the connection')
        # instrument_info = rm.resource_info('USB0::0x14EB::0x0090::389645::INSTR')
        # self.instrument = self.rm.open_resource('USB0::0x14EB::0x0090::389645::INSTR')
        # print(instrument_info)
        # self.sendInit()
        
    
    def sendInit(self):
        for data in self.INIT_COMMAND:
            self.selectedInstrument.write(data)
            time.sleep(0.1)    

    def read(self):
        self.selectedInstrument.write('*CLS\n')
        response = self.selectedInstrument.query('MEASure:FREQuency?', delay=2)
        # print(f'read response: {response}')
        return float(response)
    
class commSetting:
    METER_ADDR = 100
    CLIENT_NUMBER = 0x73
    AUTH_KEY = "wwwwwwwwwwwwwwww"
    GUEK = "30303030303030303030303030303030"
    GAK = "30303030303030303030303030303030"
    SYS_TITLE = "4954453030303030"
    # For HW 5
    USE_RLRQ = True
    IS_RLRQ_PROTECTED = True

logger.info('Init Instrument')
instrument = FrequencyCounterInstrument()
logger.info('Init Dlms Client')
calibrationRegister = CalibrationRegister()
meterSetupRegister = MeterSetup()
ser_client = DlmsCosemClient(
    port=METER_USB_PORT,
    baudrate=19200,
    parity=serial.PARITY_NONE,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.05,
    inactivity_timeout=10,
    login_retry=1,
    meter_addr=commSetting.METER_ADDR,
    client_nb=commSetting.CLIENT_NUMBER,
)

def calRunningCRC16(dataFrame):
    lCrc = 0xffff
    
    for dataIdx in range(0, len(dataFrame)):
        data = dataFrame[dataIdx]
        lCrc = lCrc ^ (data << 8)
        for i in range(0,8):
            if (lCrc & 0x8000):
                lCrc = (lCrc << 1) ^ 0x1021
            else:
                lCrc <<= 1
        lCrc &= 0xffff
    return lCrc

ser_client.client_logout()
if ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL):
    logger.info('Reading fw version')
    fwVersion = ser_client.get_cosem_data(1, '1;0;0;2;0;255', 2)
    logger.info(f'Firmware Version: {bytes(fwVersion).decode("utf-8")}')
    
    logger.info('Fetching calibration register')
    result = ser_client.get_cosem_data(1, "0;128;96;14;80;255", 2)
    calibrationRegister.extract(result)
    
    logger.info('Fetching meter setup register')
    result = ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
    meterSetupRegister.extract(result)
    
    # SET RTC CALIBRATION TO DEFAULT
    meterSetupRegister.RTCCalibration.value = 0
    configurationData = calibrationRegister.dataFrame()
    configurationData.extend(meterSetupRegister.dataFrame())
    for i in range(2): #Pop CRC
        configurationData.pop(-1)
    newCRC = calRunningCRC16(configurationData)
    meterSetupRegister.CRC.value = newCRC
    df = meterSetupRegister.dataFrame()
    retryAttemp = 3
    isMeterSetupOK = False
    for i in range(retryAttemp):
        try:
            logger.info(f'Set register to meter setup result to default. Atemp {i+1} of {retryAttemp}')
            result = ser_client.set_cosem_data(1, "0;128;96;14;81;255", 2, 9, df)
            isMeterSetupOK = result
            logger.debug(f'Result: {result}')
            if result == 0:
                logger.info(f'Default set SUCCESS')
                break
            else:
                logger.critical('Set meter setup FAILED')
                exit(1)
        except:
            if i<retryAttemp-1:
                logger.debug('Timeout. Retry process')
                ser_client.client_logout()
                ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
                meterRegister = ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
                if meterRegister == df:
                    logger.debug('Meter configuration is already saved by the meter')
                    break
            pass
    
    # TRANSMIT RTC
    RtcCalibrationValue = 0
    for i in range(3):
        rtcCommand = [1, 0xFF, 0x10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(0, 1):
            logger.info('Apply 4 Hz')
            result = ser_client.set_cosem_data(1, '0;128;96;14;82;255', 2, 9, rtcCommand)
        # time.sleep(0.5) # give a moment for instrument to read frequency
        instrument.sendInit()
        
        # READ FREQUENCY MEASUREMENT FROM INSTRUMENT
        sample = []
        measuredFreqValue = 0
        for i in range(10):
            try:
                measuredFreqValue = instrument.read()
                if 3.0 < measuredFreqValue and  measuredFreqValue < 5:
                    if i == 0:  # in case the first measurement is invalid
                        continue
                    logger.info(f'Measured value: {measuredFreqValue}Hz')
                    sample.append(measuredFreqValue)
                    time.sleep(1)
                    
                if len(sample) == 2:
                    break
            except:
                pass
            
        if len(sample) == 0:
            logger.critical('Error when get instrument data')
            exit('Error when get instrument data')
        
        # CALCAULTE RTC GAIN
        frequencyAverage = sum(sample)/len(sample)
        logger.info(f'Measured rtc: {sample} -> Avg {frequencyAverage}Hz')
        RtcCalibrationValue = ( ( (frequencyAverage-4)/4) * 10**6 ) / 0.954
        RtcCalibrationValue = int(RtcCalibrationValue)
        logger.debug(f'Calculate RTC Calibration Value: {RtcCalibrationValue}')
        
        if -50 <= RtcCalibrationValue and RtcCalibrationValue <= 50:
            logger.info(f'Set rtc calibration from {meterSetupRegister.RTCCalibration.value} to: {RtcCalibrationValue}')
            break
        logger.debug(f'PPM not acceptable, Recalculate')
        if i == 3:
            logger.critical(f'RTC REJECT :(')
            ser_client.client_logout()
            exit()        
    meterSetupRegister.RTCCalibration.value = RtcCalibrationValue
    
    # CALCULATE NEW CRC from new configuration
    logger.info('Calculating new CRC')
    configurationData = calibrationRegister.dataFrame()
    configurationData.extend(meterSetupRegister.dataFrame())
    for i in range(2): #Pop CRC
        configurationData.pop(-1)
    newCRC = calRunningCRC16(configurationData)
    meterSetupRegister.CRC.value = newCRC 
    
    # SEND NEW METER SETUP
    df = meterSetupRegister.dataFrame()
    retryAttemp = 3
    isMeterSetupOK = False
    for i in range(retryAttemp):
        try:
            logger.info(f'Set register to meter setup result. Atemp {i+1} of {retryAttemp}')
            result = ser_client.set_cosem_data(1, "0;128;96;14;81;255", 2, 9, df)
            isMeterSetupOK = result
            logger.debug(f'Result: {result}')
            if result == 0:
                logger.info(f'Set meter setup SUCCESS')
                break
            else:
                logger.critical('Set meter setup FAILED')
                exit(1)
                
        except:
            if i<retryAttemp-1:
                logger.debug('Timeout. Retry process')
                ser_client.client_logout()
                ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
                meterRegister = ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
                if meterRegister == df:
                    logger.debug('Meter configuration is already saved by the meter')
                    break
            pass
    
    # VERIFY DATA
    verifyData = ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
    meterSetupRegister.extract(verifyData)
    ser_client.client_logout()
    logger.info('RTC Calibration is finished')
    input('Press ENTER to Exit')
    
    if not os.path.exists(f'{CURRENT_PATH}/logs/rtc_calibration.csv'):
        f = open(f'{CURRENT_PATH}/logs/rtc_calibration.csv', 'w')
        f.write('meter id;measured frequency;RtcCalibrationValue;isMeterSetupOK;calibration gain readback\n')
    
    with open(f'{CURRENT_PATH}/logs/rtc_calibration.csv', 'a') as f:
        print(f'{meterId};{measuredFreqValue};{RtcCalibrationValue};{isMeterSetupOK};{meterSetupRegister.RTCCalibration.value}', file=f)