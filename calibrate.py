import serial
from lib.DLMS_Client import dlmsCosemUtil
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec
from lib.GENY.GENYApi import GENYClient, ElementSelector

import constant
import translator
import numpy as np
import time
import json
import os

BOOTING_TIME = 7
ERROR_ACCEPTANCE = 0.01
IS_GENY_ON = False

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
        print(f"[Ratio:{self.object}] mean: {normalize_value} {type(normalize_value)}")
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
        
        print(f"[Ratio:{self.object}] reference:{reference:.4f}, meter_measurement:{meter_measurement:.4f}, current_gain:{current_gain}, new gain calculation:{self.last_ratio}, error: {(reference-meter_measurement) / reference : .5f}")
        
        error_treshold = 1 - self.threshold
        error = (reference - meter_measurement) / reference
        print(f'[Ratio:{self.object}] acceptance error must be less than {error_treshold:.5f}', end=' -- ')
        if abs(error) < error_treshold: # if the error near 0 then don't care calibration by passing the same gain value
            print(f'[Ratio:{self.object}] (PASSED)')
            return current_gain, False
        print(f'[Ratio:{self.object}] (NOPE)')
        return self.last_ratio, True

# UTILS
def read_calibration_data(dlms_client:DlmsCosemClient):    
    data_read = dlms_client.get_cosem_data(1, "0;128;96;14;80;255", 2)
    try:
        bytes(data_read).hex()
    except:
        print('error when read calibration data')
        print('data: ', data_read)
        print('retry to read calibration data')
        print('re login dlms client')
        
        ser_client.client_logout()
        meter_login()
        return read_calibration_data(dlms_client)
    
    output = translator.translate(data_read)
    return output

def meter_login():
    # loggin to dlms
    
    if ser_client.is_connected:
        print('[meter_login] already connected')
        return
    
    meter_logout() # make sure dlms connection
    
    try:
        # print('[meter_login] login dlms')
        result = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
        # print(f'[meter_login] login dlms - {result}')
    except Exception as e:
        print(f'[meter_login] login failed caused by communication problem. message {str(e)}')

    
def meter_logout():
    try:
        # print('[meter_logout] logout dlms')
        ser_client.client_logout()
    except:
        pass

def restart_geny():
    global IS_GENY_ON
    
    print("restart on meter")
    geny.calib_stop()
    time.sleep(3)
    turnon_geny()
    IS_GENY_ON = True

def turnon_geny():
    global IS_GENY_ON
    
    print("turn on meter")
    geny.calib_testCMD(ElementSelector._COMBINE_ALL, 230.0, 5.0, 0.5, 50, 1000, 5)
    geny.calib_execute()
    print(f'Wait meter booting (HARD CODED {BOOTING_TIME} sec)')
    time.sleep(BOOTING_TIME) # wait meter for booting up
    
    IS_GENY_ON = True

def turnoff_geny():
    global IS_GENY_ON
    
    print('turn off geny')
    geny.calib_stop()
    IS_GENY_ON = False
# end of UTILS 

