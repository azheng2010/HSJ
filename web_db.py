#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
class MYDB():
    def __init__(self,user, passwd, db_name, host='localhost', port=3306, charset='utf8'):
        self.db_name=db_name
        self.db = pymysql.connect(host=host,port=port,user=user,passwd=passwd,
                                  db=db_name,charset=charset)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT VERSION()")
        data = self.cursor.fetchone()
        print("Database version : %s " % data)
    def create_table(self,table_name,field=None,mode='w'):
        self.cursor.execute("DROP TABLE IF EXISTS %s"%table_name)
        sql = """CREATE TABLE {tablename} (
                 FIRST_NAME  CHAR(20) NOT NULL,
                 LAST_NAME  CHAR(20),
                 AGE INT,
                 SEX CHAR(1),
                 INCOME FLOAT )""".format(tablename=table_name)
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
    def query(self,table_name,query_keyword,all_display=True,col_list=None):
        if (not all_display) and col_list:
            sql = "SELECT {cols} FROM {tablename} WHERE {queryword}".format(
                    cols=','.join(col_list),
                    tablename=table_name,
                    queryword=query_keyword)
        else:
            sql = "SELECT * FROM {tablename} WHERE {queryword}".format(
                    tablename=table_name,
                    queryword=query_keyword)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            if results is None:
                print("查询结果为空")
            else:
                for row in results:
                    print(row)
            print('-'*20)
            print('共查询到 %s个结果！\n'%len(results))
        except:
            print("Error: unable to fetch data")
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
if __name__=='__main__':
    mydb=MYDB('root','mysql','hsj_tiku')
    col_list=mydb.list_col_table('tiku')[1:]
    print(col_list)
    data=[None, 650375, '组成护理程序框架的理论是：', 'A.人的基本需要论', 'B.一般系统论', 'C.方法论', 'D.信息交流论', 'E.解决问题论', '', '', '', 'B', '中公医考题APP', '单选A1', '护士资格', '在众多相关理论中，一般系统论构成了护理程序的基本框架，是护理程序的步骤及内涵的核心。']
    mydb.insert_many_data2('tiku',col_list,[data,data,data])
    mydb.close()
    pass