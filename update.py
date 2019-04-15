#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,sys
import requests
import zipfile,shutil
import platform
__version__="0.1.0"
j={"version": "0.1.2", "files": ["main.py", "comm.py", "HSJ_AES.py", "logger.py", "m2m.py", "mitm_test.py", "models.py", "update.py"], "folders": ["audio", "conf", "data", "log", "runtxt"]}
def downloadfiles(url0,fns,localpath):
    url0='https://raw.githubusercontent.com/azheng2010/HSJ/master/'
    localpath='download/'
    if not os.path.exists(localpath):os.makedirs(localpath)
    for fn in fns:
        url=url0+fn
        r=requests.get(url)
        if r.status_code==200:
            with open(localpath+fn,'w',encoding='utf-8') as f:
                f.write(r.text)
            print('%s下载完毕'%fn)
def downloadzipfile(localpath):
    url='https://github.com/azheng2010/HSJ/archive/master.zip'
    r=requests.get(url)
    if r.status_code==200:
        fn=url.split('/')[-1]
        zip_path=os.path.abspath(os.path.join(localpath,fn))
        with open(zip_path,'wb') as f:
            f.write(r.content)
        print('[%s]已保存'%zip_path)
        return zip_path
def update():
    if platform.system()=='Linux':
        localpath='/storage/emulated/0/'
        unpack_dir='/storage/emulated/0/'
        zp=downloadzipfile(localpath)
        if zp is not None:
            unpackfiles(zp,unpack_dir=unpack_dir)
            os.remove(zp)
def updatefile():
    shutil.copy2("/home/code/newest/file1.py", "/home/code/") 
    shutil.rmtree('/home/code/newest') 
    sys.exit("exit to restart the true program")
def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            print('unzipping %s'%file)
            fz.extract(file, dst_dir)
        print('%s unzip finished'%zip_src)
    else:
        print('This is not zip files')
def unpackfiles(zipname,unpack_dir=None,zipdir=''):
    if unpack_dir is None:
        unpack_dir=zipname.split(sep='.')[0]
    zip_path=os.path.abspath(os.path.join(zipdir,zipname))
    if os.path.exists(zip_path):
        shutil.unpack_archive(zip_path,extract_dir=unpack_dir)
        print('unpacked to [%s]'%os.path.abspath(unpack_dir))
    else:
        print(zipname,' is not exist!')
if __name__=="__main__":
    update()
    pass