import pymysql
import os
import json
import sys
import signal
import urllib.parse
from time import sleep


def extractDomain(referer):
    if referer[0:4]=='http':
        referlist=referer.split('/')
        return referlist[2]
    else:
        return referer

def process_except_path(request):
    new_req=request[0:3]+['']+request[-10:-1]+[request[-1]]
    path=request[3]
    for section in request[4:-10]:
        path=path+'|'+section
    new_req[3]=path
    return new_req

def getsql(request):
    global sql_template
    global tmplist
    drequest=dict(zip(tmplist,request))
    sql=sql_template%drequest
    return sql

    

if __name__=='__main__':
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='log',
                                 charset='utf8',
                                 port=3306,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    file='~/httpdata/'+sys.argv[1]
    database=sys.argv[2]

    with open('%s'%file,'rb') as f:
        ID=0
        sql_template="""insert into weblog_nomatch (time,type,domain,path,content_type,content_len,referer,src,src_port,dst,dst_port,useragent,ID,raw_path) 
                values( '%(time)s','%(type)s','%(domain)s','%(path)s','%(content_type)s','%(content_len)s','%(referer)s','%(src)s','%(src_port)s','%(dst)s','%(dst_port)s','%(useragent)s',%(ID)d,'%(raw_path)s' ); """.replace('weblog_nomatch',database)
        for line in f:
            request=line.decode('utf8').split('|')
            request.append(ID)
            request.append(request[3])
            # print('former',request[3])
            request[3]=str(urllib.parse.unquote(request[3]))
            tmplist=['time','type','domain','path','content_type','content_len','referer','src','src_port','dst','dst_port','useragent','ID','raw_path']
            try:
                sql=getsql(request)
                print(sql)
            except:
                request=process_except_path(request)
                sql=getsql(request)
                print(sql)
                y=input('contine? y/n:')
                if y=='n' or y== 'N':
                    sys.exit(0)
            cursor.execute(sql)
            connection.commit()
            ID+=1
        connection.close()


