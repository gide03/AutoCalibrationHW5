'''
    NOTE: I use wireless switch using nodemcu that listen command throug TCP/IP. The switch configuration could follow different design.
    - Send b'1' to switch ON the meter and send b'0' to switch OFF meter.
    - Each command will send ACK b'ok'. After ACK received, spam SNRM until success.
    - Read a register to make sure connection is really established.
'''

import socket
import time
import serial
import logging
import config
from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('./logs/communicationReady.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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

ser_client = DlmsCosemClient(
    port='COM4',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.05,
    inactivity_timeout=0.5,
    login_retry=1,
    meter_addr=commSetting.METER_ADDR,
    client_nb=commSetting.CLIENT_NUMBER,
)

host = '192.168.137.137'
port = 5005

TEST_EPOCH = 100
m_cosem = config.CosemList.InstantVoltagePhase1
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    logger.info('connecting to switch')
    s.connect((host, port))
    s.send(b'0')
    data = s.recv(128)
    logger.info(data)
    time.sleep(2)
    readyTime = []
    for bt in range(0, TEST_EPOCH):
        logger.info('='*30)
        logger.info(f'ATTEMP #{bt+1} of {TEST_EPOCH}')
        message = b'1'
        s.send(message)     # Turn ON switch
        
        data = s.recv(128)
        logger.info(f'receive {data}')
        t = datetime.now()
        timeReady = None
        logger.info(f'Start burst data at: {t}')
        while True:
            try:
                logger.info('Try to login')
                if ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL):
                    logger.info('LOGIN SUCCESS')
                    instantVoltage = ser_client.get_cosem_data(m_cosem.classId, m_cosem.obis, 2)
                    if isinstance(instantVoltage,str):
                        logger.warning(f'Cannot read instant voltage. Read result: {instantVoltage}')
                        ser_client.client_logout()
                        continue
                    logger.info(f'Instant current: {instantVoltage}')
                    timeReady = datetime.now() - t
                    readyTime.append(timeReady)
                    logger.info(f'Meter ready after {timeReady}')
                    break
                else:
                    logger.info('LOGIN FAILED')
            except TimeoutError:
                logger.warning('TIME OUT')
            except TypeError:
                logger.warning('Parsing error')
        
        logger.info('Turn off switch')
        message = b'0'
        s.send(message)
        data = s.recv(128)
        logger.info(f'receive {data}')
        
        logger.info('Wait 5sec (Hard coded)')
        time.sleep(5)
    
    readyTime = [i.total_seconds() for i in readyTime]
    import json
    with open('./logs/timeready.json', 'w') as f:
        json.dump(readyTime, f)
    average = sum(readyTime)/len(readyTime)
    logger.info(f'Max: {max(readyTime)}s Min: {min(readyTime)}s Average: {average}s')
    
    