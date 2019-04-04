#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import chardet
import os
def readfile(filename,mode):
    minbytes = min(32, os.path.getsize(filename))
    raw = open(filename, 'rb').read(minbytes)
    result = chardet.detect(raw)
    encoding = result['encoding']
    print('当前文档编码格式',encoding)
    infile = open(filename, mode, encoding=encoding)
    data = infile.read()
    infile.close()
    return data
if __name__=='__main__':
    fn='d:/编码测试/UTF8.txt'
    mode='r'
    t=readfile(fn,mode)
    print(t)
    pass