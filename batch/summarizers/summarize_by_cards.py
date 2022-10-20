#-*- coding: utf-8 -*-
import datetime
import calendar
import sys
from common import *
from db_connection import scrapy, summary
from setting import FORMATS
import gc

scrapy = scrapy()
summary = summary()

#calculate
def calculate(start, end, which):
    #集計
    for format_type in FORMATS:
        gc.collect()
        item = {
            'start'      : start,
            'end'        : end,
            'format'     : format_type,
            'country_id' : 1
        }
        result = scrapy.getSummaryBycards(item)
        
        #DBに投入
        if result is not None:
            for res in result:
                data = {
                    'start'            : start,
                    'end'              : end,
                    'format'           : format_type,
                    'country_id'       : 1,
                    'mtg_card_main_id' : res['mtg_card_main_id'],
                    'total_used'       : res['total_used']
                }
                if which == 'weekly':
                    summary.putWeeklyBycard(data)
                else:
                    summary.putMonthlyBycard(data)

#main
def main():
    #引数があるかのチェック
    argvs = sys.argv
    argc = len(argvs)
    
    if argc != 2:
        send_mail('引数がありませんぜよ!')
        sys.exit()
    
    today = datetime.date.today()
    if argvs[1] == 'weekly':
        start = today + datetime.timedelta(days=-7)
        start = start.strftime("%Y-%m-%d")
        end = today + datetime.timedelta(days=-1)
        end = end.strftime("%Y-%m-%d")
    elif argvs[1] == 'monthly':
        start = today + datetime.timedelta(days=-1)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = str(start.year) + '-' + str(start.month) + '-' + str(last_day)
        start = str(start.year) + '-' + str(start.month) + '-01'
    else:
        send_mail('引数が間違ったフォーマットです')
        sys.exit()

    calculate(start, end, argvs[1])

if __name__ == '__main__':
    main()