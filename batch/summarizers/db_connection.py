#-*- coding: utf-8 -*-
import pymysql as MySQLdb
from setting import SUMMARY_SETTING, SCRAPY_SETTING
from common import send_error_mail

class summary():
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=SUMMARY_SETTING['SQL_HOST'],
            user=SUMMARY_SETTING['SQL_USER'],
            passwd=SUMMARY_SETTING['SQL_PASSWD'],
            db=SUMMARY_SETTING['SQL_DB'],
            charset=SUMMARY_SETTING['SQL_CHAR'],
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
        
    #insert inoto card weekly
    def putWeeklyBycard(self, item):
        sql = "SELECT COUNT(*) as count FROM mtg_card_weekly_use WHERE start = %s AND "
        sql += "end = %s AND format = %s AND mtg_card_main_id = %s AND country_id = %s"
        self.cursor.execute(sql, (
            item['start'],
            item['end'],
            item['format'],
            item['mtg_card_main_id'],
            item['country_id']
        ))
        
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_card_weekly_use (start, end, format, total_used, mtg_card_main_id, country_id)
                    VALUE(%s, %s, %s, %s, %s, %s)""",
                    (item['start'],
                    item['end'],
                    item['format'],
                    item['total_used'],
                    item['mtg_card_main_id'],
                    item['country_id']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
            else:
                self.conn.commit()
                
                
    def putMonthlyBycard(self, item):
        sql = "SELECT COUNT(*) as count FROM mtg_card_monthly_use WHERE start = %s AND "
        sql += "end = %s AND format = %s AND mtg_card_main_id = %s AND country_id = %s"
        self.cursor.execute(sql, (
            item['start'],
            item['end'],
            item['format'],
            item['mtg_card_main_id'],
            item['country_id']
        ))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_card_monthly_use (start, end, format, total_used, mtg_card_main_id, country_id)
                    VALUE(%s, %s, %s, %s, %s, %s)""",
                    (item['start'],
                    item['end'],
                    item['format'],
                    item['total_used'],
                    item['mtg_card_main_id'],
                    item['country_id']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
            else:
                self.conn.commit()
        
        
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
        
    #get list
    def getSummaryBycards(self, item):
        sql = "SELECT COUNT(detail.card_id) as total_used, detail.card_id as mtg_card_main_id"
        sql += " FROM mtg_decklist deck INNER JOIN mtg_tournament tour ON deck.tournament_id = tour.id AND tour.delete_flag = 0"
        sql += " INNER JOIN mtg_decklist_detail detail ON deck.id = detail.decklist_id AND detail.delete_flag = 0"
        sql += " INNER JOIN mtg_decklist_where ms ON detail.mtg_decklist_where_id = ms.id AND ms.delete_flag = 0"
        sql += " INNER JOIN mtg_format format ON tour.format = format.id"
        sql += " INNER JOIN mtg_card mc ON detail.card_id = mc.id"
        sql += " WHERE deck.delete_flag = 0 AND tour.start >= %s AND tour.end <= %s"
        sql += " AND tour.format = %s AND tour.country_id = %s GROUP BY detail.card_id ORDER BY COUNT(detail.card_id) desc"
        self.cursor.execute(sql, (
            item['start'], 
            item['end'], 
            item['format'],
            item['country_id']
        ))
        return self.cursor.fetchall()