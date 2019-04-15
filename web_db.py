#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
from comm import load_data_only,tk_col
class MYDB():
    def __init__(self,user, passwd, db_name, host='localhost', port=3306, charset='utf8'):
        self.db_name=db_name
        self.db = pymysql.connect(host=host,port=port,user=user,passwd=passwd,
                                  db=db_name,charset=charset)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT VERSION()")
        self.addnum=0
        self.modifynum=0
        data = self.cursor.fetchone()
        print("Database version : %s " % data)
    def create_table(self,table_name,field=None,mode='w'):
        self.cursor.execute("DROP TABLE IF EXISTS %s"%table_name)
        sql = """CREATE TABLE {tablename} (
              'qid' int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '题目id，不为空，自增，唯一性',
              'stem' text,
              'options' text,
              'answer_txt' text,
              'answer_symbol' char(30) DEFAULT NULL,
              'qtype' char(20) DEFAULT NULL,
              'company' char(255) DEFAULT NULL COMMENT '医院单位',
              'origin' char(255) DEFAULT NULL COMMENT '题目来源',
              'mark' text COMMENT '分类标签',
              PRIMARY KEY ('qid')
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """.format(tablename=table_name)
        self.cursor.execute(sql)
    def pre_data(self,data_list):
        new_list=[]
        for x in data_list:
            if type(x)==str and x.find("\\")>-1:
                x=x.replace("\\","\\\\")
            if  x is None or x=='':
                x='NULL'
            elif type(x)==str and x.find("'")>-1:
                x=x.replace("'","\\'")
                x="'"+x+"'"
            elif type(x)==str and x.find("'")==-1:
                x="'"+x+"'"
            else:
                x=str(x)
            new_list.append(x)
        return new_list
    def insert_data(self,table_name,col_list,data_list):
        data_list=self.pre_data(data_list)
        sql = "INSERT INTO {tablename}({col}) VALUES ({data})".format(
                tablename=table_name,
                col=','.join(col_list),
                data=','.join(data_list))
        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.addnum+=1
            print('共成功增加一条记录：',self.addnum)
        except:
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def insert_many_data(self,table_name,col_list,data_list,limit=1000):
        def list_split(lst,limit):
            yushu=len(lst)%limit
            shang=len(lst)//limit
            lst2=[]
            for x in range(shang):
                lst2.append(lst[x*limit:(x+1)*limit])
            if yushu>0:
                lst2.append(lst[shang*limit:])
            return lst2
        placeholder_lst=[]
        for x in col_list:
            placeholder_lst.append('%s')
        sql = "INSERT INTO {tablename}({col}) VALUES ({placeholder})".format(
                tablename=table_name,
                col=','.join(col_list),
                placeholder=','.join(placeholder_lst))
        data_list=[self.pre_data(data) for data in data_list]
        try:
            if len(data_list)>limit:
                data_split_list=list_split(data_list,limit)
                for i,data in enumerate(data_split_list):
                    self.cursor.executemany(sql,data)
                    self.db.commit()
                    print('分段执行插入命令[%s/%s]本段%s条记录'%(
                            i+1,len(data_split_list),len(data)))
            else:
                self.cursor.executemany(sql,data_list)
                self.db.commit()
            print('表%s成功插入%s条记录'%(table_name,len(data_list)))
        except :
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def insert_many_data2(self,table_name,col_list,data_list,limit=1000):
        def list_split(lst,limit):
            yushu=len(lst)%limit
            shang=len(lst)//limit
            lst2=[]
            for x in range(shang):
                lst2.append(lst[x*limit:(x+1)*limit])
            if yushu>0:
                lst2.append(lst[shang*limit:])
            return lst2
        sql0 = "INSERT INTO {tablename}({col}) VALUES ".format(
                tablename=table_name,
                col=','.join(col_list))
        data_list=[self.pre_data(data) for data in data_list]
        try:
            if len(data_list)>limit:
                data_split_list=list_split(data_list,limit)
                for i,data in enumerate(data_split_list):
                    sql_data_txt=','.join(['(%s)'%(','.join(d)) for d in data])
                    sql=sql0+sql_data_txt
                    self.cursor.execute(sql)
                    self.db.commit()
                    print('分段执行插入命令[%s/%s]本段%s条记录'%(
                            i+1,len(data_split_list),len(data)))
            else:
                sql_data_txt=','.join(['(%s)'%(','.join(d)) for d in data_list])
                sql=sql0+sql_data_txt
                self.cursor.execute(sql)
                self.db.commit()
            print('表%s成功插入%s条记录'%(table_name,len(data_list)))
        except :
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def query(self,table_name,query_keyword=None,col_list=None,display=False):
        if query_keyword is None:
            where_txt=''
        else:
            where_txt='WHERE {queryword}'.format(queryword=query_keyword)
        if col_list is None:
            col_list=self.list_col_table(table_name)
            select_txt='*'
        else:
            select_txt=','.join(col_list)
        sql = "SELECT {cols} FROM {tablename} {where_cmd}".format(
                cols=select_txt,
                tablename=table_name,
                where_cmd=where_txt)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            if results is None:
                print("查询结果为空")
                lst=None
            else:
                lst=[]
                for i,row in enumerate(results):
                    dic=dict(zip(col_list,row))
                    lst.append(dic)
                    if display:
                        print(i+1,dic)
                        print('-'*10)
            if display:
                print('共查询到 %s个结果！\n'%len(results))
            return lst
        except:
            print("Error: unable to fetch data")
            results=None
            return results
    def update_data(self,table_name,setdata,condition):
        if setdata:
            set_sql='SET %s'%setdata
        else:
            set_sql=''
        if condition:
            where_sql='WHERE %s'%condition
        else:
            where_sql=''
        sql = "UPDATE {tablename} {setsql} {wheresql}".format(
                tablename=table_name,
                setsql=set_sql,
                wheresql=where_sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.modifynum+=1
            print(self.modifynum,'成功修改一条记录：',where_sql)
        except:
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def clear_data(self,table_name):
        sql = 'truncate table {table_name}'.format(table_name=table_name)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print('表[%s]中数据已清空，不可恢复！！'%table_name)
        except:
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def delete_data(self,table_name,condition):
        if condition:
            where_sql='WHERE %s'%condition
        else:
            where_sql=''
        sql = "DELETE FROM {tablename} {wheresql}".format(
                tablename=table_name,
                wheresql=where_sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def count_datas(self,table_name):
        self.cursor.execute("select count(stem) from %s"%table_name)
        one=self.cursor.fetchone()
        return one[0]
    def list_col_table(self,table_name):
        self.cursor.execute("select * from %s limit 1"%table_name)
        col_name_list = [tuple[0] for tuple in self.cursor.description]
        return col_name_list
    def list_table(self):
        self.cursor.execute("show tables")
        table_list = [tuple[0] for tuple in self.cursor.fetchall()]
        print('数据库%s的所有表格：\n%s'%(self.db_name,table_list))
        return table_list
    def close(self):
        self.cursor.close()
        print('cursor对象关闭!')
        self.db.close()
        print('关闭db连接!')
def make_set_data_txt(cols,result,dic):
    lst=[]
    for col in cols:
        if result[col] is None:
            set_txt="%s='%s'"%(col,dic[col])
        elif dic[col] not in result[col]:
            set_txt="%s='%s|%s'"%(col,result[col],dic[col])
        else:
            set_txt=None
        if set_txt:lst.append(set_txt)
    return ' , '.join(lst)
def add_data_to_db(datafilename,origin,company):
    mydb=MYDB('root','mysql2019','hsj')
    col_list=mydb.list_col_table('tiku')
    col_list=col_list[1:]
    qids,questions=load_data_only(datafilename)
    qtotal=len(questions)
    for i,q in enumerate(questions):
        print('正在处理[%s/%s]'%(i+1,qtotal))
        question='\n'.join([q[tk_col['stem']],q[tk_col['options']]])
        results=mydb.query('tiku',query_keyword="question = '%s'"%question,
                           col_list=['qid','origin','company','mark'])
        if results :
            for r in results:
                cols=['origin','company','mark']
                dic={'origin':origin,'company':company,'mark':q[tk_col['mark']]}
                where_txt='qid = %s'%r['qid']
                set_txt=make_set_data_txt(cols,r,dic)
                if set_txt:
                    mydb.update_data('tiku',set_txt,where_txt)
        else:
            record=[]
            for col in col_list:
                if col in tk_col.keys():
                    if type(q[tk_col[col]]) is list:
                        y='|'.join(q[tk_col[col]])
                    else:
                        y=q[tk_col[col]]
                    record.append(y)
                else:
                    if col=='parsing':record.append('')
                    if col=='question':record.append(question)
                    if col=='origin':record.append(origin)
                    if col=='company':record.append(company)
            mydb.insert_data('tiku',col_list,record)
    count=mydb.count_datas('tiku')
    print('当前表中有记录%s条\n本次新增了%s条,修订了%s条'%(count,mydb.addnum,mydb.modifynum))
    mydb.close()
if __name__=='__main__':
    origin='AHUAPP'
    datafilename='阿虎医考护理题库.data'
    company=''
    add_data_to_db(datafilename,origin,company)
    pass