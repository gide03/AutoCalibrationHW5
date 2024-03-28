import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import gc
import pytest
from time import sleep
from lib.TestBench.GenyTestBench import GenyTestBench

@pytest.mark.parametrize('serial_port', [
    'COM1'
])


@pytest.mark.geny_v1
def test_serialPort(serial_port):
    '''
        Ekspektasi:
            1. Serial port automatically opened when generate new object.
            2. Serial port will closed on object.close(). (FYI: There is thread named SerialMonitor that also need to be stopped)
            3. Serial port will reopen when object.open(). Test bench will switched to rs232 mode.
            4. Serial port will closed after delete the object. We may need to gc.collect().
    '''    
    geny = GenyTestBench(usbport=serial_port, baudrate=115200)
    serialPort = geny.getSerial()
    
    # It is okay if occur exception the main expectation is the serial port could be opened or closed
    try:
        geny.open()
    except:
        pass
    assert serialPort.is_open == True
    
    try:
        geny.close()
    except:
        pass
    assert serialPort.is_open == False
    
    # Open it again
    try:
        geny.open()
    except:
        pass
    assert serialPort.is_open 
    
    # Delete the object, serial should closed. Indicated we could generate new Serial object
    from serial import Serial
    print('Test delete object')
    del geny
    gc.collect()

    isOk = False
    newSer = Serial(port=serial_port)
    isOk = newSer.is_open
    assert isOk    
    sleep(2)