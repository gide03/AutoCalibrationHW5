from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.Utils.CalibrationData import CalibrationRegister
from config import CosemList
from . import TestFetchCosem

import logging
logger = logging.getLogger(__name__)

calibrationDataCosem = CosemList.CalibarationData

def fetchRegister(dlmsClient:DlmsCosemClient, verbose=False, returnRaw=False)->CalibrationRegister:
    TestFetchCosem.logger = logger
    
    calibrationRegister = CalibrationRegister()
    dataRead = TestFetchCosem.fetch(dlmsClient, calibrationDataCosem, 2)
    calibrationRegister.extract(dataRead[:])
    
    if verbose:
        logger.info('='*30)
        logger.info('CALIBRATION REGISTER INFO')
        logger.info('='*30)
        registers = vars(calibrationRegister) # dict
        for regName in registers:
            register = registers[regName]
            logger.info(f'{regName} : {register.value}')
    
    if returnRaw:
        return dataRead
    return calibrationRegister
    
def writeRegister(dlmsClient:DlmsCosemClient, calibrationRegister:CalibrationRegister) -> bool:
    if not isinstance(calibrationRegister, CalibrationRegister):
        raise TypeError('Wrong data type of calibrationData')
    
    logger.debug(f'Send meterSetup')
    # calculate new crc
    df = calibrationRegister.dataFrame()
    result = dlmsClient.set_cosem_data(calibrationDataCosem.classId, calibrationDataCosem.obis, 2, 9, df)    
    logger.debug(f'Result: {result}')
    return True if result==0 else False

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