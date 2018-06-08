#coding=utf-8
import urllib,operator,json
from utils import get_md5,is_chinese,decode
from HttpUtils import get_path,get_payload
import numpy as np
from hmmlearn.hmm import GaussianHMM
from xml.etree import ElementTree
from functools import reduce 
import pickle
import pymysql
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Extractor(object):
    def __init__(self,data):
        self.parameter={}
        self.data=data
        self.uri = urllib.parse.unquote(data["uri"].encode("utf-8").decode('utf8'))
        # self.path = decode(get_path(self.uri))
        self.path = get_path(self.uri)
        self.payload = get_payload(self.uri).strip("?")
        self.get_parameter()
    def get_parameter(self):
        if self.payload.strip():
            for (p_id,p_state,p_type,p_name) in self.url():
                self.parameter[p_id]={}
                self.parameter[p_id]["p_state"]=p_state
                self.parameter[p_id]["p_type"]=p_type
                self.parameter[p_id]["p_name"]=p_name
            (p_id,p_state,p_type,p_name)=self.uri_p_name()
            self.parameter[p_id] = {}
            self.parameter[p_id]["p_state"] = p_state
            self.parameter[p_id]["p_type"] = p_type
            self.parameter[p_id]["p_name"] = p_name
        if self.path.strip():
            (p_id,p_state,p_type,p_name)=self.path_p()
            self.parameter[p_id] = {}
            self.parameter[p_id]["p_state"] = p_state
            self.parameter[p_id]["p_type"] = p_type
            self.parameter[p_id]["p_name"] = p_name
        if self.data["http_type"].strip():
            (p_id,p_state,p_type,p_name)=self.http_type()
            self.parameter[p_id] = {}
            self.parameter[p_id]["p_state"] = p_state
            self.parameter[p_id]["p_type"] = p_type
            self.parameter[p_id]["p_name"] = p_name
        if self.data["content_length"]:
            (p_id, p_state,p_type,p_name) = self.content_length()
            self.parameter[p_id] = {}
            self.parameter[p_id]["p_state"] = p_state
            self.parameter[p_id]["p_type"] = p_type
            self.parameter[p_id]["p_name"] = p_name
        if self.data["cookie"].strip():
            for (p_id,p_state,p_type,p_name) in self.cookie():
                self.parameter[p_id] = {}
                self.parameter[p_id]["p_state"] = p_state
                self.parameter[p_id]["p_type"] = p_type
                self.parameter[p_id]["p_name"] = p_name
            (p_id,p_state,p_type,p_name)=self.cookie_p_name()
            self.parameter[p_id] = {}
            self.parameter[p_id]["p_state"] = p_state
            self.parameter[p_id]["p_type"] = p_type
            self.parameter[p_id]["p_name"] = p_name
        if self.data["data"].strip():
            p_names=""
            for (p_id, p_state, p_type, p_name) in self.post():
                self.parameter[p_id] = {}
                self.parameter[p_id]["p_state"] = p_state
                self.parameter[p_id]["p_type"] = p_type
                self.parameter[p_id]["p_name"] = p_name
                p_names+=p_name
            (p_id, p_state, p_type, p_name)=self.post_p_name(p_names)
            self.parameter[p_id] = {}
            self.parameter[p_id]["p_state"] = p_state
            self.parameter[p_id]["p_type"] = p_type
            self.parameter[p_id]["p_name"] = p_name
    def get_Ostate(self,s):
        """
        字母 =》'A'
        数字 =》'N'
        中文 =》'C'
        特殊字符不变

        :param s:
        :return:
        """
        A=self.get_num('A')
        N=self.get_num("N")
        C=self.get_num("C")
        state=[]
        s=str(s)
        if len(s)==0:
        #空字符串取0
            state.append([0])
            return state
        s=str(s).encode("utf-8","ignore").decode('utf8','ignore')
        for i in s:
            if i.encode("utf-8").isalpha():
                state.append([A])
            elif i.isdigit():
                state.append([N])
            elif is_chinese(i):
                state.append([C])
            else:
                state.append([self.get_num(i)])
        return state
    def get_num(self,s):
        return ord(s)
    def url(self):
        for p in self.payload.split("&"):
            p_list=p.split("=")
            p_name=p_list[0]
            if len(p_list)>1:
                p_value=reduce(operator.add,p_list[1:])
                p_id=get_md5(self.data["host"]+self.path+p_name.encode().decode('utf8','ignore')+self.data["method"])
                p_state=self.get_Ostate(p_value)
                p_type="uri"
                yield (p_id,p_state,p_type,p_name)
    def path_p(self):
        p_id=get_md5(self.data["host"]+self.data["method"])
        p_state=self.get_Ostate(self.path)
        p_type="uri_path"
        p_name=""
        return (p_id,p_state,p_type,p_name)
    def post(self):
        post_data=urllib.parse.unquote(urllib.parse.unquote(self.data["data"]))
        content_t=self.data["content_type"]
        def ex_urlencoded(post_data):
            for p in post_data.split("&"):
                p_list = p.split("=")
                p_name = p_list[0]
                if len(p_list) > 1:
                    p_value = reduce(operator.add, p_list[1:])
                    p_id = get_md5(self.data["host"] + self.path + decode(p_name) + self.data["method"])
                    p_state = self.get_Ostate(p_value)
                    p_type = "post"
                    yield (p_id, p_state, p_type, p_name)
        def ex_json(post_data):
            post_data=json.loads(post_data)
            for p_name,p_value in post_data.items():
                p_id = get_md5(self.data["host"] + self.path + decode(p_name) + self.data["method"])
                p_state=self.get_Ostate(str(p_value))
                p_type="post"
                yield (p_id, p_state, p_type, p_name)
        def ex_xml(post_data):
            tree=ElementTree.fromstring(post_data)
            elements=[]
            p_names=[]
            def get_item(tree,parent_tag=""):
                if tree.getchildren():
                    if parent_tag:
                        parent_tag += "/" + tree.tag
                    else:
                        parent_tag = tree.tag
                    for t in tree.getchildren():
                        get_item(t,parent_tag)
                else:
                    elements.append(tree.text)
                    p_names.append(parent_tag+"/"+tree.tag)
            get_item(tree)
            for (p_name,p_value) in zip(p_names,elements):
                p_state=self.get_Ostate(p_value)
                p_type="post"
                p_id = get_md5(self.data["host"] + self.path + decode(p_name) + self.data["method"])
                yield (p_id, p_state, p_type, p_name)
        if "application/x-www-form-urlencoded" in content_t:
            return ex_urlencoded(post_data)
        elif "application/json" in content_t:
            return ex_json(post_data)
        elif "text/xml" in content_t:
            return ex_xml(post_data)
        else:return None
    def http_type(self):
        http_type=self.data["http_type"]
        p_id=get_md5(self.data["host"]+self.path+"http_type"+self.data["method"])
        p_state=self.get_Ostate(http_type)
        p_type="http_type"
        p_name=""
        return (p_id,p_state,p_type,p_name)
    def content_length(self):
        content_length=self.data["content_length"]
        p_id = get_md5(self.data["host"] + self.path + "content_length"+ self.data["method"] )
        p_state = self.get_Ostate(content_length)
        p_type="content_length"
        p_name=""
        return (p_id, p_state,p_type,p_name)
    def cookie(self):
        cookies=urllib.parse.unquote(self.data["cookie"].encode("utf-8").decode('utf8','ignore'))
        for p in cookies.split("; "):
            if p.strip():
                p_list=p.split("=")
                p_name=p_list[0]
                if len(p_list)>1:
                    p_value=reduce(operator.add,p_list[1:])
                    p_id=get_md5(self.data["host"]+self.path+decode(p_name)+self.data["method"])
                    p_state=self.get_Ostate(p_value)
                    p_type="cookie"
                    yield (p_id,p_state,p_type,p_name)
    def uri_p_name(self):
        p_name=""
        for p in self.payload.split("&"):
            p_name+=p.split("=")[0]
        p_state=self.get_Ostate(p_name)
        p_type="uri_pname"
        p_id = get_md5(self.data["host"] + self.path + self.data["method"]+p_type)
        p_name=""
        return (p_id, p_state,p_type,p_name)
    def cookie_p_name(self):
        cookie = urllib.parse.unquote(self.data["cookie"].encode("utf-8").decode('utf8','ignore'))
        p_name=""
        for p in cookie.split("; "):
            if p.strip():
                p_name+=p.split("=")[0]
        p_type = "cookie_pname"
        p_id = get_md5(self.data["host"] + self.path + self.data["method"]+p_type)
        p_state = self.get_Ostate(p_name)
        p_name=""
        return (p_id, p_state,p_type,p_name)
    def post_p_name(self,p_names):
        p_state = self.get_Ostate(p_names)
        p_type = "post_pname"
        p_name = ""
        p_id = get_md5(self.data["host"] + self.path + self.data["method"]+p_type)
        return (p_id, p_state, p_type, p_name)
