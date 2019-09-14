#！/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2018-12-23 19:11:25
@author: wzh
Sys_Env : AMD64_Windows-7-6.1.7601-SP1_Python 3.6.1
Email:hrcl2015@126.com
WeChat: hrcl2015 (微信)
Filename:main.py
Description : 应用程序主入口
              2019-09-14更新
"""

from models import MyWatchDog
if __name__=='__main__':
    user='13870088955'#护世界账号,修改时注意单引号要保留
    pwd='123456789'#护世界登录密码，单引号保留
    method='Auto'#手动答题，下面的正确率设置无效
    email='12345678@qq.com'
    rate_min= 85 #正确率下限 0-100
    rate_max= 95 #正确率上限 0-100
    watchdog=MyWatchDog(user,pwd,method,email,rate_min,rate_max)
    watchdog.showlog(fn='HSJ.txt')#显示log
    watchdog.choice()#功能选择
    pass
    """第一次使用时，记得要修改账号密码，
    修改正确率大小，切记要保存
    保存方法：
    点上方文件夹图标，选择save，即保存
    """