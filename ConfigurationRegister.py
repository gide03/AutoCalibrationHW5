import struct
from typing import Union

class Register:
    byteSize = {
        'uint32': 4,
        'uint16': 2, 
        'uint8' : 1, 
        'int16' : 2,
        'int8' : 1,
    }
    
    def __init__(self, name, c_stringDtype:str) -> None:
        '''
            parameters:
            - c_stringDtype (str) example: 'uint32', 'uint16', 'uint8', 'int16'
            c_s
        '''
        self.name = name
        self.c_stringDtype = c_stringDtype
        self.value = None
        self.size = Register.byteSize[self.c_stringDtype]
        
    def setValueFromDf(self, dataFrame:list):
        '''
            Set value from dataframe, the dataframe will be converted to decimal form
        '''
        # Unsigned
        if self.c_stringDtype == 'uint8':
            self.value = dataFrame[0]
        elif self.c_stringDtype == 'uint16':
            self.value = Register.deserializeU16(dataFrame)
        elif self.c_stringDtype == 'uint32':
            self.value = Register.deserializeU32(dataFrame)
        
        # Signed
        elif self.c_stringDtype == 'int8':
            self.value = dataFrame[0]
        elif self.c_stringDtype == 'int16':
            self.value = Register.deserializeS16(dataFrame)
        elif self.c_stringDtype == 'int32':
            self.value = Register.deserializeS32(dataFrame)      
    
    def hex(self):
        '''
            Return its value in list (represented hex)
        '''
        # Unsigned
        if self.c_stringDtype == 'uint8':
            return [self.value]
        elif self.c_stringDtype == 'uint16':
            return Register.serializeU16(self.value)
        elif self.c_stringDtype == 'uint32':
            return Register.serializeU32(self.value)
        
        # Signed
        elif self.c_stringDtype == 'int8':
            return [self.value]
        elif self.c_stringDtype == 'int16':
            return Register.serializeS16(self.value)
        elif self.c_stringDtype == 'int32':
            return Register.serializeS32(self.value)

    # SERIALIZE and DESERIALIZE
    def serializeU32(iData):
        mArrayReturn = []
        mArrayReturn = list(struct.pack("<L", iData))
        return mArrayReturn

    def deserializeU32(iData):
        mReturn = []
        mReturn = struct.unpack("<L", bytearray(iData))
        return mReturn[0]

    def serializeS32(iData):
        mArrayReturn = []
        mArrayReturn = list(struct.pack("<l", iData))
        return mArrayReturn

    def deserializeS32(iData):
        mReturn = []
        mReturn = struct.unpack("<l", bytearray(iData))
        return mReturn[0]

    def serializeU16(iData):
        mArrayReturn = []
        mArrayReturn = list(struct.pack("<H", iData))
        return mArrayReturn

    def deserializeU16(iData):
        mReturn = []
        mReturn = struct.unpack("<H", bytearray(iData))
        return mReturn[0]

    def serializeS16(iData):
        mArrayReturn = []
        mArrayReturn = list(struct.pack("<h", iData))
        return mArrayReturn

    def deserializeS16(iData):
        mReturn = []
        mReturn = struct.unpack("<h", bytearray(iData))
        return mReturn[0]

    def serializeS08(iData):
        mArrayReturn = []
        mArrayReturn = list(struct.pack("<b", iData))
        return mArrayReturn

    def deserializeS08(iData):
        mReturn = []
        mReturn = struct.unpack("<b", bytearray(iData))
        return mReturn[0]

