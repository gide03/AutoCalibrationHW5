import serial
import time
from .hdlc.hdlc_app import HdlcClass
from .hdlc.hdlc_util import controlType, segmentBit, pollFinalBit, frameError
from .hdlc.hdlc_parameter import hdlcParam
from .dlmsCosemUtil import aareConstant
from .dlmsCosemUtil import authError
from .dlmsCosemUtil import cosemAccessResult
from .dlmsCosemUtil import convert_dtype_to_string, convert_data_result_to_string
from .dlms_service.dlms_service import DlmsService, mechanism, ServiceTag, unserialize_data, extract_data
from threading import Thread

class TransportSec:
	NO_SECURITY = 0x00
	AUTH_ONLY = 0x10
	ENC_ONLY = 0x20
	AUTH_ENC = 0x30

def conv_enum_to_baud(in_enum):
	return {
        0 : 300,
        1 : 600,
        2 : 1200,
        3 : 2400,
        4 : 4800,
        5 : 9600,
        6 : 19200,
        7 : 38400,
        8 : 57600,
        9 : 115200
    }[in_enum]

class DlmsCosemClient:
	ser = None
	frame_buff = []
	dest_addr = 0
	src_addr = 0
	counter_R = 0
	counter_S = 0

	def __init__(self, port="", baudrate=9600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=0.3, inactivity_timeout=60, login_retry=1, meter_addr=16, client_nb=16, direct_ser = None):
		if direct_ser != None:
			self.ser = direct_ser
		else:
			self.ser = serial.Serial(
				port=port,
				baudrate=baudrate,
				parity=parity,
				bytesize=bytesize,
				stopbits=stopbits,
				timeout=timeout
			)
		SAP_LOGICAL_DEVICE = 1 # Hardcoded
		self.dest_addr = SAP_LOGICAL_DEVICE << 16 | meter_addr
		self.src_addr = client_nb
		windowTx = 1
		windowRx = 1
		maxSizeInfoField = 128
		maxCosemBuffSize = 512
		hdlc_param = hdlcParam(windowRx, windowTx, maxSizeInfoField, maxCosemBuffSize)
		self.hdlc = HdlcClass(hdlc_param)
		self.dlms = DlmsService(maxCosemBuffSize)
		self.max_apdu_size = maxCosemBuffSize
		self.is_connected = False
		self.last_GET_status = cosemAccessResult.success
		self.last_SET_status = cosemAccessResult.success
		self.last_ACT_status = cosemAccessResult.success
		self.timer_count = 0
		self.is_timer_stop = False
		self.timeout_counter = inactivity_timeout
		self.is_inactive = False
		self.num_of_retry = login_retry
		self.retry_counter = 0
		self.last_send_msg = []

	def is_out_empty(self):
		is_empty = (self.ser.out_waiting == 0)
		return is_empty

	def reset_out_buff(self):
		self.ser.reset_output_buffer()

	def start_inactivity(self):
		self.is_inactive = False
		self.timer_count = 0
		Thread(target = self.count_inactivity, daemon=True, args = ()).start()

	def count_inactivity(self):
		while self.timer_count <= self.timeout_counter and not self.is_timer_stop:
			self.timer_count += 1
			time.sleep(1)
		if not self.is_timer_stop:
			self.is_inactive = True
		self.is_timer_stop = False

	"""
		Date time convertion helper
		in: date_time, format: [year, month, date, hour, minute, second]
		out: dlms format date time
	"""
	def convert_date_time(self, date_time):

		conv_date_time = []

		conv_date_time.append(date_time[0] >> 8)

		conv_date_time.append(date_time[0] & 0xFF)

		conv_date_time += date_time[1:3]

		conv_date_time.append(0xFF)

		conv_date_time += date_time[3:6]

		conv_date_time += [0x00, 0x80, 0x00, 0x00]

		return conv_date_time

	# Bit string manipulation helper
	def get_val_bitstring(self, bit_post):
		val = 0
		if type(bit_post) != type([]):
			bit_post = [bit_post]
		for i in bit_post:
			byte_num = int((i+8-1)/8)
			pos = (8*byte_num) - (i-(8*(byte_num-1)))
			val += (1 << pos)
		return val

	def get_pos_bitstring(self, value):
		num_of_byte = 0
		check_val = 0
		while check_val <= value:
			num_of_byte += 1
			check_val = 2**(8*num_of_byte)
		check_active_bit = []
		for byte in range(num_of_byte):
			check_byte = value >> (8*byte) &0xFF
			if check_byte:
				for i in range(8):
					check_bit = (check_byte >> i) & 1
					if check_bit:
						check_active_bit.append((8*byte)+(8-i))
		check_active_bit.sort()
		return check_active_bit

	# in case need to unserialize data separately
	def helper_unserialize(self, buff):
		return unserialize_data(buff)

	def helper_extract_data(self, buff):
		return extract_data(buff)

	def change_client(self, client_nb):
		self.src_addr = client_nb
	
	def get_active_client(self):
		return self.src_addr

	def get_sap_logical_device(self):
		return self.dest_addr >> 16

	def get_meter_address(self):
		return int(self.dest_addr & 0x0000FFFF)

	def set_sap_logical_device(self, value):
		temp_meter_addr = int(self.dest_addr & 0x0000FFFF)
		self.dest_addr = value << 16 | temp_meter_addr

	def set_meter_address(self, value):
		temp_sap_ld = self.dest_addr >> 16
		self.dest_addr = temp_sap_ld << 16 | value

	def convert_buffer(self, buffer):
		length = len(buffer)
		for i_hex in range(length):
			buffer[i_hex] = int(buffer[i_hex], 16)
		return buffer		

	def set_counter_R(self, value):
		self.counter_R = value

	def set_counter_S(self, value):
		self.counter_S = value
	
	def increment_R(self):
		self.counter_R = (self.counter_R + 1) % 8

	def increment_S(self):
		self.counter_S = (self.counter_S + 1) % 8

	def iec1107_req_msg(self):
		req_msg = [
			0x2F, 0x3F, 0x21, 0x0D, 0x0A
		]
		self.send_msg(req_msg)
	
	def iec1107_ack_msg(self):
		ack_msg = [
			0x06, 0x32, 0x35, 0x32, 0x0D, 0x0A
		]
		self.send_msg(ack_msg)

	def snrm_msg(self):
		negotiation_param = [
			0x81, 0x80, 0x12, 
			0x05, 0x01, 0x80, 
			0x06, 0x01, 0x80, 
			0x07, 0x04, 0x00, 0x00, 0x00, 0x01, 
			0x08, 0x04, 0x00, 0x00, 0x00, 0x01]
		self.set_counter_R(0)
		self.set_counter_S(0)
		response_buff = self.hdlc.getTxHdlcFrame(negotiation_param, segmentBit.SB_OFF, self.dest_addr, self.src_addr, 0, controlType.SNRM, 0, 0, pollFinalBit.PF_ON)
		self.send_msg(response_buff)

	def send_rlrq_msg(self, reason=1, is_with_ui=False, is_protected=False):
		rlrq_frame = self.dlms.get_RLRQ_frame(reason, is_with_ui, is_protected)
		rlrq_frame = self.hdlc.getTxInformationField(rlrq_frame)
		response_buff = self.hdlc.getTxHdlcFrame(rlrq_frame, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		self.increment_S()
		self.send_msg(response_buff)

	def aarq_msg(self, auth_mech, password):
		if password != "":
			conv_password = [ord(i) for i in password]
			password = conv_password
		else:
			password = []
		aarq_frame = self.dlms.get_AARQ_frame(auth_mech, password)
		aarq_frame = self.hdlc.getTxInformationField(aarq_frame)
		response_buff = self.hdlc.getTxHdlcFrame(aarq_frame, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		self.increment_S()
		self.send_msg(response_buff)

	def aare_check(self, buffer):
		return self.dlms.check_AARE_frame(buffer)

	def set_secure_param(self, sys_TC, GUEK, GAK, sec_type, invoc_count = None):
		try:
			if len(sys_TC) != 16 or len(GUEK) != 32 or len(GAK) != 32:
				raise ValueError # Bad length parameter
			self.dlms.set_security_param(sys_TC, GUEK, GAK, sec_type, invoc_count)
			print("TRANSPORT IS SECURED")
		except Exception:
			print("BAD SEC PARAMETER INPUT")

	def send_HLS_Pass3(self, auth_mech, force_false=False):
		pass3_frame = []
		if auth_mech in [mechanism.HIGH_LEVEL, mechanism.HIGH_LEVEL_GMAC]:
			pass3_frame = self.dlms.get_Reply_to_HLS_frame(force_false)
		pass3_frame = self.hdlc.getTxInformationField(pass3_frame)
		response_buff = self.hdlc.getTxHdlcFrame(pass3_frame, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		self.increment_S()
		self.send_msg(response_buff)

	def check_HLS_Pass4(self, buffer):
		return self.dlms.check_Reply_to_HLS_response(buffer)

	def read_msg(self, is_optic = False):
		receive_in_progress = False
		self.frame_buff = []
		check_msg = None
		self.retry_counter = 0
		while self.retry_counter < self.num_of_retry:
			self.start_inactivity()
			while not self.is_inactive:
				check_serial = self.ser.read().hex()
				if (len(check_serial) != 0 or check_serial == '7e') and not(receive_in_progress):
					receive_in_progress = True
				if receive_in_progress:
					if(len(check_serial) == 0):
						self.is_timer_stop = True
						break
					else:
						self.frame_buff.append(check_serial)
			if self.is_inactive:
				self.send_msg(self.last_send_msg)
				self.retry_counter += 1
			else:
				break
		if self.is_inactive:
			raise TimeoutError
		if not self.is_inactive and not is_optic:
			self.frame_buff = self.convert_buffer(self.frame_buff)
			check_msg = self.hdlc.checkRxHdlcFrame(self.frame_buff, self.get_meter_address())
			if self.hdlc.getControlType() == controlType.INFO:
				self.increment_R()
		elif not self.is_inactive and is_optic:
			check_msg = True
		self.frame_buff = []
		return check_msg

	def send_msg(self, buffer):
		self.last_send_msg = buffer
		# print("delay before send")
		time.sleep(300/1000.0)
		self.ser.write(buffer)

	def rr_response(self):
		rr_buff = []
		response_buff = self.hdlc.getTxHdlcFrame(rr_buff, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.RR, controlType.RR, self.counter_R, 0, pollFinalBit.PF_ON)
		self.send_msg(response_buff)

	def idle_rr_msg(self):
		self.rr_response()
		self.read_msg()

	def open_hdlc_only(self):
		is_ok = False
		self.snrm_msg()
		check_resp = self.read_msg()
		if check_resp == frameError.NO_ERROR:
			is_ok = True
		return is_ok

	def test_info(self, buff):
		send_buff = self.hdlc.getTxInformationField(buff)
		response_buff = self.hdlc.getTxHdlcFrame(send_buff, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.UI, controlType.UI, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		return response_buff

	def send_tx_remaining_info_frame(self):
		remaining_buffer = self.hdlc.getTxInformationField(self.hdlc.tx_segmented_info)
		seg_bit = segmentBit.SB_OFF
		if len(self.hdlc.tx_segmented_info) > 0:
			seg_bit = segmentBit.SB_ON
		response_buff = self.hdlc.getTxHdlcFrame(remaining_buffer, seg_bit, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		self.increment_S()
		self.send_msg(response_buff)

	def client_login_optic(self, password = "", auth_mech=mechanism.LOWEST_LEVEL):
		# Adding try except cause sometime the change baudrate error
		try:
			self.last_send_msg = []
			login_success = False
			self.ser.baudrate = 300
			self.ser.parity = serial.PARITY_EVEN
			self.ser.bytesize = serial.SEVENBITS
			self.iec1107_req_msg()
			if self.read_msg(True) == True:
				time.sleep(200/1000.0)
				self.iec1107_ack_msg()
				time.sleep(200/1000.0)
				self.ser.baudrate = 9600
				if self.read_msg(True) == True:
					time.sleep(200/1000.0)
					self.ser.parity = serial.PARITY_NONE
					self.ser.bytesize = serial.EIGHTBITS
					login_success = self.client_login(password, auth_mech)
		except Exception:
			time.sleep(0.5)
			print("RETRY Happen!")
			login_success = self.client_login_optic(password)
		return login_success

	def client_login_optic_HLS(self, auth_mech, force_false=False, hls_key=None):
		self.last_send_msg = []
		login_success = False
		self.ser.baudrate = 300
		self.ser.parity = serial.PARITY_EVEN
		self.ser.bytesize = serial.SEVENBITS
		self.iec1107_req_msg()
		if self.read_msg(True) == True:
			time.sleep(200/1000.0)
			self.iec1107_ack_msg()
			time.sleep(200/1000.0)
			self.ser.baudrate = 9600
			if self.read_msg(True) == True:
				time.sleep(200/1000.0)
				self.ser.parity = serial.PARITY_NONE
				self.ser.bytesize = serial.EIGHTBITS
				try:
					login_success = self.client_login_HLS(auth_mech, force_false, hls_key)
				except Exception:
					login_success = False
		return login_success

	def client_login_optic_HLS_Fail(self, auth_mech):
		self.client_login_optic_HLS(auth_mech, True)
		print("HLS 5 Optical Failed Trigger")

	def client_login_HLS(self, auth_mech, force_false=False, hls_key=None):
		self.last_send_msg = []
		login_success = False
		if auth_mech == mechanism.HIGH_LEVEL:
			if hls_key == None:
				return False
			if len(hls_key) < 16:
				print("WRONG HLS KEY LENGTH")
				return False
			if type(hls_key) != type(''):
				print("WRONG HLS KEY TYPE")
				return False
			self.dlms.hls_key = [ord(i) for i in hls_key]
		elif auth_mech == mechanism.HIGH_LEVEL_GMAC:
			if self.dlms.is_sec_param_filled == False:
				return False
		self.snrm_msg()
		check_resp = self.read_msg()
		if check_resp == frameError.NO_ERROR:
			self.retry_counter = 0
			self.aarq_msg(auth_mech, [])
			check_resp = self.read_msg()
			if check_resp == frameError.NO_ERROR:
				is_next = self.aare_check(self.hdlc.rx_frameInfo)
				if is_next:
					self.send_HLS_Pass3(auth_mech, force_false)
					check_resp = self.read_msg()
					if check_resp == frameError.NO_ERROR:
						is_success = self.check_HLS_Pass4(self.hdlc.rx_frameInfo)
						if is_success:
							login_success = True
							self.is_connected = True
			else:
				login_success = False
				self.client_logout()
		return login_success

	def client_login_HLS_Fail(self, auth_mech):
		try:
			self.client_login_HLS(auth_mech, True)
		except Exception:
			print("HLS 5 Failed Trigger")

	def client_login(self, password = "", auth_mech=mechanism.LOWEST_LEVEL):
		self.last_send_msg = []
		login_success = False
		if len(password) > 0 and (auth_mech == mechanism.LOWEST_LEVEL):
			auth_mech = mechanism.LOW_LEVEL
		if auth_mech in [mechanism.HIGH_LEVEL, mechanism.HIGH_LEVEL_GMAC]:
			login_success = self.client_login_HLS(auth_mech, False, password)
		else:
			self.snrm_msg()
			check_resp = self.read_msg()
			if check_resp == frameError.NO_ERROR:
				self.retry_counter = 0
				self.aarq_msg(auth_mech, password)
				check_resp = self.read_msg()
				if check_resp == frameError.NO_ERROR:
					rx_frameInfo = self.hdlc.rx_frameInfo
					if rx_frameInfo[aareConstant.offsetAcseDiagVal] == authError.NO_ERROR:
						login_success = True
						self.is_connected = True
					elif rx_frameInfo[aareConstant.offsetAcseDiagVal] == authError.LLS_PASSWORD_ERROR:
						print('Wrong LLS Password')
						self.client_logout()
				else:
					login_success = False
					self.client_logout()
		return login_success
	
	def client_logout(self, is_rlrq=False, is_protected=False):
		if is_rlrq:
			self.send_rlrq_msg(1, True, is_protected)
			self.read_msg() # for now didnt need to check RLRE to make faster testing
		disc_frame = []
		response_buff = self.hdlc.getTxHdlcFrame(disc_frame, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.DISC, controlType.DISC, 0, 0, pollFinalBit.PF_ON)
		self.send_msg(response_buff)
		self.read_msg()
		self.is_connected = False		

	def send_get_req_buffer(self, req_buffer):
		req_buffer = self.hdlc.getTxInformationField(req_buffer)
		req_buffer = self.hdlc.getTxHdlcFrame(req_buffer, segmentBit.SB_OFF, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		self.increment_S()
		self.send_msg(req_buffer)

	def read_get_resp_buffer(self):
		frame_to_process = []
		is_continue = True
		check = self.read_msg()
		if check == frameError.NO_ERROR:
			if self.hdlc.rx_seg_bit == segmentBit.SB_ON:
				self.hdlc.rx_segmented_info = self.hdlc.rx_segmented_info + self.hdlc.rx_frameInfo
				self.hdlc.is_rx_segmented = True
				self.rr_response()
			else:
				if self.hdlc.is_rx_segmented:
					frame_to_process = self.hdlc.rx_segmented_info + self.hdlc.rx_frameInfo
					self.hdlc.is_rx_segmented = False
				else:
					frame_to_process = self.hdlc.rx_frameInfo
					self.hdlc.rx_segmented_info = []
				is_continue = False
		else:
			is_continue = False
		
		if check == None:
			is_continue = False
		if len(frame_to_process) > 3:
			frame_to_process = frame_to_process[3:]
		return is_continue, frame_to_process

	def get_cosem_data(self, class_id, obis_code, att_id, sel_access_param = None, is_note = False):
		data_result = None
		dtype = 0
		is_ok = False
		if self.is_connected:
			req_buffer = self.dlms.get_GET_REQ_frame(ServiceTag.GET_REQUEST_NORMAL, class_id, obis_code, att_id, sel_access_param)
			if self.dlms.is_transport_secured():
				req_buffer = self.dlms.get_GLO_ENC_frame(ServiceTag.GLO_GET_REQUEST, req_buffer)
			self.send_get_req_buffer(req_buffer)
			get_resp_process = True
			frame_to_process = []
			while get_resp_process:
				get_resp_process, frame_to_process = self.read_get_resp_buffer()
			self.hdlc.rx_segmented_info = []
			if len(frame_to_process) > 0:
				if self.dlms.is_transport_secured():
					frame_to_process = self.dlms.check_GLO_RESP_frame(frame_to_process)
				is_finish, is_ok, dtype, data_result = self.dlms.check_GET_RESP_frame(frame_to_process)
				while not is_finish:
					req_buffer = self.dlms.get_GET_REQ_frame(ServiceTag.GET_REQUEST_NEXT, class_id, obis_code, att_id, sel_access_param)
					if self.dlms.is_transport_secured():
						req_buffer = self.dlms.get_GLO_ENC_frame(ServiceTag.GLO_GET_REQUEST, req_buffer)
					self.send_get_req_buffer(req_buffer)
					get_resp_process = True
					frame_to_process = []
					while get_resp_process:
						get_resp_process, frame_to_process = self.read_get_resp_buffer()
					self.hdlc.rx_segmented_info = []
					if len(frame_to_process) > 0:
						if self.dlms.is_transport_secured():
							frame_to_process = self.dlms.check_GLO_RESP_frame(frame_to_process)
						is_finish, is_ok, dtype, data_result = self.dlms.check_GET_RESP_frame(frame_to_process)
					else:
						self.last_GET_status = cosemAccessResult.other_reason
						data_result = None
			else:
				self.last_GET_status = cosemAccessResult.other_reason
				data_result = None
		else:
			self.last_GET_status = cosemAccessResult.other_reason
			data_result = None
		if is_ok:
			self.last_GET_status = cosemAccessResult.success
		else:
			self.last_GET_status = data_result
		if is_note:
			if self.last_GET_status == cosemAccessResult.success:
				dtype = convert_dtype_to_string(dtype)
			else:
				dtype = "NONE"
				data_result = "NONE"
			get_result = convert_data_result_to_string(self.last_GET_status)
			note_result = "GET attribute %s of %s. Result: %s, Data Type: %s, Data Result: %s" %(att_id, obis_code, get_result, dtype, data_result)
			data_result = note_result
		else:
			if not is_ok:
				try:
					data_result = convert_data_result_to_string(self.last_GET_status)
				except Exception:
					data_result = convert_data_result_to_string(cosemAccessResult.other_reason)
		return data_result

	def get_profile_record_by_date_time(self, obis_code, from_time, to_time):
		result = self.get_cosem_data(7, obis_code, 2, [1, [from_time, to_time]], False)
		return result

	def get_profile_record_by_idx(self, obis_code, record_idx):
		result = self.get_cosem_data(7, obis_code, 2, [2, [record_idx, record_idx, 1, 0]], False)
		return result

	def get_specific_data_in_record(self, obis_code, record_idx, data_idx):
		result = self.get_cosem_data(7, obis_code, 2, [2, [record_idx, record_idx, data_idx, data_idx]], False)
		return result

	def send_set_req_buffer(self, req_buffer, is_unconfirmed = False):
		req_buffer = self.hdlc.getTxInformationField(req_buffer)
		seg_bit = segmentBit.SB_OFF
		if len(self.hdlc.tx_segmented_info) > 0:
			seg_bit = segmentBit.SB_ON
		if is_unconfirmed:
			response_buff = self.hdlc.getTxHdlcFrame(req_buffer, seg_bit, self.dest_addr, self.src_addr, controlType.UI, controlType.UI, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		else:	
			response_buff = self.hdlc.getTxHdlcFrame(req_buffer, seg_bit, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		if not is_unconfirmed:
			self.increment_S()
		self.send_msg(response_buff)

	def read_set_resp_buffer(self):
		is_answered = True
		set_resp_progress = True
		check = self.read_msg()
		if check == frameError.NO_ERROR:
			if self.hdlc.getControlType() == controlType.RR:
				self.send_tx_remaining_info_frame()
			elif self.hdlc.getControlType() == controlType.INFO:
				set_resp_progress = False
		if check == None:
			is_answered = False
			set_resp_progress = False
		if len(self.hdlc.rx_frameInfo) > 3:
			frame_to_process = self.hdlc.rx_frameInfo[3:]
		else:
			frame_to_process = []
		return is_answered, set_resp_progress, frame_to_process

	def set_cosem_data(self, class_id, obis_code, att_id, dtype, value, is_note = False):
		result = None
		if self.is_connected:
			set_buffer, remaining_buff = self.dlms.get_SET_REQ_frame(ServiceTag.SET_REQUEST_NORMAL, class_id, obis_code, att_id, dtype, value)
			if len(set_buffer) > self.max_apdu_size:
				set_buffer, remaining_buff = self.dlms.get_SET_REQ_frame(ServiceTag.SET_REQUEST_FIRST_DATABLOCK, class_id, obis_code, att_id, dtype, value)
			self.send_set_req_buffer(set_buffer)
			self.remain_set_buff = remaining_buff
			set_resp_progress = True
			is_answered = True
			frame_to_process = []
			while set_resp_progress:
				is_answered, set_resp_progress, frame_to_process = self.read_set_resp_buffer()
			if is_answered:
				is_finish, result = self.dlms.check_SET_RESP_frame(frame_to_process)
				if not is_finish:
					while len(self.remain_set_buff) > 0:
						set_buffer, remaining_buff = self.dlms.get_SET_REQ_frame(ServiceTag.SET_REQUEST_DATABLOCK, class_id, obis_code, att_id, dtype, self.remain_set_buff)
						self.send_set_req_buffer(set_buffer)
						self.remain_set_buff = remaining_buff
						set_resp_progress = True
						is_answered = True
						while set_resp_progress:
							is_answered, set_resp_progress, frame_to_process = self.read_set_resp_buffer()
						if is_answered:
							is_finish, result = self.dlms.check_SET_RESP_frame(frame_to_process)
							if is_finish:
								break
						else:
							result = cosemAccessResult.other_reason
							break
			else:
				result = cosemAccessResult.other_reason
		else:
			result = cosemAccessResult.other_reason
		if is_note:
			set_result = convert_data_result_to_string(result)
			note_result = "SET RESULT of attribute %s of %s is %s" %(att_id, obis_code, set_result)
			result = note_result
		return result

	def set_cosem_data_unconfirmed(self, class_id, obis_code, att_id, dtype, value):
		set_buffer, _ = self.dlms.get_SET_REQ_frame(ServiceTag.SET_REQUEST_NORMAL, class_id, obis_code, att_id, dtype, value)
		self.send_set_req_buffer(set_buffer, True) # no need to check response in set unconfirmed

	def send_act_req_buffer(self, req_buffer, is_unconfirmed = False):
		req_buffer = self.hdlc.getTxInformationField(req_buffer)
		seg_bit = segmentBit.SB_OFF
		if len(self.hdlc.tx_segmented_info) > 0:
			seg_bit = segmentBit.SB_ON
		if is_unconfirmed:
			response_buff = self.hdlc.getTxHdlcFrame(req_buffer, seg_bit, self.dest_addr, self.src_addr, controlType.UI, controlType.UI, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		else:
			response_buff = self.hdlc.getTxHdlcFrame(req_buffer, seg_bit, self.dest_addr, self.src_addr, controlType.INFO, controlType.INFO, self.counter_R, self.counter_S, pollFinalBit.PF_ON)
		if not is_unconfirmed:
			self.increment_S()
		self.send_msg(response_buff)

	def read_act_resp_buffer(self):
		is_answered = True
		act_resp_progress = True
		check = self.read_msg()
		if check == frameError.NO_ERROR:
			if self.hdlc.getControlType() == controlType.RR:
				self.send_tx_remaining_info_frame()
			elif self.hdlc.getControlType() == controlType.INFO:
				act_resp_progress = False
		if check == None:
			is_answered = False
			act_resp_progress = False
		return is_answered, act_resp_progress

	def act_cosem_data(self, class_id, obis_code, mtd_id, dtype, param, is_note = False):
		result = None
		is_success = True
		if self.is_connected:
			act_req_buff = self.dlms.get_ACT_REQ_frame(class_id, obis_code, mtd_id, dtype, param)
			self.send_act_req_buffer(act_req_buff)
			act_resp_progress = True
			is_answered = True
			while act_resp_progress:
				is_answered, act_resp_progress = self.read_act_resp_buffer()
			if is_answered:
				result, opt_data = self.dlms.check_ACT_RESP_frame(self.hdlc.rx_frameInfo)
		else:
			result = cosemAccessResult.other_reason
		if result != cosemAccessResult.success:
			is_success = False
		if is_note:
			act_result = convert_data_result_to_string(result)
			note_result = "ACT RESULT of method %s of %s is %s" %(mtd_id, obis_code, act_result)
			result = note_result
		else:
			result = is_success
		return result

	def act_cosem_data_unconfirmed(self, class_id, obis_code, mtd_id, dtype, param):
		act_buffer = self.dlms.get_ACT_REQ_frame(class_id, obis_code, mtd_id, dtype, param)
		self.send_act_req_buffer(act_buffer, True) # no need to check response in set unconfirmed