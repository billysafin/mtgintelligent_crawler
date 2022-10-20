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

#standard
FORMAT = { 
    "standard" : {
        "daily"      : "http://magic.wizards.com/en/articles/archive/mtgo-standings/standard-daily-",
        "league_one" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/competitive-standard-constructed-league-",
        "league_two" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/standard-constructed-league-",
        "ptq"        : "http://magic.wizards.com/en/articles/archive/mtgo-standings/standard-ptq-",
        "mocs"       : "http://magic.wizards.com/en/articles/archive/mtgo-standings/standard-mocs-"
    },
    "modern" : {
        "daily"      : "http://magic.wizards.com/en/articles/archive/mtgo-standings/modern-daily-",
        "league_one" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/competitive-modern-constructed-league-",
        "league_two" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/modern-constructed-league-",
        "ptq"        : "http://magic.wizards.com/en/articles/archive/mtgo-standings/modern-ptq-",
        "mocs"       : "http://magic.wizards.com/en/articles/archive/mtgo-standings/modern-mocs-"
    },
    "legacy" : {
        "daily"      : "http://magic.wizards.com/en/articles/archive/mtgo-standings/legacy-daily-",
        "league_one" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/competitive-legacy-constructed-league-",
        "league_two" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/legacy-constructed-league-",
        "ptq"        : "http://magic.wizards.com/en/articles/archive/mtgo-standings/legacy-ptq-",
        "mocs"       : "http://magic.wizards.com/en/articles/archive/mtgo-standings/legacy-mocs-"
    },
    "vintage" : {
        "daily"      : "http://magic.wizards.com/en/articles/archive/mtgo-standings/vintage-daily-",
        "league_one" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/competitive-vintage-constructed-league-",
        "league_two" : "http://magic.wizards.com/en/articles/archive/mtgo-standings/vintage-constructed-league-",
        "ptq"        : "http://magic.wizards.com/en/articles/archive/mtgo-standings/vintage-ptq-",
        "mocs"       : "http://magic.wizards.com/en/articles/archive/mtgo-standings/vintage-mocs-"
    }
}