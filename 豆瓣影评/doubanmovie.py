'''
使用Selenium，实现登录豆瓣网功能，并拉取《我不是药神》的豆瓣影评。
用队列Queue保存等待爬取的目标url，和等待解析的HTML网页源码
可实现批量爬取，但是需要注意爬取速度，速度太快可能会被封IP，可以考虑使用sleep减缓程序爬取的速度，或者是更换IP
影评提取使用Beautiful Soup，提取网友的网络名，点评时间和点评内容，并保存到本地文件中。

更新部分：
	仅提取评论的文本，保存到本地文件。
	从本地文件中读取所有爬取到的评论，生成结巴分词，并用读取停用词的文本，过滤不必要的词汇。
	<提取的评论也可不必存档，更新的部分里面有将评论存档只是为了方便测试>
	注意：需提前下载停用词的文档，以过滤评论中的标点符号和一些不必要的词汇
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from bs4 import BeautifulSoup
from queue import Queue

import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

import os
import datetime
import time
import random
import logging

FORMAT = '%(asctime)s info: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

COMMENTS_INFO = 'movie_comments.txt'

COMMENTS_TEXT = 'movie_new_comments.txt'


url = 'https://accounts.douban.com/passport/login?source=movie'
spider_urls = Queue()
analyze_htmls = Queue()

def savepic(browser):
    base_dir = 'E:/Python/spider/practice/'
    filename = '{}{:%Y%m%d%H%M%S}{:03}.png'.format(base_dir, datetime.datetime.now(), random.randint(1,100))
    browser.save_screenshot(filename)

def login(username, password, browser):
    try:
        browser.get(url=url) #打开登录界面

        ele = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.CLASS_NAME, 'account-body-tabs')))
        logging.info('type: {}'.format(type(ele)))
        logging.info('ele: {}'.format(ele))

        #查找密码登录标签
        login_table = browser.find_element_by_class_name('account-tab-account')
        #鼠标移动至密码登录标签
        ActionChains(browser).move_to_element(login_table)
        #点击密码登录标签
        ActionChains(browser).click(login_table).perform()

        login_ele = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, 'username')))
        print(login_ele)

        username_ele = browser.find_element_by_id('username')
        password_ele = browser.find_element_by_id('password')
        logging.info('username ele: {}'.format(username_ele))
        logging.info('password ele: {}'.format(password_ele))

        username_ele.send_keys(username)
        password_ele.send_keys(password)
        password_ele.send_keys(Keys.ENTER)
        WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.CLASS_NAME, 'nav-user-account')))
        print(browser.get_cookies())
    except Exception as e:
        print("exception:", e)
        browser.close()

def get_comments(browser, page=0):
    for i in range(page):
        comments_url = "https://movie.douban.com/subject/26752088/comments?start={}&limit=20&sort=new_score&status=P".format(i*20)
        spider_urls.put(comments_url)

    while not spider_urls.empty():
        time.sleep(3)
        url = spider_urls.get()
        try:
            browser.get(url=url)
            WebDriverWait(browser, 30).until(ec.presence_of_element_located((By.ID, 'comments')))
            analyze_htmls.put(browser.page_source)
        except Exception as e:
            print(e)

def analyze_comments():
    if os.path.exists(COMMENTS_INFO):
        os.remove(COMMENTS_INFO)
    while not analyze_htmls.empty():
        html = analyze_htmls.get()
        soup = BeautifulSoup(html, 'lxml')
        comment_tags = soup.find_all(class_='comment-item')
        with open(COMMENTS_INFO, 'a+', encoding='utf-8') as f:
            for tag in comment_tags:
                comment = tag.find(class_='short').string.strip()
                user = tag.find(class_='comment').find(class_='comment-info').a.string
                time = tag.find(class_='comment-time').string.strip()
                line = '{} {} {}\n'.format(user, time, comment)
                f.write(line)


def analyze_comments2():
    if os.path.exists(COMMENTS_TEXT):
        os.remove(COMMENTS_TEXT)
    while not analyze_htmls.empty():
        html = analyze_htmls.get()
        soup = BeautifulSoup(html, 'lxml')
        comment_tags = soup.find_all(class_='comment-item')
        with open(COMMENTS_TEXT, 'a+', encoding='utf-8') as f:
            for tag in comment_tags:
                comment = tag.find(class_='short').string.strip()
                line = '{}\n'.format(comment)
                f.write(line)


def create_word_pic(file):
    stop_words = set()
    words = dict()

    #读取停用词
    with open('E:\Python\spider\practice\chineseStopWords.txt', encoding='gbk') as f:
        for line in f.readlines():
            stop_words.add(line.rstrip('\r\n'))
    print(stop_words)

    if not os.path.exists(file):
        print('不存在评论文本')
    else:
        with open(file, encoding='utf8') as f:
            for line in f.readlines():      #读取评论
                for word in jieba.cut(line):    #精确模式，结巴分词切割
                    if word not in stop_words:      #清洗数据，过滤掉停用词
                        words[word] = words.get(word, 0) + 1

    words_len = len(words)

    #计算词频
    words_freq = {k:v/words_len for k,v in words.items()}
    sorted(words_freq.items(), key=lambda x:x[1], reverse=False)
    print(words_freq)

    mask_pic = np.array(Image.open('pkq.png')) #指定词云的背景框
    word_cloud = WordCloud(font_path='simhei.ttf', background_color='white', max_font_size=120, mask=mask_pic)

    plt.figure(2)
    word_cloud.fit_words(words_freq)
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.show()


if __name__ == '__main__':

    #登录豆瓣，爬取《我不是药神》影评
    # browser = webdriver.Chrome()
    # login(username, password, browser)
    # get_comments(browser, 10)
    # analyze_comments2()
    # browser.close()

    #生成词云
    create_word_pic(COMMENTS_INFO)

	

