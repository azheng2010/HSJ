#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,json
from comm import datapath,tk_col,base64encode,base64decode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
def loaddata(datafile,encrpt=True):
    dpath=datapath+datafile
    if os.path.exists(dpath) is False:
        print('%s文件不存在'%datafile)
        qids=[]
        questions=[]
        savedata(qids,questions,datafile,encrpt=encrpt,display=True)
        return
    with open(dpath,mode='r',encoding='utf-8') as f:
        t=f.read()
    try:
        j=json.loads(t,encoding='utf-8')
    except:
        print(datafile,'加密文档')
        j=json.loads(base64decode(t),encoding='utf-8')
    qids=j['题库id']
    questions=j['题库']
    if datafile.split(sep='.')[0].isnumeric():
        fn=datafile[-9:]
    else:
        fn=datafile
    tips='{fn}题库加载完成，共{total}题'.format(fn=fn,total=len(questions))
    print(tips)
    return qids,questions
def savedata(qids,questions,datafile,encrpt=True,display=True):
    dpath=datapath+datafile
    data={}
    data["题库id"]=qids
    data['题库']=questions
    with open(dpath,mode='w',encoding='utf-8') as f:
        txt=json.dumps(data,ensure_ascii=False)
        if encrpt:txt=base64encode(txt)
        f.write(txt)
        if display:print('题库数据%s已保存'%datafile)
        pass
def log_decoder(fp,fns):
    if not os.path.exists(fp):
        print('{fp}目录不存在'.format(fp=fp))
        return
    for fn in fns:
        if not os.path.exists(fp+fn):
            print(fp+fn,'文件不存在')
            continue
        with open(fp+fn,'r') as f:#,encoding='utf-8'
            txt=f.read()
        fp2=fp+'decode'+os.path.sep
        if not os.path.exists(fp2):os.mkdir(fp2)
        with open(fp2+fn[:-4]+'_decoded'+fn[-4:],'a',encoding='utf-8') as f2:
            sep='------------------------------'
            lst=txt.split(sep=sep)
            for x in lst:
                k=x.strip().split(sep='\n')
                info=k[0]
                if 'INFO' in info:
                    msg=base64decode(k[1])
                else:
                    msg='\n'.join(k[1:])
                f2.write('\n'.join([info,msg,sep])+'\n')
        print(fp+fn,'解码完成')
def add_tiku(newdatafile,datafiles,encrpt=True):
    qids=[]
    questions=[]
    for d in datafiles:
        dqids,dquestions=loaddata(d)
        qids=qids+dqids
        questions=questions+dquestions
    savedata(qids,questions,newdatafile,encrpt=encrpt,display=True)
    savedata(qids,questions,newdatafile[:-5]+'（未加密）'+newdatafile[-5:],
             encrpt=False,display=False)
def tiku_deduplication(datafile0,datafiles1,encrpt=True):
    if os.path.exists(datapath+datafile0):
        qids0,questions0=loaddata(datafile0)
    else:
        qids0,questions0=[],[]
    stem_options_0_lst=[q[tk_col['stem']]+'\n'+q[tk_col['options']] for q in questions0]
    datafilesnum=len(datafiles1)
    for ix,datafile1 in enumerate(datafiles1):
        qids1,questions1=loaddata(datafile1)
        questionsnum=len(questions1)
        for iy,q1 in enumerate(questions1):
            print('='*20)
            print('当前进度：[%s/%s][%s/%s]'%(ix+1,datafilesnum,iy+1,questionsnum))
            qid1=q1[tk_col['qid']]
            stem_options=q1[tk_col['stem']]+'\n'+q1[tk_col['options']]
            if (qid1 in qids0) and (qid1 != '000000'):
                print('qid相同',qid1)
                continue
            one=process.extractOne(stem_options,stem_options_0_lst,
                                   scorer=fuzz.UWRatio)
            if one:
                if one[1]>=99:
                    print('相似度：',one[1])
                    print(qid1,stem_options)
                    print('-'*10)
                    stem_options_0_lst.index(one[0])
                    print(one[0])
                    continue
                else:
                    stem_options_0_lst.append(stem_options)
                    questions0.append(q1)
                    qids0.append(q1[tk_col['qid']])
            else:
                stem_options_0_lst.append(stem_options)
                questions0.append(q1)
                qids0.append(q1[tk_col['qid']])
        savedata(qids0,questions0,datafile0,encrpt=encrpt,display=True)
def test():
    datafile0='合并题库.data'
    datafiles1=['13507499021.data','00103007575.data',]
    tiku_deduplication(datafile0,datafiles1,encrpt=True)
def decode_logfiles():
    fp='C:/Users/wzh/Desktop/'
    fns=['2019-04-03_00_07_14.log',]
    log_decoder(fp,fns)
def merge_questions():
    datafiles=['15533259831.data','17732836213.data','18533501113.data',]
    newdatafile='合并后新题库.data'
    add_tiku(newdatafile,datafiles,encrpt=False)
    x,y=loaddata(newdatafile)
if __name__=="__main__":
    decode_logfiles()
    pass