'''
CALIBRATION PROCESS
1.	Attach the probes to Cal/programming pads.
2.	Apply 240 Volts at test amps with power factor (60 degree) to the meter.
3.	Apply 2s delay to allow meter to power up.
4.	The meter will power up with default calibration data.
5.	Write “Calibration Data” (OBIS 0.128.96.14.80.255) and ‘Meter Setup’ (OBIS 0.128.96.14.81.255) with default values to the meter according to the meter form, class, etc. from the meter bar code scan. Note to set RTC temperature coeff = 0.
6.	Read the temperature information from the meter (OBIS 1.0.96.9.0.255) and standard. Store the information for later averaging.
7.	Program LED pulse output (OBIS 0.128.96.6.8.255) to “No Pulse”, so that calibration mode can be used.
8.	Start calibration mode (OBIS 0.128.96.14.82.255) for PF Watts with a test time of 1.5s (90 cycles) with RTC output continue mode on (cal mode status = 1). 
9.	4Hz RTC pulses are enabled from RTC output after start pulse.
10.	Delay for test to complete.
11.	Read the instantaneous voltage and current from Cal Mode reading, temperature (OBIS 1.0.96.9.0.255) information from the meter and the calibration standard.  Read the RTC 4Hz frequency from the counter. 
12.	Average the temperature, voltage, current, and RTC frequency readings from both the meter and standard.
13.	Calculate the calibration constants such as gains, phase delays, RTC error. Check if all those constants are within the limit.
14.	Write the new constants via “Calibration Data” and ‘Meter Setup’ to the meter.
'''

'''
VERIFICATION PROCESS
1.	Verify that 240 Volts at test amps with power factor is applied to the meter. 
2.	Apply 2s delay for new constants running.
3.	Read all the calibration values and verify that they were updated correctly.
4.	Start calibration mode (OBIS 0.128.96.14.82.255) for Watts with a test time of 0.5s (30 cycles)
5.	Delay for test to complete.
6.	Read the result of the calibration mode command and store this data into the database as the PF Reading.
7.	Check if PF accuracies are within the limits. If the error is not within the 0.10%, adjust the phase delay, and redo the PF verification (step #1).
8.	Change the load to 240 Volts at Test Amps at Unity power factor.
9.	Apply 2s for meter and standard to stabilize.
10.	Start calibration mode for Watts with a test time of 0.5s (30 cycles).
11.	Delay for test to complete.
12.	Read the result of the Calibration mode command and store this data into the database as the FL Reading.
13.	Check if FL accuracies are within the limits. If the error is not within the 0.05%, adjust the energy gains, write new gains to ‘Calibration Data’. And redo verification from PF verification (step #1).
14.	Change the load to 240 Volts at Light Load at Unity power factor.
15.	Apply 3s for meter and standard to stabilize. 
16.	Start Calibration Mode for Watts with a test time of 1s (60 cycles) with RTC output continue mode off (cal mode status = 0).
17.	Delay for calibration mode to complete.
18.	Read the result of the calibration mode command and store this into the database as LL Reading.
'''

import pathlib
import site
import os
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import json
import serial
import config
import math
from time import sleep
from datetime import datetime, timedelta
from src.Logger import getLogger
from lib.TestBench.TestBench import TestBench
# from lib.TestBench.GenyApi import GenyApi
from lib.TestBench.GenyTestBench import GenyTestBench
from lib.TestBench.GenyUtil import ElementSelector, PowerSelector, VoltageRange

from lib.Utils.CalibrationData import CalibrationRegister
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalMode import CalMode
from lib.Utils.Register import Register

from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

PORT_GENY = '/dev/ttyUSB0'
PORT_METER = '/dev/ttyUSB1'

logger = getLogger('dev.log')
with open(f'{CURRENT_PATH}/configurations/CalibrationStep.json', 'r') as f:
    configFile = json.load(f)

