#-*- coding: utf-8 -*-
import pymysql as MySQLdb
from setting import SCRAPY_SETTING

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
        
        
    def getCounts(self):
        sql = "SELECT mtg_meta_name.id AS meta_id ,date_format(mtg_tournament.start, '%Y-%m-%d') AS start"
        sql += " ,date_format(mtg_tournament.end, '%Y-%m-%d') AS end ,mtg_meta_name.name AS name"
        sql += " ,count(mtg_meta_name.name) AS count FROM mtg_decklist"
        sql += " INNER JOIN mtg_tournament ON mtg_tournament.id = mtg_decklist.tournament_id"
        sql += " INNER JOIN mtg_meta_name ON mtg_meta_name.id = mtg_decklist.meta_deck_name_id"
        sql += " WHERE mtg_meta_name.delete_flag = 0 GROUP BY date_format(mtg_tournament.start, '%Y-%m-%d'), mtg_meta_name.name"
        
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def getMtgDeckCountByDateAggregate(self):
        sql = "SELECT * FROM mtg_deck_count_by_date_aggregate"
        
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def insertOrUpdate(self, item):
        sql = "INSERT INTO mtg_deck_count_by_date_aggregate (meta_id, start, end, name, count) "
        sql += "VALUES (%s, %s, %s, %s, %s) on duplicate key update count=" + str(item['count'])
        
        try:
            self.cursor.execute(sql, 
                (str(item['meta_id']),
                str(item['start']),
                str(item['end']),
                str(item['name']),
                str(item['count'])))
        except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
        else:
            self.conn.commit()
        