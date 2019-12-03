from urllib import request
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from bs4 import  BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import time
import random

import logging

FORMAT = '%(asctime)s info: %(message)s'
logging.basicConfig(level=logging.INFO)


def get_html(browser, url):
    time.sleep(random.randint(5, 12))
    browser.get(url=url)
    time.sleep(random.randint(3, 7))

    return BeautifulSoup(browser.page_source, 'lxml')


#获取省份列表
def get_province_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    logging.info('请求目的地列表...')
    req = request.Request(url=url, headers=headers)
    response = request.urlopen(req)

    logging.info('解析目的地列表的HTML DOM...')
    soup = BeautifulSoup(response.read(), 'lxml')
    provinces = soup.find(name='div', attrs={'class': 'hot-list clearfix'}).find_all(name='dt')

    provinces_url_list = []
    for province in provinces:
        tmp = province.find_all(name='a')
        for tag in tmp:
            provinces_url_list.append(tag.attrs['href'])

    provinces_url_list = ['https://www.mafengwo.cn/'+provinces_url_list[i] for i in range(0, len(provinces_url_list))]
    logging.info('返回省份url列表...')
    return provinces_url_list


#获取城市列表
def get_city_list(province_url_list):
    logging.info('获取城市名称和ID...')
    city_id_list = []
    city_name_list = []

    for url in province_url_list:
        browser = webdriver.Chrome()
        browser.maximize_window()
        des_url = url.replace('travel-scenic-spot/mafengwo', 'mdd/citylist')
        browser.get(url=des_url)

        while True:
            sleep_time = random.randint(3,8)
            try:
                time.sleep(sleep_time)
                soup = BeautifulSoup(browser.page_source, 'lxml')
                tmp = soup.find_all(name='a', attrs={'data-type': '目的地'})
                city_id_list = city_id_list + [tag.attrs['data-id'] for tag in tmp]
                city_name_list = city_name_list + [tag.find('div').get_text().strip().replace('\n', '') for tag in tmp]


                browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1.5)
                next = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pg-next _j_pageitem')))
                action = ActionChains(browser)
                action.move_to_element(next)
                action.click(next).perform()

            except:
                logging.info('当前省份结束...')
                break
        browser.close()
    logging.info('返回城市名称列表，城市ID列表...')
    return city_name_list, city_id_list


#获取基础信息，包括：城市名，标签总数，景点标签数，餐饮标签数，娱乐和购物标签数，游记总数
def get_city_base_info(cityname, cityid, browser):
    logging.info('获取城市基础信息...')
    url = 'http://www.mafengwo.cn/xc/{}/'.format(cityid)
    print(url)

    soup = get_html(browser, url)

    tag_all_count = 0
    tag_jd_count = 0
    tag_cy_count = 0
    tag_gw_yl_count = 0

    try:
        tags_list = soup.find(name='div', attrs={'class': 'm-box m-tags'}).find(name='div', attrs={'class': 'bd'}).find_all('a')
        tag_href = [node.attrs['href'][1:3] for node in tags_list]
        tag_count_list = soup.find(name='div', attrs={'class': 'm-box m-tags'}).find(name='div', attrs={'class': 'bd'}).find_all('em')
        tag_count = [int(count.get_text().strip()) for count in tag_count_list]

        tag_count_type_list =  zip(tag_count, tag_href)

        for item in tag_count_type_list:
            print(item[0], item[1])
            tag_all_count += item[0]
            if item[1] == 'jd':
                tag_jd_count += item[0]
            elif item[1] == 'cy':
                tag_cy_count += item[0]
            elif item[1] in ['gw', 'yl']:
                tag_gw_yl_count += item[0]

        yj_url = 'http://www.mafengwo.cn/yj/{}/2-0-1.html'.format(cityid)
        soup = get_html(browser, yj_url)
        total_city_yj_count = int(soup.find(name='span', attrs={'class', 'count'}).find_all(name='span')[1].get_text())

        print('cityname', cityname)
        print('all_tags_count', tag_all_count)
        print('jd_tags_count', tag_jd_count)
        print('cy_tags_count', tag_cy_count)
        print('yl&gw_tags_count', tag_gw_yl_count)
        print('all_yj_counts', total_city_yj_count)
        return {'cityname': cityname,
                'all_tags_count': tag_all_count,
                'jd_tags_count': tag_jd_count,
                'cy_tags_count': tag_cy_count,
                'yl&gw_tags_count': tag_gw_yl_count,
                'all_yj_counts': total_city_yj_count}
    except Exception as e:
        logging.info(f'{cityname} has no tags.')
        logging.info(f'Exception: {e}')
        return {'cityname': cityname,
                'all_tags_count': tag_all_count,
                'jd_tags_count': tag_jd_count,
                'cy_tags_count': tag_cy_count,
                'yl&gw_tags_count': tag_gw_yl_count,
                'all_yj_counts': 0}


