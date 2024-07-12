import pathlib
import site
import os
import click
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import json
import serial
import pyvisa as visa
from time import sleep
from lib.Utils.Logger import getLogger

from lib.Utils.CalibrationData import CalibrationRegister
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalMode import CalMode

from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

try:
    from . import config
except:
    import config

if not os.path.exists(f'{CURRENT_PATH}/logs'):
    os.mkdir(f'{CURRENT_PATH}/logs')

logger = None
with open(f'{CURRENT_PATH}/configurations/CalibrationStep.json', 'r') as f:
    configFile = json.load(f)

def initFreqCounter():
    '''
        vendor list:
        "KEYSIGHT"
        "PENDULUM"
    '''
    instrumentPath = configFile['Environment']['Connectivity']['FrequencyCounter']['InstrumentPath']
    vendorList = configFile['Environment']['Connectivity']['FrequencyCounter']['VendorList']
    isPendulum = vendorList['PENDULUM']
    isKeysight = vendorList['KEYSIGHT']
    
    rm = visa.ResourceManager()
    if isPendulum:
        instrument = rm.open_resource(instrumentPath)
        instrument.write("CONF:FREQ 4, (@1)")
        instrument.write("INP:COUP DC")
        instrument.write("INP:LEV 0.1")
    elif isKeysight:
        instrument = rm.open_resource(instrumentPath)
        instrument.write("CONF:FREQ 4, (@1)")
        instrument.write("INP:IMP 1000000")
        instrument.write("INP:RANG 5")
        instrument.write("INP:COUP DC")
        instrument.write("INP:LEV 0.1")
        instrument.write("INP:NREJ ON")
    return instrument
    

def initDlmsClient(port) -> DlmsCosemClient:
    logger.info('Initialize DLMS client')
    myConfiguration = configFile['Environment']['Connectivity']['DlmsClient']
    serialPort = port
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
        exit('Dlms client initialization failed')
        
def readInstrument(instrument)->float:
    for i in range(3):
        try:
            instrument.write("*CLS")
            instrument.write("READ?")
            response = instrument.read()
            freq = float(response[:-1])
            if 3 < freq < 5:
                return freq
        except:
            pass
    exit(f'Instrument read error')


def main(meterid, port):
    global logger
    
    logger = getLogger(f'{CURRENT_PATH}/logs/rtc calibration {meterid}.log')
    logger.info('='*30)
    logger.info(f'Start RTC calibration for {meterid}')
    logger.info('='*30)
    
    dlmsClient = initDlmsClient(port)
    dlmsClient.client_logout()
    instrument = initFreqCounter()
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
    
    logger.info(f'Set meter rtc calibartion to 0 for initialization')
    if meterSetupRegister.RTCCalibration.value != 0:
        meterSetupRegister.RTCCalibration.set(0)
        meterSetupRegister.updateCRC(calibrationRegister)
        result = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, 9, meterSetupRegister.dataFrame())
        logger.info(f'Set result: {result}')
        sleep(2)
    else:
        logger.info('Set result: SKIP, RtcCalibration already 0')
        
    
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
    calModeRegister.Cycles.set(400)
    
    result = dlmsClient.set_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2, 9, calModeRegister.dataFrame())
    try:
        assert result == 0
    except:
        logger.critical('Failed Write CalMode to apply 4Hz signal')
        exit(1)
    logger.info('Write calibration mode SUCCESS')
    logger.info('Reading frequency from instrument')
    
    # TODO 2: Reading instrument
    frequency = readInstrument(instrument)
    
    # Calculate RTC value
    logger.info(f'Instrument measurement: {frequency}Hz')
    RtcCalibrationValue = ( ( (frequency-4)/4) * 10**6 ) / 0.954
    RtcCalibrationValue = int(RtcCalibrationValue)
    logger.info(f'Set RtcCalibration value from {meterSetupRegister.RTCCalibration.value} to {RtcCalibrationValue}')
    meterSetupRegister.RTCCalibration.set(RtcCalibrationValue)
    logger.info(f'Update CRC')
    meterSetupRegister.updateCRC(calibrationRegister)
    logger.info(f'Write meter setup')
    result = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, 9, meterSetupRegister.dataFrame())
    try:
        assert result == 0
        logger.info(f'Write SUCCESS')
    except:
        logger.critical('Failed to write Meter Setup')
        exit(1)
    
    dlmsClient.client_logout()


@click.command()
@click.option('--meterid', 'Enter meter id')
@click.option('--meterport', 'Enter meter meter port')
def run(meterid, meterport):
    main(meterid, meterport)

if __name__ == '__main__':
    run()