from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType
from lib.Utils.Register import Register
from config import CosemList
from . import TestFetchCosem

import logging
logger = logging.getLogger(__name__)

kyz1 = CosemList.KYZ1
kyz2 = CosemList.KYZ2
kyz3 = CosemList.KYZ3

kyzStructure = [
    ('PulseWeight', CosemDataType.e_LONG_UNSIGNED),
    ('PulseOnTime', CosemDataType.e_LONG_UNSIGNED),
    ('PulseOffTime', CosemDataType.e_LONG_UNSIGNED),
    ('Phase', CosemDataType.e_ENUM),
    ('Direction', CosemDataType.e_ENUM),
    ('Energy', CosemDataType.e_ENUM),
    ('CalculationType', CosemDataType.e_ENUM),
    ('Variant', CosemDataType.e_ENUM),
    ('Function', CosemDataType.e_ENUM),
    ('DIFunction', CosemDataType.e_ENUM),
    ('Status', CosemDataType.e_ENUM),
    ('Reserved', CosemDataType.e_LONG_UNSIGNED),
]

def fetchRegister(dlmsClient:DlmsCosemClient, register:Register=None, verbose=False, returnRaw=False):
    TestFetchCosem.logger = logger    
    readResult = dlmsClient.get_cosem_data(register.classId, register.obis, 2)
    if isinstance(readResult, str):
        return readResult
    if verbose:
        logger.info('='*30)
        logger.info(f'{register.objectName} INFO')
        logger.info('='*30)
        for value, (desc, dtype) in zip(readResult, kyzStructure):
            logger.info(f'{desc}: {value}')
    return readResult

def configureKYZ1(dlmsClient:DlmsCosemClient, verbose=False)->bool:
    register = kyz1
    
    logger.debug('Set KYZ1')
    readResult = fetchRegister(dlmsClient, register=register, verbose=verbose)
    if isinstance(readResult, str):
        logger.warning(f'Failed to fetch KYZ1. Read result: {readResult}')
        return False
        
    # NOTE: If the status is 1 change it to 0. Based on kyzStructure the status is at index -2.
    kyzStatus = readResult[-2]
    logger.debug(f'Status: {kyzStatus}')
    if kyzStatus == 1:
        logger.debug('Set KYZ1 status to 0') 
        dataSet = []
        readResult[-2] = 0
        for val, (_, dtype) in zip(readResult, kyzStructure):
            dataSet.append([dtype, val])
        logger.debug(f'Send configuration: {readResult}')
        print(dataSet)
        result = dlmsClient.set_cosem_data(register.classId, register.obis, 2, 2, dataSet)
        logger.debug(f'Result: {result}')
        return result
    
    else:
        logger.debug('SKIP KYZ1 config because status already 0')
        return True

def configureKYZ2(dlmsClient:DlmsCosemClient, verbose=False)->bool:
    register = kyz2
    
    logger.debug('Set KYZ2')
    readResult = fetchRegister(dlmsClient, register=register, verbose=verbose)
    if isinstance(readResult, str):
        logger.warning(f'Failed to fetch KYZ2. Read result: {readResult}')
        return False
        
    # NOTE: If the status is 1 change it to 0. Based on kyzStructure the status is at index -2.
    kyzStatus = readResult[-2]
    logger.debug(f'Status: {kyzStatus}')
    if kyzStatus == 1:
        logger.debug('Set KYZ2 status to 0') 
        dataSet = []
        readResult[-2] = 0
        for val, (_, dtype) in zip(readResult, kyzStructure):
            dataSet.append([dtype, val])
        logger.debug(f'Send configuration: {readResult}')
        print(dataSet)
        result = dlmsClient.set_cosem_data(register.classId, register.obis, 2, 2, dataSet)
        logger.debug(f'Result: {result}')
        return result
    else:
        logger.debug('SKIP KYZ2 config because status already 0')
        return True

def configureKYZ3(dlmsClient:DlmsCosemClient, verbose=False)->bool:
    register = kyz3
    
    logger.debug('Set KYZ3')
    readResult = fetchRegister(dlmsClient, register=register, verbose=verbose)
    if isinstance(readResult, str):
        logger.warning(f'Failed to fetch KYZ3. Read result: {readResult}')
        return False
        
    # NOTE: If the status is 1 change it to 0. Based on kyzStructure the status is at index -2.
    kyzStatus = readResult[-2]
    logger.debug(f'Status: {kyzStatus}')
    if kyzStatus == 1:
        logger.debug('Set KY3 status to 0') 
        dataSet = []
        readResult[-2] = 0
        for val, (_, dtype) in zip(readResult, kyzStructure):
            dataSet.append([dtype, val])
        logger.debug(f'Send configuration: {readResult}')
        print(dataSet)
        
        result = dlmsClient.set_cosem_data(register.classId, register.obis, 2, 2, dataSet)
        logger.debug(f'Result: {result}')
        return True if result==0 else False
    
    else:
        logger.debug('SKIP KYZ3 config because status already 0')
        return True
    
if __name__ == '__main__':
    from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
    from lib.DLMS_Client.hdlc.hdlc_app import AddrSize
    import serial

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
        port='com7',
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=commSetting.METER_ADDR,
        client_nb=commSetting.CLIENT_NUMBER,
        address_size = AddrSize.ONE_BYTE
    )