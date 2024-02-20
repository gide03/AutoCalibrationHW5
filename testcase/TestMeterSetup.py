from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalibrationData import CalibrationRegister
from config import CosemList
from . import TestFetchCosem

import logging
logger = logging.getLogger(__name__)

meterSetupCosem = CosemList.MeterSetup

def calRunningCRC16(dataFrame):
    lCrc = 0xffff
    
    for dataIdx in range(0, len(dataFrame)):
        data = dataFrame[dataIdx]
        lCrc = lCrc ^ (data << 8)
        for i in range(0,8):
            if (lCrc & 0x8000):
                lCrc = (lCrc << 1) ^ 0x1021
            else:
                lCrc <<= 1
        lCrc &= 0xffff
    # return [lCrc&0xff, lCrc>>8]
    return lCrc

def fetchRegister(dlmsClient:DlmsCosemClient, verbose=False, returnRaw=False)->MeterSetup:
    TestFetchCosem.logger = logger
    
    meterSetupRegister = MeterSetup()
    dataRead = TestFetchCosem.fetch(dlmsClient, meterSetupCosem, 2)
    meterSetupRegister.extract(dataRead[:])
    
    if verbose:
        logger.info('='*30)
        logger.info('METER SETUP INFO')
        logger.info('='*30)
        registers = vars(meterSetupRegister) # dict
        for regName in registers:
            register = registers[regName]
            logger.info(f'{regName} : {register.value}')
    
    if returnRaw:
        return dataRead
    return meterSetupRegister
    
def writeRegister(dlmsClient:DlmsCosemClient, meterSetup:MeterSetup, calibrationData:CalibrationRegister):
    if not isinstance(calibrationData, CalibrationRegister):
        raise TypeError('Wrong data type of calibrationData')
    if not isinstance(meterSetup, MeterSetup):
        raise TypeError('Wrong data type of meterSetup')
    
    logger.debug(f'Send meterSetup')
    df = calibrationData.dataFrame()
    df.extend(meterSetup.dataFrame())
    
    # calculate new crc
    df = df[:-2]
    meterSetup.CRC.value = calRunningCRC16(df)
    
    df = meterSetup.dataFrame()
    result = dlmsClient.set_cosem_data(meterSetupCosem.classId, meterSetupCosem.obis, 2, 9, df)    
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