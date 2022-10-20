# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
import scrapy
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor

domain = "hareruyamtg.com"
articles = "/article/en/sp/"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "hareruyaEnglishspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "https://www." + domain + articles
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            r"\?cmdarticlesearch=1&posted_sort=d&absolutepage=1"
        ],
        deny = [
            r"(!?.*\?cmdarticlesearch=1&posted_sort=d&absolutepage=1).+$",
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "https://www." + domain + articles + "?cmdarticlesearch=1&posted_sort=d&absolutepage=1"
        yield scrapy.Request(url=url, callback=self.parse_item)
    
    def parse_item(self, response):
        item = WizardsItem()
        yesterday = datetime.date.today() - datetime.timedelta(1),
        two_days_ago = datetime.date.today() - datetime.timedelta(2)
        date_check = [
            datetime.date.today().strftime('%Y-%m-%d'),
            yesterday[0].strftime('%Y-%m-%d'),
            two_days_ago.strftime('%Y-%m-%d')
        ]
        for t in response.xpath('//html/body/div/div[@class="container"]/div[@class="forcms_block"]/a'):
            published = "".join(t.xpath('.//div/div/p[@class="date"]/text()').extract())
            published = re.sub(r'\.', '-', published)
            if re.sub('/', '-', published) in date_check:
                item['published']  = published
                item['link'] = "".join(t.xpath('.//@href').extract())
                item['title'] = "".join(t.xpath('.//div/div/p[@class="title"]/text()').extract()).strip()
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 26
                yield item
