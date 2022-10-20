#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import pymysql as MySQLdb
import sys
import httplib2
import json

class MySQLPipeline():
    def __init__(self):
        self.conn = MySQLdb.connect(
            host='10.20.0.1',
            user='mtgstats',
            passwd='mtgstats',
            db='scrapy',
            charset='utf8',
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def last_inserted_id(self):
         sql = "SELECT LAST_INSERT_ID() as lid"
         self.cursor.execute(sql)
         id = self.cursor.fetchone()
         return id['lid']

    def getCurrencyId(self, currency_short):
        sql = 'SELECT id as lid FROM currency WHERE currency_short = "' + str(currency_short).upper() + '" and delete_flag = 0'
        self.cursor.execute(sql)
        id = self.cursor.fetchone()

        if id is None:
            sql = 'INSERT INTO currency (name, currency_short) VALUES ("' + str(currency_short).upper() + '", "' + str(currency_short).upper() + '")'
            self.cursor.execute(sql)
            self.cursor.fetchone()
            lid = self.last_inserted_id()

            return lid

        return id['lid']

    def InsertIntoExchangeRate(self, from_id, to_id, rate):
        sql = "INSERT INTO currency_exchange_rate (currency_id_from, currency_id_to, "
        sql += " exchange_rate) VALUES (" + str(from_id) + ", " + str(to_id) + ", " + str(rate) + ")"

        try:
            self.cursor.execute(sql)
        except MySQLdb.Error as e:
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True


APP_ID = 'd17d59ac9bfc43fb8e106641ff854c1e'
BASE = 'USD'
APP_URL = 'https://openexchangerates.org/api/latest.json?app_id=' + APP_ID + '&base=' + BASE
DB = MySQLPipeline()

def main():
    client = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
    response, context = client.request(APP_URL, "GET")
    rates = json.loads(context.decode("utf-8"))['rates']

    usd_id = DB.getCurrencyId(BASE)

    for k in rates:
        to_id = DB.getCurrencyId(k)
        DB.InsertIntoExchangeRate(usd_id, to_id, rates[k])

if __name__ == '__main__':
    main()
