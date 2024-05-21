class TestBench:
    def __init__(self):
        pass
    
    def open(serialPort:str, baudrate:int, aditionalInfo) -> bool:
        '''
            Attach serial port to test bench. Raise Exception if failed
        '''
        return True
    
    def close(self) -> bool:
        '''
            Close geny connection
        '''
        return True

    def CloseAll(self):
        '''
            Close test bench connections
        '''
    
    # Test bench parameter setup
    def getReadBack(self)->dict:
        return {}
    
    def setVoltage(self, nominal:float)->bool:
        '''
            Set voltage for all phase
        '''
        return True
        
    def setCurrent(self, nominal:float)->bool:
        '''
            Set current for all phase
        '''
        return True
    
    def setPhase(self, name:float)->bool:
        '''
            Set Voltage-Current phase for all phase
        '''
        return True
        
    def setFrequency(self, nominal:float)->bool:
        '''
            Set frequency for all phase
        '''
        return True