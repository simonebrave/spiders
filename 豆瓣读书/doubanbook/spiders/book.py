# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.response.html import HtmlResponse
from ..items import DoubanbookItem


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['douban.com']
    start_urls = ['https://book.douban.com/tag/%E7%BC%96%E7%A8%8B?start=0&type=T']

    custom_settings = {
        'filename': 'E:\Python\spider\practice\dbresult.txt'
    }

    def parse(self, response:HtmlResponse):
        print(type(response), '+++++++++++++++++++++++++')
        print(response.encoding)
        print(response.status)

        with open('books.html', 'w', encoding='utf8') as f:
            f.write(response.text)

        subjects = response.xpath('//li[@class="subject-item"]')
        for subject in subjects:
            item = DoubanbookItem()

            title = subject.xpath('.//h2/a/text()').extract_first()
            item['title'] = title.strip()

            rate = subject.xpath('.//span[@class="rating_nums"]/text()').extract_first()
            item['rate'] = rate

            publish = subject.xpath('.//div[@class="pub"]/text()').extract_first()
            item['publish'] = publish.strip()
            yield item

        for i in range(2):
            next_pag = response.xpath('//div[@class="paginator"]/a/@href').extract_first()
            url = response.urljoin(next_pag)
            yield  scrapy.Request(url=url, callback=self.parse)
