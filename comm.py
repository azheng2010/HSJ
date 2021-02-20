#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import requests,csv
from html.parser import HTMLParser
import os, time, json, base64, platform
import demjson
import socket, urllib.request
from myaes import MYAES
from pypinyin import pinyin,Style
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
path0 = os.path.dirname(os.path.abspath(__file__)) + os.path.sep
datapath = os.path.join(path0, 'data') + os.path.sep
confpath = os.path.join(path0, 'conf') + os.path.sep
txtpath = os.path.join(path0, 'runtxt') + os.path.sep
logpath = os.path.join(path0, 'log') + os.path.sep
if not os.path.exists(datapath):os.makedirs(datapath)
if not os.path.exists(txtpath):os.makedirs(txtpath)
if not os.path.exists(logpath):os.makedirs(logpath)
if not os.path.exists(confpath):os.makedirs(confpath)
global M
global DBCONF
global UPLOAD_URL
global QUYjson
version='0.5.5'
#logger_level='warning'#日志显示级别debug,info不会显示'debug'
logger_level='DEBUG'
tk_col = {'qid':0,'stem':1,'answer_txt':2,'pinyin':3,'answer_symbol':4,
           'options':5,'qtype':6,'mark':7,}
tiku_db_col = ['qid','qtype', 'stem', 'options', 'answer_txt', 'answer_symbol',
               'solution', 'company', 'origin', 'mark',]
app=MYAES()
with open(confpath+'use.db','r') as f:
    txt=f.read().strip()
