# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "fgrecservices.com"
articles = "/category/mtg-%E3%82%B3%E3%83%A9%E3%83%A0/"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "fgrecservicesspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://www." + domain,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/page\/1\/"
        ],
        deny = [
            r"^(?!.*\/page\/1\/.*).*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://www." + domain + "/page/1/"
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
        for t in response.xpath('//*[@id="main"]/div/article'):
            published = "".join(t.xpath('.//footer/span/time/@datetime').extract())
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = "".join(t.xpath('.//header/h1/span/a/text()').extract())
                item['link'] = "".join(t.xpath('.//header/h1/span/a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 7
                yield item
