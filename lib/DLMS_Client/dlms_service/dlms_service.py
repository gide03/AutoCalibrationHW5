import struct

####################################################################
# CLASS DEFINITION
####################################################################

class cosemAccessResult:
	success = 0
	hardware_fault = 1
	temporary_failure = 2
	read_write_denied = 3
	object_undefined = 4
	object_class_inconsistent = 9
	object_unavailable = 11
	type_unmatched = 12
	scope_of_access_violated = 13
	data_block_unaivailable = 14
	long_get_aborted = 15
	other_reason = 250

class AARQTag:
	AARQ = 0x60
	ProtocolVer = 0x80
	AppContext = 0xA1
	ChoiceACN = 0x06
	SysTitle = 0xA6
	TypeST = 0x04
	ACSEReq = 0x8A
	Mechanism = 0x8B
	AuthVal = 0xAC		
	ChoiceAuthVal = 0x80
	UserInfo = 0xBE
	ChoiceUserInfo = 0x04
	ImplementationInfo = 0xBD

class AARETag:
	AARE = 0x61
	AppContext = 0xA1
	ACNLength = 0x09
	ChoiceACN = 0x06
	ChoiceACNLength = 0x07
	ResultAsso = 0xA2
	ResultAssoLength = 0x03
	ChoiceResultAsso = 0x02
	ChoiceResultAssoLength = 0x01
	Diagnostic = 0xA3
	DiagnosticLength = 0x05
	DiagnosticACSEUser = 0xA1
	DiagnosticACSEProvider = 0xA2
	DiagnosticACSELength = 0x03
	ResultDiagACSE = 0x02
	ResultDiagACSELength = 0x01
	SysTitle = 0xA4
	TypeST = 0x04
	ACSEReqField = [0x88, 0x02, 0x07, 0x80]
	MechanismField = [0x89, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02]
	RespondToAuthTag = 0xAA
	RespondValTag = 0x80
	UserInfo = 0xBE
	ChoiceUserInfo = 0x04
	SuccessUserInfoVal = [0x08, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x10, 0x1C, 0x02, 0x00, 0x00, 0x07]
	Fail1UserInfoVal = [0x08, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x10, 0x1E, 0x00, 0x00, 0x00, 0x07]
	Fail2UserInfoVal = [0x0E, 0x01, 0x06, 0x01]

class assoSourceDiag:
	SERVICE_USER = 1
	SERVICE_PROVIDER = 2

class userDiag:
	SUCCESS = 0
	NO_REASON_GIVEN = 1
	APPLICATION_CONTEX_NAME_NOT_SUPPORTED = 2
	CALLING_AP_TITLE_NOT_RECOGNIZED = 3
	CALLING_AP_QUALIFIER_NOT_RECOGNIZED = 4
	CALLING_AE_QUALIFIER_NOT_RECOGNIZED = 5
	CALLING_AE_INVOCATION_IDENTIFIER_NOT_RECOGNIZED = 6
	AUTHENTICATION_MECHANISM_NAME_NOT_RECOGNISED = 11
	AUTHENTICATION_MECHANISM_NAME_REQUIRED = 12
	AUTHENTICATION_FAILURE = 13
	AUTHENTICATION_REQUIRED = 14
	RAISE_EXCEPTION = 255

class providerDiag:
    SUCCESS = 0
    NO_REASON_GIVEN = 1
    NO_COMMON_ACSE_VERSION = 2

class mechanism:
	LOWEST_LEVEL = 0
	LOW_LEVEL = 1
	HIGH_LEVEL = 2
	HIGH_LEVEL_GMAC = 5
	HIGH_LEVEL_ECDSA = 7

class assoResult:
	ACCEPTED = 0
	REJECTED_PERMANENT = 1
	REJECTED_TRANSIENT = 2

class chipered_tag:
	GLO_INIT_REQUEST = 33
	GLO_INIT_RESPONSE = 40

class ServiceTag:
    AARQ = 0x60
    RLRQ = 0x62
    # No chipering
    GET_REQUEST = 0xC0
    GET_REQUEST_NORMAL = 0x01
    GET_REQUEST_NEXT = 0x02

    GET_RESPONSE = 0xC4
    GET_RESPONSE_NORMAL = 0x01
    GET_RESPONSE_DATABLOCK = 0x02

    SET_REQUEST = 0xC1
    SET_REQUEST_NORMAL = 0x01
    SET_REQUEST_FIRST_DATABLOCK = 0x02
    SET_REQUEST_DATABLOCK = 0x03

    SET_RESPONSE = 0xC5
    SET_RESPONSE_NORMAL = 0x01
    SET_RESPONSE_DATABLOCK = 0x02
    SET_RESPONSE_LAST_DATABLOCK = 0x03

    ACT_REQUEST = 0xC3
    ACT_REQUEST_NORMAL = 0x01
    ACT_REQUEST_NEXT_PBLOCK = 0x02
    ACT_REQUEST_FIRST_PBLOCK = 0x04
    ACT_REQUEST_PBLOCK = 0x06

    ACT_RESPONSE = 0xC7
    ACT_RESPONSE_NORMAL = 0x01
    ACT_RESPONSE_PBLOCK = 0x02
    ACT_RESPONSE_NEXT_PBLOCK = 0x04
    
    NORMAL_TAG = 0x01
    NEXT_TAG = 0x02
    WITH_DATABLOCK = 0x02

    # Glo-Chipering
    GLO_GET_REQUEST = 0xC8
    GLO_SET_REQUEST = 0xC9
    GLO_ACT_REQUEST = 0xCB

    GLO_GET_RESPONSE = 0xCC
    GLO_SET_RESPONSE = 0xCD
    GLO_ACT_RESPONSE = 0xCF

    SET_RESP_LAST_DATABLOCK = 0x03

    INVOKE_ID_MASK = 0x40

    # General-APDU
    GENERAL_SIGNING = 0xDF

    # Exception
    EXCEPTION_RESPONSE = 0xD8
    EXCEPT_STATE_ERROR = 0x00
    EXCEPT_SERVICE_ERROR = 0x01

    EXCEPT_STATE_SERVICE_NOT_ALLOWED = 0x01
    EXCEPT_STATE_SERVICE_UNKNOWN = 0x02

    EXCEPT_SERVICE_OPERATION_NOT_POSSIBLE = 0x01
    EXCEPT_SERVICE_SERVICE_NOT_SUPPORTED = 0x02
    EXCEPT_SERVICE_OTHER_REASON = 0x03
    EXCEPT_SERVICE_PDU_TOO_LONG = 0x04
    EXCEPT_SERVICE_DECHIPERING_ERROR = 0x05
    EXCEPT_SERVICE_INVOC_COUNTER_ERROR = 0x06

