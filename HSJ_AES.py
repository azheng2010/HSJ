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
        amount_to_pad = AES.block_size - text_length % AES.block_size
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad
    def __unpad(self, text):
        pad = ord(text[-1])
        return text[:-pad]
    def encrypt(self, raw):
        raw2 = self._AESCipher__pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        r=base64.b64encode(cipher.encrypt(raw2))
        return self.base64encode(r.decode()).encode()
    def decrypt(self, enc):
        enc=self.base64decode(enc)
        enc2 = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._AESCipher__unpad(cipher.decrypt(enc2).decode('utf-8'))
    def base64encode(self,txt):
        enb64=base64.b64encode(txt.encode())
        en64=enb64.decode()
        return en64
    def base64decode(self,en64):
        if type(en64) is bytes:en64=en64.decode()
        btxt=base64.b64decode(en64.encode())
        txt=btxt.decode()
        return txt
if __name__ == '__main__':
    e = AESCipher()
    secret_data = e.base64encode("中文")
    enc_str = e.encrypt(secret_data)
    print('enc_str: ' + enc_str.decode())
    dec_str = e.decrypt(enc_str)
    dec_str=e.base64decode(dec_str)
    print('dec str: ' + dec_str)
    pass