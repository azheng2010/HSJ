#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import regex as re
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
class MyAPP():
    def __init__(self,datafile=None):
        self.method=''
        self.user=''
        self.freeuser=False
        self.limitcount=0
        self.date_end_str=''
        self.count=0
        self.usability=False
        self.sessionid=''
        self.NEEDLOGIN=True
        self.testunits=[]
        self.qids=[]
        self.questions=[]
        if datafile is None:
            self.dpath='data/'+'questions.data'
        else:
            self.dpath='data/'+datafile
def login(self,user,pwd=None):
    print('{user}正在登录中……'.format(user=user))
    user_agent='Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36'
    self.user=user
    if not pwd:pwd=user[-6:]
    url='http://admin.hushijie.com.cn/account/app/login'
    pdata={
            'username':user,
            'password':pwd,
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
            self.NEEDLOGIN=False
            info=self.parser_login(j['account'])
            print('登录成功',self.sessionid)
            return True,j["tip"],self.sessionid,info
        else:
            print(j["tip"])
            return False,j["tip"],None,None
def login_check(self,user,pwd=None):
    print('正在登录中……')
    user_agent='Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36'
    if pwd is None:pwd=user[-6:]
    url='http://admin.hushijie.com.cn/account/app/login'
    pdata={
            'username':user,
            'password':pwd,
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
            info=self.parser_login(j['account'])
            info["密码"]=pwd
            return True,j["tip"],self.sessionid,info
        else:
            print(j["tip"])
            return False,j["tip"],None,None
def get_testunitid(self):
    url='http://admin.hushijie.com.cn/mobile/testunit/student/practice/query'
    params={
            'page':1,
            'pageSize':200,
            'session_id':self.sessionid,
            }
    headers={
            'Host':'admin.hushijie.com.cn',
            'Connection':'keep-alive',
            'Accept':'application/json, text/plain, */*',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
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
                if status>-1:
                    self.testunits.append((testunitid,testunitname))
                print(testunitid,testunitname,endtime)
        else:
            print(j["tip"])
def get_testunit_questions(self,testunit):
    url='http://admin.hushijie.com.cn/testunit/student/answer/start'
    postdata={
            'testunitid':testunit,
            'session_id':self.sessionid,
            }
    headers={
            'Host':'admin.hushijie.com.cn',
            'Connection':'keep-alive',
            'Accept':'application/json, text/plain, */*',
            'Origin':'file://',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
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
            for x in qlst:
                qid,stem,answertxt,answer2,options,type_name=self.parser(x)
                self.count+=1
                if qid not in self.qids:
                    self.qids.append(qid)
                    stempinyin=self.str_to_pinyin(stem)
                    self.questions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                print('%s目前题目有%s题'%(self.count,len(self.qids)))
        elif j['tip']=='用户需要登录!':
            self.NEEDLOGIN=True
            flag,msg,self.sessionid,info=login_check(self.user)
        else:
            print(j["tip"])
def get_testunit_questions(sessionid,testunit):
    url='http://admin.hushijie.com.cn/testunit/student/answer/start'
    postdata={
            'testunitid':testunit,
            'session_id':sessionid,
            }
    headers={
            'Host':'admin.hushijie.com.cn',
            'Connection':'keep-alive',
            'Accept':'application/json, text/plain, */*',
            'Origin':'file://',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
            'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,en-US;q=0.9',
            'Cookie':'session_id=%s'%sessionid,
            'X-Requested-With':'cn.com.hushijie.app',
            }
    r=requests.post(url,headers=headers,data=postdata)
    if r.status_code==200:
        j=r.json()
        if j["ret"]==1:
            qlst=j["examPaperFullInfo"]["questionRelations"]
            classification=j["examPaperFullInfo"]["name"]
            for x in qlst:
                qid,stem,answertxt,answer2,options,type_name=parser(x)
                self.count+=1
                if qid not in self.qids:
                    self.qids.append(qid)
                    stempinyin=str_to_pinyin(stem)
                    self.questions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                print('%s目前题目有%s题'%(self.count,len(self.qids)))
        elif j['tip']=='用户需要登录!':
            self.NEEDLOGIN=True
            flag,msg,self.sessionid,info=login_check(self.user)
        else:
            print(j["tip"])
def parser(questionRelation):
    typedic={1:'单选',2:'多选',3:'判断',}
    x=questionRelation
    qid=x["questionid"]
    stem=x['question']['stem']
    optionlst=x['question']['questionOptionList']
    qtype=x['question']['questiontype']
    answerNodic={1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',8:'H',9:'I'}
    answertxt=[]
    answer2=[]
    options_dic={}
    for y in optionlst:
        options_dic[y["questionNo"]]=answerNodic[y["questionNo"]]+'. '+y['optionCont']
        if y['answer']==True and qtype==1:
            answertxt.append(y['optionCont'])
            answer2.append(answerNodic[y["questionNo"]])
        if y['answer']==True and qtype==2:
            answertxt.append(y['optionCont'])
            answer2.append(answerNodic[y["questionNo"]])
        if y['answer']==True and qtype==3:
            answertxt.append(y['optionCont'])
            answer2.append(answerNodic[y["questionNo"]])
    answer2.sort()
    p=list(options_dic.keys())
    p.sort()
    options='\n'.join([options_dic[z] for z in p])
    type_name=typedic[qtype]
    return qid,stem,answertxt,answer2,options,type_name
def parser_login(account):
    dic={}
    dic["姓名"]=account["realname"]
    dic["性别"]=account["sexName"]
    dic["电话"]=account["phone"]
    dic["工号"]=account["workid"]
    dic["职称"]=account["professionalTitleName"]
    dic["职业"]=account["jobName"]
    dic["最高学历"]=account["maxEducationName"]
    dic["所属部门"]=account["departmentName"]
    dic["所属医院名称"]=account["hospitalName"]
    dic["编制特性"]=account["staffPropertyName"]
    dic["医院代码"]=account["hospitalId"]
    dic["护士等级"]=account["nurseLevelName"]
    dic["是否部门主管"]=account["departmentManeger"]
    dic["是否医院主管"]=account["hospitalManager"]
    return dic
def commit_answer(self,testunitid,answerlist_str):
    url='http://admin.hushijie.com.cn/testunit/student/answer/commit'
    headers={
            'Host':'admin.hushijie.com.cn',
            'Connection':'keep-alive',
            'Accept':'application/json, text/plain, */*',
            'Origin':'file://',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
            'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,en-US;q=0.9',
            'Cookie':'session_id=%s'%self.sessionid,#'session_id=b3abec9a1b8abcbcf58d14d3460133edf65eadac87f6b86263f3b90e76b2e8f3',
            'X-Requested-With':'cn.com.hushijie.app',
            }
    pdata={
            'testunitid':testunitid,
            'answer':answerlist_str,
            'session_id':self.sessionid,
            'commit_type':'overList',
            'clientType':'app',
            'leaveTimes':'-1',
            'curLeaveTimes':'-6',
            'limitTime':'120',
            'curCountDown':'',
            'endTime':'',
            }
    r=requests.post(url,headers=headers,data=pdata)
    if r.status_code==200:
        j=r.json()
        if j["ret"]==1:
            print('考试数据提交成功')
            return True
        else:
            print(j["tip"])
            return False
def get_score(self,testunitid):
    url='http://admin.hushijie.com.cn/testunit/student/transcript/get'
    headers={
            'Host':'admin.hushijie.com.cn',
            'Connection':'keep-alive',
            'Accept':'application/json, text/plain, */*',
            'Origin':'file://',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.1.0; MI 6X Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36',
            'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,en-US;q=0.9',
            'Cookie':'session_id=%s'%self.sessionid,#'session_id=b3abec9a1b8abcbcf58d14d3460133edf65eadac87f6b86263f3b90e76b2e8f3',
            'X-Requested-With':'cn.com.hushijie.app',
            }
    pdata={
            'testunitid':testunitid,
            'session_id':self.sessionid,#'b3abec9a1b8abcbcf58d14d3460133edf65eadac87f6b86263f3b90e76b2e8f3',
            }
    r=requests.post(url,headers=headers,data=pdata)
    if r.status_code==200:
        j=r.json()
        if j["ret"]==1:
            score=j["transcript"]["transcript"]
            print('考试得分：%d'%score)
            return score
        else:
            print(j["tip"])
            return 0
if __name__=="__main__":
    pass