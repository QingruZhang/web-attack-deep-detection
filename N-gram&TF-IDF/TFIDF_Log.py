# coding: utf-8
import os
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
import urllib
import time
import pickle
import html
import re
import json


class N_gram_Model(object):

    def __init__(self,goodqueries='goodqueries.txt',badqueries='badqueries.txt'):
        good_query_list = self.get_query_list(goodqueries)
        bad_query_list = self.get_query_list(badqueries)
        
        good_y = [0 for i in range(0,len(good_query_list))]
        bad_y = [1 for i in range(0,len(bad_query_list))]

        queries = bad_query_list+good_query_list
        y = bad_y + good_y

        #converting data to vectors  定义矢量化实例
        self.vectorizer = TfidfVectorizer(tokenizer=self.get_ngrams)

        # 把不规律的文本字符串列表转换成规律的 ( [i,j],tdidf值) 的矩阵X
        # 用于下一步训练分类器 lgs
        X = self.vectorizer.fit_transform(queries)

        # 使用 train_test_split 分割 X y 列表
        # X_train矩阵的数目对应 y_train列表的数目(一一对应)  -->> 用来训练模型
        # X_test矩阵的数目对应      (一一对应) -->> 用来测试模型的准确性
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=20, random_state=42)

        # 定理逻辑回归方法模型
        self.lgs = LogisticRegression()

        # 使用逻辑回归方法训练模型实例 lgs
        self.lgs.fit(X_train, y_train)

        # 使用测试值 对 模型的准确度进行计算
        print('模型的准确度:{}'.format(self.lgs.score(X_test, y_test)))
    
    # 对 新的请求列表进行预测
    def predict(self,new_queries,predicttime=1):
        new_queries = [urllib.parse.unquote(url) for url in new_queries]
        X_predict = self.vectorizer.transform(new_queries)
        res = self.lgs.predict(X_predict)
        res_list = []
        fbg=open('badfromgood_%d.txt'%predicttime,'w')
        fb=open('badquery2_%d.txt'%predicttime,'w')
        with open('goodquery_result_%d.txt'%predicttime,'w') as f:            
            for q,r in zip(new_queries,res):
                tmp = '正常请求'if r == 0 else '恶意请求'
                q_entity = html.escape(q)            
                res_list.append({'url':q_entity,'res':r})
                reg_result=None
                if r:
                    print('|RESULT:|',r,q)
                    fb.write(q+'\n')
                elif not reg_result:
                    f.write(q+'\n')
                else:
                    print('|BAD FROM GOOD:|',r,q)
                    fbg.write(q+'|'+str(reg_result)+'\n')
        fbg.close()
        fb.close()
        return res

    def judge(self,paths):
        new_query=[urllib.parse.unquote(path) for path in paths]
        X_predict=self.vectorizer.transform(new_query)
        res=self.lgs.predict(X_predict)
        return list(res)
                

    # 得到文本中的请求列表
    def get_query_list(self,filename):
        directory = str(os.getcwd())
        filepath = directory + "/" + filename
        data = open(filepath,'r', encoding='UTF-8').readlines()
        query_list = []
        for d in data:
            d = str(urllib.parse.unquote(d))   #converting url encoded data to simple string
            query_list.append(d)
        return list(set(query_list))


    #tokenizer function, this will make 3 grams of each query
    def get_ngrams(self,query):
        tempQuery = str(query)
        ngrams = []
        for i in range(0,len(tempQuery)-3):
            ngrams.append(tempQuery[i:i+3])
        return ngrams

def sql_connect(sql):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='log',
                                 charset='utf8',
                                 port=3306,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(sql)
    path_list=[cell['path'] for cell in cursor ]
    connection.close()
    return path_list

#读入整理好的正则表达式
with open('REG.txt','r') as f:
    Repatterns=[]
    for line in f:
        reg=re.compile(line.strip())
        Repatterns.append(reg)


#规则匹配url
def re_match(url):
    global Repatterns
    for i,re_pattern in enumerate(Repatterns):
        if re_pattern.match(url):
            print('catch by ',i,re_pattern)
            return i
    return None

def get_inner_data(sql_hmm="select * from weblog0407 where domain like '%.shafc.edu.cn';"):
    if 'data_hmm' not in os.listdir('./'):
        data_hmm=get_sql_data(sql_hmm)
        print(len(data_hmm))
        with open('data_hmm','w') as f:
            json.dump(data_hmm,f)
    else:
        with open('data_hmm','r') as f:
            data_hmm=json.load(f)
    return data_hmm

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

if __name__ == '__main__':
    # 若 检测模型文件lgs.pickle 不存在,需要先训练出模型
    if 'lgs.pickle' not in os.listdir('./'):
        classifier1 = N_gram_Model('goodqueries.txt')
        with open('lgs.pickle','wb') as output:
            pickle.dump(classifier1,output)
    else:
        with open('lgs.pickle','rb') as f_model:
            classifier1=pickle.load(f_model)

    with open('testdata1_good.txt',encoding='utf8') as f_testg:
        testdata1_good=[data for data in f_testg]
    with open('testdata1_bad.txt',encoding='utf8') as f_testb:
        testdata1_bad=[data for data in f_testb]
    with open('badqueries.txt',encoding='utf8') as f_trainb:
        traindata1_bad=[data for data in f_trainb]
    with open('goodqueries.txt',encoding='utf8') as f_traing:
        traindata1_good=[data for data in f_traing]

    true_train_res=classifier1.judge(traindata1_good)
    false_train_res=classifier1.judge(traindata1_bad)
    true_test_res=classifier1.judge(testdata1_good)
    false_test_res=classifier1.judge(testdata1_bad)

    TP_train=true_train_res.count(0)
    FN_train=true_train_res.count(1)
    FP_train=false_train_res.count(0)
    TN_train=false_train_res.count(1)

    TP_test=true_test_res.count(0)
    FN_test=true_test_res.count(1)
    FP_test=false_test_res.count(0)
    TN_test=false_test_res.count(1)

    TP_FN=len(testdata1_good)
    FP_TN=len(testdata1_bad)
    FN_re=0
    for good_url in testdata1_good:
        if re_match(good_url):
            FN_re+=1
    TP_re=TP_FN-FN_re

    TN_re=0
    for bad_url in testdata1_bad:
        if re_match(bad_url):
            TN_re+=1
    FP_re=FP_TN-TN_re


    





