from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

def toHexList(byteVal):
    hexList = []
    for val in byteVal:
        # hexList.append(ord(val))
        # fix for python3 usage
        hexList.append(int(val))
    return hexList

def toByteStr(listVal):
    byteStr = ""
    for val in listVal:
        byteStr += (chr(val))
    return byteStr

def encrypt_aes128(key, plain_text):
    key = bytes(key)
    plain_text = bytes(plain_text)
    iv = 16 * b'\0'
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    ).encryptor()

    return toHexList(encryptor.update(plain_text) + encryptor.finalize())

def verify_HLS2(key, proc_clg, clg):
    key = bytes(key)
    plain_text = bytes(clg)
    iv = 16 * b'\0'
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    ).encryptor()
    enc_clg = toHexList(encryptor.update(plain_text) + encryptor.finalize())
    return (enc_clg == proc_clg)