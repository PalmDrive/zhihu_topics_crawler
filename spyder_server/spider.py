# -*- coding: utf-8 -*-
import requests
import re
import time
import os.path
import json
import urllib
import urllib2
import cookielib
from models import *
import random
import time

try:
    from PIL import Image
except:
    pass
from bs4 import BeautifulSoup


class Topic(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Content(object):
    def __init__(self, id, imgsrc, name, content):
        self.id = id
        self.img = imgsrc
        self.name = name
        self.content = content

def loop_until_return(n, f, *args, **kwargs):
    for i in range(n):
        print 'trying NO.%s time of %s(%s)' % (i, f, args)
        try:
            return f(*args, **kwargs)
        except Exception:
            pass
    else:
        print '----'*20
        print f,args,kwargs
        print 'tried '+str(n)+'times and failed'
        print '----'*20



def getTopics():
    zhihuTopics = []
    url = 'https://www.zhihu.com/topics'
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url)
    response = opener.open(request)
    pattern = re.compile('<li.*?data-id="(.*?)"><a.*?>(.*?)</a></li>', re.S)
    results = re.findall(pattern, response.read().decode('utf-8'))
    for n1 in results:
        print n1[0], n1[1]
        topic = Topic(n1[0], n1[1])
        zhihuTopics.append(topic)
    return zhihuTopics


def getSubTopic(topic):
    url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
    isGet = True
    offset = -20
    contents = []

    time.sleep(random.random())
    while isGet:
        offset = offset + 20
        values = {'method': 'next',
                  'params': '{"topic_id":' + topic.id + ',"offset":' + str(
                      offset) + ',"hash_id":""}'}
        try:
            data = urllib.urlencode(values)
            request = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(request)
            json_str = json.loads(response.read().decode('utf-8'))
            # 将获取到的数组转换成字符串
            topicMsg = '.'.join(json_str['msg'])

            pattern = re.compile(
                '"/topic/(.*?)">\n<img src="(.*?)" alt="(.*?)">\n<strong>(.*?)</strong>.*?<p>(.*?)</p>',
                re.S)
            results = re.findall(pattern, topicMsg)

            if len(results) == 0:
                isGet = False
            for n in results:
                content = Content(n[0], n[1], n[2], n[4])
                contents.append(content)
                print n[0], '->' + n[1] + '->' + n[2]  + '->' + n[4]

        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"错误原因", e

    # file = open(topic.name + '.txt', 'w')
    # wiriteLog(contents, file)
    return contents


def wiriteLog(contentes, file):
    for content in contentes:
        file.writelines(
            (
                '\n' +content+ content.img + '->' + content.name + '->' + content.content).encode(
                "UTF-8"))

def get_the_topics_with_img():
    print '开始拉取数据...\n'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.zhihu.com/topics',
        'Cookie': '__utma=51854390.517069884.1416212035.1416212035.1416212035.1; q_c1=c02bf44d00d240798bfabcfc95baeb56|1455778173000|1416205243000; _za=b1c8ae35-f986-46a2-b24a-cb9359dc6b2a; aliyungf_tc=AQAAAJ1m71jL1woArKqF22VFnL/wRy6C; _xsrf=9d494558f9271340ab24598d85b2a3c8; cap_id="MDNiMjcwM2U0MTRhNDVmYjgxZWVhOWI0NTA2OGU5OTg=|1455864276|2a4ce8247ebd3c0df5393bb5661713ad9eec01dd"; n_c=1; _alicdn_sec=56c6ba4d556557d27a0f8c876f563d12a285f33a'
    }

    alen = 0
    topics = getTopics()


    for topic in topics:
        parent_id = topic.id
        contents = getSubTopic(topic)
        for i in contents:
            topic = ZhihuTopic()
            topic.set("topic_id",i.id)
            topic.set("img", i.img)
            topic.set("name", i.name)
            topic.set("description", i.content)
            topic.set("parent_topic_id", parent_id)
            loop_until_return(10,lambda :topic.save())

        alen += len(contents)

    print '知乎总话题数为：' + str(alen)
    print '拉取数据结束'


