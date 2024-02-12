import pyvisa as visa
import os
import logging
import serial
import pathlib
import time

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()

from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec

from ConfigurationRegister import Register, RegisterWrapper


METER_USB_PORT = "/dev/ttyUSB0"


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
        ":INP:IMP 1E6\n",
        ":INP2:IMP 1E6\n",
        ":INP:LEV:AUTO ON\n",
        ":INP2:LEV:AUTO ON\n",
        ":INP:COUP DC\n",
        ":INP2:COUP DC\n",
    )
    
    def __init__(self):
        self.rm = visa.ResourceManager()
        logger.debug('searching instrument')
        self.instrument_list = self.rm.list_resources()
        logger.debug(f'instrument list: {self.instrument_list}')
        
        self.selectedInstrument = ''
        for instrument in self.instrument_list:
            if 'USB' in instrument:
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
            print(f'Send {data}')
            self.selectedInstrument.write(data)
            try:
                response = self.selectedInstrument.read()
                print(response, type(response))
                return response
            except:
                pass
    

    def read(self):
        # for data in self.INIT_COMMAND:
        #     self.selectedInstrument.write(data)
        #     try:
        #         response = self.selectedInstrument.read()
        #         print(response, type(response))
        #         return response
        #     except:
        #         pass
        self.selectedInstrument.write(":MEASure:FREQuency:BURSt?\n")
        response = self.selectedInstrument.read()
        # print(type(response))
        return float(response[:-1])
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

class CalibrationRegister(RegisterWrapper):
    def __init__(self):
        self.GainActiveE_A = Register('GainActiveE_A', 'uint16')
        self.GainActiveE_B = Register('GainActiveE_B', 'uint16')
        self.GainActiveE_C = Register('GainActiveE_C', 'uint16')
        self.GainReactiveE_A = Register('GainReactiveE_A', 'uint16')
        self.GainReactiveE_B = Register('GainReactiveE_B', 'uint16')
        self.GainReactiveE_C = Register('GainReactiveE_C', 'uint16')
        self.GainIrms_A = Register('GainIrms_A', 'uint16')
        self.GainIrms_B = Register('GainIrms_B', 'uint16')
        self.GainIrms_C = Register('GainIrms_C', 'uint16')
        self.GainIrms_N = Register('GainIrms_N', 'uint16')
        self.GainVrms_A = Register('GainVrms_A', 'uint16')
        self.GainVrms_B = Register('GainVrms_B', 'uint16')
        self.GainVrms_C = Register('GainVrms_C', 'uint16')
        self.FilterK1PhA = Register('FilterK1PhA', 'int16')
        self.FilterK2PhA = Register('FilterK2PhA', 'int16')
        self.FilterK3PhA = Register('FilterK3PhA', 'int16')
        self.FilterK1PhB = Register('FilterK1PhB', 'int16')
        self.FilterK2PhB = Register('FilterK2PhB', 'int16')
        self.FilterK3PhB = Register('FilterK3PhB', 'int16')
        self.FilterK1PhC = Register('FilterK1PhC', 'int16')
        self.FilterK2PhC = Register('FilterK2PhC', 'int16')
        self.FilterK3PhC = Register('FilterK3PhC', 'int16')
        self.FilterGainSlope = Register('FilterGainSlope', 'int16')
        self.TempK1V = Register('TempK1V', 'int16')
        self.TempK2V = Register('TempK2V', 'int16')
        self.TempK3V = Register('TempK3V', 'int16')
        self.TempK1I = Register('TempK1I', 'int16')
        self.TempK2I = Register('TempK2I', 'int16')
        self.TempK3I = Register('TempK3I', 'int16')
        self.TempK1ShiftVolt = Register('TempK1ShiftVolt', 'uint8')
        self.TempK2ShiftVolt = Register('TempK2ShiftVolt', 'uint8')
        self.TempK3ShiftVolt = Register('TempK3ShiftVolt', 'uint8')
        self.TempK1ShiftCurr = Register('TempK1ShiftCurr', 'uint8')
        self.TempK2ShiftCurr = Register('TempK2ShiftCurr', 'uint8')
        self.TempK3ShiftCurr = Register('TempK3ShiftCurr', 'uint8')
        self.NonLinearK1 = Register('NonLinearK1', 'int16')
        self.NonLinearK2 = Register('NonLinearK2', 'int16')
        self.NonLinearK3 = Register('NonLinearK3', 'int16')
        self.NonLinearK4 = Register('NonLinearK4', 'int16')
        self.NonLinearK5 = Register('NonLinearK5', 'int16')
        self.NonLinearK6 = Register('NonLinearK6', 'int16')
        self.NonLinearK7 = Register('NonLinearK7', 'uint16')
        self.NonLinearBreakCurr0 = Register('NonLinearBreakCurr0', 'uint16')
        self.NonLinearBreakCurr1 = Register('NonLinearBreakCurr1', 'uint16')
        self.NonLinearK1Shift = Register('NonLinearK1Shift', 'uint8')
        self.NonLinearK2Shift = Register('NonLinearK2Shift', 'uint8')
        self.NonLinearK3Shift = Register('NonLinearK3Shift', 'uint8')
        self.NonLinearK4Shift = Register('NonLinearK4Shift', 'uint8')
        self.NonLinearK5Shift = Register('NonLinearK5Shift', 'uint8')
        self.NonLinearK6Shift = Register('NonLinearK6Shift', 'uint8')
        self.VrmsSlope = Register('VrmsSlope', 'int16')
        self.VrmsOffset = Register('VrmsOffset', 'uint16')
        self.Cal_Temperature = Register('Cal_Temperature', 'int16')
        self.ActualTemperature = Register('ActualTemperature', 'int16')
        self.PhDirectionA = Register('PhDirectionA', 'int8')
        self.PhDirectionB = Register('PhDirectionB', 'int8')
        self.PhDirectionC = Register('PhDirectionC', 'int8')
        self.PhDirectionN = Register('PhDirectionN', 'int8')
        self.PhaseDelayA = Register('PhaseDelayA', 'uint16')
        self.PhaseDelayB = Register('PhaseDelayB', 'uint16')
        self.PhaseDelayC = Register('PhaseDelayC', 'uint16')
        self.PhaseDelayN = Register('PhaseDelayN', 'uint16')
        self.FrequencyWindow = Register('FrequencyWindow', 'uint8')
        self.Wh_Offset_A = Register('Wh_Offset_A', 'int16')
        self.Wh_Offset_B = Register('Wh_Offset_B', 'int16')
        self.Wh_Offset_C = Register('Wh_Offset_C', 'int16')
        self.Varh_Offset_A = Register('Varh_Offset_A', 'int16')
        self.Varh_Offset_B = Register('Varh_Offset_B', 'int16')
        self.Varh_Offset_C = Register('Varh_Offset_C', 'int16')
        
        # Aditional for version 2
        self.tf_control = Register('tf_control', 'uint32')
        self.tf_coeff_a0 = Register('tf_coeff_a0', 'int32')
        self.tf_coeff_a1 = Register('tf_coeff_a1', 'int32')
        self.tf_coeff_a2 = Register('tf_coeff_a2', 'int32')
        self.tf_coeff_a3 = Register('tf_coeff_a3', 'int32')
        self.tf_coeff_b1 = Register('tf_coeff_b1', 'int32')
        self.tf_coeff_b2 = Register('tf_coeff_b2', 'int32')
        self.tf_coeff_b3 = Register('tf_coeff_b3', 'int32')

