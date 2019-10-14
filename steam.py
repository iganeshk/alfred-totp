#!/usr/env/python3
# coding=utf-8
#
# Generate Steamguard OTP with the shared secret passed as an arguemtn
# Ganesh Velu 

import hmac
import base64
import hashlib
import codecs
import time
import sys

STEAM_DECODE_CHARS = ['2', '3', '4', '5', '6', '7', '8', '9',
                      'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                      'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                      'X', 'Y']

def get_authentication_code(secret):
    msg = bytes.fromhex(('%016x' % int(time.time() // 30)))
    key = base64.b64decode(secret)
    auth = hmac.new(key, msg, hashlib.sha1)
    digest = auth.digest()
    start = digest[19] & 0xF
    code = digest[start:start + 4]
    auth_code_raw = int(codecs.encode(code, 'hex'), 16) & 0x7FFFFFFF

    auth_code = []
    for i in range(5):
        auth_code.append(STEAM_DECODE_CHARS[int(auth_code_raw % len(STEAM_DECODE_CHARS))])
        auth_code_raw /= len(STEAM_DECODE_CHARS)

    return ''.join(auth_code)

if __name__ == '__main__':
    print(get_authentication_code(sys.argv[1]), end='')