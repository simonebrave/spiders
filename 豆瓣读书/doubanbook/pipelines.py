# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class DoubanbookPipeline(object):
    def __init__(self):
        print('init  >>>>>>>>>>>>>>>>>')

    def open_spider(self, spider):
        print('Start #####################')
        self.file = open(spider.settings.get('filename'), 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = 'title: {} \nrate: {} \npublish: {}\n\n'.format(item['title'], item['rate'], item['publish'])
        print(line)
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
        print('End $$$$$$$$$$$$$$$$$$')
