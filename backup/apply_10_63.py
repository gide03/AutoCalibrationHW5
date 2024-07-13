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

from Utils.CalibrationData_10_63 import CalibrationRegister as CalibrationData_10_63
from Utils.MeterSetup import MeterSetup

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
    calibrationData_10_63 = CalibrationData_10_63()

    with open(f'{CURRENT_PATH}/backup/{meterid}_10_54.pkl', 'rb') as f:
        calibrationData_10_54 = pickle.load(f)

    calib_reg_10_63 = vars(calibrationData_10_63)
    calib_reg_10_54 = vars(calibrationData_10_54)
    for reg_3 in calib_reg_10_63:
        calData_10_63 = calib_reg_10_63[reg_3]
        if reg_3 in calib_reg_10_54:
            calData_10_54 = calib_reg_10_54[reg_3]
            calib_reg_10_63[reg_3].set(calData_10_54.value)
            print(f'set {calData_10_63.name} from {calData_10_63.value} to {calData_10_54.value}')
    
    # offset phase delay
    calibrationData_10_63.IrmsGainPhA.set(calibrationData_10_63.IrmsGainPhA.value - 415)
    calibrationData_10_63.IrmsGainPhB.set(calibrationData_10_63.IrmsGainPhB.value - 416)
    calibrationData_10_63.IrmsGainPhC.set(calibrationData_10_63.IrmsGainPhC.value - 416)
    calibrationData_10_63.PhaseDelayA.set(calibrationData_10_63.PhaseDelayA.value + 213)
    calibrationData_10_63.PhaseDelayB.set(calibrationData_10_63.PhaseDelayB.value + 214)
    calibrationData_10_63.PhaseDelayC.set(calibrationData_10_63.PhaseDelayC.value + 217)

    cosem_meterSetup = config.CosemList.MeterSetup
    meterSetup = MeterSetup()
    meterSetup.updateCRC(calibrationData_10_63)

    logger.info(f'Set meter setup')
    result = dlmsClient.set_cosem_data(cosem_meterSetup.classId, cosem_meterSetup.obis, 2, 9, meterSetup.dataFrame())
    logger.info(f'Meter setup set result: {result}')

    logger.info(f'Write calibration_10_63: {calibrationData_10_63.dataFrame()}')
    result = dlmsClient.set_cosem_data(cosem.classId, cosem.obis, 2, 9, calibrationData_10_63.dataFrame())
    logger.info(f'Result {result}')

    with open(f'{CURRENT_PATH}/backup/{meterid}_10_63.pkl', 'wb') as f:
        pickle.dump(calibrationData_10_63, f)

    dlmsClient.client_logout()

if __name__ == '__main__':
    main()