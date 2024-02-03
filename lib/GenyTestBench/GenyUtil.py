import struct

class VoltageRangeError(Exception):
    pass

class CurrentRangeError(Exception):
    pass

class DatFrameError(Exception):
    pass

class CommmandDataFrame:
    SOI_BIT_LENGTH = 1
    DATA_FRAME_BIT_LENGTH = 4
    COMMAND_BIT_LENGTH = 2
    CRC16_BIT_LENGTH = 2
    EOI_BIT_LENGTH = 1
    
    SOI_CONSTANT = 0x7e
    EOI_CONSTANT = 0xff
    
    def __init__(self):
        # variable that store 
        self.SOI = []
        self.LEN = []
        self.COMMAND = []
        self.DATA = []
        self.CRC16 = []
        self.EOI = []
        
        self.errorMessage = ''
        
    def reinit(self):
        self.SOI = []
        self.LEN = []
        self.COMMAND = []
        self.DATA = []
        self.CRC16 = []
        self.EOI = []
    
    def toDict(self) -> dict:
        '''
            Get dictionary contained data frame information
        '''
        return {
            'SOI' : self.SOI,
            'LEN' : self.LEN,
            'COMMAND' : self.COMMAND,
            'DATA' : self.DATA,
            'CRC16' : self.CRC16,
            'EOI' : self.EOI
        }
    
    def extractDataFrame(self, dataFrame:bytearray):
        '''
            Extract information inside Command data frame
        '''
        dFrame = list(dataFrame)
        if len(dFrame) == 0 or dFrame == None: # Protection for empty datframe
            raise Exception(f'Data frame is empty')
        
        # Protection for invalid flag
        if dFrame[0] == CommmandDataFrame.SOI_CONSTANT and dFrame[-1] == CommmandDataFrame.EOI_CONSTANT:
            pass
        else:
            raise Exception(f'Wrong dataframe format (INVALID FLAG)')

        _SOI = [dFrame.pop(0)]
        _LEN = [dFrame.pop(0) for i in range(CommmandDataFrame.DATA_FRAME_BIT_LENGTH)]
        commandDataLen = Util.Hex2uint(_LEN, self.DATA_FRAME_BIT_LENGTH)
        if commandDataLen + CommmandDataFrame.CRC16_BIT_LENGTH + CommmandDataFrame.EOI_BIT_LENGTH == len(dFrame):
            pass
        else:
            raise Exception(f'Invalid dataframe')
        _COMMAND = [dFrame.pop(0) for i in range(CommmandDataFrame.COMMAND_BIT_LENGTH)]
        _DATA = [dFrame.pop(0) for i in range(commandDataLen - CommmandDataFrame.COMMAND_BIT_LENGTH)]
        _CRC16 = [dFrame.pop(0) for i in range(CommmandDataFrame.CRC16_BIT_LENGTH)]
        _EOI = [dFrame.pop(0)]   
        
        self.SOI = _SOI
        self.LEN = _LEN
        self.COMMAND = _COMMAND
        self.DATA = _DATA
        self.CRC16 = _CRC16
        self.EOI = _EOI
        
    def genDataFrame(self, command:int, data:list)->list:
        '''
            generate geny command dataframe (refer to AT-PRO-YC99T documentation)
        '''
        temp = []
        # create COMMAND + DATA field
        temp.append(command)
        temp.append(0x00)
        temp.extend(data)

        # create crc field
        crc_ = Util.calc_CRC(temp[:])

        # create length field
        data_length = Util.uint2byteList(len(temp))

        # join fields
        output = [CommmandDataFrame.SOI_CONSTANT]
        output.extend(data_length)
        output.extend(temp)   
        output.extend(crc_)     
        output.append(CommmandDataFrame.EOI_CONSTANT)
        
        self.extractDataFrame(output)
        return output.copy()

