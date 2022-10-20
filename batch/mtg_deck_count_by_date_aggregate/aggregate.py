#-*- coding: utf-8 -*-
from db_connection import scrapy
import gc

scrapy = scrapy()

#main
def main():
    aggregates = scrapy.getCounts()
    for items in aggregates:
        gc.collect()
        scrapy.insertOrUpdate(items)
        

if __name__ == '__main__':
    main()