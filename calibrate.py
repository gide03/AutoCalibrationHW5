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

# UTILS
def read_scalar(dlms_client:DlmsCosemClient, object_list:list)->dict: # the register shall be class id 3
    output = {}
    for obj in object_list:
        data_read = dlms_client.get_cosem_data(3, obj, 3)
        output[obj] = data_read
    return output

def read_value(dlms_client:DlmsCosemClient, object_list:list, epoch:int=5)->dict: # the register shall be class id 3
    output = {}
    for obj in object_list:
        output[obj] = []
        
        for i in range(epoch):
            data_read = dlms_client.get_cosem_data(3, obj, 2)
            output[obj].append(data_read)
    
    return output

def apply_scalar(value:dict, scalar:dict):
    '''
        value and scalar shall be have the same keys and it's order
    '''
    _value = {}
    for key in value:
        _value[key] = np.array(value[key]) * scalar[key][0] # NOTE: scalar data structure is [scalar, unit]
    print(_value)
    return _value
        
def read_calibration_data(dlms_client:DlmsCosemClient):
    data_read = dlms_client.get_cosem_data(1, "0;128;96;14;80;255", 2)
    output = translator.translate(data_read)
    print(output)
    
    # print(dlms_client.set_cosem_data(1, "0;128;96;14;80;255", 2, 9, data_read))
    return data_read
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
    # read_calibration_data(ser_client)
        
    # TODO 4: Pembacaan voltage RMS setiap detik, 5 kali, nilai disimpan
    print('4: Pembacaan voltage RMS setiap detik, 5 kali, nilai disimpan')
    V_rms_objects = ["1;0;32;7;0;255", "1;0;52;7;0;255", "1;0;72;7;0;255"]
    voltage_rms_value = read_value(ser_client, V_rms_objects, 5)
    voltage_rms_scalar = read_scalar(ser_client, V_rms_objects)
    print(voltage_rms_value)
    print(voltage_rms_scalar)
    print(apply_scalar(voltage_rms_value, voltage_rms_scalar))

    # TODO 6: Pembacaan arus RMS setiap detik, 5 kali, nilai disimpan
    print('6: Pembacaan arus RMS setiap detik, 5 kali, nilai disimpan')
    I_rms_objects = ["1;0;31;7;0;255", "1;0;51;7;0;255", "1;0;71;7;0;255"]
    current_rms_value = read_value(ser_client, I_rms_objects, 5)
    # current_rms_scalar = read_scalar(ser_client, I_rms_objects)
    print(current_rms_value)
    print()

    # TODO 8: Pembacaan nilai active power setiap detik, 5 kali, nilai disimpan
    print('8: Pembacaan nilai active power setiap detik, 5 kali, nilai disimpan')
    P_rms_objects = ["1;0;35;7;0;255", "1;0;55;7;0;255", "1;0;75;7;0;255"]
    activePower_rms_value = read_value(ser_client, P_rms_objects, 5)
    # activePower_rms_scalar = read_scalar(ser_client, P_rms_objects)
    print(activePower_rms_value)
    print()

    # TODO 10: Pembacaan nilai reactive power setiap detik, 5 kali, nilai disimpan
    print('10: Pembacaan nilai reactive power setiap detik, 5 kali, nilai disimpan')
    Q_rms_objects = ["1;0;23;7;0;255", "1;0;43;7;0;255", "1;0;63;7;0;255"]
    reactivePower_rms_value = read_value(ser_client, Q_rms_objects, 5)
    # reactivePower_rms_scalar = read_scalar(ser_client, Q_rms_objects)
    print(reactivePower_rms_value)
    print()

    # TODO 12: Pembacaan nilai apparent power setiap detik, 5 kali, nilai disimpan
    print('12: Pembacaan nilai apparent power setiap detik, 5 kali, nilai disimpan')
    S_rms_objects = ["1;0;29;7;0;255", "1;0;49;7;0;255", "1;0;69;7;0;255"]
    apparentPower_rms_value = read_value(ser_client, S_rms_objects, 5)
    # apparentPower_rms_scalar = read_scalar(ser_client, S_rms_objects)
    print(apparentPower_rms_value)
    print()

    ser_client.client_logout()
    

if __name__ == "__main__":
    start_calibration()
