import logging
import serial
import time
import pathlib
import os
import math
from datetime import datetime
import argparse
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
parser = argparse.ArgumentParser(description="Energy Calibration. If you didn't add parameter, configuration will taken from config.py")
parser.add_argument('-p', '--meterport', type=str, help='Communication port for meter.')
parser.add_argument('-g', '--genyport', type=str, help='Communication port for geny.')
parser.add_argument('-f', action='store_true', help='Flag to force calibrate')
args = parser.parse_args()

from lib.GenyTestBench.GenyUtil import ElementSelector, PowerSelector, VoltageRange
from lib.GenyTestBench.GenyTestBench import GenyTestBench
from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalibrationData import CalibrationRegister

import pickle
import config
from config import CosemList, GENY_USB_PORT, METER_USB_PORT, CalibrationParameter


# Serial and geny portn configuration
GENY_SLOT_INDEX = CalibrationParameter.GENY_SLOT_INDEX        # NOTE: Posisi meter pada slot geny test bench, ditihitung dari palig kiri 1, 2, 3
ERROR_ACCEPTANCE = CalibrationParameter.ERROR_ACCEPTANCE      # NOTE: Kriteria meter sukses dikalibrasi dalam persen
GENY_USB_PORT = config.GENY_USB_PORT
METER_USB_PORT = config.METER_USB_PORT

FORCE_CALIBRATE = False
if args.meterport != None:
    METER_USB_PORT = args.meterport
if args.genyport != None:
    GENY_USB_PORT = args.genyport
if args.f:
    FORCE_CALIBRATE = True

# Parameter configuration
PHASE_ANGLE_CONFIG = CalibrationParameter.PHASE_ANGLE_CONFIG    # in Degree
VOLTAGE_NOMINAL = CalibrationParameter.VOLTAGE_NOMINAL          # in Volt
CURRENT_NOMINAL = CalibrationParameter.CURRENT_NOMINAL          # in Ampere
BOOTING_TIME = CalibrationParameter.BOOTING_TIME                # in Second
REBOOT_WAIT = CalibrationParameter.REBOOT_WAIT                  # in Second

