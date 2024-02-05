import logging
import serial
import sys
import time

from translator import translate

from lib.GenyTestBench.GenyUtil import ElementSelector, PowerSelector, VoltageRange
from lib.GenyTestBench.GenyTestBench import GenyTestBench, EnergyErrorCalibration
from lib.DLMS_Client import dlmsCosemUtil
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient

from ConfigurationRegister import Register, RegisterWrapper

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

# Create a logger
logger = logging.getLogger(__name__)
# logger.setLevel(logging.)

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
        
    class MeterSetup(RegisterWrapper):
        def __init__(self):
            self.CalibratiOndateTime = Register("CalibratiOndateTime", "uint32")
            self.MeterForm = Register("MeterForm", "uint8")
            self.MeterClass = Register("MeterClass", "uint8")
            self.FrequencySelection = Register("FrequencySelection", "uint8")
            self.MeterType = Register("MeterType", "uint8")
            self.MeterVoltageType = Register("MeterVoltageType", "uint8")
            self.MeterPowerSupplyType = Register("MeterPowerSupplyType", "uint8")
            self.ServicesenseMode = Register("ServicesenseMode", "uint8")
            self.VACalculatiOnConfig = Register("VACalculatiOnConfig", "uint8")
            self.WattCalculatiOnConfig = Register("WattCalculatiOnConfig", "uint8")
            self.VARCalculatiOnConfig = Register("VARCalculatiOnConfig", "uint8")
            self.LED1PulseWeight = Register("LED1PulseWeight", "uint16")
            self.LED1PulseOnTime = Register("LED1PulseOnTime", "uint16")
            self.LED1PulseOffTime = Register("LED1PulseOffTime", "uint16")
            self.LED1DebugData = Register("LED1DebugData", "uint32")
            self.LED1Phase = Register("LED1Phase", "uint8")
            self.LED1Direction = Register("LED1Direction", "uint8")
            self.LED1Energy = Register("LED1Energy", "uint8")
            self.LED1CreepEvent = Register("LED1CreepEvent", "uint8")
            self.LED2PulseWeight = Register("LED2PulseWeight", "uint16")
            self.LED2PulseOnTime = Register("LED2PulseOnTime", "uint16")
            self.LED2PulseOffTime = Register("LED2PulseOffTime", "uint16")
            self.LED2DebugData = Register("LED2DebugData", "uint32")
            self.LED2Phase = Register("LED2Phase", "uint8")
            self.LED2Direction = Register("LED2Direction", "uint8")
            self.LED2Energy = Register("LED2Energy", "uint8")
            self.LED2CreepEvent = Register("LED2CreepEvent", "uint8")
            self.AnticreepConstant = Register("AnticreepConstant", "uint16")
            self.AnticreepVoltage = Register("AnticreepVoltage", "uint16")
            self.AnticreepTimer = Register("AnticreepTimer", "uint32")
            self.ArcDetectiOnCounter = Register("ArcDetectiOnCounter", "uint8")
            self.MagneticSensorXaxis = Register("MagneticSensorXaxis", "int16")
            self.MagneticSensorYaxis = Register("MagneticSensorYaxis", "int16")
            self.MagneticSensorZaxis = Register("MagneticSensorZaxis", "int16")
            self.MagneticSensorNegXaxis = Register("MagneticSensorNegXaxis", "int16")
            self.MagneticSensorNegYaxis = Register("MagneticSensorNegYaxis", "int16")
            self.MagneticSensorNegZaxis = Register("MagneticSensorNegZaxis", "int16")
            self.AccelerometerXaxis = Register("AccelerometerXaxis", "int16")
            self.AccelerometerYaxis = Register("AccelerometerYaxis", "int16")
            self.AccelerometerZaxis = Register("AccelerometerZaxis", "int16")
            self.AccelerometerNegXaxis = Register("AccelerometerNegXaxis", "int16")
            self.AccelerometerNegYaxis = Register("AccelerometerNegYaxis", "int16")
            self.AccelerometerNegZaxis = Register("AccelerometerNegZaxis", "int16")
            self.RTCCalibration = Register("RTCCalibration", "int16")
            self.RTCTempCoeff = Register("RTCTempCoeff", "int16")
            self.OpticalUartBaudrate = Register("OpticalUartBaudrate", "uint8")
            self.DIUartBaudrate = Register("DIUartBaudrate", "uint8")
            self.NICUartBaudrate = Register("NICUartBaudrate", "uint8")
            self.ADCchannelNum = Register("ADCchannelNum", "uint8")
            self.VaADCChannelMapping = Register("VaADCChannelMapping", "uint8")
            self.IaADCChannelMapping = Register("IaADCChannelMapping", "uint8")
            self.VbADCChannelMapping = Register("VbADCChannelMapping", "uint8")
            self.IbADCChannelMapping = Register("IbADCChannelMapping", "uint8")
            self.VcADCChannelMapping = Register("VcADCChannelMapping", "uint8")
            self.IcADCChannelMapping = Register("IcADCChannelMapping", "uint8")
            self.VauxADCChannelMapping = Register("VauxADCChannelMapping", "uint8")
            self.IneutralADCChannelMapping = Register("IneutralADCChannelMapping", "uint8")
            self.Reserved0 = Register("Reserved0", "uint32")
            self.Reserved1 = Register("Reserved1", "uint32")
            self.Reserved2 = Register("Reserved2", "uint16")

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
        self.calibrationRegister = self.CalibrationRegister()
        self.meterSetupRegister = self.MeterSetup()

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
        logger.info('read calibration data')
        data_read = self.ser_client.get_cosem_data(1, "0;128;96;14;80;255", 2)            
        self.calibrationRegister.extract(data_read)
        if verbose == True:
            self.calibrationRegister.info()
    
    def write_calibration_data(self) -> bool:
        retry = 3
        calibrationBuffer = self.calibrationRegister.dataFrame()
        for i in range(retry):
            try:
                logger.debug(f'try to send data calibration. Attemp {i+1} of {retry}')
                # calibrationBuffer = self.calibrationRegister.dataFrame()
                result = self.ser_client.set_cosem_data(
                    class_id=1,
                    obis_code='0;128;96;14;80;255',
                    att_id=2,
                    dtype=9,
                    value=calibrationBuffer
                )
                return result
            except:
                if i < retry-1:
                    logger.warning(f'timeout. Data sent: {calibrationBuffer}')
                    self.logout()
                    self.login()
                    continue
                
        logger.critical(f'TIMEOUT!!. Turn off test bench')
        geny.close()
        raise TimeoutError
    
    def read_meter_setup(self, verbose=False) -> list:
        '''
            returns
                list of data read excess
        '''
        logger.info('reading meter setup')
        data_read = self.ser_client.get_cosem_data(1, "0;128;96;14;81;255", 2)
        logger.debug(f'meter setup data length: {len(data_read)} B')
        self.meterSetupRegister.extract(data_read)
        if verbose:
            self.meterSetupRegister.info()
        return data_read
    
    def configure_meter_setup(self):
        logger.info('Configuring meter setup')
        excessData = self.read_meter_setup()
        self.meterSetupRegister.CalibratiOndateTime.value = int(time.time())
        logger.info(f'Set time epoch: {self.meterSetupRegister.CalibratiOndateTime.value} second')
        self.meterSetupRegister.MeterForm.value = 133
        self.meterSetupRegister.MeterClass.value = 5
        self.meterSetupRegister.FrequencySelection.value = 0
        self.meterSetupRegister.MeterType.value = 0
        self.meterSetupRegister.MeterVoltageType.value = 0
        self.meterSetupRegister.MeterPowerSupplyType.value = 1
        self.meterSetupRegister.ServicesenseMode.value = 0
        
        logger.info('Constructing data frame')
        meterSetupBuffer = self.meterSetupRegister.dataFrame()
        # NOTE: Different byte size and unknown CRC calculation type
        meterSetupBuffer = [249, 0, 81, 45, 133, 5, 0, 0, 0, 0, 255, 5, 2, 3, 10, 0, 0, 45, 0, 45, 0, 0, 0, 0, 4, 3, 1, 0, 10, 0, 0, 45, 0, 45, 0, 0, 0, 0, 4, 3, 3, 0, 182, 9, 120, 5, 0, 64, 126, 5, 20, 96, 2, 32, 11, 8, 8, 96, 7, 224, 4, 144, 28, 10, 0, 10, 0, 10, 0, 246, 255, 246, 255, 246, 255, 0, 0, 163, 1, 0, 0, 0, 8, 2, 5, 1, 4, 0, 6, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 141, 229, 0, 250, 0, 250, 0, 0]
        logger.debug(f'meter setup data length: {len(meterSetupBuffer)} B')
        
        logger.info('Sending data frame')
        result = self.ser_client.set_cosem_data(1, "0;128;96;14;81;255", 2, 9, meterSetupBuffer)
        logger.info(f'Result: {result}')
    
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
        
    def calibrateVoltageAndCurrent(self, genySamplingFeedback):
        logger.info('fetching calibration register')
        self.read_calibration_data()
        
        errorBefore = []
        errorAfter = []
        
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
            meterMeasurement = self.fetch_register(instanRegister)
            prevGain = target[1].value
            genyFeedback = target[2]
            
            # calculate error before
            currentError = ((genyFeedback - meterMeasurement) / genyFeedback) * 100
            errorBefore.append(currentError)
            
            # calculate new gain
            logger.info(f'Calculate new gain for {target[1].name}')
            newGain = (prevGain * genyFeedback) / meterMeasurement
            newGain = int(newGain)
            logger.info(f'Apply new gain for {target[1].name} from {target[1].value} to {newGain}')
            target[1].value = newGain

        result = self.write_calibration_data()
        logger.info(f'set calibration register. result: {result}')
        
        if result == 0:
            for target in targets:
                instanRegister = target[0]
                meterMeasurement = self.fetch_register(instanRegister)
                prevGain = target[1].value
                genyFeedback = target[2]
                
                # calculate error before
                currentError = ((genyFeedback - meterMeasurement) / genyFeedback) * 100
                errorAfter.append(currentError)
        logger.info(f'Error Before: {errorBefore}')
        logger.info(f'Error After : {errorAfter}')        
    
    def calibratePowerActive(self, genySamplingFeedback):
        logger.info('fetching calibration register')
        self.read_calibration_data()
        
        errorBefore = []
        errorAfter = []
        
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
            
            # calculate error before
            currentError = ((genyFeedback - meterMeasurement) / genyFeedback) * 100
            errorBefore.append(currentError)
            
            # calculate new gain
            logger.info(f'Calculate new gain for {target[1].name}')
            newGain = (prevGain * genyFeedback) / meterMeasurement
            logger.debug(f'PrefGain: {prevGain} GenyFeedback: {genyFeedback} MeterMeasurement: {meterMeasurement}')
            newGain = int(newGain)
            logger.info(f'Apply new gain for {target[1].name} from {target[1].value} to {newGain}')
            target[1].value = newGain

        result = self.write_calibration_data()
        logger.info(f'set calibration register. result: {result}')
        
        if result == 0:
            for target in targets:
                instanRegister = target[0]
                meterMeasurement = self.fetch_register(instanRegister)
                prevGain = target[1].value
                genyFeedback = target[2]
                
                # calculate error before
                currentError = ((genyFeedback - meterMeasurement) / genyFeedback) * 100
                errorAfter.append(currentError)        
        logger.info(f'Error Before: {errorBefore}')
        logger.info(f'Error After : {errorAfter}')
    
    def fetch_register(self, register):
        logger.info('Fetch instant register value')
        
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
        return register.value


