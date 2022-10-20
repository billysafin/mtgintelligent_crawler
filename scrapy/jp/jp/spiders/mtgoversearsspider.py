# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "mtgoversears.com"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "mtgoversearsspider"
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
            r".*\/category\/.*"
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
        for t in response.xpath('//*[@id="list"]/div/div[@class="entry-card-content"]'):
            published = "".join(t.xpath('.//p/span/span[@class="published"]/text()').extract())
            if re.sub('/', '-', published) in date_check:
                item['title'] = "".join(t.xpath('.//h2/a/text()').extract())
                item['link'] =   "".join(t.xpath('.//h2/a/@href').extract())
                item['published'] = published
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 4
                yield item
