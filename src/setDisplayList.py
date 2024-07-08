import serial
import pathlib
import time
import json
import site
import click
import os

CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

from datetime import datetime, timedelta
from lib.Utils.Logger import getLogger
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

try:
    from .config import CosemList
except:
    from config import CosemList

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

def main(meterid, port):
    logger = getLogger(f'{CURRENT_PATH}/logs/displayconfig {meterid}.log')

    ser_client = DlmsCosemClient(
        port=port,
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

    with open(f'{CURRENT_PATH}/configurations/DisplayList.json') as f:
        displayConfig = json.load(f)
        display_items = displayConfig['DisplayItems']

    ser_client.client_logout()
    login_result = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
    logger.info(f'login result: {login_result}')

    Cosem_DisplayProfile = CosemList.DisplayConfigProfile
    Cosem_DisplayObis = CosemList.DisplayObisConfig

    const_emptyDisplay = [0, 0, 0, 0, 0, 0, 0, 0, 253, 0, 0, 0]

    obisListDisplay = []
    captureObjectValue = []
    for item in display_items:
        # new capture object
        new_captureObject = [2, [
                [CosemDataType.e_LONG_UNSIGNED, display_items[item][0]],
                [CosemDataType.e_OCTET_STRING, [int(i) for i in display_items[item][1].split(';')]],
                [CosemDataType.e_INTEGER, display_items[item][2]],
                [CosemDataType.e_LONG_UNSIGNED, display_items[item][3]]
            ]
        ]
        captureObjectValue.append(new_captureObject)

        # new obis display item
        new_obisDisplay = [0] + [int(i) for i in display_items[item][1].split(';')] + [2] + [253, 0, 0, 0]
        obisListDisplay.append(new_obisDisplay)

    # DISPLAY CAPTURE OBJECT
    logger.info('Set display capture object')
    logger.info(f'Display items: {[display_items]}')

    logger.info('Capture object before')
    captureObject = ser_client.get_cosem_data(Cosem_DisplayProfile.classId, Cosem_DisplayProfile.obis, 3)
    logger.info(captureObject)
    result = ser_client.set_cosem_data(Cosem_DisplayProfile.classId, Cosem_DisplayProfile.obis, 3, CosemDataType.e_ARRAY, captureObjectValue)
    logger.info(f'Set result: {"SUCCESS" if result==0 else "FAILED "+str(result)}')
    time.sleep(5)
    logger.info('Capture object after')
    captureObject = ser_client.get_cosem_data(Cosem_DisplayProfile.classId, Cosem_DisplayProfile.obis, 3)
    logger.info(captureObject)

    # OBIS DISPLAY LIST
    logger.info('Set obis config')
    logger.info(f'Obis items: {obisListDisplay}')
    obisDisplaySetValue = []
    for obis in obisListDisplay:
        obisDisplaySetValue.extend(obis)
    obisDisplaySetValue.extend(const_emptyDisplay*(32-len(obisListDisplay)))
    logger.info('Object data before')
    obisDisplay = ser_client.get_cosem_data(Cosem_DisplayObis.classId, Cosem_DisplayObis.obis, 2)
    logger.info(obisDisplay)
    logger.info(f'Set value: {obisDisplaySetValue}')
    result = ser_client.set_cosem_data(Cosem_DisplayObis.classId, Cosem_DisplayObis.obis, 2, CosemDataType.e_OCTET_STRING, obisDisplaySetValue)
    logger.info(f'Set result: {"SUCCESS" if result==0 else "FAILED "+str(result)}')
    logger.info('Object data after')
    obisDisplay = ser_client.get_cosem_data(Cosem_DisplayObis.classId, Cosem_DisplayObis.obis, 2)
    logger.info(obisDisplay)

    ser_client.client_logout()

@click.command()
@click.option('--meterid', prompt='Enter meterid')
@click.option('--port', prompt='Enter serial port')
def run(meterid, port):
    main(meterid, port)

if __name__ == '__main__':
    run()