#获取城市美食信息，包括美食名称，热度数量
def get_city_food(cityname, cityid, browser):
    logging.info(f'获取{cityname}美食信息...')
    url = 'http://www.mafengwo.cn/cy/{}/gonglve.html'.format(cityid)

    soup = get_html(browser, url)
    try:
        foods_list = soup.find(name='ol', attrs={'class': 'list-rank'}).find_all(name='h3')
        foods = ['{}-{}'.format(cityname, item.get_text().strip()) for item in foods_list]
        foods_count_list = soup.find(name='ol', attrs={'class': 'list-rank'}).find_all(name='span', attrs={'class': 'trend'})
        foods_count = [int(item.get_text().strip()) for item in foods_count_list]
        foods_info = zip(foods, foods_count)

        return list(foods_info)
    except Exception as e:
        logging.info(f'smoe error occur while access the food information in city {cityname}, error: {e}')
        return None


#获取城市景点信息， 包括景点名，景点点评数
def get_city_jd(cityname, cityid, browser):
    logging.info(f'获取{cityname}景点信息...')
    url = 'http://www.mafengwo.cn/jd/{}/gonglve.html'.format(cityid)
    print(url)

    soup = get_html(browser, url)
    try:
        jd_info_list = soup.find(name='div', attrs={'class': 'row row-top5'}).find_all(name='h3')
        #获取景点名
        jd_name = ['{}-{}'.format(cityname, node.find(name='a').get_text().strip()) for node in jd_info_list]
        # 获取景点的点评数量
        comment_count = [int(node.find(name='em').get_text().strip()) for node in jd_info_list]

        jd_info = zip(jd_name, comment_count)

        return list(jd_info)
    except Exception as e:
        logging.info(f'smoe error occur while access the food information in city {cityname}, error: {e}')
        return None

#数据可视化
def get_hot_city(file, sheet_name):
    info_excel = pd.read_excel(file, sheet_name=sheet_name)

    data_info = {info_excel['cityname'][i]: [info_excel['all_tags_count'][i], info_excel['jd_tags_count'][i],
                                             info_excel['cy_tags_count'][i], info_excel['yl&gw_tags_count'][i],
                                             info_excel['all_yj_counts'][i]]
                 for i in range(len(info_excel))}

    #游记总数排名
    city_rank = sorted(data_info.items(), key=lambda x:x[1][4], reverse=True)
    #景点标签排名
    city_jd_rank = sorted(data_info.items(), key=lambda x:x[1][1], reverse=True)
    #餐饮标签排名
    city_food_rank = sorted(data_info.items(), key=lambda x:x[1][2], reverse=True)
    #休闲标签
    city_xx_rank = sorted(data_info.items(), key=lambda x:x[1][3], reverse=True)

    x = np.arange(1, 21, 1)

    hot_city = city_rank[:20]
    y_hot = list()
    x_hot_tick_label = list()
    for item in hot_city:
        y_hot.append(item[1][4])
        x_hot_tick_label.append(item[0])

    jd_city = city_jd_rank[:20]
    y_jd = list()
    x_jd_tick_label = list()
    for item in jd_city:
        y_jd.append(item[1][1])
        x_jd_tick_label.append(item[0])

    food_city = city_food_rank[:20]
    y_food = list()
    x_food_tick_label = list()
    for item in food_city:
        y_food.append(item[1][2])
        x_food_tick_label.append(item[0])

    xx_city = city_xx_rank[:20]
    y_xx = list()
    x_xx_tick_label = list()
    for item in xx_city:
        y_xx.append(item[1][3])
        x_xx_tick_label.append(item[0])

    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False

    plt.figure(0)
    plt.bar(x, y_hot, align='center', color='c', tick_label=x_hot_tick_label, alpha=0.6)
    plt.xlabel('城市名')
    plt.ylabel('游记数量')
    plt.title('游记总数排名')

    plt.figure(1)
    plt.bar(x, y_jd, align='center', color='#FF3399', tick_label=x_jd_tick_label, alpha=0.6)
    plt.xlabel('城市名')
    plt.ylabel('景点标签数')
    plt.title('景点标签总数排名')

    plt.figure(2)
    plt.bar(x, y_food, align='center', color='#6633FF', tick_label=x_food_tick_label, alpha=0.6)
    plt.xlabel('城市名')
    plt.ylabel('美食标签数')
    plt.title('美食标签总数排名')

    plt.figure(3)
    plt.bar(x, y_xx, align='center', color='#0000FF', tick_label=x_xx_tick_label, alpha=0.6)
    plt.xlabel('城市名')
    plt.ylabel('休闲标签数')
    plt.title('休闲标签总数排名')

    plt.show()


