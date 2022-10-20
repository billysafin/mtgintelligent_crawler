#-*- coding: utf-8 -*-
import pymysql as MySQLdb
import sys
from setting import SCRAPY_SETTING
from common import send_error_mail
        
class scrapy():
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=SCRAPY_SETTING['SQL_HOST'],
            user=SCRAPY_SETTING['SQL_USER'],
            passwd=SCRAPY_SETTING['SQL_PASSWD'],
            db=SCRAPY_SETTING['SQL_DB'],
            charset=SCRAPY_SETTING['SQL_CHAR'],
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
    
    #last_inserted_id
    def last_inserted_id(self):
        sql = "SELECT LAST_INSERT_ID() as lid"
        self.cursor.execute(sql)
        id = self.cursor.fetchone()
        return id['lid']
     
    #get all decklist (init only)
    def getAllDecklists(self, item):
        sql = "SELECT md.id as decklist_id FROM mtg_decklist md INNER JOIN mtg_tournament mt"
        sql += " ON md.tournament_id = mt.id AND mt.delete_flag = 0 AND mt.format = %s AND mt.end <= %s"
        sql += " WHERE md.delete_flag = 0 AND md.meta_deck_name_id is null"
        self.cursor.execute(sql, (
            item['format_type'],
            item['end']
        ))
        return self.cursor.fetchall()
    
    #get meta_names
    def getMetaNames(self, item):
        sql = "SELECT id, name FROM mtg_meta_name WHERE delete_flag = 0 AND "
        sql += "mtg_format_id = %s AND rotation_date > now()"
        self.cursor.execute(sql, (
            item['format']
        ))
        return self.cursor.fetchall()
        
    #get sample decklists
    def getSampleDecklists(self, item):
        sql = "SELECT card_name, mtg_decklist_where_id, used_total as amount FROM mtg_sample_decks WHERE delete_flag = 0 AND "
        sql += "mtg_meta_name_id = %s"
        self.cursor.execute(sql, (
            item['mtg_meta_name_id']
        ))
        return self.cursor.fetchall()
    
    #get tourlists
    def getTourList(self, item):
        sql = "SELECT id FROM mtg_tournament WHERE delete_flag = 0 AND format = %s"
        sql += " AND start >= %s AND end <= %s"
        self.cursor.execute(sql, (
            item['format'],
            item['start'],
            item['end']
        ))
        return self.cursor.fetchall()
    
    #get decklist_ids
    def getDecklistIds(self, item):
        sql = "SELECT id FROM mtg_decklist WHERE delete_flag = 0 AND "
        sql += "tournament_id = %s"
        self.cursor.execute(sql, (
            item['tour_id']
        ))
        return self.cursor.fetchall()
    
    #get decklist
    def getDecklist(self, item):
        sql = "SELECT cards.name as card_name, detail.used_amount as amount, detail.mtg_decklist_where_id,"
        sql += " main.color as color FROM"
        sql += " mtg_decklist_detail detail INNER JOIN mtg_card cards ON detail.card_id"
        sql += " = cards.id AND cards.delete_flag = 0 LEFT JOIN mtg_card_main main ON"
        sql += " cards.id = main.mtg_card_id WHERE detail.delete_flag = 0 AND detail.decklist_id = %s"
        self.cursor.execute(sql, (
            item['decklist_id']
        ))
        return self.cursor.fetchall()
    
    #insert into meta
    def updateMetaName(self, item):
        sql = "SELECT id FROM mtg_meta_name WHERE name = %s AND mtg_format_id = %s"
        sql += " AND rotation_date = %s"
        self.cursor.execute(sql, (
            item['name'],
            item['mtg_format_id'],
            item['rotation_date']
        ))
        result = self.cursor.fetchone()
        if result is None:
            try:
                sql = "INSERT INTO mtg_meta_name (name, mtg_format_id,"
                sql += " rotation_date) VALUES(%s, %s, %s)"
                self.cursor.execute(sql, (
                    item['name'],
                    item['mtg_format_id'],
                    item['rotation_date']
                ))
            except MySQLdb.Error as e:
                print('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
                sys.exit()
            else:
                self.conn.commit()
                return self.last_inserted_id()
        else:
            return result['id']
         
    #insert into sample
    def updateSampleDecklist(self, item):
        sql = "INSERT INTO mtg_sample_decks (mtg_meta_name_id, used_total, card_name, mtg_decklist_where_id)"
        sql += " VALUES(%s, %s, %s, %s)"
        try:
            self.cursor.execute(sql, (
                item['mtg_meta_name_id'],
                item['used_total'],
                item['card_name'],
                item['mtg_decklist_where_id']
            ))
        except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
                sys.exit()
        else:
            self.conn.commit()
         
    #update mtg decklist (categorize)
    def updatCategory(self, item):
        sql = "UPDATE mtg_decklist SET meta_deck_name_id = %s WHERE id = %s AND delete_flag = 0"
        try:
            self.cursor.execute(sql, (
                item['meta_deck_name_id'],
                item['id']
            ))
        except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
                sys.exit()
        else:
            self.conn.commit()