class MeterSetup(RegisterWrapper):
    def __init__(self):
        self.CalibratiOndateTime = Register('CalibratiOndateTime', 'uint32')
        self.MeterForm = Register('MeterForm', 'uint8')
        self.MeterClass = Register('MeterClass', 'uint8')
        self.FrequencySelection = Register('FrequencySelection', 'uint8')
        self.MeterType = Register('MeterType', 'uint8')
        self.MeterVoltageType = Register('MeterVoltageType', 'uint8')
        self.MeterPowerSupplyType = Register('MeterPowerSupplyType', 'uint8')
        self.ServicesenseMode = Register('ServicesenseMode', 'uint8')
        self.VACalculatiOnConfig = Register('VACalculatiOnConfig', 'uint8')
        self.WattCalculatiOnConfig = Register('WattCalculatiOnConfig', 'uint8')
        self.VARCalculatiOnConfig = Register('VARCalculatiOnConfig', 'uint8')
        self.LED1PulseWeight = Register('LED1PulseWeight', 'uint16')
        self.LED1PulseOnTime = Register('LED1PulseOnTime', 'uint16')
        self.LED1PulseOffTime = Register('LED1PulseOffTime', 'uint16')
        self.LED1DebugData = Register('LED1DebugData', 'uint32')
        self.LED1Phase = Register('LED1Phase', 'uint8')
        self.LED1Direction = Register('LED1Direction', 'uint8')
        self.LED1Energy = Register('LED1Energy', 'uint8')
        self.LED1CreepEvent = Register('LED1CreepEvent', 'uint8')
        self.LED2PulseWeight = Register('LED2PulseWeight', 'uint16')
        self.LED2PulseOnTime = Register('LED2PulseOnTime', 'uint16')
        self.LED2PulseOffTime = Register('LED2PulseOffTime', 'uint16')
        self.LED2DebugData = Register('LED2DebugData', 'uint32')
        self.LED2Phase = Register('LED2Phase', 'uint8')
        self.LED2Direction = Register('LED2Direction', 'uint8')
        self.LED2Energy = Register('LED2Energy', 'uint8')
        self.LED2CreepEvent = Register('LED2CreepEvent', 'uint8')
        self.AnticreepConstant = Register('AnticreepConstant', 'uint16')
        self.AnticreepVoltage = Register('AnticreepVoltage', 'uint16')
        self.AnticreepTimer = Register('AnticreepTimer', 'uint32')
        self.ArcDetectiOnCounter = Register('ArcDetectiOnCounter', 'uint8')
        self.MagneticSensorXaxis = Register('MagneticSensorXaxis', 'int16')
        self.MagneticSensorYaxis = Register('MagneticSensorYaxis', 'int16')
        self.MagneticSensorZaxis = Register('MagneticSensorZaxis', 'int16')
        self.MagneticSensorNegXaxis = Register('MagneticSensorNegXaxis', 'int16')
        self.MagneticSensorNegYaxis = Register('MagneticSensorNegYaxis', 'int16')
        self.MagneticSensorNegZaxis = Register('MagneticSensorNegZaxis', 'int16')
        self.AccelerometerXaxis = Register('AccelerometerXaxis', 'int16')
        self.AccelerometerYaxis = Register('AccelerometerYaxis', 'int16')
        self.AccelerometerZaxis = Register('AccelerometerZaxis', 'int16')
        self.AccelerometerNegXaxis = Register('AccelerometerNegXaxis', 'int16')
        self.AccelerometerNegYaxis = Register('AccelerometerNegYaxis', 'int16')
        self.AccelerometerNegZaxis = Register('AccelerometerNegZaxis', 'int16')
        self.RTCCalibration = Register('RTCCalibration', 'int16')
        self.RTCTempCoeff = Register('RTCTempCoeff', 'int16')
        self.OpticalUartBaudrate = Register('OpticalUartBaudrate', 'uint8')
        self.DIUartBaudrate = Register('DIUartBaudrate', 'uint8')
        self.NICUartBaudrate = Register('NICUartBaudrate', 'uint8')
        self.ADCchannelNum = Register('ADCchannelNum', 'uint8')
        self.VaADCChannelMapping = Register('VaADCChannelMapping', 'uint8')
        self.IaADCChannelMapping = Register('IaADCChannelMapping', 'uint8')
        self.VbADCChannelMapping = Register('VbADCChannelMapping', 'uint8')
        self.IbADCChannelMapping = Register('IbADCChannelMapping', 'uint8')
        self.VcADCChannelMapping = Register('VcADCChannelMapping', 'uint8')
        self.IcADCChannelMapping = Register('IcADCChannelMapping', 'uint8')
        self.VauxADCChannelMapping = Register('VauxADCChannelMapping', 'uint8')
        self.IneutralADCChannelMapping = Register('IneutralADCChannelMapping', 'uint8')
        self.SLBMode = Register('SLBMode', 'uint8')
        self.BoardVersion = Register('BoardVersion', 'uint8')
        self.Reserved0 = Register('Reserved0', 'uint16')
        self.Reserved1 = Register('Reserved1', 'uint16')
        self.Reserved2 = Register('Reserved2', 'uint16')
        self.Reserved3 = Register('Reserved3', 'uint16')
        self.CRC = Register('CRC', 'uint16')

