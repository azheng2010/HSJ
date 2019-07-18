#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, urllib, time, demjson
from m2m import e2e
import mitmproxy.http
from mitmproxy import ctx
from configparser import ConfigParser
from comm import path0, txtpath, confpath, pick_ua, str_to_pinyin,tk_col
from comm import getip, boxmsg, read_start_response, delete_start_response,parser, parser_login
from comm import base64decode as bde
from comm import base64encode as be
from models import AnswerRobot
import logger
class Hsj_Addon:
    def __init__(self):
        self.id = ''
        self.flag = ''
        self.response_path = ''
        self.request_path = ''
        self.answer_lst = None
        self.txt = None
        self.examname=''
        self.run1st = True 
        self.read_config()
        self.logger = logger.logger()
        self.mitm_msg_formater = self.read_mitm_msg_formater()
        self.answer_robot = AnswerRobot(self.logger)
    def read_config(self):
        self.conf = ConfigParser()
        self.conf.read(confpath + 'default.ini', encoding='utf-8')
        self.DEBUG = self.conf.getint('Work-Mode', 'debug')
        self.UA = self.conf.get('Client', 'uainfo')
        self.useragent = self.conf.get('Client', 'useragent')
        self.user = self.conf.get('UserInf', 'user')
        self.username=self.conf.get('UserInf', 'username')
        self.hosp_id=self.conf.get('Hospital_Inf','hospital_id')
    def save_config(self):
        self.conf.set('Client', 'uainfo', self.UA)
        self.conf.set('Client','useragent',self.useragent)
        self.conf.set('UserInf', 'username',self.username)
        self.conf.set('Hospital_Inf','hospital_id',str(self.hosp_id))
        self.conf.write(open(confpath + 'default.ini', 'w',encoding='utf-8'))
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
        if self.DEBUG:
            self.logger.info('\n' + t)
        else:
            self.logger.info('\n' + be(t))
    def response(self, flow):
        if self.flag == 'exam_file_saved':
            self.flag = 'match_answer_processing'
            self.logger.debug(self.flag)
            fn = read_start_response(makefile=True)
            if not (e2e('HSJ_log_%s_%s' % (self.user,self.username), '考题文件已保存', 
                        fps=[self.logger.log_file_path,
                         txtpath + 'start_response.txt',
                         txtpath + fn])):
                self.logger.error('Failed to send exam_file')
            self.answer_lst = self.answer_robot.match_answer()
            self.answer_lst = self.answer_robot.adjust_rate(self.answer_lst)
        if 'hushijie.com' in flow.request.host:
            if self.run1st:
                uastr = flow.request.headers['User-Agent']
                print(uastr)
                client = pick_ua(uastr)
                self.run1st = False
                if self.UA != client:
                    self.useragent = uastr
                    e2e('HSJ_client_%s_%s' % (self.user,self.username), 
                        'Origin_Client:%s\nCurrent_Client:%s' % (self.UA, client))
                    self.logger.debug('UserAgent信息更改：%s--->%s' % (self.UA, client))
                    self.UA=client
                    self.save_config()
            if self.flag=='exam_answer_saved':
                with open(txtpath+'exam_standard_answer.txt','r',encoding='utf-8') as f:
                    txt=f.read()
                Relations=json.loads(txt,encoding='utf-8')
                qids,questions=parser_exam_answer(Relations,self.examname)
                for q in questions:
                    stem_option=q[tk_col['stem']] + '\n' + q[tk_col['options']]
                    if stem_option not in self.answer_robot.myowndata.stem_options:
                        self.answer_robot.myowndata.qids.append(q[tk_col['qid']])
                        self.answer_robot.add_data.qids.append(q[tk_col['qid']])
                        self.answer_robot.myowndata.questions.append(q)
                        self.answer_robot.add_data.questions.append(q)
                self.answer_robot.myowndata.savedata()
                self.answer_robot.add_data.savedata()
                self.flag='exam_standard_answer_processed'
            self.record_msg(flow)
        if 'hushijie.com' in flow.request.host and \
            'answer/start' in flow.request.path and \
            'start_answer' not in flow.request.path:
            self.response_path = txtpath + 'start_response.txt'
            text = flow.response.get_text()
            j = json.loads(text)
            if j['ret'] == 0:
                print(j['tip'])
                self.logger.debug(j['tip'])
            else:
                if j['ret'] == 1:
                    print(boxmsg('已收到考试响应文件', CN_zh=True))
                    self.logger.debug('已收到考试响应文件！')
                    with open(self.response_path, mode='w', encoding='utf-8') as (f):
                        f.write(text)
                    self.flag = 'exam_file_saved'
                    print(self.flag)
                    self.logger.debug('考试文件已保存！')
                    print(('{rpath}已保存').format(rpath=self.response_path))
        if self.flag == 'commit':
            self.response_path = txtpath + 'commit_response.txt'
            if self.id is not '' and flow.id == self.id:
                text = flow.response.get_text()
                with open(self.response_path, mode='w', encoding='utf-8') as (f):
                    f.write(text)
                print(('{rpath}已保存').format(rpath=self.response_path))
                if not (e2e('HSJ_log_%s_%s' % (self.user,self.username), '答案数据已提交', 
                            fps=[self.logger.log_file_path, txtpath + 'commit_response.txt'])):
                    self.logger.error('Failed to send commit_file')
                delete_start_response()
        if 'hushijie.com' in flow.request.host and \
            flow.request.method == 'POST' and \
            'account/app/login' in flow.request.path:
            self.txt = urllib.parse.unquote(flow.request.text)
            text = flow.response.get_text()
            j = json.loads(text)
            if j['ret'] == 1:
                sessionid = j['sessionid']
                info = parser_login(j['account'])
                self.username=info["姓名"]
                self.hosp_id=info["医院代码"]
                self.save_config()
                st = ('\n').join(self.txt.split(sep='&'))
                msg = ('{st}\n{info}\n{sid}').format(st=st, info=info, sid=sessionid)
                self.logger.debug('用户%s%s成功登陆app'%(self.user,self.username))
                if self.DEBUG:
                    print(msg)
                if not e2e('护世界_登录信息_%s_%s' % (self.user,self.username), msg):
                    self.logger.error('Failed to send login')
                self.txt = None
        if 'hushijie.com' in flow.request.host and \
            'testunit/student/transcript/get' in flow.request.path:
            text = flow.response.get_text()
            s = text.replace('\\"', '')#替换返回数据中的\"
            j = demjson.decode(s)
            Relations=j["testUnitAnswer"]["examPaperFullInfo"]["questionRelations"]
            self.examname = j['testUnitAnswer']['examPaperFullInfo']['name']
            userdata = j['transcript']['userTranscript']
            totalscore = userdata['transcript']
            score = userdata['realTranscript']
            totalnum = userdata['questionNum']
            right = userdata['rightNum']
            wrong = userdata['wrongNum']
            wrong = totalnum-right
            rate = int(round(right / totalnum * 100, 0))
            report_format = '考试名称：{examname}\n总分：{total}分，实际得分：{score}分\n总题数：{totalnum}题，答对{right}题，答错{wrong}题\n正确率：{rate}%'
            report_txt = report_format.format(examname=self.examname, rate=rate, total=totalscore,
                                              score=score,totalnum=totalnum,
                                              right=right,wrong=wrong)
            if not (e2e('HSJ_考试结果_%s_%s' % (self.user,self.username), report_txt, 
                        fps=[self.logger.log_file_path])):
                self.logger.error('Failed to send exam_result！')
            with open(txtpath+'exam_standard_answer.txt','w',encoding='utf-8') as f:
                f.write(json.dumps(Relations,ensure_ascii=False))
            self.flag='exam_answer_saved'
            print(boxmsg('收到考试结果数据',CN_zh=True))
            self.logger.debug('收到考试结果数据')
    def request(self, flow):
        if 'hushijie' in flow.request.host and \
            'commit' in flow.request.path and \
            flow.request.method == 'POST':
            print(boxmsg('考生正在提交答案', CN_zh=True))
            self.id = flow.id
            self.flag = 'commit'
            self.request_path = txtpath + 'commit_request.txt'
            text = urllib.parse.unquote(flow.request.text)
            with open(self.request_path, mode='w', encoding='utf-8') as (f):
                f.write(text)
            print(('{rpath}已保存').format(rpath=self.request_path))
            self.logger.debug('已收到考生提交的答案')
            if self.answer_robot.method == 'Auto':
                self.logger.debug('机器人正在修改答案……')
                if 'appVersion' in text:
                    print('提交加密数据')
                    if not self.answer_lst:
                        self.answer_lst = self.answer_robot.match_answer()
                        self.answer_lst = self.answer_robot.adjust_rate(self.answer_lst)
                    jdata = self.answer_robot.modify_answer(flow,
                      self.answer_lst, enc=True)
                else:
                    print('提交不加密数据')
                    if not self.answer_lst:
                        self.answer_lst = self.answer_robot.match_answer()
                        self.answer_lst = self.answer_robot.adjust_rate(self.answer_lst)
                    jdata = self.answer_robot.modify_answer(flow,
                      self.answer_lst, enc=False)
                    if 'CSP' in flow.request.headers:
                        flow.request.headers.pop('CSP')
                self.logger.debug('生成提交答案jdata\n%s' % jdata)
                modify_content = urllib.parse.urlencode(jdata).encode()
                flow.request.content = modify_content
                print(boxmsg('答案修改完毕，已提交答案', CN_zh=True))
