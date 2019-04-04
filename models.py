#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,time,json,random,base64,urllib
import configparser
import platform
from subprocess import Popen
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from comm import path0,confpath,datapath,txtpath,boxmsg,tk_col
from comm import check_user,check_date,read_start_response,symb_options,delete_files
from m2m import e2e
from HSJ_AES import AESCipher
class AnswerRobot():
    def __init__(self,logger,):
        self.logger=logger
        self.conf=configparser.ConfigParser()
        self.confpath=confpath+"default.ini"
        self.readconfig()
        self.match_rate=0
        self.qid=[]
        self.sbqid=[] 
        self.sbstem=[]
        self.sbwebdb=[]
        self.sbwebpage=[]
        self.notfound=[]
        if self.OwnDataFlag:
            self.myowndata=Bumblebee(datafile='%s.data'%self.user,encrpt=True,
                                  debug=self.DEBUG)
        else:
            self.myowndata=None
        if self.ComDataFlag:
            self.mycommdata=Bumblebee(datafile='comm.data',encrpt=True,
                                   debug=self.DEBUG)
        else:
            self.mycommdata=None
        if self.WebDBFlag:
            self.mywebdb=DataCat(debug=self.DEBUG)
        else:
            self.mywebdb=None
        if self.WebSearchFlag:
            self.mywebsearch=SpiderMan(debug=self.DEBUG)
        else:
            self.mywebsearch=None
    def readconfig(self):
        self.conf.read(self.confpath, encoding="utf-8")
        self.method=self.conf.get('Answer-Method','Method')
        self.user=self.conf.get('UserInf','user')
        self.rate_max=int(self.conf.get('Correctrate-Setting','max'))
        self.rate_min=int(self.conf.get('Correctrate-Setting','min'))
        self.email=self.conf.get('Notice','email')
        self.OwnDataFlag=int(self.conf.get('Search-Switch','owndata'))
        self.ComDataFlag=int(self.conf.get('Search-Switch','comdata'))
        self.WebDBFlag=int(self.conf.get('Search-Switch','webdb'))
        self.WebSearchFlag=int(self.conf.get('Search-Switch','websearch'))
        self.DEBUG=self.conf.getint('Work-Mode','debug')
        self.logger.debug('读取配置文件{}'.format(self.confpath))
    def saveconfig(self):
        self.conf.set('Answer-Method','Method',self.method)
        self.conf.set('UserInf','user',self.user)
        self.conf.set('Correctrate-Setting','max',str(self.rate_max))
        self.conf.set('Correctrate-Setting','min',str(self.rate_min))
        self.conf.set('Notice','email',self.email)
        self.conf.set('Search-Switch','owndata',str(self.OwnDataFlag))
        self.conf.set('Search-Switch','comdata',str(self.ComDataFlag))
        self.conf.set('Search-Switch','webdb',str(self.WebDBFlag))
        self.conf.set('Search-Switch','websearch',str(self.WebSearchFlag))
        self.conf.set('Work-Mode','debug',str(self.DEBUG))
        self.conf.write(open(self.confpath, "w"))
        self.logger.debug('保存配置文件{}'.format(self.confpath))
        print('配置文件{}已保存'.format(self.confpath))
    def clear_sblst(self):
        self.qid=[]
        self.sbqid=[] 
        self.sbstem=[]
        self.sbwebdb=[]
        self.sbwebpage=[]
        self.notfound=[]
    def match_answer(self,):
        msg=boxmsg('正在匹配答案',CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        all_answer_lst=[]
        writetxt=''
        exam_lst,title=read_start_response()
        for i,x in enumerate(exam_lst):
            qid=x["questionid"]
            self.qid.append(qid)
            stem=x["question"]["stem"]
            q_option_lst=x["question"]["questionOptionList"]
            ops=[op["optionCont"] for op in q_option_lst]
            ABCD_ops_lst=symb_options(ops)
            symb_ops_str='\n'.join(ABCD_ops_lst)
            if self.DEBUG:
                print('='*20,'\n','正在匹配第%s题……'%(i+1))
                print('qid =',qid)
                print(stem)
                print(symb_ops_str)
            if self.myowndata:
                print('\n第[%s]题'%(i+1))
                match=self.myowndata.search_by_stem_options(stem,symb_ops_str)
                if match : self.sbstem.append(qid)
            if (not match) and self.mycommdata:
                match=self.mycommdata.search_by_stem_options(stem,symb_ops_str)
                if match : self.sbstem.append(qid)
            if (not match) and self.mywebdb:
                match=self.mywebdb.search_by_webdb(stem,symb_ops_str)
                if match : self.sbwebdb.append(qid)
            if (not match) and self.mywebsearch:
                match=self.mywebsearch.search_by_webpage(stem,symb_ops_str)
                if match : self.sbwebpage.append(qid)
            if not match:
                self.notfound.append(qid)
            if self.DEBUG:print('第%s题匹配结束\n'%(i+1))
            symb_answers=self.get_symb_answer(match,ops)
            txt='[{n}]{stem}\n{options}\n【答案】{answer}\n----------\n'
            answered_txt=txt.format(n=i+1,stem=stem,options=symb_ops_str,
                       answer='■'.join(symb_answers))
            writetxt=writetxt+answered_txt
            format_answer=self.get_format_answer(match,qid,q_option_lst)
            if format_answer['answers']:
                all_answer_lst.append(format_answer)
        own=len(self.sbqid)
        comm=len(self.sbstem)
        wdb=len(self.sbwebdb)
        ws=len(self.sbwebpage)
        no=len(self.notfound)
        total=len(self.qid)
        self.match_rate=round(100*(total-no)/total)
        tj_txt='自有题库搜到{own}题，公共题库搜到{comm}题，网络数据库搜到{wdb}题，网页搜索搜到{ws}题\n未搜到答案{no}题 合计有{total}题\n预计正确率：{rate}%'
        tj=tj_txt.format(own=own,comm=comm,wdb=wdb,ws=ws,no=no,
                         total=total,rate=self.match_rate)
        timestr=time.strftime("%Y%m%d_%H%M%S", time.localtime())
        fp=txtpath+'考题答案_%s.txt'%timestr
        writetxt=title+'\n\n'+tj+'\n\n'+writetxt
        with open(fp,'w',encoding='utf-8') as f:
            f.write(writetxt)
            print(fp,'已生成')
        msg=boxmsg('答案匹配已完成',CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        print(tj)
        if not e2e('HSJ_匹配的答案_%s'%self.user,'考试答案数据',fps=[fp]):
            self.logger.error('Failed to send exam_answer')
        return all_answer_lst
    def get_symb_answer(self,match,ops):
        if not match:return []
        symb_answers=[]
        ABCD_ops_lst=symb_options(ops)
        for answer in match[tk_col['answer_txt']]:
            one=process.extractOne(answer,ops,scorer=fuzz.UWRatio)
            p=ops.index(one[0])
            symb_one=ABCD_ops_lst[p]
            symb_answers.append(symb_one)
            symb_answers.sort(key=lambda x:x[0])
        return symb_answers
    def get_format_answer(self,match,qid,q_option_lst):
        dic={}
        answer_lst=[]
        dic["questionid"]=qid
        dic["type"]=1
        dic["answers"]=answer_lst
        if not match:return dic
        ops=[op["optionCont"] for op in q_option_lst]
        for answer in match[tk_col['answer_txt']]:
            one=process.extractOne(answer,ops,scorer=fuzz.UWRatio)
            p=ops.index(one[0])
            qo=q_option_lst[p]
            answer_lst.append(qo["questionNo"])
        dic["answers"]=answer_lst
        return dic
    def encode_answer(self,answerdic,timestamp):
        if not answerdic["answers"]:return None
        dic=answerdic.copy()
        dic["answers"]=[]
        timestamp=int(timestamp)
        dic["oldAnswer"]=answerdic["answers"]
        for x in dic["oldAnswer"]:
            an=int(answerdic["questionid"])%1000+x*13
            chcode=(timestamp%10000)*an
            dic["answers"].append(chcode)
        return dic
    def encode_all_answer(self,answer_lst,ts):
        enc_answer_lst=[]
        for x in answer_lst:
            enc_answer=self.encode_answer(x,ts)
            enc_answer_lst.append(enc_answer)
        return enc_answer_lst
    def modify_answer(self,flow,answer_lst,enc=True):
        msg=boxmsg('答题机器人正在修正答案',CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        txt=urllib.parse.unquote(flow.request.text)
        j=dict(urllib.parse.parse_qsl(txt))
        studentanswer=j['answer']
        if not enc:
            jstudent=json.loads(studentanswer,encoding='utf-8')
            join_answer=self.join_robot_student(answer_lst,jstudent)
            j['answer']=json.dumps(join_answer).replace(' ','')
        else:
            ts=int(j['endTime'])
            answer=self.encode_all_answer(answer_lst,ts)
            e=AESCipher()
            studentanswer=studentanswer.replace(' ','+')
            studentanswer=e.decrypt(studentanswer)
            jstudent=json.loads(studentanswer,encoding='utf-8')
            join_answer=self.join_robot_student(answer,jstudent)
            answertxt=json.dumps(join_answer).replace(' ','')
            j['answer']=e.encrypt(answertxt).decode()
        self.clear_sblst()
        return j
    def join_robot_student(self,robot_answer,student_answer):
        r_a_qid=[x["questionid"] for x in robot_answer]
        s_a_qid=[x["questionid"] for x in student_answer]
        joinanswerlst=[]
        for q in self.qid:
            if q in r_a_qid:
                joinanswerlst.append(robot_answer[r_a_qid.index(q)])
            elif q in s_a_qid:
                joinanswerlst.append(student_answer[s_a_qid.index(q)])
        return joinanswerlst
    def adjust_rate(self,answer_lst,):
        msg=boxmsg('正在检查正确率',CN_zh=True)
        print(msg)
        self.logger.debug(msg)
        if self.match_rate >= self.rate_min:
            if self.email and (self.email != '12345678@qq.com'):
                e2e('答题匹配好消息','正确率超过预定值！！！',to=[self.email])
        if self.match_rate > self.rate_max:
            print('正确率高于设定值，需要调小一点')
            ownnum=len(self.sbqid)
            commnum=len(self.sbstem)
            wdbnum=len(self.sbwebdb)
            wsnum=len(self.sbwebpage)
            nonum=len(self.notfound)
            total=ownnum+commnum+wdbnum+wsnum+nonum
            n=int(total*(self.match_rate-self.rate_max)/100)
            if self.DEBUG:print('需要削减的数量：',n)
            n_qid_lst=[]
            if n<nonum:
                n_qid_lst=random.sample(self.notfound,n)
            elif n<nonum+wsnum:
                n_qid_lst=self.notfound+random.sample(self.sbwebpage,n-nonum)
            elif n<nonum+wsnum+wdbnum:
                n_qid_lst=self.notfound+self.sbwebpage+random.sample(self.sbwebdb,n-nonum-wsnum)
            elif n<nonum+wsnum+wdbnum+commnum:
                n_qid_lst=self.notfound+self.sbwebpage+self.sbwebdb+random.sample(self.sbstem,n-nonum-wsnum-wdbnum)
            elif n<nonum+wsnum+wdbnum+commnum+ownnum:
                n_qid_lst=self.notfound+self.sbwebpage+self.sbwebdb+self.sbstem+random.sample(self.sbqid,n-nonum-wsnum-wdbnum-commnum)
            adjust_answer_lst=[x for x in answer_lst if x["questionid"] not in n_qid_lst]
            if self.DEBUG:print('调整后的个数：',len(adjust_answer_lst))
            return adjust_answer_lst
        elif self.match_rate > self.rate_min:
            print('正确率本来就在区间中，不需要调整')
            return answer_lst
        else:
            print('正确率低于设定范围，需要自己做题来提高，自求多福吧！')
            return answer_lst
class Bumblebee():
    def __init__(self,datafile='comm.data',encrpt=True,debug=1):
        self.DEBUG=debug
        self.path0=path0
        self.datafile=datafile
        self.qids=[]
        self.stem_options=[]
        self.questions=[]
        self.dpath=datapath+self.datafile
        self.loaddata(encrpt)
    def loaddata(self,encrpt=True):
        if os.path.exists(self.dpath) is False:
            print('%s文件不存在'%self.datafile)
            self.savedata(encrpt=encrpt)
            return
        with open(self.dpath,mode='r',encoding='utf-8') as f:
            t=f.read()
        try:
            j=json.loads(t,encoding='utf-8')
        except:
            t=self.base64decode(t)
            j=json.loads(t,encoding='utf-8')
        self.qids=j['题库id']
        self.questions=j['题库']
        if j['题库']:
            if type(j['题库'][0][tk_col['options']]) is list:
                print('所加载题库为旧版本题库类型，正在强制转换')
                for i,x in enumerate(self.questions):
                    self.questions[i][tk_col['options']]='\n'.join(self.questions[i][tk_col['options']])
                print('转换后样式：\n',self.questions[0])
                self.savedata(encrpt=encrpt)
        self.stem_options=[q[tk_col['stem']]+'\n'+q[tk_col['options']] 
                            for q in self.questions]
        self.tips='{fn}题库加载完成，共{total}题'.format(fn=self.datafile[-9:],
                                                       total=len(self.questions))
        print(self.tips)
    def savedata(self,encrpt=True,display=True):
        data={}
        data["题库id"]=self.qids
        data['题库']=self.questions
        with open(self.dpath,mode='w',encoding='utf-8') as f:
            txt=json.dumps(data,ensure_ascii=False)
            if encrpt:txt=self.base64encode(txt)
            f.write(txt)
            if display:print('题库数据%s已保存'%self.datafile)
            pass
    def base64encode(self,txt):
        enb64=base64.b64encode(txt.encode())
        en64=enb64.decode()
        return en64
    def base64decode(self,en64):
        btxt=base64.b64decode(en64.encode())
        txt=btxt.decode()
        return txt
    def search_by_questionid(self,qid):
        if self.DEBUG:print('正在%s库进行qid匹配……'%self.datafile)
        if qid in self.qids:
            p=self.qids.index(qid)
            match=self.questions[p]
            return match
        else:
            return None
    def search_by_stem_options(self,stem,options):
        if self.DEBUG:print('正在%s库进行相似度匹配……'%self.datafile)
        base_score=70
        option_score=80
        searchtxt='\n'.join([stem,options])
        print('-'*20)
        print(searchtxt)
        one=process.extractOne(searchtxt,
                               self.stem_options,
                               scorer=fuzz.UWRatio)
        if one is None :return None
        if self.DEBUG:print('题干+选项匹配得分：',one[1])
        print('题目匹配相似度：%s%%'%one[1])
        if one[1]<base_score:return None
        p=self.stem_options.index(one[0])
        match=self.questions[p]
        if self.DEBUG:print('一次匹配结果\n',match)
        score=fuzz.token_sort_ratio(options, match[tk_col['options']])
        if self.DEBUG:print('纯选项匹配得分：',score)
        print('选项匹配相似度：%s%%'%score)
        if score>=option_score:
            print('匹配答案：',match[tk_col['answer_txt']])
            return match
        else:
            if self.DEBUG:print('未匹配上数据\n----------')
            print('未匹配到答案！')
            return None
            top3=process.extract('\n'.join([stem,options]),
                            self.stem_options,
                            limit=3)
            if self.DEBUG:print('top3=',top3)
            top3options=['\n'.join(x[0].splitlines()[1:]) for x in top3]
            if self.DEBUG:print('top3options',top3options)
            top3option_one=process.extractOne(options,top3options,
                                              scorer=fuzz.UWRatio)
            if self.DEBUG:print('前3名中纯选项匹配最高得分：',top3option_one[1])
            pt=top3options.index(top3option_one[0])
            p=self.stem_options.index(top3[pt][0])
            match=self.questions[p]
            if self.DEBUG:print('二次匹配的结果\n',match)
            score2=fuzz.token_sort_ratio('\n'.join([stem,options]),
                    '\n'.join([match[tk_col['stem']],match[tk_col['options']]]))
            if self.DEBUG:print('对二次匹配结果检验得分：',score2)
            if score2>=option_score:
                return match
            else:
                return None
class DataCat():
    def __init__(self,debug):
        self.DEBUG=debug
        pass
    def search_by_webdb(self,stem,symb_ops_str):
        if self.DEBUG:print('正在网络数据库中进行搜索匹配……')
        return None
class SpiderMan():
    def __init__(self,debug):
        self.DEBUG=debug
        pass
    def search_by_webpage(self,stem,symb_ops_str):
        if self.DEBUG:print('正在进行网页搜索匹配……')
        return None
class MyWatchDog():
    def __init__(self,user,method,email,rate_min,rate_max):
        self.user=user
        self.rate_min=rate_min
        self.rate_max=rate_max
        self.method=method
        self.path0=path0
        self.email=email
        self.confpathname=confpath+"default.ini"
        self.conf=configparser.ConfigParser()
        self.conf.read(self.confpathname, encoding="utf-8")
        self.DEBUG=self.conf.getint('Work-Mode','debug')
        self.saveconfig()
    def choice(self):
        fp=confpath+'choice.txt'
        with open(fp,'r',encoding='utf-8') as f:
            txt=f.read()
        choicenum=input(txt)
        choicenum=choicenum.strip()
        if choicenum=='1':
            print('-'*20)
            print('你选择的是  [1]  检查软件版本并更新程序')
            print('-'*20)
            pass
        elif choicenum=='2':
            print('-'*20)
            print('你选择的是  [2]  更新题库')
            print('-'*20)
            pass
        elif choicenum=='3':
            print('-'*20)
            print('你选择的是  [3]  更新程序后再更新题库')
            print('-'*20)
            pass
        elif choicenum=='4' or choicenum=='':
            print('-'*20)
            print('你选择的是  [4]  准备考试')
            print('-'*20)
            self.login()
            pass
        else:
            print('您的输入错误！')
    def showlog(self,fn=None):
        if fn is None:
            fp=confpath+'wzh_slant.txt'
        else:
            fp=confpath+fn
        if not os.path.exists(fp):return
        with open(fp,mode='r',encoding='utf-8') as f:
            mylog=f.read()
        print(mylog)
    def login(self):
        print('%s正在连线答题机器人……'%self.user[-4:])
        if self.check_user() and self.check_date():
            print('[连线成功]')
            self.showlog()
            cmdtxt='mitmdump -s {path}mitm_test.py'.format(path=path0)
            if platform.system()=='Windows':
                os.system(cmdtxt)
            elif platform.system()=='Linux':
                Popen(cmdtxt,shell=True)
        else:
            print('登录失败！')
    def saveconfig(self):
        self.conf.set('UserInf','user',self.user)
        self.conf.set('Correctrate-Setting','max',str(self.rate_max))
        self.conf.set('Correctrate-Setting','min',str(self.rate_min))
        self.conf.set('Answer-Method','Method',self.method)
        self.conf.set('Notice','email',self.email)
        self.conf.write(open(self.confpathname, "w"))
        if self.DEBUG:print('配置文件{}已保存'.format(self.confpathname))
    def check_date(self):
        return check_date()
    def check_user(self):
        return check_user(self.user)
        pass
if __name__=='__main__':
    import logger
    mylogger=logger.logger()
    robot=AnswerRobot(mylogger)
    pass