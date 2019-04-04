#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests,json
import os,time
from bs4 import BeautifulSoup
def login(user,pwd):
    url='http://www.medtiku.com/login.php'
    pdata={
            'name':user,#'htcl2015',
            'pwd':pwd,#'wzh2018',
            }
    headers={
            'Host':'www.medtiku.com',
            'Connection':'keep-alive',
            'Cache-Control':'max-age=0',
            'Origin':'http://www.medtiku.com',
            'Upgrade-Insecure-Requests':'1',
            'Content-Type':'application/x-www-form-urlencoded',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer':'http://www.medtiku.com/login.php',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cookie':'erLog=1',
            }
    r=requests.post(url,headers=headers,data=pdata)
    if r.status_code==200:
        dic={}
        token=r.request._cookies['token']
        userID=r.request._cookies['userID']
        userName=r.request._cookies['userName']
        userStatus=r.request._cookies['userStatus']
        cookie=r.request._cookies._cookies['www.medtiku.com']['/']
        cookie_token=cookie['token']
        expires=cookie_token.expires
        dic['token']=token
        dic['userID']=userID
        dic['userName']=userName
        dic['userStatus']=userStatus
        dic['expires']=expires
        savecookie(dic)
        return dic
    return None
def savecookie(dic):
    print('cookie到期时间:{datetime}'.format(datetime=time.strftime(
        '%Y-%m-%d %H:%M:%S',time.localtime(dic['expires']))))
    txt=json.dumps(dic,ensure_ascii=False)
    fp='cookie/'
    fn='www.medtiku.com.cookie'
    if not os.path.exists(fp):
        os.makedirs(fp)
    with open(fp+fn,mode='w',encoding='utf-8') as f:
        f.write(txt)
    print('%s文件已保存'%fn)
def readcookie():
    fp='cookie/'
    fn='www.medtiku.com.cookie'
    if not os.path.exists(fp+fn):
        print('cookie文件不存在！')
        return None
    with open(fp+fn,'r',encoding='utf-8') as f:
        txt=f.read()
    try:
        j=json.loads(txt,encoding='utf-8')
        print('cookie到期时间:{datetime}'.format(datetime=time.strftime(
                '%Y-%m-%d %H:%M:%S',time.localtime(j['expires']))))
    except:
        print('cookie文件损坏,无法正常读取')
        return None
    return j
def get_id():
    url='http://www.medtiku.com/'
    j=readcookie()
    if j is None:return None
    cookie_txt='erLog=1; userID={userid}; userName={username}; userStatus={userstatus}; token={token}'
    cookie=cookie_txt.format(userid=j['userID'],username=j['userName'],
                         userstatus=j['userStatus'],token=j['token'])
    headers={
            'Host':'www.medtiku.com',
            'Connection':'keep-alive',
            'Cache-Control':'max-age=0',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer':'http://www.medtiku.com/login.php',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cookie':cookie,
            }
    r=requests.get(url,headers=headers)
    if r.status_code==200:
        medids=medtiku_parser(r.text)
        if medids is not None :
            return medids
def medtiku_parser(html):
    soup = BeautifulSoup(html, 'lxml')
    results=soup.find_all(name='div',attrs={"class":"span1 m-card p-center"})
    id_lst=[]
    for result in results:
        a=result.find(name='a')
        id_lst.append((a.text,a.attrs['href']))
    if id_lst:return id_lst
    else:return None
def get_part_id():
    url='http://www.medtiku.com/exam.php?id=7'
    j=readcookie()
    if j is None:return None
    cookie='erLog=1; userID={userid}; userName={username}; userStatus={userstatus}; token={token}'
    cookie=cookie.format(userid=j['userID'],username=j['userName'],
                         userstatus=j['userStatus'],token=j['token'])
    headers={
            'Host':'www.medtiku.com',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer':'http://www.medtiku.com/',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cookie':cookie,
            }
    r=requests.get(url,headers=headers)
    if r.status_code==200:
        html=r.text
        partids=medtiku_part_parser(html)
        if partids is not None :
            return partids
def medtiku_part_parser(html):
    soup = BeautifulSoup(html, 'lxml')
    div=soup.find(name='div',attrs={"page-main"})
    part_id_lst=[]
    pa_ids=div.find_all(name='a')
    for pa in pa_ids:
        part_id_lst.append((pa.text,pa.attrs['href']))
    if part_id_lst:return part_id_lst
    else:return None
def get_subject_id():
    url='http://www.medtiku.com/subject.php?id=44'
    j=readcookie()
    if j is None:return None
    cookie='erLog=1; userID={userid}; userName={username}; userStatus={userstatus}; token={token}'
    cookie=cookie.format(userid=j['userID'],username=j['userName'],
                         userstatus=j['userStatus'],token=j['token'])
    headers={
'Connection':'keep-alive',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Referer':'http://www.medtiku.com/exam.php?id=7',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cookie':'erLog=1; userID=105055; userName=htcl2015; userStatus=0; token=45860986c3ca37a376a747788426f488',
}
    r=requests.get(url,headers=headers)
    if r.status_code==200:
        html=r.text
        return html
        subjectids=medtiku_subject_parser(html)
        if subjectids is not None :
            return subjectids
def medtiku_subject_parser(html):
    soup = BeautifulSoup(html, 'lxml')
    div=soup.find(name='div',attrs={"page-main"})
    subject_id_lst=[]
    subject_ids=div.find_all(name='li')
    for subject in subject_ids:
        a=subject.find(name='a')
        subject_id_lst.append((a.text,a.attrs['href']))
    if subject_id_lst:return subject_id_lst
    else:return None
def get_question_id():
    pass
if __name__=='__main__':
    user='htcl2015'
    pwd='wzh2018'
    pass