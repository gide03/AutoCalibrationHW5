import math
from datetime import datetime, timedelta
from serial import Serial

from typing import Union
from .GenyUtil import VoltageRange, VoltageRangeError, ElementSelector, PowerSelector
from .GenyUtil import ResponseDataFrame
from .src.SerialMonitor import SerialMonitor
from .src.ErrorCalibration import EnergyErrorCalibration
from .src.GenySystemCommand import GenySys

class GenyTestBench(GenySys):
    class Mode:
        ENERGY_ERROR_CALIBRATION = 1
            
    def __init__(self, usbport, baudrate:int=115200):
        super().__init__()
        
        self.response = ResponseDataFrame()
        
        self.usbport = usbport
        self.baudrate = baudrate
        
        self.mode = GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION
        self.serialMonitor = SerialMonitor(self.usbport, self.baudrate, self.onSerialReceived)
        self.energyErrorCalibration = EnergyErrorCalibration()
        
        self.documentation = {}
        
        # Set mode
        self.setMode(self.mode)
    
    def setMode(self, mode:Mode):
        self.mode = mode
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            pass
    
    # Callback function
    def onSerialReceived(self, dataframe:bytearray):
        # print('[onSerialReceived] received incoming data')
        # print(dataframe)
        pass


    # API
    def getSerial(self)->Serial:
        '''
            Get Serial object
        '''
        return self.serialMonitor.ser
    
    def open(self):
        print('[GenyTestBench] Establishing connection to geny')
        print('[GenyTestBench] Start monitor')
        self.serialMonitor.startMonitor()
        
        buffer = self.connect()
        result = self.serialMonitor.transaction(buffer)
        if result == b'':
            raise TimeoutError
        
        self.response.extractDataFrame(result)
        if self.response.getErrorCode() == 0:
            return True
        return False
    
    def close(self):
        buffer = self.disconnect()
        result = self.serialMonitor.transaction(buffer)
        try:
            self.response.extractDataFrame(result)
            if self.response.getErrorCode() == 0:
                self.serialMonitor.stopMonitor()
                return True
            self.serialMonitor.stopMonitor()
            return False
        except:
            self.serialMonitor.stopMonitor()
            return False
    
    def setElementSelector(self, elementSelector:[ElementSelector.EnergyErrorCalibration, ElementSelector.ThreePhaseAcStandard]):
        '''
            combine or separate element selction
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            self.energyErrorCalibration.setElementSelector(elementSelector)

    def setPowerSelector(self, powerSelector:PowerSelector):
        '''
            power selection setting
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            self.energyErrorCalibration.setPowerSelector(powerSelector)
    
    def setVoltageRange(self, voltageRange:Union[VoltageRange.YC99T_5C, VoltageRange.YC99T_3C]):
        '''
            Set voltage range
            
            parameters:
                voltagerRange (int|Util.VoltageRange) voltage range. if voltage register is exceed voltage range, it will raise exception
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            if self.energyErrorCalibration.voltage > voltageRange.nominal:
                raise VoltageRangeError(f'Voltage range is exceed from voltage range you had set. Consider to set voltage first before set the voltage range')
            self.energyErrorCalibration.setVoltageRange(voltageRange)
    
    def setVoltage(self, voltage:float):
        '''
            Set voltage amplitude to corresponding mode
            
            parameters:
                voltage (float) aplitude of voltage. Raise exception if voltage range is exceed voltageRange
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            voltageRangeNominal = self.energyErrorCalibration.voltageRange.nominal
            if voltage > voltageRangeNominal:
                raise VoltageRangeError(f'Voltage set should not exceed {voltageRangeNominal}, or you could set the voltage range larger')            
            self.energyErrorCalibration.setVoltage(voltage)

    def setCurrent(self, current:float):
        '''
            Set current amplitude to corresponding mode
            
            parameters:
                current (float) aplitude of current. Raise exception if current range is exceed currentRange
                elementSelector (Util.ElementSelector) channel selection for Geny to transmit current. `Please consider match the selection and Geny's mode you've been set`
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            currentRangeNominal = self.energyErrorCalibration.currentRange.nominal
            print(f'Current RANGE Nominal: {currentRangeNominal}')
            if current > currentRangeNominal:
                raise VoltageRangeError(f'Current set should not exceed {currentRangeNominal}, or you could set the current range larger')
            self.energyErrorCalibration.setCurrent(current)
    
    def setFrequency(self, frequency:float):
        '''
            parameters:
                frequency (float) the signal frequency
        '''
        self.frequency = frequency
    
    def setPowerFactor(self, value:float, inDegree:bool=False):
        '''
            params:
                value (float) power factor input
                inDegree (bool) if True the value will be considered as degree and will be convert to power factor
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            powerFactor = value
            if inDegree:
                powerFactor = math.cos(math.radians(value))
            
            self.energyErrorCalibration.setPowerFactor(powerFactor)
    
    def setPowerFactorUnit(self, value:EnergyErrorCalibration.PFUnit):
        '''
            params:
                value (int|EnergyErrorCalibration.PFUnit) enumeration of power factor unit (There are No Unit, L, C), refer to geny documentation
        '''
        self.energyErrorCalibration.setPowerFactorUnit(value)
    
    def setCalibrationConstants(self, meterConstant:int, cycle:int):
        '''
            parameters:
                meterConstant (int) meter LED blink constant per energy unit
                value (int) number of measurement cycles
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            self.energyErrorCalibration.setCalibrationConstants(meterConstant, cycle)
        
    def apply(self):
        '''
            Apply configuration on test bench
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            buffer = self.energyErrorCalibration.setTestCommandForm(verbose=True)
            result = self.serialMonitor.transaction(buffer)
            self.response.extractDataFrame(result)
            if self.response.getErrorCode() == 0:
                return True
            return False
        
    def readBackSamplingData(self, verbose=False):
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            samplingRegister = None
            for i in range(2):
                try:
                    buffer = self.energyErrorCalibration.readbackSampling()
                    result = self.serialMonitor.transaction(buffer)
                    # print(f'Transaction result: {result}')
                    self.response.extractDataFrame(result)
                        
                    samplingRegister = self.energyErrorCalibration.readbackSamplingRegister.extractResponseDataFrame(self.response)
                    # print(f'Sampling register: {samplingRegister}')
                    if verbose == True:
                        print('================================')
                        print('READ BACK SAMPLING')
                        print('================================')
                        for reg in samplingRegister:
                            print(f'{reg.name} -> {reg.value}')
                    break
                except:
                    continue
            # print(f'Sampling Register: {samplingRegister}')
            if samplingRegister != None:
                return vars(self.energyErrorCalibration.readbackSamplingRegister)
            raise TimeoutError
            
    def readBackError(self, verbose=False, timeout=100):
        '''
            If test bench is not ready to send data:
            - For type YC99T-3C each command will answered right after send the command with empty data field
            - For type YC99T-5C each command will blocked until testbench return data stream
        '''
        if self.mode == GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION:
            t0 = datetime.now()
            tout = timedelta(seconds=timeout)
            while datetime.now() - t0 < tout:
                # try:
                buffer = self.energyErrorCalibration.readbackErrorSampling()
                result = self.serialMonitor.transaction(buffer, timeout=20)
                self.response.extractDataFrame(result)
                if len(self.response.DATA) == 0:
                    continue
                
                errorRegister = self.energyErrorCalibration.errorSamplingRegister.extranctResponseDataFrame(self.response)                
                if verbose == True:
                    print('================================')
                    print('READ BACK ERROR')
                    print('================================')
                    for reg in errorRegister:
                        if isinstance(reg.dtype, float):
                            print(f'{reg.name} -> {reg.value:.5f}')
                        else:
                            print(f'{reg.name} -> {reg.value}')
                return errorRegister
                # except:
                #     pass
        

