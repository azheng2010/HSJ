#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from models import MyWatchDog
if __name__=='__main__':
    user='13507499021'
    pwd='password'
    method='Auto'
    email='12345678@qq.com'
    rate_min= 80 
    rate_max= 95 
    watchdog=MyWatchDog(user,method,email,rate_min,rate_max)
    watchdog.showlog(fn='HSJ.txt')
    watchdog.choice()
    pass