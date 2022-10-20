# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
#import scrapy

class WizardsspiderSpider(CrawlSpider):
#class WizardsspiderSpider(scrapy.spider):
    name = "legitmtgspider"
    domain = "legitmtg.com"
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "/page/1/"
        ],
        deny = [
            r".*\/write-for-legit-mtg\/.*",
            r".*\/contact-us\/.*",
            r".*\/category\/.*",
            r".*\/events\/.*",
            r".*\/\?s.*$.*",
            r".*\/products\/.*",
            r".*\/store_policies\/.*",
            r".*\/advanced_search.*",
            r".*\/user\/.*",
            r".*\/store\/.*",
            r".*\/wp-content\/.*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain + "/page/1/"
        yield scrapy.Request(url=url, callback=self.parse_item)
    '''
    def parse_item(self, response):
        item = WizardsItem()
        yesterday = datetime.date.today() - datetime.timedelta(1),
        two_days_ago = datetime.date.today() - datetime.timedelta(2)
        date_check = [
            datetime.date.today().strftime('%Y-%m-%d'),
            yesterday[0].strftime('%Y-%m-%d'),
            two_days_ago.strftime('%Y-%m-%d')
        ]
        for t in response.xpath('//*[@id="system"]/div[1]/div/article'):
            published = "".join(t.xpath('.//header/p/time/@datetime').extract())
            published = re.sub(r'\.', '-', published)
            if re.sub('/', '-', published) in date_check:
                item['published']  = published
                item['link'] = "".join(t.xpath('.//header/h1/a/@href').extract())
                item['title'] = "".join(t.xpath('.//header/h1/a/text()').extract()).strip()
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 27
                yield item