urls=demjson.decode(app.decrypt(txt))
def boxprint(outtxt, CN_zh=False):
    txt = outtxt.strip()
    lst = ['  ' + x + '  ' for x in txt.splitlines()]
    maxlen = max([len(x) for x in lst])
    if CN_zh:
        head = [
         '┏' + '━' * maxlen + '┓']
        tip = ['┗' + '━' * maxlen + '┛']
        content = ['┃' + y + ' ' * (maxlen - len(y)) + '┃' for y in lst]
    else:
        half = maxlen % 2
        head = ['┏' + '━' * (maxlen // 2 + half) + '┓']
        tip = ['┗' + '━' * (maxlen // 2 + half) + '┛']
        content = ['┃' + y + ' ' * (maxlen - len(y) + half) + '┃' for y in lst]
    format_txt = ('\n').join(head + content + tip)
    print(format_txt)
def boxmsg(outtxt, CN_zh=False):
    txt = outtxt.strip()
    lst = ['  ' + x + '  ' for x in txt.splitlines()]
    maxlen = max([len(x) for x in lst])
    if CN_zh:
        head = [
         '+' + '-' * (maxlen * 2 - 4) + '+']
        tip = ['+' + '-' * (maxlen * 2 - 4) + '+']
        content = ['|' + y + '  ' * (maxlen - len(y)) + '|' for y in lst]
    else:
        head = [
         '+' + '-' * maxlen + '+']
        tip = ['+' + '-' * maxlen + '+']
        content = ['|' + y + ' ' * (maxlen - len(y)) + '|' for y in lst]
    format_txt = ('\n').join(head + content + tip)
    return format_txt
def pick_txt_answer(answer_lst, options_lst):
    answer_txt_lst = []
    for option in options_lst:
        for x in answer_lst:
            if option.startswith(x):
                res = re.compile('(^[A-S]\\s*[\\.、．]\\s*).*').search(option)
                res2 = re.compile('(^[A-S]\\s*[\\.、．]\\s*)').search(option)
                if res:
                    answer_txt = res.group()
                    symbol=res2.group()
                    answer_txt=answer_txt.replace(symbol,'',1)
                else:
                    answer_txt = option
                answer_txt = answer_txt.strip()
                answer_txt_lst.append(answer_txt)
                break
    return answer_txt_lst
def pick_ABCD_answer(answer_txt_lst, options_lst):
    score = 70
    answer_lst = []
    for answertxt in answer_txt_lst:
        one_tupp = process.extractOne(answertxt, choices=options_lst, scorer=fuzz.UWRatio)
        if one_tupp[1] < score:
            return ''
        answer_lst.append(one_tupp[0].strip()[0])
    return ('').join(answer_lst)
def folder_walk(fdir, file_type):
    file_lst = []
    if not fdir.endswith('/'):
        fdir += '/'
    if file_type == '*.*':
        for parent, dirnames, filenames in os.walk(fdir):
            for filename in filenames:
                if parent == fdir:
                    file_lst.append(fdir + filename)
    else:
        for parent, dirnames, filenames in os.walk(fdir):
            for filename in filenames:
                if filename.endswith(file_type) and parent == fdir:
                    file_lst.append(fdir + filename)
    return file_lst
def folder_walk2(fdir, file_type):
    file_lst = []
    if not fdir.endswith('/'):
        fdir += '/'
    if file_type == '*.*':
        for parent, dirnames, filenames in os.walk(fdir):
            for filename in filenames:
                if parent == fdir:
                    file_lst.append(filename)
    else:
        for parent, dirnames, filenames in os.walk(fdir):
            for filename in filenames:
                if filename.endswith(file_type) and parent == fdir:
                    file_lst.append(filename)
    return file_lst
def delete_files(fdir, file_type, fnames=None,display=True):
    if not (fdir.endswith('/') or fdir.endswith('\\')):
        fdir += '/'
    if not os.path.exists(fdir):
        print('指定的目录不存在！')
        return
    if file_type is not None:
        fpaths = folder_walk(fdir, file_type)
        for fpath in fpaths:
            if os.path.exists(fpath):
                os.remove(fpath)
                if display:print('[%s]已删除' % fpath)
    if fnames is not None:
        for fn in fnames:
            fpath = fdir + fn
            if os.path.exists(fpath):
                os.remove(fpath)
                if display:print('[%s]已删除' % fpath)
def filter_page_labels(htmltxt, save=None):
    result = []
    start = []
    data = []
    def starttag(tag, attrs):
        if tag not in save:
            return
        start.append(tag)
        if attrs:
            j = 0
            for attr in attrs:
                attrs[j] = attr[0] + '="' + attr[1] + '"'
                j += 1
            attrs = ' ' + (' ').join(attrs)
        else:
            attrs = ''
        result.append('<' + tag + attrs + '>')
    def endtag(tag):
        if start and tag == start[len(start) - 1]:
            result.append('</' + tag + '>')
    re_script = re.compile('<\\s*script[^>]*>[^<]*<\\s*/\\s*script\\s*>', re.I)
    htmltxt = re_script.sub('', htmltxt)
    re_style = re.compile('<\\s*style[^>]*>[^<]*<\\s*/\\s*style\\s*>', re.I)
    htmltxt = re_style.sub('', htmltxt)
    parser = HTMLParser()
    parser.handle_data = result.append
    if save:
        parser.handle_starttag = starttag
        parser.handle_endtag = endtag
    parser.feed(htmltxt)
    parser.close()
    for i in range(0, len(result)):
        tmp = result[i]
        if tmp.strip():
            data.append(tmp)
    return ('').join(data)
def base64encode(txt):
    enb64 = base64.b64encode(txt.encode())
    en64 = enb64.decode()
    return en64
def base64decode(en64):
    btxt = base64.b64decode(en64.encode())
    txt = btxt.decode()
    return txt
def timestr_to_timestamp(timestr):
    st = time.strptime(timestr, '%Y-%m-%d %H:%M:%S')
    timestamp = int(time.mktime(st))
    return timestamp
def getip():
    if platform.system() == 'Windows':
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('www.baidu.com', 0))
            ip = s.getsockname()[0]
        except:
            ip = '0.0.0.0'
        finally:
            s.close()
        return [ip]
    if platform.system() == 'Linux':
        out = os.popen("ifconfig | grep 'inet addr:' | grep -v '127.0.0.1' | cut -d: -f2 ").read()
        ips = [x.split()[0] for x in out.strip().split('\n') if x.startswith('192')]
        return ips
    return ['0.0.0.0']
def read_deadline():
    fp = confpath + 'usb.db'
    if os.path.exists(fp):
        with open(fp, 'r') as (f):
            d = base64decode(f.read().strip())
        print('使用期限:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(d))))
        return int(d)
    print('使用授权文件不存在，请微信联系hrcl2015')
    return 0
def check_date():
    deadline = read_deadline()
    nowtimestamp = int(time.time())
    if deadline > nowtimestamp:
        return True
    else:
        return False
def check_user(user):
    fp = confpath + 'usd.db'
    if os.path.exists(fp):
        with open(fp, 'r') as (f):
            u = base64decode(f.read().strip())
        resp = urllib.request.urlopen(u)
        print('正在连接网络验证……')
        if resp.status == 200:
            t = resp.read().decode()
            if user in t:
                return True
            print('非授权用户%s' % user)
        else:
            print('用户检测文件不存在，请微信联系hrcl2015')
        return False
def read_start_response(fdir=None, fname=None, makefile=False):
    if fdir is None:
        fdir = txtpath
    if fname is None:
        fname = 'start_response.txt'
    fpath = fdir + fname
    if not os.path.exists(fpath):
        print('考题文件不存在!')
        if not makefile:
            return (None, None)
        return None
    with open(fpath, mode='r', encoding='utf-8') as f:
        t = f.read()
    j = json.loads(t, encoding='utf-8')
    if j['examPaperFullInfo']:
            exam_lst = j['examPaperFullInfo']['questionRelations']
            title = j['examPaperFullInfo']['name']
    elif j['data']:
            exam_lst = j['data']['questionRelations']
            title = j['data']['name']
    else:
        print('考题文件格式和以前不一样哦，不能处理！')
        if not makefile:
            return (None, None)
        return None
    if not makefile:
        return (exam_lst, title)
    format_txt = '\n{num}. [{qtype}]{stem}\n{options}\n'
    fn = 'examfile' + time.strftime('_%Y%m%d_%H%M%S.txt', time.localtime())
    fp = fdir + fn
    with open(fp, mode='w', encoding='utf-8') as (f2):
        f2.write(title + '\n')
        for i, x in enumerate(exam_lst):
            stem = x['question']['stem']
            qtype = x['question']['questionTypeName']
            options = [y['optionCont'] for y in x['question']['questionOptionList']]
            options = symb_options(options)
            s = format_txt.format(num=i + 1, qtype=qtype, stem=stem, options=('\n').join(options))
            f2.write(s)
    print('考题文件[%s]已生成！' % fn)
    return fn
def delete_start_response(fdir=None, fname=None):
    if fdir is None:
        fdir = txtpath
    if fname is None:
        fname = 'start_response.txt'
    fpath = fdir + fname
    if os.path.exists(fpath):
        os.remove(fpath)
        print('start_response.txt已删除！')
    else:
        print("%s文件不存在！！"%fpath)
def symb_options(options):
    symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    symboptions = [symbols[iy] + '. ' + y for iy, y in enumerate(options)]
    return symboptions
def parser(questionRelation):
    x=questionRelation
    qid=x["questionid"]
    stem=x['question']['stem']
    desc=''
    if x['question'].get('caseid'):
        desc=x['question']['caseAnalysis']['desc']
    stem=desc+stem
    answertip=x['question'].get('answertip')
    optionlst=x['question']['questionOptionList']
    qtype=x['question']['questiontype']
    qtypename=x['question'].get('questionTypeName')
    answerNodic={1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',
                 8:'H',9:'I',10:'J',11:'K',12:'L',13:'M',
                 14:'N',15:'O',16:'P',17:'Q',18:'R',19:'S',
                 20:'T',21:'U',22:'V',23:'W',24:'X',25:'Y',26:'Z',}
    answertxt=[]
    answer2=[]
    options_dic={}
    for y in optionlst:
        try:
            options_dic[y["questionNo"]]=answerNodic[y["questionNo"]]+'. '+y['optionCont']
        except:
            print(optionlst)
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
    type_name=qtypename
    return qid,stem,answertxt,answer2,options,type_name,answertip
def parser_course(testQuestionList):
    x=testQuestionList
    qid=x["questionId"]
    stem=x['question']['stem']
    desc=''
    if x['question'].get('caseid'):
        desc=x['question']['caseAnalysis']['desc']
    stem=desc+stem
    answertip=x['question'].get('answertip')
    optionlst=x['question']['questionOptionList']
    qtype=x['question']['questiontype']
    qtypename=x['question'].get('questionTypeName')
    answerNodic={1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',
                 8:'H',9:'I',10:'J',11:'K',12:'L',13:'M',
                 14:'N',15:'O',16:'P',17:'Q',18:'R',19:'S'}
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
    type_name=qtypename
    return qid,stem,answertxt,answer2,options,type_name,answertip
def parser_login(account,cn=True):
    dic={}
    if cn:
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
    else:
        dic["name"]=account.get("realname")
        dic["sex"]=account.get("sexName")
        dic["phone"]=account.get("phone")
        dic["workid"]=account.get("workid")
        dic["professionalTitle"]=account.get("professionalTitleName")
        dic["job"]=account.get("jobName")
        dic["maxEducation"]=account.get("maxEducationName")
        dic["departmentName"]=account.get("departmentName")
        dic["departmentId"]=account.get("departmentId")
        dic["hospitalName"]=account.get("hospitalName")
        dic["staffProperty"]=account.get("staffPropertyName")
        dic["hospitalId"]=account.get("hospitalId")
        dic["nurseLevel"]=account.get("nurseLevelName")
        dic["departmentManeger"]="Y" if account.get("departmentManeger") else "N"
        dic["hospitalManager"]="Y" if account.get("hospitalManager") else "N"
        dic["usernameid"]=account.get("username")
    return dic
def read_commit_answer(fn=None, txt=None):
    if txt is None:
        if fn is None:
            fn = 'commit_request.txt'
        if not os.path.exists(txtpath + fn):
            print('[%s]文件不存在' % fn)
            return
        with open(txtpath + fn, mode='r', encoding='utf-8') as (f):
            t = f.read()
    else:
        t = txt
    i_start = t.find('&answer=')
    i_end = t.find('&', i_start + 1)
    return (
     t[:i_start], t[i_start:i_end], t[i_end:])
def pick_ua(ua):
    re_s='\((Linux|iPhone).[^\)]*\)'
    m=re.search(re_s,ua,re.S)
    if m:
        out=m.group()
        out=';'.join([x for x in out[1:-1].split(sep='; ') if x not in ['U','wv']])
        print(out)
        return out
def str_to_pinyin(txt):
    symbols="""\n\r,.'"`~!@#$%^&*()_+-=;:?<>·！！@#￥%…&（）——、|【】{}“‘'；：？》《。，"""
    txtCN=txt
    for sym in symbols:
        txtCN=txtCN.replace(sym,'')
    lst=pinyin(txtCN,style=Style.FIRST_LETTER)
    ft=''.join([x[0] for x in lst])
    return ft
def load_data_only(datafile):
    dpath=datapath+datafile
    if os.path.exists(dpath) is False:
        print('%s文件不存在'%datafile)
        qids=[]
        questions=[]
        return qids,questions
    with open(dpath,mode='r',encoding='utf-8') as f:
        t=f.read()
    try:
        j=json.loads(t,encoding='utf-8')
    except:
        print('加密题库:',datafile)
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
def get_dir_file(fpath,file_type='.txt'):
    if not os.path.exists(fpath):
        print('指定目录不存在')
        return []
    dirs = os.listdir(fpath) 
    if file_type:
        lst=[x for x in dirs if file_type in os.path.splitext(x)[1]]
    else:
        lst=[x for x in dirs if os.path.splitext(x)[1]]
    return lst
def get_email_data():
    try:
        r = requests.get(urls["giteemail"])
    except:
        r = requests.get(urls["githubmail"])
    if r.status_code == 200:
        txt = r.text
        reader = csv.reader(txt.strip().split(sep='\n'))
        lst=[x for x in reader]
        de=MYAES()
        data_lst = [[de.decrypt(x[1]),de.decrypt(x[2]),x[3],x[4],
                     de.decrypt(x[5]),de.decrypt(x[6]),
                     de.decrypt(x[7])] for i,x in enumerate(lst) if i>0]
    return data_lst[1]
def get_webdb_conf():
    try:
        r = requests.get(urls["giteewebdb"])
    except:
        r = requests.get(urls["githubwebdb"])
    if r.status_code == 200:
        txt = r.text
        de=MYAES()
        jsontxt =de.decrypt(txt)
        dic=json.loads(jsontxt,encoding='utf-8')
        dbuser=dic["user"]
        dbpwd=dic["pwd"]
        host=dic["host"]
        port=dic["port"]
        dbname=dic["dbname"]
        tablename=dic["tablename"]
        uploadtxturl=dic.get("uploadtxturl")
        uploadurl=dic.get("uploadurl")
        return (dbuser,dbpwd,host,port,dbname,tablename),(uploadtxturl,uploadurl)
    print('无法获取网络数据库连接配置信息！！')
    return None,None,None,None,None,None,None,None
def get_qiniu_conf():
    try:
        r = requests.get(urls["giteeqny"])
    except:
        r = requests.get(urls["githubqny"])
    if r.status_code == 200:
        j = r.json()
        de=MYAES()
        for k in j.keys():
            j[k]=de.decrypt(j[k])
        return j
def txtanswer_to_formatanswer(exam_lst,minianswertxt_lst):
    txt_all_answer_lst=[]
    len_txt=len(minianswertxt_lst)
    len_exam=len(exam_lst)
    if len_txt>len_exam:
        print('远程答案文本＞考题列表，是不是出错了？')
    for i,at in enumerate(minianswertxt_lst):
        if i>len_exam-1:
            break
        ex=exam_lst[i]
        qid=ex["questionid"]
        answer_abcd=at.strip().split(sep=']')[-1]
        ops_dic={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8,'J':9,'K':10}
        index_lst=[ops_dic[a] for a in answer_abcd]
        ex_ops=ex['question']['questionOptionList']
        answer_lst=[ex_ops[p]["questionNo"] for p in index_lst]
        dic = {}
        dic['questionid'] = qid
        dic['type'] = 1
        dic['answers'] = answer_lst
        txt_all_answer_lst.append(dic)
    return txt_all_answer_lst
def get_remote_txt(fn):
    print('='*20)
    print(urls['giteetxtanswer']+fn)
    try:
        r=requests.get(urls['giteetxtanswer']+fn)
    except:
        r=requests.get(urls['githubtxtanswer']+fn)
    if r.status_code==404:
        return None
    elif r.status_code==200:
        return r.text
def get_py_pyc():
    try:
        r=requests.get(urls["giteepypyc"])
    except:
        r=requests.get(urls["githubpypyc"])
    if r.status_code==200:
        j=r.json()
        return j
def uploadfile_to_server(fp,istk=False):
    uploadtxturl,uploadurl=UPLOAD_URL
    if istk:
        url=uploadtxturl
    else:
        url=uploadurl
    if not os.path.exists(fp):return
    files={'file':open(fp,'rb')}
    try:
        r=requests.post(url,files=files)
        if r.status_code==200:
            return r.json()
    except:
        pass
def progress_bar(rate,style='#',padding='-',total=25,msg=''):
    if rate>1:rate=1
    bar=int(rate*total)*style+padding*total
    bar=bar[:total]
    out='\r[%s]%3s%% %s'%(bar,int(rate*100),msg)
    print(out,end='')
M=get_email_data()
DBCONF,UPLOAD_URL=get_webdb_conf()
QNYjson=get_qiniu_conf()
if __name__ == '__main__':
    pass