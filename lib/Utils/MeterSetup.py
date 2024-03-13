from .Register import Register, RegisterWrapper

class MeterSetup(RegisterWrapper):
    def __init__(self):
        self.CalibratiOndateTime = Register('CalibratiOndateTime', 'uint32', 2147516416)
        self.MeterForm = Register('MeterForm', 'uint8', 0)
        self.MeterClass = Register('MeterClass', 'uint8', 128)
        self.FrequencySelection = Register('FrequencySelection', 'uint8', 0)
        self.MeterType = Register('MeterType', 'uint8', 128)
        self.MeterVoltageType = Register('MeterVoltageType', 'uint8', 0)
        self.MeterPowerSupplyType = Register('MeterPowerSupplyType', 'uint8', 128)
        self.ServicesenseMode = Register('ServicesenseMode', 'uint8', 0)
        self.VACalculatiOnConfig = Register('VACalculatiOnConfig', 'uint8', 128)
        self.WattCalculatiOnConfig = Register('WattCalculatiOnConfig', 'uint8', 232)
        self.VARCalculatiOnConfig = Register('VARCalculatiOnConfig', 'uint8', 128)
        self.LED1PulseWeight = Register('LED1PulseWeight', 'uint16', 33000)
        self.LED1PulseOnTime = Register('LED1PulseOnTime', 'uint16', 33000)
        self.LED1PulseOffTime = Register('LED1PulseOffTime', 'uint16', 33000)
        self.LED1DebugData = Register('LED1DebugData', 'uint32', 1900573000)
        self.LED1Phase = Register('LED1Phase', 'uint8', 72)
        self.LED1Direction = Register('LED1Direction', 'uint8', 113)
        self.LED1Energy = Register('LED1Energy', 'uint8', 0)
        self.LED1CreepEvent = Register('LED1CreepEvent', 'uint8', 0)
        self.LED2PulseWeight = Register('LED2PulseWeight', 'uint16', 0)
        self.LED2PulseOnTime = Register('LED2PulseOnTime', 'uint16', 0)
        self.LED2PulseOffTime = Register('LED2PulseOffTime', 'uint16', 0)
        self.LED2DebugData = Register('LED2DebugData', 'uint32', 0)
        self.LED2Phase = Register('LED2Phase', 'uint8', 0)
        self.LED2Direction = Register('LED2Direction', 'uint8', 0)
        self.LED2Energy = Register('LED2Energy', 'uint8', 0)
        self.LED2CreepEvent = Register('LED2CreepEvent', 'uint8', 0)
        self.AnticreepConstant = Register('AnticreepConstant', 'uint16', 0)
        self.AnticreepVoltage = Register('AnticreepVoltage', 'uint16', 0)
        self.AnticreepTimer = Register('AnticreepTimer', 'uint32', 0)
        self.ArcDetectiOnCounter = Register('ArcDetectiOnCounter', 'uint8', 0)
        self.MagneticSensorXaxis = Register('MagneticSensorXaxis', 'int16', 0)
        self.MagneticSensorYaxis = Register('MagneticSensorYaxis', 'int16', 0)
        self.MagneticSensorZaxis = Register('MagneticSensorZaxis', 'int16', 0)
        self.MagneticSensorNegXaxis = Register('MagneticSensorNegXaxis', 'int16', 0)
        self.MagneticSensorNegYaxis = Register('MagneticSensorNegYaxis', 'int16', 0)
        self.MagneticSensorNegZaxis = Register('MagneticSensorNegZaxis', 'int16', 0)
        self.AccelerometerXaxis = Register('AccelerometerXaxis', 'int16', 0)
        self.AccelerometerYaxis = Register('AccelerometerYaxis', 'int16', 0)
        self.AccelerometerZaxis = Register('AccelerometerZaxis', 'int16', 0)
        self.AccelerometerNegXaxis = Register('AccelerometerNegXaxis', 'int16', 0)
        self.AccelerometerNegYaxis = Register('AccelerometerNegYaxis', 'int16', 0)
        self.AccelerometerNegZaxis = Register('AccelerometerNegZaxis', 'int16', 0)
        self.RTCCalibration = Register('RTCCalibration', 'int16', 0)
        self.RTCTempCoeff = Register('RTCTempCoeff', 'int16', 14464)
        self.OpticalUartBaudrate = Register('OpticalUartBaudrate', 'uint8', 1)
        self.DIUartBaudrate = Register('DIUartBaudrate', 'uint8', 83)
        self.NICUartBaudrate = Register('NICUartBaudrate', 'uint8', 7)
        self.ADCchannelNum = Register('ADCchannelNum', 'uint8', 0)
        self.VaADCChannelMapping = Register('VaADCChannelMapping', 'uint8', 0)
        self.IaADCChannelMapping = Register('IaADCChannelMapping', 'uint8', 0)
        self.VbADCChannelMapping = Register('VbADCChannelMapping', 'uint8', 0)
        self.IbADCChannelMapping = Register('IbADCChannelMapping', 'uint8', 0)
        self.VcADCChannelMapping = Register('VcADCChannelMapping', 'uint8', 0)
        self.IcADCChannelMapping = Register('IcADCChannelMapping', 'uint8', 0)
        self.VauxADCChannelMapping = Register('VauxADCChannelMapping', 'uint8', 0)
        self.IneutralADCChannelMapping = Register('IneutralADCChannelMapping', 'uint8', 0)
        self.SLBMode = Register('SLBMode', 'uint8', 128)
        self.BoardVersion = Register('BoardVersion', 'uint8', 36)
        self.Reserved0 = Register('Reserved0', 'uint16')
        self.Reserved1 = Register('Reserved1', 'uint16')
        self.Reserved2 = Register('Reserved2', 'uint16')
        self.Reserved3 = Register('Reserved3', 'uint16')
        self.CRC = Register('CRC', 'uint16')
