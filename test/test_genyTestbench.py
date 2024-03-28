import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import pytest
from time import sleep
from lib.TestBench.GenyTestBench import GenyTestBench

@pytest.mark.geny_v1
def test_serialPort():
    '''
        Ekspektasi:
            1. Saat pembuatan object serial port akan langsung di buka.
            2. Saat object.close() serial akan tertutup. (FYI: Terdapat background process <serialMonitor> yang perlu di stop pula)
            3. Saat object.open() serial akan terbuka kembali.
            4. Saat object di delete, serial akan tertutup
    '''
    
    geny = GenyTestBench(usbport='com1', baudrate=115200)
    serialPort = geny.serialMonitor.ser
    # assert serialPort.is_open()
    print('Stop monitor')
    geny.serialMonitor.stopMonitor()
    
    print('Force close serialport')
    serialPort.close()
    print('Start monitor')
    serialPort.open()
    
    sleep(2)
    

test_serialPort()