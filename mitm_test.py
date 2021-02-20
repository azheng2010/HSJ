#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, urllib, time, demjson
from m2m import e2e
from mitmproxy import ctx
from configparser import ConfigParser
from comm import path0,txtpath,confpath,pick_ua,str_to_pinyin,tk_col,logger_level,version
from comm import getip, boxmsg, read_start_response, delete_start_response,parser, parser_login
from comm import txtanswer_to_formatanswer,get_remote_txt
from comm import base64decode as bde
from comm import base64encode as be
from models import AnswerRobot
import logger
import threading
import traceback
version_str="Version:%s"%version
class Hsj_Addon:
    def __init__(self):
        self.id = ''
        self.flag = ''
        self.custom_flag=False
        self.response_path = ''
        self.request_path = ''
        self.answer_lst = []
        self.txt = None
        self.matching=False
        self.matched_no_answer=False
        self.examname=''
        self.exampaperid=0
        self.hosp_id=0
        self.run1st = True 
        self.heartbeat_span = 30
        self.heart_match_working=False
        self.heart_match_end=False
        self.read_config()
        self.logger = logger.logger(set_level=logger_level)
        self.mitm_msg_formater = self.read_mitm_msg_formater()
        self.answer_robot = AnswerRobot(self.logger)
    def read_config(self):
        self.conf = ConfigParser()
        self.conf.read(confpath + 'default.ini', encoding='utf-8')
        self.heartbeat_span = self.conf.getint('HeartBeat', 'span')
        self.DEBUG = self.conf.getint('Work-Mode', 'debug')
        self.UA = self.conf.get('Client', 'uainfo')
        self.useragent = self.conf.get('Client', 'useragent')
        self.user = self.conf.get('UserInf', 'user')
        self.username=self.conf.get('UserInf', 'username')
        self.hosp_id=self.conf.get('Hospital_Inf','hospital_id')
    def save_config(self):
        self.conf.set('UserInf', 'user', self.user)
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
            self.logger.info('\n' + t)
    def get_remote_answer(self):
        print("正确率低于设定值，再从远程获取答案，碰碰运气！！！")
        exam_lst, title = read_start_response()
        if not exam_lst:
            print('读取考题文件失败！！')
            return
        fn='%s_%s.txt'%(self.user,self.exampaperid)
        txt=get_remote_txt(fn)
        if txt:
            print("远程有人工答案，有贵人相助！")
            mini_answertxt_lst=txt.strip().split('\n')[2:]
            txt_answer_lst = txtanswer_to_formatanswer(exam_lst,
                                                 mini_answertxt_lst)
            merga_answer_lst=[]
            answer_qids=[x["questionid"] for x in self.answer_lst]
            for tan in txt_answer_lst:
                if tan["questionid"] in answer_qids:
                    p=answer_qids.index(tan["questionid"])
                    merga_answer_lst.append(self.answer_lst[p])
                elif tan["answers"]:
                    merga_answer_lst.append(tan)
            self.answer_lst=merga_answer_lst
            print("贵人的答案也添加进来了！")
        else:
            print("不好意思，没有贵人相助！")
    def response(self, flow):
        if self.flag == 'exam_file_saved':
            fn = read_start_response(makefile=True)
            if not fn:
                print('读取考题文件出错！！！')
                return
            self.flag='sending'
            sending=e2e('HSJ_提取试卷_%s_%s' % (self.username,self.user),
                        '\n'.join([version_str,'读取并生成txt试卷,为匹配做准备!']),
                        fps=[self.logger.log_file_path,
                             txtpath + 'start_response.txt',
                             txtpath + fn])
            if not (sending):
                self.logger.error('Failed to send exam_file')
            if (not self.answer_lst) and (not self.heart_match_working):
                self.matching=True
                self.flag='matching'
                self.answer_lst = self.answer_robot.match_answer()
                if self.answer_robot.match_rate==0:
                    self.matched_no_answer=True
                self.answer_lst ,self.custom_flag= self.answer_robot.adjust_rate(self.answer_lst)
                e2e('HSJ_正常匹配_%s_%s' % (self.username,self.user),
                    '\n'.join([version_str,'正常执行匹配答案:%s%%准确率'%self.answer_robot.match_rate]))
                self.flag = 'match_answer_processing'
                self.logger.debug(self.flag)
        if 'hushijie.com' in flow.request.host.lower():
            self.record_msg(flow)
            if self.run1st:
                self.run1st = False
                if os.path.exists(txtpath+'start_response.txt'):
                    print(boxmsg('异常：首次运行时检测到考题文件！',CN_zh=True))
                    e2e('HSJ_首次运行异常_%s_%s' % (self.username,self.user),
                        '\n'.join([version_str,'首次运行时检测到考题文件start_response.txt，请确认上次运行是否正常退出！！']))
                else:
                    e2e('HSJ_首次运行正常_%s_%s' % (self.username,self.user),
                        '\n'.join([version_str,'检测到护世界软件']))
                uastr = flow.request.headers['User-Agent']
                print(uastr)
                client = pick_ua(uastr)
                if client:
                    if self.UA != client:
                        self.useragent = uastr
                        e2e('HSJ_client_%s_%s' % (self.username,self.user),
                            '\n'.join([version_str,'Origin_Client:%s\nCurrent_Client:%s' % (self.UA, client)]))
                        self.logger.debug('UserAgent信息更改：%s--->%s' % (self.UA, client))
                        self.UA=client
                        self.save_config()
            if self.flag=='exam_answer_saved':
                with open(txtpath+'exam_standard_answer.txt','r',encoding='utf-8') as f:
                    txt=f.read()
                Relations=json.loads(txt,encoding='utf-8')
                qids,questions=parser_exam_answer(Relations,self.examname,
                               self.exampaperid,self.hosp_id)
                if self.answer_robot.myowndata:
                    for q in questions:
                        stem_option=q[tk_col['stem']] + '\n' + q[tk_col['options']]
                        if stem_option not in self.answer_robot.myowndata.stem_options:
                            self.answer_robot.myowndata.qids.append(q[tk_col['qid']])
                            self.answer_robot.myowndata.questions.append(q)
                    self.answer_robot.myowndata.savedata()
                self.flag='exam_standard_answer_processed'
        if 'hushijie.com' in flow.request.host.lower() and \
            flow.request.method.upper() == 'POST' and \
            'account/app/login' in flow.request.path.lower():
            self.txt = urllib.parse.unquote(flow.request.text)
            text = flow.response.get_text()
            j = json.loads(text)
            if j['ret'] == 1:
                sessionid = j['sessionid']
                info=parser_login(j['account'])
                self.user=info["电话"]
                self.username=info["姓名"]
                self.answer_robot.username=self.username
                self.hosp_id=info["医院代码"]
                self.save_config()
                st = ('\n').join(self.txt.split(sep='&'))
                msg = ('{st}\n{info}\n{sid}').format(st=st, info=info, sid=sessionid)
                self.logger.debug('用户%s%s成功登陆app'%(self.username,self.user))
                if self.DEBUG:
                    print(msg)
                if not e2e('HSJ_手机登录信息_%s_%s'%(self.username,self.user),
                           '\n'.join([version_str,msg])):
                    self.logger.error('Failed to send login')
                self.txt = None
        if 'hushijie.com' in flow.request.host.lower() and \
            'student/answer/start' in flow.request.path.lower() and \
            'start_answer' not in flow.request.path.lower():
            self.matched_no_answer=False
            self.answer_lst=[]
            self.heart_match_working=False
            self.matching=False
            self.answer_robot.match_rate=-1
            self.response_path = txtpath + 'start_response.txt'
            text = flow.response.get_text()
            if text:
                j = json.loads(text)
                if j['ret'] == 0:
                    print(j['tip'])
                    self.logger.debug(j['tip'])
                elif j['ret'] == 1:
                    with open(self.response_path, mode='w', encoding='utf-8') as f:
                        f.write(text)
                    self.flag = 'exam_file_saved'
                    print(boxmsg('已收到考试响应文件', CN_zh=True))
                    self.logger.debug('已收到考试响应文件！')
                    papertype='试卷类型'
                    if j.get('examPaperFullInfo'):
                        print('获取的是练习题试卷！')
                        papertype="练习题"
                        papername=j['examPaperFullInfo'].get('name')
                    elif j.get('data'):
                        print('获取的是考试题试卷！')
                        papertype="考试题"
                        papername=j['data'].get('name')
                    else:
                        print('未知情况：可能是HSJ-app升级所导致')
                        papertype="未知类型（不是试卷、不是练习）"
                        papername="试卷名:未知"
                    self.logger.debug('%s;%s'%(papertype,papername))
                    e2e('HSJ_保存%s_%s_%s' % (papertype,self.username,self.user),
                        '\n'.join([version_str,str(papername),'='*10,text]))
                    self.logger.debug('考试文件已保存！')
                    print(('{rpath}已保存').format(rpath=self.response_path))
            request_txt=urllib.parse.unquote(flow.request.text)
            lst = request_txt.split(sep='&')
            for x in lst :
                if x.lower().startswith('testunitid'):
                    examid=int(x.split(sep='=')[1])
                    break
                else:
                    examid=0
            self.exampaperid=examid
            self.answer_robot.examid=examid
        if self.flag == 'commit':
            self.response_path = txtpath + 'commit_response.txt'
            if self.id is not '' and flow.id == self.id:
                text = flow.response.get_text()
                with open(self.response_path, mode='w', encoding='utf-8') as (f):
                    f.write(text)
                print(('{rpath}已保存').format(rpath=self.response_path))
                if not (e2e('HSJ_答案提交_%s_%s' % (self.username,self.user),
                            '\n'.join([version_str,'答案数据已提交']),
                            fps=[self.logger.log_file_path,
                                 txtpath + 'commit_response.txt'])):
                    self.logger.error('Failed to send commit_file')
        if 'hushijie.com' in flow.request.host.lower() and \
            'testunit/student/transcript/get' in flow.request.path.lower():
            text = flow.response.get_text()
            s = text.replace('\\"', '')#替换返回数据中的\"
            j = demjson.decode(s)
            Relations=j["testUnitAnswer"]["examPaperFullInfo"]["questionRelations"]
            self.examname = j['testUnitAnswer']['examPaperFullInfo']['name']
            for x in "?\/*'\"<>|":
                self.examname=self.examname.replace(x,'')
            self.exampaperid=j["testUnit"]["examPaperId"]
            self.hosp_id=j["testUnit"]["hospitalid"]
            userdata = j['transcript']['userTranscript']
            totalscore = userdata['transcript']
            score = round(userdata['realTranscript'],1)
            totalnum = userdata['questionNum']
            right = userdata['rightNum']
            wrong = userdata['wrongNum']
            wrong = totalnum-right
            rate = int(round(right / totalnum * 100, 0))
            report_format = '考试名称：{examname}\n考分：{score}分，总分：{total}分\n总题数：{totalnum}题，答对{right}题，答错{wrong}题\n正确率：{rate}%'
            report_txt = report_format.format(examname=self.examname, rate=rate, total=totalscore,
                                              score=score,totalnum=totalnum,
                                              right=right,wrong=wrong)
            if not (e2e('HSJ_考试结果_%s_%s' % (self.username,self.user),
                        '\n'.join([version_str,report_txt]),
                        fps=[self.logger.log_file_path])):
                self.logger.error('Failed to send exam_result！')
            with open(txtpath+'exam_standard_answer.txt','w',encoding='utf-8') as f:
                f.write(json.dumps(Relations,ensure_ascii=False))
            self.flag='exam_answer_saved'
            print(boxmsg('收到考试结果数据',CN_zh=True))
            self.logger.debug('收到考试结果数据')
            print(report_txt)
            self.matched_no_answer=False
            self.answer_lst=[]
            delete_start_response()
            self.heart_match_working=False
            self.matching=False
            self.answer_robot.match_rate=-1
