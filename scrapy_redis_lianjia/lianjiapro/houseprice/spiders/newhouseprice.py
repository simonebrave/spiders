# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.http.response.html import HtmlResponse
from ..items import HousepriceItem


class NewhousepriceSpider(RedisCrawlSpider):
    name = 'newhouseprice'
    allowed_domains = ['lianjia.com']
    redis_key = 'newhouseprice:start_urls'
    base_url = 'https://cd.fang.lianjia.com/loupan/pg{}/'
    # start_urls = ['http://lianjia.com/loupan/']

    rules = (
        Rule(LinkExtractor(allow=r'data-page="\d+"'), callback='parse', follow=True),
    )

    def parse(self, response:HtmlResponse):
        print('#############解析response################')

        objs = response.xpath('//ul[@class="resblock-list-wrapper"]/li[@class="resblock-list post_ulog_exposure_scroll has-results"]')

        for obj in objs:
            print(obj.extract())
            item = HousepriceItem()

            # name   //ul[@class="resblock-list-wrapper"]//div[@class="resblock-name"]/a/text()
            item['name'] = obj.xpath('.//div[@class="resblock-name"]/a/text()').extract_first().strip()
            #type    //ul[@class="resblock-list-wrapper"]//div[@class="resblock-name"]/span/text()        #取第一个span的text（）
            item['type'] = obj.xpath('.//div[@class="resblock-name"]/span[@class="resblock-type"]/text()').extract_first().strip()
            #price   //ul[@class="resblock-list-wrapper"]//div[@class="resblock-price"]//span/text()      #取第一个span的text（）
            item['price'] = obj.xpath('.//div[@class="resblock-price"]//span[@class="number"]/text()').extract_first().strip()
            #location  //ul[@class="resblock-list-wrapper"]//div[@class="resblock-location"]/span/text()  #取两个span的text（）
            locations = obj.xpath('.//div[@class="resblock-location"]/span/text()').extract()
            item['location'] = '{}-{}'.format(locations[0].strip(), locations[1].strip())
            #area      //ul[@class="resblock-list-wrapper"]//div[@class="resblock-area"]/span/text()
            tmp = obj.xpath('.//div[@class="resblock-area"]/span/text()')
            if tmp:
                item['area'] = re.search('\d+-?\w*', tmp.extract_first().strip()).group()
            else:
                item['area'] = None

            yield item

        #获取下一次需要访问的资源
        next  = response.css('.page-box span.active + a::attr("data-page")').extract_first()
        if next == '2':
            self.crawler.engine.close_spider(self, "停止爬取")
            print('*****************停止爬取**********************')
        else:
            print('~~~~~~~~~~~next~~~~~~~~~~~', next)
            url = self.base_url.format(next)
            yield scrapy.Request(url=url, callback=self.parse)
