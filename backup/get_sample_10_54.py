import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import os
import serial
import click
import pickle
from lib.Utils.Logger import getLogger
from src import config

from Utils.CalibrationData_10_54 import CalibrationRegister as CalibrationData_10_54

from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

if not os.path.exists(f'{CURRENT_PATH}/appdata'):
    os.mkdir(f'{CURRENT_PATH}/appdata')
if not os.path.exists(f'{CURRENT_PATH}/backup'):
    os.mkdir(f'{CURRENT_PATH}/backup')

@click.command()
@click.option('--port', prompt='Enter serial port')
@click.option('--meterid', prompt='Enter meterid')
def main(port, meterid):
    logger = getLogger(f'{CURRENT_PATH}/appdata/test_getCalibrationData.log')
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

    cosem = config.CosemList.CalibarationData
    calibrationData = CalibrationData_10_54()
    calibrationDataRaw = dlmsClient.get_cosem_data(cosem.classId, cosem.obis, 2)
    logger.info(f'Byte size: {len(calibrationDataRaw)} calibrationData: {calibrationData.byteSize()}')
    logger.info(f'Data: {calibrationDataRaw}')
    calibrationData.extract(calibrationDataRaw[:])
    logger.info(f'Excess bytes: {len(calibrationDataRaw)}')
    calibrationData.info(verbose=True)

    with open(f'{CURRENT_PATH}/backup/{meterid}_10_54.pkl', 'wb') as f:
        pickle.dump(calibrationData, f)

    dlmsClient.client_logout()

if __name__ == '__main__':
    main()