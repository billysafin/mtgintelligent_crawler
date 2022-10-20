# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "d.hatena.ne.jp"
article = "/Strike"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "strikeandtournamentspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain + article,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/archive\/",
            "\/archive\/[0-9]{6,}"
        ],
        deny = [
            r"^(?!.*\/archive\/.*).*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain + article + "/archive/"
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
        for t in response.xpath('//*[@id="hatena-archive"]/div[3]/div/div/ul/li[@class="archive archive-date"]'):
            published = "".join(t.xpath('.//a/text()').extract())
            published = published[0:10]
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = "".join(t.xpath('.//ul/li[@class="archive archive-section"]/a/text()').extract())
                item['link'] =   "".join(t.xpath('.//ul/li[@class="archive archive-section"]/a/@href').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 10
                yield item
