import os
import serial
import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(f'{CURRENT_PATH.parent}')

from lib.Utils.Logger import getLogger
from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient

try:
    from . import config
except:
    import config

if not os.path.exists(f'{CURRENT_PATH}/logs'):
    os.mkdir(f'{CURRENT_PATH}/logs')

def main(meterid, comport, timediv):
    filename = f'{CURRENT_PATH}/logs/{meterid} rtc_synchronize.log' 
    logger = getLogger(filename)
    logger.info('='*30)
    logger.info(f'RTC Sync for {meterid} - serialport {comport}')
    logger.info('='*30)
    
    GMT = int(timediv)

    ser_client = DlmsCosemClient(
        port=comport,
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

    ser_client.client_logout()
    logger.info('Login to meter')
    try:
        loginResult = ser_client.client_login(config.commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)
        logger.info(f'Login result: {loginResult}')
    except:
        logger.critical('Could not login to meter')
        exit(1)
      
    # TODO: Read battery voltage
    logger.info(f'Fetch battery level')
    batteryLevel = ser_client.get_cosem_data(cosem_batteryLevel.classId, cosem_batteryLevel.obis, 2)
    if isinstance(batteryLevel,str):
        logger.critical(f'Could not fetch battery level. Read result: {batteryLevel}')
    logger.info(f'Battery level: {batteryLevel*10**-3} V')
    if (batteryLevel*10**-3) >= 3.6:
        logger.info('Battery voltage PASSED')
    else:
        logger.critical('Battery voltage under 3.6V')
        ser_client.client_logout()
        exit()
    
    # TODO: Synchronize RTC
    cosem_clock = config.CosemList.Clock
    logger.info(f'Synchronize RTC using GMT: {GMT} OR time deviation: {GMT*60}')
    logger.info('Read current time deviation')
    timeDeviation = ser_client.get_cosem_data(cosem_clock.classId, cosem_clock.obis, 3)
    logger.info(f'Time deviation: {timeDeviation}')
    if timeDeviation != GMT*60:
        logger.info(f'Set time deviation to {GMT*60}')
        setResult = ser_client.set_cosem_data(cosem_clock.classId, cosem_clock.obis, 3, 16, 60*GMT)
        logger.info(f'Set deviation result: {setResult}')
        logger.info('Time deviation after')
        timeDeviation = ser_client.get_cosem_data(cosem_clock.classId, cosem_clock.obis, 3)
        logger.info(f'Time deviation: {timeDeviation}')
    else:
        logger.info(f'Time deviation already at {GMT}')
    
    logger.info('Synchronize Clock')
    currentDate = datetime.now() - timedelta(minutes=60*7) + timedelta(minutes=60*GMT)
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
    clock_data = ser_client.get_cosem_data(cosem_clock.classId, cosem_clock.obis, 2)
    logger.info(f"Clock data: {clock_data}")
    logger.info('Logout from meter')
    ser_client.client_logout()
    logger.info('RTC sync finished :)')
    
    input('Press Enter to continue')


import click
@click.command()
@click.option('--meterid', prompt='Enter meter id')
@click.option('--meterport', prompt='Enter meterport')
@click.option('--timediv', prompt='Enter timediv')
def run(meterid, meterport, timediv):
    main(meterid, meterport, timediv)
    
if __name__ == '__main__':
    run()