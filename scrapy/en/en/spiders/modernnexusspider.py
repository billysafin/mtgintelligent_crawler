# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class WizardsspiderSpider(CrawlSpider):
    name = "modernnexusspider"
    domain = "modernnexus.com"
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            r"\/category\/[a-zA-Z0-9].*",
            r"\/page\/[2-9]{1,}"
        ],
        deny = [],
    ), callback='parse_item', follow=True),)

    def parse_item(self, response):
        item = WizardsItem()
        yesterday = datetime.date.today() - datetime.timedelta(1),
        two_days_ago = datetime.date.today() - datetime.timedelta(2)
        date_check = [
            datetime.date.today().strftime('%Y-%m-%d'),
            yesterday[0].strftime('%Y-%m-%d'),
            two_days_ago.strftime('%Y-%m-%d')
        ]
        for t in response.xpath('//main/article/header'):
            published = "".join(t.xpath('.//div[@class="entry-meta"]/span/a/time/@datetime').extract())
            published = re.sub(r'T.*$', '', published)
            if re.sub('/', '-', published) in date_check:
                item['published']  = published
                item['link'] = "".join(t.xpath('.//h1/a/@href').extract())
                item['title'] = "".join(t.xpath('.//h1/a/text()').extract()).strip()
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 31
                yield item
