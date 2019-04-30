#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import shutil
import platform
from comm import urls
import zipfile
def downloadzipfile(localpath):
    try:
        url=urls['zip1']
        r = requests.get(url)
    except:
        url=urls['zip2']
        r = requests.get(url)
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
            print("脚本更新成功，请关闭软件后重新进入！")
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
    pass