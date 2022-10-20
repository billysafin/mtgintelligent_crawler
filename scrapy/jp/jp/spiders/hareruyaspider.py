# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "hareruyamtg.com"
reading = "/article/"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "hareruyaspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://www." + domain + reading,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\?cmdarticlesearch=1&posted_sort=d&absolutepage=1"
        ],
        deny = [
            r"^(?!.*\?cmdarticlesearch=1&posted_sort=d&absolutepage=1).*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://www." + domain + reading + "?cmdarticlesearch=1&posted_sort=d&absolutepage=1"
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
        for t in response.xpath('//html/body/div[1]/div[4]/div/div[2]/div/div/div[@class="article_list ref clearfix"]'):
            published = "".join(t.xpath('.//ul[@class="articleInfo"]/a/li/p/text()').extract())
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                title = "".join(t.xpath('.//ul[@class="articleInfo"]/a/li[@class="article_ttl"]/text()').extract()).strip()
                title = re.sub('\s+', '', title)
                item['title'] = title.strip()
                item['link'] =   "".join(t.xpath('.//ul[@class="articleInfo"]/a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 2
                yield item