# MAIN PROGRAM START HERE
if __name__ == '__main__':
    logger.info('SOFTWARE INITIALIZATION')
    geny = GenyTestBench('/dev/ttyUSB4', 115200)
    meter = Calibration('/dev/ttyUSB0')

    logger.info('TURNING ON METER')
    geny.close()
    time.sleep(2)
    geny.open()
    geny.setMode(GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION)
    geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
    geny.setElementSelector(ElementSelector.EnergyErrorCalibration._COMBINE_ALL)
    geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
    geny.setPowerFactor(60, inDegree=True)
    geny.setVoltage(220)
    geny.setCurrent(5)
    geny.setCalibrationConstants(1000, 5)
    logger.debug('APPLY CONFIGURATION')
    geny.apply()
    logger.info('WAIT METER FOR BOTTING (10 second)')    
    time.sleep(15)
        
    logger.info('LOGIN TO METER') 
    try:
        meter.logout()
    except:
        pass
    meter.login()
    
    # STEP 1: Configure meter setup
    # NOTE: Length of meter setup not match (101 Bytes instead of 109 Bytes). There is CRC that need to be update. Currently using hardcoded configuration from HW5+ software
    logger.info('CONFIGURE METER')
    setupRetryAttemp = 2
    for i in range(setupRetryAttemp):
        try:
            logger.info(f'Try to configure meter setup. Attemp {i+1} of {setupRetryAttemp}')
            meter.configure_meter_setup()
            break
        except:
            if i<setupRetryAttemp-1:
                meter.logout()
                meter.login()
        if i == setupRetryAttemp-1:
            geny.close()
    
    # STEP 2: Calibrate Vrms and Irms
    logger.info('CALIBRATING Vrms Irms')
    meter.read_calibration_data()
    readBackRegisters = geny.readBackSamplingData()
    meter.calibrateVoltageAndCurrent(readBackRegisters)
    
    # STEP 3: Calibrate Power Active
    logger.info('CALIBRATING POWER ACTIVE')
    meter.read_calibration_data()
    readBackRegisters = geny.readBackSamplingData()
    meter.calibratePowerActive(readBackRegisters)
    for i in range(3):
        print('Reading errors')
        geny.readBackError(verbose=True)
        time.sleep(1)
    
    # STEP x: Finishing
    logger.info('FINISHING')
    meter.logout()
    geny.close()