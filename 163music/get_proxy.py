import requests
import os,json
from commen import join_str
#获取代理IP

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

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


# ips = get_proxies()
# for ip in ips:
#     print(ip)

