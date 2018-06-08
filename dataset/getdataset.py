#coding=utf-8
import urllib,operator,json
from functools import reduce 
import pickle
import pymysql
import os
import sys

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
        item['data']=''
        if item['method'][0]>='0' and item['method'][0]<='9' :
            item['http_type']='Response'
        else:
            item['http_type']='Request'
        data_list.append(item)
    return data_list

if __name__=='__main__':
	table='weblog0407'
	sql_hmm="select * from table where domain like '%.shafc.edu.cn'  ;".replace('table',table)
	if 'data_hmm' not in os.listdir('./'):
		data_hmm=get_sql_data(sql_hmm)
		print(len(data_hmm))
		with open('data_hmm','w') as f:
			json.dump(data_hmm,f)
	else:
		with open('data_hmm','r') as f:
			data_hmm=json.load(f)

	number=14
	setid=int(input('input your datasetid(zixuan--0,ballball--1,minghua--2,qingru--3):'))
	frag=len(data_hmm)//number
	total=1000
	f_done=open('done.txt','a').close()
	f_train=open('hmmTrainSet','a')
	f_good_txt=open('goodSetForHmm.txt','a')
	f_bad_txt=open('badSetForHmm.txt','a')
	with open('done.txt','r') as f_done:
		done=[int(i.strip()) for i in f_done if i.strip()!='']
		if not done:
			last=0
			f_train.write('[]')
		else:
			last=done[-1]+1
		print('last time is %d'%last)
	f_train.close()
	f_done=open('done.txt','a')

	with open('hmmTrainSet','r') as f_train:
		data_train=json.load(f_train)
		if not data_train:
			data_train=[]


	with open('hmmTrainSet','w') as f_train:
		for i,data in enumerate(data_hmm[setid*frag:(setid*frag+total)]):
			if i in done:
				continue
			f_done.write(str(i)+'\n')
			print('[Judge path %d]:%s'%(i,data['uri']))
			judge=input('0--bad,1--good,q--quit and save:')
			if judge=='0':
				data['tag']=0
				data_train.append(data)
				f_bad_txt.write(data['uri']+'\n')
			elif judge=='1':
				data['tag']=1
				data_train.append(data)
				f_good_txt.write(data['uri']+'\n')
			elif judge=='q':
				f_bad_txt.close()
				f_good_txt.close()
				f_done.close()
				json.dump(data_train,f_train)
				print('save and quit!')
				break
			else:
				print('your input is wrong')
		json.dump(data_train,f_train)
		f_bad_txt.close()
		f_good_txt.close()
		f_done.close()



