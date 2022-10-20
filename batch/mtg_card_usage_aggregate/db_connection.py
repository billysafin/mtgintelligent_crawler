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

    def getStats(self):
        sql = "SELECT mmn.id as meta_id, mdd.mtg_decklist_where_id as where_board,"
        sql += " mdd.used_amount as amount, mdd.card_id as card_id, count(md.player_id) as player_count"
        sql += " ,DATE_FORMAT(mt.start, '%Y-%m') as date"
        sql += " FROM mtg_decklist md INNER JOIN mtg_meta_name mmn ON md.meta_deck_name_id = mmn.id"
        sql += " INNER JOIN mtg_decklist_detail mdd ON md.id = mdd.decklist_id "
        sql += " INNER JOIN mtg_tournament mt ON md.tournament_id = mt.id"
        sql += " WHERE md.delete_flag = 0 AND mmn.delete_flag = 0 AND mdd.delete_flag = 0 AND mt.delete_flag = 0"
        sql += " GROUP BY meta_id, where_board, amount, card_id, DATE_FORMAT(mt.start, '%Y-%m')"

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def getTotalPlayersByMetaId(self, item, date_from):
        sql = "SELECT count(md.player_id) as total_players FROM mtg_decklist md"
        sql += " INNER JOIN mtg_meta_name mmn ON md.meta_deck_name_id = mmn.id"
        sql += " INNER JOIN mtg_tournament mt ON md.tournament_id = mt.id"
        sql += " WHERE md.delete_flag = 0 AND mmn.delete_flag = 0 AND mt.delete_flag = 0"
        sql += " AND mmn.id = " + str(item) + " AND DATE_FORMAT(mt.start, '%Y-%m') = '" + str(date_from) + "'"

        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def insertOrUpdate(self, item):
        date = str(item['date']) + "-01"

        sql = "INSERT INTO mtg_card_usage_aggregate (meta_id, card_id, amount, where_board, player_count, total_players, date, delete_flag)"
        sql += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update"
        sql += " player_count='" + str(item['player_count']) + "', total_players='" + str(item['total_players']) + "'"
        sql += ", delete_flag='" + str(item['delete_flag']) + "', date='" + date + "'"
        try:


            self.cursor.execute(sql,
                (str(item['meta_id']),
                str(item['card_id']),
                str(item['amount']),
                str(item['where_board']),
                str(item['player_count']),
                str(item['total_players']),
                date,
                str(item['delete_flag']))),
        except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
        else:
            self.conn.commit()
