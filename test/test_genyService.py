import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import pytest
from time import sleep
from lib.TestBench.GenyApi import GenyApi
from src.TestbenchService import TestBenchService

@pytest.mark.parametrize('serial_port', [
    'COM1'
])
@pytest.mark.parametrize('geny_version', [
    GenyApi.GenyVersion.YC99T_5C
])

@pytest.mark.genyservice_v1
def test_serviceOpenClose(serial_port, geny_version):
    '''
        # Manually test
            Using serial snipping tool ex: Eltima serial monitor
        # Automatic test
            Create Serial object to make sure the serial is opened or not
    
        1. Try open new connection to Geny, there will be 2 possibility:
            1.1 The server will open SUCCESS fully. Then pass to next test
            1.2 The server will reject because it has already exists. Close it and reopen.
        2. Close the connection
    
    '''
    from serial import Serial
    
    # genyService = TestBenchService('localhost', 1234)
    # genyService.start()
    
    geny = GenyApi('Client1')
    print('Open')
    
    # create geny connection
    is_alreadyOpened = False
    try:
        result = geny.open('COM1', 9600, geny_version)
        print(f'Response: {result}')
        assert result
    except Exception as e:
        errorMessage = str(e)
        print(f'Open failed. {str(e)}')
        if 'FileNotFoundError' in errorMessage:
            is_alreadyOpened = False
        elif 'PermissionError' in errorMessage:    
            is_alreadyOpened = True
    
    # recreate the geny connection
    if is_alreadyOpened: 
        print('Connection already exist. Close and reopen connectino')
        result = geny.close()
        print(f'Close connection: {result}')
        assert result
        
        # Create Serial instance to open serial_port. If opened, it already closed on geny.close()
        print('Check serial port')
        temp = Serial(serial_port)
        print('Is closed? '+'PASSED' if temp.is_open else 'FAILED')
        assert temp.is_open
        temp.close()
        
        result = geny.open('COM1', 9600, geny_version)
        print(f'Reopen connection: {result}')
        assert result
        
        # Create Serial instance to open serial_port. If could not opened, it already open on geny.open()
        print('Check serial port')
        try:
            temp = Serial(serial_port)
            temp.close()
        except:
            print('Is opened? '+'PASSED' if temp.is_open else 'FAILED')
            assert False # force false because the serial could open (should be couldn't opened)
        
        
    print('Close')
    result = geny.close()
    print(f'Response: {result}')
    assert result

@pytest.mark.genyservice_v1
def test_duplicatedConnection(serial_port, geny_version):
    '''
        # Manually test
            Using serial snipping tool ex: Eltima serial monitor
        # Automatic test
            Create Serial object to make sure the serial is opened or not
    
        # Test repro
            1. Close all connection
            2. Open connection
            3. Open connection again and make sure the serial is already opened
            2. Close the connection
    
    '''
    from serial import Serial
    
    # genyService = TestBenchService('localhost', 1234)
    # genyService.start()
    
    geny = GenyApi('Client1')
    
    print('Close all connection')
    result = geny.closeAll()
    print(f'Response: {result}')
    
    print('Open first')
    result = geny.open('COM1', 9600, geny_version)
    print(f'Response: {result}')
    
    # Re open connection
    is_alreadyOpened = False
    try:
        print('Open Second')
        result = geny.open('COM1', 9600, geny_version)
        print(f'Response: {result}')
        assert result
    except Exception as e:
        errorMessage = str(e)
        print(f'Open failed. {str(e)}')
        if 'FileNotFoundError' in errorMessage:
            is_alreadyOpened = False
        elif 'PermissionError' in errorMessage:    
            is_alreadyOpened = True
    
    # recreate the geny connection
    if is_alreadyOpened: 
        print('Connection already exist. Close and reopen connectino')
        result = geny.close()
        print(f'Close connection: {result}')
        assert result
        
        # Create Serial instance to open serial_port. If opened, it already closed on geny.close()
        print('Check serial port')
        temp = Serial(serial_port)
        print('status: ' + ('PASSED' if temp.is_open else 'FAILED'))
        assert temp.is_open
        temp.close()
        
        result = geny.open('COM1', 9600, geny_version)
        print(f'Reopen connection: {result}')
        assert result
        
        # Create Serial instance to open serial_port. If could not opened, it already open on geny.open()
        print('Check serial port')
        try:
            temp = Serial(serial_port)
            temp.close()
            assert False # force false because the serial could open (should be couldn't opened)
        except:
            print('status: '+ ('PASSED' if not temp.is_open else 'FAILED'))
        
        
    print('Close')
    result = geny.close()
    print(f'Response: {result}')
    assert result

# test_serviceOpenClose('COM1', GenyApi.GenyVersion.YC99T_5C)
test_duplicatedConnection('COM1', GenyApi.GenyVersion.YC99T_5C)