class Spider(object):
    def __init__(self):
        self.logn_url = 'http://www.zhihu.com/#signin'
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
        }
        self._xsrf = ""

    # 获取验证码
    def get_captcha(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = self.session.get(captcha_url, headers=self.headers)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(
                u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = raw_input(u"输入验证码\n>")
        return captcha

    def get_xsrf(self):
        self._xsrf = self.soup.find('input', attrs={'name': "_xsrf"})['value']
        return self._xsrf

    def isLogin(self):
        # 通过查看用户个人信息来判断是否已经登录
        url = "https://www.zhihu.com/settings/profile"
        login_code = self.session.get(url, allow_redirects=False).status_code
        if int(x=login_code) == 200:
            return True
        else:
            return False

    def start(self):
        r = self.session.get("http://localhost:63360/register", )
        res = json.loads(r.content)
        self.id = res["id"]
        print 'spider id:%s ' % self.id
        if not self.isLogin():
            print '登录中:'
            self.login('asdfgh', '935685518@qq.com')
        else:
            print '已登录..'

        print '开始获取话题列表...'
        topics = self.get_topics()
        print '获取到话题个数:%s' % len(topics)


    def get_topics(self):
        zhihuTopics = []
        url = 'https://www.zhihu.com/topics'
        response = self.session.get(url)
        pattern = re.compile('<li.*?data-id="(.*?)"><a.*?>(.*?)</a></li>', re.S)
        results = re.findall(pattern, response.content.decode('utf-8'))
        for n1 in results:
            print n1[0], n1[1]
            topic = Topic(n1[0], n1[1])
            zhihuTopics.append(topic)
        return zhihuTopics

    def login(self, secret, account):
        self.content = self.session.get(self.logn_url,
                                        headers=self.headers).content
        self.soup = BeautifulSoup(self.content, 'html.parser')
        self.get_xsrf()

        # 通过输入的用户名判断是否是手机号
        if re.match(r"^1\d{10}$", account):
            print("手机号登录 \n")
            post_url = 'https://www.zhihu.com/login/phone_num'
            postdata = {
                '_xsrf': self._xsrf,
                'password': secret,
                'remember_me': 'true',
                'phone_num': account,
            }
        else:
            print("邮箱登录 \n")
            post_url = 'https://www.zhihu.com/login/email'
            postdata = {
                '_xsrf': self._xsrf,
                'password': secret,
                'remember_me': 'true',
                'email': account,
            }
        try:
            # 不需要验证码直接登录成功
            login_page = self.session.post(post_url, data=postdata,
                                           headers=self.headers)
        except:
            # 需要输入验证码后才能登录成功
            print '需要输入验证码...'
            postdata["captcha"] = self.get_captcha()
            login_page = self.session.post(post_url, data=postdata,
                                           headers=self.headers)
        finally:
            login_code = login_page.text
            result = json.loads(login_code)
            print "登录结果:", result["msg"].encode("utf8")


    def getallview(self):
        nums = 27  # 这个是我关注的人数
        followees_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
            'Referer': 'https://www.zhihu.com/people/GitSmile/followees',
            'Origin': 'https://www.zhihu.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'CG - Sid': '57226ad5 - 793b - 4a9d - 9791 - 2a9a17e682ef',
            'Accept': '* / *'

        }
        count = 0
        for index in range(0, nums):
            fo_url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'
            m_data = {
                'method': 'next',
                'params': '{"offset":' + str(
                    index) + ',"order_by":"created","hash_id":"de2cb64bc1afe59cf8a6e456ee5eaebc"}',
                '_xsrf': str(self.get_xsrf())
            }
            result = self.session.post(fo_url, data=m_data,
                                       headers=followees_headers)
            dic = json.loads(result.content.decode('utf-8'))
            li = dic['msg'][0]
            mysoup = BeautifulSoup(li, 'html.parser')
            for result in mysoup.findAll('a', attrs={
                'class': 'zm-item-link-avatar'}):
                print(index + 1)
                print(result.get('title'))
                href = str(result.get('href'))
                print(
                    mysoup.find('a', attrs={'href': href + '/followers'}).text)
                print(mysoup.find('a', attrs={'href': href + '/asks'}).text)
                print(mysoup.find('a', attrs={'href': href + '/answers'}).text)
                print(mysoup.find('a', attrs={'href': href,
                                              'class': 'zg-link-gray-normal'}).text + '\n')
                count += 1
        print('一共关注了 %d人' % count)


s = Spider()

# s.start()
