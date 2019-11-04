import requests
import json
import pandas as pd
from lxml import etree
from queue import Queue


EXCEL = 'books.xlsx'

books_list = Queue()
book_info_url = Queue()
htmls_dom = Queue()

key_word = ['出品方:','丛书:']

#从excel中读取书名
def read_books(filename):
    print('读取书名')
    exc_doc = pd.read_excel(filename)
    blist = list(exc_doc['书名'])
    for book in blist:
        books_list.put(book)
    print(books_list)


#拉取书本信息url
def get_urls():
    print('获取书本信息的url')
    while not books_list.empty():
        bookname = books_list.get()
        url = 'https://book.douban.com/j/subject_suggest?q={}'.format(bookname)
        response = requests.get(url=url)
        results = json.loads(response.text)
        print('results:', results)
        book_info_url.put(results[0]['url'])


#拉取详情html DOM
def request_book():
    print('拉取详情HTML DOM')
    while not book_info_url.empty():
        url = book_info_url.get()
        print(url)
        html = requests.get(url)
        htmls_dom.put(html.text)
        # if os.path.exists(FILENAME):
        #     os.remove(FILENAME)
        # with open(FILENAME, 'w', encoding='utf8') as f:
        #     f.write(html.text)


#拉取基本信息
def get_information(books_info_list:list):
    print('获取书本详情')
    # if os.path.exists(FILENAME):
    while not htmls_dom.empty():
        book_info = dict()
        dom = htmls_dom.get()
        html = etree.HTML(dom, etree.HTMLParser())
        title = html.xpath('//div[@id="wrapper"]/h1/span/text()')[0]
        author_info = html.xpath('//div[@id="info"]/a/text()')[0].strip().split()
        author = ''.join(author_info)
        info = [v for v in html.xpath('//div[@id="info"]/text()') if v.strip()]
        binfo = html.xpath('//div[@id="info"]//*')

        book_info['书名:'] = title
        book_info['作者:'] = author

        book_info.update(get_plinfo(binfo, info))

        #提取豆瓣评分
        book_info['评分:'] = html.xpath('//div[contains(@class, "rating_self")]/strong/text()')[0].strip()

        #提取评论数
        book_info['评论数'] = html.xpath('//a[@class="rating_people"]/span/text()')[0].strip()

        books_info_list.append(book_info)


#提取出版社，出版时间，价格，ISBN，详细信息
def get_plinfo(binfo, info):
    title = []
    info_dict = {}
    for ele in binfo:
        if ele.tag == 'span':
            text = ele.text.strip()
            if not text.startswith('作者') and text not in key_word:
                if not ele.getchildren() and ele.getparent().tag == 'div':
                     title.append(text)
    for item in zip(title, info):
        info_dict[item[0]] = item[1]
    return info_dict


if __name__ == '__main__':
    read_books(EXCEL)
    get_urls()
    request_book()
    out_list = list()
    get_information(out_list)

    books_frame = pd.DataFrame(out_list)
    books_frame.to_excel('books_ex.xlsx', index=False)



