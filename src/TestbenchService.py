import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__)
site.addsitedir(CURRENT_PATH)

import socket
import serial
import json
from typing import Tuple
from threading import Thread
from time import sleep
from lib.TestBench.GenyTestBench import GenyTestBench

class TestBenchService:
    SupportedTestBench = {
        "Geny YC99T_5C",
        "Geny YC99T_3C"
    }
    
    def __init__(self, ipAddress:str='localhost', port:int=1234):
        self.ipAddress = ipAddress
        self.port = port
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.testBench = {}
                
        self.api = {
            "systemGetSupportedTestBench": self.system_getSupportedTestBench,
            "systemAddTestBench": self.systen_addTestBench,
            "systemCloseTestBench": self.system_closeTestBench,
        }
    
    def start(self):
        self.mSocket.bind((self.ipAddress, self.port))
        self.mSocket.listen()
        self.mSocket.settimeout(0.1)
        print(f'Server is listening to {self.ipAddress} {self.port}')
        while True:
            try:
                clientSocket, clientAddress = self.mSocket.accept()
            except TimeoutError:
                continue

            # Create handler
            handler = Thread(target=self.clientHandler, daemon=True, args=(clientSocket,))
            handler.start()
            sleep(0.01)
            
    def parseRequest(self, requestBytes:bytes) -> Tuple[str, str, str]:
        '''
            split request frame from client
            
            parameters:
                - requestBytes
            
            return:
                tuple of agentName `str`, request API `str`, api data `str` (loaded as dict)
        '''
        _req = requestBytes.decode('utf-8')
        _req = _req.split('#')
        
        agentName = _req[0]
        api, data = _req[1].split('?')
        # print(f'Agent name : {agentName}')
        # print(f'Request API: {api}')
        # print(f'API data   : {data}')
        data = json.loads(data)
        return agentName, api, data
        
    
    def clientHandler(self, clientSocket:socket.socket):
        '''
            Thread function that will handle request from client. Each API have it's function to handle request, and the response will send inside api funtion
            prameters:
                - clientSocket `socket`:
        '''
        print('Receive Connection')
        while True:
            try:
                data = clientSocket.recv(516)
                if not data:
                    break
                
                agentName, api, data = self.parseRequest(data)
                if api not in self.api:
                    clientSocket.send(b'NA')
                elif 'system' in api:
                    self.api[api](data, clientSocket)
                else:
                    testBench = self.testBench[agentName]
                    self.api[api](testBench, data, clientSocket)    
            except TimeoutError:
                break
        clientSocket.close()
        print('[Client Handler] Socket closed')
                
    #
    # HANDLERS
    #
    def system_getSupportedTestBench(self, apiData:dict, socketClient:socket.socket):
        '''
            apiData will be ignored
        '''
        
    
    def systen_addTestBench(self, apiData:dict, socketClient:socket.socket):
        '''
            apiData keys:
                - id `str`: used for testbench id
                - testbenchVendor `str`: vendor of the test bench supported testbench: [Geny YC99T_5C, Geny YC99T_3C]
                - serialport `str`: usb serial port
                - baudRate `int`: baudate for the serial
        '''
        try:
            id = apiData['id']
            testBenchVendor = apiData['testbenchVendor']
            serialport = apiData['serialPort']
            baudRate = apiData['baudRate']
        except:
            socketClient.send(b'NA. Key error')
            return
        
        # Creating Connection to test bench
        isOk = False
        try:
            if testBenchVendor == 'Geny YC99T_5C':
                newTestbench = GenyTestBench.GenyTestBench(usbport=serialport, baudrate=baudRate)
                self.testBench[id] = newTestbench
                isOk = True
            elif testBenchVendor == 'Geny YC99T_3C':
                newTestbench = GenyTestBench.GenyTestBench(usbport=serialport, baudrate=baudRate)
                self.testBench[id] = newTestbench
                isOk = True
        except serial.SerialException as e:
            socketClient.send(f'NA. {str(e)}'.encode('utf-8'))
            return
        
        if isOk:
            socketClient.send(b'OK')
        else:
            socketClient.send(b'NA')
        
    def system_closeTestBench(self, apiData:dict, socketClient:socket.socket):
        '''
            apiData keys:
                - id `str`: id of the test bench that will be closed. if it is '*' then all test bench will be closed
        '''
        try:
            id = apiData['id']
        except:
            socketClient.send(b'NA, Key error')
            return
        
        # Close testbench
        if id == '*':
            tbIds = list(self.testBench.keys())
            for id in tbIds:
                testbench = self.testBench[id]
                del testbench
        else:
            if id not in self.testBench:
                socketClient.send(b'NA. Testbench is not exist')
            self.testBench[id].close()
            del self.testBench[id]
            print('Current testbench:', self.testBench)
            
        socketClient.send(b'OK')
    
class GenyApi:
    def __init__(self, id:str):
        self.id=id
        self.ipAddress = 'localhost'
        self.port = 1234
        
        self.streamBuffer = 512
        self.tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClient.connect((self.ipAddress, self.port))
        
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
        api = f'{self.id}#systemAddTestBench?{payload}'.encode('utf-8')
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
        api = f'{self.id}#systemCloseTestBench?{payload}'.encode('utf-8')
        response = self.transaction(api)
        if 'OK' in response:
            return True
        else:
            raise Exception(f'Could not close test bench. Error Message: {response}')

def test():
    COM_PORT = 'COM1'
    
    is_alreadyOpened = False
    
    geny = GenyApi('coba')
    print('Open')
    try:
        result = geny.open('COM1', 9600, "Geny YC99T_5C")
        print(f'Response: {result}')
    except Exception as e:
        print('Open failed')
        if COM_PORT in str(e):
            print(f'{COM_PORT} already opened')
            is_alreadyOpened = True

            # print('Close first')
            # geny.close()
            # result = geny.open('COM1', 9600, "Geny YC99T_5C")
            # print(f'Response: {result}')
        
    print('Close')
    result = geny.close()
    print(f'Response: {result}')
    

import sys
argv = sys.argv
if '-s' in argv:
    testbenchService = TestBenchService('localhost', 1234)
    testbenchService.start()
    while True:
        sleep(0.1)
else:
    test()