# -*- coding: utf-8 -*-
import datetime
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import re
import scrapy

domain = "blog.livedoor.jp"
article = "/gobasan/"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "5thsanMTGspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain + article,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            article,
            "\?p=1"
        ],
        deny = [
            r"^(?!.*\/gobasan\/.*).*",
            r".*\/archives\/.*",
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain + article + "?p=1"
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
        for t in response.xpath('//*[@id="main"]/div[2]/div/div[2]/div/div/div'):
            published = "".join(t.xpath('.//div[1]/div[1]/abbr/@title').extract())
            published = re.sub('T.*$', '', published)
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = "".join(t.xpath('.//div[1]/div[2]/h2/a/text()').extract())
                item['link'] =  "".join(t.xpath('.//div[1]/div[2]/h2/a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 9
                yield item