def initDlmsClient() -> DlmsCosemClient:
    logger.info('Initialize DLMS client')
    myConfiguration = configFile['Environment']['Connectivity']['DlmsClient']
    serialPort = myConfiguration['SerialPort']
    baudRate = myConfiguration['BaudRate']
    interOctetTimeout = myConfiguration['InterOctetTimeout']
    inactivityTimeout = myConfiguration['InactivityTimeout']
    loginRetry = myConfiguration['LoginRetry']
    meterAddress = myConfiguration['MeterAddress']
    clientId = myConfiguration['ClientId']
    
    logger.info(f'serialPort:{serialPort}(Baud:{baudRate}); meter addr:{meterAddress} clientId:{clientId}')
    
    try:
        dlmsClient = DlmsCosemClient(
            port = serialPort,
            baudrate=baudRate,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=interOctetTimeout,
            inactivity_timeout=inactivityTimeout,
            login_retry=loginRetry,
            meter_addr=meterAddress,
            client_nb=clientId,
            address_size = AddrSize.ONE_BYTE
        )
        return dlmsClient
    except Exception as e:
        logger.warning(str(e))
        logger.critical('Failed to initialize DlmsClient. Process terminated')
        exit(1)
    
def initGenyClient() -> GenyTestBench:
    myConfiguration = configFile['Environment']['Connectivity']['TestBench']
    
    if not myConfiguration['UseGeny']:
        return
    
    serialPort = myConfiguration['SerialPort']
    baudRate = myConfiguration['BaudRate']
    
    geny = GenyTestBench(serialPort, baudRate)
    try:
        geny.close()
        sleep(3)
    except:
        pass
    
    try:
        # geny.open(serialPort, baudRate, GenyApi.GenyVersion.YC99T_5C)
        geny.open()
        return geny
    except Exception as e:
        logger.warning(str(e))
        logger.critical('Failed to initialize Geny test bench. Process terminated')
        exit(1)
    
def turnOnGeny(geny:GenyTestBench):
    logger.info('TURN ON GENY')
    
    # Get the configurations
    myConfiguration = configFile['step 1']
    if myConfiguration['isEnable'] == False:
        return
    
    parameters = myConfiguration['parameters']
    voltage = parameters['Voltage']
    current = parameters['Current']
    phase = parameters['Phase']
    frequency = parameters['Frequency']
    logger.info(f'Geny Parameters: V:{voltage}V I:{current}A Phase:{phase} Deg Freq:{frequency}Hz')
        
    # try:
    # geny.(
    #     isCommon=True,
    #     voltage=230,
    #     current=30,
    #     phase=60,
    #     frequency=50,
    #     meterConstant=1000,
    #     ring=3
    # )
    geny.setMode(GenyTestBench.Mode.ENERGY_ERROR_CALIBRATION)
    geny.setPowerSelector(PowerSelector._3P4W_ACTIVE)
    geny.setElementSelector(ElementSelector.EnergyErrorCalibration._COMBINE_ALL)
    geny.setVoltageRange(VoltageRange.YC99T_3C._380V)
    geny.setPowerFactor(60, inDegree=True)
    geny.setVoltage(230)
    geny.setCurrent(30)
    geny.apply()
    # geny.setCalibrationConstants(1000, 2)
    # except:
    #     logger.critical('Something wrong with Geny. Process terminated')
    #     exit(1)

def powerUpDelay():
    myConfiguration = configFile['step 2']
    if myConfiguration['isEnable'] == False:
        return
    
    delay = myConfiguration['parameters']['DelayTime']
    
    logger.info(f'Waiting for delay {delay}s')
    t = datetime.now()
    while datetime.now() - t < timedelta(seconds=delay):
        print(f'Power up delay {(datetime.now() - t).total_seconds() :.2f}/{delay}s', end='\r')

