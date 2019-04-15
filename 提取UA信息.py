#！/usr/bin/env python3
# -*- coding: utf-8 -*-
def pick_ua(ua):
    import re
    re_s='\((Linux|iPhone).[^\)]*\)'
    m=re.search(re_s,ua,re.S)
    if m:
        out=m.group()
        print(out)
        return out
if __name__=="__main__":
    ua='Mozilla/5.0 (Linux; Android 7.1.1; MX6 Build/NMF26O; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044205 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x26070236) NetType/4G Language/zh_CN'
    t=pick_ua(ua)
    pass