# Error relate to meter Vrms and Irms measurement
VOLTAGE_ERROR_ACCEPTANCE = 30/100   # in Percent
CURRENT_ERROR_ACCEPTANCE = 30/100   # in Percent
POWER_ERROR_ACCEPTANCE   = 30/100   # in Percent

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    PhaseAnglePhase1 = CosemObject('PhaseAnglePhase1', 3, "1;0;81;7;40;255")
    PhaseAnglePhase2 = CosemObject('PhaseAnglePhase2', 3, "1;0;81;7;51;255")
    PhaseAnglePhase3 = CosemObject('PhaseAnglePhase3', 3, "1;0;81;7;62;255")
    
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
        self.calibrationRegister = CalibrationRegister()
        self.meterSetupRegister = MeterSetup()
        
        self.backupCalibrationData = CalibrationRegister()
        self.backupMeterSetup = MeterSetup()

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
            address_size = AddrSize.ONE_BYTE
        )
        self.instantRegister = None
    
    def isValueRangeValid(self, measuredValue, referenceValue, errorAcceptance) -> bool:
        upperValue = referenceValue + (referenceValue*errorAcceptance)
        lowerValue = referenceValue - (referenceValue*errorAcceptance)
        return lowerValue < measuredValue < upperValue
            
    def login(self):
        loginResult = False
        try:
            logger.info('Login to meter')
            loginResult = self.ser_client.client_login(Calibration.commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
            logger.info(f'result login dlms - {loginResult}')
            return True
        except Exception as e:
            logger.critical(f'Failed to login, error message: {str(e)}')
            return False
    
    def logout(self):
        logger.info('Logout from meter')
        self.ser_client.client_logout()
        
    def eraseFlash(self):
        resetResult = self.ser_client.set_cosem_data(1,'1;1;128;130;3;255',2,22,1)
        print(f'reset flash result: {"SUCCESS" if resetResult==0 else "FAILED"}')
        return resetResult

    def saveCalibrationData(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self.calibrationRegister, f)
    
    def saveMeterSetup(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self.meterSetupRegister, f)
    
    def syncClock(self):
        logger.info('Synchronize clock')
        currentDate = datetime.now()
        year_HB = (currentDate.year >> 8) & 0xff
        year_LB = currentDate.year & 0xff
        month = currentDate.month
        day = currentDate.day
        weekday = currentDate.weekday() + 1
        hour = currentDate.hour
        minute = currentDate.minute
        second = currentDate.second
        hundredths = 0
        deviation = 128
        clockstatus = 0
        season = 0
        dlmsDate = [year_HB, year_LB, month, day, weekday, hour, minute, second, hundredths, deviation, clockstatus, season]
        result = self.ser_client.set_cosem_data(8, "0;0;1;0;0;255", 2, 9, dlmsDate)
        logger.info(f'Set current time: {result} -- {currentDate} inDlms: {dlmsDate}')
        logger.info('Check meter time after synchronize')
        clock_data = self.ser_client.get_cosem_data(8, "0;0;1;0;0;255", 2)
        logger.info(f"CLOCK DATA: {clock_data}")
        
    def verify_instant_registers(self, genySamplingReadback):
        '''
            Comparing value of Vrms and Irms based on Geny readback
        '''
        logger.info('validating instant register measurement.')
        logger.debug(f'error acceptance: voltage {VOLTAGE_ERROR_ACCEPTANCE}, current {CURRENT_ERROR_ACCEPTANCE}')
        targets = (
            (self.InstantVoltagePhase1, genySamplingReadback.Voltage_A.value ),
            (self.InstantVoltagePhase2, genySamplingReadback.Voltage_B.value ),
            (self.InstantVoltagePhase3, genySamplingReadback.Voltage_C.value ),
            (self.InstantCurrentPhase1, genySamplingReadback.Current_A.value ),
            (self.InstantCurrentPhase2, genySamplingReadback.Current_B.value ),
            (self.InstantCurrentPhase3, genySamplingReadback.Current_C.value ),
        )
        
        valid = []
        for target in targets:
            register = target[0]
            referenceValue = target[1]
            logger.info(f'Fetching {register.name}')
            # readResult = self.ser_client.get_cosem_data(register.classId, register.obis, 2)
            readResult = self.fetch_register(register)
            isValid = False
            if 'Voltage' in register.name :
                upperError = referenceValue + (referenceValue*VOLTAGE_ERROR_ACCEPTANCE)
                lowerError = referenceValue - (referenceValue*VOLTAGE_ERROR_ACCEPTANCE)
                if lowerError < readResult < upperError:
                    isValid = True
            elif 'Current' in register.name:
                upperError = referenceValue + (referenceValue*CURRENT_ERROR_ACCEPTANCE)
                lowerError = referenceValue - (referenceValue*CURRENT_ERROR_ACCEPTANCE)
                if lowerError < readResult < upperError:
                    isValid = True
            logger.info(f'{register.name} value: {readResult} is between {lowerError} {upperError} ? -- {isValid}')
            valid.append(isValid)
        return all(valid)
                
    def fetch_calibration_data(self, verbose = False):
        logger.info('read calibration data')
        mCosem = config.CosemList.CalibarationData
        data_read = self.ser_client.get_cosem_data(mCosem.classId, mCosem.obis, 2)
        logger.debug(f'calibration data read: {data_read}')
        self.calibrationRegister.extract(data_read)
        if verbose == True:
            self.calibrationRegister.info()
    
    def write_calibration_data(self, filepath=None) -> bool:
        retry = 5
        if filepath != None:
            if os.path.exists(filepath):
                logger.debug('write calibration data with file')
                logger.debug(f'filepath: {filepath}')
                with open(filepath, 'rb') as f:
                    buffer = pickle.load(f)
                    self.calibrationRegister = buffer
                    # print out the register to logfile
                    logger.info('#'*30)
                    logger.info('calibration value:')
                    _registers = self.calibrationRegister.info()
                    for register in _registers:
                        logger.info(f'{register}: {_registers[register].value}')
                    logger.info('#'*30)
        
        mCosem = config.CosemList.CalibarationData
        calibrationBuffer = self.calibrationRegister.dataFrame()
        for i in range(retry):
            try:
                logger.debug(f'try to send data calibration. Attemp {i+1} of {retry}')
                logger.debug(f'data: {calibrationBuffer}')
                # calibrationBuffer = self.calibrationRegister.dataFrame()
                result = self.ser_client.set_cosem_data(
                    class_id=mCosem.classId,
                    obis_code=mCosem.obis,
                    att_id=2,
                    dtype=CosemDataType.e_OCTET_STRING,
                    value=calibrationBuffer
                )
                logger.info(f'Result: {result}')
                return result
            except: # Handler for fw v7.62. The meter is going restart after set calibration data but the data is changed. Check if the value was changed, if not retry set.
                if i < retry-1:
                    logger.warning(f'timeout. Data sent: {calibrationBuffer}')
                    self.logout()
                    self.login()
                    calData = self.ser_client.get_cosem_data(mCosem.classId, mCosem.obis, 2)
                    logger.debug('matching current state with value sent before')
                    if calData == calibrationBuffer:
                        logger.debug('MATCH')
                        return True
                    continue
                
        logger.critical(f'TIMEOUT!!. Turn off test bench')
        raise TimeoutError
        
    def fetch_meter_setup(self, verbose=False) -> list:
        '''
            returns
                list of data read excess
        '''
        logger.info('reading meter setup')
        mCosem = config.CosemList.MeterSetup
        data_read = self.ser_client.get_cosem_data(mCosem.classId, mCosem.obis, 2)
        if isinstance(data_read, str):
            raise Exception(f'Fetch meter FAILED. Data result: {data_read}')
        
        logger.debug(f'meter setup data: {data_read}')
        self.meterSetupRegister.extract(data_read)
        if verbose:
            self.meterSetupRegister.info()
        return data_read
    
    def configure_meter_setup(self, filepath:str):
        '''
            parameter:
                - filepath `str` filepath of meter setup
        '''
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
            # return [lCrc&0xff, lCrc>>8]
            return lCrc
    
        logger.info('Fetch meter setup')
        if os.path.exists(filepath):
            logger.debug('write meter setup data with file')
            logger.debug(f'filepath: {filepath}')
            with open(filepath, 'rb') as f:
                buffer = pickle.load(f)
                self.meterSetupRegister = buffer
                # print out the register to logfile
                logger.info('#'*30)
                logger.info('Meter setup value:')
                _registers = self.meterSetupRegister.info()
                for register in _registers:
                    logger.info(f'{register}: {_registers[register].value}')
                logger.info('#'*30)
                
                logger.debug(f'RTC Calibration data: {self.meterSetupRegister.RTCCalibration.value}')
        else:
            self.fetch_meter_setup()
            
        
        logger.info('Fetch calibration data') # to calculate new crc
        self.fetch_calibration_data()
        self.meterSetupRegister.CalibratiOndateTime.value = int(time.time())
        self.meterSetupRegister.MeterForm.value = 133
        self.meterSetupRegister.MeterClass.value = 5
        self.meterSetupRegister.FrequencySelection.value = 0
        self.meterSetupRegister.MeterType.value = 1
        self.meterSetupRegister.MeterVoltageType.value = 0
        self.meterSetupRegister.MeterPowerSupplyType.value = 1
        self.meterSetupRegister.ServicesenseMode.value = 0
        self.meterSetupRegister.AnticreepConstant.value = 793
        
        # Calculate new data frame
        configurationData = self.calibrationRegister.dataFrame()
        configurationData.extend(self.meterSetupRegister.dataFrame())
        for i in range(2): #Pop CRC
            configurationData.pop(-1)
        newCRC = calRunningCRC16(configurationData)
        self.meterSetupRegister.CRC.value = newCRC
                
        retry = 5
        logger.info('Constructing data frame')
        mCosem = config.CosemList.MeterSetup
        meterSetupBuffer = self.meterSetupRegister.dataFrame()
        # NOTE: Different byte size and unknown CRC calculation type
        for i in range(retry):
            try:
                logger.debug(f'meter setup data length: {len(meterSetupBuffer)} B')
                
                logger.info(f'Sending data frame: {meterSetupBuffer}')
                result = self.ser_client.set_cosem_data(mCosem.classId, mCosem.obis, 2, CosemDataType.e_OCTET_STRING, meterSetupBuffer)
                logger.info(f'Result: {result}')
                return result
            except: # Handler for fw v7.62. The meter is going restart after set calibration data but the data is changed. Check if the value was changed, if not retry set.
                if i < retry-1:
                    logger.warning(f'timeout. Data sent: {meterSetupBuffer}')
                    self.logout()
                    self.login()
                    logger.debug('Read meter setup')
                    _meterSetup = self.ser_client.get_cosem_data(mCosem.classId, mCosem.obis, 2)
                    logger.debug(f'Comparing with data sent: {_meterSetup}')
                    if _meterSetup == meterSetupBuffer:
                        logger.debug('MATCH')
                        return True
                    logger.debug('NOT MATCH')
                    self.meterSetupRegister.extract(_meterSetup)
                    continue
                
        # TODO: Add comparison summary that
        logger.critical(f'TIMEOUT!!. Turn off test bench')
        raise TimeoutError
            
    def calibratePhaseDelay(self, genySamplingFeedback):
        '''
            Procedure:
                [1] Fetch calibration data
                [2] Set phase direction each phase
                [3] Update phase parameter
                [4] 
        '''
        global PHASE_ANGLE_CONFIG
        
        logger.info('fetching initial calibration data')
        # [1]
        self.fetch_calibration_data()
        # [/1]
        
        # [2]
        logger.info('Set phase direction to 1')
        self.calibrationRegister.PhDirectionA.value = 1
        self.calibrationRegister.PhDirectionB.value = 1
        self.calibrationRegister.PhDirectionC.value = 1
        self.calibrationRegister.PhDirectionN.value = 1        
        logger.info('update phase delay parameters to 0')        
        self.calibrationRegister.PhaseDelayA.value = 0
        self.calibrationRegister.PhaseDelayB.value = 0
        self.calibrationRegister.PhaseDelayC.value = 0
        self.calibrationRegister.PhaseDelayN.value = 0
        self.calibrationRegister.tf_coeff_a0.value = 7972264
        self.calibrationRegister.tf_coeff_a1.value = -7541100
        self.calibrationRegister.tf_coeff_a2.value = -409914
        self.calibrationRegister.tf_coeff_a3.value = 0
        self.calibrationRegister.tf_coeff_b1.value = -8387011
        self.calibrationRegister.tf_coeff_b2.value = 0
        self.calibrationRegister.tf_coeff_b3.value = 0
        
        logger.info('update tf control to 1')
        self.calibrationRegister.tf_control.value = 1
        logger.info('write calibration data')
        result = self.write_calibration_data()
        logger.info(f'calibration data result: {result}')
        #  [/2]
        
        # NOTE: DON'T CHANGE THIS BLOCK WIHTOUT INFORM YOUR TEAM
        targets = (
            (self.PhaseAnglePhase1, self.calibrationRegister.PhaseDelayA, PHASE_ANGLE_CONFIG),
            (self.PhaseAnglePhase2, self.calibrationRegister.PhaseDelayB, PHASE_ANGLE_CONFIG),
            (self.PhaseAnglePhase3, self.calibrationRegister.PhaseDelayC, PHASE_ANGLE_CONFIG)
        )
        for idx,target in enumerate(targets):
            #TODO: New Gain = (Previous Gain * Referensi Geny) / Average Instant Vrms    
            instanRegister = target[0]
            meterMeasurement = self.fetch_register(instanRegister, numOfSample=2) - (120*idx)
            prevGain = target[1].value
            genyFeedback = target[2]
            
            # calculate error before
            newPhaseDelay = (meterMeasurement - genyFeedback)*100
            if newPhaseDelay<0:
                # newPhaseDelay = (genyFeedback - meterMeasurement)*100
                newPhaseDelay = 0
            newPhaseDelay = int(newPhaseDelay)
            logger.info(f'Apply new phase delay for {target[1].name} from {target[1].value} to {newPhaseDelay}')
            target[1].value = newPhaseDelay
        
        result = self.write_calibration_data()
        logger.info(f'set calibration register. result: {result}')        
        
    def calibrateVoltageAndCurrent(self, genySamplingFeedback):
        logger.info('fetching calibration register')
        self.fetch_calibration_data()        
        
        targets = (
            (self.InstantVoltagePhase1, self.calibrationRegister.GainVrms_A, genySamplingFeedback.Voltage_A.value),
            (self.InstantVoltagePhase2, self.calibrationRegister.GainVrms_B, genySamplingFeedback.Voltage_B.value),
            (self.InstantVoltagePhase3, self.calibrationRegister.GainVrms_C, genySamplingFeedback.Voltage_C.value),
            (self.InstantCurrentPhase1, self.calibrationRegister.GainIrms_A, genySamplingFeedback.Current_A.value),
            (self.InstantCurrentPhase2, self.calibrationRegister.GainIrms_B, genySamplingFeedback.Current_B.value),
            (self.InstantCurrentPhase3, self.calibrationRegister.GainIrms_C, genySamplingFeedback.Current_C.value)
        )        
        # TODO: calibrate instant voltage and current
        for target in targets:
            #TODO: New Gain = (Previous Gain * Referensi Geny) / Average Instant Vrms    
            instanRegister = target[0]
            meterMeasurement = self.fetch_register(instanRegister, numOfSample=2)
            prevGain = target[1].value
            genyFeedback = target[2]
            
            # Validating meter measurement
            errorAcceptance = 0
            if 'Voltage' in instanRegister.name:
                errorAcceptance = VOLTAGE_ERROR_ACCEPTANCE
            elif 'Current' in instanRegister.name:
                errorAcceptance = CURRENT_ERROR_ACCEPTANCE            
            if not self.isValueRangeValid(meterMeasurement, genyFeedback, errorAcceptance):
                logger.critical(f'Invalid measurement at {instanRegister.name}')
                return False
            
            # calculate new gain
            logger.info(f'Calculate new gain for {target[1].name}')
            logger.debug(f'PrevGain: {prevGain} GenyFeedBack: {genyFeedback} MeterMasurement: {meterMeasurement}')
            newGain = (prevGain * genyFeedback) / meterMeasurement
            newGain = int(newGain)
            logger.info(f'Apply new gain for {target[1].name} from {target[1].value} to {newGain}')
            target[1].value = newGain

        result = self.write_calibration_data()
        logger.info(f'set calibration register. result: {result}')
        return result
        # if result == 0:
        #     for target in targets:
        #         instanRegister = target[0]
        #         meterMeasurement = self.fetch_register(instanRegister)
        #         prevGain = target[1].value
        #         genyFeedback = target[2]   
    
    def calibratePowerActive(self, genySamplingFeedback) -> bool:
        logger.info('fetching calibration register')
        self.fetch_calibration_data()
                
        targets = (
            (self.InstantActivePowerPhase1, self.calibrationRegister.GainActiveE_A, genySamplingFeedback.PowerActive_A.value),
            (self.InstantActivePowerPhase2, self.calibrationRegister.GainActiveE_B, genySamplingFeedback.PowerActive_B.value),
            (self.InstantActivePowerPhase3, self.calibrationRegister.GainActiveE_C, genySamplingFeedback.PowerActive_C.value),
        )
        # TODO: calibrate instant voltage and current
        for target in targets:
            #TODO: New Gain = (Previous Gain * Referensi Geny) / Average Instant Vrms    
            instanRegister = target[0]
            meterMeasurement = self.fetch_register(instanRegister)
            prevGain = target[1].value
            genyFeedback = target[2]
            
            # Validating meter measurement      
            if not self.isValueRangeValid(meterMeasurement, genyFeedback, POWER_ERROR_ACCEPTANCE):
                logger.critical('Meter measurement is not valid')
                return False
            
            # Calculating new gain
            logger.info(f'Calculate new gain for {target[1].name}')
            newGain = (prevGain * genyFeedback) / meterMeasurement
            logger.debug(f'PrefGain: {prevGain} GenyFeedback: {genyFeedback} MeterMeasurement: {meterMeasurement}')
            newGain = int(newGain)
            logger.info(f'Apply new gain for {target[1].name} from {target[1].value} to {newGain}')
            target[1].value = newGain

        result = self.write_calibration_data()
        logger.info(f'set calibration register. result: {result}')
        return result
    
    def fetch_register(self, register, numOfSample=1):        
        logger.info('Fetch instant register value')
        
        samples = []
        for i in range(numOfSample):
            value = self.ser_client.get_cosem_data(
                class_id=register.classId,
                obis_code=register.obis,
                att_id=2
            )
            samples.append(value)
        value = sum(samples)/numOfSample # measurement average
        
        # scalarUnit = self.ser_client.get_cosem_data(
        #     class_id=register.classId,
        #     obis_code=register.obis,
        #     att_id=3
        # )         
        scalarUnit = (-3, None)  
        logger.info(f'Fetch {register.name} att.2:{value} att.3:{scalarUnit}. NOTE: Scalar unit was hard coded')
            
        actualValue = value*10**scalarUnit[0]
        logger.info(f'Value of {register.name}: {value} * 10^{scalarUnit[0]} = {actualValue}')
        register.value = actualValue
        return register.value

def validateGeny(genyReadback):
    params = (
        genyReadback.Voltage_A,
        genyReadback.Voltage_B,
        genyReadback.Voltage_C,
        genyReadback.Current_A,
        genyReadback.Current_B,
        genyReadback.Current_C,        
    )
    valid = []
    for param in params:
        isValid = False
        genyFeedback = param.value
        expectedGenyFeedback = 0
        acceptanceError = 10/100
        if 'Voltage' in param.name:
            expectedGenyFeedback = VOLTAGE_NOMINAL
            # acceptanceError = VOLTAGE_ERROR_ACCEPTANCE
            # upperError = expectedGenyFeedback + (expectedGenyFeedback*acceptanceError)
            # lowerError = expectedGenyFeedback - (expectedGenyFeedback*acceptanceError)
            # if lowerError < genyFeedback < upperError:
            #     isValid = True
        elif 'Current' in param.name:
            expectedGenyFeedback = CURRENT_NOMINAL
            # acceptanceError = CURRENT_ERROR_ACCEPTANCE
            # upperError = expectedGenyFeedback + (expectedGenyFeedback*acceptanceError)
            # lowerError = expectedGenyFeedback - (expectedGenyFeedback*acceptanceError)
            # if lowerError < genyFeedback < upperError:
            #     isValid = True
        elif 'Power' in param.name:
            expectedGenyFeedback = (VOLTAGE_NOMINAL - CURRENT_NOMINAL) * math.cos(math.radians(PHASE_ANGLE_CONFIG))
            # acceptanceError = POWER_ERROR_ACCEPTANCE
            
        upperError = expectedGenyFeedback + (expectedGenyFeedback*acceptanceError)
        lowerError = expectedGenyFeedback - (expectedGenyFeedback*acceptanceError)
        if lowerError < genyFeedback < upperError:
            isValid = True
        
        valid.append(isValid)
    return all(valid)

# MAIN PROGRAM START HERE
def main():
    global PHASE_ANGLE_CONFIG    
    global GENY_USB_PORT
    global METER_USB_PORT
    
    geny = GenyTestBench(GENY_USB_PORT, 9600)
    meter = Calibration(METER_USB_PORT)
    readBackRegisters = None
    
    if not os.path.exists(f'{CURRENT_PATH}/logs'):
        os.mkdir(f'{CURRENT_PATH}/logs')
    if not os.path.exists(f'{CURRENT_PATH}/appdata'):
        os.mkdir(f'{CURRENT_PATH}/appdata')
    
    print('Please input meter ID. If empty program will terminated')
    meterId = input('Meter ID: ')
    if len(meterId) == 0:
        exit('Calibration Canceled')
    dataCalibration = f'{CURRENT_PATH}/appdata/{meterId} calibration.pkl'
    dataMeterSetup = f'{CURRENT_PATH}/appdata/{meterId} meterSetup.pkl'
    filename = f'{CURRENT_PATH}/logs/{meterId} calibration.log' 
        
    #
    # Logger setup    
    #
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
    logger.info('\n')
    logger.info('='*30)
    logger.info('STARTING CALIBRATION')
    logger.info('='*30)
    logger.info('Initializing')
    logger.info('Configuring test bench')
    geny.close()
    time.sleep(3)
    # TURN ON METER
    geny.open()
    geny.setMode(GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION)
    geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
    geny.setElementSelector(ElementSelector.EnergyErrorCalibration._COMBINE_ALL)
    geny.setVoltageRange(VoltageRange.YC99T_3C._380V)
    geny.setPowerFactor(PHASE_ANGLE_CONFIG, inDegree=True)
    geny.setVoltage(VOLTAGE_NOMINAL)
    geny.setCurrent(CURRENT_NOMINAL)
    geny.setCalibrationConstants(1000, 2)
    logger.debug('TURN ON METER')
    geny.apply()
    logger.info(f'WAIT METER FOR BOOTING ({BOOTING_TIME} second)')
    readBackRegisters = None
    for i in range(0, BOOTING_TIME):
        if i == int(BOOTING_TIME/2):
            while True:
                readBackRegisters = geny.readBackSamplingData()
                if validateGeny(readBackRegisters):
                    break
        time.sleep(1)
    
    logger.info('LOGIN TO METER') 
    try:
        meter.logout()
    except:
        pass
    if not meter.login():
        logger.info('Could not login to meter')
        geny.close()
        exit()
            
    # STEP 1: Reading firmware version and data backup
    logger.info('STEP 1: Reading fw version')
    fwVersion = meter.ser_client.get_cosem_data(1, '1;0;0;2;0;255', 2)
    if type(fwVersion) == str:
        logger.critical(f'Error while get fw version. Read result: {fwVersion}')
        geny.close()
        exit(1)
    logger.info(f'Firmware Version: {bytes(fwVersion).decode("utf-8")}')
    
    # Backup calibration data. If only the meter is already calibrated
    '''
        Calibrated meter is determined when :
            - Meter SETUP CRC = 64000. I get this value after erase flash.
    
        NOTE:
            - RTC Calibration is inside meter setup register
            - Energy Calibration data is inside calibration register, all values inside it will be set directly
            
            [Optional] On the future, create a flag to remove the file to recalibrate the meterId
    '''
    meter.fetch_calibration_data()
    meter.fetch_meter_setup()
    print(meter.meterSetupRegister.CRC.value)
    IsCalibrated = False
    
    if not FORCE_CALIBRATE:
        if meter.meterSetupRegister.CRC.value != 10762:
            logger.debug('Detect calibrated meter')
            logger.info('Backup calibration data')
            meter.saveMeterSetup(dataMeterSetup)
            meter.saveCalibrationData(dataCalibration)
            IsCalibrated = True
        else:
            logger.debug('Detect uncalibrated meter')
    else:
        logger.info('FORCE CALIBRATE')
        
    # STEP 3: ERASE FLASH
    logger.info('STEP 2: Erase flash')
    meter.eraseFlash()
    logger.info('Restarting meter')
    geny.close()
    logger.info(f'Test bench turned off, take a breath for {REBOOT_WAIT}s')
    time.sleep(REBOOT_WAIT)
    logger.info('TURN ON METER')
    geny.open()
    geny.apply()
    logger.info(f'WAIT METER FOR BOOTING ({BOOTING_TIME} second)')    
    time.sleep(BOOTING_TIME+5)
    try:
        meter.logout()
    except:
        pass
    logger.info('LOGIN TO METER')     
    if not meter.login():
        geny.close()
        exit()
        
    # meter.fetch_calibration_data()
    # meter.fetch_meter_setup()
    # print(meter.meterSetupRegister.CRC.value)
    
    # geny.close()
    # exit()
            
    # STEP 3: Configure LED1 setup
    logger.info('STEP 3: Setup LED1')
    led1ConfigValue = [       
        [CosemDataType.e_LONG_UNSIGNED, 10],
        [CosemDataType.e_LONG_UNSIGNED, 11520],
        [CosemDataType.e_LONG_UNSIGNED, 11520],
        [CosemDataType.e_ENUM, 4],
        [CosemDataType.e_ENUM, 3],
        [CosemDataType.e_ENUM, 2],
        [CosemDataType.e_ENUM, 0],
        [CosemDataType.e_ENUM, 1],
        [CosemDataType.e_ENUM, 0],
        [CosemDataType.e_ENUM, 0],
        [CosemDataType.e_ENUM, 1],
        [CosemDataType.e_LONG_UNSIGNED, 0],

    ]
    logger.info(f'LED1 Config Value: {led1ConfigValue}')
    led1_setResult = meter.ser_client.set_cosem_data(1, '0;128;96;6;8;255', 2, 2, led1ConfigValue)
    logger.info(f'Result: {led1_setResult}')
    
    # STEP 4: Configure LED1 setup
    logger.info('STEP 4: Setup LED2')
    led2ConfigValue = [
        [CosemDataType.e_LONG_UNSIGNED, 10],
        [CosemDataType.e_LONG_UNSIGNED, 11520],
        [CosemDataType.e_LONG_UNSIGNED, 11520],
        [CosemDataType.e_ENUM, 4],
        [CosemDataType.e_ENUM, 3],
        [CosemDataType.e_ENUM, 1],
        [CosemDataType.e_ENUM, 0],
        [CosemDataType.e_ENUM, 1],
        [CosemDataType.e_ENUM, 0],
        [CosemDataType.e_ENUM, 0],
        [CosemDataType.e_ENUM, 1],
        [CosemDataType.e_LONG_UNSIGNED, 0],
    ]
    logger.info(f'LED2 Config Value: {led2ConfigValue}')
    led2_setResult = meter.ser_client.set_cosem_data(1, '0;128;96;6;20;255', 2, 2, led2ConfigValue)  
    logger.info(f'Result: {led2_setResult}')  
    
    # STEP 5: Configure KYZ
    logger.info('STEP 5: Configure KYZ to make sure the KYZ status is 0')
    kyz_cosem = (
    '0;128;96;6;23;255',
    '0;128;96;6;24;255',
    '0;128;96;6;25;255'
    )
    kyz_dtype = (
        CosemDataType.e_LONG_UNSIGNED,
        CosemDataType.e_LONG_UNSIGNED,
        CosemDataType.e_LONG_UNSIGNED,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_ENUM,
        CosemDataType.e_LONG_UNSIGNED,
    )
    for kyz in kyz_cosem:
        logger.info(f'Configure {kyz}')
        kyzData = []
        logger.info(f'Read {kyz}')
        readData = meter.ser_client.get_cosem_data(1, kyz, 2)
        logger.info(f'Read result -- {readData}')
        if readData[-2] == 0:
            logger.info('Skip configuration because the status already 0')
            continue
        readData[-2] = 0
        for idx, (data,dtype) in enumerate(zip(readData, kyz_dtype)):
            temp = [dtype,data]
            kyzData.append(temp)
            
        logger.info(f'Data will be set: {kyzData}')
        result = meter.ser_client.set_cosem_data(1, kyz, 2, 2, kyzData)
        logger.info(f'Set result: {result}')
    
    # STEP 6: Configure meter setup
    # NOTE: Length of meter setup not match (101 Bytes instead of 109 Bytes). There is CRC that need to be update. Currently using hardcoded configuration from HW5+ software
    logger.info('STEP 6: Writing meter setup')
    meter.configure_meter_setup(dataMeterSetup)
    time.sleep(2)
                
    # STEP 7: Calibrate phase delay
    logger.info('STEP 7: CALIBRATING phase delay')
    if not IsCalibrated:
        while True:
            readBackRegisters = geny.readBackSamplingData()
            if validateGeny(readBackRegisters):
                break
        meter.calibratePhaseDelay(readBackRegisters)
    else:
        logger.info('SKIP. Phase delay values will set by data file')
        
    
    # STEP 8: Calibrate Vrms and Irms
    logger.info('STEP 8: CALIBRATING Vrms Irms')
    if not IsCalibrated:
        meter.fetch_calibration_data()
        while True:
            readBackRegisters = geny.readBackSamplingData()
            if validateGeny(readBackRegisters):
                break
        isCalibrationSuccess = meter.calibrateVoltageAndCurrent(readBackRegisters)
        if not isCalibrationSuccess:
            logger.critical('CALIBRATION FAILED')
            meter.logout()
            geny.close()
            exit(1)
    else:
        logger.info('SKIP. Vrms and Irms gain values will set by data file')
        
    
    # STEP 9: Calibrate Power Active
    logger.info('STEP 9: CALIBRATING POWER ACTIVE')
    if not IsCalibrated:
        meter.fetch_calibration_data()
        while True:
            readBackRegisters = geny.readBackSamplingData()
            if validateGeny(readBackRegisters):
                break
        isCalibrationSuccess = meter.calibratePowerActive(readBackRegisters)
        if not isCalibrationSuccess:
            logger.critical('CALIBRATION FAILED')
            meter.logout()
            geny.close()
            exit(1)
    else:
        logger.info('SKIP. Energy gain values will set by data file')
    
    # STEP 10: Write calibration data (if calibrated) and calculate error
    if IsCalibrated:
        logger.info('Write backup calibration data to meter')
        meter.write_calibration_data(dataCalibration)
        time.sleep(1)
        
    logger.info('Calculating power active error')
    while True:
        readBackRegisters = geny.readBackSamplingData()
        if validateGeny(readBackRegisters):
            break
    instantPowerActive = (
        meter.InstantActivePowerPhase1,
        meter.InstantActivePowerPhase2,
        meter.InstantActivePowerPhase3,
    )
    reference = (
        readBackRegisters.PowerActive_A,
        readBackRegisters.PowerActive_B,
        readBackRegisters.PowerActive_C
    )
    for instantRegister, referenceRegister in zip(instantPowerActive, reference):
        instantValue = meter.fetch_register(instantRegister) 
        error = ((referenceRegister.value - instantValue) / referenceRegister.value) * 100
        logger.info(f'{instantRegister.name} meter measure: {instantRegister.value:.4f}, reference: {referenceRegister.value:.4f} error: {error:.5f}%')

    # STEP 11: 
    logger.info('STEP 11: FINISHING')
    
    if not IsCalibrated:
        logger.info('Store calibration values')
        meter.fetch_calibration_data()
        meter.fetch_meter_setup()
        meter.saveMeterSetup(dataMeterSetup)
        meter.saveCalibrationData(dataCalibration)
        
    # meter.syncClock()
    logger.debug('Logout from meter')
    meter.logout()
    logger.debug('Turn off meter')
    geny.close()
    
if __name__ == '__main__':
    main()
    input('Calibration finished. Press enter to continue')