class CosemState:
    e_CLOSE = 0
    e_OPEN = 1
    e_RELEASE = 2
    e_ABORT = 3
    e_PENDING = 4

class DataAccessResult:
    e_SUCCESS = 0
    e_HARDWARE_FAULT = 1
    e_TEMPORARY_FAILURE = 2
    e_READ_WRITE_DENIED = 3
    e_OBJECT_UNDEFINED = 4
    e_OBJECT_CLASS_INCONSISTENT = 9
    e_OBJECT_UNAVAILABLE = 11
    e_TYPE_UNMATCHED = 12
    e_SCOPE_OF_ACCESS_VIOLATED = 13
    e_DATA_BLOCK_UNAVAILABLE = 14
    e_LONG_GET_ABORTED = 15
    e_NO_LONG_GET_IN_PROGRESS = 16
    e_LONG_SET_ABORTED = 17
    e_NO_LONG_SET_IN_PROGRESS = 18
    e_DATA_BLOCK_NUMBER_INVALID = 19
    e_OTHER_REASON = 255

class ActionResult:
	e_SUCCESS = 0
	e_HARDWARE_FAULT = 1
	e_TEMPORARY_FAILURE = 2
	e_READ_WRITE_DENIED = 3
	e_OBJECT_UNDEFINED = 4
	e_OBJECT_CLASS_INCONSISTENT = 9
	e_OBJECT_UNAVAILABLE = 11
	e_TYPE_UNMATCHED = 12
	e_SCOPE_OF_ACCESS_VIOLATED = 13
	e_DATA_BLOCK_UNAVAILABLE = 14
	e_LONG_ACTION_ABORTED = 15
	e_NO_LONG_ACTION_IN_PROGRESS = 16
	e_OTHER_REASON = 250

class ServiceResponse:
	OK = 0
	NOT_OK = 1
	EXCEPTION = 2
	ASSO_EXCEPTION = 255

class CosemDataType:
	e_NULL_DATA = 0
	e_ARRAY = 1
	e_STRUCTURE = 2
	e_BOOLEAN = 3
	e_BIT_STRING = 4
	e_DOUBLE_LONG = 5
	e_DOUBLE_LONG_UNSIGNED = 6
	e_OCTET_STRING = 9
	e_VISIBLE_STRING = 10
	e_UTF8_STRING = 12
	e_BCD = 13
	e_INTEGER = 15
	e_LONG = 16
	e_UNSIGNED = 17
	e_LONG_UNSIGNED = 18
	e_LONG64 = 20
	e_LONG64_UNSIGNED = 21
	e_ENUM = 22
	e_FLOAT32 = 23
	e_FLOAT64 = 24
	e_DATE_TIME = 25

def convert_dtype_to_num(dtype):
	return {
        'Itron.XMX.WCF.Data.XMS.BooleanDTO' : CosemDataType.e_BOOLEAN,
        'Itron.XMX.WCF.Data.XMS.Unsigned8DTO' : CosemDataType.e_UNSIGNED,
        'Itron.XMX.WCF.Data.XMS.Unsigned16DTO' : CosemDataType.e_LONG_UNSIGNED,
        'Itron.XMX.WCF.Data.XMS.Unsigned32DTO' : CosemDataType.e_DOUBLE_LONG_UNSIGNED,
        'Itron.XMX.WCF.Data.XMS.Unsigned64DTO' : CosemDataType.e_LONG64_UNSIGNED,
        'Itron.XMX.WCF.Data.XMS.Integer8DTO' : CosemDataType.e_INTEGER,
        'Itron.XMX.WCF.Data.XMS.Integer16DTO' : CosemDataType.e_LONG,
        'Itron.XMX.WCF.Data.XMS.Integer32DTO' : CosemDataType.e_DOUBLE_LONG,
        'Itron.XMX.WCF.Data.XMS.Integer64DTO' : CosemDataType.e_LONG64,
        'Itron.XMX.WCF.Data.XMS.EnumeratedDTO' : CosemDataType.e_ENUM,
        'Itron.XMX.WCF.Data.XMS.SequenceDTO' : CosemDataType.e_STRUCTURE,
        'Itron.XMX.WCF.Data.XMS.SequenceOfDTO' : CosemDataType.e_ARRAY,
        'Itron.XMX.WCF.Data.XMS.OctetStringDTO' : CosemDataType.e_OCTET_STRING,
        'Itron.XMX.WCF.Data.XMS.VisibleStringDTO' : CosemDataType.e_VISIBLE_STRING,
        'Itron.XMX.WCF.Data.XMS.BitStringDTO' : CosemDataType.e_BIT_STRING,
        'Itron.XMX.WCF.Data.XMS.UtcDTO' : CosemDataType.e_DATE_TIME,
		'Itron.XMX.WCF.Data.XMS.ChoiceDTO' : CosemDataType.e_ARRAY,
        '' : CosemDataType.e_NULL_DATA
    }[dtype]

def convert_dtype_to_string(dtype):
	return {
        CosemDataType.e_BOOLEAN : 'bool',
        CosemDataType.e_UNSIGNED : 'unsigned',
        CosemDataType.e_LONG_UNSIGNED : 'long_unsigned',
        CosemDataType.e_DOUBLE_LONG_UNSIGNED : 'double_long_unsigned',
        CosemDataType.e_LONG64_UNSIGNED : 'long64_unsigned',
        CosemDataType.e_INTEGER : 'integer',
        CosemDataType.e_LONG : 'long',
        CosemDataType.e_DOUBLE_LONG : 'double_long',
        CosemDataType.e_LONG64 : 'long64',
        CosemDataType.e_ENUM : 'enum',
        CosemDataType.e_STRUCTURE : 'struct',
        CosemDataType.e_ARRAY : 'array',
        CosemDataType.e_OCTET_STRING : 'octet_string',
        CosemDataType.e_VISIBLE_STRING : 'visible_string',
        CosemDataType.e_BIT_STRING : 'bit_string',
		CosemDataType.e_FLOAT32	: 'float32',
		CosemDataType.e_FLOAT64	: 'float64',
        CosemDataType.e_DATE_TIME : 'date_time'
    }[dtype]	

