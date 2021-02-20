#！/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
import time
import os,json,random
from comm import DBCONF
tk_col_ex = {'qid':0,'stem':1,'answer_txt':2,'pinyin':3,'answer_symbol':4,'options':5,
          'qtype':6,  'mark':7,'hospital':8,'source':9,'update_time':10,'user':11}
db_col=['qtype', 'stem', 'options', 'answer_txt', 'answer_symbol', 'solution',
        'company', 'origin', 'mark', 'update_time','user']
db_index={x:i for i,x in enumerate(db_col)}
tk_to_db={'qtype':'qtype', 'stem':'stem', 'options':'options', 'answer_txt':'answer_txt',
          'answer_symbol':'answer_symbol', 'solution':'pinyin','company':'hospital',
          'origin':'source', 'mark':'mark', 'update_time':'update_time','user':'user'}
hsjuser_db_col=["userid","updatetime","account","password","name","sex","workid",
                "job","staffProperty","hospitalId","hospitalName",
                "departmentId","departmentName","maxEducation","phone","nurseLevel",
                "departmentManeger","hospitalManager","professionalTitle","usernameid"]
class HSJ_WEB_DB():
    def __init__(self,user, passwd, db_name, table_name,host='localhost', port=3306, charset='utf8',display=True):
        self.db_name=db_name
        self.table_name=table_name
        self.db = pymysql.connect(host=host,port=port,user=user,passwd=passwd,
                                  db=db_name,charset=charset)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT VERSION()")
        self.addnum=0
        self.modifynum=0
        data = self.cursor.fetchone()
        if data:
            self.version=data
            if display:print("Successfully connected to the remote database!")
        self.dbcol_lst=self.list_col_table()
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
    def insert_data(self,col_list,data_list):
        data_list=self.pre_data(data_list)
        sql = "INSERT INTO {tablename}({col}) VALUES ({data})".format(
                tablename=self.table_name,col=','.join(col_list),
                data=','.join(data_list))
        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.addnum+=1
            flag=True
        except:
            flag=False
        return flag
    def insert_many_data(self,table_name,col_list,data_list,limit=1000):
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
    def insert_many_data2(self,col_list,data_list,limit=1000):
        sql0 = "INSERT INTO {tablename}({col}) VALUES ".format(
                tablename=self.table_name,col=','.join(col_list))
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
            print('表%s成功插入%s条记录'%(self.table_name,len(data_list)))
        except :
            self.db.rollback()
            print('Error: %s 语句未能成功执行！'%sql)
    def writetxt(self,fpath,txt,mode='w'):
        try:
            with open(fpath,mode=mode,encoding='utf-8') as f:
                f.write(txt)
        except:
            time.sleep(random.uniform(0,3))
            with open(fpath,mode=mode,encoding='utf-8') as f:
                f.write(txt)
    def query(self,query_keyword=None,col_list=None,limit_i=0,limit_n=None,display=False):
        if query_keyword is None:
            where_txt=''
        else:
            where_txt='WHERE {queryword}'.format(queryword=query_keyword)
        if limit_n is None:
            limit_txt=''
        else:
            limit_txt='LIMIT {i},{n}'.format(i=limit_i,n=limit_n)
        if col_list is None:
            col_list=self.dbcol_lst
            select_txt=','.join(col_list)
        else:
            select_txt=','.join(col_list)
        sql = "SELECT {cols} FROM {tablename} {where_cmd} {limit}".format(
                cols=select_txt,
                tablename=self.table_name,
                where_cmd=where_txt,
                limit=limit_txt)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            if results is None:
                print("No query found!")
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
                print('%s records found!'%len(results))
            return lst
        except:
            print("Error: unable to fetch data")
            self.writetxt('queryerror.txt','%s\n'%sql,mode='a')
            results=None
            return results
    def update_data(self,setdata,condition):
        if setdata:
            set_sql='SET %s'%setdata
        else:
            set_sql=''
        if condition:
            where_sql='WHERE %s'%condition
        else:
            where_sql=''
        sql = "UPDATE {tablename} {setsql} {wheresql}".format(
                tablename=self.table_name,
                setsql=set_sql,
                wheresql=where_sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.modifynum+=1
            print('%s records updated successfully!'%self.modifynum)
            flag=True
        except:
            print('Error:[ %s ] command failed!'%sql)
            flag=False
        return flag
    def count_datas(self,col='stem'):
        self.cursor.execute("select count(%s) from %s"%(col,self.table_name))
        one=self.cursor.fetchone()
        return one[0]
    def list_col_table(self):
        self.cursor.execute("select * from %s limit 1"%self.table_name)
        col_name_list = [tuple[0] for tuple in self.cursor.description]
        return col_name_list
    def list_table(self):
        self.cursor.execute("show tables")
        table_list = [tuple[0] for tuple in self.cursor.fetchall()]
        return table_list
    def close(self):
        self.cursor.close()
        self.db.close()
def list_split(lst,limit):
    yushu=len(lst)%limit
    shang=len(lst)//limit
    lst2=[]
    for x in range(shang):
        lst2.append(lst[x*limit:(x+1)*limit])
    if yushu>0:
        lst2.append(lst[shang*limit:])
    return lst2
def escape_string(value, mapping=None):
    value = value.replace('\\', '\\\\')
    value = value.replace('\0', '\\0')
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('\032', '\\Z')
    value = value.replace("'", "\\'")
    value = value.replace('"', '\\"')
    return value
def insert_hsj_datas(datas,dbcol,hospital,source,user,myclientdb,start=0):
    length=len(datas)
    insert_datas=[]
    for ix in range(start,length):
        data=datas[ix]
        update_time= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        data=data+[hospital,source,update_time,user]
        data[tk_col_ex['answer_txt']]='|'.join(data[tk_col_ex['answer_txt']])
        data[tk_col_ex['answer_symbol']]=''.join(data[tk_col_ex['answer_symbol']])
        one=[data[tk_col_ex[tk_to_db[x]]] for x in dbcol]
        if not is_contain_chinese(one[db_index['solution']]):
            one[db_index['solution']]=''
        insert_datas.append(one)
    myclientdb.insert_many_data2(dbcol,insert_datas)
def questions_to_webdb(questions,hospitalname,source,user,start=0):
    dbuser,dbpwd,host,port,dbname,tablename=DBCONF
    myclientdb=HSJ_WEB_DB(dbuser,dbpwd,dbname,tablename,host=host,port=port,charset='utf8')
    insert_hsj_datas(questions,db_col,hospitalname,source,user,myclientdb,start=start)
    num=myclientdb.count_datas()
    print('Total current records: ',num)
    myclientdb.close()
def insert_txt_to_webdb(datalst,showmsg=True):
    dbuser,dbpwd,host,port,dbname,tablename=DBCONF
    tablename='txt_lst'
    myclientdb=HSJ_WEB_DB(dbuser,dbpwd,dbname,tablename,host=host,port=port,charset='utf8',display=showmsg)
    cols=['fn_start','fn','updatetime']
    myclientdb.insert_data(cols,datalst)
    num=myclientdb.count_datas(col='fn_start')
    if showmsg:print('Total current records: ',num)
    myclientdb.close()
    return num
def get_txt_from_webdb(showmsg=True):
    dbuser,dbpwd,host,port,dbname,tablename=DBCONF
    tablename='txt_lst'
    myclientdb=HSJ_WEB_DB(dbuser,dbpwd,dbname,tablename,host=host,port=port,charset='utf8',display=showmsg)
    lst=myclientdb.query(col_list=['fn_start'])
    lst=[x['fn_start'] for x in lst]
    if showmsg:print('records: ',len(lst))
    myclientdb.close()
    return lst,len(lst)
def is_contain_chinese(check_str):
    for ch in check_str:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False
def is_chinese(string):
    for chart in string:
        if chart < u'\u4e00' or chart > u'\u9fff':
            return False
    return True
def insert_hsjuser_data(userinfo):
    dbuser,dbpwd,host,port,dbname,tablename=DBCONF 
    tablename="hsjuser"
    user_db_col=hsjuser_db_col[1:] 
    myclientdb=HSJ_WEB_DB(dbuser,dbpwd,dbname,tablename,host=host,port=port,charset='utf8')
    results=myclientdb.query(query_keyword="account='%s'"%userinfo["account"])
    if results:
        condition="account='%s'"%userinfo["account"]
        setdata_lst=[]
        for x in user_db_col:
            if type(userinfo[x]) is str:
                setdata_lst.append("%s = '%s'"%(x,userinfo[x]))
            else:
                info = userinfo[x] if userinfo[x] else 'null'
                setdata_lst.append("%s = %s"%(x,info))
        setdata=','.join(setdata_lst)
        myclientdb.update_data(setdata,condition)
    else:
        onebar=[ userinfo[x] for x in user_db_col ]
        myclientdb.insert_data(user_db_col,onebar)
    myclientdb.close()
def loaddata(fdir,fn):
    fp=os.path.join(fdir,fn)
    if os.path.exists(fp):
        with open(fp,'r',encoding='utf-8') as f:
            txt=f.read()
            j=json.loads(txt)
        print('数据已加载完成！共%s题'%len(j))
        return j
def insert_xxqg_data():
    fdir='C:/Users/wzh/Desktop/'
    j=loaddata(fdir,'xxqg_data.json')
    col_list=['category','stem','options','answertxt','answer','reference','notes']
    dic={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':7}
    datas=[[x['category'],x['content'],'\n'.join(x['options']),'|'.join([x['options'][dic[y]] for y in x['answer']]),x['answer'],x['reference'],x['notes']] for x in j]
    dbuser,dbpwd,host,port,dbname,tablename=DBCONF
    tablename='xxqgdata'
    myclientdb=HSJ_WEB_DB(dbuser,dbpwd,dbname,tablename,host=host,port=port,charset='utf8')
    myclientdb.insert_many_data2(col_list,datas)
    myclientdb.close()
if __name__=="__main__":
    insert_xxqg_data()
    pass