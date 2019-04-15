#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from models import MyWatchDog
if __name__=='__main__':
    user='18373759966'
    pwd='726655555'
    method='Auto'
    email='12345678@qq.com'
    rate_min= 80 
    rate_max= 90 
    watchdog=MyWatchDog(user,method,email,rate_min,rate_max)
    watchdog.showlog(fn='HSJ.txt')
    watchdog.choice()
    pass