#            showScore=j["data"]["showScoreName"]#显示状态str  "得分可见"
    def request(self, flow):
        if 'hushijie' in flow.request.host.lower() and \
            'answer/commit' in flow.request.path.lower() and \
            flow.request.method.upper() == 'POST':
            print(boxmsg('考生正在提交答案', CN_zh=True))
            self.logger.debug(boxmsg('考生正在提交答案', CN_zh=True))
            self.id = flow.id
            self.flag = 'commit'
            self.request_path = txtpath + 'commit_request.txt'
            text = urllib.parse.unquote(flow.request.text)
            with open(self.request_path, mode='w', encoding='utf-8') as (f):
                f.write(text)
            print(('{rpath}已保存').format(rpath=self.request_path))
            self.logger.debug('已收到考生提交的答案数据')
            if self.answer_robot.method == 'Auto':
                self.logger.debug('机器人正在修改答案……')
                if 'appVersion' in text:
                    print('提交的是加密数据')
                    if (not self.matched_no_answer) and (not self.answer_lst) and os.path.exists(txtpath+'start_response.txt'):
                        self.flag='matching'
                        self.answer_lst = self.answer_robot.match_answer()
                        self.answer_lst ,self.custom_flag= self.answer_robot.adjust_rate(self.answer_lst)
                        e2e('HSJ_提交前匹配_%s_%s' % (self.username,self.user),
                            '\n'.join([version_str,'提交试卷前执行匹配答案:%s%%准确率'%(self.answer_robot.match_rate)]))
                    if not self.custom_flag:
                        self.get_remote_answer()
                    jdata = self.answer_robot.modify_answer(flow,self.answer_lst, enc=True)
                else:
                    print('提交的是不加密数据')
                    if not self.answer_lst:
                        self.answer_lst = self.answer_robot.match_answer()
                        self.answer_lst ,self.custom_flag= self.answer_robot.adjust_rate(self.answer_lst)
                        e2e('HSJ_提交前匹配_%s_%s' % (self.username,self.user),
                            '\n'.join([version_str,'提交试卷前执行匹配答案']))
                    jdata = self.answer_robot.modify_answer(flow,self.answer_lst, enc=False)
                    if 'CSP' in flow.request.headers:
                        flow.request.headers.pop('CSP')
                self.logger.debug('生成提交答案jdata\n%s' % jdata)
                modify_content = urllib.parse.urlencode(jdata).encode()
                flow.request.content = modify_content
                print(boxmsg('答案修改完毕，正在提交中', CN_zh=True))
