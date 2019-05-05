#！/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2018-12-23 19:11:25
@author: wzh
Sys_Env : AMD64_Windows-7-6.1.7601-SP1_Python 3.6.1
Email:hrcl2015@126.com
WeChat: hrcl2015 (WeiXin)
Filename:main.py
Description : 应用程序主入口
"""

from models import MyWatchDog
if __name__=='__main__':
    user='13870088955'#护世界账号,修改时注意单引号要保留
    pwd='123456789'#护世界登录密码，单引号保留
    method='Auto'#手动答题，下面的正确率设置无效
    email='12345678@qq.com'
    rate_min= 80 #正确率下限 0-100
    rate_max= 90 #正确率上限 0-100
    watchdog=MyWatchDog(user,pwd,method,email,rate_min,rate_max)
    watchdog.showlog(fn='HSJ.txt')
    watchdog.login()
    pass



    """
                                 _ooOoo_
                                o8888888o
                                88" . "88
                                (| -_- |)
                                 O\ = /O
                             ____/`---'\____
                           .   ' \\| |// `.
                            / \\||| : |||// \
                          / _||||| -:- |||||- \
                            | | \\\ - /// | |
                          | \_| ''\---/'' | |
                           \ .-\__ `-` ___/-. /
                        ___`. .' /--.--\ `. . __
                     ."" '< `.___\_<|>_/___.' >'"".
                    | | : `- \`.;`\ _ /`;.`/ - ` : | |
                      \ \ `-. \_ __\ /__ _/ .-` / /
              ======`-.____`-.___\_____/___.-`____.-'======
                                 `=---='
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              .............................................
    """