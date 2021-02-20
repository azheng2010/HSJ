#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from subprocess import Popen
import os
import requests
import shutil
import platform
from comm import urls,path0,confpath,get_py_pyc
import zipfile
from configparser import ConfigParser
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
                updater_py_file(unpack_dir+'HSJ',path0)
                updater_conf_file(os.path.realpath(unpack_dir+'HSJ/conf'),
                                  os.path.realpath(confpath))
                overwritemain(confpath+'default.ini',path0+'main.py')
            elif os.path.basename(zp)=='HSJ-master.zip':
                unzip_file(zp, unpack_dir)
                os.remove(zp)
                updater_py_file(unpack_dir+'HSJ-master',path0)
                updater_conf_file(os.path.realpath(unpack_dir+'HSJ-master/conf'),
                                  os.path.realpath(confpath))
                overwritemain(confpath+'default.ini',path0+'main.py')
            else:
                print('无法更新')
                return
            print("脚本更新成功，请关闭软件后重新进入！")
    if platform.system()=='Windows':
        print('Windows系统下暂时无法更新！')
def updater_py_file(new_src,old_dst):
    lst=filter_file_type(new_src,file_type='.py')
    if lst:
        for x in lst:
            newfp=os.path.join(new_src,x)
            oldfp=os.path.join(old_dst,x)
            shutil.copyfile(newfp,oldfp,follow_symlinks=False)
            print('%16s updated'%x)
    lst2=filter_file_type(new_src,file_type='.pyc')
    if lst2:
        for x2 in lst2:
            newfp=os.path.join(new_src,x2)
            oldfp=os.path.join(old_dst,x2)
            shutil.copyfile(newfp,oldfp,follow_symlinks=False)
            print('%16s updated'%x2)
            if os.path.exists(oldfp[:-1]):
                os.remove(oldfp[:-1])
                print('%16s deleted'%x2[:-1])
    print('py文件和pyc文件更新完毕！！')
def updater_conf_file(new_src,old_dst):
    lst=filter_file_type(new_src,file_type=None)
    if lst:
        for x in lst:
            newfp=os.path.join(new_src,x)
            oldfp=os.path.join(old_dst,x)
            if x=='default.ini':
                overwriteconf(oldfp,newfp)
            shutil.copyfile(newfp,oldfp,follow_symlinks=False)
            print('%s updated'%x)
    print('conf目录更新完毕')
def filter_file_type(fpath,file_type='.txt'):
    if not os.path.exists(fpath):
        print('指定目录不存在')
        return []
    dirs = os.listdir(fpath) 
    if file_type:
        lst=[x for x in dirs if file_type in os.path.splitext(x)[1]]
    else:
        lst=[x for x in dirs if os.path.splitext(x)[1]]
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
def overwriteconf(oldfn,newfn):
    conf = ConfigParser()
    data_lst=[]
    conf.read(oldfn,encoding='utf-8')
    sections=conf.sections()
    for section in sections:
        options=conf.options(section)
        for option in options:
            value=conf.get(section,option)
            bar=[section,option,value]
            data_lst.append(bar)
            print('>>'.join(bar))
    conf.read(newfn,encoding='utf-8')
    for data in data_lst:
        conf.set(data[0],data[1],data[2])
    with open(newfn,'w',encoding='utf-8') as f:
        conf.write(f)
def overwritemain(conf_fn,main_fn):
    conf = ConfigParser()
    conf.read(conf_fn,encoding='utf-8')
    user=conf.get('UserInf','user')
    pwd=conf.get('UserInf','password')
    limit9=conf.get('Correctrate-Setting','max')
    limit0=conf.get('Correctrate-Setting','min')
    with open(main_fn,'r',encoding='utf-8') as f:
        lines=f.readlines()
    for i,line in enumerate(lines):
        if "user=" in line:
            lst=line.split(sep='user=')
            lst[-1]="user='%s'#修改时保留单引号\n"%user
            lines[i]=''.join(lst)
        if "pwd=" in line:
            lst=line.split(sep='pwd=')
            lst[-1]="pwd='%s'#单引号保留\n"%pwd
            lines[i]=''.join(lst)
        if "rate_min,rate_max=" in line:
            lst=line.split(sep='rate_min,rate_max=')
            lst[-1]="rate_min,rate_max=(%s , %s)#正确率区间(百分比)\n"%(limit0,limit9)
            lines[i]=''.join(lst)
    with open(main_fn,'w',encoding='utf-8') as f2:
        f2.write(''.join(lines))
    print("main.py更新完毕!!")
if __name__=="__main__":
    pass