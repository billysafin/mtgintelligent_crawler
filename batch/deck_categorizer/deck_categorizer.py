#-*- coding: utf-8 -*-
import sys
import datetime
from common import *
from db_connection import scrapy
from setting import FORMATS
from sim_calculater import *
import gc
from pprint import pprint

scrapy = scrapy()

def main():
    today = datetime.datetime.today()
    #start = today + datetime.timedelta(days=-1)
    #start = start.strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    
    start = '2014-01-01'
    
    for format_type in FORMATS:
        gc.collect()
        #sample
        meta_names = scrapy.getMetaNames({'format' : format_type})
        
        for meta in meta_names:
            gc.collect()
            decklist = []
            decklist = scrapy.getSampleDecklists({'mtg_meta_name_id' : meta['id']})
        
            if decklist is None or len(decklist) == 0:
                continue
        
            #加工
            sample_main = []
            sample_side = []
            main = []
            side = []
            for card in decklist:
                gc.collect()
                t = 1
                i = 1
                if int(card['mtg_decklist_where_id']) == 1:
                    while t <= int(card['amount']):
                        main.append(card['card_name'])
                        t += 1
                else:
                    while i <= int(card['amount']):
                        side.append(card['card_name'])
                        i += 1
            sample_main = ','.join(main)
            sample_side = ','.join(side)
        
            #デッキ対象
            item = {
                'format' : format_type,
                'start'  : start,
                'end'    : end
            }
            tour_lists = scrapy.getTourList(item)

            if tour_lists is None or len(tour_lists) == 0:
                continue

            for tour in tour_lists:
                players = scrapy.getDecklistIds({'tour_id': tour['id']})            

            for player in players:
                gc.collect()
                decklist = scrapy.getDecklist({'decklist_id' : player['id']})

                #加工
                main = []
                side = []
                for card in decklist:
                    t = 1
                    i = 1
                    if int(card['mtg_decklist_where_id']) == 1:
                        while t <= int(card['amount']):
                            main.append(card['card_name'])
                            t += 1
                    else:
                        while i <= int(card['amount']):
                            side.append(card['card_name'])
                            i += 1

                main_compare = ','.join(main)
                
                #only for future use
                side_compare = ','.join(side)

                #compare
                main_sim = int(jaccard_calculate(sample_main, main_compare)) * 100
                
                #for future use
                #side_sim = dice_calculate(sample_side, side_compare)
                
                #フォマットによって％を変更
                if format_type == 1:
                    if main_sim >= 80:
                        item = {}
                        item['meta_deck_name_id'] = meta['id']
                        item['id'] = player['id']
                        scrapy.updatCategory(item)
                elif format_type == 2:
                    if main_sim >= 80:
                        item = {}
                        item['meta_deck_name_id'] = meta['id']
                        item['id'] = player['id']
                        scrapy.updatCategory(item)
                elif format_type == 3:
                    if main_sim >= 80:
                        item = {}
                        item['meta_deck_name_id'] = meta['id']
                        item['id'] = player['id']
                        scrapy.updatCategory(item)  
                elif format_type == 4:
                    if main_sim >= 80:
                        item = {}
                        item['meta_deck_name_id'] = meta['id']
                        item['id'] = player['id']
                        scrapy.updatCategory(item)
                
if __name__ == '__main__':
    main()