calibrationRegister = CalibrationRegister()
meterSetupRegister = MeterSetup()
ser_client = DlmsCosemClient(
    port=METER_USB_PORT,
    baudrate=19200,
    parity=serial.PARITY_NONE,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.3,
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
   
    rtcCommand = [1, 0xff, 0x0a, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    measuredFreqValue = []
    for i in range(0, 1):
        logger.info('Apply 4 Hz')
        result = ser_client.set_cosem_data(1, '0;128;96;14;82;255', 2, 9, rtcCommand)
    measuredFreqValue = input('Measured RTC: ')
    measuredFreqValue = float(measuredFreqValue)
    
    RtcCalibrationValue = ( ( (measuredFreqValue-4)/4) * 10**6 ) / 0.954
    RtcCalibrationValue = int(RtcCalibrationValue)
    logger.info(f'Set rtc calibration to: {RtcCalibrationValue}')
    meterSetupRegister.RTCCalibration.value = RtcCalibrationValue
    
    # CALCULATE NEW CRC from new configuration
    logger.info('Calculating new CRC')
    configurationData = calibrationRegister.dataFrame()
    configurationData.extend(meterSetupRegister.dataFrame())
    for i in range(2): #Pop CRC
        configurationData.pop(-1)
    newCRC = calRunningCRC16(configurationData)
    meterSetupRegister.CRC.value = newCRC 
    
    df = meterSetupRegister.dataFrame() + ([0x00]*(109-meterSetupRegister.byteSize()))
    retryAttemp = 3
    for i in range(retryAttemp):
        try:
            logger.info(f'Set register to meter setup result. Atemp {i+1} of {retryAttemp}')
            result = ser_client.set_cosem_data(1, "0;128;96;14;81;255", 2, 9, df)
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
    
    verifyData = ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
    meterSetupRegister.extract(verifyData)
    meterSetupRegister.info()
    ser_client.client_logout()

    logger.info('RTC Calibration is completed')
    input('Press ENTER to Exit')