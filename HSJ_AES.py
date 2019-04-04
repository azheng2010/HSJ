#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
from Crypto.Cipher import AES
class AESCipher:
    def __init__(self):
        self.key = 'aedfb5ceaa834dbf' 
        self.iv = '2b2fd8747b3c4fa4' 
    def __pad(self, text):
        text_length = len(text)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad
    def __unpad(self, text):
        pad = ord(text[-1])
        return text[:-pad]
    def encrypt(self, raw):
        raw2 = self.__pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw2))
    def decrypt(self, enc):
        enc2 = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv )
        return self.__unpad(cipher.decrypt(enc2).decode("utf-8"))
if __name__ == '__main__':
    pass