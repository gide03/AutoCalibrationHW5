import os
import serial
import pathlib
import time
import click
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()

import site
site.addsitedir(f'{CURRENT_PATH.parent}')

from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.Utils.Logger import getLogger

if not os.path.exists(f'{CURRENT_PATH}/logs'):
    os.mkdir(f'{CURRENT_PATH}/logs')

if not os.path.exists(f'{CURRENT_PATH}/appdata'):
    os.mkdir(f'{CURRENT_PATH}/appdata')

class commSetting:
    METER_ADDR = 100
    CLIENT_NUMBER = 0x73
    AUTH_KEY = "wwwwwwwwwwwwwwww"
    GUEK = "30303030303030303030303030303030"
    GAK = "30303030303030303030303030303030"
    SYS_TITLE = "4954453030303030"
    # For HW 5
    USE_RLRQ = True
    IS_RLRQ_PROTECTED = True

class TestId:
    def __init__(self, id:int, desc:str, isRunTest:bool, expectedResult:bool=True, waitStateMsg:str='', needVerify=False):
        self.id = id
        self.desc = desc
        self.isRunTest = isRunTest
        self.isPassed = False
        self.isSkip = False
        self.waitStateMsg = waitStateMsg
        self.expectedResult = expectedResult
        self.needVerify = needVerify
        
        
def transaction(serial:serial.Serial, buffer, timeout = 10):
    mSerial = serial
    mSerial.write(buffer)
    tempBuffer = b''
    timeoutTime = timedelta(seconds=timeout)
    startTime = datetime.now()
    while datetime.now() - startTime < timeoutTime:
        byte = mSerial.read()
        if byte != b'':
            tempBuffer += byte
        else:
            if tempBuffer != b'':
                return tempBuffer
    return b'ERROR::Serial timeout'

def main(meterid, meterport):
    logger = getLogger(f'{CURRENT_PATH}/logs/{meterid} eraseFlash.log')
    
    logger.info('='*30)
    logger.info(f'Erase Flash meter {meterid}, serialport {meterport}')
    logger.info('='*30)
    
    ser_client = DlmsCosemClient(
        port=meterport,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.3,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=commSetting.METER_ADDR,
        client_nb=commSetting.CLIENT_NUMBER,
    )
    
    hvt_ser = ser_client.ser
    
    try:
        ser_client.client_logout()
        loginResult = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
        if loginResult == False:
            logger.info('Could not login to meter')
    except TimeoutError:
        logger.info('Login timeout')
        logger.info('Try to get hvt menu')
        response = transaction(hvt_ser, b'?50\r').decode('utf-8')
        logger.info(f'Response: {response}')
        if 'ERROR' in response:
            logger.critical('Serial timeout. Please check your connection configuration')
            return 1
    except Exception:
        logger.info('Meter might be already at hvt mode')
        logger.info('Get hvt menu')
        response = transaction(hvt_ser, b'?50\r').decode('utf-8')
        logger.info(f'Response: {response}')
        if 'ERROR' in response:
            logger.critical('Serial timeout. Please check your connection configuration')
            return 1
        
    try:
        if loginResult :
            logger.info('Reading fw version')
            fwVersion = ser_client.get_cosem_data(1, '1;0;0;2;0;255', 2)
            logger.info(f'Firmware Version: {bytes(fwVersion).decode("utf-8")}')
            
            print('Enter to mode HVT')
            # TODO: CHANGE OBIS CODE FOR HVT
            # obis = '1;1;128;130;1;255'
            obis = '0;0;128;130;1;255'
            classId = 1
            attId = 2
            value = 1
            ser_client.set_cosem_data_unconfirmed(classId, obis, attId, CosemDataType.e_UNSIGNED, value)
            logger.info('Meter should be run in HVT mode')
            time.sleep(2)
    except:
        print('')
    
    logger.info('Show HVT menu')
    hvtMenu = transaction(hvt_ser, b'?50\r')
    hvtMenu = hvtMenu.decode('utf-8')
    logger.info(hvtMenu)
    
    logger.info('Erase Flash, you may need to wait 170 second for the process')
    result = transaction(hvt_ser, b'?65\r', 170)
    print('show menu', result)
    result = result.decode('utf-8')
    logger.info(f'Result: {result}')
    if "Pass" in result:
        logger.info('Erase flash success')
    else:
        logger.critical('Erase flash Failed')
    
    logger.info('Exit HVT')
    transaction(hvt_ser, b'?30\r')
    
@click.command()
@click.option('--meterid', prompt='Enter meter id')
@click.option('--meterport', prompt='Enter meterport')
def run(meterid, meterport):
    main(meterid, meterport)
    
if __name__ == '__main__':
    run()