class RegisterWrapper:
    def info(self):
        objectList = vars(self)
        print('============== REGISTER INFO ==============')
        for regName in objectList:
            print(f'{regName}: {objectList[regName].value}')
    
    def byteSize(self)->int:
        '''
            bytesize of register wrapper
        '''
        objectList = vars(self)
        byteSize = sum([register.size for register in objectList])

    def extract(self, dataFrame:Union[list,tuple,bytearray]):
        objectList = vars(self)
        # byteSize = [objectList[register].size for register in objectList]
        # print(byteSize)
        # print(sum(byteSize))
        # if len(dataFrame) != byteSize:
            # raise Exception('dataFrame not valid')
        
        print('extracting dataFrame')
        for regName in objectList:
            register = objectList[regName]
            registerSize = register.size
            raw_value = [dataFrame.pop(0) for i in range(registerSize)]
            register.setValueFromDf(raw_value)
        
    def objectList(self):
        return vars(self)

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
        self.g_MQAcquisition_gainActiveE_phase_A = Register('g_MQAcquisition_gainActiveE_phase_A', 'uint16')
        self.g_MQAcquisition_gainActiveE_phase_B = Register('g_MQAcquisition_gainActiveE_phase_B', 'uint16')
        self.g_MQAcquisition_gainActiveE_phase_C = Register('g_MQAcquisition_gainActiveE_phase_C', 'uint16')
        self.g_MQAcquisition_gainReactiveE_phase_A = Register('g_MQAcquisition_gainReactiveE_phase_A', 'uint16')
        self.g_MQAcquisition_gainReactiveE_phase_B = Register('g_MQAcquisition_gainReactiveE_phase_B', 'uint16')
        self.g_MQAcquisition_gainReactiveE_phase_C = Register('g_MQAcquisition_gainReactiveE_phase_C', 'uint16')
        self.g_MQAcquisition_gainIrms_phase_A = Register('g_MQAcquisition_gainIrms_phase_A', 'uint16')
        self.g_MQAcquisition_gainIrms_phase_B = Register('g_MQAcquisition_gainIrms_phase_B', 'uint16')
        self.g_MQAcquisition_gainIrms_phase_C = Register('g_MQAcquisition_gainIrms_phase_C', 'uint16')
        self.g_MQAcquisition_gainIrms_neutral = Register('g_MQAcquisition_gainIrms_neutral', 'uint16')
        self.g_MQAcquisition_gainVrms_phase_A = Register('g_MQAcquisition_gainVrms_phase_A', 'uint16')
        self.g_MQAcquisition_gainVrms_phase_B = Register('g_MQAcquisition_gainVrms_phase_B', 'uint16')
        self.g_MQAcquisition_gainVrms_phase_C = Register('g_MQAcquisition_gainVrms_phase_C', 'uint16')
        self.g_MQPhaseFilter_k1_phase_A = Register('g_MQPhaseFilter_k1_phase_A', 'int8')
        self.g_MQPhaseFilter_k2_phase_A = Register('g_MQPhaseFilter_k2_phase_A', 'int8')
        self.g_MQPhaseFilter_k3_phase_A = Register('g_MQPhaseFilter_k3_phase_A', 'int8')
        self.g_MQPhaseFilter_k1_phase_B = Register('g_MQPhaseFilter_k1_phase_B', 'int8')
        self.g_MQPhaseFilter_k2_phase_B = Register('g_MQPhaseFilter_k2_phase_B', 'int8')
        self.g_MQPhaseFilter_k3_phase_B = Register('g_MQPhaseFilter_k3_phase_B', 'int8')
        self.g_MQPhaseFilter_k1_phase_C = Register('g_MQPhaseFilter_k1_phase_C', 'int8')
        self.g_MQPhaseFilter_k2_phase_C = Register('g_MQPhaseFilter_k2_phase_C', 'int8')
        self.g_MQPhaseFilter_k3_phase_C = Register('g_MQPhaseFilter_k3_phase_C', 'int8')
        self.g_MQPhaseFilter_gainSlope = Register('g_MQPhaseFilter_gainSlope', 'int8')
        self.Temperature_k1_V = Register('Temperature_k1_V', 'int8')
        self.Temperature_k2_V = Register('Temperature_k2_V', 'int8')
        self.Temperature_k3_V = Register('Temperature_k3_V', 'int8')
        self.Temperature_k1_I = Register('Temperature_k1_I', 'int8')
        self.Temperature_k2_I = Register('Temperature_k2_I', 'int8')
        self.Temperature_k3_I = Register('Temperature_k3_I', 'int8')
        self.Temperature_k1Shift_V = Register('Temperature_k1Shift_V', 'uint8')
        self.Temperature_k2Shift_V = Register('Temperature_k2Shift_V', 'uint8')
        self.Temperature_k3Shift_V = Register('Temperature_k3Shift_V', 'uint8')
        self.Temperature_k1Shift_I = Register('Temperature_k1Shift_I', 'uint8')
        self.Temperature_k2Shift_I = Register('Temperature_k2Shift_I', 'uint8')
        self.Temperature_k3Shift_I = Register('Temperature_k3Shift_I', 'uint8')
        self.g_NonLinear_k1 = Register('g_NonLinear_k1', 'int8')
        self.g_NonLinear_k2 = Register('g_NonLinear_k2', 'int8')
        self.g_NonLinear_k3 = Register('g_NonLinear_k3', 'int8')
        self.g_NonLinear_k4 = Register('g_NonLinear_k4', 'int8')
        self.g_NonLinear_k5 = Register('g_NonLinear_k5', 'int8')
        self.g_NonLinear_k6 = Register('g_NonLinear_k6', 'int8')
        self.g_NonLinear_k7 = Register('g_NonLinear_k7', 'uint16')
        self.g_NonLinear_Break_Current_0 = Register('g_NonLinear_Break_Current_0', 'uint16')
        self.g_NonLinear_Break_Current_1 = Register('g_NonLinear_Break_Current_1', 'uint16')
        self.g_NonLinear_k1_Shift = Register('g_NonLinear_k1_Shift', 'uint8')
        self.g_NonLinear_k2_Shift = Register('g_NonLinear_k2_Shift', 'uint8')
        self.g_NonLinear_k3_Shift = Register('g_NonLinear_k3_Shift', 'uint8')
        self.g_NonLinear_k4_Shift = Register('g_NonLinear_k4_Shift', 'uint8')
        self.g_NonLinear_k5_Shift = Register('g_NonLinear_k5_Shift', 'uint8')
        self.g_NonLinear_k6_Shift = Register('g_NonLinear_k6_Shift', 'uint8')
        self.Vrms_Slope = Register('Vrms_Slope', 'int8')
        self.Vrms_Offset = Register('Vrms_Offset', 'uint16')
        self.Temperature_Calibration_Temperature = Register('Temperature_Calibration_Temperature', 'int8')
        self.Temperature_Actual_Temp_At_Cal = Register('Temperature_Actual_Temp_At_Cal', 'int8')
        self.Phase_Direction_Phase_A = Register('Phase_Direction_Phase_A', 'int8')
        self.Phase_Direction_Phase_B = Register('Phase_Direction_Phase_B', 'int8')
        self.Phase_Direction_Phase_C = Register('Phase_Direction_Phase_C', 'int8')
        self.Phase_Direction_Phase_N = Register('Phase_Direction_Phase_N', 'int8')
        self.Phase_Delay_Phase_A = Register('Phase_Delay_Phase_A', 'uint16')
        self.Phase_Delay_Phase_B = Register('Phase_Delay_Phase_B', 'uint16')
        self.Phase_Delay_Phase_C = Register('Phase_Delay_Phase_C', 'uint16')
        self.Phase_Delay_PhaseN = Register('Phase_Delay_PhaseN', 'uint16')
        self.g_MQFrequency_window = Register('g_MQFrequency_window', 'uint8')
        self.g_MQMetrology_activeqties_energy_offset_phase_A = Register('g_MQMetrology_activeqties_energy_offset_phase_A', 'int8')
        self.g_MQMetrology_activeqties_energy_offset_phase_B = Register('g_MQMetrology_activeqties_energy_offset_phase_B', 'int8')
        self.g_MQMetrology_activeqties_energy_offset_phase_C = Register('g_MQMetrology_activeqties_energy_offset_phase_C', 'int8')
        self.g_MQMetrology_reactiveqties_energy_offset_phase_A = Register('g_MQMetrology_reactiveqties_energy_offset_phase_A', 'int8')
        self.g_MQMetrology_reactiveqties_energy_offset_phase_B = Register('g_MQMetrology_reactiveqties_energy_offset_phase_B', 'int8')
        self.g_MQMetrology_reactiveqties_energy_offset_phase_C = Register('g_MQMetrology_reactiveqties_energy_offset_phase_C', 'int8')
        self.tf_control = Register('tf_control', 'uint32')
        self.tf_coeff_a0 = Register('tf_coeff_a0', 'int32')
        self.tf_coeff_a1 = Register('tf_coeff_a1', 'int32')
        self.tf_coeff_a2 = Register('tf_coeff_a2', 'int32')
        self.tf_coeff_a3 = Register('tf_coeff_a3', 'int32')
        self.tf_coeff_b1 = Register('tf_coeff_b1', 'int32')
        self.tf_coeff_b2 = Register('tf_coeff_b2', 'int32')
        self.tf_coeff_b3 = Register('tf_coeff_b3', 'int32')
        

