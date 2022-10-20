# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor
import scrapy

domain = "magic.tcgplayer.com"
articles = "/db/article_search_result.asp"

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "tcgplayerspider"
    '''
    allowed_domains = [
        domain
    ]
    start_urls = [
        "http://" + domain + articles,
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
        url = "http://" + domain + articles + "?page=1"
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
        t = response.xpath('/html/body/div[3]/div')

        links = []
        for x in t.xpath('.//a[not(contains(@style, "font-size:12px;"))][not(contains(@href, "?page="))][not(contains(@href, "&writer="))]'):
            links.append(x.xpath('.//@href').extract())

        titles = []
        for y in t.xpath('.//a[not(contains(@style, "font-size:12px;"))]'):
            title = "".join(y.xpath('.//h2/text()').extract())
            if title != '':
                titles.append(title)

        published = []
        for x in t.xpath('.//font[contains(text(), "published")]'):
            published.append(x.xpath('.//text()').extract())

        total = len(published) - 1
        i = 0;

        while i < total:
            mPublished = re.sub('\s.*[a-zA-Z]{1,2}$', '', re.sub('published\son\s', '', "".join(published[i])))
            pub = re.split(r'[/]', mPublished)
            pd = pub[2] + "-" + pub[0] + "-" + pub[1]
            if re.sub('/', '-', pd) in date_check:
                item['published'] = pd
                item['link'] = "http://magic.tcgplayer.com/db/article_search_result.asp" + "".join(links[i])
                item['title'] = "".join(titles[i])
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 24
                i += 1
                yield item
            else:
                i += 1
