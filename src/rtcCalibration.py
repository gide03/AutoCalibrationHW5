import pathlib
import site
import os
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import json
import serial
import config
import click
from time import sleep
from datetime import datetime, timedelta
from lib.Utils.Logger import getLogger
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

logger = getLogger('rtc calibration.log')
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
        

def readInstrument()->float:
    # NOTE: HARDCODED
    # TODO: Read instrument
    return 4.0001
    
@click.command()
@click.option('--meterid', prompt="Enter meter id")
def main(meterid):
    logger.info('='*30)
    logger.info(f'Start RTC calibration for {meterid}')
    logger.info('='*30)
    
    dlmsClient = initDlmsClient()
    loginResult = dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
    if loginResult == False:
        logger.critical('Could not connect to meter')
        exit(1)
    
    # Reading calibration data and meter setup
    logger.info(f'Read calibration data')
    calibrationRegister = CalibrationRegister()
    cosem_calibrationData = config.CosemList.CalibarationData
    raw_calibrationData = dlmsClient.get_cosem_data(cosem_calibrationData.classId, cosem_calibrationData.obis, 2)
    try:
        assert isinstance(raw_calibrationData, list)
    except:
        logger.critical(f'Error when reading calibration data')
        exit(1)
    logger.info(f'Calibration data raw: {raw_calibrationData}')
    calibrationRegister.extract(raw_calibrationData)
    
    logger.info(f'Read meter setup')
    meterSetupRegister = MeterSetup()
    cosem_meterSetup = config.CosemList.MeterSetup
    raw_meterSetup = dlmsClient.get_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2)
    try:
        assert isinstance(raw_meterSetup, list)
    except:
        logger.critical(f'Error when reading raw_meterSetup')
        exit(1)
    logger.info(f'Meter setup data raw: {raw_meterSetup}')
    meterSetupRegister.extract(raw_meterSetup)        
    
    # Apply 4Hz signal
    logger.info('Reading CalibrationMode data')
    calModeRegister = CalMode()
    cosem_calMode = config.CosemList.CalMode
    raw_calMode = dlmsClient.get_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2)
    try:
        assert isinstance(raw_meterSetup, list)
    except:
        logger.critical(f'Error when reading raw_calMode')
        exit(1)
    logger.info(f'Calibration Mode raw: {raw_calMode}')
    calModeRegister.extract(raw_calMode)
    
    logger.info(f'Apply 4Hz signal')
    #TODO 1: Set cal mode to apply 4Hz signal
    
    result = dlmsClient.set_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2, CosemDataType.e_STRUCTURE, calModeRegister.dataFrame())
    try:
        assert result == 0
    except:
        logger.critical('Failed Write CalMode to apply 4Hz signal')
        exit(1)
    logger.info('Write calibration mode SUCCESS')
    logger.info('Reading frequency from instrument')
    
    # TODO 2: Reading instrument
    frequency = readInstrument()
    
    # Calculate RTC value
    logger.info(f'Instrument measurement: {frequency}Hz')
    RtcCalibrationValue = ( ( (frequency-4)/4) * 10**6 ) / 0.954
    logger.info(f'Set RtcCalibration value from {meterSetupRegister.RTCCalibration.value} to {RtcCalibrationValue}')
    meterSetupRegister.RTCCalibration.set(RtcCalibrationValue)
    logger.info(f'Update CRC')
    meterSetupRegister.updateCRC(calibrationRegister)
    logger.info(f'Write meter setup')
    result = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, CosemDataType.e_OCTET_STRING, meterSetupRegister.dataFrame())
    try:
        assert result == 0
    except:
        logger.critical('Failed to write Meter Setup')
        exit(1)
    
    dlmsClient.client_logout()

if __name__ == '__main__':
    main()