if __name__ == '__main__':
    import time
    
    geny = GenyTestBench('COM6', 115200)
    geny.setMode(GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION)
        
    def login_logout():
        print('[login_logout] opening port')
        print(geny.open())
        print('[login_logout] closing port')
        print(geny.close())
        exit()

    def apply_voltage():
        print('[apply_voltage] opening port')
        print(geny.open())
        print('[apply_voltage] set power selector')
        geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
        
        # channel selector
        elementSelector = (
            ElementSelector.EnergyErrorCalibration._A_ELEMENT,
            ElementSelector.EnergyErrorCalibration._B_ELEMENT,
            ElementSelector.EnergyErrorCalibration._C_ELEMENT,
            ElementSelector.EnergyErrorCalibration._COMBINE_ALL
        )
        for element in elementSelector:
            print(f'[apply_voltage] set channel selector: {element}')        
            geny.setElementSelector(element)        
            print('[apply_voltage] set voltage range')
            geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
            print('[apply_voltage] set voltage')
            geny.setVoltage(220)
            print('[apply_voltage] apply test bench configuration')
            result = geny.apply()
            print(f'[apply_voltage] result: {result}')
            if result == False:
                print('[apply_voltage] could not satisfied your command')
                print('[apply_voltage] closing port')
                geny.close()
                exit(1)
            
            input('Enter to continue')
            timeWait = 10
            for i in range(timeWait):
                print(f'[apply_voltage] wait {timeWait-1-i}')
                time.sleep(1)
        print('[apply_voltage] closing port')
        geny.close()

    def apply_current():
        print('[apply_voltage] opening port')
        print(geny.open())
        print('[apply_voltage] set power selector')
        geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
        
        # channel selector
        elementSelector = (
            ElementSelector.EnergyErrorCalibration._A_ELEMENT,
            ElementSelector.EnergyErrorCalibration._B_ELEMENT,
            ElementSelector.EnergyErrorCalibration._C_ELEMENT,
            ElementSelector.EnergyErrorCalibration._COMBINE_ALL
        )
        for element in elementSelector:
            print(f'[apply_voltage] set channel selector: {element}')        
            geny.setElementSelector(element)        
            print('[apply_voltage] set voltage range')
            geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
            print('[apply_voltage] set voltage')
            geny.setVoltage(220)
            print('[apply_voltage] set current')
            geny.setCurrent(5)
            print('[apply_voltage] apply test bench configuration')
            result = geny.apply()
            print(f'[apply_voltage] result: {result}')
            if result == False:
                print('[apply_voltage] could not satisfied your command')
                print('[apply_voltage] closing port')
                geny.close()
                exit(1)
            
            input('Enter to continue')
            timeWait = 10
            for i in range(timeWait):
                print(f'[apply_voltage] wait {timeWait-1-i}')
                time.sleep(1)
        print('[apply_voltage] closing port')
        geny.close()
    
    def readback_sampling_data():
        print('[apply_voltage] opening port')
        print(geny.open())
        print('[apply_voltage] set power selector')
        geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
        
        # channel selector
        elementSelector = (
            ElementSelector.EnergyErrorCalibration._A_ELEMENT,
            ElementSelector.EnergyErrorCalibration._B_ELEMENT,
            ElementSelector.EnergyErrorCalibration._C_ELEMENT,
            ElementSelector.EnergyErrorCalibration._COMBINE_ALL
        )
        for element in elementSelector:
            print(f'[apply_voltage] set channel selector: {element}')        
            geny.setElementSelector(element)        
            print('[apply_voltage] set voltage range')
            geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
            print('[apply_voltage] set voltage')
            geny.setVoltage(220)
            print('[apply_voltage] set current')
            geny.setCurrent(5)
            print('[apply_voltage] apply test bench configuration')
            result = geny.apply()
            print(f'[apply_voltage] result: {result}')
            if result == False:
                print('[apply_voltage] could not satisfied your command')
                print('[apply_voltage] closing port')
                geny.close()
                exit(1)
            geny.readBackSamplingData(verbose = True)
            input('Enter to continue')
        print('[apply_voltage] closing port')
        geny.close()
    
    def apply_power_factor():
        print('[apply_voltage] opening port')
        print(geny.open())
        print('[apply_voltage] set power selector')
        geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
        
        # channel selector
        elementSelector = (
            ElementSelector.EnergyErrorCalibration._A_ELEMENT,
            ElementSelector.EnergyErrorCalibration._B_ELEMENT,
            ElementSelector.EnergyErrorCalibration._C_ELEMENT,
            ElementSelector.EnergyErrorCalibration._COMBINE_ALL
        )
        for element in elementSelector:
            print(f'[apply_voltage] set channel selector: {element}')        
            geny.setElementSelector(element)        
            print('[apply_voltage] set voltage range')
            geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
            print('[apply_voltage] set voltage')
            geny.setVoltage(220)
            print('[apply_voltage] set current')
            geny.setCurrent(5)
            print('[apply_voltage] set power factor')
            geny.setPowerFactor(75, inDegree=True)
            print('[apply_voltage] apply test bench configuration')
            result = geny.apply()
            print(f'[apply_voltage] result: {result}')
            if result == False:
                print('[apply_voltage] could not satisfied your command')
                print('[apply_voltage] closing port')
                geny.close()
                exit(1)
            geny.readBackSamplingData(verbose = True)
            input('Enter to continue')
        print('[apply_voltage] closing port')    
        geny.close()
        
    def readback_error_sampling():
        print('[apply_voltage] opening port')
        print(geny.open())
        print('[apply_voltage] set power selector')
        geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
        
        # channel selector
        elementSelector = (
            # ElementSelector.EnergyErrorCalibration._A_ELEMENT,
            # ElementSelector.EnergyErrorCalibration._B_ELEMENT,
            # ElementSelector.EnergyErrorCalibration._C_ELEMENT,
            ElementSelector.EnergyErrorCalibration._COMBINE_ALL,
        )
        for element in elementSelector:
            print(f'[apply_voltage] set channel selector: {element}')        
            geny.setElementSelector(element)        
            print('[apply_voltage] set voltage range')
            geny.setVoltageRange(VoltageRange.YC99T_5C._220V)
            print('[apply_voltage] set voltage')
            geny.setVoltage(220)
            print('[apply_voltage] set current')
            geny.setCurrent(10)
            print('[apply_voltage] set power factor')
            geny.setPowerFactor(40, inDegree=True)
            print('[apply_voltage] set calibration constants')
            geny.setCalibrationConstants(1000, 5)
            print('[apply_voltage] apply test bench configuration')
            result = geny.apply()
            print(f'[apply_voltage] result: {result}')
            if result == False:
                print('[apply_voltage] could not satisfied your command')
                print('[apply_voltage] closing port')
                geny.close()
                exit(1)
            geny.readBackSamplingData(verbose = True)
            geny.readBackError(verbose = True)
            input('Enter to continue')
        print('[apply_voltage] closing port')    
        geny.close()
    
    # Test Case
    login_logout()
    apply_voltage()
    apply_current()
    readback_sampling_data()
    apply_power_factor()
    readback_error_sampling()
    