#Developing purpose
def convert_data_result_to_string(dres):
	return {
		DataAccessResult.e_SUCCESS : 'Success',
		DataAccessResult.e_HARDWARE_FAULT : 'Hardware Fault',
		DataAccessResult.e_TEMPORARY_FAILURE : 'Temp Fault',
		DataAccessResult.e_READ_WRITE_DENIED : 'Read Write Denied',
		DataAccessResult.e_OBJECT_UNDEFINED : 'Object Undefined',
		DataAccessResult.e_OBJECT_CLASS_INCONSISTENT : 'Object Class Inconsistent',
		DataAccessResult.e_OBJECT_UNAVAILABLE : 'Object Unavailable',
		DataAccessResult.e_TYPE_UNMATCHED : 'Type Unmatched',
		DataAccessResult.e_SCOPE_OF_ACCESS_VIOLATED : 'Scope of Access Violated',
		DataAccessResult.e_DATA_BLOCK_UNAVAILABLE : 'Data Block Unavailable',
		DataAccessResult.e_LONG_GET_ABORTED : 'Long Get Aborted',
		DataAccessResult.e_OTHER_REASON : 'Other Reason'
    }[dres]

def serialize_data(dataType, data):
	buff = []
	if dataType == CosemDataType.e_NULL_DATA:
		buff.append(CosemDataType.e_NULL_DATA)
	if dataType == CosemDataType.e_BOOLEAN:
		buff.append(CosemDataType.e_BOOLEAN)
		buff.append(data)
	elif dataType == CosemDataType.e_UNSIGNED:
		buff.append(CosemDataType.e_UNSIGNED)
		buff.append(data)
	elif dataType == CosemDataType.e_LONG_UNSIGNED:
		buff.append(CosemDataType.e_LONG_UNSIGNED)
		buff.append(data >> 8 & 0xFF)
		buff.append(data & 0xFF)
	elif dataType == CosemDataType.e_DOUBLE_LONG_UNSIGNED:
		buff.append(CosemDataType.e_DOUBLE_LONG_UNSIGNED)
		buff.append(data >> 24 & 0xFF)
		buff.append(data >> 16 & 0xFF)
		buff.append(data >> 8 & 0xFF)
		buff.append(data & 0xFF)
	elif dataType == CosemDataType.e_LONG64_UNSIGNED:
		buff.append(CosemDataType.e_LONG64_UNSIGNED)
		buff.append(data >> 56 & 0xFF)
		buff.append(data >> 48 & 0xFF)
		buff.append(data >> 40 & 0xFF)
		buff.append(data >> 32 & 0xFF)
		buff.append(data >> 24 & 0xFF)
		buff.append(data >> 16 & 0xFF)
		buff.append(data >> 8 & 0xFF)
		buff.append(data & 0xFF)
	elif dataType == CosemDataType.e_INTEGER:
		buff.append(CosemDataType.e_INTEGER)
		bits = 8
		data = (data + (1 << bits)) % (1 << bits)
		buff.append(data)
	elif dataType == CosemDataType.e_LONG:
		buff.append(CosemDataType.e_LONG)
		bits = 16
		data = (data + (1 << bits)) % (1 << bits)
		buff.append(data >> 8 & 0xFF)
		buff.append(data & 0xFF)
	elif dataType == CosemDataType.e_DOUBLE_LONG:
		buff.append(CosemDataType.e_DOUBLE_LONG)
		bits = 32
		data = (data + (1 << bits)) % (1 << bits)
		buff.append(data >> 24 & 0xFF)
		buff.append(data >> 16 & 0xFF)
		buff.append(data >> 8 & 0xFF)
		buff.append(data & 0xFF)
	elif dataType == CosemDataType.e_LONG64:
		buff.append(CosemDataType.e_LONG64)
		bits = 64
		data = (data + (1 << bits)) % (1 << bits)
		buff.append(data >> 56 & 0xFF)
		buff.append(data >> 48 & 0xFF)
		buff.append(data >> 40 & 0xFF)
		buff.append(data >> 32 & 0xFF)
		buff.append(data >> 24 & 0xFF)
		buff.append(data >> 16 & 0xFF)
		buff.append(data >> 8 & 0xFF)
		buff.append(data & 0xFF)
	elif dataType == CosemDataType.e_ENUM:
		buff.append(CosemDataType.e_ENUM)
		buff.append(data)
	elif dataType == CosemDataType.e_DATE_TIME:
		buff.append(CosemDataType.e_OCTET_STRING)
		buff.append(len(data))
		buff = buff + data
	elif dataType == CosemDataType.e_OCTET_STRING:
		buff.append(CosemDataType.e_OCTET_STRING)
		length_data = len(data)
		if length_data >= 128:
			if length_data <= 0xFF:
				buff.append(0x81)
				buff.append(length_data)
			elif length_data > 0xFF and length_data <= 0xFFFF:
				buff.append(0x82)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
			elif length_data > 0xFFFF and length_data <= 0xFFFFFF:
				buff.append(0x83)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)				
			elif length_data > 0xFFFFFF and length_data <= 0xFFFFFFFF:
				buff.append(0x84)
				buff.append(length_data >> 24 & 0xFF)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
		else:
			buff.append(length_data)
		buff = buff + data
	elif dataType == CosemDataType.e_VISIBLE_STRING:
		buff.append(CosemDataType.e_VISIBLE_STRING)
		length_data = len(data)
		if length_data >= 128:
			if length_data <= 0xFF:
				buff.append(0x81)
				buff.append(length_data)
			elif length_data > 0xFF and length_data <= 0xFFFF:
				buff.append(0x82)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
			elif length_data > 0xFFFF and length_data <= 0xFFFFFF:
				buff.append(0x83)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)				
			elif length_data > 0xFFFFFF and length_data <= 0xFFFFFFFF:
				buff.append(0x84)
				buff.append(length_data >> 24 & 0xFF)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
		else:
			buff.append(length_data)
		buff = buff + data
	elif dataType == CosemDataType.e_BIT_STRING:
		buff.append(CosemDataType.e_BIT_STRING)
		if type(data) == int:
			default_bit_length = 8
			if data > 0xFF and data <= 0xFFFF:
				default_bit_length = 16
			elif data > 0xFFFF and data <= 0xFFFFFFFF:
				default_bit_length = 32
			elif data > 0xFFFFFFFF and data <= 0xFFFFFFFFFFFFFFFF:
				default_bit_length = 64
			data = [default_bit_length, data]
		length_data = data[0]
		if length_data >= 128:
			if length_data <= 0xFF:
				buff.append(0x81)
				buff.append(length_data)
			elif length_data > 0xFF and length_data <= 0xFFFF:
				buff.append(0x82)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
			elif length_data > 0xFFFF and length_data <= 0xFFFFFF:
				buff.append(0x83)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)				
			elif length_data > 0xFFFFFF and length_data <= 0xFFFFFFFF:
				buff.append(0x84)
				buff.append(length_data >> 24 & 0xFF)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
		else:
			buff.append(length_data)
		serialize_seg = int((length_data+8-1)/8)
		bitstring_val = []
		for i in range(serialize_seg):
			bitstring_val.append(data[1] >> (8*((serialize_seg-1)-i)) & 0xFF)
		buff = buff + bitstring_val[::-1]
	elif dataType == CosemDataType.e_FLOAT32:
		buff.append(CosemDataType.e_FLOAT32)
		if type(data) == type([]):
			buff += data
		elif type(data) == type(0.0):
			conv_val = int(struct.pack(">f", data).hex(), 16)
			buff.append(conv_val >> 24 & 0xFF)
			buff.append(conv_val >> 16 & 0xFF)
			buff.append(conv_val >> 8 & 0xFF)
			buff.append(conv_val & 0xFF)
	elif dataType == CosemDataType.e_FLOAT64:
		buff.append(CosemDataType.e_FLOAT64)
		if type(data) == type([]):
			buff += data
		elif type(data) == type(0.0):
			conv_val = int(struct.pack(">d", data).hex(), 16)
			buff.append(conv_val >> 56 & 0xFF)
			buff.append(conv_val >> 48 & 0xFF)
			buff.append(conv_val >> 40 & 0xFF)
			buff.append(conv_val >> 32 & 0xFF)
			buff.append(conv_val >> 24 & 0xFF)
			buff.append(conv_val >> 16 & 0xFF)
			buff.append(conv_val >> 8 & 0xFF)
			buff.append(conv_val & 0xFF)
	elif dataType == CosemDataType.e_ARRAY:
		buff.append(CosemDataType.e_ARRAY)
		length_data = len(data)
		if length_data >= 128:
			if length_data <= 0xFF:
				buff.append(0x81)
				buff.append(length_data)
			elif length_data > 0xFF and length_data <= 0xFFFF:
				buff.append(0x82)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
			elif length_data > 0xFFFF and length_data <= 0xFFFFFF:
				buff.append(0x83)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)				
			elif length_data > 0xFFFFFF and length_data <= 0xFFFFFFFF:
				buff.append(0x84)
				buff.append(length_data >> 24 & 0xFF)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
		else:
			buff.append(length_data)
		for i in data:
			buff += serialize_data(i[0], i[1])
	elif dataType == CosemDataType.e_STRUCTURE:
		buff.append(CosemDataType.e_STRUCTURE)
		length_data = len(data)
		if length_data >= 128:
			if length_data <= 0xFF:
				buff.append(0x81)
				buff.append(length_data)
			elif length_data > 0xFF and length_data <= 0xFFFF:
				buff.append(0x82)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
			elif length_data > 0xFFFF and length_data <= 0xFFFFFF:
				buff.append(0x83)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)				
			elif length_data > 0xFFFFFF and length_data <= 0xFFFFFFFF:
				buff.append(0x84)
				buff.append(length_data >> 24 & 0xFF)
				buff.append(length_data >> 16 & 0xFF)
				buff.append(length_data >> 8 & 0xFF)
				buff.append(length_data & 0xFF)
		else:
			buff.append(length_data)
		for i in data:
			buff += serialize_data(i[0], i[1])
	return buff