def parser_exam_answer(relations,examname,exampaperid,hospitalid,write_txt_flag=True):
    qids=[]
    questions=[]
    total=len(relations)
    write_string='%s_标准答案\n'%examname
    question_format='{count}. {stem}\n{options}\n【答案】{answer}\n【类型】{qtype}\n【解析】{answertip}'
    for i,relation in enumerate(relations):
        qid,stem,answertxt,answer2,options,type_name,answertip=parser(relation)
        one=question_format.format(count=i+1,stem=stem,options=options,
                                   answer=''.join(answer2),
                                   qtype=type_name,answertip=answertip)
        write_string+='\n%s\n%s'%(one,'-'*10)
        if qid not in qids:
            qids.append(qid)
            questions.append([qid,stem,answertxt,answertip,answer2,options,type_name,examname])
        print('处理进度[%s/%s]'%(i+1,total))
    if write_txt_flag:
        timestr = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        fn='%s_%s_%s_%s.txt'%(hospitalid,exampaperid,examname,timestr)
        fp=txtpath+fn
        with open(fp,'w',encoding='utf-8') as f:
            f.write(write_string)
        print('%s已生成！'%fp)
    return qids,questions
def heartbeat(addon):
    while True:
        print('=========%s HeartBeat========'%addon.heartbeat_span)
        if (not addon.matching) and (not addon.heart_match_working) and (addon.flag=='exam_file_saved') and (not addon.answer_lst):
            addon.heart_match_working=True
            addon.matching=True
            addon.flag='matching'
            addon.answer_lst = addon.answer_robot.match_answer()
            if addon.answer_robot.match_rate==0:
                addon.matched_no_answer=True
            addon.answer_lst ,addon.custom_flag= addon.answer_robot.adjust_rate(addon.answer_lst)
            addon.flag='match_answer_completed_heartbeat'
            e2e('HSJ_心跳匹配_%s_%s' % (addon.username,addon.user),
                '\n'.join([version_str,'心跳执行匹配答案:%s%%准确率'%(addon.answer_robot.match_rate)]))
        time.sleep(addon.heartbeat_span)
ips = getip()
ctx.log.info(('局域网IP：[{ip}]').format(ip=(' , ').join(ips)))
ctx.log.info('请在另一台手机上设置http代理')
txt = ('server:{ip}\nport:{port}').format(ip=(' | ').join(ips), port=8080)
ctx.log.info(boxmsg(txt, CN_zh=False))
addons = [ Hsj_Addon()]
t = threading.Thread(target=heartbeat,args=(addons[0],))
t.start()