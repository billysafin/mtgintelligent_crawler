#-*- coding: utf-8 -*-
from db_connection import scrapy
import gc

scrapy = scrapy()
#main
def main():
    stats = scrapy.getStats()

    for item in stats:
        gc.collect()
        item['total_players'] = scrapy.getTotalPlayersByMetaId(item['meta_id'], item['date'])[0]['total_players']
        item['delete_flag'] = 0
        scrapy.insertOrUpdate(item)

if __name__ == '__main__':
    main()
