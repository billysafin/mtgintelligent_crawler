# -*- coding: utf-8 -*-
from scrapy.item import Item, Field
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

class WizardsItem(Item):
  title = Field()
  link = Field()
  published = Field()
  date = Field()
  source_from = Field()
  pass