import serial
from lib.DLMS_Client import dlmsCosemUtil
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec

import constant
import translator
import numpy as np
import copy

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
    def __init__(self, dlms_client:DlmsCosemClient, object:str, num_of_sample:int=3, threshold:int=0.991):
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
    
    def read_value(self):
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
        
        self.read_value()
        
        meter_measurement = self.get_mean()
        if meter_measurement == 0:
            return current_gain
        self.last_ratio = reference/meter_measurement * current_gain
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
    
    # Login to meter
    ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
    # ser_client.client_logout()
    # return
    
    # Create object list
    # Voltage
    InstantVoltagePhase1 = Ratio(ser_client, "1;0;32;7;0;255")
    InstantVoltagePhase2 = Ratio(ser_client, "1;0;52;7;0;255")
    InstantVoltagePhase3 = Ratio(ser_client, "1;0;72;7;0;255")
    
    # # Current
    # InstantCurrentPhase1 = Ratio(ser_client, "1;0;31;7;0;255")
    # InstantCurrentPhase2 = Ratio(ser_client, "1;0;51;7;0;255")
    # InstantCurrentPhase3 = Ratio(ser_client, "1;0;71;7;0;255")
    
    # # Power factor
    # PowerFactorImportPhase1 = Ratio(ser_client, "1;0;33;7;0;255")
    # PowerFactorImportPhase2 = Ratio(ser_client, "1;0;53;7;0;255")
    # PowerFactorImportPhase3 = Ratio(ser_client, "1;0;73;7;0;255")
    
    # # Power Active
    # InstantActivePowerPhase1 = Ratio(ser_client, "1;0;35;7;0;255")
    # InstantActivePowerPhase2 = Ratio(ser_client, "1;0;55;7;0;255")
    # InstantActivePowerPhase3 = Ratio(ser_client, "1;0;75;7;0;255")
    
    # # Power Reactive
    # PowerReactiveImportPhase1 = Ratio(ser_client, "1;0;23;7;0;255")
    # PowerReactiveImportPhase2 = Ratio(ser_client, "1;0;43;7;0;255")
    # PowerReactiveImportPhase3 = Ratio(ser_client, "1;0;63;7;0;255")
    
    # # Power Apparent
    # PowerApparentImportPhase1 = Ratio(ser_client, "1;0;29;7;0;255")
    # PowerApparentImportPhase2 = Ratio(ser_client, "1;0;49;7;0;255")
    # PowerApparentImportPhase3 = Ratio(ser_client, "1;0;69;7;0;255")
    
    instant_voltages = [
        (InstantVoltagePhase1, "g_MQAcquisition.gainVrms[phaseA]"),
        (InstantVoltagePhase2, "g_MQAcquisition.gainVrms[phaseB]"),
        (InstantVoltagePhase3, "g_MQAcquisition.gainVrms[phaseC]"),
        # (InstantCurrentPhase1, 'g_MQAcquisition.gainIrms[phaseA]'),
        # (InstantCurrentPhase2, 'g_MQAcquisition.gainIrms[phaseB]'),
        # (InstantCurrentPhase3, 'g_MQAcquisition.gainIrms[phaseC]'),
        # (PowerFactorImportPhase1, ),
        # (PowerFactorImportPhase2, ),
        # (PowerFactorImportPhase3, ),
        # (InstantActivePowerPhase1, ),
        # (InstantActivePowerPhase2, ),
        # (InstantActivePowerPhase3, ),
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
            InstantVoltagePhase1.read_value()
            print(f'Get meter measurement: {InstantVoltagePhase1.get_mean()}')
            
    else:
        import json
        for i in range(2):
            print('Trial ',i+1,' of 3')
            gain_value = read_calibration_data(ser_client)
            for gain_key in gain_value:
                print(f'{gain_key}: {gain_value[gain_key]}')            
            calibration_data = translator.translate(gain_value, True)
            print(json.dumps(gain_value,indent=1))
            print(calibration_data)
            break
            for instant_register in instant_voltages:
                register_object, gain_key = instant_register
                print(f'Calculate {gain_key}')
                gain, is_calibrate = register_object.calculate_gain(230.0, gain_value[gain_key]) #TODO: Read geny feedback programmatically
                if not is_calibrate: 
                    continue
                print(f"Set {gain_key}: {gain}")
                gain_value[gain_key] = gain
            
            gain_value['Phase Delay[PhaseA]'] = 0
            gain_value['Phase Delay[PhaseB]'] = 0
            gain_value['Phase Delay[PhaseC]'] = 0
            gain_value['Phase Delay[PhaseN]'] = 0
            gain_value['Phase Direction[PhaseN]'] = 1
            
            
            print('\nSUMMARY')
            for gain_key in gain_value:
                print(f'{gain_key}: {gain_value[gain_key]}')            
            calibration_data = translator.translate(gain_value, True)
            import json
            with open('./calibration_params.json', 'w') as f:
                json.dump(gain_value, f)
            print(f'Send calibration gain data')
            result = ser_client.set_cosem_data(1, "0;128;96;14;80;255", 2, dlmsCosemUtil.cosemDataType.octet_string, calibration_data)
            print(f'Result: {result}\n')
                            
            # gain = InstantVoltagePhase1.calculate_gain(230.0, gain_value['g_MQAcquisition.gainVrms[phaseA]'])
            # print('SHOW GAIN')
            # print(gain)
            
    ser_client.client_logout()

if __name__ == "__main__":
    start_calibration()