def parser_exam_answer(relations,examname,write_txt_flag=True):
    qids=[]
    questions=[]
    total=len(relations)
    write_string='%s_标准答案\n'%examname
    question_format='{count}. {stem}\n{options}\n【答案】{answer}\n【类型】{qtype}\n【解析】暂无解析'
    for i,relation in enumerate(relations):
        qid,stem,answertxt,answer2,options,type_name=parser(relation)
        one=question_format.format(count=i+1,stem=stem,options=options,
                                   answer=''.join(answer2),
                                   qtype=type_name)
        write_string+='\n%s\n%s'%(one,'-'*10)
        if qid not in qids:
            qids.append(qid)
            stempinyin=str_to_pinyin(stem)
            questions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,examname])
        print('处理进度[%s/%s]'%(i+1,total))
    if write_txt_flag:
        timestr = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        fp=txtpath+'%s(标准答案)%s.txt'%(examname,timestr)
        with open(fp,'w',encoding='utf-8') as f:
            f.write(write_string)
        print('%s已生成！'%fp)
    return qids,questions
ips = getip()
ctx.log.info(('局域网IP：[{ip}]').format(ip=(' , ').join(ips)))
ctx.log.info('请在另一台手机上设置http代理')
txt = ('server:{ip}\nport:{port}').format(ip=(' | ').join(ips), port=8080)
ctx.log.info(boxmsg(txt, CN_zh=False))
addons = [ Hsj_Addon()]