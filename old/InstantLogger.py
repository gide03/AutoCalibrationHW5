'''
    REQUEST team hardware
'''

import serial
import logging
import pathlib
import time
import os

from datetime import datetime, timedelta
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

COM_PORT = 'COM4'
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()

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

class CosemObject():
    def __init__(self, objectName:str, classId:int, obis:str):
        self.objectName = objectName
        self.classId = classId
        self.obis = obis


def getLogger(filename) -> logging.Logger:
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    
    # Create a formatter and set it for both handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def main():
    logger = getLogger(f'{CURRENT_PATH}/instantLog.log')
    t = datetime.now()
    outputFile = f'instant_log{t.strftime("%d%m%Y %H%M%S")}.csv'
    logger.info(f'Instant values will record at: {outputFile}')
    objectList = (
        CosemObject('Instantaneous current L1', 3, '1;0;31;7;0;255'),
        CosemObject('Instantaneous current L2', 3, '1;0;51;7;0;255'),
        CosemObject('Instantaneous current L3', 3, '1;0;71;7;0;255'),
        
        CosemObject('Instantaneous voltage L1', 3, '1;0;32;7;0;255'),
        CosemObject('Instantaneous voltage L2', 3, '1;0;52;7;0;255'),
        CosemObject('Instantaneous voltage L3', 3, '1;0;72;7;0;255'),
        
        CosemObject('Instantaneous Active Power L1', 3, '1;0;35;7;0;255'),
        CosemObject('Instantaneous Active Power L2', 3, '1;0;55;7;0;255'),
        CosemObject('Instantaneous Active Power L3', 3, '1;0;75;7;0;255'),
        
        CosemObject('Total Inst Power factor Lead Ph L1', 3, '1;128;33;7;0;255'),
        CosemObject('Total Inst Power factor Lead Ph L2', 3, '1;128;53;7;0;255'),
        CosemObject('Total Inst Power factor Lead Ph L3', 3, '1;128;73;7;0;255'),
        
        CosemObject('Total Inst Reactive Import Power Lead L1', 3, '1;128;23;7;0;255'),
        CosemObject('Total Inst Reactive Import Power Lead L2', 3, '1;128;43;7;0;255'),
        CosemObject('Total Inst Reactive Import Power Lead L3', 3, '1;128;63;7;0;255'),
        
        CosemObject('Temperature', 3, '1;0;96;9;0;255')
    )
    with open(outputFile, 'w') as f:
        column = ';'.join(['Time Stamp']+[cosem.objectName for cosem in objectList])
        f.write(column + '\n')
    
    dlms_client = DlmsCosemClient(
        port=COM_PORT,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.05,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=commSetting.METER_ADDR,
        client_nb=commSetting.CLIENT_NUMBER,
        address_size = AddrSize.ONE_BYTE
    )
    dlms_client.client_logout()
    
    # Flag forever loop
    flagFile = f'{CURRENT_PATH}/run.flag'
    if not os.path.exists(flagFile):
        with open(flagFile, 'w') as f:
            pass
    
    tRead = datetime.now()
    counter = 0
    while os.path.exists(flagFile):
        try:
            counter += 1
            logger.info(f'Attemp #{counter}')
            while datetime.now() - tRead < timedelta(seconds=5):
                time.sleep(0.01)
            tRead = datetime.now()
            
            with open(outputFile, 'a') as f:    
                logger.info('login to meter')
                loginResult = dlms_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
                logger.info(f'login result: {loginResult}')
                
                if not loginResult:
                    dlms_client.client_logout()
                    continue
                
                t = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                instantValues = [t]
                for cosem in objectList:
                    objectName = cosem.objectName
                    classId = cosem.classId
                    obis = cosem.obis
                    
                    logger.info(f'Read {objectName}')
                    value = dlms_client.get_cosem_data(classId, obis, 2)
                    logger.info(f'Value: {value}')
                    instantValues.append(value)
                
                dlms_client.client_logout()
                
                instantValues = [str(value) for value in instantValues]
                f.write(';'.join(instantValues)+'\n')
        except:
            pass
                
main()