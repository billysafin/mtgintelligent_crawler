# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "mtgmintcard.com"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "mtgmintcardspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://www." + domain + "/articles",
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\?page=1"
        ],
        deny = [
            r".*\/mtg\/singles\/.*",
            r".*\/mtg\/card-lots\/.*",
            r".*\/promotion\/.*",
            r".*\/accessories\/.*",
            r".*\/buylist\/.*",
            r".*\/login\/.*",
            r".*\/faq\/.*",
            r".*\/shipping\/.*",
            r".*\/privacy\/.*",
            r".*\/guarantee\.php\/.*",
            r".*\/terms-of-use\/.*",
            r".*\/contact-us\/.*",
            r".*\/global-site-search.*",
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://www." + domain + "/articles?page=1"
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
        for t in response.xpath('//*[@id="articlesBody"]/div/div[2]/div[1]/div/div[@class="col-sm-4"]'):
            published = t.xpath('.//div/div/div/div[@class="col-sm-7"]/div[@class="articlesDateAndWriter"]')
            topDate = "".join(published.xpath('.//span/@title').extract())
            if topDate != '':
                published = re.sub(r',.*$', '', topDate)
            else:
                published = re.sub(',.*$', '', re.sub('\n', '', published.xpath('.//text()').extract()[2]))
            pdate = datetime.datetime.strptime(published, "%d %b %Y")
            pdate = pdate.strftime('%Y-%m-%d')
            if re.sub('/', '-', pdate) in date_check:
                item['published'] = pdate
                item['link'] = t.xpath('.//div/div/div[1]/div/a/@href').extract()[0]
                item['title'] = "".join(t.xpath('.//div/div/div[1]/div/a/b/text()').extract())
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 23
                yield item
