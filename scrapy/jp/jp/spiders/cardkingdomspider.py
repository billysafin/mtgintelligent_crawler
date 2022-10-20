# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class WizardsspiderSpider(CrawlSpider):
    name = "cardkingdomspider"
    domain = "63088.diarynote.jp"
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/list\/",
            "\/list\/\?page=1"
        ],
        deny = [
            r"^(?!.*\/list\/.*).*"
        ],
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
        for t in response.xpath('//*[@id="main"]/ul[@class="list-article-list"]/li'):
            title = "".join(t.xpath('a/span[@class="list-subject"]/text()').extract())
            if re.search('マジック：ザ・ギャザリング', title):
                published = "".join(t.xpath('.//span[1]/text()').extract())
                published = re.sub(r'月', '-', re.sub(r'年', '-', published[0:10]))
                if re.sub('/', '-', published) in date_check:
                    item['published'] = published
                    item['title'] = title
                    url = "".join(t.xpath('.//a/@href').extract())
                    item['link'] = "http://63088.diarynote.jp" + url
                    aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                    item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                    item['source_from'] = 18
                    yield item
