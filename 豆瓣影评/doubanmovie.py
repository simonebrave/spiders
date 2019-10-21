'''
使用Selenium，实现登录豆瓣网功能，并拉取《我不是药神》的豆瓣影评。
用队列Queue保存等待爬取的目标url，和等待解析的HTML网页源码
可实现批量爬取，但是需要注意爬取速度，速度太快可能会被封IP，可以考虑使用sleep减缓程序爬取的速度，或者是更换IP
影评提取使用Beautiful Soup，提取网友的网络名，点评时间和点评内容，并保存到本地文件中。
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from bs4 import BeautifulSoup
from queue import Queue

import os
import datetime
import random
import logging

FORMAT = '%(asctime)s info: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

COMMENTS_INFO = 'E:\Python\spider\practice\movie_comments.txt'

COMMENTS_FILE = 'E:\Python\spider\practice\comments1.txt'

browser = webdriver.Chrome()
url = 'https://accounts.douban.com/passport/login?source=movie'
spider_urls = Queue()
analyze_htmls = Queue()

def savepic():
    base_dir = 'E:/Python/spider/practice/'
    filename = '{}{:%Y%m%d%H%M%S}{:03}.png'.format(base_dir, datetime.datetime.now(), random.randint(1,100))
    browser.save_screenshot(filename)

def login(username, password):
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

def get_comments(page=0):
    for i in range(page):
        comments_url = "https://movie.douban.com/subject/26752088/comments?start={}&limit=20&sort=new_score&status=P".format(i*20)
        spider_urls.put(comments_url)

    while not spider_urls.empty():
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




if __name__ == '__main__':

    #登录豆瓣，爬取《我不是药神》影评
    login("username", "password")
    get_comments(2)
    analyze_comments()

