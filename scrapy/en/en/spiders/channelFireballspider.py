# -*- coding: utf-8 -*-
import datetime
import re
from en.items import WizardsItem
import scrapy
#from scrapy.spiders import CrawlSpider, Rule
#from scrapy.linkextractors import LinkExtractor

#class WizardsspiderSpider(CrawlSpider):
class WizardsspiderSpider(scrapy.Spider):
    name = "channelFireballspider"
    '''
    domain = "channelfireball.com"
    allowed_domains = [
        domain
    
    start_urls = [
        "http://" + domain,
    ]
    rules = (Rule(LinkExtractor(
        allow = [
            "\/articles\/"
        ],
        deny = [
            r"\/buylist.*\/",
            r"\/all-strategy.*\/",
            r"\/videos.*\/",
            r"\/store.*\/",
            r"\/landing.*\/",
            r"\/articles\/(?!page).*\/",
            r"\/articles\/javascript",
            r"\/articles\/[0-9]{1,}.*\/"
        ],
    ), callback='parse_item', follow=True),)
    '''
    def start_requests(self):
        url = "http://channelfireball.com/articles/"
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
        for t in response.xpath('//*[@id="mainContent"]/article'):
            if 'articleContainer oneUp clearfix' in t.xpath('.//@class').extract():
                #記載日
                published = t.xpath('.//div/p/span/text()').extract()[1]
                published = re.sub(u',', '', re.sub(r"\s\s//\s\s", "", published))
                pdate = datetime.datetime.strptime(published, "%d %b %Y")
                #link
                link = "".join(t.xpath('.//div/h2/a/@href').extract())
                #title
                title = "".join(t.xpath('.//div/h2/a/descendant-or-self::*/text()').extract())
            else:
                #記載日
                published = t.xpath('.//div/div/span/text()').extract()[2]
                published = re.sub(u',', '', published)

                pdate = datetime.datetime.strptime(published, "%d %b %Y")
                #link
                link = "".join(t.xpath('.//div/div/h3/a/@href').extract())
                #title
                title = t.xpath('.//div/div/h3/a/text()').extract()
                if (len(title) == 3):
                    title = title[0] + title[2] + title[1]
                else:
                    title= "".join(title)

            pdate = pdate.strftime('%Y-%m-%d')
            if re.sub('/', '-', pdate) in date_check:
                item['published'] = pdate
                item['link'] = link
                item['title'] = title
                aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                item['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
                item['source_from'] = 25
                yield item