def checkCalibrationData(dlmsClient:DlmsCosemClient):
    '''
        Check calibration and meter setup, set it to default based on configuration json file
    '''
    myConfiguration = configFile['step 3']
    if not myConfiguration['isEnable']:
        return
    
    parameters = myConfiguration['parameters']
    flagSetToDefault = parameters['Set default value']
    
    logger.info('Check Calibration Data ')
    
    calibrationRegister = CalibrationRegister()
    meterSetupRegister = MeterSetup()
    
    cosem_calibrationData = config.CosemList.CalibarationData
    cosem_meterSetup = config.CosemList.MeterSetup
    
    # Read calibration data
    raw_calibrationData = dlmsClient.get_cosem_data(cosem_calibrationData.classId, cosem_calibrationData.obis, 2)
    raw_meterSetupData = dlmsClient.get_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2)
    
    isCalibrationDataDefault = (raw_calibrationData == calibrationRegister.dataFrame())
    logger.info(f'Calibration data is {"NOT" if not isCalibrationDataDefault else ""} in default')
    if not isCalibrationDataDefault:
        logger.debug('Data lookup')
        logger.debug(f'Default : {calibrationRegister.dataFrame()}')
        logger.debug(f'Read val: {raw_calibrationData}')
    
    isMeterSetupDefault = raw_meterSetupData == meterSetupRegister.dataFrame()
    logger.info(f'Meter setup is {"NOT" if not isMeterSetupDefault else ""} in default')
        
    if not isMeterSetupDefault:
        logger.debug('Data lookup')
        logger.debug(f'Default : {meterSetupRegister.dataFrame()}')
        logger.debug(f'Read val: {raw_meterSetupData}')
    
    # If flag to default
    if flagSetToDefault:
        logger.info('Write MeterSetup to default') 
        if isMeterSetupDefault and isCalibrationDataDefault:
            logger.info('Configuration already in default, skip process')
            return True
        
        result = writeCalibrationToDefault(dlmsClient)
        if result == False:
            logger.critical('Set calibration data to default FAILED')
            exit(1)
        return result
    else:
        logger.info('Write MeterMeterSetup based on configuration file')
        setValue = parameters['Default meter setup']
        meterSetupRegisters = meterSetupRegister.objectList()
        for keyName in setValue:
            value = setValue[keyName]
            logger.info(f'Change {keyName} from {meterSetupRegisters[keyName].value} to {value}')
            meterSetupRegisters[keyName].set(value)
        
        result = writeMeterSetup(dlmsClient, calibrationRegister, meterSetupRegister)
        if result == False:
            logger.critical('Set MeterSetup to default FAILED')
            exit(1)
    
    logger.info(f'Configure CalibrationData')
    setValue = parameters['Default calibration data']
    calibrationRegisters = calibrationRegister.objectList()
    for keyName in setValue:
        value = setValue[keyName]
        logger.info(f'Change {keyName} from {calibrationRegisters[keyName].value} to {value}')
        calibrationRegisters[keyName].set(value)
    writeCalibrationData(dlmsClient, calibrationRegister)
    
def writeCalibrationToDefault(dlmsClient:DlmsCosemClient):
    calibrationRegister = CalibrationRegister()
    meterSetupRegister = MeterSetup()
        
    # TODO: Write CalibrationData
    logger.info('Set CalibrationData to default')
    writeCalibrationData(dlmsClient, calibrationRegister)
    
    # TODO: Write MeterSetup
    logger.info('Set MeterSetup to default')
    writeMeterSetup(dlmsClient, calibrationRegister, meterSetupRegister)

def writeCalibrationData(dlmsClient:DlmsCosemClient, calibrationRegister:CalibrationRegister):
    cosem_calibrationData = config.CosemList.CalibarationData
    df = calibrationRegister.dataFrame()
    logger.info(f'Writing data. Data: {df}')
    result = dlmsClient.set_cosem_data(cosem_calibrationData.classId, cosem_calibrationData.obis, 2, CosemDataType.e_OCTET_STRING, df)
    if result == 0:
        logger.info(f'Write data SUCCESS')
        return True
    logger.critical(f'Write data FAILED. Error code ({result})')
    return False

