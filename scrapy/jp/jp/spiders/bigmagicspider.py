# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
import scrapy

domain = "mtg.bigweb.co.jp"

class WizardsspiderSpider(scrapy.Spider):
    name = "bigmagicspider"
    
    def start_requests(self):
        url = "https://" + domain + "/articles/tag?page=1"
        yield scrapy.Request(url=url, callback=self.parse_item)

    def parse_item(self, response):
        item = WizardsItem()
        yesterday = datetime.date.today() - datetime.timedelta(1),
        two_days_ago = datetime.date.today() - datetime.timedelta(2)
        date_check = [
            
        ]
        for t in response.xpath('//*[@id="main"]/section/div/ul/li'):
            n = 1
            while n < 21:
                published = "".join(t.xpath('//*[@id="main"]/section/div/ul/li[' + str(n) + ']/div/div/div/text()').extract())
                if re.sub('/', '-', published) in date_check:
                    pass

                item['published'] = published
                item['title'] = "".join(t.xpath('//*[@id="main"]/section/div/ul/li[' + str(n) + ']/div/h3/a/text()').extract())
                item['link'] = "http://www.bigmagic.net" + "".join(t.xpath('//*[@id="main"]/section/div/ul/li[' + str(n) + ']/div/h3/a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 5

                print(item)
                n += 1
                yield item
