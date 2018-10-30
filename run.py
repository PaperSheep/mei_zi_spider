import requests
import threading
import random
from lxml import etree
import os
import json
import sys
import re


thread_lock = threading.BoundedSemaphore(value=10)


def get_cover_and_album_url(raw_page_url, headers, cover_url_list, album_url_list):
    raw_index_html = requests.get(raw_page_url, headers=headers)
    # 处理一下源码
    raw_index_html.encoding = 'utf-8'
    index_html = etree.HTML(raw_index_html.text)
    cover_url_list += index_html.xpath('//div[@class="place-padding"]//figure//img/@data-original') # 这里可能没有匹配到
    album_url_list += index_html.xpath('//div[@class="place-padding"]//figure/a/@href') 
    thread_lock.release()  # 解锁


def get_pic_url(album_url, headers, total_pic_list):
    raw_index_html = requests.get(album_url, headers=headers)
    # 处理一下源码
    raw_index_html.encoding = 'utf-8'
    index_html = etree.HTML(raw_index_html.text)
    album_pic_list = []
    raw_end_count = index_html.xpath('//div[@class="prev-next"]//span[@class="prev-next-page"]/text()')[0] # 这里可能没有匹配到
    end_count = int(re.findall(r'/(.*?)页', raw_end_count)[0])
    for page_count in range(end_count):
        target_url = album_url
        if page_count != 0:
            target_url = album_url + '/{}'.format(page_count+1)
        raw_page_html = requests.get(target_url, headers=headers)
        raw_page_html.encoding = 'utf-8'
        page_html = etree.HTML(raw_page_html.text)
        album_pic_list.append({'referer': album_url, 'pic_url': page_html.xpath('//figure//img/@src')})
    total_pic_list.append(album_pic_list)
    thread_lock.release()  # 解锁


# 写入文档
def write(path, text):
    dic = {'content': text}
    with open(path, 'a') as f:
        json.dump(dic, f, ensure_ascii=False)
        # f.write('\n')


# 读取文档
def read(path):
    with open(path, 'r') as f:
        json_data = json.load(f)
        return json_data['content']


def get_cover_and_album_main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
    # //a/text()
    # //a/[@href="xxxxxx"]/text()
    # //li/a//@href
    cover_url_list = []
    album_url_list = []
    raw_page_url = ''
    threads = []
    try:
        for i in range(198):
            if i == 0:
                raw_page_url = 'http://m.mzitu.com/'
            else:
                raw_page_url = 'http://m.mzitu.com/page/{}/'.format(i+1)
            t = threading.Thread(target=get_cover_and_album_url, args=(raw_page_url, headers, cover_url_list, album_url_list))
            threads.append(t)
        # 开始跑线程
        for s in threads:
            thread_lock.acquire() 
            print('丢一页进线程池')
            sys.stdout.flush()
            s.start()
        # 等待所有线程
        for e in threads:
            e.join()
        # 保存封面链接
        write('json/cover_url_list.json', cover_url_list)
        # 保存相册链接
        write('json/album_url_list.json', album_url_list)
    except:
        print('该链接寻找失败', raw_page_url)
        # 保存封面链接
        write('json/cover_url_list.json', cover_url_list)
        # 保存相册链接
        write('json/album_url_list.json', album_url_list)


def get_pic_url_main():
    album_url_list = read('json/album_url_list.json')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
    total_pic_list = []
    threads = []
    try:
        for album_url in album_url_list:
            t = threading.Thread(target=get_pic_url, args=(album_url, headers, total_pic_list))
            threads.append(t)
        # 开始跑线程
        for s in threads:
            thread_lock.acquire()
            # print('丢一页进线程池')
            # sys.stdout.flush() 
            s.start()
        # 等待所有线程
        for e in threads:
            e.join()
        # 保存相册链接
        write('json/total_pic_list.json', total_pic_list)
    except:
        print('该链接寻找失败', total_pic_list[-1])
        # 保存相册链接
        write('json/total_pic_list.json', total_pic_list)



if __name__ == '__main__':
    main()

