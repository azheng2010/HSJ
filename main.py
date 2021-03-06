#！/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2018-12-23 19:11:25
@author: hrcl2015
Sys_Env : AMD64_Windows-7-6.1.7601-SP1_Python 3.6.1
Email:hrcl2015@126.com
WeChat: hrcl2015 (微信)
Filename:main.py
Description : 应用程序主入口
    版本:0.5.4  2020-09-07,第54次更新
    第一次使用时，记得要修改账号密码，
    修改正确率大小，切记要保存
    保存方法：
    点上方文件夹图标，选择save，即保存

"""

from models import MyWatchDog
if __name__=='__main__':
    user='你的护世界账号'#修改时保留单引号
    pwd='你的护世界密码'#单引号保留
    rate_min,rate_max=(85,90)#正确率区间(百分比)
    method='Auto'#Auto自动答题,Manual手动答题
    email='12345678@qq.com'#提醒邮箱
    comdata=0#是否开启公用题库1启用0关闭
    webdb=0#是否开启网络数据库1启用0关闭
    webpage=0#是否开启网页搜索1启用0关闭（暂未开发）
    watchdog=MyWatchDog(user,pwd,method,email,rate_min,rate_max)
    watchdog.save_search_mode(comdata,webdb,webpage)
    watchdog.showlog(fn='HSJ.txt')
    watchdog.watchdoginit()
    watchdog.choice()
    pass