if __name__ == '__main__':
    buffer_meterSetup = [160, 249, 75, 45, 2, 5, 1, 0, 0, 0, 255, 5, 2, 3, 10, 0, 0, 45, 0, 45, 0, 0, 0, 0, 4, 3, 1, 1, 10, 0, 0, 45, 0, 45, 0, 0, 0, 0, 4, 3, 3, 1, 182, 9, 120, 5, 0, 64, 126, 5, 20, 96, 2, 32, 11, 8, 8, 96, 7, 224, 4, 144, 28, 10, 0, 10, 0, 10, 0, 246, 255, 246, 255, 246, 255, 0, 0, 164, 1, 0, 0, 0, 8, 2, 5, 1, 4, 0, 6, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 82, 154, 0, 250, 0, 250, 0, 0]
    meterSetup = MeterSetup()
    meterSetup.extract(buffer_meterSetup)
    meterSetup.info()
    
    buffer_calibrationRegister = [0, 128, 0, 128, 0, 128, 0, 128, 0, 128, 0, 128, 232, 128, 232, 128, 232, 128, 232, 128, 72, 113, 72, 113, 72, 113, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 56, 1, 83, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 36, 19, 32, 3, 255, 1, 1, 255, 250, 0, 250, 0, 250, 0, 250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 55, 246, 119, 0, 103, 72, 144, 255, 179, 2, 248, 255, 0, 0, 0, 0, 150, 1, 128, 255, 0, 0, 0, 0, 0, 0, 0, 0]
    calibrationRegsiter = CalibrationRegister()
    calibrationRegsiter.extract(buffer_calibrationRegister)
    calibrationRegsiter.info()