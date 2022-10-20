# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "mtgoacademy.com"
articles = "/category/article"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "mtgoacademyspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "https://www." + domain + articles,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            r"\/",
            r"\/page\/1\/"
        ],
        deny = [
            r".*\/store\/.*",
            r".*\/video\+[a-zA-Z0-9].*\/.*",
            r".*\/tutorials\/.*",
            r".*\/the-academy\/.*",
            r".*\/mission-statement\/.*",
            r".*\/mtgo-academy-update\/.*",
            r".*\/mtgo-academy-casting-call\/.*",
            r".*\/contact\/.*",
            r".*\/\?s=&submit=Search\/.*",
            r".*\/catalog\/.*",
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "https://www." + domain + articles + "/page/1/"
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
        for t in response.xpath('//article[contains(@class,"status-publish")]'):
            published = "".join(t.xpath('.//div/div[@class="entry-date"]/a/time/@datetime').extract())
            published = re.sub(r'T.*$', '', published)
            if re.sub('/', '-', published) in date_check:
                item['published']  = published
                item['link'] = "".join(t.xpath('.//div/div[@class="entry-title"]/a/@href').extract())
                item['title'] = "".join(t.xpath('.//div/div[@class="entry-title"]/a/text()').extract()).strip()
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 29
                yield item
