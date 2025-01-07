import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import os
import serial
import click
from lib.Utils.Logger import getLogger
from src import config

from lib.Utils.MeterSetup import MeterSetup

from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize


if not os.path.exists(f'{CURRENT_PATH}/appdata'):
    os.mkdir(f'{CURRENT_PATH}/appdata')

@click.command()
@click.option('--port', prompt="Enter serial port")
def main(port):
    logger = getLogger(f'{CURRENT_PATH}/appdata/test_getMeterSetup.log')
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

    # obis = "1;0;16;24;0;255"
    obis = "1;0;1;24;0;255"

    attr2 = dlmsClient.get_cosem_data(5, obis, 2)
    attr3 = dlmsClient.get_cosem_data(5, obis, 3)
    attr6 = dlmsClient.get_cosem_data(5, obis, 6)
    attr7 = dlmsClient.get_cosem_data(5, obis, 7)
    attr8 = dlmsClient.get_cosem_data(5, obis, 8)
    attr9 = dlmsClient.get_cosem_data(5, obis, 9)
    print(attr2,attr3,attr6,attr7,attr8,attr9)

    obis = "1;0;15;24;0;255"
    attr2 = dlmsClient.get_cosem_data(5, obis, 2)
    attr3 = dlmsClient.get_cosem_data(5, obis, 3)
    attr6 = dlmsClient.get_cosem_data(5, obis, 6)
    attr7 = dlmsClient.get_cosem_data(5, obis, 7)
    attr8 = dlmsClient.get_cosem_data(5, obis, 8)
    attr9 = dlmsClient.get_cosem_data(5, obis, 9)
    print(attr2,attr3,attr6,attr7,attr8,attr9)

    dlmsClient.client_logout()

if __name__ == '__main__':
    main()