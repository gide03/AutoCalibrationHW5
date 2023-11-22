from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from .security_util import sc_byte

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

def helper_encrypt(key, nonce, plaintext, associated_data):
    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (ciphertext + encryptor.tag[:12])

def helper_decrypt(key, nonce, ciphertext, associated_data, tag):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag, 12),
        backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    if tag != None:
        decryptor.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    if tag != None:
        decrypted_text = decryptor.update(ciphertext) + decryptor.finalize()
    else:
        decrypted_text = decryptor.update(ciphertext)
    return decrypted_text

def encrypt(EK, AK, SC, Sys_T, IC, plain_text):
    IV = Sys_T + IC
    # nonce = toByteStr(IV)
    # fix for python3 usage
    nonce = bytes(IV)
    data = []
    associate_data = []
    if SC[0] & 0x30 == sc_byte.AUTH_ONLY:
        # associate_data = toByteStr(SC+AK+plain_text)
        # fix for python3 usage
        associate_data = SC+AK+plain_text
    elif SC[0] & 0x30 == sc_byte.ENCRYPT_ONLY:
        # data = toByteStr(plain_text)
        # fix for python3 usage
        data = plain_text
    elif SC[0] & 0x30 == sc_byte.AUTH_ENCRYPT:
        # data = toByteStr(plain_text)
        # associate_data = toByteStr(SC+AK)
        # fix for python3 usage
        data = plain_text
        associate_data = SC+AK
    # encrypted_result = helper_encrypt(toByteStr(EK), nonce, data, associate_data)
    # fix for python3 usage
    encrypted_result = helper_encrypt(bytes(EK), nonce, bytes(data), bytes(associate_data))
    if SC[0] & 0x30 == sc_byte.AUTH_ONLY:
        encrypted_result = bytes(plain_text) + encrypted_result
    elif SC[0] & 0x30 == sc_byte.ENCRYPT_ONLY:
        encrypted_result = encrypted_result[:-12]
    encrypted_result = toHexList(encrypted_result)
    return encrypted_result

def decrypt(EK, AK, SC, Sys_T, IC, chipered_text, tag):
    IV = Sys_T + IC
    nonce = bytes(IV)
    data = []
    associate_data = []
    if SC[0] & 0x30 == sc_byte.AUTH_ONLY:
        associate_data = SC+AK+chipered_text
    elif SC[0] & 0x30 == sc_byte.ENCRYPT_ONLY:
        data = chipered_text
    elif SC[0] & 0x30 == sc_byte.AUTH_ENCRYPT:
        data = chipered_text
        associate_data = SC+AK
    is_tag_ok = True
    dechipered_msg = ""
    if len(tag) == 0:
        tag = None
    else:
        tag = bytes(tag)
    try:
        dechipered_msg = helper_decrypt(bytes(EK), nonce, bytes(data), bytes(associate_data), tag)
        if SC[0] & 0x30 == sc_byte.AUTH_ONLY:
            dechipered_msg = bytes(chipered_text)
        dechipered_msg = toHexList(dechipered_msg)
    except Exception:
        is_tag_ok = False
    return is_tag_ok, dechipered_msg

def verify_GMAC(EK, AK, SC, Sys_T, IC, in_gmac, challenge):
    IV = Sys_T + IC
    nonce = bytes(IV)
    data = []
    associate_data = bytes(SC+AK+challenge)
    is_tag_ok = True
    try:
        helper_decrypt(bytes(EK), nonce, bytes(data), associate_data, bytes(in_gmac))
    except Exception:
        # print("VERIFY ERROR")
        is_tag_ok = False
    return is_tag_ok