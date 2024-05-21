import socket
import serial
import os
import sys
import json
import pathlib
currdir = pathlib.Path(__file__).parent.absolute()
from datetime import datetime,timedelta

try:
    os.mkdir(f'{currdir}/config')
except:
    pass

try:
    os.mkdir(f'{currdir}/logs')
except:
    pass


class HDLC_PORT:    
    BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
    TCP_IP = '0.0.0.0'
    stop_listening = False

    def __init__(self,port,usbport):
        self.port = port
        self.usbport = usbport

    def __del__(self):
        try:
            del self.ser
            self.f.close()
        except:
            pass

    def serial_ports():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            # ports = glob.glob('/dev/tty[A-Za-z]*')
            import os
            dmesg_info = os.popen('dmesg | grep "MOXA UPort 1400 series converter now attached to"').read()
            usb_list = os.popen('ls /dev/ttyUSB*').read()


            dmesg_info = dmesg_info.split('\n')
            usb_list = usb_list.split('\n')[:-1]
            try:
                usb_list = [i.split('/')[-1] for i in usb_list]
            except:
                print('Linux OS get ports error. Terminated 1')
                exit(1)

            ports = []
            for i in range(0,len(usb_list)):
                for info in dmesg_info:
                    if usb_list[i] in info:
                        ports.append('/dev/%s'%usb_list[i])
                        
        else:
            raise EnvironmentError('Unsupported platform')

        ports = list(set(ports))
        ports.sort()
        result = []
        for port in ports:
            try:
                if sys.platform.startswith('win'):
                    s=serial.Serial()
                elif sys.platform.startswith('linux'):
                    s = serial.Serial(
                        port=port,
                        exclusive=True
                    )
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                print("cant open %s"%port)
                pass       
        return result 

    def initialize_socket(self,tcp_port,usbport):
        if sys.platform.startswith('win'):
            self.ser = serial.Serial(
                port = usbport, 
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                bytesize = serial.EIGHTBITS,
                stopbits = serial.STOPBITS_ONE,
                timeout = 0.1
            )
        elif sys.platform.startswith('linux'):
            self.ser = serial.Serial(
                port = usbport, 
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                bytesize = serial.EIGHTBITS,
                stopbits = serial.STOPBITS_ONE,
                timeout = 1,
                exclusive = True
            )
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.s.settimeout(1)
        self.s.bind((self.TCP_IP, tcp_port))
        self.s.listen(1)

        import os
        if os.path.exists('%s/config/%s.json'%(currdir,self.port)):
            return

        f = open('%s/config/%s.json'%(currdir,self.port),'w')
        f.write(json.dumps({'stop':False}))
        f.close()

    def transaction(self,data_frame,timeout=5):
        self.ser.write(data_frame)
        response = self.readResponse()
        if len(response)>0:
            return response
        return b''
    
    def readResponse(self,timeout=5):
        t1 = datetime.now()
        on_receive = False
        recv_data = b''
        while datetime.now()-t1 < timedelta(seconds=timeout):
            x = self.ser.read()
            if len(x) != 0 and not on_receive:
                on_receive = True
                recv_data += x
                continue
            if on_receive and len(x) != 0:
                recv_data += x
                t1 = datetime.now()
            elif on_receive and len(x) == 0:
                return recv_data
        print('Reach timeout')
        return b''

    def listen(self):
        self.stop_listening = False
        print('Server STARTED')
        while not self.stop_listening:
            try:                
                conn, addr = self.s.accept()
                while not self.stop_listening:
                    data= conn.recv(self.BUFFER_SIZE)
                    if not data: break
                    print('\nRecv: ', data.hex())
                    resp = self.transaction(data)
                    print('Send: ', resp.hex())
                    conn.send(resp)  # echo
                        
                conn.close()
            except socket.timeout:
                f=open('%s/config/%s.json'%(currdir,self.port),'r')
                self.stop_listening = json.load(f)['stop']
                f.close()
        print()

param = sys.argv
print('HDLC service parameter %s'%param)
if len(param) == 5:
    if '--port' in param and '--usbport' in param:
        try:
            port = int(param[param.index('--port')+1])
        except:
            print('port shall be number')
            exit(1)

        usbport = param[param.index('--usbport')+1]
        if usbport not in HDLC_PORT.serial_ports():
            print('usb port not available')
            exit(1)

        o_hdlc = HDLC_PORT(port=port,usbport=usbport)
        o_hdlc.initialize_socket(port,usbport)
        o_hdlc.listen()
    else:
        print('exception')
        exit(1)
else:
    print('Please input argument: --usbport <serial port> --port <port where service is running>')