def writeMeterSetup(dlmsClient:DlmsCosemClient, calibrationRegister:CalibrationRegister, meterSetup:MeterSetup):
    cosem_meterSetup = config.CosemList.MeterSetup
    
    # TODO: Apply MeterSetup values into register from JSON file
    # NOTE: Set RTC temperature coeff = 0
    meterSetup.RTCTempCoeff.set(0)        
    
    # TODO: Calculate new CRC
    meterSetup.updateCRC(calibrationRegister)
    df = meterSetup.dataFrame()
    logger.info(f'MeterSetup Data: {df}')
    result = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, CosemDataType.e_OCTET_STRING, df)
    if result == 0:
        logger.info(f'Write data SUCCESS')
        return True
    logger.critical(f'Write data FAILED. Error code ({result})')
    sleep(2)
    return False

def backupTemperatureData(dlmsClient:DlmsCosemClient):
    myConfiguration = configFile['step 4']
    if not myConfiguration['isEnable']:
        return
    
    parameters = myConfiguration['parameters']
    flagSaveToFile = parameters['isSaveToFile']

    cosem_temperature = config.CosemList.Temperature
    temperature = dlmsClient.get_cosem_data(cosem_temperature.classId, cosem_temperature.obis, 2)
    logger.info(f'Temperature: {temperature}')
    
    if flagSaveToFile == True:
        if not os.path.exists(f'{CURRENT_PATH}/appdata'):
            os.mkdir(f'{CURRENT_PATH}/appdata')
        
        filename = f'{CURRENT_PATH}/appdata/{parameters["filename"]}'
        logger.info(f'Store temperature to file. Path: {filename}')
        with open(filename, 'w') as f:
            json.dump({'temperature':temperature}, f)

def miscelaneousConfiguration(dlmsClient:DlmsCosemClient):
    myConfiguration = configFile['step 5']
    if not myConfiguration['isEnable']:
        return
    
    parameters = myConfiguration['parameters']
    flagNopulse = parameters['NoPulseParameter']
    
    cosem_Led1Config = config.CosemList.LED1Configuration
    cosem_Led2Config = config.CosemList.LED2Configuration
    
    # LED CONFIGURATION
    # NOTE: Read LED config to makesure we don't change other configurations
    logger.info('Read LED 1 configuration')
    led1Config = [10, 11520, 11520, 4, 3, 1, 0, 1, 0, 0, 0, 65535] # This magic value is hardcoded from manual test
    led2Config = [10, 11520, 11520, 4, 3, 2, 0, 1, 0, 0, 0, 65535] # This magic value is hardcoded from manual test
    logger.info('Read LED 1 configuration')
    led2Config = dlmsClient.get_cosem_data(cosem_Led2Config.classId, cosem_Led2Config.obis, 2)
    
    flag_setLed1 = True
    flag_setLed2 = True
    # TODO: Modify led config to No pulse (change index 6 to 0). Skip if already No Pulse
    if flag_setLed1:
        logger.info(f'Set LED1 configuration')
        valueLed_1 = [CosemDataType.e_STRUCTURE, [
            [CosemDataType.e_LONG_UNSIGNED, led1Config[0]],
            [CosemDataType.e_LONG_UNSIGNED, led1Config[1]],
            [CosemDataType.e_LONG_UNSIGNED, led1Config[2]],
            [CosemDataType.e_ENUM, led1Config[3]],
            [CosemDataType.e_ENUM, led1Config[4]],
            [CosemDataType.e_ENUM, led1Config[5]], 
            [CosemDataType.e_ENUM, led1Config[6]],
            [CosemDataType.e_ENUM, led1Config[7]],
            [CosemDataType.e_ENUM, led1Config[8]],
            [CosemDataType.e_ENUM, led1Config[9]],
            [CosemDataType.e_ENUM, led1Config[10]],
            [CosemDataType.e_LONG_UNSIGNED, led1Config[11]],
        ]]
        
        result = dlmsClient.set_cosem_data(cosem_Led1Config.classId, cosem_Led1Config.obis, 2, CosemDataType.e_STRUCTURE, valueLed_1[1])
        logger.info(f'Result: {"PASSED" if result == 0 else "FAILED"}')
    
    if flag_setLed2:
        logger.info(f'Set LED2 configuration')
        valueLed_2 = [CosemDataType.e_STRUCTURE, [
            [CosemDataType.e_LONG_UNSIGNED, led2Config[0]],
            [CosemDataType.e_LONG_UNSIGNED, led2Config[1]],
            [CosemDataType.e_LONG_UNSIGNED, led2Config[2]],
            [CosemDataType.e_ENUM, led2Config[3]],
            [CosemDataType.e_ENUM, led2Config[4]],
            [CosemDataType.e_ENUM, led2Config[5]], 
            [CosemDataType.e_ENUM, led2Config[6]],
            [CosemDataType.e_ENUM, led2Config[7]],
            [CosemDataType.e_ENUM, led2Config[8]],
            [CosemDataType.e_ENUM, led2Config[9]],
            [CosemDataType.e_ENUM, led2Config[10]],
            [CosemDataType.e_LONG_UNSIGNED, led2Config[11]],
        ]]
        
        result = dlmsClient.set_cosem_data(cosem_Led2Config.classId, cosem_Led2Config.obis, 2, CosemDataType.e_STRUCTURE, valueLed_2[1])
        logger.info(f'Result: {"PASSED" if result == 0 else "FAILED"}')    
    
    # KYZ CONFIGURATION
    logger.info('Configure KYZ to make sure the KYZ status is 0')
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
        readData = dlmsClient.get_cosem_data(1, kyz, 2)
        logger.info(f'Read result -- {readData}')
        if readData[-2] == 0:
            logger.info('Skip configuration because the status already 0')
            continue
        readData[-2] = 0
        for idx, (data,dtype) in enumerate(zip(readData, kyz_dtype)):
            temp = [dtype,data]
            kyzData.append(temp)
            
        logger.info(f'Data will be set: {kyzData}')
        result = dlmsClient.set_cosem_data(1, kyz, 2, 2, kyzData)
        logger.info(f'Set result: {result}')