def unserialize_data(data):
	value = None
	dataType = data[0]
	if dataType == CosemDataType.e_NULL_DATA:
		value = "NULL"
		del data[0]
	if dataType == CosemDataType.e_BOOLEAN:
		if len(data) >= 2:
			value = data[1]
			del data[0:2]
	elif dataType == CosemDataType.e_UNSIGNED:
		if len(data) >= 2:
			value = data[1]
			del data[0:2]
	elif dataType == CosemDataType.e_LONG_UNSIGNED:
		if len(data) >= 3:
			value = data[1] << 8
			value += data[2]
			del data[0:3]
	elif dataType == CosemDataType.e_DOUBLE_LONG_UNSIGNED:
		if len(data) >= 5:
			value = data[1] << 24
			value += data[2] << 16
			value += data[3] << 8
			value += data[4]
			del data[0:5]
	elif dataType == CosemDataType.e_LONG64_UNSIGNED:
		if len(data) >= 9:
			value = data[1] << 56
			value += data[2] << 48
			value += data[3] << 40
			value += data[4] << 32
			value += data[5] << 24
			value += data[6] << 16
			value += data[7] << 8
			value += data[8]
			del data[0:9]
	elif dataType == CosemDataType.e_INTEGER:
		if len(data) >= 2:
			value = data[1]
			bits = 8
			if value & (1 << (bits-1)):
				value -= 1 << bits
			del data[0:2]
	elif dataType == CosemDataType.e_LONG:
		if len(data) >= 3:
			value = data[1] << 8
			value += data[2]
			bits = 16
			if value & (1 << (bits-1)):
				value -= 1 << bits
			del data[0:3]
	elif dataType == CosemDataType.e_DOUBLE_LONG:
		if len(data) >= 5:
			value = data[1] << 24
			value += data[2] << 16
			value += data[3] << 8
			value += data[4]
			bits = 32
			if value & (1 << (bits-1)):
				value -= 1 << bits
			del data[0:5]
	elif dataType == CosemDataType.e_LONG64:
		if len(data) >= 9:
			value = data[1] << 56
			value += data[2] << 48
			value += data[3] << 40
			value += data[4] << 32
			value += data[5] << 24
			value += data[6] << 16
			value += data[7] << 8
			value += data[8]
			bits = 64
			if value & (1 << (bits-1)):
				value -= 1 << bits
			del data[0:9]
	elif dataType == CosemDataType.e_ENUM:
		if len(data) >= 2:
			value = data[1]
			del data[0:2]
	elif dataType == CosemDataType.e_OCTET_STRING:
		offset = 0
		data_length = data[1]
		if data_length > 0x80:
			offset = data_length - 0x80
			if offset == 1:
				data_length = data[1+offset]
			elif offset == 2:
				data_length = data[1+(offset-1)] << 8
				data_length += data[1+offset]
			elif offset == 3:
				data_length = data[1+(offset-2)] << 16
				data_length += data[1+(offset-1)] << 8
				data_length += data[1+offset]
			elif offset == 4:
				data_length = data[1+(offset-3)] << 24
				data_length += data[1+(offset-2)] << 16
				data_length += data[1+(offset-1)] << 8
				data_length += data[1+offset]
		if len(data) >= (data_length+offset+2):
			value = data[(2+offset):((2+offset)+data_length)]
			del data[0:(2+offset+data_length)]
	elif dataType == CosemDataType.e_VISIBLE_STRING:
		offset = 0
		data_length = data[1]
		if data_length > 0x80:
			offset = data_length - 0x80
			if offset == 1:
				data_length = data[1+offset]
			elif offset == 2:
				data_length = data[1+(offset-1)] << 8
				data_length += data[1+offset]
			elif offset == 3:
				data_length = data[1+(offset-2)] << 16
				data_length += data[1+(offset-1)] << 8
				data_length += data[1+offset]
			elif offset == 4:
				data_length = data[1+(offset-3)] << 24
				data_length += data[1+(offset-2)] << 16
				data_length += data[1+(offset-1)] << 8
				data_length += data[1+offset]
		if len(data) >= (data_length+offset+2):
			value = data[(2+offset):((2+offset)+data_length)]
			del data[0:(2+offset+data_length)]
	elif dataType == CosemDataType.e_BIT_STRING:
		num_of_bit = data[1]
		value = 0
		offset = 0
		if num_of_bit > 0x80:
			offset = num_of_bit - 0x80
			if offset == 1:
				num_of_bit = data[1+offset]
			elif offset == 2:
				num_of_bit = data[1+(offset-1)] << 8
				num_of_bit += data[1+offset]
			elif offset == 3:
				num_of_bit = data[1+(offset-2)] << 16
				num_of_bit += data[1+(offset-1)] << 8
				num_of_bit += data[1+offset]
			elif offset == 4:
				num_of_bit = data[1+(offset-3)] << 24
				num_of_bit += data[1+(offset-2)] << 16
				num_of_bit += data[1+(offset-1)] << 8
				num_of_bit += data[1+offset]
		num_of_byte = int((num_of_bit+8-1)/8)
		for i in range(num_of_byte):
			value += data[2+offset+i] << (8*i)
		del data[0:((2+offset)+num_of_byte)]
	elif dataType == CosemDataType.e_FLOAT32:
		if len(data) >= 5:
			value = data[1] << 24
			value += data[2] << 16
			value += data[3] << 8
			value += data[4]

			conv_val = bin(value).replace('0b','')
			value = struct.unpack('!f',struct.pack('!I', int(conv_val, 2)))[0]

			del data[0:5]
	elif dataType == CosemDataType.e_FLOAT64:
		if len(data) >= 9:
			value = data[1] << 56
			value += data[2] << 48
			value += data[3] << 40
			value += data[4] << 32
			value += data[5] << 24
			value += data[6] << 16
			value += data[7] << 8
			value += data[8]

			conv_val = bin(value).replace('0b','')
			value = struct.unpack('!d',struct.pack('!I', int(conv_val, 2)))[0]

			del data[0:9]
	elif dataType == CosemDataType.e_ARRAY:
		if len(data) >= 2:
			offset = 0
			data_length = data[1]
			if data_length > 0x80:
				offset = data_length - 0x80
				if offset == 1:
					data_length = data[1+offset]
				elif offset == 2:
					data_length = data[1+(offset-1)] << 8
					data_length += data[1+offset]
				elif offset == 3:
					data_length = data[1+(offset-2)] << 16
					data_length += data[1+(offset-1)] << 8
					data_length += data[1+offset]
				elif offset == 4:
					data_length = data[1+(offset-3)] << 24
					data_length += data[1+(offset-2)] << 16
					data_length += data[1+(offset-1)] << 8
					data_length += data[1+offset]
			value = data_length
			del data[0:2+offset]
	elif dataType == CosemDataType.e_STRUCTURE:
		if len(data) >= 2:
			offset = 0
			data_length = data[1]
			if data_length > 0x80:
				offset = data_length - 0x80
				if offset == 1:
					data_length = data[1+offset]
				elif offset == 2:
					data_length = data[1+(offset-1)] << 8
					data_length += data[1+offset]
				elif offset == 3:
					data_length = data[1+(offset-2)] << 16
					data_length += data[1+(offset-1)] << 8
					data_length += data[1+offset]
				elif offset == 4:
					data_length = data[1+(offset-3)] << 24
					data_length += data[1+(offset-2)] << 16
					data_length += data[1+(offset-1)] << 8
					data_length += data[1+offset]
			value = data_length
			del data[0:2+offset]
	return value

