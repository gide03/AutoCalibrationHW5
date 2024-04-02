'''
CALIBRATION PROCESS
1.	Attach the probes to Cal/programming pads.
2.	Apply 240 Volts at test amps with power factor (60 degree) to the meter.
3.	Apply 2s delay to allow meter to power up.
4.	The meter will power up with default calibration data.
5.	Write “Calibration Data” (OBIS 0.128.96.14.80.255) and ‘Meter Setup’ (OBIS 0.128.96.14.81.255) with default values to the meter according to the meter form, class, etc. from the meter bar code scan. Note to set RTC temperature coeff = 0.
6.	Read the temperature information from the meter (OBIS 1.0.96.9.0.255) and standard. Store the information for later averaging.
7.	Program LED pulse output (OBIS 0.128.96.6.8.255) to “No Pulse”, so that calibration mode can be used.
8.	Start calibration mode (OBIS 0.128.96.14.82.255) for PF Watts with a test time of 1.5s (90 cycles) with RTC output continue mode on (cal mode status = 1). 
9.	4Hz RTC pulses are enabled from RTC output after start pulse.
10.	Delay for test to complete.
11.	Read the instantaneous voltage and current from Cal Mode reading, temperature (OBIS 1.0.96.9.0.255) information from the meter and the calibration standard.  Read the RTC 4Hz frequency from the counter. 
12.	Average the temperature, voltage, current, and RTC frequency readings from both the meter and standard.
13.	Calculate the calibration constants such as gains, phase delays, RTC error. Check if all those constants are within the limit.
14.	Write the new constants via “Calibration Data” and ‘Meter Setup’ to the meter.
'''

'''
VERIFICATION PROCESS
1.	Verify that 240 Volts at test amps with power factor is applied to the meter. 
2.	Apply 2s delay for new constants running.
3.	Read all the calibration values and verify that they were updated correctly.
4.	Start calibration mode (OBIS 0.128.96.14.82.255) for Watts with a test time of 0.5s (30 cycles)
5.	Delay for test to complete.
6.	Read the result of the calibration mode command and store this data into the database as the PF Reading.
7.	Check if PF accuracies are within the limits. If the error is not within the 0.10%, adjust the phase delay, and redo the PF verification (step #1).
8.	Change the load to 240 Volts at Test Amps at Unity power factor.
9.	Apply 2s for meter and standard to stabilize.
10.	Start calibration mode for Watts with a test time of 0.5s (30 cycles).
11.	Delay for test to complete.
12.	Read the result of the Calibration mode command and store this data into the database as the FL Reading.
13.	Check if FL accuracies are within the limits. If the error is not within the 0.05%, adjust the energy gains, write new gains to ‘Calibration Data’. And redo verification from PF verification (step #1).
14.	Change the load to 240 Volts at Light Load at Unity power factor.
15.	Apply 3s for meter and standard to stabilize. 
16.	Start Calibration Mode for Watts with a test time of 1s (60 cycles) with RTC output continue mode off (cal mode status = 0).
17.	Delay for calibration mode to complete.
18.	Read the result of the calibration mode command and store this into the database as LL Reading.
'''

import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__)
site.addsitedir(CURRENT_PATH)

import serial
import config
from time import sleep
from datetime import datetime, timedelta
from src.Logger import getLogger
from lib.TestBench.GenyApi import GenyApi

from lib.Utils.CalibrationData import CalibrationRegister
from lib.Utils.MeterSetup import MeterSetup
from lib.Utils.CalMode import CalMode

from lib.DLMS_Client.dlms_service.dlms_service import mechanism, CosemDataType
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient
from lib.DLMS_Client.hdlc.hdlc_app import AddrSize

PORT_GENY = '/dev/ttyUSB0'
PORT_METER = '/dev/ttyUSB1'

logger = getLogger('dev.log')

logger.info('\n')
logger.info('*'*30)
logger.info('STARRTING CALIBRATION')
logger.info('='*30)


VOLTAGE_NOMINAL = 230   # in Volt
CURRENT_NOMINAL = 30    # in Ampere
POWERUP_DELAY = 10      # in Second
CYCLE_CAL = 90


def calibrate(comPort):
    t = datetime.now()
    logger.info(f'Wait meter for booting for {POWERUP_DELAY}s')
    dlmsClient = DlmsCosemClient(
        port=comPort,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=16,
        client_nb=16,
        address_size = AddrSize.ONE_BYTE
    )

    while datetime.now()-t < timedelta(seconds=POWERUP_DELAY):
        sleep(0.01)

    # Login
    cosemList = config.CosemList()
    loginResult = False
    try:
        logger.info('Login to meter')
        loginResult = dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
        logger.info(f'result login dlms - {loginResult}')
    except Exception as e:
        logger.critical(f'Failed to login, error message: {str(e)}')
        return False

    
    

def main():
    logger.info('='*30)
    logger.info('STARTING CALIBRATION')
    logger.info('='*30)
    
    logger.info('TURN ON GENY')
    geny = GenyApi('Geny')
    geny.open('/dev/ttyUSB0', 9600, GenyApi.GenyVersion.YC99T_5C)
    geny.setGeny(
        isCommon=True,
        voltage=230,
        current=30,
        phase=60,
        frequency=50,
        meterConstant=1000,
        ring=3
    )
    calibrate(PORT_METER)

if __name__ == "__main__":
    main()