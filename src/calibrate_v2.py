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
CURRENT_PATH = pathlib.Path(__file__)
site.addsitedir(CURRENT_PATH)

import json
import serial
import config
from time import sleep
from datetime import datetime, timedelta
from src.Logger import getLogger
from lib.TestBench.GenyApi import GenyApi

from lib.Utils.CalibrationData import CalibrationRegister
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalMode import CalMode

from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

PORT_GENY = '/dev/ttyUSB0'
PORT_METER = '/dev/ttyUSB1'

logger = getLogger('dev.log')
with open(f'{CURRENT_PATH}/configurations/MeterSetup.json', 'r') as f:
    configFile = json.load(f)

def initDlmsClient() -> DlmsCosemClient:
    logger.info('Initialize DLMS client')
    myConfiguration = configFile['Environment']['DlmsClient']
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
    
def initGenyClient() -> GenyApi:
    myConfiguration = configFile['Environment']['TestBench']
    
    serialPort = myConfiguration['SerialPort']
    baudRate = myConfiguration['BaudRate']
    
    geny = GenyApi('client 1', 1234)
    try:
        geny.open(serialPort, baudRate, GenyApi.GenyVersion.YC99T_5C)
        return geny
    except Exception as e:
        logger.warning(str(e))
        logger.critical('Failed to initialize Geny test bench. Process terminated')
        exit(1)
    
def turnOnGeny(geny:GenyApi):
    logger.info('TURN ON GENY')
    
    # Get the configurations
    myConfiguration = configFile['step 1']
    if myConfiguration['isEnable'] == False:
        return
    
    parameters = myConfiguration['parameters']
    voltage = parameters['Voltage']
    current = parameters['Current']
    phase = parameters['phase']
    frequency = parameters['frequency']
    logger.info(f'Geny Parameters: V:{voltage}V I:{current}A Phase:{phase} Deg Freq:{frequency}Hz')
        
    try:
        geny.setGeny(
            isCommon=True,
            voltage=230,
            current=30,
            phase=60,
            frequency=50,
            meterConstant=1000,
            ring=3
        )
    except:
        logger.critical('Something wrong with Geny. Process terminated')
        exit(1)

def powerUpDelay():
    try:
        assert delay >= 0
    except:
        logger.critical('Invalid parameter')
        exit(1)
    
    myConfiguration = configFile['step 2']
    if myConfiguration['isEnable'] == False:
        return
    
    delay = myConfiguration['parameters']['DelayTime']
    
    logger.info(f'Waiting for delay {delay}s')
    t = datetime.now()
    while datetime.now() - t < timedelta(seconds=delay):
        print(f'Power up delay {datetime.now().second}/{delay}s', end='\r')

def checkCalibrationData(dlmsClient:DlmsCosemClient):
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
    
    isCalibrationDataDefault = raw_calibrationData == calibrationRegister.dataFrame()
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
    
    if flagSetToDefault:
        result = writeCalibrationToDefault(dlmsClient)
        if result == False:
            logger.critical('Set calibration data to default FAILED')
            exit(1)
        return result
    
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
        logger.info('Store temperature to file')
        filename = f'{CURRENT_PATH}/appdata/{parameters["filename"]}'
        with open(filename, 'w') as f:
            json.dump({'temperature':temperature}, f)

def configureLEDConfiguration(dlmsClient:DlmsCosemClient):
    myConfiguration = configFile['step 5']
    if not myConfiguration['isEnable']:
        return
    
    parameters = myConfiguration['parameters']
    flagNopulse = parameters['NoPulseParameter']
    
    cosem_Led1Config = config.CosemList.LED1Configuration
    cosem_Led2Config = config.CosemList.LED2Configuration
    
    # NOTE: Read LED config to makesure we don't change other configurations
    logger.info('Read LED 1 configuration')
    led1Config = dlmsClient.get_cosem_data(cosem_Led1Config.classId, cosem_Led1Config.obis, 2)
    logger.info('Read LED 1 configuration')
    led2Config = dlmsClient.get_cosem_data(cosem_Led2Config.classId, cosem_Led2Config.obis, 2)
    
    flag_setLed1 = True
    flag_setLed2 = True
    if led1Config[6] == 0:
        logger.info('LED 1 Configuration already at No Pulse')
        flag_setLed1 = False
    if led2Config[6] == 0:
        logger.info('LED 2 Configuration already at No Pulse')
        flag_setLed2 = False
        
    # TODO: Modify led config to No pulse (change index 6 to 0). Skip if already No Pulse
    if flag_setLed1:
        logger.info(f'Set LED1 configuration')
        led1Config[6] = 0
        valueLed_1 = [CosemDataType.e_STRUCTURE, [
            [CosemDataType.e_FLOAT32, led1Config[0]],
            [CosemDataType.e_LONG_UNSIGNED, led1Config[1]],
            [CosemDataType.e_LONG_UNSIGNED, led1Config[2]],
            [CosemDataType.e_DOUBLE_LONG_UNSIGNED, led1Config[3]],
            [CosemDataType.e_ENUM, led1Config[4]],
            [CosemDataType.e_ENUM, led1Config[5]],
            [CosemDataType.e_ENUM, led1Config[6]], 
            [CosemDataType.e_ENUM, led1Config[7]],
        ]]
        
        result = dlmsClient.set_cosem_data(cosem_Led1Config.classId, cosem_Led1Config.obis, 2, CosemDataType.e_STRUCTURE, valueLed_1[1])
        logger.info(f'Result: {"PASSED" if result == 0 else "FAILED"}')
    
    if flag_setLed2:
        logger.info(f'Set LED2 configuration')
        led2Config[6] = 0
        valueLed_2 = [CosemDataType.e_STRUCTURE, [
            [CosemDataType.e_FLOAT32, led2Config[0]],
            [CosemDataType.e_LONG_UNSIGNED, led2Config[1]],
            [CosemDataType.e_LONG_UNSIGNED, led2Config[2]],
            [CosemDataType.e_DOUBLE_LONG_UNSIGNED, led2Config[3]],
            [CosemDataType.e_ENUM, led2Config[4]],
            [CosemDataType.e_ENUM, led2Config[5]],
            [CosemDataType.e_ENUM, led2Config[6]], 
            [CosemDataType.e_ENUM, led2Config[7]],
        ]]
        
        result = dlmsClient.set_cosem_data(cosem_Led2Config.classId, cosem_Led2Config.obis, 2, CosemDataType.e_STRUCTURE, valueLed_2[1])
        logger.info(f'Result: {"PASSED" if result == 0 else "FAILED"}')    
 
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
    
    
    
    calibrate(PORT_METER)

if __name__ == "__main__":
    main()