#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from qiniu import Auth, put_file, etag,BucketManager,build_batch_stat
import qiniu.config
import json,os
from comm import QNYjson
class MY_QINIU:
    def __init__(self):
        self.access_key=QNYjson["AK"]
        self.secret_key=QNYjson["SK"]
        self.bucket_name=QNYjson["BN"]
        self.host=QNYjson["HOST"]
        self.q = Auth(self.access_key, self.secret_key)
        self.bucket = BucketManager(self.q)
    def upload_file(self,local_file,remote_file,overwrite=False):
        key = remote_file
        if not overwrite:
            if self.check_file_status(key):
                print('%s文件已存在！'%remote_file)
                return None,None
        token = self.q.upload_token(self.bucket_name, key, 3600)
        localfile = local_file
        ret, info = put_file(token, key, localfile)
        assert ret['key'] == key
        assert ret['hash'] == etag(localfile)
        return ret,info
    def upload_files(self,local_files,remote_files):
        pass
    def upload_dir(self,local_dir,remote_dir='',overwrite=False):
        if not os.path.isdir(local_dir):
            print("%s不是文件夹"%local_dir)
            return
        local_dir=os.path.normpath(local_dir)
        if remote_dir.startswith('/'):remote_dir=remote_dir[1:]
        if remote_dir.endswith('/'):remote_dir=remote_dir[:-1]
        if remote_dir:remote_dir=remote_dir+'/'
        dir0=local_dir.split(sep=os.path.sep)[-1]
        path0=local_dir[:-len(dir0)]
        rets=[]
        infos=[]
        for parent,dirnames,filenames in os.walk(local_dir):
            for fn in filenames:
                fp=os.path.join(parent,fn)
                key=remote_dir+'/'.join(parent[len(path0):].split(sep=os.path.sep)+[fn])
                ret,info=self.upload_file(fp,key,overwrite=overwrite)
                rets.append(ret)
                infos.append(info)
        return rets,infos
    def check_file_status(self,remote_file):
        key=remote_file
        ret, info = self.bucket.stat(self.bucket_name, key)
        return ret
    def many_stats(self,remote_files):
        keys = remote_files
        ops = build_batch_stat(self.bucket_name, keys)
        ret, info = self.bucket.batch(ops)
        print(info)
        return json.loads(info.text_body)
    def ls_all(self,):
        ret,flag,info=self.bucket.list(self.bucket_name)
        return ret
    def ls(self,remote_dir='/',filetype=None,limit=10):
        ret,flag,info=self.bucket.list(self.bucket_name,limit=limit)
        pass
    def rm(self,remote_file):
        key=remote_file
        ret,info=self.bucket.delete(self.bucket_name,key)
        return ret
    def download_file(self,remote_file,local_file):
        pass
if __name__=="__main__":
    myqn=MY_QINIU()
    pass