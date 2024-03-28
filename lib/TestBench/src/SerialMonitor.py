import serial 
from datetime import datetime,timedelta
import sys
import time
import threading

class SerialMonitor:
    '''
        Handler for GENY serial communication
    '''

    def __init__(self,usb_port:str, baudrate:int, onReceive):
        '''
            params:
                usb_port (str) USB path attached to GENY test bench
                baudrate (int) Baudrate used to communicate with the test benchs
                onReceive (function) Function used as callback when there is buffer received from test bench
        '''
        if sys.platform.startswith('win'):
            self.ser = serial.Serial(
                port = usb_port, 
                baudrate = baudrate,
                parity = serial.PARITY_NONE,
                bytesize = serial.EIGHTBITS,
                stopbits = serial.STOPBITS_ONE,
                timeout = 0.1 # octet string timeout
            )    
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            self.ser = serial.Serial(
                port = usb_port, 
                baudrate = baudrate,
                parity = serial.PARITY_NONE,
                bytesize = serial.EIGHTBITS,
                stopbits = serial.STOPBITS_ONE,
                timeout = 0.1,  # octet string timeout
                exclusive = True
            )
        
        self.port = usb_port
        self.recvBuffer = b''
        self.recv_buffer = []
        self.serviceIsActive = False
        self.emergency = False
        self.callback = onReceive
        self.isRunning = False
        self.service = threading.Thread(target=self.serialMonitor, daemon=True)
    
    def startMonitor(self):
        '''
            Run serial handler monitor
        '''
        print('[SerialHandler] check serial is open')
        if not self.ser.is_open:
            print('[SerialHandler] opening serial')
            self.ser.open()
        else:
            print('[SerialHandler] serial already open')
            
        print('[SerialHandler] starting serialMonitor')
        try:
            self.service.start()
            self.isRunning = True
        except:
            self.service.join()
            self.isRunning = True

    def stopMonitor(self, isBlocking=True):
        '''
            Stop serial handler monitor
        '''
        print('[SerialHandler] stoping serialMonitor')
        self.isRunning = False
        if isBlocking:                
            while self.serviceIsActive:
                time.sleep(0.1)
        
        # make sure to close serial port
        if self.ser.is_open:
            self.ser.close()
        
    def transaction(self, dataFrame:bytearray, timeout=5) -> bytearray:
        '''
            parameter
                dataFrame (bytearray) data farme will be sent to test bench
                timeout (int) how much time for waiting serial answer in second
        '''
        self.recvBuffer = b''
        self.ser.write(dataFrame)
        d_initial = datetime.now()
        t_timeout = timedelta(seconds=timeout)
        while datetime.now() - d_initial < t_timeout and self.isRunning:
            if self.recvBuffer == b'':
                time.sleep(0.1)
                continue
            temp = self.recvBuffer
            self.recvBuffer = b''
            # print(f'[SerialMonitor] Transaction {temp}')
            return temp
        return b''

    def serialWrite(self, dataFrame:bytearray)->None:
        '''
            send serial buffer to serial
        '''
        self.ser.write(dataFrame)
        
    def serialMonitor(self):
        print('[SerialHandler] serialMonitor started')
        while self.isRunning:
            self.serviceIsActive = True
            # self.recvBuffer = b''
            tempBuffer = b''
            while self.isRunning:
                temp = self.ser.read()
                if temp != b'':
                    tempBuffer += temp
                else: # enter this block if serial not detect incoming data (refer timeout parameter on class Serial)
                    if len(tempBuffer) > 0:
                        self.recvBuffer = tempBuffer
                        if self.callback != None:
                            self.callback(tempBuffer)
                        break
        print('[SerialHandler] closing serial')
        self.ser.close()
        print('[SerialHandler] serialMonitor has been terminated')
        self.serviceIsActive = False
        