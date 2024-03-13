from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from config import CosemObject

import logging
logger = logging.getLogger(__name__)

def fetch(dlmsClient:DlmsCosemClient, cosemObject:CosemObject, att:int):
    logger.debug(f'Fetching {cosemObject.objectName}')
    result = dlmsClient.get_cosem_data(cosemObject.classId, cosemObject.obis, att)
    logger.debug(f'Result: {result}')
    if isinstance(result, str):
        logger.critical(f'FAILED TO FETCH {cosemObject.objectName} att.{att}')
        dlmsClient.client_logout()
        exit(1)
    return result

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