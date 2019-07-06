#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from subprocess import Popen
import os
import requests
import shutil
import platform
from comm import urls,path0
import zipfile
def downloadzipfile(localpath):
    if platform.system() == 'Linux':
        try:
            url=urls['zip3']
            r = requests.get(url)
        except:
            url=urls['zip4']
            r = requests.get(url)
        if r.status_code==200:
            fn=url.split(sep='/')[-1]
            zip_path=os.path.abspath(os.path.join(localpath,fn))
            with open(zip_path,'wb') as f:
                f.write(r.content)
            print('[%s]已保存'%zip_path)
            return zip_path
def update():
    if platform.system()=='Linux':
        print("正在更新程序……")
        localpath='/storage/emulated/0/'
        unpack_dir='/storage/emulated/0/hsjdownload/'
        if not os.path.exists(unpack_dir):os.makedirs(unpack_dir)
        zp=downloadzipfile(localpath)
        if zp is not None:
            if os.path.basename(zp)=='HSJ.zip':
                unpackfiles(os.path.basename(zp),
                            unpack_dir=os.path.join(unpack_dir,'HSJ'),
                            zipdir=os.path.dirname(zp))
                os.remove(zp)
                updater_py_file(unpack_dir+'HSJ',path0,file_type='.py')
            elif os.path.basename(zp)=='HSJ-master.zip':
                unzip_file(zp, unpack_dir)
                os.remove(zp)
                updater_py_file(unpack_dir+'HSJ-master',path0,file_type='.py')
            else:
                print('无法更新')
                return
            print("脚本更新成功，请关闭软件后重新进入！")
def updater_py_file(new_src,old_dst,file_type='.py'):
    lst=filter_file_type(new_src,file_type=file_type)
    if lst:
        for x in lst:
            if x=='main.py':continue
            newfp=os.path.join(new_src,x)
            oldfp=os.path.join(old_dst,x)
            shutil.copyfile(newfp,oldfp,follow_symlinks=False)
            print(x,'update completed')
    print('更新完毕')
def filter_file_type(fpath,file_type='.txt'):
    if not os.path.exists(fpath):
        print('指定目录不存在')
        return []
    dirs = os.listdir(fpath) 
    lst=[x for x in dirs if file_type in os.path.splitext(x)[1]]
    return lst
def zip_file(src_dir):
    zip_name = src_dir +'.zip'
    z = zipfile.ZipFile(zip_name,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = dirpath.replace(src_dir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
            print ('==压缩成功==')
    z.close()
def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    print(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            print('unzipping %s'%file)
            fz.extract(file, dst_dir)
        print('%s unzip finished\n%s'%(zip_src,'-'*20))
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
    print('-'*20)
if __name__=="__main__":
    unpackfiles('HSJ.zip',unpack_dir='d:\\123',zipdir='D:\\MyPython\\HSJ_release\\HSJ_zip')
    pass