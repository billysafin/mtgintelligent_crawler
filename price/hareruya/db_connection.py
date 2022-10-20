#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import pymysql as MySQLdb

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

    def getCardId(self, setId, editionId):
        sql = 'SELECT mtg_card_id as card_id FROM mtg_card_image where set_number = '
        sql += str(setId) + ' and edition_id = ' + str(editionId) + ' AND country_id = 2'

        self.cursor.execute(sql)
        id = self.cursor.fetchone()

        if id is not None:
            return id['card_id']
        else:
            return None

    def InsertUpdatePrice(self, data):
        sql = 'INSERT INTO mtg_card_price (store_id, mtg_edition_id, mtg_card_id, currency_id, price, url) '
        sql += ' VALUES (' + str(data['store_id']) + ' , ' + str(data['mtg_edition_id']) + ' , ' + str(data['mtg_card_id'])
        sql += ' , ' + str(data['currency_id']) + ' , ' + str(data['price']) + ' , "' + str(data['url']) + '")'
        sql += ' ON DUPLICATE KEY UPDATE price = ' + str(data['price'])

        try:
            self.cursor.execute(sql)
        except MySQLdb.Error as e:
            self.conn.rollback()
            return e
        else:
            self.conn.commit()
            return None