class Trainer(object):
    def __init__(self,data):
        self.p_id=data["p_id"]
        self.p_state=data["p_states"]
    def get_model(self):
        self.train()
        print('end train')
        self.get_profile()
        return (self.model,self.profile)
    def train(self):
        print('start train')
        Hstate_num=list(range(len(self.p_state)))
        Ostate_num=list(range(len(self.p_state)))
        Ostate = []
        global value,index
        for (index,value) in enumerate(self.p_state):
            Ostate+=value     #观察状态序列
            Hstate_num[index]=len(set(np.array(value).reshape(1,len(value))[0]))
            Ostate_num[index]=len(value)
        self.Ostate=Ostate
        self.Hstate_num=Hstate_num
        self.n=int(round(np.array(Hstate_num).mean()))#隐藏状态数
        model = GaussianHMM(n_components=self.n, n_iter=1000, init_params="mcs",covariance_type="full")
        model.fit(np.array(Ostate),lengths=Ostate_num)
        s=model.transmat_.sum(axis=1).tolist()
        try:
            print('transmat')
            model.transmat_[s.index(0.0)]=np.array([1.0/self.n]*self.n)
        except ValueError:
            pass
        self.model=model
    def get_profile(self):
        print('get profile')
        scores=np.array(range(len(self.p_state)),dtype="float64")
        for (index,value) in enumerate(self.p_state):
            scores[index]=self.model.score(value)
        self.profile=float(scores.min())
        self.scores=scores
    def re_train(self):
        score_mean=self.scores.mean()
        sigma=self.scores.std()
        if self.profile < (score_mean-3*sigma):
            index=self.scores.tolist().index(self.profile)
            self.p_state.pop(index)
            self.train()
            self.get_profile()
            self.re_train()
