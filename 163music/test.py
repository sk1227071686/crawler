# a ='dads '
# print(type(a) is str)
# b = b'dadasdasfa'
# print(type(b) is bytes)
# c = '减肥的怕警方怕是'.encode('utf-8')
# print(type(c) is str)

# python 3.6+
import requests

url = "http://www.baidu.com/"
ip, port = "49.72.41.120", "8118	"
proxies = {"http": f"http://{ip}:{port}"}
#空白位置为测试代理ip和代理ip使用端口

#响应头
res = requests.get(url, proxies=proxies, timeout=3)
#发起请求
print(res.status_code) #返回响应码
