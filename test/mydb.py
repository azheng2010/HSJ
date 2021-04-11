#！/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2020-11-14 23:17:42
Author: wzh
Platform: Python 3.7.4 Windows-10-10.0.18362-SP0 AMD64
Email: hrcl2015@126.com
Wechat: hrcl2015
Filename: mydb.py
Description :数据库操作类对象

"""
import time,json,os,platform
import hashlib
import pymysql
from models.comm import confdir,get_myip_from_httpbin
#confdir='C:/Users/wzh/Desktop/python_Flask_lantu/config/'#本地测试时使用
def md5(txt):
    """文本的MD5加密"""
    if txt and (type(txt) is str):
        return hashlib.md5(txt.encode(encoding='UTF-8')).hexdigest()
    elif txt and (type(txt) is bytes):
        return hashlib.md5(txt).hexdigest()
    else:
        return None

class MYDB_client:
    def __init__(self,user=None,passwd=None,db_name=None,table_name='',host='localhost',port=3306,charset='utf8'):
        '''初始化数据库，创建数据库对象，游标对象'''
        if user is None:
            user,passwd,db_name,table_name,host,myport=self.readconfig_db()#读取配置文件
        self.addnum=0#增加记录条数
        self.modifynum=0#修改记录条数
        self.col_index=None#字段位置对应表,dict
        self.db_name=db_name#数据库名称
        self.table_name=table_name#表名,默认不指定
        self.db = pymysql.connect(host=host,port=myport,user=user,passwd=passwd,
                                  db=db_name,charset=charset)# 打开数据库连接
        self.cursor = self.db.cursor()#创建一个游标对象 cursor
        self.cursor.execute("SELECT VERSION()")#查询版本
        data = self.cursor.fetchone()#获取查询单条数据.
        #print("Database version : %s " % data)
    def readconfig_db(self,fn='DB.conf'):
        fpath=confdir+fn
        with open(fpath,'r',encoding='utf-8') as f:
            txt=f.read()
        j=json.loads(txt)
        if platform.system()=='Windows':
            dbinfo=j["Windows"]
            return dbinfo["user"],dbinfo["passwd"],dbinfo["db_name"],dbinfo["table_name"],dbinfo["hosturl"],dbinfo["port"]
        elif platform.system()=='Linux':
            dblinux=j["Linux"]
            myip=get_myip_from_httpbin()
            dbinfo=dblinux[myip]
            return dbinfo["user"],dbinfo["passwd"],dbinfo["db_name"],dbinfo["table_name"],dbinfo["hosturl"],dbinfo["port"]
        else:
            return None, None,None,None,None

    def query(self,table_name,query_keyword=None,col_list=None,limit_i=0,limit_n=None,display=False):
        '''查询数据库，返回并打印结果
        col_list------->需要打印的字段列表，默认为全部字段
        table_name----->要查询的表名
        query_keyword-->改成tuple,防止SQL注入：("stem like '%%%s%%'",keywords)
        查询的语句，要符合sql语法 如 NAME = 'xiaoming'
                                              或 INCOME > 100 等等
        '''
        if query_keyword is None:
            where_txt=''
        elif isinstance(query_keyword,tuple):
            where_txt='WHERE {queryword}'.format(queryword=query_keyword[0])
        elif isinstance(query_keyword,str):
            where_txt='WHERE {queryword}'.format(queryword=query_keyword)
        else:
            where_txt=''
        if limit_n is None:
            limit_txt=''
        else:
            limit_txt='LIMIT {i},{n}'.format(i=limit_i,n=limit_n)
        if col_list is None:
            col_list=self.list_col_table(table_name)#所有字段
            select_txt=','.join(col_list)
            #select_txt='*'
        else:
            select_txt=','.join(col_list)
        self.col_index={c:i for i,c in enumerate(col_list)}#字段列表，用于结果数据中查找options所在位置
        sql = "SELECT {cols} FROM {tablename} {where_cmd} {limit}".format(
                cols=select_txt,
                tablename=table_name,
                where_cmd=where_txt,
                limit=limit_txt)
        #print('-'*20,sql,'-'*20,sep='\n')
        try:
            if isinstance(query_keyword,tuple):
                self.cursor.execute(sql,query_keyword[1])#使用参数传递，防止SQL注入攻击
            else:
                self.cursor.execute(sql)# 执行SQL语句,全文搜索match() against()
            results = self.cursor.fetchall()# results是个元组对象
            return results
        except:
            print("Error: unable to fetch data")
            results=None
            return results
    def pre_data(self,data_list):
        '''插入数据预处理，主要是字符串加单引号
        本身有单引号的转成\'，数字转成字符串型,数字还是保持原来的类型
        空字符串或None则转换成null'''
        new_list=[]
        for x in data_list:
            if type(x)==str and x.find("\\")>-1:
                x=x.replace("\\","\\\\")
            if  x is None or x=='':#
                x='NULL'
            elif type(x)==str and x.find("'")>-1:
                x=x.replace("'","\\'")
                x="'"+x+"'"
            elif type(x)==str and x.find("'")==-1:
                x="'"+x+"'"
            elif type(x)==int:
                pass
            elif type(x)==float:
                pass
            else:
                x=str(x)
                
            new_list.append(x)
        return new_list
    def insert_data(self,table_name,col_list,data_list):
        '''向数据库table表中插入单条数据
        col_list-->需插入的字段名列表
        data_list->单条数据列表，与字段名对应'''
        #去重插入数据，”INSERT IGNORE INTO 和 REPLACE INTO“：
        #INSERT IGNORE会忽略数据库中已经存在的数据，如果数据库没有数据，就插入新的数据，如果有数据的话就跳过这条数据。这样就可以保留数据库中已经存在数据，达到在间隙中插入数据的目的
        #REPLACE INTO 如果存在primary 或 unique相同的记录，则先删除掉。再插入新记录。
        data_list=self.pre_data(data_list)#数据预处理,字符串的数据加上引号
        data_list=[str(d) for d in data_list]#把数字转换成str，但不加引号
        sql = "INSERT INTO {tablename}({col}) VALUES ({data})".format(
                tablename=table_name,col=','.join(col_list),
                data=','.join(data_list))
        #print(sql)#测试
        try:
            self.cursor.execute(sql)# 执行sql语句
            self.db.commit()# 提交到数据库执行
            self.addnum+=1
            print('Insert records: ',self.addnum)
            flag=True
        except:
            #self.db.rollback()# 如果发生错误则回滚
            print('Error: %s 语句未能成功执行！'%sql)
            #self.writetxt('notinsert.txt','%s\n'%data_list,mode='a')##############
            flag=False
        return flag
    def delete_data(self,table_name,query_txt):
        '''删除数据库table表中符合条件的数据,慎重使用！！！
        query_txt-->查询条件'''
        if not query_txt:return False
        #if 'or' in query_txt#如何防止SQL注入
        sql = "DELETE FROM {tablename} WHERE {query}".format(
                tablename=table_name,query=query_txt)
        #print(sql)#测试
        try:
            self.cursor.execute(sql)# 执行sql语句
            self.db.commit()# 提交到数据库执行
            print('delete data successfully')
            flag=True
        except:
            #self.db.rollback()# 如果发生错误则回滚
            print('Error: %s 语句未能成功执行！'%sql)
            #self.writetxt('notinsert.txt','%s\n'%data_list,mode='a')##############
            flag=False
        return flag

    def update_data(self,table_name,setdata,condition):
        '''更新数据,修改数据
        table_name----->要修改数据的表名
        setdata-------->设置数据表达式，如 AGE = AGE + 1
        condition------>where条件，如 SEX = 'M'
        '''
        if setdata:
            set_sql='SET %s'%setdata
        else:
            set_sql=''
        if condition:
            where_sql='WHERE %s'%condition
        else:
            where_sql=''
        # SQL 更新语句
        sql = "UPDATE {tablename} {setsql} {wheresql}".format(
                tablename=table_name,
                setsql=set_sql,
                wheresql=where_sql)
        #print('-'*5+'\n',sql)
        try:
            self.cursor.execute(sql)# 执行SQL语句
            self.db.commit()# 提交执行
            self.modifynum+=1
            #print(self.modifynum,'成功修改一条记录：',where_sql)
            print('%s records updated successfully!'%self.modifynum)
            flag=True
        except:
            #self.db.rollback()#回滚
            print('Error:[ %s ] command failed!'%sql)
            flag=False
        return flag

    def list_col_table(self,table_name):
            '''列出指定表的所有字段'''
            self.cursor.execute("select * from %s limit 1"%table_name)
            col_name_list = [tuple[0] for tuple in self.cursor.description]
            #print('表%s的所有字段：\n%s'%(table_name,col_name_list))
            return col_name_list
    def count_datas(self,table_name):
        """统计指定表中有记录条数"""
        self.cursor.execute("select count(stem) from %s"%table_name)
        one=self.cursor.fetchone()
        return one[0]
    def close(self):
        '''关闭游标，关闭数据库连接'''
        self.cursor.close()# 关闭游标
        #print('cursor对象关闭!')
        self.db.close()# 关闭数据库连接
        #print('关闭db连接!')
    def escape_string(self,value):
        """字符转义，防注入"""
        #assert isinstance(value, (bytes, bytearray))
        value = value.replace('\\', '\\\\')
        value = value.replace('\0', '\\0')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\032', '\\Z')
        value = value.replace("'", "\\'")
        value = value.replace('"', '\\"')
        return value
#----------------------------------------------------------
def read_dbnum(fn='DB.conf'):
    fpath=confdir+fn
    with open(fpath,'r',encoding='utf-8') as f:
        txt=f.read()
    j=json.loads(txt)
    return j["DBnum"]

def insert_hsjuser_data(userinfo):
    """向用户表中插入记录，先判断是否存在，再添加或更新"""
    dbuser,dbpwd,host,port,dbname,tablename=DBCONF # table = tiku
    tablename="hsjuser"
    user_db_col=hsjuser_db_col[1:] # 第一个userid自增，去掉
    myclientdb=MYDB(dbuser,dbpwd,dbname,tablename,host=host,port=port,charset='utf8')
    results=myclientdb.query(query_keyword="account='%s'"%userinfo["account"])#先查询有没有相同记录
    if results:
        #print('有重复的记录')
        condition="account='%s'"%userinfo["account"]#修改标签的条件qid唯一值 WHERE qid=15478
        setdata_lst=[]
        for x in user_db_col:
            if type(userinfo[x]) is str:
                setdata_lst.append("%s = '%s'"%(x,userinfo[x]))
            else:
                info = userinfo[x] if userinfo[x] else 'null'
                setdata_lst.append("%s = %s"%(x,info))
        #setdata_lst=[ '%s = %s'%(x,userinfo[x] if userinfo[x] else 'null') for x in user_db_col ]
        setdata=','.join(setdata_lst)
        myclientdb.update_data(setdata,condition)#更新数据
        #UPDATE hsjuser SET company='xxx',origin='yyy',mark='zzz' WHERE qid=215792
    else:
        onebar=[ userinfo[x] for x in user_db_col ]
        myclientdb.insert_data(user_db_col,onebar)#不重复，直接插入
    myclientdb.close()
    
#mydbclient=MYDB_client(user,passwd,db_name,host=hosturl)
if __name__=='__main__':
    #mydbclient=MYDB_client(user,passwd,db_name,host=hosturl)
    #mydbclient=MYDB_client()
    pass
