import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import os
import serial
from src.Logger import getLogger
from src import config

from lib.Utils.MeterSetup import MeterSetup
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

def main():
    logger = getLogger(f'{CURRENT_PATH}/appdata/test_writeMeterSetup.log')
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

    cosem_meterSetup = config.CosemList.MeterSetup
    cosem_calibrationData = config.CosemList.CalibarationData
    
    meterSetup = MeterSetup()
    calibReg = CalibrationRegister()
    

    dlmsClient.client_logout()

    logger.info(f'Login to meter')
    loginResult = dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
    logger.info(f'Login result: {loginResult}')
    assert loginResult == True

    logger.info('Get calibration data')
    raw_calibData = dlmsClient.get_cosem_data(cosem_calibrationData.classId, cosem_calibrationData.obis, 2)
    logger.info('Get meter setup')
    raw_meterSetup = dlmsClient.get_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2)
    meterSetup.extract(raw_meterSetup)
    calibReg.extract(raw_calibData)
    
    logger.info(f'Calculate CRC with the same configuration')
    logger.info(f'Current CRC: {meterSetup.Crc.value}')
    meterSetup.updateCRC(calibReg)
    logger.info(f'After update CRC (should not change): {meterSetup.Crc.value}')
    
    writeResult = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, CosemDataType.e_OCTET_STRING, meterSetup.dataFrame())
    logger.info(f'Write result: {"SUCCESS" if writeResult==0 else "FAILED"}')
    
    # Change a parameter
    dummyRTC = 21
    meterSetup.RTCCalibration.value = dummyRTC
    meterSetup.updateCRC(calibReg)
    writeResult = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, CosemDataType.e_OCTET_STRING, meterSetup.dataFrame())
    logger.info(f'Write result: {"SUCCESS" if writeResult==0 else "FAILED"}')
    logger.info(f'CRC after set: {meterSetup.RTCCalibration.value} - {"PASSED" if meterSetup.RTCCalibration.value==dummyRTC else "FAILED"}')
    
    # Set RTC to default
    meterSetup.RTCCalibration.value = 0
    meterSetup.updateCRC(calibReg)
    writeResult = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, CosemDataType.e_OCTET_STRING, meterSetup.dataFrame())
    logger.info(f'Write result: {"SUCCESS" if writeResult==0 else "FAILED"}')
    logger.info(f'CRC after set: {meterSetup.RTCCalibration.value} - {"PASSED" if meterSetup.RTCCalibration.value==0 else "FAILED"}')
    
    
    dlmsClient.client_logout()

if __name__ == '__main__':
    main()