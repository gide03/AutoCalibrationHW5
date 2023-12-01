import serial
from lib.DLMS_Client import dlmsCosemUtil
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec
from lib.GENY.GENYApi import GENYClient, ElementSelector

import constant
import translator
import numpy as np
import time

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

class Ratio:
    def __init__(self, dlms_client:DlmsCosemClient, object:str, num_of_sample:int=3, threshold:int=0.99):
        '''
            Parameter perspective
        '''
        assert dlms_client.is_connected
        
        self.dlms_client = dlms_client
        self.object = object
        self.scalar = None
        self.value = []
        self.last_ratio = 0
        self.threshold = threshold
        self.num_of_sample = num_of_sample
        self.read_scalar()
        
        
    def read_scalar(self):
        assert self.dlms_client.is_connected
        
        if self.scalar != None:
            return
        data_read = self.dlms_client.get_cosem_data(3, self.object, 3)
        self.scalar = data_read
        
    def read_instant_value(self):
        assert self.dlms_client.is_connected
        
        return self.dlms_client.get_cosem_data(3, self.object, 2) * (10**self.scalar[0])
    
    def sampling_data(self):
        assert self.dlms_client.is_connected
        
        self.value = []
        for i in range(0, self.num_of_sample):
            data_read = self.dlms_client.get_cosem_data(3, self.object, 2)
            self.value.append(data_read)
    
    def get_mean(self):
        '''
            value and scalar shall be have the same keys and it's order
        '''
        normalize_value = np.array(self.value) * (10**self.scalar[0]) # NOTE: scalar data structure is [scalar, unit]
        normalize_value = float(normalize_value.mean())
        print(f"mean: {normalize_value} {type(normalize_value)}")
        return normalize_value
    
    def calculate_gain(self, reference:float, current_gain) -> tuple:
        '''
            param:
                reference is the value of actual data from test bench.
                current_gain is meter's gain correspond to self.object
            returns:
                tuple (gain value, is_dont_care)
        '''
        assert self.dlms_client.is_connected
        
        self.sampling_data()
        
        meter_measurement = self.get_mean()
        if meter_measurement == 0:
            return current_gain, False
        self.last_ratio = (reference*current_gain)/meter_measurement
        self.last_ratio = int(self.last_ratio)
        
        print(f"reference:{reference}, meter_measurement:{meter_measurement}, current_gain:{current_gain}, new gain calculation:{self.last_ratio}, error: {(reference-meter_measurement) / reference}")
        
        error_treshold = 1 - self.threshold
        error = (reference - meter_measurement) / reference
        print(f'acceptance error: {error_treshold}', end=' -- ')
        if abs(error) < error_treshold: # if the error near 0 then don't care calibration by passing the same gain value
            print('(PASSED)')
            return current_gain, False
        print('(NOPE)')
        return self.last_ratio, True

# UTILS
def read_calibration_data(dlms_client:DlmsCosemClient):    
    data_read = dlms_client.get_cosem_data(1, "0;128;96;14;80;255", 2)
    try:
        bytes(data_read).hex()
    except:
        print('error when read calibration data')
        print('data: ', data_read)
        print('retry to read')
        return read_calibration_data(dlms_client)
    
    output = translator.translate(data_read)
    return output
# end of UTILS 

