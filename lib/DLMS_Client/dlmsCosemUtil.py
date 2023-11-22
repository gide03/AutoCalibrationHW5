class aarqConstant:
	AARQTag = 0x60
	LLSLength = 0x36
	NSLength = 0x1D
	ACNTag = 0xA1
	ACNLength = 0x09
	choiceACNTag = 0x06
	choiceACNLength = 0x07
	ACSEReqTag = 0x8A
	ACSELength = 0x02
	mechanismTag = 0x8B
	mechanismLength = 0x07
	AuthValTag = 0xAC
	AuthValLength = 0x0A
	choiceAuthValTag = 0x80
	choiceAuthValLength = 0x08
	offsetLLSPass = 30

class aareConstant:
	AARETag = 0x61
	AARELength = 0x29
	ACNTag = 0xA1
	ACNLength = 0x09
	choiceACNTag = 0x06
	choiceACNLength = 0x07
	resultAssoTag = 0xA2
	resultAssoLength = 0x03
	choiceResultAssoTag = 0x02
	choiceResultAssoLength = 0x01
	successResultAssoVal = 0x00
	failResultAssoVal = 0x01
	diagnosticTag = 0xA3
	diagnosticLength = 0x05
	choiceAcseTag = 0xA1
	choiceAcseLength = 0x03
	resultAcseDiagTag = 0x02
	resultAcseDiagLength = 0x01
	successAcseDiagVal = 0x00
	fail1AcseDiagVal = 0x0D
	fail2AcseDiagVal = 0x01
	userInfoTag = 0xBE
	userInfoLength = 0x10
	choiceUserInfoTag = 0x04
	choiceUserInfoLength = 0x0E
	#successUserInfoVal = [0x08, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x50, 0x1F, 0x01, 0xF4, 0x00, 0x07]
	successUserInfoVal = [0x08, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x10, 0x1C, 0x02, 0x00, 0x00, 0x07]
	fail1UserInfoVal = [0x08, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x10, 0x1E, 0x00, 0x00, 0x00, 0x07]
	fail2UserInfoVal = [0x0E, 0x01, 0x06, 0x01]
	offsetAcseDiagVal = 27


class authError:
	NO_ERROR = 0x00
	LLS_PASSWORD_ERROR = 0x0D
	AARQ_ERROR = 0x02

class secMechanism:
	LOWEST_LEVEL = 0
	LOW_LEVEL = 1

class cosemRequest:
	GET_REQUEST_TAG = 0xC0
	GET_REQUEST_NORMAL_TAG = 0x01
	INVOKE_ID = 0x41
	SET_REQUEST_TAG = 0xC1
	SET_REQUEST_NORMAL_TAG = 0x01
	ACT_REQUEST_TAG = 0xC3
	ACT_REQUEST_NORMAL_TAG = 0x01

class cosemDataType:
	null_data = 0
	array = 1
	structure = 2
	boolean = 3
	bit_string = 4
	double_long = 5
	double_long_unsigned = 6
	octet_string = 9
	visible_string = 10
	utf8_string = 12
	bcd = 13
	integer = 15
	long = 16
	unsigned = 17
	long_unsigned = 18
	long64 = 20
	long64_unsigned = 21
	enum = 22
	float32 = 23
	float64 = 24
	date_time = 25

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

def convert_dtype_to_string(dtype):
	return {
		cosemDataType.null_data : 'null',
        cosemDataType.boolean : 'bool',
        cosemDataType.unsigned : 'unsigned',
        cosemDataType.long_unsigned : 'long_unsigned',
        cosemDataType.double_long_unsigned : 'double_long_unsigned',
        cosemDataType.long64_unsigned : 'long64_unsigned',
        cosemDataType.integer : 'integer',
        cosemDataType.long : 'long',
        cosemDataType.double_long : 'double_long',
        cosemDataType.long64 : 'long64',
        cosemDataType.enum : 'enum',
        cosemDataType.structure : 'struct',
        cosemDataType.array : 'array',
        cosemDataType.octet_string : 'octet_string',
        cosemDataType.visible_string : 'visible_string',
        cosemDataType.bit_string : 'bit_string',
        cosemDataType.date_time : 'date_time'
    }[dtype]

def convert_data_result_to_string(dres):
	return {
		cosemAccessResult.success : 'SUCCESS',
		cosemAccessResult.hardware_fault : 'HARDWARE FAULT',
		cosemAccessResult.temporary_failure : 'TEMPORARY FAULT',
		cosemAccessResult.read_write_denied : 'R/W DENIED',
		cosemAccessResult.object_undefined : 'OBJECT UNDEFINED',
		cosemAccessResult.object_class_inconsistent : 'OBJECT CLASS INCONSISTENT',
		cosemAccessResult.object_unavailable : 'OBJECT UNAVAILABLE',
		cosemAccessResult.type_unmatched : "TYPE UNMATCHED",
		cosemAccessResult.scope_of_access_violated : "SCOPE OF ACCESS VIOLATED",
		cosemAccessResult.data_block_unaivailable : "DATA BLOCK UNAVAILABLE",
		cosemAccessResult.long_get_aborted : "LONG GET ABORTED",
		cosemAccessResult.other_reason : 'OTHER REASON'
    }[dres]