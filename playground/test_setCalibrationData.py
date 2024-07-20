import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import os
import serial
from lib.Utils.Logger import getLogger
from src import config
from lib.Utils.Register import Register

from lib.Utils.CalibrationData import CalibrationRegister

from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

import argparse
parser = argparse.ArgumentParser(description='A simple script to demonstrate Get Meter Setup')
parser.add_argument('--port', help='USB PORT', required=True)
args = parser.parse_args()
USB_PORT = args.port

if not os.path.exists(f'{CURRENT_PATH}/appdata'):
    os.mkdir(f'{CURRENT_PATH}/appdata')

def writeCalibrationData(dlmsClient:DlmsCosemClient, calibrationRegister:CalibrationRegister):
    cosem_calibrationData = config.CosemList.CalibarationData
    df = calibrationRegister.dataFrame()

    print(f'Writing data. Data: {df}')
    result = dlmsClient.set_cosem_data(cosem_calibrationData.classId, cosem_calibrationData.obis, 2, CosemDataType.e_OCTET_STRING, df)
    if result == 0:
        print(f'Write data SUCCESS')
        return True
    print(f'Write data FAILED. Error code ({result})')
    return False

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
    calibrationData.extract(calibrationDataRaw[:])
    calibrationData.info(verbose=True)

    # calibrationData.TransferFunction_control.set(0x0)
    # calibrationData.PhaseDelayA.set(18)
    # calibrationData.PhaseDelayB.set(16)
    # calibrationData.PhaseDelayC.set(8)
    # calibrationData.IrmsGainPhA.set(33528)
    # calibrationData.IrmsGainPhB.set(33403)
    # calibrationData.IrmsGainPhC.set(33675)
    # calibrationData.VrmsGainPhA.set(29749)
    # calibrationData.VrmsGainPhB.set(30056)
    calibrationData.VrmsGainPhC.set(29898)
    # df = calibrationData.dataFrame()
    # print(df)
    # calibrationData.extract(df[:])
    # calibrationData.info(verbose=True)

    result = writeCalibrationData(dlmsClient, calibrationData)
    if result == False:
        logger.critical('Calibration FAILED')
        exit(1)

    # cosem_calibrationData = config.CosemList.CalibarationData
    # result = dlmsClient.set_cosem_data(cosem_calibrationData.classId, cosem_calibrationData.obis, 2, CosemDataType.e_OCTET_STRING, df)
    # if result == 0:
    #     print(f'Write data SUCCESS')
    #     return True
    # print(f'Write data FAILED. Error code ({result})')

    calibrationDataRaw = dlmsClient.get_cosem_data(cosem.classId, cosem.obis, 2)
    calibrationData.extract(calibrationDataRaw[:])
    calibrationData.info(verbose=True)

    dlmsClient.client_logout()

if __name__ == '__main__':
    main()