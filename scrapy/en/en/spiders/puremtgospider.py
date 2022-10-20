# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "puremtgo.com"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "puremtgospider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            r"\/node\?page1",
            r"\/"
        ],
        deny = [
            r".*\/articles\/.*",
            r".*\/forum\/.*",
            r".*\/deck\/.*",
            r".*\/node\/1451.*",
            r".*\/user\/.*",
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain
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
        for t in response.xpath('//*[@id="main-content"]/div[contains(@class, "node")]'):
            published = "".join(t.xpath('.//div[contains(@class,"node-info")]/span[@class="published"]/text()').extract())
            published = re.sub(r'\s[0-9]{1,2}:[0-9]{1,2}[a-z]{1,2}$', '', published)
            pdate = datetime.datetime.strptime(published, "%b %d %Y")
            pdate = pdate.strftime('%Y-%m-%d')
            if re.sub('/', '-', pdate) in date_check:
                item['published'] = pdate
                item['link'] = "http://puremtgo.com" + "".join(t.xpath('.//div[@class="node-title"]/a/@href').extract())
                item['title'] = "".join(t.xpath('.//div[@class="node-title"]/a/@title').extract()).strip()
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 28
                yield item
