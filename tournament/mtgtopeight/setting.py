# -*- coding: utf-8 -*-
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"

# SQL DATABASE SETTING
SQL_SETTING = {
    'SQL_DB'    :'scrapy',
    'SQL_HOST'  :'10.20.0.1',
    'SQL_USER'  :'mtgstats',
    'SQL_PASSWD':'mtgstats',
    'SQL_CHAR'  :'utf8'
}

CHECKED_PLAYER = []

FORMATS = {
    "Standard"   : 1
    ,"Modern"    : 2
    ,"Legacy"    : 3
    ,"Vintage"   : 4
    ,"Limited"   : 7
    ,"Pauper"    : 6
    ,"Commander" : 8
}