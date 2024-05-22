import os
import serial
import pathlib
import sys
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
    logger = getLogger(f'{CURRENT_PATH}/logs/{meterid} hvt.log')
    TestList = (
        TestId(b'?0\r', 'Show Menu', False),
        TestId(b'?1\r', 'START BIST', False),
        TestId(b'?2\r', 'NIC UART', True),
        TestId(b'?3\r', 'DI UART', True),
        TestId(b'?4\r', 'P1 UART', True),
        TestId(b'?5\r', 'ADC SPI', True),
        TestId(b'?6\r', 'Ext Flash SPI', False), # (Fail) maybe need to manually test
        TestId(b'?7\r', 'DI SPI', True),
        TestId(b'?8\r', 'LCD I2C', True),
        TestId(b'?9\r', 'ACC I2C', False),
        TestId(b'?10\r', 'MAG I2C', True),
        TestId(b'?11\r', 'LCD CONTRAST', True),
        TestId(b'?12\r', 'LCD BACKLIGHT', True),
        TestId(b'?13\r', 'EXT PULSE', True),
        TestId(b'?14\r', 'M1- UB/Test LED1', True, waitStateMsg="After this, push TOP button to turn on TOP LED.", needVerify=True),
        TestId(b'?15\r', 'M2- UB/Test LED2', True, waitStateMsg="After this, push BOT button to turn on BOT LED.", needVerify=True),
        TestId(b'?16(1,1,2)\r', 'RDS Ctrl', True, waitStateMsg="Hear relay?", needVerify=True),
        TestId(b'?17(1,1,5)\r', 'AUX Ctrl', False, waitStateMsg="Hear relay?", needVerify=True),
        TestId(b'?18(0)\r', 'TAMPER I/P TEST-1 Closed ', True, waitStateMsg='Push and hold MCOD button!'),
        TestId(b'?18(0)\r', 'TAMPER I/P TEST-1 Opened', True, expectedResult= False, waitStateMsg='Release MCOD button!'),
        TestId(b'?18(1)\r', 'TAMPER I/P TEST-2 Closed', True, expectedResult=False, waitStateMsg='Push and hold TCOD button!'),
        TestId(b'?18(1)\r', 'TAMPER I/P TEST-2 Opened', True, waitStateMsg='Release TCOD button!'),
        TestId(b'?19\r', '32kHz OSC', True),
        TestId(b'?20\r', '16.777Mhz OSC', True),
        TestId(b'?21\r', 'TEMPERATURE', True),
        TestId(b'?22\r', 'POWER GOOD', True),
        TestId(b'?23\r', 'RDS CAP MONITOR', False),
        TestId(b'?24\r', 'BATTERY MONITOR', True),
        TestId(b'?25\r', 'HW EPF', False),
        TestId(b'?26(0)\r', 'DI I/O-1', False),
        TestId(b'?26(1)\r', 'DI I/O-2', False),
        TestId(b'?26(2)\r', 'DI I/O-3', True, expectedResult= True, waitStateMsg='Push modem busy!'),
        TestId(b'?27(0)\r', 'Ext I/O-1', True),
        TestId(b'?27(1)\r', 'Ext I/O-1', True),
        TestId(b'?28\r', 'MainB I/O', True),
        TestId(b'?29\r', 'Validate Ext ADC data', True),
        TestId(b'?30\r', 'SWITCH TO MAIN FW', True),
        
        # TODO: b?50\r to show other menu
        # TODO: b?65\r reset flash
    )
    
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
        response = transaction(hvt_ser, b'?0\r').decode('utf-8')
        logger.info(f'Response: {response}')
        if 'ERROR' in response:
            logger.critical('Serial timeout. Please check your connection configuration')
            exit(1)
    except Exception:
        logger.info('Meter might be already at hvt mode')
        logger.info('Get hvt menu')
        response = transaction(hvt_ser, b'?0\r').decode('utf-8')
        logger.info(f'Response: {response}')
        if 'ERROR' in response:
            logger.critical('Serial timeout. Please check your connection configuration')
            exit(1)
        
    try:
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

    except:
        print('')
        # exit()
    input('Meter should be enter HVT mode. Press ENTER to continue')
    
    input('Please press ENTER to execute command for each test id. (Press ENTER to continue!)')
    num_of_test = 0
    num_of_success = 0
    num_of_fail = 0
    num_of_skip = 0
    for test in TestList:
        num_of_test += 1
        if test.isRunTest:
            logger.info(f'Testing {test.desc}')
            if len(test.waitStateMsg) > 0:
                sys.stdin.flush()
                input(f'{test.waitStateMsg}. Press ENTER if ready')
            else:
                # input('Press Enter to continue')
                pass
            
            retryAttemp = 2
            
            for i in range(retryAttemp):
                result = transaction(ser_client.ser, test.id, 5)
                logger.debug(f'Transaction Tx: {test.id.hex()} Rx: {result.hex()}')
                try:
                    result = result.decode('utf-8').replace('\n', '')
                    result = result.replace('\r', '')
                    
                    if test.needVerify: # Manual verification
                        sys.stdin.flush()
                        userVerification = input('Is it Okay? (y/n. Default y)')
                        if userVerification == 'n':
                            result = 'Fail'
                        else:
                            result = 'Pass'
                    else:
                        logger.debug(f'{test.desc} result -> {result}')
                        
                    if 'Pass' in result:
                        if test.expectedResult == True:
                            test.isPassed = True
                            logger.info(f'PASSED')
                            num_of_success += 1
                        else:
                            logger.warning(f'FAILED')
                            num_of_fail += 1
                    elif 'Fail' in result:
                        if test.expectedResult == False:
                            test.isPassed = True
                            logger.info(f'PASSED')
                            num_of_success += 1
                        else:
                            logger.warning(f'FAILED')
                            num_of_fail += 1
                    elif 'ERROR' in result:
                        raise Exception('')
                    break
                except Exception as e:
                    logger.warning(e)
                    if i < retryAttemp-1:
                        logger.debug('Retry transaction')
                    else:
                        logger.critical('Transaction FAILED. Please retry the test script')
                        exit(1)
        else:
            logger.info(f'Skip Testing {test.desc}')
            num_of_skip += 1
            test.isSkip = True

    logger.info(f'Summarize test id to csv file')
    summaryFilename = f'{CURRENT_PATH}/appdata/hvt_summary.csv'
    column = ['Meter ID']
    column.extend([testItem.desc for testItem in TestList])
    if not os.path.exists(summaryFilename):
        line = ';'.join(column)
        with open(summaryFilename, 'w') as f:
            f.write(f'{line}\n')
    with open(summaryFilename, 'a') as f:
        rowValue = [meterid]
        for testItem in TestList:
            if testItem.isSkip == False:
                rowValue.append(str(testItem.isPassed))
            else:
                rowValue.append('Skip')
        line = ';'.join(rowValue)
        f.write(f'{line}\n')
            
    logger.info(f'HVT Finished. Num of test {num_of_test}, Num of success {num_of_success}, Num of fail {num_of_fail}, Num of skip {num_of_skip}')

@click.command()
@click.option('--meterid', prompt='Enter meter id')
@click.option('--meterport', prompt='Enter meterport')
def run(meterid, meterport):
    main(meterid, meterport)
    
if __name__ == '__main__':
    run()