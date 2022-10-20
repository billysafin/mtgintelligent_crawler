# -*- coding: utf-8 -*-
import pymysql as MySQLdb
from setting import SQL_SETTING

class MySQLPipeline():
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=SQL_SETTING['SQL_HOST'],
            user=SQL_SETTING['SQL_USER'],
            passwd=SQL_SETTING['SQL_PASSWD'],
            db=SQL_SETTING['SQL_DB'],
            charset=SQL_SETTING['SQL_CHAR'],
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

    #store locator
    def store_process(self, item):
        sql = "SELECT COUNT(*) as count FROM mtg_events WHERE date = %s AND type = %s AND store = %s AND delete_flag = 0"
        self.cursor.execute(sql, (item['date'], item['type'], item['store']))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_events (date, type, store, location, format, email)
                    VALUE(%s, %s, %s, %s, %s, %s)""",
                    (item['date'],
                    item['type'],
                    item['store'],
                    item['location'],
                    item['format'],
                    item['email']))
                self.conn.commit()
            except MySQLdb.Error as e:
                print('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
            else:
                self.conn.commit()

    #player
    def player_process(self, player):
        sql = "SELECT COUNT(*) as count, id FROM mtg_player WHERE name = %s AND delete_flag = 0"
        self.cursor.execute(sql, (player))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_player (name) VALUE(%s)""", (player))
            except MySQLdb.Error as e:
                self.conn.rollback()
                print('Error %d: %s' % (e.args[0], e.args[1]))
            else:
                self.conn.commit()
                return self.last_inserted_id()
        elif result['count'] == 1:
            return result['id']

    #tournament
    def tournament_process(self, tour):
        sql = "SELECT COUNT(*) as count, id FROM mtg_tournament " 
        sql += " WHERE name = %s AND format = %s AND start = %s AND delete_flag = 0"
        self.cursor.execute(sql, (tour['name'], tour['format'], tour['start']))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_tournament (start, end, country_id, name, rounds, format) 
                VALUE(%s, %s, %s, %s, %s, %s)""", (
                tour['start'],
                tour['end'],
                tour['country_id'],
                tour['name'],
                tour['rounds'],
                tour['format']
                ))
            except MySQLdb.Error as e:
                self.conn.rollback()
                print('Error %d: %s' % (e.args[0], e.args[1]))
            else:
                self.conn.commit()
                return self.last_inserted_id()
        elif result['count'] == 1:
            return result['id']

    #player record
    def player_record_process(self, record):
        sql = "SELECT COUNT(*) as count FROM mtg_player_record "
        sql += "WHERE player_id = %s AND tournament_id = %s AND delete_flag = 0"
        self.cursor.execute(sql, (record['player_id'], record['tournament_id']))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_player_record (
                player_id, tournament_id, rank, omwp, gwp, ogwp, points)
                VALUE(%s, %s, %s, %s, %s, %s, %s)""", (
                record['player_id'],
                record['tournament_id'],
                record['rank'],
                record['omwp'],
                record['gwp'],
                record['ogwp'],
                record['points']
                ))
            except MySQLdb.Error as e:
                self.conn.rollback()
                print('Error %d: %s' % (e.args[0], e.args[1]))
            else:
                self.conn.commit()

    #card
    def mtg_card_process(self, card):
        sql = "SELECT COUNT(*) as count, id FROM mtg_card "
        sql += "WHERE name = %s AND delete_flag = 0"
        self.cursor.execute(sql, (card['name']))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_card (
                name, url)
                VALUE(%s, %s)""",(
                card['name'],
                card['url']
                ))
            except MySQLdb.Error as e:
                self.conn.rollback()
                print('Error %d: %s' % (e.args[0], e.args[1]))
            else:
                self.conn.commit()
                return self.last_inserted_id()
        elif result['count'] == 1:
            return result['id']

    #decklist
    def mtg_decklist_process(self, list):
        sql = "SELECT COUNT(*) as count, id FROM mtg_decklist "
        sql += "WHERE player_id = %s AND tournament_id = %s AND delete_flag = 0"
        self.cursor.execute(sql, (list['player_id'], list['tournament_id']))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_decklist (
                player_id, tournament_id)
                VALUE(%s, %s)""",(
                list['player_id'],
                list['tournament_id']
                ))
            except MySQLdb.Error as e:
                self.conn.rollback()
                print('Error %d: %s' % (e.args[0], e.args[1]))
            else:
                self.conn.commit()
                return self.last_inserted_id()
        else:
            return result['id']

    #decklist
    def mtg_decklist_detail_process(self, list):
        sql = "SELECT COUNT(*) as count, id FROM mtg_decklist_detail "
        sql += "WHERE decklist_id = %s AND delete_flag = 0"
        sql += " AND mtg_decklist_where_id = %s AND used_amount = %s AND card_id = %s"
        self.cursor.execute(sql, (list['decklist_id'], list['mtg_decklist_where_id'], list['used_amount'], list['card_id']))
        result = self.cursor.fetchone()
        if result['count'] == 0:
            try:
                self.cursor.execute("""INSERT INTO mtg_decklist_detail (
                decklist_id, mtg_decklist_where_id, used_amount, card_id)
                VALUE(%s, %s, %s, %s)""",(
                list['decklist_id'],
                list['mtg_decklist_where_id'],
                list['used_amount'],
                list['card_id']
                ))
            except MySQLdb.Error as e:
                self.conn.rollback()
                print('Error %d: %s' % (e.args[0], e.args[1]))
            else:
                self.conn.commit()

    #get player_id
    def get_player_id(self, player):
        sql = "SELECT id FROM mtg_player WHERE name = %s AND delete_flag = 0"
        self.cursor.execute(sql, (player))
        result = self.cursor.fetchone()
        return result['id']
    
    #get tour_id
    def get_tour_id(self, tour):
        sql = "SELECT id FROM mtg_tournament" 
        sql += " WHERE name = %s AND format = %s AND start = %s AND delete_flag = 0"
        self.cursor.execute(sql, (tour['name'], tour['format'], tour['start']))
        result = self.cursor.fetchone()
        return result['id']