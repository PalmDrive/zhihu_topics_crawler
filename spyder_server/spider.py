# -*- coding: utf-8 -*-
import json
import time

import os.path
import re
import requests
from graph import Topic, save, is_done, save_new_topic

try:
    from PIL import Image
except:
    pass
from bs4 import BeautifulSoup


class Spider(object):
    Load_More_Sub_Topics_URL_Pattern = "https://www.zhihu.com/topic/%s/organize/entire?child=%s&parent=%s"
    Load_Sub_Topics_URL_Pattern = 'https://www.zhihu.com/topic/%s/organize/entire'
    Top_Topic_ID = '19776749'

    def __init__(self):
        self.logn_url = 'http://www.zhihu.com/#signin'
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1581.2 Safari/537.36',
            'Host': 'www.zhihu.com',
            'Origin': 'http://www.zhihu.com',
            'Connection': 'keep-alive',
            'Referer': 'http://www.zhihu.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',

        }
        self._xsrf = ""
        self.pending_topics = []

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

    def is_login(self):
        # 通过查看用户个人信息来判断是否已经登录
        url = "https://www.zhihu.com/settings/profile"
        login_code = self.session.get(url, allow_redirects=False).status_code
        if int(x=login_code) == 200:
            return True
        else:
            return False

    def start(self):
        if not self.is_login():
            print '登录中:'
            self.login('', '')
        else:
            print '已登录..'

        print '开始获取话题列表...'
        self.bfs_fetch_all_topics()
        topics = self.get_topics()
        print '获取到话题个数:%s' % len(topics)
        print ', '.join(topics)

    def get_topics(self):
        url = 'https://www.zhihu.com/topics'
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
        topics = [x.find('a').get_text() for x in
                  soup.find_all('li', class_='zm-topic-cat-item')]
        return topics

    def bfs_fetch_all_topics(self):
        pt = Topic.nodes.filter(done=False)
        if len(pt) == 0:
            self.pending_topics.append(self.Top_Topic_ID)
        else:
            for p in pt:
                self.pending_topics.append(p.topic_id)
        while len(self.pending_topics):
            current_children = []
            target = self.pending_topics[0]
            self.pending_topics.pop(0)
            try:
                if is_done(target):
                    continue

                (current_topic, child_topics, sub_topic_url) = self.fetch_child_topics(
                        self.Load_Sub_Topics_URL_Pattern % target)
                current_children = current_children + child_topics
                print 'current child topic', len(current_children)
                while sub_topic_url:
                    (current_topic, child_topics, sub_topic_url) = self.fetch_child_topics(sub_topic_url)
                    current_children = current_children + child_topics
                    print 'current child topic', len(current_children)

                save(current_topic, current_children)
                for p in current_children:
                    self.pending_topics.append(p.topic_id)
                    save_new_topic(p)
                print len(self.pending_topics)
            except Exception as e:
                print e

    def fetch_child_topics(self, url):
        response = self.session.post(
                url, headers=self.headers, data={'_xsrf': self.get_xsrf()})
        content = response.content.decode('utf-8')
        data = json.loads(content)
        if len(data['msg']) == 0:
            return

        data = data['msg']
        current_topic = None
        sub_topic_url = None
        child_topics = []
        # current_topic
        if data[0][0] == u'topic':
            current_topic = Topic(name=data[0][1], topic_id=data[0][2], done=False)

        if len(data) > 1:
            data = data[1]

        for i in range(0, len(data)):
            if data[i][0][0] == u'topic':
                child_topic = Topic(name=data[i][0][1], topic_id=data[i][0][2], done=False)
                child_topics.append(child_topic)

            elif data[i][0][0] == u'load':
                sub_topic_url = self.Load_More_Sub_Topics_URL_Pattern % (
                    data[i][0][3], data[i][0][2], data[i][0][3])
        return current_topic, child_topics, sub_topic_url

    def login(self, secret, account):
        self.content = self.session.get(
                self.logn_url, headers=self.headers).content
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
            print result
            print "登录结果:", result["msg"].encode("utf8")


s = Spider()

s.start()
