import os
import logging
import serial
import pathlib
import argparse
from datetime import datetime
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
parser = argparse.ArgumentParser(description="Checking battery voltage and synchronize meter clock. If you didn't pass parameter, configuration will taken from config.py")
parser.add_argument('-p', '--meterport', type=str, help='Communication port for meter.')
# parser.add_argument('-g', '--genyport', type=str, help='Communication port for geny.')
args = parser.parse_args()


import config
from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from testcase import TestFetchCosem


METER_USB_PORT = config.METER_USB_PORT
if args.meterport != None:
    METER_USB_PORT = args.meterport

if not os.path.exists(f'{CURRENT_PATH}/logs'):
    os.mkdir(f'{CURRENT_PATH}/logs')

print('Please input meter ID. If empty program will terminated')
meterId = input('Meter ID: ')
if len(meterId) == 0:
    exit('Calibration Canceled')
    

#
# Logger setup    
#
filename = f'{CURRENT_PATH}/logs/{meterId} rtc_synchronize.log' 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.DEBUG)
# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# End of LOGGER  Configuration

# TODO: Distribute Logger
TestFetchCosem.logger = logger


ser_client = DlmsCosemClient(
    port=METER_USB_PORT,
    baudrate=19200,
    parity=serial.PARITY_NONE,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.05,
    inactivity_timeout=10,
    login_retry=1,
    meter_addr=config.commSetting.METER_ADDR,
    client_nb=config.commSetting.CLIENT_NUMBER,
)

# list cosem will be access
cosem_batteryLevel = config.CosemList.BatteryVoltage
cosem_clock = config.CosemList.Clock

logger.info('Login to meter')
if ser_client.client_login(config.commSetting.AUTH_KEY, mechanism.HIGH_LEVEL):
    # TODO: Read battery voltage
    logger.info(f'Fetch battery level')
    batteryLevel = TestFetchCosem.fetch(ser_client, cosem_batteryLevel, 2)    
    logger.info(f'Battery level: {batteryLevel*10**-3} V')

    isValid = input(f'Is valid? (default y)')
    if isValid == 'n':
        logger.critical('REJECT Battery voltage.')
        ser_client.client_logout()
        exit()
    logger.info('Battery voltage PASSED')
    
    # TODO: Synchronize RTC
    logger.info('Synchronize Clock')
    currentDate = datetime.now()
    year_HB = (currentDate.year >> 8) & 0xff
    year_LB = currentDate.year & 0xff
    month = currentDate.month
    day = currentDate.day
    weekday = currentDate.weekday() + 1
    hour = currentDate.hour
    minute = currentDate.minute
    second = currentDate.second
    hundredths = 0
    deviation = 128
    clockstatus = 0
    season = 0
    dlmsDate = [year_HB, year_LB, month, day, weekday, hour, minute, second, hundredths, deviation, clockstatus, season]
    result = ser_client.set_cosem_data(cosem_clock.classId, cosem_clock.obis, 2, 9, dlmsDate)
    logger.info(f'Set current time with {currentDate} (inDlms {dlmsDate}) -- {"SUCCESS" if result==0 else "FAILED"}')
    if result != 0:
        logger.critical('Set clock FAILED')
        ser_client.client_logout()
        exit()
    logger.info('Check meter time after synchronize')
    clock_data = ser_client.get_cosem_data(8, "0;0;1;0;0;255", 2)
    logger.info(f"Clock data: {clock_data}")
    logger.info('Logout from meter')
    ser_client.client_logout()
    logger.info('RTC sync finished :)')
    
    input('Press Enter to continue')