class Detector(object):
    def __init__(self,model,p):
        self.model=model
        self.profile=p
    def detect(self,data):
        self.score=self.model.score(data["p_state"])
        if self.score<self.p:
            return True
        else :
            return False


def main():
    data={'content_length': 43, 'status': '', 'src_port': '59474',\
     'cookie': 'JSESSIONID%3Da449d6d0-a91d-4db4-a619-ed55239675e9%3B%20socm4ia%3D33SdLeElYV-1ES4bZEzfJ2msWUzGyf8G%257Cguoweibo01.3QGvYoBnZm98bE%252B6w%252B6e1RMN%252BY6x1H4YjY%252FQ5lfKKZU%3B%20connectId%3Ds%253A33SdLeElYV-1ES4bZEzfJ2msWUzGyf8G.8AqrleZu1lQY%252BvV2sakGkiUNdtcyB6WNYf1HfK%252FaPpA%3B%20socm4ts%3D0p4JtcIKKScCOzTN1ZJ_0kCoUVelMBsu%257Cguoweibo01.1zRT7PIXe9CrS2Pn5kBTCQsKpwPydoKf0KaieeHD1I8%3B%20tsConnectId%3Ds%253A0p4JtcIKKScCOzTN1ZJ_0kCoUVelMBsu.7Z7vNkjVarRmFz0czSHUxEoMNzXnE69iYXxJWnKSkds',\
      'uri': '/portal/logins/checklogin', 'http_type': 'Request', 'server': '', 'src_ip': '192.168.126.131', 'host': '10.10.10.1:8888', \
      'referer': 'http://10.10.10.1:8888/portal/logins/login', 'flow_time': 1493966490, 'content_type': 'text/xml', 'date': '', 'dst_ip': '10.10.10.1.180',\
       'dst_port': '8888', 'data': '%3Croot%3E%3Cheader%3E%3Ctype%3Efetch%3C/type%3E%3C/header%3E%3Ccontent%3E%3Cprogram%3Etest%3C/program%3E%3C/content%3E%3C/root%3E', 'method': 'POST', \
       'user_agent': ' Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'}
    global ps
    ps=Extractor(data).parameter
    print(ps)
    for key in ps.keys():
        if ps[key]["p_type"]=="post_pname":
            pass

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

