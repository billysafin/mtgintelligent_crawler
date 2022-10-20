# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "kungfumagic.com"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "kungfumagicspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/archives.php"
        ],
        deny = [
            r"^(?!.*\/archives.php).*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain + "/archives.php"
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
        for t in response.xpath('//*[@id="content"]/div/div[3]/ul/li'):
            published = "".join(t.xpath('.//text()').extract())
            published = re.sub(r'\.', '-', re.sub(r': ', '', published[0:10]))
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = "".join(t.xpath('.//a/text()').extract())
                item['link'] = "".join(t.xpath('.//a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 22
                yield item
