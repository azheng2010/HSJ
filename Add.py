#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from mysql_db import MYDB
from yikaoti import get_all_questions
db_info={'user':'root',
        'passwd':'mysql',
        'db_name':'hsj_tiku',
        'host':'localhost',
        'port':3306,
        'charset':'utf8',}
def add_hsj_file(fpath,note,file_encrpt=True,table_name='tiku',method='append'):
    from comm import MyHSJ
    if not fpath:fpath='questions.data'
    myapp=MyHSJ(datapath=fpath,encrpt=file_encrpt)
    mydb=MYDB(db_info['user'],db_info['passwd'],db_info['db_name'],
              host=db_info['host'], port=db_info['port'],
              charset=db_info['charset'])
    if method=='new':mydb.clear_data(table_name)
    col_list=mydb.list_col_table(table_name)[1:]
    data_list=[]
    for x in myapp.questions:
        options=x[5].splitlines()
        num=len(options)
        for i in range(8-num):
            options.append('')
        dic={}
        dic['other_qid']=None
        dic['hsj_qid']=x[0]
        dic['title']=x[1]
        dic['optionA']=options[0]
        dic['optionB']=options[1]
        dic['optionC']=options[2]
        dic['optionD']=options[3]
        dic['optionE']=options[4]
        dic['optionF']=options[5]
        dic['optionG']=options[6]
        dic['optionH']=options[7]
        dic['answer']=''.join(x[4])
        dic['note']=note
        dic['type_name']=x[6]
        dic['classification']=x[7]
        dic['parsing']=None
        data_one=[dic[col] for col in col_list]
        data_list.append(data_one)
    mydb.insert_many_data2(table_name,col_list,data_list,limit=1000)
    mydb.close()
def add_yikaoti_app(table_name='tiku',method='append'):
    print('正在从医考题APP添加题库……')
    yikaoti=get_all_questions()
    print(yikaoti[-1])
    mydb=MYDB(db_info['user'],db_info['passwd'],db_info['db_name'],
              host=db_info['host'], port=db_info['port'],
              charset=db_info['charset'])
    if method=='new':mydb.clear_data(table_name)
    col_list=mydb.list_col_table(table_name)[1:]
    data_list=[]
    for dic in yikaoti:
        data_one=[dic[col] for col in col_list]
        data_list.append(data_one)
    mydb.insert_many_data2(table_name,col_list,data_list)
    mydb.close()
if __name__=='__main__':
    add_hsj_file('18274465516.data','武冈市人民医院',file_encrpt=True,table_name='tiku',method='append')
    pass