def split_task():
    os.system('mkdir id_group')
    section_size=50
    global p_dict
    id_list=list(p_dict.ksys())
    section=0
    i=0
    while section+section_size<=len(id_list):
        sub_id=id_list[section:section+section_size]
        json.dump(sub_id,open('id_group/id_group_%d.json'%i,'w'))
        section+=section_size
        i+=1
    json.dump(id_list[section:],open('id_group/id_group_%d.json'%i,'w'))





if __name__ =="__main__":
    table='weblog0407'
    min_train_num=5
    os.system('mkdir model_output')
    os.system('mkdir model_profile_output')
    remove_list=[
        'http_type',
        'content_length'
    ]
    sql="select * from table where domain like '%.shafc.edu.cn' ;".replace('table',table)
    trainfile='Hmmtrainset'
    if trainfile not in os.listdir('./'):
        data_list=get_sql_data(sql)
    else:
        data_list=json.load(open(trainfile,'r'))
    data_true=[]
    for data in data_list:
        if data['tag']==1:
            data_true.append(data)
        

    p_dict={}
    for data in data_true:
        p_tmp=Extractor(data).parameter
        for key_p in p_tmp.keys():
            if key_p not in p_dict.keys():
                p_dict[key_p]={}
                p_dict[key_p]['p_states']=[p_tmp[key_p]['p_state']]
                p_dict[key_p]['p_type']=p_tmp[key_p]['p_type']
                p_dict[key_p]['p_name']=p_tmp[key_p]['p_name']
            p_dict[key_p]['p_states'].append(p_tmp[key_p]['p_state'])
    for key in list(p_dict):
        if len(p_dict[key]["p_states"]) <min_train_num or p_dict[key]['p_type'] in remove_list:
            p_dict.pop(key)

    with open('id_done.txt','r') as f_done:
        done=set([i.strip() for i in f_done if i.strip() != ''])

    trained_num=0
    models=[]
    for p_id in p_dict.keys():
        if p_id in done:
            continue
        data={}
        data["p_id"]=p_id
        data["p_states"]=p_dict[p_id]["p_states"]
        model = {}
        model["p_id"] = p_id
        model["p_type"]=p_dict[p_id]["p_type"]
        model["p_name"] = p_dict[p_id]["p_name"]
        try:
            trainer=Trainer(data)
            (m,p)=trainer.get_model()
            model["model"] = pickle.dumps(m)
            model["profile"] = p
            with open('model_output/%s'%p_id,'wb') as f_model:
                pickle.dump(m,f_model)
            with open('id_done.txt','a') as f_done:
                f_done.write(p_id+'\n')
            with open('model_profile_output/%s'%p_id,'wb') as f_m:
                pickle.dump(model,f_m)
            print("|Trained|:%s,num is %s"%(p_id,trained_num))
            trained_num+=1
        except Exception as e:
            print('|EXCEPT|:',p_id,str(e))
            model["model"]=None
            model["profile"]=None
        models.append(model)
    with open('Models_%s.pickle'%table,'wb') as output:
        pickle.dump(models,output)

    
