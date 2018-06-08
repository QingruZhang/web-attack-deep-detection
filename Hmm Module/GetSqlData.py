import pymysql
import sys
import json

def get_sql_data(sql):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='log',
                                 charset='utf8',
                                 port=3306,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(sql)
    data_list=[]
    for item in cursor:
        item.update(content_length=item.pop('content_len'))
        item.update(method=item.pop('type'))
        item.update(uri=item.pop('path'))
        item.update(flow_time=item.pop('time'))
        item.update(src_ip=item.pop('src'))
        item.update(dst_ip=item.pop('dst'))
        item.update(host=item.pop('domain'))
        item.update(user_agent=item.pop('useragent'))
        item['status']=''
        item['cookie']=''
        item['date']=''
        if item['method'][0]>='0' and item['method'][0]<='9' :
            itme['http_type']='Response'
        else:
            item['http_type']='Request'
        data_list.append(item)
    return data_list

if __name__=='__main__':
	table=sys.argv[1]
	sql=="select path from %s where domain like '%.shafc.edu.cn' ;"%table
	data_list=get_sql_data(sql)
	json.dump(data_list,open('%s_data.json'%table,'w'))