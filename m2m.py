#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
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
def send(f, n, p, t, h, s, c, fps):
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
        server = smtplib.SMTP(h, 25)
        server.login(f, p)
        server.sendmail(f, t, m.as_string())
        server.quit()
        return True
    except smtplib.SMTPException as e:
        return False
def e2e(s, c, fps=None):
    inf = bde((open('conf/usc.db', 'r', encoding='utf-8')).read().strip()).split('|')
    f = inf[0]
    n = inf[2]
    h = inf[1]
    p = bde((open('conf/usa.db', 'r', encoding='utf-8')).read().strip())
    t = [inf[3], inf[4]]
    if fps is None:
        fps = []
    return send(f, n, p, t, h, s, c, fps)
if __name__ == '__main__':
    pass