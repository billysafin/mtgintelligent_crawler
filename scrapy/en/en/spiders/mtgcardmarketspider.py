# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "articles.mtgcardmarket.com"
articles = "/category/articles"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "mtgcardmarketspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain + articles,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            r"\/",
            r"\/page\/1\/"
        ],
        deny = [
            r".*\/videos\/.*",
            r".*\/about\/.*",
            r".*\/contact_us\/.*",
            r".*\/policy\/.*",
            r".*\/live\/.*",
            r".*\/news\/.*",
            r".*\/card_condition_guide\/.*",
            r".*\/products\/.*",
            r".*\/buylist\/.*",
            r".*\/catalog\/.*",
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://" + domain + articles + "/page/1/"
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
        for t in response.xpath('//*[@id="content"]/div[contains(@class, "status-publish")]'):
            published = "".join(t.xpath('.//div[@class="entry-utility"]/div[@class="tabs-content"]/div[1]/p/abbr[@class="published"]/text()').extract())
            published  = re.sub(r',', '', published)
            pdate = datetime.datetime.strptime(published, "%B %d %Y")
            pdate = pdate.strftime('%Y-%m-%d')
            if re.sub('/', '-', pdate) in date_check:
                item['published'] = pdate
                item['link'] = "".join(t.xpath('.//h2[@class="entry-title"]/a/@href').extract())
                item['title'] = "".join(t.xpath('.//h2[@class="entry-title"]/a/text()').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 32
                yield item
