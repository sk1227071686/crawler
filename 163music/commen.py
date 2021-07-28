
import redis
import json
import base64
import os
import requests

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj)
        return json.JSONEncoder.default(self, obj)


def connect_redis(host='localhost', port=6379, out_string=False):
        #pool = redis.ConnectionPool(host=host, port=port,decode_responses=out_string)
        r = redis.Redis(host=host, port=port,decode_responses=out_string)
        return r

# r = connect_redis()
# r.hset('ss',mapping={'s1':b's1'})
# print(r.hget('ss','s1'))
# r.hdel('ss','s1')
# print(r.hget('ss','s1'))

def join_str(str1,str2,*args,sep=''):
        tmp_str = sep.join((str1,str2))
        for string in args:
            tmp_str = sep.join((tmp_str,string))
        return tmp_str

def save_as_file(path,filename,content=''):
    if os.path.exists(path):
        pass
    else:
        os.mkdir(path)
    try:
        if type(content) is str :
            with open(os.path.join(path,filename),'w',encoding='utf-8')as f:
                f.write(content)
        elif type(content) is bytes:
            with open(os.path.join(path,filename),'wb')as f:
                f.write(content)
        else:
            raise TypeError
    except Exception as e:
        print(e)


#获取代理IP
def get_proxies():
    next_page = 1
    last_page = 2
    ip_list = []
    while next_page <= last_page:
        response = requests.get(f'https://ip.jiangxianli.com/api/proxy_ips?page={next_page}')
        next_page += 1
        info = json.loads(response.text)
        #print(type(info),info)
        ip_data = info['data']['data']
        last_page = info['data']['last_page']

        #print(ip_data)
        for dic in ip_data:
            ip_list.append(join_str(dic['protocol'],'://',dic['ip'],':',dic['port']))
        # for dic in ip_list:
        #     #print(dic['ip'],':',dic['port'])
        #     ip_dic[dic['ip']]=dic['port']
    # with open(os.path.join(BASE_DIR, 'proxies.txt'), 'a')as fp:
    #     json.dump(ip_dic,fp)
    return ip_list

