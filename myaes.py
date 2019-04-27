#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
class MYAES():
    def __init__(self,key=None,iv=None,mode='CBC'):
        if key is None:
            self.key="hi_O/*GK{o)bAL4V"
        else:
            self.key=self.keep_key(key)
            print(self.key)
        if iv is None:
            self.iv="AYibBtn$CDNUO&="
        else:
            self.iv=iv
        if mode.upper()=="CBC":
            self.mode=AES.MODE_CBC
        elif mode.upper()=="ECB":
            self.mode=AES.MODE_ECB
        else:
            self.mode=None
            print("AES加密模式设置错误！")
        pass
    def keep_key(self,text):
        if len(text)<=8:text=text+'0'*8
        if len(text.encode('utf-8')) % 8:
            add = 8 - (len(text.encode('utf-8')) % 8)
        else:
            add = 0
        text = text + ('0' * add)
        if len(text)>32:text=text[:32]
        return text
    def add_to_16(self,text):
        if len(text.encode('utf-8')) % 16:
            add = 16 - (len(text.encode('utf-8')) % 16)
        else:
            add = 0
        text = text + ('\0' * add)
        return text.encode('utf-8')
    def encrypt_ecb(self,text):
        key = self.key.encode('utf-8')
        mode = AES.MODE_ECB
        text = self.add_to_16(text)
        cryptos = AES.new(key, mode)
        cipher_text = cryptos.encrypt(text)
        return b2a_hex(cipher_text).decode('utf-8')
    def decrypt_ecb(self,text):
        key = self.key.encode('utf-8')
        mode = AES.MODE_ECB
        cryptor = AES.new(key, mode)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip('\0')
    def encrypt_cbc(self,text):
        key = self.key.encode('utf-8')
        iv = self.iv.encode('utf-8')
        mode = AES.MODE_CBC
        text = self.add_to_16(text)
        cryptos = AES.new(key, mode, iv)
        cipher_text = cryptos.encrypt(text)
        return b2a_hex(cipher_text).decode('utf-8')
    def decrypt_cbc(self,text):
        key = self.key.encode('utf-8')
        iv = self.iv.encode('utf-8')
        mode = AES.MODE_CBC
        cryptos = AES.new(key, mode, iv)
        plain_text = cryptos.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip('\0')
    def encrypt(self,text):
        if self.mode==AES.MODE_ECB:
            return self.encrypt_ecb(text)
        elif self.mode==AES.MODE_CBC:
            return self.encrypt_cbc(text)
        else:
            return text
    def decrypt(self,text):
        if self.mode==AES.MODE_ECB:
            return self.decrypt_ecb(text)
        elif self.mode==AES.MODE_CBC:
            return self.decrypt_cbc(text)
        else:
            return text
if __name__ == '__main__':
    myaes=MYAES(key='sjhflis;eltja;lksjdf;lkaihwihhriqwpoeiyt;sa;fsn;ds',mode='ecb')
    s='中文测试明文字符串this is a test string'
    e = myaes.encrypt(s)  
    print("加密:", e)
    d = myaes.decrypt(e)  
    print("解密:", d)
    print('key',myaes.key)