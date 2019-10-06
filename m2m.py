#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from comm import M
import time
def my_split(txt, seps):
    res = [txt]
    for sep in seps:
        t = []
        list(map(lambda ss: t.extend(ss.split(sep)), res))
        res = t
    return res
def bde(en64):
    btxt = base64.b64decode(en64.encode())
    txt = btxt.decode()
    return txt
def send(f, n, p, t, h, s, c, fps,port=25):
    m = MIMEMultipart()
    m['Subject'] = s
    m['From'] = ('{n}<{f}>').format(n=n, f=f)
    m['To'] = (';').join(t)
    textApart = MIMEText(c)
    m.attach(textApart)
    for fp in fps:
        attachmentApart = MIMEApplication(open(fp, 'rb').read())
        fn = my_split(fp, '\\/')[-1]
        attachmentApart.add_header('Content-Disposition', 'attachment', 
                                   filename=('gbk', '', fn))
        m.attach(attachmentApart)
    try:
        server = smtplib.SMTP(h, port)
        server.login(f, p)
        server.sendmail(f, t, m.as_string())
        server.quit()
        return True
    except smtplib.SMTPException as e:
        print(e)
        return False
def e2e(s,c,to=[], fps=None,m=M):
    timestr = time.strftime('Created on %Y-%m-%d %H:%M:%S', time.localtime())
    c='\n'.join([timestr,c])
    f,h,n,p = m[0], m[1],m[3],m[6]
    pt=int(m[2])
    if to:
        t=to
    else:
        t = [m[4],m[5]]
        t=[x for x in t if x]
    if fps is None:fps=[]
    if send(f,n,p,t,h,s,c,fps,port=pt):
        print(n)
        return True
    else:
        return False
if __name__ == '__main__':
    e2e('测试主题电脑端3','测试邮件\nthis is a test email')
    pass