import pathlib
CURRENT_DIR = pathlib.Path(__file__).parent.absolute()

import site
site.addsitedir(f'{CURRENT_DIR.parent}')

from DlmsCosemClient import DlmsCosemClient, AddrSize, mechanism
import serial
import click
from lib.Utils.CalMode import CalMode
from config import CosemList


@click.command()
@click.option('--port', prompt="Enter serial port")
def main(port):
    dlmsClient = DlmsCosemClient(
        port=port,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.05,
        inactivity_timeout=10,
        login_retry=1,
        meter_addr=100,
        client_nb=115,
        address_size=AddrSize.TWO_BYTE
    )
    
    loginResult = dlmsClient.client_login('wwwwwwwwwwwwwwww', mechanism.HIGH_LEVEL)
    print(f'Login result: {loginResult}')
    
    calModeReg = CalMode()
    cosem_calMode = CosemList.CalMode
    raw_calMode = dlmsClient.get_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2)
    calModeReg.extract(raw_calMode)
    print(f'Excess bytes: {raw_calMode}')
    calModeReg.info(verbose=True)
    calModeReg.Cycles.set(500)
    
    result = dlmsClient.set_cosem_data(cosem_calMode.classId, cosem_calMode.obis, 2, 9, calModeReg.dataFrame())
    print(f'Result: {result}')
    dlmsClient.client_logout()
    

if __name__ == '__main__':
    main()
    