def fake_calibration():
    # loggin to dlms
    print('[fake_calibration] start calibrating')
    print('[fake_calibration] Login dlms')
    meter_login()
    
    # FORCE calibrating
    data_raw = [97, 168, 97, 168, 97, 168, 117, 48, 117, 48, 117, 48, 117, 48, 117, 48, 117, 48, 166, 4, 168, 97, 32, 78, 64, 156, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 1, 56, 7, 83, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 62, 249, 3, 32, 1, 1, 1, 1, 0, 250, 0, 250, 0, 250, 0, 250, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    result = ser_client.set_cosem_data(1, "0;128;96;14;80;255", 2, dlmsCosemUtil.cosemDataType.octet_string, data_raw)
    print('[fake_calibration] Dummy calibration (FORCED) ',result)
    meter_logout()    

def read_instant_register():
    '''
        print meter measurement and calculate it's error reference to test bench feedback
        return: dict errors of Voltage, Current, Power
    '''
    description = ('Voltage', 'Current', 'Power')
    
    # loggin to dlms
    meter_login()
  
    instant_voltages = [
        # (Ratio instance, calibration parameter, geny feedback parameter)
        (InstantVoltagePhase1, "g_MQAcquisition.gainVrms[phaseA]", "Ua_amplitude"),
        (InstantVoltagePhase2, "g_MQAcquisition.gainVrms[phaseB]", "Ub_amplitude"),
        (InstantVoltagePhase3, "g_MQAcquisition.gainVrms[phaseC]", "Uc_amplitude"),
    ]
    instant_current = [
        (InstantCurrentPhase1, 'g_MQAcquisition.gainIrms[phaseA]', "Ia_amplitude"),
        (InstantCurrentPhase2, 'g_MQAcquisition.gainIrms[phaseB]', "Ib_amplitude"),
        (InstantCurrentPhase3, 'g_MQAcquisition.gainIrms[phaseC]', "Ic_amplitude"),
    ]
    instant_power_active = [
        (InstantActivePowerPhase1, "g_MQAcquisition.gainActiveE[phaseA]", "Pa"),
        (InstantActivePowerPhase2, "g_MQAcquisition.gainActiveE[phaseB]", "Pb"),
        (InstantActivePowerPhase3, "g_MQAcquisition.gainActiveE[phaseC]", "Pc"),
    ]
    
    print(f"[read_instant_register] Read test bench feedback")
    test_bench_feedback = geny.calib_readMeasurement()
    
    print("[read_instant_register] READING registers")
    errors = {}
    registers = (instant_voltages, instant_current, instant_power_active)
    for desc, instant_registers in zip(description, registers):        
        print(f'[test_bench_feedback] Instant {desc}:')
        errors[desc] = []
        for register in instant_registers:
            reg, _calib_parameter, _feedback_parameter = register
            value = reg.read_instant_value()
            print(f'[read_instant_register] Get meter measurement of {reg.object}: {value:.3f} ref: {test_bench_feedback[_feedback_parameter]:.3f}')
            error = (test_bench_feedback[_feedback_parameter]-value)/test_bench_feedback[_feedback_parameter]
            errors[desc].append(error)
        # print()
        
    print('[read_instant_register] Logout dlms')
    meter_logout()
    return errors

def start_calibration():
    '''
        start meter calibration, the meter shall be turned on
    '''
    
    # Login to meter
    print('[start_calibration] Start calibrating')
    print('[start_calibration] Meter login')
    meter_login()
    
    print('[start_calibration] Cathegorizing instant registers')
    instant_voltages = [
        # (Ratio instance, calibration parameter, geny feedback parameter)
        (InstantVoltagePhase1, "g_MQAcquisition.gainVrms[phaseA]", "Ua_amplitude"),
        (InstantVoltagePhase2, "g_MQAcquisition.gainVrms[phaseB]", "Ub_amplitude"),
        (InstantVoltagePhase3, "g_MQAcquisition.gainVrms[phaseC]", "Uc_amplitude"),
    ]
    instant_current = [
        (InstantCurrentPhase1, 'g_MQAcquisition.gainIrms[phaseA]', "Ia_amplitude"),
        (InstantCurrentPhase2, 'g_MQAcquisition.gainIrms[phaseB]', "Ib_amplitude"),
        (InstantCurrentPhase3, 'g_MQAcquisition.gainIrms[phaseC]', "Ic_amplitude"),
    ]
    instant_power_active = [
        (InstantActivePowerPhase1, "g_MQAcquisition.gainActiveE[phaseA]", "Pa"),
        (InstantActivePowerPhase2, "g_MQAcquisition.gainActiveE[phaseB]", "Pb"),
        (InstantActivePowerPhase3, "g_MQAcquisition.gainActiveE[phaseC]", "Pc"),
    ]
    
    print('[start_calibration] Read gain register from meter')
    gain_value = read_calibration_data(ser_client)
    print('[start_calibration] Calculate gain for rms voltage and current')
    for instant_registers in (instant_voltages, instant_current):
        is_calibrated = []
        for register_object, gain_key, feedback_key in instant_registers: # calculate new gain
            print(f'[start_calibration] Calculate {gain_key}')
            
            # Read geny feedback programmatically and feed to register object
            feedback_data = geny.calib_readMeasurement()
            gain, is_calibrate = register_object.calculate_gain(
                feedback_data[feedback_key], 
                gain_value[gain_key]
            )
            if not is_calibrate:
                is_calibrated.append(False)
                continue
            is_calibrated.append(True)
            print(f"[start_calibration] Set {gain_key}: {gain}")
            gain_value[gain_key] = gain
            print()
            
    print('[start_calibration] send calibration gain data')
    if not os.path.exists('./appdata'):
        os.mkdir('./appdata')
        
    filename = "calibration_data.json"
    with open(f'./appdata/{filename}', 'w') as f:
        json.dump(gain_value, f, indent=2)
        import pathlib
        print(f'[start_calibration] Calibration data sent is describe at: {pathlib.Path(__file__).parent.absolute()}/appdata/{filename}')
    calibration_data = translator.translate(gain_value, to_bytes=True)
    result = ser_client.set_cosem_data(1, "0;128;96;14;80;255", 2, dlmsCosemUtil.cosemDataType.octet_string, calibration_data)
    print(f'[start_calibration] send calibration data result: {result}')
    
    # TODO: Calibrating power
    time.sleep(2) # give a breath for meter
    print('[start_calibration] CALIBRATING POWER')
    print('[start_calibration] calculate instant RMS register error')
    errors = read_instant_register()
    # validate errors of voltage and current 
    vi_errors = []
    vi_errors.extend(errors['Voltage'])
    vi_errors.extend(errors['Current']) 
    
    is_calibrate_error = True
    # vi_errors -> error of [Va, Vb, Vc, Ia, Ib, Ic]
    for err in vi_errors:
        if err > ERROR_ACCEPTANCE:
            is_calibrate_error = False
    
    print('[start_calibration] Read gain register from meter')
    gain_value = read_calibration_data(ser_client) # NOTE: dlms is disconnected after execute this function
    meter_login() # relogin after read_calibration_data()
    if is_calibrate_error:
        is_calibrated = []
        for register_object, gain_key, feedback_key in instant_power_active: # calculate new gain
            print(f'[start_calibration] Calculate {gain_key}')
            
            # Read geny feedback programmatically and feed to register object
            feedback_data = geny.calib_readMeasurement()
            gain, is_calibrate = register_object.calculate_gain(
                feedback_data[feedback_key], 
                gain_value[gain_key]
            )
            if not is_calibrate:
                is_calibrated.append(False)
                continue
            is_calibrated.append(True)
            print(f"[start_calibration] Set {gain_key}: {gain}")
            gain_value[gain_key] = gain
            print()
    with open(f'./appdata/{filename}', 'w') as f:
        json.dump(gain_value, f, indent=2)
        import pathlib
        print(f'[start_calibration] Calibration data sent is describe at: {pathlib.Path(__file__).parent.absolute()}/appdata/{filename}')
    calibration_data = translator.translate(gain_value, to_bytes=True)
    result = ser_client.set_cosem_data(1, "0;128;96;14;80;255", 2, dlmsCosemUtil.cosemDataType.octet_string, calibration_data)
    print(f'[start_calibration] send calibration data result: {result}')
    
    meter_logout()

if __name__ == "__main__":    
    print('[main] Initializing GENY testbench')
    geny = GENYClient('10.23.40.32')
    geny.set_serial('COM13') # refer to server serial port
    
    print('[main] Initializing serial DLMS client')
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
    
    if not IS_GENY_ON: turnon_geny()
    
    print('[main] Initializing register')
    
    # Create object list, dlms client shall be logged in first
    meter_login()
    # Voltage registers
    InstantVoltagePhase1 = Ratio(ser_client, "1;0;32;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    InstantVoltagePhase2 = Ratio(ser_client, "1;0;52;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    InstantVoltagePhase3 = Ratio(ser_client, "1;0;72;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    # Current registers
    InstantCurrentPhase1 = Ratio(ser_client, "1;0;31;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    InstantCurrentPhase2 = Ratio(ser_client, "1;0;51;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    InstantCurrentPhase3 = Ratio(ser_client, "1;0;71;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    # Power active registers
    InstantActivePowerPhase1 = Ratio(ser_client, "1;0;35;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    InstantActivePowerPhase2 = Ratio(ser_client, "1;0;55;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    InstantActivePowerPhase3 = Ratio(ser_client, "1;0;75;7;0;255", threshold=1-ERROR_ACCEPTANCE)
    meter_logout()
    
    start_calibration()
    # fake_calibration()
    read_instant_register()

    turnoff_geny()
