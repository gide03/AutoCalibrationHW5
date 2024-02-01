import serial
from datetime import datetime, timedelta
from lib.DLMS_Client.dlms_service.dlms_service import CosemDataType, mechanism
from lib.DLMS_Client.DlmsCosemClient import DlmsCosemClient, TransportSec

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
    port="COM4",
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

try:
    if ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL):
        print('Enter to mode HVT')
        obis = '1;1;128;130;1;255'
        classId = 1
        attId = 2
        value = 1
        result = ser_client.set_cosem_data(classId, obis, attId, CosemDataType.e_UNSIGNED, value)


        print('wait 2 seconds')
        import time
        time.sleep(2)
except:
    pass

class TestId:
    def __init__(self, id:int, desc:str, isRunTest:bool):
        self.id = id
        self.desc = desc
        self.isRunTest = isRunTest
        self.isPassed = False

TID = (
    TestId(b'?0\r', 'Show Menu', True),
    TestId(b'?1\r', 'START BIST', True),
    TestId(b'?2\r', 'NIC UART', True),
    TestId(b'?3\r', 'DI UART', True),
    TestId(b'?4\r', 'P1 UART', True),
    TestId(b'?5\r', 'ADC SPI', True),
    TestId(b'?6\r', 'Ext Flash SPI', False), # (Fail) maybe need to manually test
    TestId(b'?7\r', 'DI SPI', True),
    TestId(b'?8\r', 'LCD I2C', True),
    TestId(b'?9\r', 'ACC I2C', True),
    TestId(b'?10\r', 'MAG I2C', True),
    TestId(b'?11\r', 'LCD CONTRAST', True),
    TestId(b'?12\r', 'LCD BACKLIGHT', True),
    TestId(b'?13\r', 'EXT PULSE', True),
    TestId(b'?14\r', 'M1- UB/Test LED1', False), # it is manual
    TestId(b'?15\r', 'M2- UB/Test LED2', False), # it is manual
    TestId(b'?16\r', 'RDS Ctrl', True),
    TestId(b'?17\r', 'AUX Ctrl', True),
    TestId(b'?18(0)\r', 'TAMPER I/P TEST-1', True),
    TestId(b'?18(1)\r', 'TAMPER I/P TEST-2', True),
    TestId(b'?19\r', '32kHz OSC', True),
    TestId(b'?20\r', '16.777Mhz OSC', True),
    TestId(b'?21\r', 'TEMPERATURE', True),
    TestId(b'?22\r', 'POWER GOOD', True),
    TestId(b'?23\r', 'RDS CAP MONITOR', True),
    TestId(b'?24\r', 'BATTERY MONITOR', True),
    TestId(b'?25\r', 'HW EPF', True),
    TestId(b'?26(1)\r', 'DI I/O-1', True),
    TestId(b'?26(2)\r', 'DI I/O-2', True),
    TestId(b'?26(3)\r', 'DI I/O-3', True),
    TestId(b'?27(0)\r', 'Ext I/O-1', True),
    TestId(b'?27(1)\r', 'Ext I/O-1', True),
    TestId(b'?28\r', 'MainB I/O', True),
    TestId(b'?29\r', 'Validate Ext ADC data', True),
    TestId(b'?30\r', 'SWITCH TO MAIN FW', True),
)

mSerial = ser_client.ser
def transaction(buffer, timeout = 10):
    mSerial.write(buffer)
    tempBuffer = b''
    timeoutTime = timedelta(seconds=timeout)
    startTime = datetime.now()
    while datetime.now() - startTime < timeoutTime:
        byte = mSerial.read()
        if byte != b'':
            tempBuffer += byte
        else:
            if tempBuffer != b'':
                return tempBuffer
    return b'ERROR::Serial timeout'

print('==== HVT Start ====')
for test in TID:
    if test.isRunTest:
        print(f'Testing {test.desc} -- ',end='')
        result = transaction(test.id, 120)
        result = result.decode('utf-8')
        print(result)
        if 'Pass' in result:
            test.isPassed = True
    else:
        print(f'Skip Testing -- {test.desc}')

print('SUMMARY')
for test in TID:
    status = 'FAILED'
    if test.isPassed:
        status = 'PASSED'
    if test.isRunTest == False:
        status = 'SKIPED'
    print(f'Test {test.desc} -- {status}')