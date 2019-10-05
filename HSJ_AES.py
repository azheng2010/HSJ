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
        btxt=base64.b64decode(en64.encode())
        txt=btxt.decode()
        return txt
if __name__ == '__main__':
    e = AESCipher()
    entxt="""RkpFUDV6dlBSbzVuek9sNVdBWm9oelJoa3NWSXBJZlI2TW1XYmxadTM3N3JFcm4xZmRxeTZQVlJBbW82Si9jbEJPUzVIQUdBYUV3NXhWUUUwNFdTMVFhTVhRSDNoQ0dxQTAvOEZkZlJJR0VUb2pMOXJlSUgvMVF1QTJoT3RRNmRaZTNlOUhpb0NWYlNyMUwydmthMkJmSEtWNFU5LzlGT0dWV2Z6cFpOWFBzVTl1UUtHWHpmMEc5a09NS3BRZzVzNFZmK0xzdTJOZzFNVUpzR3RoSEJZVVRZZ2NFY0xVMVdSTTZzblFuSVdmSTg1ZGk2allzN2ozQzR2M2hXc3F6Y1EremllaWRTVjdwcHpNUFZHMlZGeDhFSDlEZWw3K3ZtL295S1c5bEcySUQ1MzdoZ1lCWlNzaDg0TEs4MnIrOXhKTnMwM3VpM09WU24zZjNPLzRwY0VpRTBzVm5nZWp4QXNtQTRxS0RSR0w3UjJWSnhQd0pQQnBrNDh6cnpxYmgzQldDSmhHd0NCcEI2TkxOa2VzeGpZTTVjYU9sb0tCbU1yMVNvVEF1b1V4UDdRbndsSDR0NXdMQ1VkMk9kWVc5aTY2ME5EUkRxNktQSlF6dVlYSnlFeVJabTdhVnZacVBsTEI2dmhKdjdMTi9GUXpvajdlWS90U2xlR2tiYStmVVlDaURXaCtsQTZzWWZ0WmZqeHAwV0lTaUFqVWVUNmY1b1l4QTREbUJQbjBPa212S05yOW16VVRMbWdIelNmcWFGVFFFckNjOHJ1dDRvNUhHbVl5UUF0dkZCdTlOaHRLZ2h6YjV4NWdPZnBWVmI1U1J6VkYwdGt0YWlWMWFrU1pPVw=="""
    detxt=e.decrypt(entxt)
    print(detxt)
    pass