from .Register import Register, RegisterWrapper
from .CalibrationData import CalibrationRegister

class MeterSetup(RegisterWrapper):
    def __init__(self):
        self.CalibratiOndateTime = Register('CalibratiOndateTime', 'uint32', 0)
        self.MeterForm = Register('MeterForm', 'uint8', 2)
        self.MeterClass = Register('MeterClass', 'uint8', 5)
        self.FrequencySelection = Register('FrequencySelection', 'uint8', 1)
        self.MeterType = Register('MeterType', 'uint8', 0)
        self.MeterVoltageType = Register('MeterVoltageType', 'uint8', 3)
        self.MeterPowerSupplyType = Register('MeterPowerSupplyType', 'uint8', 1)
        self.ServicesenseMode = Register('ServicesenseMode', 'uint8', 255)
        self.VACalculatiOnConfig = Register('VACalculatiOnConfig', 'uint8', 5)
        self.WattCalculatiOnConfig = Register('WattCalculatiOnConfig', 'uint8', 2)
        self.VARCalculatiOnConfig = Register('VARCalculatiOnConfig', 'uint8', 3)

        self.BoardVersion = Register('BoardVersion', 'uint8', 4)
        self.SLBMode = Register('SLBMode', 'uint8', 0)

        self.Meter_SKU = Register('Meter_SKU', 'uint32', 754986240)
        self.LCD_Version = Register('LCD_Version', 'uint8', 5)
        self.LoadControlSets = Register('LoadControlSets', 'uint8', 1)
        self.Main_switch_bistable_open_halfms_pulse_width = Register('Main_switch_bistable_open_halfms_pulse_width', 'uint8', 1)
        self.Main_switch_bistable_close_halfms_pulse_width = Register('Main_switch_bistable_close_halfms_pulse_width', 'uint8', 0)
        self.Main_switch_pre_cross_halfms = Register('Main_switch_pre_cross_halfms', 'uint8', 255)
        self.Aux_switch_bistable_open_halfms_pulse_width = Register('Aux_switch_bistable_open_halfms_pulse_width', 'uint8', 255)
        self.Aux_switch_bistable_close_halfms_pulse_width = Register('Aux_switch_bistable_close_halfms_pulse_width', 'uint8', 255)
        self.Aux_switch_pre_cross_halfms = Register('Aux_switch_pre_cross_halfms', 'uint8', 255)
        self.LCR1_switch_bistable_open_halfms_pulse_width = Register('LCR1_switch_bistable_open_halfms_pulse_width', 'uint8', 10)
        self.LCR1_switch_bistable_close_halfms_pulse_width = Register('LCR1_switch_bistable_close_halfms_pulse_width', 'uint8', 0)
        self.LCR1_switch_pre_cross_halfms = Register('LCR1_switch_pre_cross_halfms', 'uint8', 0)
        self.LCR2_switch_bistable_open_halfms_pulse_width = Register('LCR2_switch_bistable_open_halfms_pulse_width', 'uint8', 45)
        self.LCR2_switch_bistable_close_halfms_pulse_width = Register('LCR2_switch_bistable_close_halfms_pulse_width', 'uint8', 0)
        self.LCR2_switch_pre_cross_halfms = Register('LCR2_switch_pre_cross_halfms', 'uint8', 45)

        self.ByteReserve0 = Register('ByteReserve0', 'uint8', 0)
        self.ByteReserve1 = Register('ByteReserve1', 'uint8', 0)
        self.ByteReserve2 = Register('ByteReserve2', 'uint8', 0)
        self.ByteReserve3 = Register('ByteReserve3', 'uint8', 0)
        self.ByteReserve4 = Register('ByteReserve4', 'uint8', 0)
        self.ByteReserve5 = Register('ByteReserve5', 'uint8', 0)
        self.ByteReserve6 = Register('ByteReserve6', 'uint8', 0)
        self.ByteReserve7 = Register('ByteReserve7', 'uint8', 0)

        self.AnticreepConstant = Register('AnticreepConstant', 'uint16', 2486)
        self.AnticreepVoltage = Register('AnticreepVoltage', 'uint16', 1400)
        self.AnticreepTimer = Register('AnticreepTimer', 'uint32', 92160000)

        self.ArcDetectiOnCounter = Register('ArcDetectiOnCounter', 'uint8', 20)
        self.MagneticSensorXaxis = Register('MagneticSensorXaxis', 'int16', 200)
        self.MagneticSensorYaxis = Register('MagneticSensorYaxis', 'int16', 200)
        self.MagneticSensorZaxis = Register('MagneticSensorZaxis', 'int16', 200)
        self.MagneticSensorNegXaxis = Register('MagneticSensorNegXaxis', 'int16', 200)
        self.MagneticSensorNegYaxis = Register('MagneticSensorNegYaxis', 'int16', 200)
        self.MagneticSensorNegZaxis = Register('MagneticSensorNegZaxis', 'int16', 200)
        self.AccelerometerXaxis = Register('AccelerometerXaxis', 'int16', 10)
        self.AccelerometerYaxis = Register('AccelerometerYaxis', 'int16', 10)
        self.AccelerometerZaxis = Register('AccelerometerZaxis', 'int16', 10)
        self.AccelerometerNegXaxis = Register('AccelerometerNegXaxis', 'int16', -10)
        self.AccelerometerNegYaxis = Register('AccelerometerNegYaxis', 'int16', -10)
        self.AccelerometerNegZaxis = Register('AccelerometerNegZaxis', 'int16', -10)

        self.RTCCalibration = Register('RTCCalibration', 'int16', 0)
        self.RTCTempCoeff = Register('RTCTempCoeff', 'int16', 419)

        self.OpticalUartBaudrate = Register('OpticalUartBaudrate', 'uint8', 1)
        self.DIUartBaudrate = Register('DIUartBaudrate', 'uint8', 4)
        self.NICUartBaudrate = Register('NICUartBaudrate', 'uint8', 4)
        self.ADCchannelNum = Register('ADCchannelNum', 'uint8', 8)

        self.VaADCChannelMapping = Register('VaADCChannelMapping', 'uint8', 2)
        self.IaADCChannelMapping = Register('IaADCChannelMapping', 'uint8', 5)
        self.VbADCChannelMapping = Register('VbADCChannelMapping', 'uint8', 1)
        self.IbADCChannelMapping = Register('IbADCChannelMapping', 'uint8', 4)
        self.VcADCChannelMapping = Register('VcADCChannelMapping', 'uint8', 0)
        self.IcADCChannelMapping = Register('IcADCChannelMapping', 'uint8', 6)
        self.VauxADCChannelMapping = Register('VauxADCChannelMapping', 'uint8', 3)
        self.IneutralADCChannelMapping = Register('IneutralADCChannelMapping', 'uint8', 8)

        self.RDS_Holdoff_seconds = Register('RDS_Holdoff_seconds', 'uint16', 1024)
        self.Line_Voltage_goodhreshold = Register('Line_Voltage_goodhreshold', 'uint16', 0)
        self.Line_Amps_flowinghreshold = Register('Line_Amps_flowinghreshold', 'uint16', 0)
        self.Line_Amps_deltaratiohreshold = Register('Line_Amps_deltaratiohreshold', 'uint16', 0)
        self.Cap_Voltagehreshold = Register('Cap_Voltagehreshold', 'uint16', 0)
        self.Lower_Cap_Voltagehreshold = Register('Lower_Cap_Voltagehreshold', 'uint16', 2305)

        self.Reserved = [Register('Reserved', 'uint16', 0) for i in range(67)]
        self.Crc = Register('Crc', 'uint16', 8386)
    
    def calRunningCRC16(self, dataFrame):
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

    def updateCRC(self, calibrationData:CalibrationRegister):
        df = calibrationData.dataFrame()
        df.extend(super().dataFrame())
        
        df.pop(-1)
        df.pop(-1)
        
        newCrc = self.calRunningCRC16(df)
        self.Crc.value = newCrc
        
        
        