# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "izzetmtgnews.com"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "izzetmtgnewsspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://www." + domain,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/archives\/category\/news",
            "\/archives\/category\/news\/page\/1"
        ],
        deny = [
            r".*nicovideo.*",
            r".*wizards.*",
            r".*a8.*",
            r".*amazon.*",
            r".*fc2.*",
            r".*fgamer.*",
            r".*mtg-jp.*",
            r".*yuyu-tei.*"

        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://www." + domain + "/archives/category/news/page/1"
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
        for t in response.xpath('//html/body/div/div/div/section[@class="mh-content left"]/article/header'):
            published = "".join(t.xpath('.//p/text()').extract())
            published = re.sub(r'日.*s', '', published)
            published = re.sub(r'年|月', '-', published)
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = "".join(t.xpath('.//h3/a/text()').extract())
                item['link'] =   "".join(t.xpath('.//h3/a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 3
                yield item
