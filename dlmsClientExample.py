import serial
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


if __name__ == "__main__":
    ser_client = DlmsCosemClient(
        port="/dev/ttyUSB4",
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

    def bytes_to_hex_list(byte_list):
        result = []
        for i in byte_list:
            result.append(int(i))
        return result

    ser_client.client_login(commSetting.AUTH_KEY, mechanism.HIGH_LEVEL)

    clock_data = ser_client.get_cosem_data(8, "0;0;1;0;0;255", 2)
    print("CLOCK DATA:", clock_data)

    ser_client.client_logout()