def get_food_city(foodfile, foodsheet, name, data, basefile, basesheet):
    base_info = pd.read_excel(basefile, sheet_name=basesheet)
    yj_num = {base_info['cityname'][i]: int(base_info['all_yj_counts'][i]) for i in range(len(base_info)) if base_info['all_yj_counts'][i]}

    food_info = pd.read_excel(foodfile, sheet_name=foodsheet)

    food_num = [(food_info[name][i], int(food_info[data][i])) for i in range(len(food_info))]

    food_rate = list()
    for item in food_num:
        city = item[0].split('-')[0]
        rate = item[1] / yj_num[city]
        food_rate.append((item[0], rate))

    food_rate = sorted(food_rate, key=lambda x:x[1], reverse=True)
    food_rate = food_rate[:20]

    #生成图表
    create_bar(food_rate, title='美食热度相对值')


def get_jd_city(jdfile, jdsheet, name, data):
    jd_info = pd.read_excel(jdfile, sheet_name=jdsheet)
    jd_num = [(jd_info[name][i], int(jd_info[data][i])) for i in range(len(jd_info))]

    jd_rank = sorted(jd_num, key=lambda x:x[1], reverse=True)
    jd_rank = jd_rank[:20]

    #生成图表
    create_bar(jd_rank, color='#00BB00', title='景点点评数')


def create_bar(source_lst:list, color='#FF8800', title=None):
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    fig = plt.figure()
    ax = fig.add_axes([0.09, 0.1, 0.9, 0.85])

    x = np.arange(1, 21, 1)
    y = list()
    x_tick_label = list()

    for item in source_lst:
        y.append(item[1])
        x_tick_label.append(item[0])

    for ticklabel in ax.xaxis.get_ticklabels():
        ticklabel.set_rotation(75)
        ticklabel.set_fontstyle('normal')
        ticklabel.set_fontsize(8)

    ax.bar(x, y, align='center', color=color, tick_label=x_tick_label, alpha=0.6)
    plt.title(title)

    plt.show()



if __name__ == '__main__':

    flag = False
    spider = False

    if not flag:
        get_food_city('food_data_info.xlsx', 'food info', 'foods', 'foods_count', 'city_data_info.xlsx', 'base info')
        get_jd_city('jd_data_info.xlsx', 'viewpoint info', 'jd', 'jd_comment_count')
        get_hot_city('city_data_info.xlsx', 'base info')

    if spider:
        print('start...............')
        browser = webdriver.Chrome()
        browser.maximize_window()

        # 读取excel，获取cityname，cityID
        city_id_excel = pd.read_excel('city_info.xlsx')
        city_id_lst = list()

        if len(city_id_excel['city']) == len(city_id_excel['id']):
            city_id_lst = [(city_id_excel['city'][i].split()[0], city_id_excel['id'][i]) for i in range(len(city_id_excel['city']))]

        base_info_df = pd.DataFrame(columns=['cityname', 'all_tags_count', 'jd_tags_count',
                                             'cy_tags_count', 'yl&gw_tags_count', 'all_yj_counts'])
        food_info_df = pd.DataFrame(columns=['foods', 'foods_count'])
        viewpoint_info_df = pd.DataFrame(columns=['jd', 'jd_comment_count'])

        try:
            print('开始爬取信息。。。。。。')
            # 提取信息
            for item in city_id_lst:
                # 基础信息
                base_data = get_city_base_info(item[0], item[1], browser)
                base_info_df = base_info_df.append(base_data, ignore_index=True)

                # 美食信息
                food_data = get_city_food(item[0], item[1], browser)
                if food_data:
                    for item in food_data:
                        food_line = {'foods': item[0], 'foods_count': item[1]}
                        food_info_df = food_info_df.append(food_line, ignore_index=True)

                # 景点信息
                viewpoint_data = get_city_jd(item[0], item[1], browser)
                if viewpoint_data:
                    for item in viewpoint_data:
                        jd_line = {'jd': item[0], 'jd_comment_count': item[1]}
                        viewpoint_info_df = viewpoint_info_df.append(jd_line, ignore_index=True)
        except Exception as e:
            print('出现异常。。。。。。。')
            print(f'Some error occur: {e}')
        finally:
            print('写入文件。。。。。。。。。')
            with pd.ExcelWriter('city_data_info.xlsx') as writer:
                base_info_df.to_excel(writer, sheet_name='base info')

            with pd.ExcelWriter('food_data_info.xlsx') as writer:
                food_info_df.to_excel(writer, sheet_name='food info')

            with pd.ExcelWriter('jd_data_info.xlsx') as writer:
                viewpoint_info_df.to_excel(writer, sheet_name='viewpoint info')

            browser.close()