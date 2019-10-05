#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,time,csv,json,random,base64,urllib,configparser,platform,requests,demjson
import update
from pypinyin import lazy_pinyin
from subprocess import Popen
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from comm import path0, confpath, datapath, txtpath, boxmsg, tk_col
from comm import read_start_response, symb_options,get_dir_file,delete_files
from comm import parser,parser_course,parser_login,str_to_pinyin,version,urls
from comm import base64decode as bde
from comm import base64encode as be
from m2m import e2e
from HSJ_AES import AESCipher
from myaes import MYAES
from qiniuyun import MY_QINIU
myqny=MY_QINIU()
class AnswerRobot:
    def __init__(self, logger):
        self.logger = logger
        self.conf = configparser.ConfigParser()
        self.confpath = confpath + 'default.ini'
        self.readconfig()
        self.match_rate = 0
        self.qid = []
        self.sbqid = []
        self.sbstem = []
        self.sbwebdb = []
        self.sbwebpage = []
        self.notfound = []
        if self.OwnDataFlag:
            self.myowndata = Bumblebee(datafile='%s.data' % self.user, encrpt=True, debug=self.DEBUG)
        else:
            self.myowndata = None
        if self.ComDataFlag:
            self.mycommdata = Bumblebee(datafile='comm.data', encrpt=True, debug=self.DEBUG)
        else:
            self.mycommdata = None
        if self.WebDBFlag:
            self.mywebdb = DataCat(debug=self.DEBUG)
        else:
            self.mywebdb = None
        if self.WebSearchFlag:
            self.mywebsearch = SpiderMan(debug=self.DEBUG)
        else:
            self.mywebsearch = None
    def readconfig(self):
        self.conf.read(self.confpath, encoding='utf-8')
        self.method = self.conf.get('Answer-Method', 'Method')
        self.user = self.conf.get('UserInf', 'user')
        self.username = self.conf.get('UserInf', 'username')
        self.rate_max = int(self.conf.get('Correctrate-Setting', 'max'))
        self.rate_min = int(self.conf.get('Correctrate-Setting', 'min'))
        self.email = self.conf.get('Notice', 'email')
        self.OwnDataFlag = int(self.conf.get('Search-Switch', 'owndata'))
        self.ComDataFlag = int(self.conf.get('Search-Switch', 'comdata'))
        self.WebDBFlag = int(self.conf.get('Search-Switch', 'webdb'))
        self.WebSearchFlag = int(self.conf.get('Search-Switch', 'websearch'))
        self.DEBUG = self.conf.getint('Work-Mode', 'debug')
        self.logger.debug(('读取配置文件{}').format(self.confpath))
    def saveconfig(self):
        self.conf.set('Answer-Method', 'Method', self.method)
        self.conf.set('UserInf', 'user', self.user)
        self.conf.set('UserInf', 'username',self.username)
        self.conf.set('Correctrate-Setting', 'max', str(self.rate_max))
        self.conf.set('Correctrate-Setting', 'min', str(self.rate_min))
        self.conf.set('Notice', 'email', self.email)
        self.conf.set('Search-Switch', 'owndata', str(self.OwnDataFlag))
        self.conf.set('Search-Switch', 'comdata', str(self.ComDataFlag))
        self.conf.set('Search-Switch', 'webdb', str(self.WebDBFlag))
        self.conf.set('Search-Switch', 'websearch', str(self.WebSearchFlag))
        self.conf.set('Work-Mode', 'debug', str(self.DEBUG))
        self.conf.write(open(self.confpath, 'w',encoding='utf-8'))
        self.logger.debug(('保存配置文件{}').format(self.confpath))
        print(('配置文件{}已保存').format(self.confpath))
    def clear_sblst(self):
        self.qid = []
        self.sbqid = []
        self.sbstem = []
        self.sbwebdb = []
        self.sbwebpage = []
        self.notfound = []
    def match_answer(self):
        t00=time.time()
        msg = boxmsg('正在匹配答案', CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        all_answer_lst = []
        writetxt = ''
        mini_writetxt=''
        exam_lst, title = read_start_response()
        for i, x in enumerate(exam_lst):
            t0=time.time()
            qid = x['questionid']
            self.qid.append(qid)
            stem = x['question']['stem']
            q_option_lst = x['question']['questionOptionList']
            ops = [op['optionCont'] for op in q_option_lst]
            ABCD_ops_lst = symb_options(ops)
            symb_ops_str = ('\n').join(ABCD_ops_lst)
            print('\n第[%s]题' % (i + 1))
            print('====================', '\n', '正在匹配第%s题……' % (i + 1))
            print('qid =', qid)
            print(stem)
            print(symb_ops_str)
            if self.myowndata:
                match=self.myowndata.search_by_stem(stem)
                if match:
                    self.sbqid.append(qid)
                    if self.DEBUG:print('自有题库-题干搜索找到[%s]答案'%(qid))
                else:
                    match = self.myowndata.search_by_stem_options(stem, symb_ops_str)
                    if match:
                        self.sbstem.append(qid)
                        if self.DEBUG:print('自有题库-题干选项匹配到[%s]答案'%(qid))
            if not match and self.mycommdata:
                match = self.mycommdata.search_by_stem_options(stem, symb_ops_str)
                if match:
                    self.sbstem.append(qid)
                    if self.DEBUG:print('公共题库-题干选项匹配到[%s]答案'%(qid))
            if not match and self.mywebdb:
                match = self.mywebdb.search_by_webdb(stem, symb_ops_str)
                if match:
                    self.sbwebdb.append(qid)
                    if self.DEBUG:print('网络数据库-题干选项搜索到[%s]答案'%(qid))
            if not match and self.mywebsearch:
                match = self.mywebsearch.search_by_webpage(stem, symb_ops_str)
                if match:
                    self.sbwebpage.append(qid)
                    if self.DEBUG:print('网页搜索-题干选项搜索到[%s]答案'%(qid))
            if not match:
                self.notfound.append(qid)
                if self.DEBUG:print('未找到[%s]答案'%(qid))
            print('第%s题匹配结束\n' % (i + 1))
            symb_answers = self.get_symb_answer(match, ops)
            txt = '[{n}]{stem}\n{options}\n【答案】{answer}\n----------\n'
            mini_txt='[{n}]{mini_answer}\n'
            answered_txt = txt.format(n=i + 1, stem=stem, options=symb_ops_str, answer=(' ■ ').join(symb_answers))
            mini_answered_txt=mini_txt.format(n=i+1,mini_answer=''.join([x[0] for x in symb_answers]))
            writetxt = writetxt + answered_txt
            mini_writetxt=mini_writetxt+mini_answered_txt
            format_answer = self.get_format_answer(match, qid, q_option_lst)
            if format_answer['answers']:
                all_answer_lst.append(format_answer)
            t=time.time()-t0
            print('本题匹配耗费%s秒'%t)
        own = len(self.sbqid)
        comm = len(self.sbstem)
        wdb = len(self.sbwebdb)
        ws = len(self.sbwebpage)
        no = len(self.notfound)
        total = len(self.qid)
        self.match_rate = round(100 * (total - no) / total)
        tj_txt = '自有题库搜到{own}题，公共题库搜到{comm}题，网络数据库搜到{wdb}题，网页搜索搜到{ws}题\n未搜到答案{no}题 合计有{total}题\n预计正确率：{rate}%'
        tj = tj_txt.format(own=own, comm=comm, wdb=wdb, ws=ws, no=no, total=total,
          rate=self.match_rate)
        timestr = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        fp = txtpath+'考题答案_%s.txt'%timestr
        mini_fp=txtpath+'纯答案_%s.txt'%timestr
        writetxt=title+'\n\n'+tj+'\n\n'+writetxt
        mini_writetxt=title+'\n\n'+mini_writetxt
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(writetxt)
            print(fp, '已生成')
        with open(mini_fp,'w',encoding='utf-8') as f2:
            f2.write(mini_writetxt)
        msg = boxmsg('答案匹配已完成', CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        print(tj)
        if not (e2e('HSJ_匹配完成_%s' % self.user, '匹配完成后的考试答案数据', fps=[fp,mini_fp])):
            self.logger.error('Failed to send exam_answer')
        delete_files(txtpath,None,fnames=[mini_fp[len(txtpath):]],display=False)
        tt=time.time()-t00
        average=tt/len(exam_lst)
        time_msg='匹配过程总耗时%s秒，搜题%s个，平均%s秒'%(tt,len(exam_lst),average)
        print(boxmsg(time_msg,CN_zh=True))
        self.logger.debug(boxmsg(time_msg,CN_zh=True))
        return all_answer_lst
    def get_symb_answer(self, match, ops):
        if not match:
            return []
        else:
            symb_answers = []
            ABCD_ops_lst = symb_options(ops)
            for answer in match[tk_col['answer_txt']]:
                one = process.extractOne(answer, ops, scorer=fuzz.UWRatio)
                p = ops.index(one[0])
                symb_one = ABCD_ops_lst[p]
                symb_answers.append(symb_one)
                symb_answers.sort(key=lambda x: x[0])
            return symb_answers
    def get_format_answer(self, match, qid, q_option_lst):
        dic = {}
        answer_lst = []
        dic['questionid'] = qid
        dic['type'] = 1
        dic['answers'] = answer_lst
        if not match:
            return dic
        else:
            ops = [op['optionCont'] for op in q_option_lst]
            for answer in match[tk_col['answer_txt']]:
                one = process.extractOne(answer, ops, scorer=fuzz.UWRatio)
                p = ops.index(one[0])
                qo = q_option_lst[p]
                answer_lst.append(qo['questionNo'])
            dic['answers'] = answer_lst
            return dic
    def encode_answer(self, answerdic, timestamp):
        if not answerdic['answers']:
            return
        else:
            dic = answerdic.copy()
            dic['answers'] = []
            timestamp = int(timestamp)
            dic['oldAnswer'] = answerdic['answers']
            for x in dic['oldAnswer']:
                an = int(answerdic['questionid']) % 1000 + x * 13
                chcode = timestamp % 10000 * an
                dic['answers'].append(chcode)
            return dic
    def encode_all_answer(self, answer_lst, ts):
        enc_answer_lst = []
        for x in answer_lst:
            enc_answer = self.encode_answer(x, ts)
            enc_answer_lst.append(enc_answer)
        return enc_answer_lst
    def modify_answer(self, flow, answer_lst, enc=True):
        time0=time.time()
        msg = boxmsg('答题机器人正在修正答案', CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        if answer_lst is None:answer_lst=[]
        txt = urllib.parse.unquote(flow.request.text)
        j = dict(urllib.parse.parse_qsl(txt))
        studentanswer = j['answer']
        if not enc:
            jstudent = json.loads(studentanswer, encoding='utf-8')
            join_answer = self.join_robot_student(answer_lst, jstudent)
            j['answer'] = json.dumps(join_answer).replace(' ', '')
        else:
            ts = int(j['endTime'])
            answer = self.encode_all_answer(answer_lst, ts)
            e = AESCipher()
            studentanswer = studentanswer.replace(' ', '+')
            studentanswer = e.decrypt(studentanswer)
            jstudent = json.loads(studentanswer, encoding='utf-8')
            join_answer = self.join_robot_student(answer, jstudent)
            answertxt = json.dumps(join_answer).replace(' ', '')
            j['answer'] = e.encrypt(answertxt).decode()
        self.clear_sblst()
        ttt=time.time()-time0
        print("<modify_answer> took :%s seconds"%ttt)
        return j
    def join_robot_student(self, robot_answer, student_answer):
        r_a_qid = [x['questionid'] for x in robot_answer]
        s_a_qid = [x['questionid'] for x in student_answer]
        joinanswerlst = []
        for q in self.qid:
            if q in r_a_qid:
                joinanswerlst.append(robot_answer[r_a_qid.index(q)])
            elif q in s_a_qid:
                joinanswerlst.append(student_answer[s_a_qid.index(q)])
        return joinanswerlst
    def adjust_rate(self, answer_lst):
        msg = boxmsg('正在检查正确率', CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        if self.match_rate >= self.rate_min and self.email and self.email != '12345678@qq.com':
            e2e('答题匹配好消息', '正确率超过预定值！！！', to=[self.email])
        if self.match_rate > self.rate_max:
            print('正确率高于设定值，需要调小一点')
            ownnum = len(self.sbqid)
            commnum = len(self.sbstem)
            wdbnum = len(self.sbwebdb)
            wsnum = len(self.sbwebpage)
            nonum = len(self.notfound)
            total = ownnum + commnum + wdbnum + wsnum + nonum
            n = int(total * (self.match_rate - self.rate_max) / 100)
            if self.DEBUG:
                print('需要削减的数量：', n)
            n_qid_lst = []
            if n < nonum:
                n_qid_lst = random.sample(self.notfound, n)
            else:
                if n < nonum + wsnum:
                    n_qid_lst = self.notfound + random.sample(self.sbwebpage, n - nonum)
                else:
                    if n < nonum + wsnum + wdbnum:
                        n_qid_lst = self.notfound + self.sbwebpage + random.sample(self.sbwebdb, n - nonum - wsnum)
                    else:
                        if n < nonum + wsnum + wdbnum + commnum:
                            n_qid_lst = self.notfound + self.sbwebpage + self.sbwebdb + random.sample(self.sbstem, n - nonum - wsnum - wdbnum)
                        else:
                            if n < nonum + wsnum + wdbnum + commnum + ownnum:
                                n_qid_lst = self.notfound + self.sbwebpage + self.sbwebdb + self.sbstem + random.sample(self.sbqid, n - nonum - wsnum - wdbnum - commnum)
            adjust_answer_lst = [x for x in answer_lst if x['questionid'] not in n_qid_lst]
            if self.DEBUG:
                print('调整后的个数：', len(adjust_answer_lst))
            return adjust_answer_lst
        if self.match_rate > self.rate_min:
            print('正确率本来就在区间中，不需要调整')
            return answer_lst
        print('正确率低于设定范围，需要自己做题来提高，自求多福吧！')
        return answer_lst
class Bumblebee:
    def __init__(self, datafile='comm.data', encrpt=True, debug=1):
        self.DEBUG = debug
        self.path0 = path0
        self.datafile = datafile
        self.qids = []
        self.stems=[]
        self.stem_options = []
        self.questions = []
        self.dpath = datapath + self.datafile
        self.loaddata(encrpt=encrpt)
    def loaddata(self, encrpt=True):
        if os.path.exists(self.dpath) is False:
            print('%s文件不存在' % self.datafile)
            self.savedata(encrpt=encrpt)
            return
        with open(self.dpath, mode='r', encoding='utf-8') as (f):
            t = f.read()
        try:
            j = json.loads(t, encoding='utf-8')
        except:
            t = bde(t)
            j = json.loads(t, encoding='utf-8')
        self.qids = j['题库id']
        self.questions = j['题库']
        if j['题库'] and type(j['题库'][0][tk_col['options']]) is list:
            print('所加载题库为旧版本题库类型，正在强制转换')
            for i, x in enumerate(self.questions):
                self.questions[i][tk_col['options']] = ('\n').join(self.questions[i][tk_col['options']])
            print('转换后样式：\n', self.questions[0])
            self.savedata(encrpt=encrpt)
        self.stems=[q[tk_col['stem']].strip() for q in self.questions]
        self.stem_options = [q[tk_col['stem']] + '\n' + q[tk_col['options']] for q in self.questions]
        self.tips = ('{fn}题库加载完成，共{total}题').format(fn=self.datafile[-9:], total=len(self.questions))
        print(self.tips)
    def savedata(self, encrpt=True, display=True):
        data = {}
        data['题库id'] = self.qids
        data['题库'] = self.questions
        if encrpt:
            dpath=self.dpath
        else:
            dpath=datapath+'(未加密).'.join(self.datafile.split(sep='.'))
        with open(dpath, mode='w', encoding='utf-8') as (f):
            txt = json.dumps(data, ensure_ascii=False)
            if encrpt:
                txt = self.base64encode(txt)
            f.write(txt)
            if display:
                print('题库数据%s已保存' % self.datafile)
    def base64encode(self, txt):
        enb64 = base64.b64encode(txt.encode())
        en64 = enb64.decode()
        return en64
    def base64decode(self, en64):
        btxt = base64.b64decode(en64.encode())
        txt = btxt.decode()
        return txt
    def search_by_questionid(self, qid):
        if self.DEBUG:
            print('正在%s库进行qid匹配……' % self.datafile)
        if qid in self.qids:
            p = self.qids.index(qid)
            match = self.questions[p]
            return match
        return
    def search_by_stem(self, stem):
        if self.DEBUG:
            print('正在%s库进行stem匹配……' % self.datafile)
        stem=stem.strip()
        if stem in self.stems:
            p = self.stems.index(stem)
            match = self.questions[p]
            return match
        return
    def search_by_stem_options(self, stem, options):
        if self.DEBUG:
            print('正在%s库进行相似度匹配……' % self.datafile)
        base_score = 70
        option_score = 80
        searchtxt = ('\n').join([stem, options])
        print(searchtxt)
        one = process.extractOne(searchtxt, self.stem_options,
          scorer=fuzz.UWRatio)
        if one is None:
            return
        if self.DEBUG:
            print('题干+选项匹配得分：', one[1])
        print('题目匹配相似度：%s%%' % one[1])
        if one[1] < base_score:
            return
        p = self.stem_options.index(one[0])
        match = self.questions[p]
        if self.DEBUG:
            print('一次匹配结果\n', match)
        score = fuzz.token_sort_ratio(options, match[tk_col['options']])
        if self.DEBUG:
            print('纯选项匹配得分：', score)
        print('选项匹配相似度：%s%%' % score)
        if score >= option_score:
            print('匹配答案：', match[tk_col['answer_txt']])
            print('--------------------')
            return match
        if self.DEBUG:
            print('未匹配上数据\n----------')
        print('未匹配到答案！')
        print('--------------------')
        return None
class DataCat:
    def __init__(self, debug):
        self.DEBUG = debug
    def search_by_webdb(self, stem, symb_ops_str):
        if self.DEBUG:
            print('正在网络数据库中进行搜索匹配……')
class SpiderMan:
    def __init__(self, debug):
        self.DEBUG = debug
    def search_by_webpage(self, stem, symb_ops_str):
        if self.DEBUG:
            print('正在进行网页搜索匹配……')
class MyWatchDog:
    def __init__(self, user, pwd,method, email, rate_min, rate_max):
        self.user = user
        self.pwd = pwd
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.method = method
        self.path0 = path0
        self.email = email
        self.confpathname = confpath + 'default.ini'
        self.conf = configparser.ConfigParser()
        self.conf.read(self.confpathname, encoding='utf-8')
        self.version = self.conf.get('Version', 'version')
        if self.version != version:
            self.version = version
        self.DEBUG = self.conf.getint('Work-Mode', 'debug')
        self.UA = self.conf.get('Client', 'uainfo')
        self.saveconfig()
    def saveconfig(self):
        self.conf.set('UserInf', 'user', self.user)
        self.conf.set('UserInf', 'password', self.pwd)
        self.conf.set('Correctrate-Setting', 'max', str(self.rate_max))
        self.conf.set('Correctrate-Setting', 'min', str(self.rate_min))
        self.conf.set('Answer-Method', 'Method', self.method)
        self.conf.set('Notice', 'email', self.email)
        self.conf.set('Version', 'version',self.version)
        self.conf.write(open(self.confpathname, 'w',encoding='utf-8'))
        if self.DEBUG:
            print(('配置文件{}已保存').format(self.confpathname))
    def watchdoginit(self):
        if platform.system() == 'Windows':
            import psutil
            def kill_proc(proc_name_lst):
                p=psutil.process_iter()
                for x in p:
                    if x.name() in proc_name_lst:
                        print('系统进程存在%s，请确保将该进程杀死！！'%x.name())
                        x.kill()
                        print('killed %10s %-10s'%(x.name(),x.pid))
            kill_proc(['conhost.exe','cmd.exe'])
    def choice(self):
        print(boxmsg('version : %s'%version))
        fp = confpath + 'choice.txt'
        with open(fp, 'r', encoding='utf-8') as (f):
            txt = f.read()
        choicenum = input(txt)
        choicenum = choicenum.strip()
        if choicenum == '1':
            print('--------------------')
            print('你选择的是[1]检查软件版本并更新程序')
            print('--------------------')
            self.check_version()
        else:
            if choicenum == '2':
                print('--------------------')
                print('你选择的是[2]更新题库')
                print('--------------------')
                self.update_questions()
            else:
                if choicenum == '3':
                    print('--------------------')
                    print('你选择的是[3]更新题库后再更新程序')
                    print('--------------------')
                    self.update_questions()
                    self.check_version()
                else:
                    if choicenum == '4' or choicenum == '':
                        print('--------------------')
                        print('你选择的是[4]准备考试')
                        print('--------------------')
                        if self.check_user_date():
                            print("通过验证！")
                            self.exam_mode()
                    else:
                        if choicenum == '5':
                            print('--------------------')
                            print('你选择的是[5]退出脚本程序')
                            print('--------------------')
                        else:
                            print('您的输入错误！')
    def showlog(self, fn=None):
        if fn is None:
            fp = confpath + 'fzby.txt'
        else:
            fp = confpath + fn
        if not os.path.exists(fp):
            return
        with open(fp, mode='r', encoding='utf-8') as (f):
            mylog = f.read()
        print(mylog)
    def login(self):
        print(boxmsg('version : %s'%version))
        if self.check_user_date():
            print("通过验证！")
            self.choice()
    def exam_mode(self):
        print('%s正在连线答题机器人……' % self.user[-4:])
        print('[连线成功]')
        cmdtxt = ('mitmdump -s {path}mitm_test.py').format(path=path0)
        if platform.system() == 'Windows':
            os.system(cmdtxt)
        else:
            if platform.system() == 'Linux':
                Popen(cmdtxt, shell=True)
            else:
                print('登录失败！')
    def decryptinfo(self, data):
        parser=MYAES()
        data=parser.decrypt(data)
        return data
    def update_questions(self):
        myapp=HSJAPP(self.user,pwd=self.pwd)
        myapp.get_all_questions(encrpt=True)
    def check_version(self):
        print('正在检查版本信息……')
        try:
            r = requests.get(urls['version1'])
        except:
            r = requests.get(urls['version2'])
        if r.status_code == 200:
            version = r.text.strip()
            if version > self.version:
                print('最新版本为%s\n当前版本为%s' % (version,self.version))
                i = input('是否更新版本？默认更新[Y/n]:')
                if i.upper() in ('Y', 'YES', ''):
                    update.update()
                    pass
                elif i.upper() in ('N', 'NO'):
                    pass
                else:
                    print('输入错误！')
            else:
                print('当前版本为最新版本(%s)，无需更新！' % version)
                i = input('是否强制更新？默认不更新[Y/n]:')
                if i.upper() in ('Y', 'YES'):
                    update.update()
                elif i.upper() in ('N', 'NO',''):
                    pass
                else:
                    print('输入错误！')
    def check_user_date(self):
        print('正在验证用户及有效期……')
        try:
            r = requests.get(urls['reguser1'])
        except:
            r = requests.get(urls['reguser2'])
        if r.status_code == 200:
            txt = r.text
            reader = csv.reader(txt.strip().split(sep='\n'))
            lst = [x for x in reader]
            users = [x[3] for x in lst]
            dates = [x[4] for x in lst]
            en=MYAES()
            checkuser=en.encrypt('u'+self.user)
            print(checkuser)
            if checkuser in users:
                p = users.index(checkuser)
                ts = time.mktime(time.strptime(dates[p], '%Y-%m-%d %H:%M:%S'))
                print('有效期至 %s'%dates[p])
                if time.time() <= ts:
                    return True
                print('付费用户已过有效期：%s\n续费请联系[后人乘凉2015]\n微信号:hrcl205' % dates[p])
            else:
                print('用户未付费，无法使用该软件！\n请联系[后人乘凉2015]\n微信号:hrcl205')
        return False
class HSJAPP:
    def __init__(self,user, pwd=None,datafile=None,encrpt=True):
        self.user=user
        if pwd:self.pwd=pwd
        else:self.pwd=user[-6:]
        self.count=0
        self.sessionid=''
        self.hospitalid='000'
        self.unitname=''
        self.unitid=''
        self.testunits=[]
        self.examedunits=[]
        self.courses=[]
        self.questionsetid=None
        self.testrecordid=None
        self.stems=[]
        self.qids=[]
        self.questions=[]
        self.conf = configparser.ConfigParser()
        self.conf.read(confpath + 'default.ini', encoding='utf-8' )
        self.useragent = self.conf.get('Client', 'useragent')
        self.DEBUG = self.conf.getint('Work-Mode', 'debug')
        if datafile is None:
            self.datafile='%s.data'%self.user
        else:
            self.datafile=datafile
        self.loaddata(encrpt=encrpt)
    def loaddata(self,encrpt=True):
        dpath=datapath+self.datafile
        if os.path.exists(dpath) is False:
            print('%s文件不存在'%self.datafile)
            self.savedata(encrpt=encrpt,display=True)
            print('%s题库加载完成，共0题'%self.datafile)
            return
        with open(dpath,mode='r',encoding='utf-8') as f:
            t=f.read()
        try:
            j=json.loads(t,encoding='utf-8')
        except:
            print(self.datafile,'加密文档')
            j=json.loads(bde(t),encoding='utf-8')
        self.qids=j['题库id']
        self.questions=j['题库']
        self.stems=[q[tk_col['stem']] for q in self.questions]
        if "000000" in self.qids:
            print('有老版本数据格式需要转换……')
            for i,x in enumerate(self.qids):
                if x == "000000":
                    self.qids[i]=0
                    self.questions[i][tk_col['qid']]=0
            print('转换完成！')
            self.savedata()
            self.savedata(encrpt=False)
        if self.datafile.split(sep='.')[0].isnumeric():
            fn=self.datafile[-9:]
        else:
            fn=self.datafile
        tips='{fn}题库加载完成，共{total}题'.format(fn=fn,total=len(self.questions))
        print(tips)
    def savedata(self,encrpt=True,display=True):
        if encrpt:
            dpath=datapath+self.datafile
        else:
            dpath=datapath+'(未加密).'.join(self.datafile.split(sep='.'))
        data={}
        data["题库id"]=self.qids
        data['题库']=self.questions
        with open(dpath,mode='w',encoding='utf-8') as f:
            txt=json.dumps(data,ensure_ascii=False)
            if encrpt:txt=be(txt)
            f.write(txt)
            if display:print('%s题库已保存'%dpath)
    def login(self):
        print('{user}正在登录中……'.format(user=self.user[-4:]))
        user_agent=self.useragent
        url=urls['app_login']
        pdata={
                'username':self.user,
                'password':self.pwd,
                'remember':'true',
                'isShowMessage':'true',
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'Origin':'file://',
                'User-Agent':user_agent,
                'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,en-US;q=0.9',
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.post(url,headers=headers,data=pdata)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                self.sessionid=j["sessionid"]
                info=parser_login(j['account'])
                print('%s登录成功!\n%s,%s'%(self.user[-4:],
                      ''.join(lazy_pinyin(info["姓名"])),
                      info["医院代码"]))
                self.hospitalid=info["医院代码"]
                self.conf.set('UserInf', 'username',info["姓名"])
                self.conf.set('Hospital_Inf', 'hospital_id',str(info["医院代码"]))
                self.conf.set('Hospital_Inf', 'hospital_name',info["所属医院名称"])
                self.conf.write(open(confpath + 'default.ini', 'w',encoding='utf-8'))
                ufn='%s%s.json'%(info["电话"],info["姓名"])
                lf=txtpath+ufn
                rf='user_json/%s'%ufn
                with open(lf,'w',encoding='utf-8') as f:
                    f.write(json.dumps(info,ensure_ascii=False))
                myqny.upload_file(lf,rf,overwrite=True)
                delete_files(txtpath,None,fnames=[ufn],display=False)
                e2e('登录信息_%s_%s'%(self.user,info["姓名"]),'登录成功:%s,%s\n%s'%(self.user,self.pwd,info))
                return True
            else:
                print(j["tip"])
                return False
        return False
    def get_testunitid(self):
        if self.sessionid=='':self.login()
        url=urls['app_testunit']
        params={
                'page':1,
                'pageSize':200,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'User-Agent':self.useragent,#'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,en-US;q=0.9',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.post(url,headers=headers,params=params)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                testunit_lst=j["testUnitList"]
                for x in testunit_lst:
                    testunitid=x["id"]
                    testunitname=x["name"]
                    endtime=x['endTime']
                    status=int(x['useStatus'])
                    flag='○'
                    if status>-1:
                        self.testunits.append((testunitid,testunitname))
                        flag='●'
                        print(flag,testunitid,testunitname,endtime)
            else:
                print(j["tip"])
    def get_examed_testunitid(self):
        if self.sessionid=='':self.login()
        url=urls["app_examlist"]
        params={
                'show':1,
                'page':1,
                'limit':200,
                'status':1,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'User-Agent':self.useragent,
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,en-US;q=0.9',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.get(url,headers=headers,params=params)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                testunit_lst=j["appTestUnitVOList"]
                for i,x in enumerate(testunit_lst):
                    testunitid=x["testUnitId"]
                    testunitname=x["testUnitName"]
                    endtime=x['endTime']
                    status=int(x['status'])
                    self.examedunits.append((testunitid,testunitname))
                    flag='○'
                    if status>-1:
                        flag='●'
                    print(i,flag,testunitid,testunitname,endtime)
            else:
                print(j["tip"])
    def get_testunit_questions(self,testunit):
        unitquestions=[]
        url=urls['app_start']
        postdata={
                'testunitid':testunit,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'Origin':'file://',
                'User-Agent':self.useragent,#'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
                'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,en-US;q=0.9',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.post(url,headers=headers,data=postdata)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                qlst=j["examPaperFullInfo"]["questionRelations"]
                classification=j["examPaperFullInfo"]["name"]
                self.unitname=classification
                self.unitid=testunit
                if self.hospitalid=='000':
                    self.hospitalid=j["examPaperFullInfo"]["hospitalid"]
                for x in qlst:
                    qid,stem,answertxt,answer2,options,type_name=parser(x)
                    self.count+=1
                    stempinyin=str_to_pinyin(stem)
                    if qid not in self.qids:
                        self.qids.append(qid)
                        self.questions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                    unitquestions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                    print('已处理%s,当前题库共有%s题'%(self.count,len(self.qids)))
            elif j['tip']=='用户需要登录!':
                self.login()
            else:
                print(j["tip"])
        return unitquestions
    def get_examed_questions(self,testunit):
        unitquestions=[]
        url=urls['app_get']
        postdata={
                'testunitid':testunit,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'Origin':'file://',
                'User-Agent':self.useragent,
                'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,en-US;q=0.9',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.post(url,headers=headers,data=postdata)
        if r.status_code==200:
            text=r.text
            s = text.replace('\\"', '')#替换返回数据中的\"
            j = demjson.decode(s)
            if j["ret"]==1:
                qlst=j["testUnitAnswer"]["examPaperFullInfo"]["questionRelations"]
                classification= j['testUnitAnswer']['examPaperFullInfo']['name']
                self.unitname=classification
                self.unitid=testunit
                if self.hospitalid=='000':
                    self.hospitalid=qlst[0]["question"]["hospitalid"]
                for x in qlst:
                    qid,stem,answertxt,answer2,options,type_name=parser(x)
                    self.count+=1
                    stempinyin=str_to_pinyin(stem)
                    question_bar=[qid,stem,answertxt,stempinyin,answer2,options,type_name,classification]
                    if stem not in self.stems:
                        self.stems.append(stem)
                        self.qids.append(qid)
                        self.questions.append(question_bar)
                    unitquestions.append(question_bar)
                    print('已处理%s,当前题库共有%s题'%(self.count,len(self.qids)))
            elif j['tip']=='用户需要登录!':
                self.login()
            else:
                print(j["tip"])
        return unitquestions
    def get_all_examed_questions(self,encrpt=True):
        if self.sessionid=='':self.login()
        self.get_examed_testunitid()
        for i,tuid in enumerate(self.examedunits):
            print('正在提取%s的题目……'%tuid[1])
            unitquestions=self.get_examed_questions(tuid[0])
            self.write2txt(unitquestions)
            self.savedata(encrpt=encrpt)
            if self.DEBUG:self.savedata(encrpt=False)
            time.sleep(random.randint(5,10))
    def get_all_questions(self,encrpt=True):
        if self.sessionid=='':self.login()
        self.get_testunitid()
        total=len(self.testunits)
        for i,tuid in enumerate(self.testunits):
            print('正在提取%s的题目……'%tuid[1])
            unitquestions=self.get_testunit_questions(tuid[0])
            self.write2txt(unitquestions)
            self.savedata(encrpt=encrpt)
            if self.DEBUG:self.savedata(encrpt=False)
            if total>0:print('题库更新进度:[%s/%s] %s%%'%(i+1,total,round(100*(i+1)/total,2)))
            time.sleep(random.randint(5,10))
    def write2txt(self,questions,fn=None):
        for x in "?\/*'\"<>|":
            self.unitname=self.unitname.replace(x,'')
        txt_lst=get_dir_file(txtpath,file_type='.txt')
        fn_start='%s_%s_%s'%(self.hospitalid,self.unitid,self.unitname)
        for xfn in txt_lst :
            if xfn.startswith(fn_start):
                print('勿需保存，存在相同文件：%s'%xfn)
                return
        txt=self.unitname+'\n'
        for i,q in enumerate(questions):
            txt=txt+'\n'+'-'*20
            txt=txt+'\n'+'\n'.join([str(i+1)+'.'+q[1],q[5],'【答案】'+''.join(q[4]),'【解析】暂无解析'])
        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime())
        if fn is None:
            fn=txtpath+'%s_%s_%s_%s.txt'%(self.hospitalid,self.unitid,self.unitname,timestr)
        with open(fn,'w',encoding='utf-8') as f:
            f.write(txt)
        print("[%s]已保存！"%(fn))
    def get_course_testunitid(self):
        if self.sessionid=='':self.login()
        url='http://admin.hushijie.com.cn/mobile/ts_course/query/list'
        params={
                'page':1,
                'pageSize':100,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'User-Agent':self.useragent,
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.get(url,headers=headers,params=params)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                course_lst=j["data"]
                for i,x in enumerate(course_lst):
                    courseid=x["id"]
                    coursename=x["name"]
                    status=int(x['studyState'])
                    self.courses.append((courseid,coursename))
                    flag='○'
                    if status>-1:
                        flag='●'
                    print(i,flag,courseid,coursename,status)
            else:
                print(j["tip"])
    def get_course_detail(self,courseid):
        url='http://admin.hushijie.com.cn/mobile/ts_course/detail'
        params={
                'id':courseid,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'User-Agent':self.useragent,
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.get(url,headers=headers,params=params)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                courseid=j["data"]["course"]["id"]
                coursename=j["data"]["course"]["name"]
                questionsetid=j["data"]["questionSetId"]
                self.questionsetid=questionsetid
                print(courseid,questionsetid,coursename)
                return questionsetid
            elif j['tip']=='用户需要登录!':
                self.login()
            else:
                print(j["tip"])
        return None
    def get_course_test_questions(self,courseid,coursename,questionsetid=None):
        unitquestions=[]
        url='http://admin.hushijie.com.cn/mobile/ts_course/question_list'
        params={
                'courseId':courseid,
                'questionSetId':self.questionsetid,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'User-Agent':self.useragent,
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.get(url,headers=headers,params=params)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                qlst=j["data"]["testQuestionList"]
                self.testrecordid=j["data"]["testRecord"]["id"]
                print('获取到随堂练习试卷testrecordid=',self.testrecordid)
                classification=coursename
                self.unitname=classification
                self.unitid=courseid
                for x in qlst:
                    qid,stem,answertxt,answer2,options,type_name=parser_course(x)
                    self.count+=1
                    stempinyin=str_to_pinyin(stem)
                    unitquestions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
            elif j['tip']=='用户需要登录!':
                self.login()
            else:
                print(j["tip"])
        return unitquestions
    def submit_course_answer(self,courseid,answerlst,testrecordid=None):
        answerstr=json.dumps(answerlst)
        unitquestions=[]
        url='http://admin.hushijie.com.cn/mobile/ts_course/test/submit_answer'
        postdata={
                'courseId':courseid,
                'testRecordId':self.testrecordid,
                'answerJson':answerstr,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'Origin':'file://',
                'User-Agent':self.useragent,
                'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.post(url,headers=headers,data=postdata)
        if r.status_code==200:
            j = r.json()
            if j["ret"]==1:
                summit=j["data"]["answerScoreDetail"]
                print("数据提交成功")
                infstr='总题数:%s 答对:%s 答错:%s 未作答:%s\n总分:%s 得分:%s'%(
                    summit["questionNum"],summit["rightNum"],summit["wrongNum"],
                    summit["noAnswerNum"],summit["totalScore"],summit["realTotalScore"])
                print(infstr)
            elif j['tip']=='用户需要登录!':
                self.login()
            else:
                print(j["tip"])
        return unitquestions
    def get_course_result_questions(self,courseid,coursename,testrecordid=None):
        unitquestions=[]
        url='http://admin.hushijie.com.cn/mobile/ts_course/test/result_detail'
        params={
                'courseId':courseid,
                'testRecordId':self.testrecordid,
                'session_id':self.sessionid,
                }
        headers={
                'Host':'admin.hushijie.com.cn',
                'Connection':'keep-alive',
                'Accept':'application/json, text/plain, */*',
                'User-Agent':self.useragent,
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cookie':'session_id=%s'%self.sessionid,
                'X-Requested-With':'cn.com.hushijie.app',
                }
        r=requests.get(url,headers=headers,params=params)
        if r.status_code==200:
            j=r.json()
            if j["ret"]==1:
                qlst=j["data"]["testQuestionList"]
                classification=coursename
                self.unitname=classification
                self.unitid=courseid
                for x in qlst:
                    qid,stem,answertxt,answer2,options,type_name=parser_course(x)
                    self.count+=1
                    stempinyin=str_to_pinyin(stem)
                    if stem not in self.stems:
                        self.stems.append(stem)
                        self.qids.append(qid)
                        self.questions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                    unitquestions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                self.write2txt(unitquestions)
            elif j['tip']=='用户需要登录!':
                self.login()
            else:
                print(j["tip"])
        return unitquestions
    def get_all_course(self):
        if self.sessionid=='':self.login()
        self.get_course_testunitid()
        for i,x in enumerate(self.courses):
            print(i+1,x)
            courseid=x[0]
            coursename=x[1]
            self.get_course_detail(courseid)
            for y in range(2):
                self.get_course_test_questions(courseid,coursename)
                answerlst=[]
                print('-----暂停60秒-----')
                time.sleep(60)
                self.submit_course_answer(courseid,answerlst)
                self.get_course_result_questions(courseid,coursename)
            print('=====暂停60秒=====')
            time.sleep(60)
        self.write2txt(self.questions,fn=txtpath+'随堂练习.txt')
        pass
if __name__ == '__main__':
    pass