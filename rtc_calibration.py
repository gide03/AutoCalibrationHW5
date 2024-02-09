import pyvisa as visa
import os
import logging
import serial
import pathlib
import sys
import time

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()

from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec

from ConfigurationRegister import Register, RegisterWrapper


METER_USB_PORT = "COM31"


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
        print('searching instrument')
        self.instrument_list = self.rm.list_resources()
        print(f'instrument list: {self.instrument_list}')
        
        self.selectedInstrument = ''
        for instrument in self.instrument_list:
            if 'USB' in instrument:
                self.selectedInstrument = self.rm.open_resource(instrument)
                break
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
        self.selectedInstrument.write(":MEASure:FREQuency?\n")
        response = self.selectedInstrument.read()
        print(type(response))
        print(float(response[:-1]))
            
            
        # instrument.close()
        
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

def fetch_calibration_data(verbose = False):
    logger.info('read calibration data')
    data_read = ser_client.get_cosem_data(1, "0;128;96;14;80;255", 2)  
    calibrationRegister.extract(data_read)
    if verbose == True:
        calibrationRegister.info()

calibrationRegister = CalibrationRegister()
instrument = FrequencyCounterInstrument()
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

ser_client.client_logout()
if ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL):
    logger.info('Reading fw version')
    
    fwVersion = ser_client.get_cosem_data(1, '1;0;0;2;0;255', 2)
    logger.info(f'Firmware Version: {bytes(fwVersion).decode("utf-8")}')
    
    logger.info('Fetching calibration register')
    calibrationData = ser_client.get_cosem_data(1, "0;128;96;14;80;255", 2)  
    calibrationRegister.extract(calibrationData)
    
    rtcCommand = [1, 180, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    result = ser_client.set_cosem_data(1, '0;128;96;14;82;255', 2, 9, rtcCommand)
    logger.info(f'Transmit RTC -- {result}')
    logger.debug(f'Meter shall be show 4Hz signal')
    
    for i in range(20):
        try:
            value = instrument.read()
            print(value)
        except:
            pass
    
    ser_client.client_logout()
# except:
#     pass
# TODO 1: Login dlms

# TODO 2: Setup DATA ini 01 b4 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ke object ?Tanya vian
# TODO 3: Read instrument data
# TODO 4: Read initial calibration regiter
# TODO 5: Calculate new gain
# TODO 6: Send gain and verify
# TODO 7: Logout dlms