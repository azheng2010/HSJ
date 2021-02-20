#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from m2m import e2e
from mitmproxy import ctx
from configparser import ConfigParser
from comm import path0,confpath
from comm import getip, boxmsg
from comm import base64decode as bde
import logger
import threading
class Hsj_Addon:
    def __init__(self):
        self.heartbeat_span=180
        self.logger = logger.logger(set_level='debug')
        self.mitm_msg_formater = self.read_mitm_msg_formater()
        self.read_config()
    def read_config(self):
        self.conf = ConfigParser()
        self.conf.read(confpath + 'default.ini', encoding='utf-8')
        self.user = self.conf.get('UserInf', 'user')
        self.username=self.conf.get('UserInf', 'username')
    def read_mitm_msg_formater(self):
        with open(path0 + 'conf/Msg_Formater.conf', mode='r', encoding='utf-8') as (f):
            t = bde(f.read())
        return t
    def record_msg(self, flow):
        h_lst = [] 
        for h in flow.request.headers:
            h_lst.append('%s : %s' % (h, flow.request.headers[h]))
        t = self.mitm_msg_formater.format(m=flow.request.method,
                                          u=flow.request.url,
                                          h=('\n').join(h_lst),
                                          d=flow.request.text,
                                          r=flow.response.text)
        self.logger.info('\n' + t)
    def response(self, flow):
        if 'hushijie.com' in flow.request.host:
            self.record_msg(flow)
def heartbeat(addon):
    num=0
    while num<20:
        time.sleep(addon.heartbeat_span)
        print('=========%s HeartBeat========'%addon.heartbeat_span)
        e2e('数据_%s_%s' % (addon.user,addon.username),
            '抓包数据',fps=[addon.logger.log_file_path])
        num+=1
ips = getip()
ctx.log.info(('局域网IP：[{ip}]').format(ip=(' , ').join(ips)))
ctx.log.info('请在另一台手机上设置http代理')
txt = ('server:{ip}\nport:{port}').format(ip=(' | ').join(ips), port=8080)
ctx.log.info(boxmsg(txt, CN_zh=False))
addons = [ Hsj_Addon()]
t = threading.Thread(target=heartbeat,args=(addons[0],))
t.start()