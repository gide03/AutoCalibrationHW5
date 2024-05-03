import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import os
import serial
from lib.Utils.Logger import getLogger
from src import config

from lib.Utils.MeterSetup import MeterSetup

from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

import click

if not os.path.exists(f'{CURRENT_PATH}/appdata'):
    os.mkdir(f'{CURRENT_PATH}/appdata')

@click.command()
@click.option('--port', prompt="Enter serial port")
def main(port):
    logger = getLogger(f'{CURRENT_PATH}/appdata/test_getLEDConfiguration.log')
    dlmsClient = DlmsCosemClient(                               # generate dlmsClient while waiting
        port=port,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=16,
        client_nb=0x73,
        address_size = AddrSize.ONE_BYTE
    )

    dlmsClient.client_logout()

    logger.info(f'Login to meter')
    loginResult = dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
    logger.info(f'Login result: {loginResult}')
    assert loginResult == True

    cosem_LED1 = config.CosemList.LED1Configuration
    cosem_LED2 = config.CosemList.LED2Configuration
    
    result = dlmsClient.get_cosem_data(cosem_LED1.classId, cosem_LED1.obis, 2)
    logger.info(f'LED configuration 1: {result}')
    result = dlmsClient.get_cosem_data(cosem_LED2.classId, cosem_LED2.obis, 2)
    logger.info(f'LED configuration 2: {result}')
    
    dlmsClient.client_logout()

if __name__ == '__main__':
    main()