def startCalibration(dlmsClient:DlmsCosemClient, testBench:GenyTestBench):
    myConfiguration = configFile['step 6']
    if not myConfiguration['isEnable']:
        return
    
    parameters = myConfiguration['parameters']
    numOfCycle = parameters['NumOfCycles']
    rtcMode = parameters['RtcMode']
    turnOfOnFailed = parameters['TurnOffMeterOnFailed']
    
    meterSetupRegister = MeterSetup()
    calibrationRegister = CalibrationRegister()
    calModeRegister = CalMode()
    
    cosem_meterSetup = config.CosemList.MeterSetup
    cosem_calibrationReg = config.CosemList.CalibarationData
    cosem_calMode = config.CosemList.CalMode
    
    # TODO: fetch calibration mode data, set some configuration, wait for secs, read new value from meter
    logger.info(f'Get CalibartionMode')
    raw_calMode = dlmsClient.get_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2)
    calModeRegister.extract(raw_calMode)
    logger.info(f'Configure CalibrationMode')
    CYCLE_CAL = 90
    PF = 0.5
    calModeRegister.Quantity.set(1)
    calModeRegister.Cycles.set(CYCLE_CAL)
    calModeRegister.CalStatus.set(1)
    result = dlmsClient.set_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2, CosemDataType.e_OCTET_STRING, calModeRegister.dataFrame())
    logger.info(f'CalMode write result: {"PASSED" if result == 0 else "FAILED"}')
    if result != 0:
        logger.critical(f'Could not write CalibrationMode. Script terminated')
        exit(0)
        
    logger.info(f'Delay 3 second for meter process calmode')
    sleep(3)
    logger.info(f'Read calmode after set')
    result = dlmsClient.get_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2)
    logger.info(f'CalMode data raw: {result}')
    calModeRegister.extract(result)
    
    registers = vars(calModeRegister)
    # check instant register if zero then REJECT
    instanRegisterWillCheck = ('VrmsA', 'IrmsA', 'VrmsB', 'IrmsB', 'VrmsC', 'IrmsC')
    isValid = True
    for reg in registers:
        registerData = registers[reg]
        if reg in instanRegisterWillCheck:
            if registerData.value == 0:
                logger.critical(f'{reg}: {registerData.value}{" -- REJECT" if registerData.value == 0 else ""}')
                isValid = False
            else:
                logger.info(f'{reg}: {registerData.value}')
        else:
            logger.info(f'{reg}: {registerData.value}')
    
    if isValid == False:
        logger.info(f'Stop calibration')
        if turnOfOnFailed:
            logger.info('Turn off meter')
            testBench.close()
        return False
    
    # TODO: Get Calibration Data and Meter Setup
    logger.info('Get calibration data')
    cosem_calibData = config.CosemList.CalibarationData
    raw_calibData = dlmsClient.get_cosem_data(cosem_calibData.classId, cosem_calibData.obis, 2)
    logger.info(f'Calib data: {raw_calibData}')
    calibrationRegister.extract(raw_calibData)
    
    logger.info('Get meter setup')
    cosem_calibData = config.CosemList.MeterSetup
    raw_meterSetup = dlmsClient.get_cosem_data(cosem_calibData.classId, cosem_calibData.obis, 2)
    logger.info(f'Meter setup: {raw_meterSetup}')
    meterSetupRegister.extract(raw_meterSetup)
    
    # TODO: Calculate Instant RMS values
    # NOTE: Both Vrms and Irms has scalar -3
    readbackData = testBench.readBackSamplingData()
    logger.info(f'Calculate instant rms value')
    # Voltages
    VrmsA = calModeRegister.VrmsA.value
    VrmsB = calModeRegister.VrmsB.value
    VrmsC = calModeRegister.VrmsB.value
    StdVrmsA = readbackData['Voltage_A']
    StdVrmsB = readbackData['Voltage_B']
    StdVrmsC = readbackData['Voltage_C']
    gainVrmsA = calibrationRegister.VrmsGainPhA
    gainVrmsB = calibrationRegister.VrmsGainPhB
    gainVrmsC = calibrationRegister.VrmsGainPhC
    
    # Current
    IrmsA = calModeRegister.IrmsA.value
    IrmsB = calModeRegister.IrmsB.value
    IrmsC = calModeRegister.IrmsC.value
    StdIrmsA = readbackData['Current_A']
    StdIrmsB = readbackData['Current_B']
    StdIrmsC = readbackData['Current_C']
    gainIrmsA = calibrationRegister.IrmsGainPhA
    gainIrmsB = calibrationRegister.IrmsGainPhB
    gainIrmsC = calibrationRegister.IrmsGainPhC
        
    # Power
    cosem_activePwrA = config.CosemList.InstantActivePowerPhase1
    cosem_activePwrB = config.CosemList.InstantActivePowerPhase2
    cosem_activePwrC = config.CosemList.InstantActivePowerPhase3
    
    PwrActiveA = dlmsClient.get_cosem_data(cosem_activePwrA.classId, cosem_activePwrA.obis, 2)
    logger.info(f'Power activeA: {PwrActiveA}')
    PwrActiveB = dlmsClient.get_cosem_data(cosem_activePwrB.classId, cosem_activePwrB.obis, 2)
    logger.info(f'Power activeB: {PwrActiveB}')
    PwrActiveC = dlmsClient.get_cosem_data(cosem_activePwrC.classId, cosem_activePwrC.obis, 2)
    logger.info(f'Power activeC: {PwrActiveC}')
    if True in [pwr <= 0 for pwr in (PwrActiveA, PwrActiveB, PwrActiveC)]:
        logger.critical('Power active shall not <= 0')
        exit(1)
    StdPA = Register("Standard A", "int16", (StdIrmsA.value*StdVrmsA.value)*math.cos(math.radians(60))) #readbackData['PowerActive_A']
    StdPB = Register("Standard B", "int16", (StdIrmsB.value*StdVrmsB.value)*math.cos(math.radians(60))) #readbackData['PowerActive_B']
    StdPC = Register("Standard C", "int16", (StdIrmsC.value*StdVrmsC.value)*math.cos(math.radians(60))) #readbackData['PowerActive_C']
    gainP_A = calibrationRegister.ActiveGainPhA
    gainP_B = calibrationRegister.ActiveGainPhB
    gainP_C = calibrationRegister.ActiveGainPhC
    
    # Phase delay calibration
    cosem_instFreq = config.CosemList.InstantFrequency
    Fin = round(dlmsClient.get_cosem_data(cosem_instFreq.classId, cosem_instFreq.obis, 2)/1000)
    logger.info(f'Get frequency: {Fin}')
    
    # Update instant gain
    # InstantMeasurement = (VrmsA, VrmsB, VrmsC, IrmsA, IrmsB, IrmsC, PwrActiveA, PwrActiveB, PwrActiveC)
    # GainRegister = (gainVrmsA, gainVrmsB, gainVrmsC, gainIrmsA, gainIrmsB, gainIrmsC, gainP_A, gainP_B, gainP_C)
    # Standard = (StdVrmsA, StdVrmsB, StdVrmsC, StdIrmsA, StdIrmsB, StdIrmsC, StdPA, StdPB, StdPC)
    logger.info("Calibrating RMS Value")
    InstantMeasurement = (VrmsA, VrmsB, VrmsC, IrmsA, IrmsB, IrmsC)
    GainRegister = (gainVrmsA, gainVrmsB, gainVrmsC, gainIrmsA, gainIrmsB, gainIrmsC)
    Standard = (StdVrmsA, StdVrmsB, StdVrmsC, StdIrmsA, StdIrmsB, StdIrmsC)
    for inst, gainReg, std in zip(InstantMeasurement, GainRegister, Standard):
        newGain = round((gainReg.value*(std.value*1000)) / inst)
        logger.info(f'Calculate {gainReg.name}. Instant value: {inst} GainReg: {gainReg.value} std: {std.value*1000} newGain: {newGain}')
        gainReg.set(newGain)
        
    Calimp = [calModeRegister.CalimpA.value, calModeRegister.CalimpB.value, calModeRegister.CalimpC.value]
    Calrem = [calModeRegister.CalremA.value, calModeRegister.CalremB.value, calModeRegister.CalremC.value]
    ThreshPulses = calModeRegister.Threshpulses.value
    insVrms =[calModeRegister.VrmsA.value, calModeRegister.VrmsB.value, calModeRegister.VrmsC.value]
    insIrms =[calModeRegister.IrmsA.value, calModeRegister.IrmsB.value, calModeRegister.IrmsC.value]
    
    phaseDelayOld = [calibrationRegister.PhaseDelayA.value, calibrationRegister.PhaseDelayB.value, calibrationRegister.PhaseDelayC.value]
    logger.info(f'Calimp: {Calimp}')
    logger.info(f'Calrem: {Calrem}')
    logger.info(f'TrheshPulses: {ThreshPulses}')
    logger.info(f'Phase delay old: {phaseDelayOld}')
    phaseDelayNew = [0,0,0]
    FLV = [1,1,1] #always 1
    PFV = [0,0,0]
    Wh_m = [0,0,0]
    Wh_std = [0,0,0]
    for i in range(3):
        Wh_m[i] = (Calimp[i] + (Calrem[i]/ThreshPulses))/10
        Wh_std[i] = insVrms[i] * insIrms[i] / 3600 * CYCLE_CAL/Fin * PF
        Wh_std[i] /= 1000000
        if Wh_std[i] != 0 :
            PFV[i] = Wh_m[i] / Wh_std[i]
        phaseDelayNew[i] = int(((FLV[i]*100 - PFV[i]*100) / 0.03 ) + phaseDelayOld[i])
        #check rollover
        if phaseDelayNew[i] > 256 :
            phaseDelayNew[i] -= 256
        if phaseDelayNew[i] < 0 :
            phaseDelayNew[i] = 256 + phaseDelayNew[i]
        
    logger.info(f"Wh_std {Wh_std}")
    logger.info(f'Wh_m {Wh_m}')
    logger.info(f"PFV {PFV}")
    logger.info(f"phaseDelayOld {phaseDelayOld}")
    logger.info(f"phaseDelayNew {phaseDelayNew}")
    calibrationRegister.PhaseDelayA.set(phaseDelayNew[0])
    calibrationRegister.PhaseDelayB.set(phaseDelayNew[1])
    calibrationRegister.PhaseDelayC.set(phaseDelayNew[2])

    result = writeCalibrationData(dlmsClient, calibrationRegister)
    if result == False:
        logger.critical('Calibration FAILED')
        exit(1)

    logger.info("Sleep 3 seconds to make effect in power active")
    sleep(3)
    PwrActiveA = dlmsClient.get_cosem_data(cosem_activePwrA.classId, cosem_activePwrA.obis, 2)
    logger.info(f'Power activeA: {PwrActiveA}')
    PwrActiveB = dlmsClient.get_cosem_data(cosem_activePwrB.classId, cosem_activePwrB.obis, 2)
    logger.info(f'Power activeB: {PwrActiveB}')
    PwrActiveC = dlmsClient.get_cosem_data(cosem_activePwrC.classId, cosem_activePwrC.obis, 2)
    logger.info(f'Power activeC: {PwrActiveC}')
    logger.info("Calibrate power active")
    InstantMeasurement = (PwrActiveA, PwrActiveB, PwrActiveC)
    GainRegister = (gainP_A, gainP_B, gainP_C)
    Standard = (StdPA, StdPB, StdPC)
    for inst, gainReg, std in zip(InstantMeasurement, GainRegister, Standard):
        newGain = round((gainReg.value*(std.value*1000)) / inst)
        logger.info(f'Calculate {gainReg.name}. Instant value: {inst} GainReg: {gainReg.value} std: {std.value*1000} newGain: {newGain}')
        gainReg.set(newGain)
    result = writeCalibrationData(dlmsClient, calibrationRegister)
    if result == False:
        logger.critical('Calibration FAILED')
        exit(1)
    

