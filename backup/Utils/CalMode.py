from .Register import Register, RegisterWrapper

class CalMode(RegisterWrapper):
    def __init__(self):
        self.Quantity = Register('Quantity', 'uint8', 0)
        self.Cycles = Register('Cycles', 'uint16', 0)
        self.CalimpA = Register('CalimpA', 'uint32', 0)
        self.CalremA = Register('CalremA', 'uint32', 0)
        self.CalimpB = Register('CalimpB', 'uint32', 0)
        self.CalremB = Register('CalremB', 'uint32', 0)
        self.CalimpC = Register('CalimpC', 'uint32', 0)
        self.CalremC = Register('CalremC', 'uint32', 0)
        self.CalimpN = Register('CalimpN', 'uint32', 0)
        self.CalremN = Register('CalremN', 'uint32', 0)
        self.Threshpulses = Register('Threshpulses', 'uint32', 0)
        self.CalStatus = Register('CalStatus', 'uint8', 0)
        self.VrmsA = Register('VrmsA', 'uint32', 0)
        self.IrmsA = Register('IrmsA', 'uint32', 0)
        self.VrmsB = Register('VrmsB', 'uint32', 0)
        self.IrmsB = Register('IrmsB', 'uint32', 0)
        self.VrmsC = Register('VrmsC', 'uint32', 0)
        self.IrmsC = Register('IrmsC', 'uint32', 0)
        self.IrmsN = Register('IrmsN', 'uint32', 0)