class ResponseDataFrame:
    SOI_BIT_LENGTH = 1
    DATA_FRAME_BIT_LENGTH = 4
    COMMAND_BIT_LENGTH = 2
    ERROR_CODE_BIT_LENGTH = 1
    CRC16_BIT_LENGTH = 2
    EOI_BIT_LENGTH = 1
    
    SOI_CONSTANT = 0x7e
    EOI_CONSTANT = 0xff
      
    def __init__(self):
        # variable that store 
        self.SOI = []
        self.LEN = []
        self.COMMAND = []
        self.ERRORCODE = []
        self.DATA = []
        self.CRC16 = []
        self.EOI = []
        
        self.errorMessage = ''
    
    def getErrorCode(self):
        return self.ERRORCODE[0]
    
    def extractDataFrame(self, dataFrame:bytearray):
        '''
            Extract information inside Response data frame
        '''
        dFrame = list(dataFrame)
        if len(dFrame) == 0 or dFrame == None: # Protection for empty datframe
            raise Exception(f'Data frame is empty')

        # Protection for invalid flag
        if dFrame[0] == ResponseDataFrame.SOI_CONSTANT and dFrame[-1] == ResponseDataFrame.EOI_CONSTANT:
            pass
        else:
            raise Exception(f'Wrong dataframe format (INVALID FLAG)')
        
        _SOI = [dFrame.pop(0) for i in range(ResponseDataFrame.SOI_BIT_LENGTH)]
        _LEN = [dFrame.pop(0) for i in range(ResponseDataFrame.DATA_FRAME_BIT_LENGTH)]
        responseLength = Util.Hex2uint(_LEN, ResponseDataFrame.DATA_FRAME_BIT_LENGTH)
        if responseLength + ResponseDataFrame.CRC16_BIT_LENGTH + ResponseDataFrame.EOI_BIT_LENGTH == len(dFrame):
            pass
        else:
            raise Exception(f'Invalid dataframe')
        _COMMAND = [dFrame.pop(0) for i in range(ResponseDataFrame.COMMAND_BIT_LENGTH)]
        _ERRORCODE = [dFrame.pop(0) for i in range(ResponseDataFrame.ERROR_CODE_BIT_LENGTH)]
        _DATA = [dFrame.pop(0) for i in range(responseLength - ResponseDataFrame.COMMAND_BIT_LENGTH - ResponseDataFrame.ERROR_CODE_BIT_LENGTH)]
        _CRC16 = [dFrame.pop(0) for i in range(ResponseDataFrame.CRC16_BIT_LENGTH)]
        _EOI = [dFrame.pop(0) for i in range(ResponseDataFrame.EOI_BIT_LENGTH)]
        
        self.SOI = _SOI
        self.LEN = _LEN
        self.COMMAND = _COMMAND
        self.ERRORCODE = _ERRORCODE
        self.DATA = _DATA
        self.CRC16 = _CRC16
        self.EOI = _EOI

    def toDict(self) -> dict:
        '''
            Get dictionary contained data frame information
        '''
        return {
            'SOI' : self.SOI,
            'LEN' : self.LEN,
            'COMMAND' : self.COMMAND,
            "ERRORCODE": self.ERRORCODE,
            'DATA' : self.DATA,
            'CRC16' : self.CRC16,
            'EOI' : self.EOI
        }
class Selector:
    def __init__(self, enum, description):
        self.enum = enum
        self.description = description

class ElementSelector:
    class EnergyErrorCalibration(Selector):
        _COMBINE_ALL            = Selector(0x00, '')
        _A_ELEMENT              = Selector(0x01, '')
        _B_ELEMENT              = Selector(0x02, '')
        _C_ELEMENT              = Selector(0x03, '')
        _PHASE_ABC_OUTPUT       = Selector(0x04, '')
        _PHASE_AB_OUTPUT        = Selector(0x05, '')
        _PHASE_A_OUTPUT         = Selector(0x06, '')
    
    class ThreePhaseAcStandard(Selector):
        _COMBINE_ALL            = Selector(0x00, '')
        _A_ELEMENT              = Selector(0x01, '')
        _B_ELEMENT              = Selector(0x02, '')
        _C_ELEMENT              = Selector(0x03, '')
        
class PowerSelector(Selector):
    _3P4W_ACTIVE            = Selector(0x00, '')
    _3P3W_ACTIVE            = Selector(0x01, '')
    _SINGLE_PHASE_ACTIVE    = Selector(0x02, '')
    _3P4W_REAL_REACTIVE     = Selector(0x03, '')
    _3P3W_REAL_REACTIVE     = Selector(0x04, '')
    _2_ELEMENTS_60_REACTIVE = Selector(0x05, '')
    _2_ELEMENTS_90_REACTIVE = Selector(0x06, '')
    _3_ELEMENTS_90_REACTIVE = Selector(0x07, '')
        
class RangeLevel:
    def __init__(self, enum, nominal):
        self.enum = enum
        self.nominal = nominal

class VoltageRange:
    class YC99T_5C(RangeLevel):
        _100V = RangeLevel(6, 100.0)
        _220V = RangeLevel(7, 220.0)
        _380V = RangeLevel(8, 380.0)    
    class YC99T_3C:
        _100V = RangeLevel(6, 100.0)
        _220V = RangeLevel(7, 220.0)
        _380V = RangeLevel(8, 380.0)
        _660V = RangeLevel(9, 660.0)

class CurrentRange:
    class YC99T_5C:
        _50mA = RangeLevel(7, 0.050)
        _200mA = RangeLevel(8, 0.200)
        _1A = RangeLevel(9, 1.9)
        _5A = RangeLevel(10, 5.9)
        _20A = RangeLevel(11, 20.9)
        _100A = RangeLevel(12, 100.9)
    
    class YC99T_3C:
        _50mA = 7
        _200mA = 8
        _1A = 9
        _5A = 10
        _16_667A = 11
        _100A = 12
        
        _NOM_50mA = 0.050
        _NOM_200mA = 0.200
        _NOM_1A = 1
        _NOM_5A = 5
        _NOM_16_667A = 16.667
        _NOM_100A = 100

