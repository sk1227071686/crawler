import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.proxy import Proxy,ProxyType
from selenium.webdriver.chrome.options import Options
import os
import json
import configparser
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
conf = configparser.ConfigParser()
from commen import *
from random import randint

def crawl_song_by_songList(url_list,proxy_list):
    #网易云音乐热歌榜
    #当前使用的代理(随机选择）
    proxies_num = len(proxy_list)
    current_proxy = proxy_list[randint(0,proxies_num)]

#-------------为selenium添加代理----------------
    selenium_proxy = Proxy(
        {
            'proxyType':ProxyType.MANUAL,
            'httpProxy':current_proxy,
        }
    )
    desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
    selenium_proxy.add_to_capabilities(desired_capabilities)
#-----------------end----------------

    red  = connect_redis()   #爬取到的数据保存到redis,
    song_download_headers = {
        'Accept-Encoding': 'identity;q=1, *;q=0',
        'Range': 'bytes=0-',
        'Referer': '',    #referer必须重写
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    }

    pic_download_headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'p4.music.126.net',
        'Pragma': 'no-cache',
        'Referer': '',  #必须被重写
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    }
    SONG_URL = 'http://music.163.com/song/media/outer/url'

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options,desired_capabilities=desired_capabilities)
    driver.get(f'{url_list}')
    wait = WebDriverWait(driver,10)
    driver.switch_to.frame('contentFrame')
    input = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'j-flag')))
    try:
        #歌曲流链接
        link = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td[2]/div/div/a').get_attribute('href')
        #print(link)
        start_index=link.find('?')
        song_id = link[start_index:]
        #歌手名
        singer = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td[4]/div').get_attribute('title')
        print(singer)
        #歌手链接
        singer_link = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td[4]/div/span/a').get_attribute('href')
        #图片链接
        pic_link = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td[2]/div/div/a/img').get_attribute('src')
        #歌名
        song_name = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td[2]/div/div/div/span/a/b').get_attribute('title')
        #时长
        duration = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td[3]/span').text
        #歌词链接
        lyric_link = ''.join((''.join(('http://music.163.com/api/song/lyric',song_id)),'&lv=1&kv=1&tv=-1'))
        #所属专辑需要到歌曲详情页
        driver.get(''.join(('https://music.163.com/#/song',song_id)))
        driver.switch_to.frame('contentFrame')
        wait_album = wait.until(EC.presence_of_element_located((By.ID,'g_nav')))
        album = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[2]/a')
          #专辑名和链接
        album_name = album.text
        album_link = album.get_attribute('href')
        # print(album_name,album_link)

        #print(pic_link)

        #音频流
        song_url = ''.join((SONG_URL,song_id))
        driver.get(song_url)
        new_song_url = driver.current_url   #下载链接重定向的URL
        song_download_headers['Referer']=new_song_url
        response = requests.get(new_song_url,headers=song_download_headers,stream=True)
        song_stream=response.raw.read()

        # with open('a.mp3','wb')as f:
        #     f.write(a['file'])

        #图片流
        pic_download_headers['Referer']=pic_link
        response=requests.get(pic_link,headers=pic_download_headers,stream=True)
        #print(response.url)
        pic_stream = response.raw.read()
        #print(pic_stream)
        # with open('a.jpeg','wb')as f:
        #     f.write(pic_stream)


        #歌词流
        response = requests.get(lyric_link)
        lyric = response.text

        #保存为json文件
        #保存文件名(歌曲名_歌手_专辑)+后缀
        file_audio = join_str(song_name,singer,album_name,'.mp3',sep='-')
        file_lyric = join_str(song_name,singer,album_name,'.txt',sep='-')
        file_pic = join_str(song_name,singer,album_name,'.jpeg',sep='-')

        conf.read(os.path.join(BASE_DIR,'param.ini'))

    #---------------save audio file------------------
        song_path = conf.get('music_resources','audio')
        #print(song_path)
        save_as_file(song_path,file_audio,song_stream)
    #-----------------end save-------------------

    #--------------save picture file------------------
        picture_path = conf.get('music_resources','picture')
        #print(picture_path)
        save_as_file(picture_path,file_pic,pic_stream)
    #-----------------end save--------------------

    #---------------save lyric file-------------------
        lyric_path = conf.get('music_resources','lyric')
        #print(lyric_path)
        save_as_file(lyric_path,file_lyric,lyric)
    #-----------------end save--------------------




    except NoSuchElementException as e:
        print('>>>>>本歌单全部歌曲已经下载完成>>>>>')
    finally:
        #关闭浏览器和redis连接
        driver.close()
        red.close()

proxies_list = get_proxies()
crawl_song_by_songList('https://music.163.com/#/discover/toplist?id=3778678',proxies_list)
# with open('wan'ch','wb')as f:
#     f.write(response.raw.read())



