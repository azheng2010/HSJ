#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import regex as re
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
class ASKLIB():
    def __init__(self,maxnum=3,score=70):
        self.headers={"user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",}
        self.url0='https://www.asklib.com'
        self.url='https://www.asklib.com/s/'
        self.__keyword=''
        self.__maxdisplay= maxnum 
        self.fuzz_score=score
        self.__realurl_list=[]
        self.__result_list=[]
        self.sort_href_lst=[]
    @property
    def keyword(self):
        return self.__keyword
    @property
    def maxdisplay(self):
        return self.__maxdisplay
    @property
    def realurl_list(self):
        return self.__realurl_list
    def set_keyword(self,keyword):
        self.__keyword=keyword
        self.__realurl_list=[]
        self.__result_list=[]
        pass
    def default_asklib(self):
        self.__keyword=''
        self.__realurl_list=[]
        self.__result_list=[]
        self.sort_href_lst=[]
    def search(self,keyword=''):
        if keyword=='':
            keyword=self.__keyword
        else:
            self.__keyword=keyword
        r=requests.get(self.url+keyword,headers=self.headers)
        if r.status_code==200:
            html=r.text
        else:
            return
        soup = BeautifulSoup(html, 'lxml')
        result_lst=soup.findAll(name='div',attrs={"class":"p30 bgW mb10 pb0"})
        for x in result_lst:
            question=x.find(name='h2',attrs={"class":"F18 ti2m LH_40"}).text
            start=question.find('[')
            end=question.find(']',start)
            key_lst=['问答题','简答题','填空题','分析','判断题','材料题','论述题']
            if self.isnotchoice(key_lst,question[:end+1]):continue
            question=question[end+1:]
            question=question.strip()
            score=fuzz.ratio(question, keyword)
            href=x.find(name='a').attrs['href']
            url_real=self.url0+href
            self.__realurl_list.append((score,url_real,question))
        self.sort_href_lst=self.score_sort()
        if self.maxdisplay<len(self.sort_href_lst):
            self.sort_href_lst=self.sort_href_lst[:self.maxdisplay]
    def isnotchoice(self,key_lst,headstring):
        for x in key_lst:
            if x in headstring:
                return True
        return False
    def score_sort(self):
        lst=[x for x in self.__realurl_list if x[0]>self.fuzz_score]
        lst=sorted(lst, key=lambda x: x[0])
        lst.reverse()
        return lst
    def parser_search(self):
        answers_lst=[]
        for url_real in self.sort_href_lst:
            r=requests.get(url_real[1],headers=self.headers)
            if r.status_code==200:
                html=r.text
            else:
                return
            soup = BeautifulSoup(html, 'lxml')
            result=soup.find(name='div',attrs={"class":"listbg"})
            answer_tag=result.find(name='div',attrs={"class":"listtip"})
            answer=answer_tag.text
            if '答案' in answer:
                answer=re.compile(r"[^A-Ga-g]").sub("", answer)
            result=soup.find(name='h1',attrs={"class":"F18 ti2m LH_40"})
            stem=result.text
            start=stem.find('[')
            end=stem.find(']',start)
            stem=stem[end+1:].strip()
            result=soup.find(name='p',attrs={"class":"F18 ml2m LH_40"})
            if result:
                lst=result.find_all(text=True)
                options='\n'.join(lst)
            else:
                options=''
            if len(options)<12:
                result=soup.find(name='div',attrs={"class":"essaytitle txt_l "})
                lst=result.find_all(text=True)
                lst0=[x.strip() for x in lst if x not in ['',' ','\n','\ue6ad','\ue622','\ue61a']]
                lst1=[x for x in lst0 if (x[0] in 'ABCDEFGabcdefg') and len(x)>3]
                options='\n'.join(lst1)
            answer_txt=self.pick_txt_answer(list(answer),options.splitlines())
            answers_lst.append([stem,options,answer,answer_txt])
        return answers_lst
    def search_answer(self,search_question,options=None):
        if not search_question :
            self.default_asklib()
            return
        self.search(search_question)
        if not self.sort_href_lst :
            self.default_asklib()
            return
        answers_lst=self.parser_search()
        qcontents=[x[0]+'\n'+x[1] for x in answers_lst]
        qstems=[x[0] for x in answers_lst]
        if options:
            one_tupp=process.extractOne(search_question+options, choices=qcontents, scorer=fuzz.UWRatio)
            answer=answers_lst[qcontents.index(one_tupp[0])]
        else:
            one_tupp=process.extractOne(search_question, choices=qstems, scorer=fuzz.UWRatio)
            answer=answers_lst[qstems.index(one_tupp[0])]
        if one_tupp[1]<self.fuzz_score:
            self.default_asklib()
            return
        print('匹配值：%s\n题目：%s\n答案：%s'%(one_tupp[1],one_tupp[0],answer[2]))
        self.default_asklib()
        return answer
    def pick_txt_answer(self,answer_lst,options_lst):
        print('====================pick_txt_answer===================')
        print(options_lst)
        print('==========================')
        answer_txt_lst=[]
        for option in options_lst:
            for x in answer_lst:
                if option.startswith(x):
                    res=re.compile(r'(?<=^[A-H]\s*[\.、．]\s*).*').search(option)
                    if res:
                        answer_txt=res.group()
                    else:
                        answer_txt=option
                    answer_txt=answer_txt.strip()
                    answer_txt_lst.append(answer_txt)
                    break
        return answer_txt_lst
    def pick_ABCD_answer(self,answer_txt_lst,options_lst):
        answer_lst=[]
        for answertxt in answer_txt_lst:
            one_tupp=process.extractOne(answertxt, choices=options_lst, scorer=fuzz.UWRatio)
            if one_tupp[1]<self.fuzz_score:return ''
            answer_lst.append(one_tupp[0].strip()[0])
        return ''.join(answer_lst)
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
                        stempinyin=str_to_pinyin(stem)
                        self.questions.append([qid,stem,answertxt,stempinyin,answer2,options,type_name,classification])
                    print('%s目前题目有%s题'%(self.count,len(self.qids)))
            elif j['tip']=='用户需要登录!':
                self.NEEDLOGIN=True
                flag,msg,self.sessionid,info=login_check(self.user)
            else:
                print(j["tip"])
    def parser(self,questionRelation):
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
    def parser_login(self,account):
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
if __name__=='__main__':
    pass