class Util:         
    ct_ArrayCRCHi = [
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
        0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
        0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
        0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
        0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
        0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
        0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
        0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40]

    ct_ArrayCRCLo = [
        0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06,
        0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD,
        0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
        0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A,
        0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4,
        0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
        0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3,
        0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4,
        0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
        0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29,
        0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED,
        0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
        0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60,
        0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67,
        0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
        0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68,
        0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E,
        0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
        0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71,
        0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92,
        0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
        0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B,
        0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B,
        0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
        0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42,
        0x43, 0x83, 0x41, 0x81, 0x80, 0x40]

    # CRC Calculation
    def calc_CRC(data_frame) -> list:
        '''
            dataframe shall be list of data in decimal. This function returns [Low Byte CRC, High Byte CRC]
        '''
        l_CRCHi = 0xFF 
        l_CRCLo = 0xFF 
        l_Index = 0
        for i in data_frame:
            l_Index = l_CRCHi ^ i
            l_CRCHi = l_CRCLo ^ Util.ct_ArrayCRCHi[l_Index]
            l_CRCLo = Util.ct_ArrayCRCLo[l_Index]
        return [l_CRCLo, l_CRCHi]

    # CASTING
    def float2byte(value:float, bytesize:int=4, littleEndia:bool=True)->list:
        '''
            Convert unsigned integer to list of hex. the length of list is depend on bytesize input (supported bytesize: 4,8)
        '''
        m_macro_size = None
        if bytesize==4:
            m_macro_size='I'
        elif bytesize==8:
            m_macro_size='Q'
        x = None
        if littleEndia: 
            x = '%08x'%struct.unpack('>%s'%m_macro_size, struct.pack('<f', value))[0]
        else:
            x = '%08x'%struct.unpack('<%s'%m_macro_size, struct.pack('<f', value))[0]
        temp = []
        for i in range(0,len(x),2):
            temp.append(int(x[i:i+2],16))
        return temp

    def uint2byteList(value:int, bytesize:int=4, litteEndia:bool=True)->list:
        '''
            Convert unsigned integer to list of hex. the length of list is depend on bytesize input (supported bytesize: 2,4)
        '''
        m_macro_size = None
        if bytesize == 2:
            m_macro_size = 'H'
        elif bytesize == 4:
            m_macro_size = 'I'
        x = None
        if litteEndia:
            x = list(struct.pack('<%s'%m_macro_size,value))
        return x.copy()

    def Hex2uint(value:int, size:int=4, litteEndia=True) -> int:
        '''
            Convert little endia hex list to unsigned integer
        '''
        if litteEndia:
            if size == 4:
                return struct.unpack('<I',bytearray(value))[0]
            elif size == 2:
                return struct.unpack('<H',bytearray(value))[0]
        else:
            #TODO: Convert for big endia
            pass
        
    def Hex2float(value:int, size:int=4, littleEndia=True):
        '''
            Transform hexa value to float
        '''
        if littleEndia:
            if size == 4:
                return struct.unpack('<f',bytearray(value))[0]
            elif size == 8:
                return struct.unpack('<d',bytearray(value))[0]
            elif size == 2:
                return struct.unpack('<e',bytearray(value))[0]
        else:
            #TODO: Convert for big endia
            pass
          
if __name__ == '__main__':
    
    def test_1():
        # Command data frame
        inputData = b'~A\x00\x00\x00\xa0\x00?\x06\x00\x00\xc8B\x00\x00\x00\x00\x06\x00\x00\xc8B\x00\x00pC\x06\x00\x00\xc8B\x00\x00\xf0B\n\x00\x00\xa0@\x00\x00\x00\x00\n\x00\x00\xa0@\x00\x00pC\n\x00\x00\xa0@\x00\x00\xf0B\x00\x00HB\x00\x00pB<I\xff'
        dataFrame = CommmandDataFrame()
        dataFrame.extractDataFrame(inputData)
        print(dataFrame.SOI)
        print(dataFrame.LEN)
        print(dataFrame.COMMAND)
        print(dataFrame.DATA)
        print(dataFrame.CRC16)
        print(dataFrame.EOI)
    
    def test_2():
        # Response data frame
        responseData = b'~S\x00\x00\x00\xb2\x00\x00}\xff[C\x00\x00\x00\x00\xe0\xff\x9f@\x00\x00\x00\x00\x93\x7f\x89DR\xfbN\xbdl\x00\\C\x00\x00pC\xd6\x00\xa0@\x8f\x02pC\xff\x80\x89Dd5\xf1\xbd\xd2\xff[C\x00\x00\xf0B`\x00\xa0@\x1f\x05\xf0B6\x80\x89D\xa18\xc9\xbdd@NE\xebz\x88\xbe\xf5\x1c\xff'
        dataFrame = ResponseDataFrame()
        dataFrame.extractDataFrame(responseData)
        print(dataFrame.SOI)
        print(dataFrame.LEN)
        print(dataFrame.COMMAND)
        print(dataFrame.ERRORCODE)
        print(dataFrame.DATA)
        print(dataFrame.CRC16)
        print(dataFrame.EOI)