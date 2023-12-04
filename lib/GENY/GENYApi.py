import json
import math
from paho.mqtt import client as mqtt
from time import sleep
from datetime import datetime, timedelta

from random import randint

class ElementSelector:
    _COMBINE_ALL            = 0x00
    _A_ELEMENT              = 0x01
    _B_ELEMENT              = 0x02
    _C_ELEMENT              = 0x03
    _PHASE_ABC_OUTPUT       = 0x04
    _PHASE_AB_OUTPUT        = 0x05
    _PHASE_A_OUTPUT         = 0x06

class GENYClient:
    MQTT_CONNECTION_ESTABLISHED = False
    MESSAGE_FROM_SERVER = {} # {topic : payload}
    RECV_TIMEOUT = 10

    # TPAC_FEEDBACK = 'NA'
    # HMC_FEEDBACK = 'NA'

    def __init__(self, serverAddress:str='10.23.16.33', serverPort:int=1883) -> None:
        self.mId = randint(0, 99999999)
        self.mqttClientInitial(serverAddress, serverPort)

    # 
    # MQTT initialization and callbacks
    # 
    def mqttClientInitial(self, serverAddress:str, serverPort:int) -> None:
        '''
            Cliet try to connect to GENYServer, program will terminate if fail.
        '''
        try:
            self.client = mqtt.Client() # proram is blocking here
        except:
            print('GENY server unavailable')
            exit(1)
        
        self.client.connect(serverAddress, serverPort)
        self.client.subscribe(f'response/{self.mId}')
        self.client.subscribe(f'ServerStatus')
        self.client.subscribe(f'emergency')
        self.client.on_connect = self.onConnected
        self.client.on_message = self.onDataReceived
        self.client.loop_start()
        
    def onConnected(self, client, userdata, flags, rc):
        if rc == 0:
            self.MQTT_CONNECTION_ESTABLISHED = True
        else:
            print("Need conenction to MQTT broker, return code %d\n", rc)
            exit()

    def onDataReceived(self, client, userdata, message):
        '''
            Expected data is JSON string contain key id, command, and data. If data received is valid, the the request comand will be append to request queue, else response EROR message
        '''
        try:
            payload = str(message.payload.decode('utf-8'))
            payload = json.loads(payload)
        except:
            print(f"error: Payload not json. payload: {str(message.payload.decode('utf-8'))}")
            exit()
        # data broadcast from server
        if message.topic == 'ServerStatus':
            # self.HMC_FEEDBACK = payload['ServerStatus']['FeedbackHMC']
            # self.TPAC_FEEDBACK = payload['ServerStatus']['FeedbackTPAC']
            self.GENY_MODE = payload['ServerStatus']['GenyMode']
            self.isLogedin = payload['ServerStatus']['IsLogedin']
        
        elif message.topic == 'emergency':
            raise Exception('!!!! EMERGENCY: BIIIP BIIIP BIIIP !!!\nPlease check the wiring and try again')

        # proprietary api handler
        elif message.topic == f'response/{self.mId}':
            command = payload['command']
            self.MESSAGE_FROM_SERVER[command] = payload
    ##
    #

    # 
    # Internal class tool 
    #  
    def sendRequest(self,payload:dict) -> str:
        '''
            payload shall contain:
                id          : int
                command     : str
                data        : str(JSON)
        '''
        response = ''
        topic = 'request'
        data = json.dumps(payload)
        self.client.publish(topic,data)
        return response
    
    def getResponse(self,topic:str) -> str:
        '''
            wait response from server
        '''
        t  = datetime.now()
        while datetime.now() - t < timedelta(seconds=self.RECV_TIMEOUT):
            if topic in self.MESSAGE_FROM_SERVER:
                res = self.MESSAGE_FROM_SERVER.pop(topic)
                return res
        raise Exception('Recv data timeout')

    def transaction(self,payload:dict, topic:str) -> str:
        '''
            Request to server and wait the response. This function is blocking.

            Payload is dictionary contain:
                id          : int
                command     : str
                data        : str(JSON)
        '''
        self.sendRequest(payload)
        response = self.getResponse(topic)
        return response
    ##
    #

    #
    # Server status monitor
    #
    def ping(self) -> bool:
        '''
            Ping server status
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'ping',
            'data'      : {
            }
        }
        try:
            result = self.transaction(payload, 'ping')
            if type(result['ErrorCode']) != str:
                return True
            else:
                return False
        except:
            return False
    ##
    #

    #
    # GENY system
    #
    def login(self) -> bool:
        '''
            Enter GENY Serial
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'login',
            'data'      : {
            }
        }
        result = self.transaction(payload, 'login')
        if type(result['ErrorCode']) != str:
            return True
        else:
            return False
        
    def logout(self) -> bool:
        '''
            Out GENY Serial
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'logout',
            'data'      : {
            }
        }
        result = self.transaction(payload, 'logout')
        if type(result['ErrorCode']) != str:
            return True
        else:
            return False
        
    def setSerial(self,usbPort:str,baudRate:int=115200):
        '''
            Set server serial communication to communicate with GENY. if usbPort is None and baudRate None, it means server will close serial port
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'config-usb',
            'data'      : {
                "usbport":usbPort,
                "baudrate":baudRate
            }
        }
        result = self.transaction(payload, 'config-usb')
        if type(result['ErrorCode']) != str:
            return True
        else:
            return False
    
    def set_serial(self,usbPort:str,baudRate:int=115200):
        '''
            Set server serial communication to communicate with GENY. if usbPort is None and baudRate None, it means server will close serial port
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'config-usb',
            'data'      : {
                "usbport":usbPort,
                "baudrate":baudRate
            }
        }
        result = self.transaction(payload, 'config-usb')
        if type(result['ErrorCode']) != str:
            return True
        else:
            return False
        
    def closeSerial(self):
        '''
            Set server serial communication to communicate with GENY. if usbPort is None and baudRate None, it means server will close serial port
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'config-usb',
            'data'      : {
                "usbport":None,
                "baudrate":None
            }
        }
        result = self.transaction(payload, 'config-usb')
        if type(result['ErrorCode']) != str:
            return True
        else:
            return False
        
    #
    # THREE PHASE SOURCE STANDARD 
    #    
    def tpAC_register(self):
        '''
            Get Three Phase Source Standard buffer
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'tpac-register',
            'data'      : {}
        }
        return self.transaction(payload, 'tpac-register')['result']
        
    def tpAC_testCMD(self, 
        Ua:float = None,
        Uphase_a:float = None,
        Ub:float = None,
        Uphase_b:float = None,
        Uc:float = None,
        Uphase_c:float = None,
        Ia:float = None,
        Iphase_a:float = None,
        Ib:float = None,
        Iphase_b:float = None,
        Ic:float = None,
        Iphase_c:float = None,
        Frequency:float = None,
        Frequency2:float = None
    ) -> bool:
        '''
            Configure Three Phase Standard Source buffer. If parameter is set with None, buffer will keep the last state
        '''

        register = {
            'Ua': Ua,
            'UaPhase': Uphase_a,
            'Ub': Ub,
            'UbPhase': Uphase_b,
            'Uc': Uc,
            'UcPhase': Uphase_c, 
            'Ia': Ia,
            'IaPhase': Iphase_a, 
            'Ib': Ib,
            'IbPhase': Iphase_b,
            'Ic': Ic,
            'IcPhase': Iphase_c,
            'Frequency': Frequency,
            'Frequency2' : Frequency2
        }

        temp = register.copy()
        for reg in temp:
            if temp[reg] == None:
                register.pop(reg)
        
        payload = {
            'id'        : self.mId,
            'command'   : 'tpac-config',
            'data'      : register
        }
        result = self.transaction(payload, 'tpac-config')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'tpAC_testCMD:: Got error message: {result}')
            return False

    def tpAC_execute(self) -> bool:
        '''
            Apply buffer configuration to GENY Test Bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'tpac-execute',
            'data'      : {}
        }
        result = self.transaction(payload, 'tpac-execute')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'tpAC_execute:: Got error message: {result}')
            return False
    
    def tpAC_stop(self):
        '''
            Stop Geny from Three Phase Source Standard 
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'tpac-stop',
            'data'      : {}
        }
        result = self.transaction(payload, 'tpac-stop')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'tpAC_stop:: Got error message: {result}')
            return False
    
    def tpAC_readMeasurement(self) -> dict:
        '''
            Read TPAC feedback from test bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'tpac-feedback',
            'data'      : {}
        }
        result = self.transaction(payload, 'tpac-feedback')
        print()
        if type(result['ErrorCode']) != str:
            return result['result']
        else:
            print(f'tpAC_readMeasurement:: Got error message: {result}')
            return 'NA'
    ##
    #

    #
    # HARMONIC STANDARD SOURCE
    #
    def hmc_register(self) -> dict:
        '''
            Get Harmonic Standard Source
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-register',
            'data'      : {}
        }
        return self.transaction(payload, 'hmc-register')['result']
        
    def hmc_configFundamental(self, 
        Ua:float = None,
        Uphase_a:float = None,
        Ub:float = None,
        Uphase_b:float = None,
        Uc:float = None,
        Uphase_c:float = None,
        Ia:float = None,
        Iphase_a:float = None,
        Ib:float = None,
        Iphase_b:float = None,
        Ic:float = None,
        Iphase_c:float = None,
        Frequency:float = None,
        Frequency2:float = None
    ) -> bool:
        '''
            Configure Harmonic Standard Source buffer. If parameter is set with None, buffer will keep the last state
        '''
        register = {
            'Ua': Ua,
            'UaPhase': Uphase_a,
            'Ub': Ub,
            'UbPhase': Uphase_b,
            'Uc': Uc,
            'UcPhase': Uphase_c, 
            'Ia': Ia,
            'IaPhase': Iphase_a, 
            'Ib': Ib,
            'IbPhase': Iphase_b,
            'Ic': Ic,
            'IcPhase': Iphase_c,
            'Frequency': Frequency,
            'Frequency2' : Frequency2
        }

        temp = register.copy()
        for reg in temp:
            if temp[reg] == None:
                register.pop(reg)
        
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-configFundamental',
            'data'      : register
        }
        result = self.transaction(payload, 'hmc-configFundamental')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'hmc_configFundamental:: Got error message: {result}')
            return False
    
    def hmc_configHarmonic(self, channel:int, ordo:int, amplitude:float, phase:float) -> bool:
        '''
            Configure Harmonic Standard Source buffer for harmonic

            parameter description:
                channel     : int   (0x1|0x2|0x4|0x8|0x10|0x20|0x40)
                ordo        : int   (2 to 62)
                amplitude   : float (% of it's fundamental)
                phase       : float (harmonic phase)
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-configHarmonic',
            'data'      : {
                'channel'   : channel,
                'ordo'      : ordo,
                'amplitude' : amplitude,
                'phase'     : phase
            }
        }
        result = self.transaction(payload, 'hmc-configHarmonic')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'hmc_configHarmonic:: Got error message: {result}')
            return False
    
    def hmc_onlineHarmonicAdjust(self, channel:int, ordo:int, amplitude:float, phase:float):
        '''
            Instant apply harmonic on test bench. Please to execute the fundamental parameter first!

            parameter description:
                channel     : int   (0x1|0x2|0x4|0x8|0x10|0x20|0x40)
                ordo        : int   (2 to 62)
                amplitude   : float (% of it's fundamental)
                phase       : float (harmonic phase)
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-onlineAdjust',
            'data'      : {
                'channel'   : channel,
                'ordo'      : ordo,
                'amplitude' : amplitude,
                'phase'     : phase
            }
        }
        result = self.transaction(payload, 'hmc-onlineAdjust')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'hmc_onlineHarmonicAdjust:: Got error message: {result}')
            return False
    
    def hmc_execute(self) -> bool:
        '''
            Apply buffer configuration to GENY Test Bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-execute',
            'data'      : {}
        }
        result = self.transaction(payload, 'hmc-execute')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'hmc_execute:: Got error message: {result}')
            return False
    
    def hmc_stop(self) -> bool:
        '''
            Stop Geny from Harmonic Source Standard 
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-stop',
            'data'      : {}
        }
        result = self.transaction(payload, 'hmc-stop')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'hmc_stop:: Got error message: {result}')
            return False
    
    def hmc_readMeasurement(self) -> dict:
        '''
            Read Harmonic Source Standard feedback from test bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'hmc-feedback',
            'data'      : {}
        }
        result = self.transaction(payload, 'hmc-feedback')
        print()
        if type(result['ErrorCode']) != str:
            return result['result']
        else:
            print(f'hmc_readMeasurement:: Got error message: {result}')
            return 'NA'
    ##
    #

    
    #
    # Energy Error Calibation
    #
    def calib_testCMD(self, 
        selector:ElementSelector = None,
        U:float = None,
        I:float = None,
        pf:float = None,
        frequency:float = None,
        meterConstant:float = None,
        cycle:int = None
    ) -> bool:
        '''
            Configure Calibration Error buffer. If parameter is set with None, buffer will keep the last state.

            Element description:
            + selector is enumerator with value as following:
                _COMBINE_ALL            = 0x00
                _A_ELEMENT              = 0x01
                _B_ELEMENT              = 0x02
                _C_ELEMENT              = 0x03
                _PHASE_ABC_OUTPUT       = 0x04
                _PHASE_AB_OUTPUT        = 0x05
                _PHASE_A_OUTPUT         = 0x06
            + U refer to channel voltage
            + I refer to channel current
            + pf refer to power factor
            + frequency value will apply to all channel
            + meter constant is meter LED output to be read by test bench probe counter
            + cycle shall be unsigned value
        '''
        register = {
            'Selector' : selector,
            'U' : U,
            'I' : I,
            'PF' : pf,
            'frequency' : frequency,
            'MeterConstant' : meterConstant,
            'ReadCycle' : cycle
        }

        temp = register.copy()
        for reg in temp:
            if temp[reg] == None:
                register.pop(reg)
        
        payload = {
            'id'        : self.mId,
            'command'   : 'calib-config',
            'data'      : register
        }
        result = self.transaction(payload, 'calib-config')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'calib_testCMD:: Got error message: {result}')
            return False

    def calib_execute(self) -> bool:
        '''
            Apply buffer configuration to GENY Test Bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'calib-execute',
            'data'      : {}
        }
        result = self.transaction(payload, 'calib-execute')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'calib_execute:: Got error message: {result}')
            return False
    
    def calib_stop(self):
        '''
            Stop Geny from error energy calibration 
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'calib-stop',
            'data'      : {}
        }
        result = self.transaction(payload, 'calib-stop')
        if type(result['ErrorCode']) != str:
            return True
        else:
            print(f'calib_stop:: Got error message: {result}')
            return False

    def calib_register(self):
        '''
            Get Meter Calibration Error buffer
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'calib-register',
            'data'      : {}
        }
        return self.transaction(payload, 'calib-register')['result']
    
    def calib_readMeasurement(self) -> dict:
        '''
            Read calibration feedback from test bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'calib-feedback',
            'data'      : {}
        }
        result = self.transaction(payload, 'calib-feedback')
        print()
        if type(result['ErrorCode']) != str:
            return result['result']
        else:
            print(f'calib:: Got error message: {result}')
            return 'NA'
        
        
    def calib_readErrorCalib(self) -> dict:
        '''
            Read error calibration feedback from test bench
        '''
        payload = {
            'id'        : self.mId,
            'command'   : 'calib-error',
            'data'      : {}
        }
        result = self.transaction(payload, 'calib-error')
        if type(result['ErrorCode']) != str:
            return result['result']
        else:
            print(f'calib:: Got error message: {result}')
            return 'NA'
    ##
    # 