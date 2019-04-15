#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from pypinyin import pinyin,Style
from models import HSJAPP
from 护世界操作工具 import tiku_deduplication
def txt_to_questions(fp):
    pid='000000'
    note=fp.split(sep='/')[-1][:-4]
    f=open(fp,'r',encoding='utf-8')
    lines=f.readlines()
    f.close()
    start=False
    options=[]
    stem=''
    answer=[]
    data_lst=[]
    for x in lines:
        x=x.replace('--------------------','')
        if x.startswith(('1','2','3','4','5','6','7','8','9')):
            if stem and answer:
                if not options:
                    options=['A、正确', 'B、错误']
                    leixing='判断'
                elif len(answer)==1:
                    leixing='单选'
                else:
                    leixing='多选'
                stem_pinyin=str_to_pinyin(stem)
                answer_txt=pick_txt_answer(answer,options)
                lst=[pid,stem,answer_txt,stem_pinyin,answer,'\n'.join(options),leixing,note]
                data_lst.append(lst)
                print(lst)
                print('-'*20)
                start=False
                options=[]
                stem=''
                answer=[]
            p0=x.find('（')
            p1=x.find('）')
            if p1>p0+1:
                t=x[p0+1:p1].strip()
                answer=list(t)
                stem=x[:p0+1]+x[p1:]
            else:
                stem=x.strip()
            p2=stem.find('.')
            stem=stem[p2+1:].strip()
            stem=stem.replace('【单】','').replace('【多】','')
            start=True
        elif x.startswith('【答案】'):
            answer=list(x[4:].strip())
            if answer:
                if answer[0]=='正':
                    answer=['A']
                elif answer[0]=='错':
                    answer=['B']
        elif x.startswith('【难度】'):
            pass
        elif x.startswith('【解析】'):
            start=False
            pass
        elif start:
            op=x.strip()
            if op:
                if op[0].upper() in "ABCDEFGHIJKLMNOPQ":
                    options.append(op)
        else:
            pass
    return data_lst
def str_to_pinyin(txt):
    symbols="""
          \n\r,.'"`~!@#$%^&*()_+-=;:?<>·！！@#￥%…&（）——、|【】{}“‘'；：？》《。，
            """
    txtCN=txt
    for sym in symbols:
        txtCN=txtCN.replace(sym,'')
    lst=pinyin(txtCN,style=Style.FIRST_LETTER)
    ft=''.join([x[0] for x in lst])
    return ft
def pick_txt_answer(answer_lst,options_lst):
    answer_txt_lst=[]
    for option in options_lst:
        for x in answer_lst:
            if option.startswith(x):
                answer_txt=option[2:].strip()
                answer_txt_lst.append(answer_txt)
                break
    return answer_txt_lst
if __name__=='__main__':
    myapp=HSJAPP('user1234567890',datafile='戎芹的题库.data',encrpt=True)
    data_all=[]
    fp_lst=['C:/Users/wzh/Desktop/222/中级主管护师_内科护理学.txt',
            'C:/Users/wzh/Desktop/222/高级主任护师_内科护理学.txt',
            'C:/Users/wzh/Desktop/222/内科护理学.txt',]
    for fp in fp_lst:
        data_all=data_all+txt_to_questions(fp)
    myapp.questions=myapp.questions+data_all
    myapp.qids=[x[0] for x in myapp.questions]
    myapp.savedata(encrpt=True)
    myapp.savedata(encrpt=False)
    print('共%s道题'%len(myapp.qids))
    tiku_deduplication('戎芹去重合并题库.data',['戎芹的题库.data'],encrpt=True)
    pass