from .security_util import mechanism, sc_byte
from .algo_aes_gcm import toHexList, encrypt, decrypt, verify_GMAC
from .algo_aes_ecb import encrypt_aes128, verify_HLS2
import os

class DlmsSecurity:
    def __init__(self):
        self.invoc_counter = 0
        self.CtoS = None
        self.StoC = None

    def conv_string_to_hex_list(self, val):
        conv_val = []
        for i in range(0,len(val),2):
            conv_val.append(int(val[i]+val[i+1], 16))
        return conv_val

    def reset_security_component(self):
        self.invoc_counter = 0
        self.CtoS = None
        self.StoC = None

    def set_invoc_counter(self, val):
        self.invoc_counter = val

    def get_byte_IC(self, invoc_count):
        buff = []
        buff.append(int((invoc_count & 0xFF000000) >> 24))
        buff.append(int((invoc_count & 0x00FF0000) >> 16))
        buff.append(int((invoc_count & 0x0000FF00) >> 8))
        buff.append(int(invoc_count & 0x000000FF))
        return buff

    def generate_challenge(self, num_of_byte):
        return toHexList(os.urandom(num_of_byte))

    def set_CtoS(self, val):
        self.CtoS = val

    def set_StoC(self, val):
        self.StoC = val

    def encrypt_apdu(self, sc_byte_req, GUEK, GAK, sys_T, buffer):
        sc_byte_req = [sc_byte_req]
        buff_IC = self.get_byte_IC(self.invoc_counter)
        chiper_text = sc_byte_req + buff_IC + encrypt(GUEK, GAK, sc_byte_req, sys_T, buff_IC, buffer)
        self.invoc_counter += 1
        return chiper_text

    def decrypt_apdu(self, GUEK, GAK, sys_T, buffer):
        result_text = None
        resp_sc_byte = [buffer[0]]
        meter_IC = buffer[1:5]
        if resp_sc_byte[0] & 0x30 == sc_byte.NO_SECURITY:
            result_text = buffer[5:]
        else:
            if resp_sc_byte[0] & 0x30 == sc_byte.ENCRYPT_ONLY:
                chipered_text = buffer[5:]
                tag = []
            else:
                chipered_text = buffer[5:-12]
                tag = buffer[-12:]
            is_ok, result_text = decrypt(GUEK, GAK, resp_sc_byte, sys_T,  meter_IC, chipered_text, tag)
            # if not is_ok:
            #     print("DECRYPT FAILED")
        if not is_ok:
            result_text = None
        return result_text
    
    def construct_HLS_Pass3(self, auth_mech, sys_TC, sys_TS, sec_param, force_false=False):
        buff = []
        if auth_mech == mechanism.HIGH_LEVEL:
            buff = encrypt_aes128(sec_param, self.StoC)
        elif auth_mech == mechanism.HIGH_LEVEL_GMAC:
            buff_IC = self.get_byte_IC(self.invoc_counter)
            sc_byte = [sec_param[0]]
            GUEK = sec_param[1]
            GAK = sec_param[2]
            buff = sc_byte + buff_IC
            if force_false:
                gmac = encrypt(GUEK, GAK, sc_byte, sys_TC, buff_IC, self.CtoS)
            else:
                gmac = encrypt(GUEK, GAK, sc_byte, sys_TC, buff_IC, self.StoC)
            buff = buff + gmac[-12:]
            self.invoc_counter += 1
        return buff

    def verify_HLS_Pass4(self, auth_mech, sys_TC, sys_TS, sec_param, buffer):
        verified = False
        if auth_mech == mechanism.HIGH_LEVEL_GMAC:
            sc_byte = [buffer[0]]
            buff_IC = buffer[1:5]
            in_tag = buffer[-12:]
            GUEK = sec_param[0]
            GAK = sec_param[1]
            verified = verify_GMAC(GUEK, GAK, sc_byte, sys_TS, buff_IC, in_tag, self.CtoS)
        elif auth_mech == mechanism.HIGH_LEVEL:
            verified = verify_HLS2(sec_param, buffer, self.CtoS)
        return verified