def start_calibration():
    ser_client = DlmsCosemClient(
        port=constant.METER_SERIAL_PORT,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.3,
        inactivity_timeout=20,
        login_retry=1,
        meter_addr=commSetting.METER_ADDR,
        client_nb=commSetting.CLIENT_NUMBER,
    )
    
    # create geny client
    print('Initialize GENY')
    geny = GENYClient('10.23.40.32')
    # geny.set_serial('COM13') # refer to server serial port
    
    # turn on meter
    geny.calib_stop()
    time.sleep(3)
    print('Initialize GENY -- OK')
    geny.calib_testCMD(ElementSelector._COMBINE_ALL, 230.0, 5.0, 0.5, 50, 1000, 5)
    geny.calib_execute()
    BOOTING_TIME = 7
    print(f'Wait meter booting (HARD CODED {BOOTING_TIME} sec)')
    time.sleep(BOOTING_TIME) # wait meter for booting up
    
    # Login to meter
    print('Start calibrating')
    try:
        ser_client.client_logout()
    except:
        pass
    print('Login dlms')
    result = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
    
    # Create object list
    # Voltage
    InstantVoltagePhase1 = Ratio(ser_client, "1;0;32;7;0;255")
    InstantVoltagePhase2 = Ratio(ser_client, "1;0;52;7;0;255")
    InstantVoltagePhase3 = Ratio(ser_client, "1;0;72;7;0;255")
    
    # Current
    InstantCurrentPhase1 = Ratio(ser_client, "1;0;31;7;0;255")
    InstantCurrentPhase2 = Ratio(ser_client, "1;0;51;7;0;255")
    InstantCurrentPhase3 = Ratio(ser_client, "1;0;71;7;0;255")
    
    # # Power factor
    # PowerFactorImportPhase1 = Ratio(ser_client, "1;0;33;7;0;255")
    # PowerFactorImportPhase2 = Ratio(ser_client, "1;0;53;7;0;255")
    # PowerFactorImportPhase3 = Ratio(ser_client, "1;0;73;7;0;255")
    
    # Power Active
    InstantActivePowerPhase1 = Ratio(ser_client, "1;0;35;7;0;255")
    InstantActivePowerPhase2 = Ratio(ser_client, "1;0;55;7;0;255")
    InstantActivePowerPhase3 = Ratio(ser_client, "1;0;75;7;0;255")
    
    # # Power Reactive
    # PowerReactiveImportPhase1 = Ratio(ser_client, "1;0;23;7;0;255")
    # PowerReactiveImportPhase2 = Ratio(ser_client, "1;0;43;7;0;255")
    # PowerReactiveImportPhase3 = Ratio(ser_client, "1;0;63;7;0;255")
    
    # # Power Apparent
    # PowerApparentImportPhase1 = Ratio(ser_client, "1;0;29;7;0;255")
    # PowerApparentImportPhase2 = Ratio(ser_client, "1;0;49;7;0;255")
    # PowerApparentImportPhase3 = Ratio(ser_client, "1;0;69;7;0;255")
    
    instant_voltages = [
        # (Ratio instance, calibration parameter, geny feedback parameter)
        (InstantVoltagePhase1, "g_MQAcquisition.gainVrms[phaseA]", "Ua_amplitude"),
        (InstantVoltagePhase2, "g_MQAcquisition.gainVrms[phaseB]", "Ub_amplitude"),
        (InstantVoltagePhase3, "g_MQAcquisition.gainVrms[phaseC]", "Uc_amplitude"),
        (InstantCurrentPhase1, 'g_MQAcquisition.gainIrms[phaseA]', "Ia_amplitude"),
        (InstantCurrentPhase2, 'g_MQAcquisition.gainIrms[phaseB]', "Ib_amplitude"),
        (InstantCurrentPhase3, 'g_MQAcquisition.gainIrms[phaseC]', "Ic_amplitude"),
        # (PowerFactorImportPhase1, ),
        # (PowerFactorImportPhase2, ),
        # (PowerFactorImportPhase3, ),
        (InstantActivePowerPhase1, "g_MQAcquisition.gainActiveE[phaseA]", "Pa"),
        (InstantActivePowerPhase2, "g_MQAcquisition.gainActiveE[phaseB]", "Pb"),
        (InstantActivePowerPhase3, "g_MQAcquisition.gainActiveE[phaseC]", "Pc"),
        # (PowerReactiveImportPhase1, ),
        # (PowerReactiveImportPhase2, ),
        # (PowerReactiveImportPhase3, ),
        # (PowerApparentImportPhase1, ),
        # (PowerApparentImportPhase2, ),
        # (PowerApparentImportPhase3, ),
    ]
    
    is_debug = False
    if is_debug:
        for i in range(5):
            for register in instant_voltages:
                reg, _calib_parameter, _feedback_parameter = register
                value = reg.read_instant_value()
                print(f'Get meter measurement of {reg.object}: {value}')
            print()
            
    else:                  
        t0_measurement = [] # measurement before calibration
        t1_measurement = [] # measurement after calibration
        
        LOOPS = 1
        for i in range(LOOPS):
            t0_measurement = []
            t1_measurement = []
            is_calibrated = []
            
            print(f'Trial {i+1} of {LOOPS}')
            gain_value = read_calibration_data(ser_client)
            
            for register_object, gain_key, feedback_key in instant_voltages:                
                # Get instant value
                instant_value =register_object.read_instant_value()
                t0_measurement.append(instant_value)
                
                print(f'Calculate {gain_key}')
                feedback_data = geny.calib_readMeasurement()
                
                #Read geny feedback programmatically and feed to register object
                gain, is_calibrate = register_object.calculate_gain(
                    feedback_data[feedback_key], 
                    gain_value[gain_key]
                )
                if not is_calibrate:
                    is_calibrated.append(False)
                    continue
                is_calibrated.append(True)
                print(f"Set {gain_key}: {gain}")
                gain_value[gain_key] = gain            
                
            print(f'Send calibration gain data')
            calibration_data = translator.translate(gain_value, to_bytes=True)
            result = ser_client.set_cosem_data(1, "0;128;96;14;80;255", 2, dlmsCosemUtil.cosemDataType.octet_string, calibration_data)
            print(f'Result: {result}\n')
            
            for register_object, gain_key, feedback_key in instant_voltages:
                # Get instant value after calibration
                instant_value =register_object.read_instant_value()
                t1_measurement.append(instant_value)
            
            print('\nCompare instant value before and after calibration')
            for prev, after, calibrated in zip(t0_measurement, t1_measurement, is_calibrated):
                print(f'{register_object.object} measurement before->after calibration: {prev}->{after} ({"*" if calibrated else ""})')
            
        ser_client.client_logout()

if __name__ == "__main__":
    start_calibration()
