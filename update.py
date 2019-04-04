#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from shutil import copy2, rmtree
import sys
def updatefile():
    copy2("/home/code/newest/file1.py", "/home/code/") 
    copy2("/home/code/newest/file2.py", "/home/code/")
    copy2("/home/code/newest/file3.py", "/home/code/")
    ...
    rmtree('/home/code/newest') 
    Popen("/home/code/program.py", shell=True) 
    sys.exit("exit to restart the true program")
if __name__=="__main__":
    sys.exit()
    pass