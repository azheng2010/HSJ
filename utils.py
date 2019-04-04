#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,json
from comm import txtpath,read_start_response
import random
from models import Baymax
from api import ASKLIB
def match_answer(logger):
    num=0
    yes=[]
    no=[]
    so=[]
    print('正在匹配答案中……')
    myapp=Baymax(datapath='%s.data'%user,encrpt=True)
    mycomm=Baymax(datapath='comm.data',encrpt=False)
    sxbst=SangXueBaSouTi(user='15131165536',password='165536',update=True)
    askapp=ASKLIB()
    exam_lst=read_start_response()
    all_answer_lst=[]
    for x in exam_lst:
        num+=1
        qid=x["questionid"]
        stem=x["question"]["stem"]
        q_option_lst=x["question"]["questionOptionList"]
        ops=[op["optionCont"] for op in q_option_lst]
        print('考题%s. %s'%(num,stem))
        if qid in myapp.qids:
            p=myapp.qids.index(qid)
            match=myapp.questions[p]
            print('【答案】 [%s]'%('\n'.join(match[2])))
            print('-'*20)
            dic={}
            answer_lst=[]
            for qo in q_option_lst:
                if qo["optionCont"] in match[2]:
                    answer_lst.append(qo["questionNo"])
            dic["questionid"]=qid
            dic["type"]=1
            dic["answers"]=answer_lst
            all_answer_lst.append(dic)
            yes.append((qid,num))
        else:
            binggo=False
            tqid,tstem,tanswer,tanswer2,toptions=parser(x)
            tstempinyin=str_to_pinyin(tstem)
            answerlst=askapp.search_answer(tstem,options=toptions)
            if answerlst:
                answer=askapp.pick_ABCD_answer(answerlst[3],toptions.splitlines())
                answertxt=askapp.pick_txt_answer(list(answer),toptions.splitlines())
                if answer:
                    tanswer=answertxt
                    tanswer2=list(answer)
                    dic={}
                    answer_lst=[]
                    for qo in q_option_lst:
                        if qo["optionCont"] in tanswer:
                            answer_lst.append(qo["questionNo"])
                    dic["questionid"]=qid
                    dic["type"]=1
                    dic["answers"]=answer_lst
                    if answer_lst:
                        all_answer_lst.append(dic)
                        so.append((qid,num))
                        binggo=True
                    else:
                        print('【问答库】未找到答案！')
                else:
                    print('【问答库】未找到答案！')
            if not binggo:
                q,a1,a2=sxbst.search_answer(tstem,options=toptions)
                if q:
                    tanswer=a1
                    tanswer2=a2
                    dic={}
                    answer_lst=[]
                    for qo in q_option_lst:
                        if qo["optionCont"] in tanswer:
                            answer_lst.append(qo["questionNo"])
                    dic["questionid"]=qid
                    dic["type"]=1
                    dic["answers"]=answer_lst
                    if answer_lst:
                        print('【答案】',answer_lst)
                        all_answer_lst.append(dic)
                        so.append((qid,num))
                    else:
                        no.append((qid,num))
                        print('【搜题吧】未找到答案！')
                else:
                    no.append((qid,num))
                    print('【搜题吧】未找到答案！')
            if qid not in mynew.qids:
                mynew.qids.append(tqid)
                mynew.questions.append([tqid,tstem,tanswer,tstempinyin,tanswer2,toptions])
    print('问答库搜题 %s题'%len(so))
    print('总题数：%s\n已匹配%s题\t未匹配%s题\n匹配率：%.0f%%'%(
        len(exam_lst),len(yes)+len(so),len(no),(len(yes)+len(so))/len(exam_lst)*100))
    mynew.savedata(encrpt=False,display=False)
    return all_answer_lst,yes,so,no,[myapp.score_min,myapp.score_max]
def del_appVersion(txt):
    lst=txt.split(sep='&')
    lst2=[x for x in lst if not x.startswith('appVersion')]
    txt='&'.join(lst2)
    return txt
def modify_answer(logger,default_answer=None,no=None) ->str:
    head,answer,tail=read_commit_answer()
    head=del_appVersion(head)
    tail=del_appVersion(tail)
    answer=answer.replace('&answer=','')
    ks_answer_lst=[]
    no_answer_lst=[]
    if no :
        no_qid_lst=[x[0] for x in no]
        for ks in ks_answer_lst:
            if ks["questionid"] in no_qid_lst:
                no_answer_lst.append(ks)
    if not default_answer:
        answer_lst,yes,so,no,score_lst=match_answer()
    else:
        answer_lst=default_answer
    answer_lst=answer_lst+no_answer_lst
    modified_answer='&answer='+json.dumps(answer_lst).replace(' ','')
    t=head+modified_answer+tail
    with open(path0+'commit_modify.txt',mode='w',encoding='utf-8') as f:
        f.write(t)
    return t
def match_score(logger,answer_lst,yes,so,no,score_lst):
    num_yes=len(yes)
    num_so=len(so)
    num_no=len(no)
    num_total=num_yes+num_so+num_no
    rate=(num_yes+num_so)/num_total*100
    print('num_yes=',num_yes,'num_so=',num_so,'num_no=',num_no,'num_total=',num_total)
    print('正确率=%s'%rate)
    if rate<score_lst[0]:
        print('正确率低于期望值，需要自己做题增加正确率')
        print('未找到答案的题号：\n%s'%([x[1] for x in no]))
        return answer_lst
    if score_lst[0] <= rate <= score_lst[1]:
        print('符合期望要求')
        return answer_lst
    if rate > score_lst[1]:
        print("正确率超过设定值，需要调减一下")
        n=int(num_total*(rate-score_lst[1])/100)
        if n<=num_so:
            lst=random.sample(so,n)
            lst=[x[0] for x in lst]
            pass
        if n>num_so:
            lst=so+random.sample(yes,n-num_so)
            lst=[x[0] for x in lst]
        for one in answer_lst:
            if one["questionid"] in lst:
                one["answers"]=[]
        return answer_lst
    pass
if __name__=='__main__':
    pass