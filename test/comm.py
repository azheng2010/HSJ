import requests
import base64,re,random,time
import os,json#.path as path
import zipfile
from Crypto.Cipher import AES
from models.tencentcloudsms import send_SMS
#固定路径
confdir='config/'
readdir='txt/'#试卷存放位置
download_path='downloadfile/'#下载的zip文件存放位置
hsjtxt_path='hsj_txt/'
#文件上传变量
upload_file_dir=readdir#上传文件存放位置
allowed_extensions=set(['txt','png', 'jpg', 'jpeg', 'gif'])#允许上传的文件类型后缀名
max_content_length=16 * 1024 * 1024 #上传文件大小最大为16M
wxpayconf_fn='wxpay_hrcl2015.conf'#收款二维码配置文件
sms_fn='sms_verification_code.txt'#短信验证码存放位置4位数
###################
#本地用windows主机测试连接远程数据库的标识
#用来加载不同位置的数据库账户密码
windows_test_flag='tencent'#tencent::腾讯主机在广州   hostwinds::HostWinds主机在美国西雅图
#windows_test_flag='hostwinds'
###################
def get_myip_from_cip():
    url='http://www.cip.cc/'
    headers={
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Host':'www.cip.cc',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            }
    r=requests.get(url,headers=headers)
    if r.status_code==200:
        txt=r.text
        ips = re.findall(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", txt)
        if ips:
            return ips[0]
def get_myip_from_httpbin():
    url='http://httpbin.org/ip'
    r=requests.get(url)
    if r.status_code==200:
        j=r.json()
        #有可能是多个ip，取第一个
        #{"origin": "120.227.23.58, 116.117.134.135"}
        t=j.get("origin")
        if t:t=t.split(',')[0].strip()
        return t
def fdir_walk(fdir,ends=None):
    """文件夹遍历，只遍历当前文件夹，二级目录不搜索，返回文件列表
    fdir:需要搜索的文件夹
    ends:指定文件后缀名 .txt  .csv  .zip
    """
    f_dir=fdir
    file_lst=[]#文件列表
    if not os.path.exists(f_dir):
        print(f'{f_dir}不存在!')
        return file_lst
    for parent,dirnames,filenames in os.walk(f_dir):
        for filename in filenames:
            if ends:
                if filename.endswith(ends) and parent==f_dir: #只遍历根目录下的文件
                    file_lst.append(filename)
            else:
                if parent==f_dir: #只遍历根目录下的文件
                    file_lst.append(filename)
    return file_lst

def random_str(size=8):
    """生成随机字符串只有字母数字"""
    return ''.join(random.choices('1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',k=size))

def random_verification_code(size=4):
    """生成4位数字验证码"""
    return ''.join(random.choices('1234567890',k=size))

def get_verification_code(phone,n_min=10,fdir=confdir,fn=sms_fn,send=False):
    '''生成验证码，保存到文件，查询不重复，10分钟内不重复生成验证码
    phone:手机号str,对于hrcl2015，有特殊需求
    n_min:有效期（分钟）int
    返回{'maketime':cur,'deadtime':cur+n_min*60*1000,'phone':phone,'code':code}
    '''
    cur=int(time.time()*1000)#当前时间戳，毫秒ms，int
    timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #文件不存在时生成文件
    if not os.path.exists(fdir+fn):
        if not os.path.exists(fdir):os.mkdir(fdir)
        j={'data':[],'current_timestamp':cur,'time':timestr,'num':0}
        writejson(fdir+fn,j)
    else:
        j=readjson(fdir+fn)
    #清理过期的验证码
    datas=j['data']#{'maketime':验证码生成时间戳,'deadtime':验证码失效时间戳,'phone':'13870000855','code':'2154'}
    del_lst=[d for d in datas if (phone==d['phone'] and d['deadtime']<cur)]#需要清理的数据条
    for dl in del_lst:
        j['data'].remove(dl)
    #查找手机号，没有则生成验证码，有则直接使用上次生成的验证码
    bar=None
    if phone=='hrcl2015':
        bar={'maketime':cur,'deadtime':cur+n_min*60*1000,'phone':phone,'code':''}
        bar["new"]=0
        j['data'].append(bar)
        j['current_timestamp']=cur
        j['time']=timestr
        j['num']+=1
    else:
        for i,x in enumerate(j['data']):
            if phone==x['phone']:
                bar=x
                bar["new"]=0
                break
    if (bar is None) and send:
        codes=[x['code'] for x in j['data']]
        code=random_verification_code()
        while code in codes:
            code=random_verification_code()#重新生成验证码
        bar={'maketime':cur,'deadtime':cur+n_min*60*1000,'phone':phone,'code':code}
        bar["new"]=1#用new代表新发送的短信
        j['data'].append(bar)
        j['current_timestamp']=cur
        j['time']=timestr
        j['num']+=1
        info=send_SMS([phone],[code,str(n_min),'HSJ考前卷','微信添加hrcl2015'])
    writejson(fdir+fn,j)#保存验证码文件
    #print('bar=',bar)
    return bar

def check_allowed_file(filename):
    '''检查上传的文件是否为允许的文件后缀'''
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in allowed_extensions

def readtxt(fdir,fn):
    '''读取txt'''
    if os.path.exists(fdir+fn):
        with open(fdir+fn,'r',encoding='utf-8') as f:
            txt=f.read()
    else:
        txt=''
    return txt
def writetxt(fdir,fn,wtxt):
    '''写入txt'''
    with open(fdir+fn,'w',encoding='utf-8') as f:
        f.write(wtxt)
    print(f'数据成功写入{fdir+fn}')

def readjson(fp):
    '''读取json文件'''
    if os.path.exists(fp):
        with open(fp,'r',encoding='utf-8') as f:
            txt=f.read()
    else:
        txt=''
    if txt:
        return json.loads(txt)
    return txt

def writejson(fp,j):
    '''写入json文件'''
    with open(fp,'w',encoding='utf-8') as f:
        f.write(json.dumps(j,ensure_ascii=False,indent=2))

def is_phone_num(phonetxt):
    '''判断是否是手机号'''
    phonetxt = str(phonetxt).strip()
    if len(phonetxt) != 11:return False
    ret = re.match(r"^1[3456789]\d{9}$", phonetxt)
    if ret:
        return True
    else:
        return False    

def zip_fdir(fdir,zipfp):
    """打包文件夹"""
    with zipfile.ZipFile(zipfp,'w',zipfile.ZIP_DEFLATED) as target:
        for dirpath, dirnames, filenames in os.walk(fdir):
            for fn in filenames:
                fp=os.path.join(dirpath,fn)
                target.write(fp)
                print(f'{fp}已写入压缩文件')
        
class AESCipher:
    """AES加密，可以加密中文
    e=AESCipher()
    data='算法选择：对称加密AES，非对称加密: ECC，消息摘要: MD5，数字签名:DSA'
    en_data=e.encrypt(data)
    print(en_data)
    de_data=e.decrypt(en_data)
    print(de_data)

    """
    def __init__(self):
        self.key = 'aedfb5ceaa834dbf'#16位
        self.iv = '2b2fd8747b3c4fa4'# 16位字符，用来填充缺失内容#可固定值也可随机字符串，具体选择看需求。

    def __pad(self, text):
        """填充方式，加密内容必须为16字节的倍数，若不足则使用self.iv进行填充"""
        text_length = len(text)
        amount_to_pad = AES.block_size - text_length % AES.block_size
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def __unpad(self, text):
        """去除填充数据"""
        pad = ord(text[-1])
        return text[:-pad]

    def encrypt(self, raw):
        """加密，raw为str类型，返回密文str类型"""
        raw=self.base64encode(raw)
        raw2 = self._AESCipher__pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        r=base64.b64encode(cipher.encrypt(raw2))#byte
        return self.base64encode(r.decode())#str

    def decrypt(self, enc):
        """解密字符串，enc为str或byte类型，返回str类型"""
        enc=self.base64decode(enc)#2019-04-28新增
        enc2 = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        dec=self._AESCipher__unpad(cipher.decrypt(enc2).decode('utf-8'))
        return self.base64decode(dec)

    def base64encode(self,txt):
        """base64编码，返回str"""
        enb64=base64.b64encode(txt.encode())
        en64=enb64.decode()
        return en64
    def base64decode(self,en64):
        """base64解码，返回str"""
        if type(en64) is bytes:
            en64=en64.decode()
        btxt=base64.b64decode(en64.encode())
        txt=btxt.decode()
        return txt

def get_gd_ip_info(ip):
    """高德地图api获取ip位置信息"""
    gdkey='9edc4b84e2564ff8e8bfe68a9765c16b'#高德key
    url ="https://restapi.amap.com/v3/ip"
    params={'ip':ip,
          'output':'json',
          'key':gdkey}
    try:
        res = requests.get(url,params=params)
    except :
        print("连接出现异常啦！请在网页端确定URL可用")
    else:
        if res.status_code==200:
            j=res.json()
            province = j.get('province')
            city = j.get('city')
            #info = j.get('info')
            msg='{province} {city}'.format(province=province,city=city)
            print(msg)
            return j
        else:
            print("status_code:%s"%res.status_code)

def get_ip_api(ip):
    """查询国际ip位置信息"""
    url = "http://ip-api.com/json/" + ip
    try:
        res = requests.get(url)
    except :
        print("Connection error")
    else:
        if res.status_code==200:
            strpp=res.json()
            country=strpp.get('country')#国
            region=strpp.get('regionName')#省
            city=strpp.get('city')#市
            lat=strpp.get('lat')#纬度
            lon=strpp.get('lon')#经度
            isp=strpp.get('isp')#服务商
            msg='{country} {province} {city} {isp} {lat},{lon}'.format(
                    country=country,province=region,city=city,
                    lat=lat,lon=lon,isp=isp)
            print(msg)
            return strpp
        else:
            print("status_code:%s"%res.status_code)


if __name__=='__main__':
    e=AESCipher()
    x=e.encrypt('http://127.0.0.1/hsj/readexam/581_69916.txt')
    data=f'13507499021||湘雅三医院||{x}'
    en_data=e.encrypt(data)
    print(en_data)
    pass