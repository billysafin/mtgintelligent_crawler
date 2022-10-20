# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "mtg.anoad.com"
current_year = datetime.date.today().strftime('%Y')

class WizardsspiderSpider(scrapy.Spider):
#class WizardsspiderSpider(CrawlSpider):
    name = "anoadspider"

    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain + "/?m=2014&paged=1",
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "/?m=[0-9]{4}",
            "/?m=[0-9]{4}&paged=[0-9]*"
        ],
        deny = [
            r"\?page_id=[0-9].*",
            r"\?cat=[0-9].*",
            r"\?p=[0-9].*"
        ],
    ), callback='parse_item', follow=True),)
    '''

    def start_requests(self):
        url = "http://" + domain + "/?m=" + current_year + "&paged=1"
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
        for t in response.xpath('//*[@id="content"]/div[contains(@class, "type-post status-publish")]'):
            published = "".join(t.xpath('.//div/span/text()').extract())
            published = re.sub(r'日', '', re.sub(r'月', '-', re.sub(r'年', '-', re.sub(r'作成日:\s', '', published))))
            if re.sub('/', '-', published) in date_check:
                item['link'] = "".join(t.xpath('.//h2/a/@href').extract())
                item['title'] = "".join(t.xpath('.//h2/a/text()').extract())
                item['published'] = published
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 33
                yield item