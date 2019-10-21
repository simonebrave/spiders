'''
使用requests库，访问拉取猫眼电影TOP榜单
调用lxml库，提取TOP100的影片信息，包括榜单名次，影片名，主演，上映时间，评分，并保存到本地文件中
'''

from lxml import etree
import requests

user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
base_url = 'https://maoyan.com/board/4?offset='

#https://maoyan.com/board/4?offset=10

session = requests.Session()
result = list()
with session:
    with open('E:\Python\spider\practice\movietop.txt', 'ab') as file:
        for i in range(10):
            url = base_url + str(i*10)
            with session.get(url, headers={'User-Agent': user_agent}) as response:
                content = response.text

                html = etree.HTML(content)
                titles = html.xpath("//dl[@class='board-wrapper']/dd")

                for title in titles:
                    text = title.xpath(".//text()")
                    item_list = [item for item in map(lambda s:s.strip(), text) if item and '\n' not in item]
                    print(item_list)
                    rate = ''.join(item_list[-2:])
                    text = '  '.join(item_list[:-2]) + ' ' + rate
                    print(text)
                    file.write((text+'\r\n').encode())


