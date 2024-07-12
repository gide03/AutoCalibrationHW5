import struct
from typing import Union

class Register:
    byteSize = {
        'uint32': 4,
        'uint16': 2, 
        'uint8' : 1, 
        'int32' : 4,
        'int16' : 2,
        'int8' : 1,
    }
    
    def __init__(self, name, c_stringDtype:str, value=None) -> None:
        '''
            parameters:
            - c_stringDtype (str) example: 'uint32', 'uint16', 'uint8', 'int16'
            c_s
        '''
        self.name = name
        self.c_stringDtype = c_stringDtype
        self.value = value
        self.size = Register.byteSize[self.c_stringDtype]
    
    def set(self, value):
        self.value = value
        
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
            self.value = Register.deserializeS08(dataFrame)
        elif self.c_stringDtype == 'int16':
            self.value = Register.deserializeS16(dataFrame)
        elif self.c_stringDtype == 'int32':
            self.value = Register.deserializeS32(dataFrame)      
    
    def hex(self):
        '''
            Return its value in list (represented hex)
        '''
        try:
            # Unsigned
            if self.c_stringDtype == 'uint8':
                return [self.value]
            elif self.c_stringDtype == 'uint16':
                return Register.serializeU16(self.value)
            elif self.c_stringDtype == 'uint32':
                return Register.serializeU32(self.value)
            
            # Signed
            elif self.c_stringDtype == 'int8':
                return Register.serializeS08(self.value)
            elif self.c_stringDtype == 'int16':
                return Register.serializeS16(self.value)
            elif self.c_stringDtype == 'int32':
                return Register.serializeS32(self.value)
        except:
            print(f'Error at parsing: {self.name}. dtype: {self.c_stringDtype} value: {self.value}')
            exit()

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
    def info(self, verbose=False):
        objectList = vars(self)
        if verbose:
            print('============== REGISTER INFO ==============')
            for regName in objectList:
                register = objectList[regName]
                if isinstance(register, list):
                    print(f'{regName}: [{", ".join([str(i.value) for i in register])}]')
                else:
                    print(f'{regName}: {objectList[regName].value}')
        return vars(self)
    
    def byteSize(self)->int:
        '''
            bytesize of register wrapper
        '''
        objectList = vars(self)
        byteSize = 0
        for regName in objectList:
            # byteSize = sum([objectList[register].size for register in objectList])
            register = objectList[regName]
            if isinstance(register, list):
                for element in register:
                    byteSize += element.size
            else:
                byteSize += register.size
        return byteSize

    def extract(self, dataFrame:Union[list,tuple,bytearray]):
        objectList = vars(self)
        if len(dataFrame) < self.byteSize():
            raise Exception(f'data frame length not match. {len(dataFrame)} instead of {self.byteSize()}. data frame: {dataFrame}')
        
        # print('extracting dataFrame')
        for regName in objectList:
            register = objectList[regName]
            if isinstance(register, list):
                for element in register:
                    registerSize = element.size
                    raw_value = [dataFrame.pop(0) for i in range(registerSize)]
                    element.setValueFromDf(raw_value)
            else:
                registerSize = register.size
                raw_value = [dataFrame.pop(0) for i in range(registerSize)]
                register.setValueFromDf(raw_value)
        return dataFrame
        
    def dataFrame(self):
        objectList = vars(self)
        df = []
        for regName in objectList:
            register = objectList[regName]
            if isinstance(register, list):
                for element in register:
                    df.extend(element.hex())
            else:
                df.extend(register.hex())            
        return df
        
    def objectList(self):
        return vars(self)

if __name__ == '__main__':
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
            self.CRC = Register("CRC", 'uint16')
            self.Reserved3 = Register("Reserved3", 'uint16')
            self.Reserved4 = Register("Reserved4", 'uint16')
            

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
        

    # version 1
    buffer_meterSetup = [249, 0, 81, 45, 133, 5, 0, 0, 0, 0, 255, 5, 2, 3, 10, 0, 0, 45, 0, 45, 0, 0, 0, 0, 4, 3, 1, 0, 10, 0, 0, 45, 0, 45, 0, 0, 0, 0, 4, 3, 3, 0, 182, 9, 120, 5, 0, 64, 126, 5, 20, 96, 2, 32, 11, 8, 8, 96, 7, 224, 4, 144, 28, 10, 0, 10, 0, 10, 0, 246, 255, 246, 255, 246, 255, 0, 0, 163, 1, 0, 0, 0, 8, 2, 5, 1, 4, 0, 6, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 141, 229, 0, 250, 0, 250, 0, 0]   
    meterSetup = MeterSetup()   
    print(meterSetup.byteSize())
    meterSetup.extract(buffer_meterSetup)
    # meterSetup.info()
    
    # version 2
    # buffer_calibrationRegister = [0, 128, 0, 128, 0, 128, 0, 128, 0, 128, 0, 128, 232, 128, 232, 128, 232, 128, 232, 128, 72, 113, 72, 113, 72, 113, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 56, 1, 83, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 36, 19, 32, 3, 255, 1, 1, 255, 250, 0, 250, 0, 250, 0, 250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 55, 246, 119, 0, 103, 72, 144, 255, 179, 2, 248, 255, 0, 0, 0, 0, 150, 1, 128, 255, 0, 0, 0, 0, 0, 0, 0, 0]
    # calibrationRegister = CalibrationRegister()
    # print(f'BUFFER LENGTH: {len(buffer_calibrationRegister)}')
    # print(f'REGISTER BYTESIZE: {calibrationRegister.byteSize()}')
    # calibrationRegister.extract(buffer_calibrationRegister)
    # calibrationRegister.info()
    