def calibrate(comPort):
    t = datetime.now()
    dlmsClient = DlmsCosemClient(
        port=comPort,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=16,
        client_nb=16,
        address_size = AddrSize.ONE_BYTE
    )

    # Login
    cosemList = config.CosemList()
    loginResult = False
    try:
        logger.info('Login to meter')
        loginResult = dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
        logger.info(f'result login dlms - {loginResult}')
    except Exception as e:
        logger.critical(f'Failed to login, error message: {str(e)}')
        return False

def main():
    logger.info('='*30)
    logger.info('STARTING CALIBRATION')
    logger.info('='*30)
        
    dlmsClient = initDlmsClient()
    genyClient = initGenyClient()
    
    # HANDLING STEP
    turnOnGeny(genyClient)
    powerUpDelay()
    
    # Login DLMS
    logger.info(f'Login to meter')
    try:
        dlmsClient.client_logout()
    except:
        pass
        
    loginResult =  dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
    logger.info(f'Login result {loginResult}')
    if loginResult == False:
        logger.critical(f'Could not login to meter')
        exit(1)
    
    checkCalibrationData(dlmsClient)
    backupTemperatureData(dlmsClient)
    miscelaneousConfiguration(dlmsClient)
    startCalibration(dlmsClient, genyClient)
    
    dlmsClient.client_logout()
    
    
    # calibrate(PORT_METER)

if __name__ == "__main__":
    main()