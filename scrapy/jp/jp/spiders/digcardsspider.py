# -*- coding: utf-8 -*-
import datetime
import re
from jp.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "dig.cards"
article = '/columns/magicthegathering_t'

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "digcardsspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "https://" + domain + article,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\?page=1"
        ],
        deny = [
            r"^(?!.*\?page=1.*).*"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "https://" + domain + article + "?page=1"
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
        for t in response.xpath('//*[@id="main_content"]/section[2]/div'):
            #残りの記事
            for a in t.xpath('.//article[@class="media media_general"]'):
                published = re.sub('\s+', '', "".join(a.xpath('.//a/div/div[2]/time[@class="media_general--time"]/text()').extract()))
                if re.sub('/', '-' ,published) in date_check:
                    item['published'] = published
                    item['title'] = re.sub('\s+', '', "".join(a.xpath('.//div/div[2]/h2[1]/text()').extract()))
                    sub_link = "".join(a.xpath('.//a/@href').extract())
                    item['link'] = "https://dig.cards" + sub_link
                    aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                    item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                    item['source_from'] = 6
                    yield item

            #最新１件
            published = re.sub('\s+', '', "".join(t.xpath('.//article[1]/a/div/div[1]/time[@class="media_primary--time"]/text()').extract()))
            if re.sub('/', '-', published) in date_check:
                item['published'] = published
                item['title'] = re.sub('\s+', '', "".join(t.xpath('.//a/div/div[1]/h2[@class="media_primary--heading"]/text()').extract()))
                link = "".join(t.xpath('.//article[1]/a/@href').extract())
                item['link'] = "https://dig.cards" + link
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 6
                yield item
