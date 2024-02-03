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
        self.runService = True
        self.isRunning = False
        self.service = threading.Thread(target=self.serialMonitor, daemon=True)
    
    def startMonitor(self):
        '''
            Run serial handler monitor
        '''
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
        print('[SerialHandler] starting serialMonitor')
        self.isRunning = False
        if isBlocking:
            while self.serviceIsActive:
                time.sleep(0.1)
        
    def transaction(self, dataFrame:bytearray, timeout=10) -> bytearray:
        '''
            parameter
                dataFrame (bytearray) data farme will be sent to test bench
                timeout (int) how much time for waiting serial answer in second
        '''
        self.recvBuffer = b''
        self.ser.write(dataFrame)
        d_initial = datetime.now()
        t_timeout = timedelta(seconds=timeout)
        while datetime.now() - d_initial < t_timeout:
            if self.recvBuffer == b'':
                time.sleep(0.1)
                continue
            temp = self.recvBuffer
            self.recvBuffer = b''
            print(f'[SerialMonitor] Transaction {temp}')
            return temp
        return b''

    def serialWrite(self, dataFrame:bytearray)->None:
        '''
            send serial buffer to serial
        '''
        self.ser.write(dataFrame)
        
    def serialMonitor(self):
        print('[SerialHandler] serialMonitor started')
        while self.runService:
            self.serviceIsActive = True
            # self.recvBuffer = b''
            tempBuffer = b''
            while self.runService:
                temp = self.ser.read()
                if temp != b'':
                    tempBuffer += temp
                else: # enter this block if serial not detect incoming data (refer timeout parameter on class Serial)
                    if len(tempBuffer) > 0:
                        self.recvBuffer = tempBuffer
                        if self.callback != None:
                            self.callback(tempBuffer)
                        break
        print('[SerialHandler] serialMonitor has been terminated')
        self.serviceIsActive = False
            

    # def serialWatcher(self) -> None:
    #     '''
    #         This is serial watcher for full duplex fuctionality
    #     '''
    #     print('SerialWatcher STARTED!!')
    #     while self.runService:
    #         self.serviceIsActive = True # Indicate the thread is running
    #         on_receive = False
    #         data_length = [0,0,0,0]
    #         recv_data = b''
    #         data_counter = 0
    #         while self.runService:
    #             try:
    #                 data_counter += 1

    #                 # receive data based on GENY's protocol
    #                 x = self.ser.read()
    #                 if x[0] == 0x7e:
    #                     on_receive = True
    #                 if on_receive and 1<data_counter<6: # fetch 4 byte after flag
    #                     data_length[data_counter-2] = x[0]
    #                 recv_data+=x
    #                 if on_receive and x[0] == 0xff and data_counter==struct.unpack('<I',bytearray(data_length))[0]+4+4:
    #                     self.recv_buffer = list(recv_data)[:]
    #                     if self.recv_buffer[5] == 143: # GENY FATAL ERROR
    #                         self.emergency = True
    #                     # print(f'Got SERIAL DATA: {self.recv_buffer}')
    #                     time.sleep(0.01)
    #                     break
    #             except:
    #                 data_counter -= 1
    #         self.recv_buffer = []
    #     self.ser.close()

    #     self.serviceIsActive = False # Indicate the thread stopped
    #     print('[SerialHandler] Serial monitor has been terminated !!')
    
    # def getSerialBuffer(self) -> list:
    #     '''
    #         Return serial buffer
    #     '''
    #     if len(self.recv_buffer) > 0:
    #         t_buffer = self.recv_buffer[:]
    #         self.recv_buffer = []
    #         return t_buffer
    #     return self.recv_buffer


    # def readResponse(self, timeout:int=30)->bytearray:
    #     '''
    #         read ACK byte stream from GENY with specified length. refe to GENY YC99T-5C documentatio
    #     '''
    #     t1 = datetime.now()
    #     on_receive = False
    #     data_length = [0,0,0,0]
    #     recv_data = b''
    #     data_counter = 0
    #     while datetime.now()-t1 < timedelta(seconds=timeout):
    #         try:
    #             data_counter += 1

    #             # receive data based on GENY's protocol
    #             x = self.ser.read()
    #             if x[0] == 0x7e:
    #                 on_receive = True
    #             if on_receive and 1<data_counter<6: # fetch 4 byte after flag
    #                 data_length[data_counter-2] = x[0]
    #                 t1 = datetime.now() # refresh reference time when data is coming
    #             recv_data+=x
    #             if on_receive and x[0] == 0xff and data_counter==struct.unpack('<I',bytearray(data_length))[0]+4+4:
    #                 return list(recv_data)[:]
    #         except:
    #             data_counter -= 1
    #     return b''

    # # Write serial and get response until timeout
    # def transaction(self,data_frame:list, timeout:int=3, retry:int=3) -> dict:
    #     '''
    #         transaction starts serial write then wait for the response. Then the response will be parsed before return the data. 
    #         Please to consider to check first the error message.        
    #     '''
    #     # TODO: Write serial bytes
    #     payload = bytearray(data_frame)
    #     for i in range(0,retry):
    #         self.ser.write(payload)

    #         # TODO: Wait until recv buffer or timeout
    #         t1 = datetime.now()
    #         while datetime.now() - t1 < timedelta(seconds=timeout):
    #             response = self.getSerialBuffer()
    #             if len(response)>0:
    #                 data = self.extract_response_data(response)
    #                 return data.copy()

    #     print('SERIAL TRANSACTION: Read GENY reach timeout(%s)'%timeout)
    #     result = {
    #         'SOI'                 : None,
    #         'DATA_FRAME_LENGTH'   : None,
    #         'COMMAND'             : None,
    #         'ERROR_CODE'          : "ERROR. Serial read reach timeout. Source: SerialHandler.py::transaction",
    #         'DATA'                : None,
    #         'CRC'                 : None
    #     }
    #     return result

    # def extract_response_data(self, data_frame:list) -> dict:
    #     '''
    #         Parse received data from GENY
    #     '''
    #     FLAG_SOI = 0x7e
    #     FLAG_EOI = 0xff
    #     SOI_BLENGTH = 1
    #     DF_BLENGTH = 4
    #     COMMAND_BLENGTH = 2
    #     ERROR_CODE_BLENGTH = 1
    #     CRC16_BLENGTH = 2
    #     EOI_BLENGTH = 1

    #     # Protection for empty datframe
    #     if len(data_frame) == 0 or data_frame == None:
    #         result = {
    #             'SOI'                 : None,
    #             'DATA_FRAME_LENGTH'   : None,
    #             'COMMAND'             : None,
    #             'ERROR_CODE'          : "ERROR. Empty data frame. Source: SerialHandler.py::transaction",
    #             'DATA'                : None,
    #             'CRC'                 : None
    #         }
    #         return result
        
    #     # Protection for invalid flag
    #     if data_frame[0] == FLAG_SOI and data_frame[-1] == FLAG_EOI:
    #         pass
    #     else:
    #         print(f'Wrong dataframe format (INVALID FLAG)')
    #         result = {
    #             'SOI'                 : None,
    #             'DATA_FRAME_LENGTH'   : None,
    #             'COMMAND'             : None,
    #             'ERROR_CODE'          : f"ERROR. Wrong dataframe format (INVALID FLAG). SOI:{hex(data_frame[0])} EOI:{hex(data_frame[-1])}",
    #             'DATA'                : None,
    #             'CRC'                 : None
    #         }
    #         return result

    #     # Start parsing
    #     try:
    #         data_frame_blok_1 = [] # Fetch bytes from SOI until ERROR_CODE
    #         for i in (SOI_BLENGTH, DF_BLENGTH, COMMAND_BLENGTH, ERROR_CODE_BLENGTH):
    #             x = []
    #             for j in range(0,i):
    #                 x .append(data_frame.pop(0))
    #             data_frame_blok_1.append(x)
                
    #         data_frame_blok_2 = [] # Fetch dataframe CRC and EOI
    #         for i in (EOI_BLENGTH, CRC16_BLENGTH):
    #             x = []
    #             for j in range(0,i):
    #                 x.append(data_frame.pop(-1 - ((i-1)-j)))
    #             data_frame_blok_2.append(x)

    #         data_frame_output = data_frame_blok_1
    #         data_frame_output.append(data_frame)
    #         data_frame_output.append(data_frame_blok_2[-1])
    #         data_frame_output.append(data_frame_blok_2[0])

    #         temp = []
    #         temp.extend(data_frame_output[2])
    #         temp.extend(data_frame_output[3])
    #         temp.extend(data_frame)
    #         crc = Util.calc_CRC(temp)
    #         if crc == data_frame_output[5]:
    #             result = {
    #                 'SOI'                 : data_frame_output[0][0],
    #                 'DATA_FRAME_LENGTH'   : Util.leHex2uint(data_frame_output[1],4),
    #                 'COMMAND'             : Util.leHex2uint(data_frame_output[2],2),
    #                 'ERROR_CODE'          : data_frame_output[3][0],
    #                 'DATA'                : data_frame[:],
    #                 'CRC'                 : data_frame_output[5]
    #             }
    #             return result
    #         else:
    #             with open(f'{_CURRENT_PATH}/SerialHandler_error','a+') as f: # Log error

    #                 f.write('Invalid CRC')
    #                 f.write(f'Data field: {data_frame}')
    #                 f.write(f'CRC calculation: {crc}')
    #                 f.write('\n')
    #             result = {
    #                 'SOI'                 : None,
    #                 'DATA_FRAME_LENGTH'   : None,
    #                 'COMMAND'             : None,
    #                 'ERROR_CODE'          : "ERROR. Broken data (CRC not match)",
    #                 'DATA'                : [],
    #                 'CRC'                 : []
    #             }
    #             return result
    #     except:
    #         print('exception')
    #         result = {
    #             'SOI'                 : None,
    #             'DATA_FRAME_LENGTH'   : None,
    #             'COMMAND'             : None,
    #             'ERROR_CODE'          : "Got exception",
    #             'DATA'                : [],
    #             'CRC'                 : []
    #         }
    #         return result