def extract_data(val):
	data_result = None
	check_type = val[0]
	if check_type == CosemDataType.e_ARRAY or check_type == CosemDataType.e_STRUCTURE:
		data_result = []
		data_length = unserialize_data(val)
		is_ok = True
		for i in range(data_length):
			res = extract_data(val)
			data_result.append(res)
		if not is_ok:
			data_result = None
	else:
		data_result = unserialize_data(val)
	# print("type: ", check_type, " data: ", data_result)
	return data_result

####################################################################
# DLMS SERVICE
####################################################################
from .security_util import sc_byte
from .dlms_security import DlmsSecurity

class DlmsService:
	response = ServiceResponse.OK
	max_apdu_size = 0

	def __init__(self, max_apdu_size):
		self.max_apdu_size = max_apdu_size
		self.block_number = 0
		self.get_data_result = None
		self.set_data_value = None
		self.act_param = None
		self.security = DlmsSecurity()
		self.sys_TC = None
		self.sys_TS = None
		self.GUEK = None
		self.GAK = None
		self.sec_pol = None
		self.hls_key = None
		self.auth_mech = mechanism.LOWEST_LEVEL

	def conv_hexstring_to_list(self, val):
		return [int(val[i] + val[i+1], 16) for i in range(0,len(val),2)]

	def is_sec_param_filled(self):
		if self.sys_TC == None:
			return False
		if self.GUEK == None:
			return False
		if self.GAK == None:
			return False
		return True

	def is_transport_secured(self):
		return (self.sec_pol != None)

	def set_security_param(self, sys_T, GUEK, GAK, sec_pol, invoc_count):
		self.sys_TC = self.conv_hexstring_to_list(sys_T)
		self.GUEK = self.conv_hexstring_to_list(GUEK)
		self.GAK = self.conv_hexstring_to_list(GAK)
		self.sec_pol = sec_pol
		if invoc_count != None:
			self.security.set_invoc_counter(invoc_count)

	def get_InitiateRequest(self):
		buff = []
		buff.append(0x01)
		buff.append(0x00)
		buff.append(0x00)
		buff.append(0x00)
		buff.append(0x06)
		buff.append(0x5F)
		buff.append(0x1F)
		buff.append(0x04)
		buff.append(0x00)
		buff = buff + [0x1c, 0x1e, 0x7d]#[0x00, 0x3D, 0x1B] # Conformance negotiation, hardcoded for now
		buff.append(self.max_apdu_size >> 8 & 0xFF)
		buff.append(self.max_apdu_size & 0xFF)
		return buff

	def check_asso_res(self, buffer):
		is_success = True
		if buffer[2] != 0:
			is_success = False
		return is_success

	def check_asso_diag(self, buffer):
		is_success = True
		if buffer[-1] not in [userDiag.SUCCESS, userDiag.AUTHENTICATION_REQUIRED]:
			if buffer[-1] == userDiag.AUTHENTICATION_FAILURE:
				print("WRONG LLS PASSWORD!")
			else:
				print("SOMETHING WRONG IN AARQ")
			is_success = False
		return is_success

	def check_meter_sysT(self, buffer):
		self.sys_TS = buffer[2:]

	def check_StoC(self, buffer):
		self.security.set_StoC(buffer[2:])

	def validateUserInfo(self, buffer):
		value = buffer[12] << 8
		value += buffer[13]
		self.max_apdu_size = value

	def get_RLRQ_frame(self, reason, is_with_ui, is_protected):
		buff = [ServiceTag.RLRQ]
		content_buff = [0x80, reason, 0x00]
		if is_with_ui:
			user_info_buff = [AARQTag.UserInfo]
			init_req_buff = self.get_InitiateRequest()
			if is_protected:
				chipper_init_req_buff = self.security.encrypt_apdu(sc_byte.AUTH_ENCRYPT, self.GUEK, self.GAK, self.sys_TC, init_req_buff)
				init_req_buff = [0x21, len(chipper_init_req_buff)] + chipper_init_req_buff # 21 is tag of chiper init req
			user_info_buff.append(len(init_req_buff) + 2)
			user_info_buff.append(AARQTag.ChoiceUserInfo)
			user_info_buff.append(len(init_req_buff))
			user_info_buff = user_info_buff + init_req_buff
			content_buff += user_info_buff
		buff.append(len(content_buff))
		buff += content_buff
		return buff

	def get_AARQ_frame(self, auth_mech, auth_val):
		buff = [AARQTag.AARQ]
		if auth_mech == mechanism.HIGH_LEVEL_GMAC:
			acn_buff = [AARQTag.AppContext, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x03]
		else:
			acn_buff = [AARQTag.AppContext, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01]
		acse_req_buff = []
		ap_title_field = []
		auth_buff = []
		if auth_mech != mechanism.LOWEST_LEVEL:
			acse_req_buff = [AARQTag.ACSEReq, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02]
			if self.sys_TC == None:
				if auth_mech == mechanism.HIGH_LEVEL_GMAC:
					raise ValueError
			else:
				ap_title_field = [AARQTag.SysTitle, 0x0A, 0x04, 0x08] + self.sys_TC
			if auth_mech == mechanism.LOW_LEVEL:
				acse_req_buff.append(0x01)
			elif auth_mech in [mechanism.HIGH_LEVEL, mechanism.HIGH_LEVEL_GMAC]:
				acse_req_buff.append(auth_mech)
				auth_val = self.security.generate_challenge(16) # auth val in HLS is CtoS
				self.security.set_CtoS(auth_val)
				self.auth_mech = auth_mech
			auth_buff = [AARQTag.AuthVal]
			auth_buff.append(len(auth_val) + 2)
			auth_buff.append(AARQTag.ChoiceAuthVal)
			auth_buff.append(len(auth_val))
			auth_buff = auth_buff + auth_val
		user_info_buff = [AARQTag.UserInfo]
		init_req_buff = self.get_InitiateRequest()
		if auth_mech == mechanism.HIGH_LEVEL_GMAC:
			chipper_init_req_buff = self.security.encrypt_apdu(sc_byte.AUTH_ENCRYPT, self.GUEK, self.GAK, self.sys_TC, init_req_buff)
			init_req_buff = [0x21, len(chipper_init_req_buff)] + chipper_init_req_buff # 21 is tag of chiper init req
		user_info_buff.append(len(init_req_buff) + 2)
		user_info_buff.append(AARQTag.ChoiceUserInfo)
		user_info_buff.append(len(init_req_buff))
		user_info_buff = user_info_buff + init_req_buff
		aarq_buff = acn_buff + ap_title_field + acse_req_buff + auth_buff + user_info_buff
		buff.append(len(aarq_buff))
		buff = buff + aarq_buff
		return buff

	def check_AARE_frame(self, checkBuffer):
		is_ok = False
		check_index = 0
		while check_index < len(checkBuffer):
			if checkBuffer[check_index] == AARETag.AppContext:
				check_index += 1
				length = checkBuffer[check_index]
				check_index += 1
				check_index += length					
			elif checkBuffer[check_index] == AARETag.ResultAsso:
				check_index += 1
				length = checkBuffer[check_index]
				check_index += 1
				is_ok = self.check_asso_res(checkBuffer[check_index:check_index+length])
				check_index += length
			elif checkBuffer[check_index] == AARETag.Diagnostic:
				check_index += 1
				length = checkBuffer[check_index]
				check_index += 1
				is_ok = is_ok and self.check_asso_diag(checkBuffer[check_index:check_index+length])
				check_index += length
			elif checkBuffer[check_index] == AARETag.SysTitle:
				check_index += 1
				length = checkBuffer[check_index]
				check_index += 1
				self.check_meter_sysT(checkBuffer[check_index:check_index+length])
				check_index += length
			elif checkBuffer[check_index] == AARETag.RespondToAuthTag:
				check_index += 1
				length = checkBuffer[check_index]
				check_index += 1
				self.check_StoC(checkBuffer[check_index:check_index+length])
				check_index += length
			elif checkBuffer[check_index] == AARETag.UserInfo:
				check_index += 1
				length = checkBuffer[check_index]
				check_index += 1
				self.validateUserInfo(checkBuffer[check_index:check_index+length])
				check_index += length
			else:
				check_index += 1
		return is_ok

	def get_Reply_to_HLS_frame(self, force_false=False):
		response = None
		sec_param = None
		if self.auth_mech == mechanism.HIGH_LEVEL:
			sec_param = self.hls_key
		elif self.auth_mech == mechanism.HIGH_LEVEL_GMAC:
			sec_param = [sc_byte.AUTH_ONLY, self.GUEK, self.GAK]
		buff = self.security.construct_HLS_Pass3(self.auth_mech, self.sys_TC, self.sys_TS, sec_param, force_false)
		if len(buff) > 0:
			act_buff = self.get_ACT_REQ_frame(15, "0;0;40;0;0;255", 1, CosemDataType.e_OCTET_STRING, buff)
			if self.is_transport_secured():
				sec_byte = self.sec_pol
				if self.auth_mech == mechanism.HIGH_LEVEL_GMAC:
					sec_byte = sc_byte.AUTH_ENCRYPT
				chipper_act_buff = self.security.encrypt_apdu(sec_byte, self.GUEK, self.GAK, self.sys_TC, act_buff)
				response = [0xCB, len(chipper_act_buff)] + chipper_act_buff
			else:
				response = act_buff
		return response

	def check_Reply_to_HLS_response(self, buffer):
		is_ok = False
		sec_param = None
		check_buff = []
		if self.auth_mech == mechanism.HIGH_LEVEL:
			sec_param = self.hls_key
		elif self.auth_mech == mechanism.HIGH_LEVEL_GMAC:
			sec_param = [self.GUEK, self.GAK]
		if buffer[3] == ServiceTag.GLO_ACT_RESPONSE:
			buffer = buffer[5:]
			plain_buff = self.security.decrypt_apdu(self.GUEK, self.GAK, self.sys_TS, buffer)
			check_buff = plain_buff[8:]
		else:
			check_buff = buffer[11:]
		is_ok = self.security.verify_HLS_Pass4(self.auth_mech, self.sys_TC, self.sys_TS, sec_param, check_buff)
		return is_ok

	def get_GET_REQ_frame(self, type, cls_id, obis, att, sel_access_param = None):
		buff = []
		buff.append(ServiceTag.GET_REQUEST)
		buff.append(type)
		buff.append(ServiceTag.INVOKE_ID_MASK | 0x01)
		if type == ServiceTag.GET_REQUEST_NORMAL:
			buff.append(cls_id >> 8 & 0xFF)
			buff.append(cls_id & 0xFF)
			obis = obis.split(';')
			for i in obis:
				buff.append(int(i))
			buff.append(att)
			if sel_access_param == None:
				buff.append(0x00)
			else:
				buff.append(0x01)
				buff.append(sel_access_param[0])
				if sel_access_param[0] == 1:
					buff.append(0x02)
					buff.append(0x04)
					# restricting object (restricted by clock time)
					cosem_clock_id = [0x12, 0x00, 0x08, 0x09, 0x06, 0x00, 0x00, 0x01, 0x00, 0x00, 0xff, 0x0f, 0x02, 0x12, 0x00, 0x00]
					buff.append(0x02)
					buff.append(0x04)
					buff += cosem_clock_id
					# from value
					buff += serialize_data(CosemDataType.e_DATE_TIME, sel_access_param[1][0])
					# to value
					buff += serialize_data(CosemDataType.e_DATE_TIME, sel_access_param[1][1])
					# selected value (no selected value)
					buff.append(0x01)
					buff.append(0x00)
				elif sel_access_param[0] == 2:
					buff.append(0x02)
					buff.append(0x04)
					buff += serialize_data(CosemDataType.e_DOUBLE_LONG_UNSIGNED, sel_access_param[1][0])
					buff += serialize_data(CosemDataType.e_DOUBLE_LONG_UNSIGNED, sel_access_param[1][1])
					buff += serialize_data(CosemDataType.e_LONG_UNSIGNED, sel_access_param[1][2])
					buff += serialize_data(CosemDataType.e_LONG_UNSIGNED, sel_access_param[1][3])
		elif type == ServiceTag.GET_REQUEST_NEXT:
			buff.append(self.block_number >> 24 & 0xFF)
			buff.append(self.block_number >> 16 & 0xFF)
			buff.append(self.block_number >> 8 & 0xFF)
			buff.append(self.block_number & 0xFF)
		return buff

	def check_GET_RESP_frame(self, resp_buff):
		is_ok = True
		is_finish = True
		data_type = None
		data_result = None
		try:
			if resp_buff[1] == ServiceTag.GET_RESPONSE_NORMAL:
				resp_status = resp_buff[3]
				if resp_status == 0:
					data = resp_buff[4:]
					data_type = data[0]
					data_result = extract_data(data)
				else:
					is_ok = False
					data_result = resp_buff[-1]
			elif resp_buff[1] == ServiceTag.GET_RESPONSE_DATABLOCK:
				is_last_block = resp_buff[3]
				if not is_last_block:
					is_finish = False
					self.block_number = resp_buff[4] << 24
					self.block_number += resp_buff[5] << 16
					self.block_number += resp_buff[6] << 8
					self.block_number += resp_buff[7]
					if self.block_number == 1:
						self.get_data_result = resp_buff[12:]
					elif self.block_number > 1:
						self.get_data_result += resp_buff[12:]
				else:
					is_finish = True
					self.block_number = 0
					data_type = self.get_data_result[0]
					self.get_data_result += resp_buff[12:]
					data_result = extract_data(self.get_data_result)
					self.get_data_result = None
		except Exception:
			is_finish = True
			is_ok = False
			data_result = DataAccessResult.e_OTHER_REASON
		return is_finish, is_ok, data_type, data_result

	def get_SET_REQ_frame(self, type, cls_id, obis, att, dtype, value):
		buff = []
		remaining_buff = []
		buff.append(ServiceTag.SET_REQUEST)
		buff.append(type)
		buff.append(ServiceTag.INVOKE_ID_MASK | 0x01)
		if type == ServiceTag.SET_REQUEST_NORMAL or type == ServiceTag.SET_REQUEST_FIRST_DATABLOCK:
			buff.append(cls_id >> 8 & 0xFF)
			buff.append(cls_id & 0xFF)
			obis = obis.split(';')
			for i in obis:
				buff.append(int(i))
			buff.append(att)
			buff.append(0x00) # Disable selective access feature in SET
		if type == ServiceTag.SET_REQUEST_NORMAL:
			buff = buff + serialize_data(dtype, value)
		if type == ServiceTag.SET_REQUEST_FIRST_DATABLOCK:
			val_buff = serialize_data(dtype, value)
			value = val_buff
		if type == ServiceTag.SET_REQUEST_FIRST_DATABLOCK or type == ServiceTag.SET_REQUEST_DATABLOCK:
			is_last_block = False
			header_length = 8 + len(buff) + 3 # datablock header + cosem header buff length + llc length
			if (header_length + len(value)) <= self.max_apdu_size:
				is_last_block = True
			buff.append(is_last_block)
			self.block_number += 1
			buff.append(self.block_number >> 24 & 0xFF)
			buff.append(self.block_number >> 16 & 0xFF)
			buff.append(self.block_number >> 8 & 0xFF)
			buff.append(self.block_number & 0xFF)			
			buff.append(0x82)
			length_data = 0
			if is_last_block:
				self.block_number = 0 # reset block number in last block
				length_data = len(value)
			else:
				length_data = self.max_apdu_size - (header_length)
			buff.append(length_data >> 8 & 0xFF)
			buff.append(length_data & 0xFF)
			buff = buff + value[:length_data]
			remaining_buff = value[length_data:]
		return buff, remaining_buff

	def check_SET_RESP_frame(self, resp_buff):
		is_finish = True
		resp_res = cosemAccessResult.hardware_fault
		try:
			if resp_buff[1] == ServiceTag.SET_RESPONSE_NORMAL:
				resp_res = resp_buff[3]
			elif resp_buff[1] == ServiceTag.SET_RESPONSE_DATABLOCK:
				is_finish = False
			elif resp_buff[1] == ServiceTag.SET_RESP_LAST_DATABLOCK:
				resp_res = resp_buff[3]
		except Exception:
			resp_res = cosemAccessResult.hardware_fault
			is_finish = True
		return is_finish, resp_res

	def get_ACT_REQ_frame(self, cls_id, obis, mtd, dtype, param):
		buff = []
		buff.append(ServiceTag.ACT_REQUEST)
		buff.append(ServiceTag.ACT_REQUEST_NORMAL)
		buff.append(ServiceTag.INVOKE_ID_MASK | 0x01)
		buff.append(cls_id >> 8 & 0xFF)
		buff.append(cls_id & 0xFF)
		obis = obis.split(';')
		for i in obis:
			buff.append(int(i))
		buff.append(mtd)
		buff.append(0x01)
		buff = buff + serialize_data(dtype, param)
		return buff

	def check_ACT_RESP_frame(self, buff):
		resp_res = ActionResult.e_OTHER_REASON
		opt_data = None
		try:
			resp_res = buff[6]
			if len(buff) > 7:
				opt_data = buff[7:]
		except Exception:
			resp_res = ActionResult.e_OTHER_REASON
			opt_data = None
		return resp_res, opt_data

	def get_GLO_ENC_frame(self, svc_tag, plain_apdu):
		glo_enc_buff = [svc_tag]
		enc_buff = self.security.encrypt_apdu(self.sec_pol, self.GUEK, self.GAK, self.sys_TC, plain_apdu)
		length_data = len(enc_buff)
		if length_data > 128:
			if length_data <= 0xFF:
				glo_enc_buff.append(0x81)
				glo_enc_buff.append(length_data)
			elif length_data > 0xFF and length_data <= 0xFFFF:
				glo_enc_buff.append(0x82)
				glo_enc_buff.append(length_data >> 8 & 0xFF)
				glo_enc_buff.append(length_data & 0xFF)
		else:
			glo_enc_buff.append(length_data)
		glo_enc_buff = glo_enc_buff + enc_buff
		return glo_enc_buff

	def check_GLO_RESP_frame(self, chippered_buff):
		byte_of_length = 0
		if chippered_buff[1] > 0x80:
			byte_of_length = chippered_buff[1] - 0x80
		chipered_apdu = chippered_buff[(2+byte_of_length):]
		plain_apdu = self.security.decrypt_apdu(self.GUEK, self.GAK, self.sys_TS, chipered_apdu)
		return plain_apdu