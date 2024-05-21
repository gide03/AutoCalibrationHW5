import pyvisa as visa
import os
import serial
import pathlib
import time
import site
import click

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalibrationData import CalibrationRegister
from lib.Utils.Logger import getLogger

if not os.path.exists(f'{CURRENT_PATH}/logs'):
    os.mkdir(f'{CURRENT_PATH}/logs')

print('Please input meter ID. If empty program will terminated')
# meterId = input('Meter ID: ')
# if len(meterId) == 0:
    # exit('Calibration Canceled')
howMany = input('Test epoch: ')
howMany = int(howMany)

#
# Logger setup    
#
filename = f'{CURRENT_PATH}/logs/test_rtc_calibration _{howMany}x.log' 
logger = getLogger(filename)

class PendulumInstrument:
    INIT_COMMAND = (
        "*RST\n"
        "*CLS\n"
        ":INP:IMP 1E6\n",
        ":INP:LEV:AUTO ON\n",
        ":INP:COUP DC\n",
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
        self.sendInit()
    
    def sendInit(self):
        for data in self.INIT_COMMAND:
            self.selectedInstrument.write(data)
            time.sleep(0.1)    

    def read(self):        
        response = self.selectedInstrument.query(':MEASure:FREQuency:BURSt?\n', 1)
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



@click.command()
@click.option('--port', prompt="Enter serial port")
def main(port):
    logger.info('Init Instrument')
    instrument = PendulumInstrument()
    logger.info('Init Dlms Client')
    calibrationRegister = CalibrationRegister()
    meterSetupRegister = MeterSetup()
    ser_client = DlmsCosemClient(
        port=port,
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

    def test():
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
            df = meterSetupRegister.dataFrame() + ([0x00]*(109-meterSetupRegister.byteSize()))
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
                        # exit(1)
                        return 'Set meter setup FAILED'
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
            rtcCommand = [1, 0xF0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(0, 1):
                logger.info('Apply 4 Hz')
                result = ser_client.set_cosem_data(1, '0;128;96;14;82;255', 2, 9, rtcCommand)
            
            # READ FREQUENCY MEASUREMENT FROM INSTRUMENT
            sample = []
            measuredFreqValue = 0
            for i in range(5):
                try:
                    measuredFreqValue = instrument.read()
                except:
                    continue
                
                if 3.0 < measuredFreqValue and  measuredFreqValue < 4.05:
                    logger.info(f'Measured value: {measuredFreqValue}Hz')
                    sample.append(measuredFreqValue)
                    if len(sample) == 2:
                        break
                
            if len(sample) == 0:
                return 'Error when get instrument data'
            
            # CALCAULTE RTC GAIN
            frequencyAverage = sum(sample)/len(sample)
            logger.info(f'Measured rtc: {sample} -> Avg {frequencyAverage}Hz')
            RtcCalibrationValue = ( ( (frequencyAverage-4)/4) * 10**6 ) / 0.954
            RtcCalibrationValue = int(RtcCalibrationValue)
            logger.info(f'Set rtc calibration from {meterSetupRegister.RTCCalibration.value} to: {RtcCalibrationValue}')
            meterSetupRegister.RTCCalibration.value = RtcCalibrationValue
            
            # CALCULATE NEW CRC from new configuration
            logger.info('Calculating new CRC')
            meterSetupRegister.updateCRC(calibrationRegister)
            
            # SEND NEW METER SETUP
            retryAttemp = 3
            isMeterSetupOK = False
            for i in range(retryAttemp):
                try:
                    logger.info(f'Set register to meter setup result. Atemp {i+1} of {retryAttemp}')
                    result = ser_client.set_cosem_data(1, "0;128;96;14;81;255", 2, CosemDataType.e_OCTET_STRING, meterSetupRegister.dataFrame())
                    isMeterSetupOK = result
                    logger.debug(f'Result: {result}')
                    if result == 0:
                        logger.info(f'Set meter setup SUCCESS')
                        break
                    else:
                        logger.critical('Set meter setup FAILED')
                        # exit(1)
                        return 'Set meter setup FAILED'
                        
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
            # input('Press ENTER to Exit')
            
            if not os.path.exists(f'{CURRENT_PATH}/logs/rtc_calibration.csv'):
                f = open(f'{CURRENT_PATH}/logs/rtc_calibration.csv', 'w')
                f.write('meter id;measured frequency;RtcCalibrationValue;isMeterSetupOK;calibration gain readback\n')
            
            with open(f'{CURRENT_PATH}/logs/rtc_calibration.csv', 'a') as f:
                print(f'NA;{measuredFreqValue};{RtcCalibrationValue};{isMeterSetupOK};{meterSetupRegister.RTCCalibration.value}', file=f)
            
            return 'success'

    num_of_test = howMany
    num_of_success = 0
    num_of_fail = 0
    for testLoop in range(num_of_test):
        logger.info('='*30)
        logger.info(f'TEST #{testLoop+1}')
        logger.info('='*30)
        
        
        result = test()
        if result == 'success':
            num_of_success += 1
        else:
            num_of_fail += 1
            
    logger.info(f'TEST COMPLETE. NUM_OF_TEST: {num_of_test}, NUM_OF_SUCCESS: {num_of_success}, NUM_OF_FAIL: {num_of_fail}')

if __name__ == "__main__":
    main()