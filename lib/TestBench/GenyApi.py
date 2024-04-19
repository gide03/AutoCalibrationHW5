import socket
import json

class GenyApi:
    class GenyVersion:
        YC99T_5C = 'Geny YC99T_5C'
        YC99T_3C = 'Geny YC99T_3C'
    
    def __init__(self, id:str, port:int=1234):
        '''
            parameters:
                -id `id`: nametag for geny connection
                -port `int`: port where the service is listening to
        '''
        self.id=id
        self.ipAddress = 'localhost'
        self.port = port
        
        self.streamBuffer = 1024
        self.tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClient.connect((self.ipAddress, self.port))
        
        
        # Register
        self.isCommon = True
        self.voltage = 230
        self.current = 0
        self.phase = 0
        self.frequency = 50
        self.meterConstant = 1000
        self.ring = 3
        
    def transaction(self, api:bytearray, timeout:int=6)->str:
        self.tcpClient.settimeout(timeout)
        self.tcpClient.send(api)
        recvData = self.tcpClient.recv(self.streamBuffer)
        return recvData.decode('utf-8')
    
    def open(self, serialPort:str, baudrate:int, testBenchVendor:str):
        '''
            attach serial port to test bench. Raise exception if failed
        
            parameters:
                serialPort `str`: usb serial port
                baudRate `int`: baud rate used for usb serial
                testBenchVendor `str`: test bench will be used. Use get vendor list to show all supported testbench
            
            return:
                - True if SUCCESS
        '''
        payload = {
            "id": self.id,
            "testbenchVendor": testBenchVendor,
            "serialPort": serialPort,
            "baudRate": baudrate
        }
        payload = json.dumps(payload)
        api = f'{self.id}#systemAddTestBench_v1?{payload}'.encode('utf-8')
        response = self.transaction(api)
        if 'OK' in response:
            return True
        else:
            raise Exception(f'Could not open test bench. Error Message: {response}')
        
    def close(self):
        '''
            Close geny connection
        '''
        payload = {
            "id": self.id
        }
        payload = json.dumps(payload)
        api = f'{self.id}#systemCloseTestBench_v1?{payload}'.encode('utf-8')
        response = self.transaction(api)
        if 'OK' in response:
            return True
        else:
            raise Exception(f'Could not close test bench. Error Message: {response}')

    def closeAll(self):
        '''
            Close all geny connections
        '''
        payload = {
            "id" : "*"
        }
        payload = json.dumps(payload)
        api = f'{self.id}#systemCloseTestBench_v1?{payload}'.encode('utf-8')
        response = self.transaction(api)
        if 'OK' in response:
            return True
        else:
            raise Exception(f'Could not close test bench. Error Message: {response}')
        
    def setGeny(self, 
        isCommon:bool = None,
        voltage:float = None,
        current:float = None,
        phase:float = None,
        frequency:int = None,
        meterConstant:int = None,
        ring:int = None
    ):
        '''
            None means 
        '''
        payload = {
            "id" : self.id,
            "isCommon" : isCommon,
            "voltage" : voltage,
            "current" : current,
            "phase" : phase,
            "frequency" : frequency,
            "meterConstant" : meterConstant,
            "ring" : ring,
        }
        payload = json.dumps(payload)
        api = f'{self.id}#api_applySource_v1?{payload}'.encode('utf-8')
        response = self.transaction(api)
        if 'OK' in response:
            return True
        else:
            raise Exception(f'Could not set test bench. Error Message: {response}')
    
    def getReadBack(self) -> dict:
        '''
        
        '''
        api = f'{self.id}#api_getReadBack_v1?[]'.encode('utf-8')
        response = self.transaction(api)
        # try:
        print(response)
        return None
        # except:
        #     raise Exception(f'Could not close test bench. Error Message: {response}')
            