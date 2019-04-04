#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import logger
from models import AnswerRobot
import time
mylogger=logger.logger()
answer_robot=AnswerRobot(mylogger)
t1=time.time()
answer_lst=answer_robot.match_answer()
t2=time.time()
answer_lst=answer_robot.adjust_rate(answer_lst)
print('匹配答案耗时',t2-t1,'秒')
if __name__=="__main__":
    pass