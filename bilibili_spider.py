# coding= utf-8
from bs4 import BeautifulSoup
from io import StringIO
import gzip
import zlib
import re
import bs4
import time
import requests
import sys
import getopt
import json
from lxml import etree
# from support import *
import __future__
# from bilibili_api import GetPopularVideo
import os
# -----------
import argparse
from you_get import common as yg
import shutil

# reload(sys)
# sys.setdefaultencoding("utf-8")


class BILI(object):
    def __init__(self, aid, parser='lxml'):
        self.filename = str(aid)
        self.video_url = None
        self.xml = True
        self.parser = parser
        self.aid = aid
        self.cid = None
        self.videolength = None
        self.finished = False
        self.error = False
        ensure_dir('dataset/' + self.filename)
        # self.get_cid(self.aid)
        try:
            self.set_url(self.aid)
            self.get_videoInfo(self.aid)
            if self.videolength >= 300:
                shutil.rmtree('dataset/' + self.filename)
                print('Delete', self.filename)
                return
            yg.any_download(self.video_url, output_dir = './dataset/' + str(self.filename), caption = False)
            self.get_danmu(self.cid)
            self.get_comment(self.aid)
        except (Exception) as e:
            print('something serious happened  ->',)
            print(e)
            self.error = True
        if self.error == True:
            self.finished = False
            shutil.rmtree('dataset/' + self.filename)
            print('Delete', self.filename)
        else:
            self.finished = True



    def gzip_url(self, url):
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip',
            'Referer': 'http://www.bilibili.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        request = requests.get(url, headers = header)
        return request.content

    def set_url(self, aid):

        url = r"http://www.bilibili.com/video/av" + str(aid)
        self.video_url = url
        html = self.gzip_url(url)
        with open('./dataset/' + self.filename + '/' + self.filename + '.html', 'wb') as f:
            f.write(html)
        print('video gzip decompress complete...')
    # try:
        soup = BeautifulSoup(html,self.parser)
        # print('soup')
        da1 = soup.find('div', id="bofqi")
        jsstring = da1.script.string
        # print('jsttring')
        p = re.compile(r'cid=\d+&')
        self.cid = p.findall(jsstring)[0][4:-1]
        print(self.cid)
        print('Cid Achievement Complete...')
        # self.get_danmu(cid)

    # # except (Exception) as e:
    #     print('something serious happened  ->',)
    #     print(e)
    #     self.error = True
            # exit()

    def get_danmu(self, cid):

        danmu_url = "http://comment.bilibili.com/" + cid + ".xml"
        data = self.gzip_url(danmu_url)
        print("Danmu deflate decompress complete...")
        if self.xml:
            fd = open('./dataset/' + self.filename + '/' + self.filename + ".xml", 'wb')
            fd.write(data)
            fd.close()
            print(self.filename + ".xml Complete")

        soup = BeautifulSoup(data, self.parser)
        danmus = soup.find_all('d')
        fw = open('./dataset/' + self.filename + '/' + self.filename + '.dan', 'w')
        print("Writing Danmu...")
        for danmu in danmus:
            content = str(danmu.string)

            attr = danmu['p'].split(',')
            t1 = str(attr[0])  # 视频中的时间
            t2 = attr[4]  # 发布时间
            timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(t2)))

            fw.write(content + '\t' + t1 + '\t' + timestr + '\n')

        fw.close()
        print("Wriring Complete%s.dan" % self.filename)

    def get_videoInfo(self, aid):
        try:
            video = {}
            video['AID'] = str(self.aid)
            html = open('./dataset/' + str(aid) + '/' + str(self.aid) + '.html','r').read()
            soup = BeautifulSoup(html, 'lxml')
            head = soup.head
            video['title'] = head.find('title').string
            video['keywords'] = str((head.find('meta', attrs = {'name':'keywords'}))['content'])
            video['description'] = str((head.find('meta', attrs = {'name':'description'}))['content'])
            video['author'] = str((head.find('meta', attrs = {'name':'author'}))['content'])
            # print((head.find('meta', attrs = {'name':'author'}))['content'])

            url = "http://api.bilibili.com/archive_stat/stat?aid=" + aid
            s = (requests.get(url)).json()

            video['view'] = str(s['data']['view'])
            video['danmaku'] = str(s['data']['danmaku'])
            video['reply'] = s['data']['reply']
            video['favorite'] = s['data']['favorite']
            video['coin'] = s['data']['coin']
            video['share'] = s['data']['share']
            video['now_rank'] = s['data']['now_rank']
            video['his_rank'] = s['data']['his_rank']
            video['code'] = s['code']
            video['message'] = s['message']


            info_url = "http://interface.bilibili.com/player?id=cid:" + str(self.cid) + "&aid=" + str(self.aid)
            tmp = requests.get(info_url).content
            with open('./dataset/' + self.filename + '/' + self.filename + '.inf', 'wb') as f:
                f.write(tmp)
            soup = BeautifulSoup(tmp, 'lxml')
            self.videolength = tim2sec(soup.duration.string)
            video['length'] = self.videolength
            video['type'] = soup.typeid.string
        except (Exception) as e:
            print('video serious happened  ->',)
            print(e)
        with open('./dataset/' + self.filename + '/' + self.filename + '.vid', 'w') as f:
            json.dump(video, f, ensure_ascii=False,indent=2)
        print('Video Info Complete')
        return video

    def get_comment(self, aid, order = 1):
        #     """
        # 输入：
        #     aid：AV号
        #     order：排序方式 默认按发布时间倒序 可选：1 按热门排序 2 按点赞数排序
        # 返回：
        #     评论列表"""
        page = 1
        # print(aid)
        comment = {}
        while True:
            url = "http://api.bilibili.com/x/reply?type=1&oid=%s&pn=%s&nohot=1&sort=%s"%(str(aid),str(page),str(order))
            # print(url)
            tmp = (requests.get(url)).json()
            # print(tmp)
            # tmp['data']['replies']
            if len(comment) == 0:
                comment = tmp
            # print(tmp['data']['replies'])
            # print(len(tmp['data']['replies']))
            if len(tmp['data']['replies']) == 0:
                break
            comment['data']['replies'].extend(tmp['data']['replies'])
            page += 1

        with open('./dataset/' + self.filename + '/' + self.filename  + '.cmt', 'w') as f:
            json.dump(comment, f, ensure_ascii=False,indent=2)
        return comment

def ensure_dir(f):
    # print(f)
    if not os.path.exists(f):
        os.makedirs(f)
def tim2sec(tim):
    l = re.split(':', tim)
    tmp = 0
    for i in l:
        tmp += tmp*60 + int(i)
    return tmp
#
# if __name__ == '__main__':
    # b = BILI('8819938')
    # print tim2sec('3:25')
    # http://interface.bilibili.com/player?id=cid:14549995&aid=8819938
    # get_danmu(8819938)
    # info_url = "http://interface.bilibili.com/player?id=cid:" + str(14549995) + "&aid=" + str(8819938)
    # # l = requests.get(info_url)
    # video_info = requests.get(info_url)
    # video_selector = etree.HTML(video_info.text)
    # duration_log = video_selector.xpath('//duration/text()')
    # print duration_log
    # soup = BeautifulSoup(l, 'lxml')
    # head = soup.duration
    # print l.content
    # comments = all_comment_json('8819938')
    # data = profile('8819938')
    # with open('8819938.json', 'w') as f:
    #     json.dump(data, f, ensure_ascii=False)
    # with open('8819938.json', 'r') as f:
    #     data = json.load(f)
    #     print(data['description'])
    #     print(data)
