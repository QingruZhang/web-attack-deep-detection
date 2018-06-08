from HmmModel import *

def get_raw_flow():
    pass

def all_large_0(tmp,ceil=0):
    if None in tmp:
        return False
    for num in tmp:
        if num<ceil:
            return False
    return True

if __name__=='__main__':
    table='weblog0407'
    remove_list=[
        'http_type',
        'content_length'
    ]

    test_file='HmmTestSet'
    with open(test_file,'r') as f:
        data_list=json.load(f)
    with open('KeyToGroup.json','r') as m:
        pid_group=json.load(m)
    with open('id_done.txt','r') as f_done:
        done=set([i.strip() for i in f_done if i.strip() != ''])

    det_dict=[]
    lack_dict=[]
    low_dict=[]
    low_exp_dict=[]
    true_data=[]
    false_data=[]
    for data in data_list:
        p_tmp=Extractor(data).parameter
        data['result']=[]
        for key_p in p_tmp:
            if p_tmp[key_p]['p_type'] in remove_list:
                continue
            p_dec={}
            p_dec['p_id']=key_p
            p_dec['ID']=data['ID']
            p_dec['uri']=data['uri']
            p_dec['p_type']=p_tmp[key_p]['p_type']
            if key_p in done:
                with open('model_profile_output/%s'%key_p,'rb') as f_pickle:
                    model_dict=pickle.load(f_pickle)
                model=pickle.loads(model_dict['model'])
                profile=model_dict['profile']
                score = model.score(np.array(p_tmp[key_p]["p_state"]))
                p_dec['score']=score
                p_dec['profile']=profile
                p_dec['result']=score-profile
                det_dict.append(p_dec)
                if score<profile and profile-score<50:
                    low_dict.append(p_dec)
                    print('low:',score,r'/',profile,p_dec['uri'])
                else:
                    low_exp_dict.append(p_dec)

            else:
                p_dec['result']=None
                lack_dict.append(p_dec)
        data['result'].append(p_dec['result'])
        if data['tag']:
            true_data.append(data)
        elif not data['tag']:
            false_data.append(data)


    TP,FN,FP,TN=0,0,0,0
    for data in true_data:
        if all_large_0(data['result']):
            TP+=1
        else:
            FP+=1
    for data in false_data:
        if all_large_0(data['result']):
            FN+=1
        else:
            TN+=1
    print('Test Result:')
    print(TP,'|',FN,'\n',FP,'|',TN)

