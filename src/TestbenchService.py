import pathlib
import site
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
site.addsitedir(CURRENT_PATH.parent)

import gc
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
            "systemGetSupportedTestBench_v1": self.system_getSupportedTestBench,
            "systemAddTestBench_v1": self.system_addTestBench,
            "systemCloseTestBench_v1": self.system_closeTestBench,
        }
    
    def start(self):
        self.mSocket.bind((self.ipAddress, self.port))
        self.mSocket.listen()
        # self.mSocket.settimeout(0.1)
        print(f'Server is listening to {self.ipAddress} {self.port}')
        while True:
            try:
                clientSocket, clientAddress = self.mSocket.accept()
            except TimeoutError:
                sleep(0.1)
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
        
    
    def system_addTestBench(self, apiData:dict, socketClient:socket.socket):
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
                newTestbench = GenyTestBench(usbport=serialport, baudrate=baudRate)
                newTestbench.open()
                self.testBench[id] = newTestbench
                isOk = True
            elif testBenchVendor == 'Geny YC99T_3C':
                newTestbench = GenyTestBench(usbport=serialport, baudrate=baudRate)
                newTestbench.open()
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
                del self.testBench[id]
                # gc.collect()
                
            print('Current testbench:', self.testBench)
            
        else:
            if id not in self.testBench:
                socketClient.send(b'NA. Testbench is not exist')
            self.testBench[id].close()
            del self.testBench[id]
            print('Current testbench:', self.testBench)
        
        gc.collect()
        socketClient.send(b'OK')
    

# def test():
#     COM_PORT = 'COM1'
    
#     is_alreadyOpened = False
    
#     geny = GenyApi('coba')
#     print('Open')
#     try:
#         result = geny.open('COM1', 9600, "Geny YC99T_5C")
#         print(f'Response: {result}')
#     except Exception as e:
#         print('Open failed')
#         if COM_PORT in str(e):
#             print(f'{COM_PORT} already opened')
#             is_alreadyOpened = True

#             # print('Close first')
#             # geny.close()
#             # result = geny.open('COM1', 9600, "Geny YC99T_5C")
#             # print(f'Response: {result}')
        
#     print('Close')
#     result = geny.close()
#     print(f'Response: {result}')
    

import sys
argv = sys.argv
if '-s' in argv:
    testbenchService = TestBenchService('localhost', 1234)
    testbenchService.start()
    while True:
        sleep(0.1)