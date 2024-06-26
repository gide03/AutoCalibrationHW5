import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import os
import serial
from lib.Utils.Logger import getLogger
from src import config

from lib.Utils.CalibrationData import CalibrationRegister

from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

import argparse
parser = argparse.ArgumentParser(description='A simple script to demonstrate Get Meter Setup')
parser.add_argument('--port', help='USB PORT', required=True)
args = parser.parse_args()
USB_PORT = args.port

if not os.path.exists(f'{CURRENT_PATH}/appdata'):
    os.mkdir(f'{CURRENT_PATH}/appdata')

def main():
    logger = getLogger(f'{CURRENT_PATH}/appdata/test_getCalibrationData.log')
    dlmsClient = DlmsCosemClient(                               # generate dlmsClient while waiting
        port=USB_PORT,
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
    calibrationData = CalibrationRegister()
    calibrationDataRaw = dlmsClient.get_cosem_data(cosem.classId, cosem.obis, 2)
    logger.info(f'Byte size: {len(calibrationDataRaw)} calibrationData: {calibrationData.byteSize()}')
    logger.info(f'Data: {calibrationDataRaw}')
    calibrationData.extract(calibrationDataRaw[:])
    logger.info(f'Excess bytes: {len(calibrationDataRaw)}')
    calibrationData.info(verbose=True)
    logger.info(f'Raw data before: {bytes(calibrationDataRaw).hex()}')
    logger.info(f'Get dataframe: {bytes(calibrationData.dataFrame()).hex()}')
    logger.info(f'Is dataframe same as raw data? {calibrationDataRaw == calibrationData.dataFrame()}')

    dlmsClient.client_logout()

if __name__ == '__main__':
    main()