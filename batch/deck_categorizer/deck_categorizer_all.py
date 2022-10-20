#-*- coding: utf-8 -*-
import sys
import datetime
from datetime import datetime as dt
from common import *
from db_connection import scrapy
from setting import FORMATS
from sim_calculater import *
from dateutil.relativedelta import relativedelta
import gc

scrapy = scrapy()

def main():
    for format_type in FORMATS:
        gc.collect()
        #all decklists
        item = {}
        item['format_type'] = format_type
        start_time = '2014-01-01'
        start = dt.strptime(start_time, '%Y-%m-%d')
        item['end'] = start
        all_decklists = scrapy.getAllDecklists(item)
        
        #sample
        meta_names = scrapy.getMetaNames({'format' : format_type})
        
        for decklist in all_decklists:
            gc.collect()
            deck = scrapy.getDecklist({'decklist_id' : decklist['decklist_id']})
        
            for meta in meta_names:
                gc.collect()
                item = {}
                item['mtg_meta_name_id'] = meta['id']
                sample_decklist = scrapy.getSampleDecklists(item)
                
                main = []
                side = []
                for card in sample_decklist:
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
                #sample_side = ','.join(side)

                main = []
                side = []    
                for card in deck:
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
                #side_compare = ','.join(side)

                #compare
                main_sim = int(jaccard_calculate(sample_main, main_compare)) * 100

                #for future use
                #side_sim = dice_calculate(sample_side, side_compare)

                #フォマットによって％を変更
                item = {}
                item['meta_deck_name_id'] = ''
                if format_type == 1:
                    if main_sim >= 87:
                        item['meta_deck_name_id'] = meta['id']
                elif format_type == 2:
                    if main_sim >= 87:
                        item['meta_deck_name_id'] = meta['id']
                elif format_type == 3:
                    if main_sim >= 87:
                        item['meta_deck_name_id'] = meta['id']
                elif format_type == 4:
                    if main_sim >= 87:
                        item['meta_deck_name_id'] = meta['id']
                
                if item['meta_deck_name_id'] != '':
                    item['id'] = decklist['decklist_id']
                    scrapy.updatCategory(item)

if __name__ == '__main__':
    main()