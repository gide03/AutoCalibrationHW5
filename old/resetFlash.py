import os
import logging
import serial
import pathlib
import argparse
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
parser = argparse.ArgumentParser(description='HW5.0 Flash erase. You could conigure this environment at config.py')
parser.add_argument('-p', '--meterport', type=str, help='Communication port for meter.')
# parser.add_argument('-g', '--genyport', type=str, help='communication port for geny')
args = parser.parse_args()

import config
from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec

METER_USB_PORT = config.METER_USB_PORT
if args.meterport != None:
    METER_USB_PORT = args.meterport

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
    port=METER_USB_PORT,
    baudrate=19200,
    parity=serial.PARITY_NONE,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.3,
    inactivity_timeout=10,
    login_retry=1,
    meter_addr=commSetting.METER_ADDR,
    client_nb=commSetting.CLIENT_NUMBER,
)

ser_client.client_logout()
login_result = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
print('login result: ',login_result)
obisSample = '0;0;96;15;0;255'
valueBefore = ser_client.get_cosem_data(1, obisSample, 2)
print(f'temp before ({obisSample}): {valueBefore}')

resetResult = ser_client.set_cosem_data(1,'1;1;128;130;3;255',2,22,1)
print(f'reset flash result: {"SUCCESS" if resetResult==0 else "FAILED"}')

input('\nPlease restart the meter. Press ENTER to continue')
ser_client.client_logout()
login_result = ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
print('login result: ',login_result)
valueAfter = ser_client.get_cosem_data(1, obisSample, 2)
print(f'temp after ({obisSample}): {valueAfter}')

ser_client.client_logout()