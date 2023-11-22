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
    def __init__(self, dlms_client:DlmsCosemClient, object:str, num_of_sample:int=3, threshold:int=0.97):
        self.dlms_client = dlms_client
        self.object = object
        self.scalar = None
        self.value = []
        self.last_ratio = 0
        self.threshold = threshold
        self.num_of_sample = num_of_sample
        
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
        normalize_value = (np.array(self.value) * (10**self.scalar[0])) # NOTE: scalar data structure is [scalar, unit]
        normalize_value = normalize_value.mean()
        return normalize_value
    
    def calculate_gain(self, reference:float, current_gain):
        '''
            param:
                reference is the value of actual data from test bench.
                current_gain is meter's gain correspond to self.object
        '''
        assert self.dlms_client.is_connected
        
        self.read_scalar()
        self.read_value()
        
        current_mesurement = self.get_mean()
        if current_mesurement == 0:
            return current_gain
        self.last_ratio = reference/current_mesurement * current_gain
        
        print(reference, current_mesurement, current_gain, self.last_ratio)
        
        error_treshold = 1 - self.threshold
        error = (reference - current_mesurement) / reference
        if abs(error) < error_treshold: # if the error near 0 then don't care calibration by passing the same gain value
            return current_gain
        return self.last_ratio

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
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=commSetting.METER_ADDR,
        client_nb=commSetting.CLIENT_NUMBER,
    )
    
    # Login to meter
    ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
    
    InstantVoltagePhase1 = Ratio(ser_client, "1;0;32;7;0;255")
    InstantVoltagePhase2 = Ratio(ser_client, "1;0;52;7;0;255")
    InstantVoltagePhase3 = Ratio(ser_client, "1;0;72;7;0;255")
    
    instant_voltages = [InstantVoltagePhase1, InstantVoltagePhase2, InstantVoltagePhase3]
    voltage_gain_key = ["g_MQAcquisition.gainVrms[phaseA]", "g_MQAcquisition.gainVrms[phaseB]", "g_MQAcquisition.gainVrms[phaseC]"]
    
    for i in range(1):
        gain_value = read_calibration_data(ser_client)
        print(gain_value['g_MQAcquisition.gainVrms[phaseA]'])
        
        for register_object, gain_key in zip(instant_voltages, voltage_gain_key):
            gain = register_object.calculate_gain(230.0, gain_value[gain_key])
            gain_value[gain_key] = gain
            print(register_object.object, gain)
                        
        # gain = InstantVoltagePhase1.calculate_gain(230.0, gain_value['g_MQAcquisition.gainVrms[phaseA]'])
        # print('SHOW GAIN')
        # print(gain)

        print(gain_value['g_MQAcquisition.gainVrms[phaseA]'])
        gain_data = translator.translate(gain_value, to_bytes=True)
        print(gain_data)
            
    ser_client.client_logout()

if __name__ == "__main__":
    start_calibration()
