from .Register import Register, RegisterWrapper

class CalibrationRegister(RegisterWrapper):
    def __init__(self):
        self.ActiveGainPhA = Register('ActiveGainPhA', 'uint16', 0)
        self.ActiveGainPhB = Register('ActiveGainPhB', 'uint16', 0)
        self.ActiveGainPhC = Register('ActiveGainPhC', 'uint16', 0)
        self.ReActiveGainPhA = Register('ReActiveGainPhA', 'uint16', 0)
        self.ReActiveGainPhB = Register('ReActiveGainPhB', 'uint16', 0)
        self.ReActiveGainPhC = Register('ReActiveGainPhC', 'uint16', 0)
        self.IrmsGainPhA = Register('IrmsGainPhA', 'uint16', 0)
        self.IrmsGainPhB = Register('IrmsGainPhB', 'uint16', 0)
        self.IrmsGainPhC = Register('IrmsGainPhC', 'uint16', 0)
        self.IrmsGainNeutral = Register('IrmsGainNeutral', 'uint16', 0)
        self.VrmsGainPhA = Register('VrmsGainPhA', 'uint16', 0)
        self.VrmsGainPhB = Register('VrmsGainPhB', 'uint16', 0)
        self.VrmsGainPhC = Register('VrmsGainPhC', 'uint16', 0)
  
        self.FilterK1PhA = Register('FilterK1PhA', 'int16', 0)
        self.FilterK2PhA = Register('FilterK2PhA', 'int16', 0)
        self.FilterK3PhA = Register('FilterK3PhA', 'int16', 0)
        self.FilterK1PhB = Register('FilterK1PhB', 'int16', 0)
        self.FilterK2PhB = Register('FilterK2PhB', 'int16', 0)
        self.FilterK3PhB = Register('FilterK3PhB', 'int16', 0)
        self.FilterK1PhC = Register('FilterK1PhC', 'int16', 0)
        self.FilterK2PhC = Register('FilterK2PhC', 'int16', 0)
        self.FilterK3PhC = Register('FilterK3PhC', 'int16', 0)
        self.FilterGainslope = Register('FilterGainslope', 'int16', 0)
        self.TempK1V = Register('TempK1V', 'int16', 0)
        self.TempK2V = Register('TempK2V', 'int16', 0)
        self.TempK3V = Register('TempK3V', 'int16', 0)
        self.TempK1I = Register('TempK1I', 'int16', 0)
        self.TempK2I = Register('TempK2I', 'int16', 0)
        self.TempK3I = Register('TempK3I', 'int16', 0)
        self.TempK1ShiftVolt = Register('TempK1ShiftVolt', 'uint8', 0)
        self.TempK2ShiftVolt = Register('TempK2ShiftVolt', 'uint8', 0)
        self.TempK3ShiftVolt = Register('TempK3ShiftVolt', 'uint8', 0)
        self.TempK1ShiftCurr = Register('TempK1ShiftCurr', 'uint8', 0)
        self.TempK2ShiftCurr = Register('TempK2ShiftCurr', 'uint8', 0)
        self.TempK3ShiftCurr = Register('TempK3ShiftCurr', 'uint8', 0)
  
        self.NonLinearK1 = Register('NonLinearK1', 'int16', 0)
        self.NonLinearK2 = Register('NonLinearK2', 'int16', 0)
        self.NonLinearK3 = Register('NonLinearK3', 'int16', 0)
        self.NonLinearK4 = Register('NonLinearK4', 'int16', 0)
        self.NonLinearK5 = Register('NonLinearK5', 'int16', 0)
        self.NonLinearK6 = Register('NonLinearK6', 'int16', 0)
        self.NonLinearK7 = Register('NonLinearK7', 'uint16', 0)
        self.NonLinearBreakCurrA = Register('NonLinearBreakCurrA', 'uint16', 0)
        self.NonLinearBreakCurrB = Register('NonLinearBreakCurrB', 'uint16', 0)
        self.NonLinearK1Shift = Register('NonLinearK1Shift', 'uint8', 0)
        self.NonLinearK2Shift = Register('NonLinearK2Shift', 'uint8', 0)
        self.NonLinearK3Shift = Register('NonLinearK3Shift', 'uint8', 0)
        self.NonLinearK4Shift = Register('NonLinearK4Shift', 'uint8', 0)
        self.NonLinearK5Shift = Register('NonLinearK5Shift', 'uint8', 0)
        self.NonLinearK6Shift = Register('NonLinearK6Shift', 'uint8', 0)
        self.VrmsSlope = Register('VrmsSlope', 'int16', 0)
        self.VrmsOffset = Register('VrmsOffset', 'uint16', 0)
        self.CaliTemperature = Register('CaliTemperature', 'int16', 0)
        self.ActualTemperature = Register('ActualTemperature', 'int16', 0)
  
        self.PhDirectionA = Register('PhDirectionA', 'int8', 0)
        self.PhDirectionB = Register('PhDirectionB', 'int8', 0)
        self.PhDirectionC = Register('PhDirectionC', 'int8', 0)
        self.PhDirectionN = Register('PhDirectionN', 'int8', 0)
        self.PhaseDelayA = Register('PhaseDelayA', 'uint16', 0)
        self.PhaseDelayB = Register('PhaseDelayB', 'uint16', 0)
        self.PhaseDelayC = Register('PhaseDelayC', 'uint16', 0)
        self.PhaseDelayN = Register('PhaseDelayN', 'uint16', 0)
  
        self.FrquencyWindow = Register('FrquencyWindow', 'uint8', 0)
  
        self.AciveEnergyOffsetphA = Register('AciveEnergyOffsetphA', 'int16', 0)
        self.AciveEnergyOffsetphB = Register('AciveEnergyOffsetphB', 'int16', 0)
        self.AciveEnergyOffsetphC = Register('AciveEnergyOffsetphC', 'int16', 0)
        self.ReAciveEnergyOffsetphA = Register('ReAciveEnergyOffsetphA', 'int16', 0)
        self.ReAciveEnergyOffsetphB = Register('ReAciveEnergyOffsetphB', 'int16', 0)
        self.ReAciveEnergyOffsetphC = Register('ReAciveEnergyOffsetphC', 'int16', 0)
  
        self.tf_control = Register('tf_control', 'uint32', 0)
        self.tf_coeff_a0 = Register('tf_coeff_a0', 'int32', 0)
        self.tf_coeff_a1 = Register('tf_coeff_a1', 'int32', 0)
        self.tf_coeff_a2 = Register('tf_coeff_a2', 'int32', 0)
        self.tf_coeff_a3 = Register('tf_coeff_a3', 'int32', 0)
        self.tf_coeff_b1 = Register('tf_coeff_b1', 'int32', 0)
        self.tf_coeff_b2 = Register('tf_coeff_b2', 'int32', 0)
        self.tf_coeff_b3 = Register('tf_coeff_b3', 'int32', 0)