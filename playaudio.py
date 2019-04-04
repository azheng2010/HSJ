#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,platform
from comm import audiopath
if platform.system()=='Linux':
    from kivy.core.audio import SoundLoader
def playsound(fn):
    if platform.system()=='Linux':
        if not os.path.exists(audiopath+fn):
            print('[%s]文件不存在！'%fn)
            return
        sound = SoundLoader.load(audiopath+fn)
        if sound:
            sound.play()
            print("Sound is %.3f seconds" % sound.length)
    else:
        print('非安卓平台不能播放声音！')
if __name__=='__main__':
    playsound('Gmail.wav')
    pass