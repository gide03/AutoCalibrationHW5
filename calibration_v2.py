import serial
import sys
import time

from translator import translate

from lib.GenyTestBench.GenyUtil import ElementSelector, PowerSelector, VoltageRange
from lib.GenyTestBench.GenyTestBench import GenyTestBench

from lib.DLMS_Client import dlmsCosemUtil
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient


import logging

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

# Create a logger
logger = logging.getLogger(__name__)

class CosemObject:
    def __init__(self, name, classId, obis):
        self.name = name
        self.classId = classId
        self.obis = obis
        self.value = 0

class Calibration:
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
        
    # Instant Register List
    InstantVoltagePhase1 = CosemObject('InstantVoltagePhase1', 3, "1;0;32;7;0;255")
    InstantVoltagePhase2 = CosemObject('InstantVoltagePhase2', 3, "1;0;52;7;0;255")
    InstantVoltagePhase3 = CosemObject('InstantVoltagePhase3', 3, "1;0;72;7;0;255")
    InstantCurrentPhase1 = CosemObject('InstantCurrentPhase1', 3, "1;0;31;7;0;255")
    InstantCurrentPhase2 = CosemObject('InstantCurrentPhase2', 3, "1;0;51;7;0;255")
    InstantCurrentPhase3 = CosemObject('InstantCurrentPhase3', 3, "1;0;71;7;0;255")
    InstantActivePowerPhase1 = CosemObject('InstantActivePowerPhase1', 3, "1;0;35;7;0;255")
    InstantActivePowerPhase2 = CosemObject('InstantActivePowerPhase2', 3, "1;0;55;7;0;255")
    InstantActivePowerPhase3 = CosemObject('InstantActivePowerPhase3', 3, "1;0;75;7;0;255")
    
    def __init__(self, comPort):
        self.comPort = comPort
        self.instanRegisters = (
            Calibration.InstantVoltagePhase1,
            Calibration.InstantVoltagePhase2,
            Calibration.InstantVoltagePhase3,
            Calibration.InstantCurrentPhase1,
            Calibration.InstantCurrentPhase2,
            Calibration.InstantCurrentPhase3,
            Calibration.InstantActivePowerPhase1,
            Calibration.InstantActivePowerPhase2,
            Calibration.InstantActivePowerPhase3,
        )
        self.gainValue = {} # refer to 0;128;96;14;80;255 

        self.ser_client = DlmsCosemClient(
            port=self.comPort,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            inactivity_timeout=10,
            login_retry=1,
            meter_addr=Calibration.commSetting.METER_ADDR,
            client_nb=Calibration.commSetting.CLIENT_NUMBER,
        )
        self.instantRegister = None
    
    def login(self):
        for i in range(2):
            loginResult = False
            try:
                logger.info('Login to meter')
                loginResult = self.ser_client.client_login(Calibration.commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
                logger.info(f'result login dlms - {loginResult}')
                break
            except:
                print('')
            if loginResult == False:
                logger.critical(f'Could not connect to meter')
                
    
    def logout(self):
        logger.info('Logout from meter')
        self.ser_client.client_logout()
        
    def read_calibration_data(self, verbose = False):
        logger.info('result login dlms - read calibration data')
        data_read = self.ser_client.get_cosem_data(1, "0;128;96;14;80;255", 2)
        print(data_read)
        bytes(data_read).hex()
        logger.info('translate register')
        self.gainValue = translate(data_read)
    
    def read_manufacturing_setup(self, verbose=False):
        logger.info('result login dlms - read calibration data')
        data_read = self.ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
        print(data_read)
        print(' '.join([]))
        # bytes(data_read).hex()
        # logger.info('translate register')
        # self.gainValue = translate(data_read)
    
    def calculateNewGain(self, genySamplingFeedback:tuple):
        targets = (
            (self.InstantVoltagePhase1, "g_MQAcquisition.gainVrms[phaseA]", "Voltage_A"),
            (self.InstantVoltagePhase2, "g_MQAcquisition.gainVrms[phaseB]", "Voltage_B"),
            (self.InstantVoltagePhase3, "g_MQAcquisition.gainVrms[phaseC]", "Voltage_C"),
            (self.InstantCurrentPhase1, 'g_MQAcquisition.gainIrms[phaseA]', "Current_A"),
            (self.InstantCurrentPhase2, 'g_MQAcquisition.gainIrms[phaseB]', "Current_B"),
            (self.InstantCurrentPhase3, 'g_MQAcquisition.gainIrms[phaseC]', "Current_C"),
            (self.InstantActivePowerPhase1, "g_MQAcquisition.gainActiveE[phaseA]", "PowerActive_A"),
            (self.InstantActivePowerPhase2, "g_MQAcquisition.gainActiveE[phaseB]", "PowerActive_B"),
            (self.InstantActivePowerPhase3, "g_MQAcquisition.gainActiveE[phaseC]", "PowerActive_C")
        )
        
        # transform tuple to dict
        test_bench_feedback = {}
        for target in targets:
            for samplingData in genySamplingFeedback:
                if target[-1] == samplingData.name:
                    test_bench_feedback[target[-1]] = samplingData
                    break
        
        for target in targets:
            meterMeasurement = target[0].value
            prevGain = self.gainValue[target[1]]
            genyFeedback = test_bench_feedback[target[2]].value
            
            # New Gain = (Previous Gain * Referensi Geny) / Average Instant Vrms    
            newGain = (prevGain * genyFeedback) / meterMeasurement
            
            objectName = target[0].name
            logger.info(f'{objectName}, prevGain = {prevGain} newGain = {newGain}')
            
        
    def fetchInstantRegister(self):
        logger.info('Fetch instant register value')
        
        for register in self.instanRegisters:
            value = self.ser_client.get_cosem_data(
                class_id=register.classId,
                obis_code=register.obis,
                att_id=2
            )
            scalarUnit = self.ser_client.get_cosem_data(
                class_id=register.classId,
                obis_code=register.obis,
                att_id=3
            )           
            logger.info(f'Fetch {register.name} att.2:{value} att.3:{scalarUnit}')
             
            actualValue = value*10**scalarUnit[0]
            logger.info(f'Value of {register.name}: {value} * 10^{scalarUnit[0]} = {actualValue}')
            register.value = actualValue

geny = GenyTestBench('/dev/ttyUSB1', 115200)
calib_1 = Calibration('/dev/ttyUSB0')


# geny.close()
# time.sleep(5)
# print('Open')
# geny.open()
# print('Setup buffer')
# geny.setMode(GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION)
# geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
# geny.setElementSelector(ElementSelector.EnergyErrorCalibration._COMBINE_ALL)
# geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
# geny.setPowerFactor(50, inDegree=True)
# geny.setVoltage(220)
# geny.setCurrent(5)
# print('Apply configuration')
# geny.apply()
# print('Done')
# time.sleep(10)
# geny.readBackSamplingData(verbose=True)
        # readBackRegisters = geny.readBackSamplingData()
        # for i in readBackRegisters:
        #     print(i.name)
        # exit()
calib_1.login()
calib_1.read_manufacturing_setup()
# calib_1.fetchInstantRegister()
calib_1.read_calibration_data()
# readBackRegisters = geny.readBackSamplingData()
# calib_1.calculateNewGain(readBackRegisters)
calib_1.logout()
    
# print('Close')
# geny.close()