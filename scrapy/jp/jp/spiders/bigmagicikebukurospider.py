# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "108038.diarynote.jp"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "bigmagicikebukurospider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/list\/",
            "\/list\/\?page=1"
        ],
        deny = [
            r"^(?!.*\/list\/.*).*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain + "/list/"
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
        for t in response.xpath('//*[@id="main"]/ul[@class="list-article-list"]/li'):
            published = "".join(t.xpath('.//span[1]/text()').extract())
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = "".join(t.xpath('a/span[@class="list-subject"]/text()').extract())
                url = "".join(t.xpath('.//a/@href').extract())
                item['link'] = "http://108038.diarynote.jp" + url
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 15
                yield item
