#-*- coding: utf-8 -*-
import pymysql as MySQLdb
import sys
from setting import SQL_SETTING
from common import send_error_mail

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

    #get list to be updated
    def getAllUpdateList(self):
        sql = "SELECT id, name FROM mtg_card WHERE delete_flag = 0 AND obtained_flag = 0 "
        sql += " ORDER BY id"
        #sql += "AND (url <> '' OR url <> NULL) ORDER BY id"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    #insert inoto main
    def putCardInfoMain(self, item):
        sql = "SELECT id FROM mtg_card_main WHERE mtg_card_id = %s AND delete_flag = 0"
        self.cursor.execute(sql, (item['mtg_card_id']))
        result = self.cursor.fetchone()
        if result is None:
            try:
                self.cursor.execute("""INSERT INTO mtg_card_main (mtg_card_id, color, converted_mana_cost, mana_cost, type, power, thoughness, loyalty, text_en, second_card_form)
                    VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['mtg_card_id'],
                    item['color'],
                    item['converted_mana_cost'],
                    item['mana_cost'],
                    item['type'],
                    item['power'],
                    item['thoughness'],
                    item['loyalty'],
                    item['text_en'],
                    item['second_card_form']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
                sys.exit()
            else:
                self.conn.commit()
                return self.last_inserted_id()
        else:
            return result['id']

    #insert into jp
    def putCardInfoMainJp(self, item):
        sql = "SELECT id FROM mtg_card_main_jp WHERE mtg_card_main_id = %s AND name_jp = %s AND delete_flag = 0"
        self.cursor.execute(sql, (
            item['mtg_card_main_id'],
            item['name_jp']
        ))
        result = self.cursor.fetchone()
        if result is None:
            try:
                if 'text_jp' not in item:
                    item['text_jp'] = '';

                if 'flavor_text_jp' not in item:
                    item['flavor_text_jp'] = '';

                self.cursor.execute("""INSERT INTO mtg_card_main_jp
                    (mtg_card_main_id, name_jp, text_jp, flavor_text_jp)
                    VALUE(%s, %s, %s, %s)""",
                    (item['mtg_card_main_id'],
                    item['name_jp'],
                    item['text_jp'],
                    item['flavor_text_jp']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
            else:
                self.conn.commit()
                return self.last_inserted_id()
        else:
            return result['id']

    #insert inoto main second
    def putCardInfoMainSecond(self, item):
        sql = "SELECT id FROM mtg_card_main_second WHERE mtg_card_main_id = %s AND delete_flag = 0"
        self.cursor.execute(sql, (item['mtg_card_main_id']))
        result = self.cursor.fetchone()
        if result is None:
            try:
                self.cursor.execute("""INSERT INTO mtg_card_main_second (mtg_card_main_id, color, converted_mana_cost, mana_cost, type, power, thoughness, loyalty, text_en)
                    VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['mtg_card_main_id'],
                    item['color'],
                    item['converted_mana_cost'],
                    item['mana_cost'],
                    item['type'],
                    item['power'],
                    item['thoughness'],
                    item['loyalty'],
                    item['text_en']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
                sys.exit()
            else:
                self.conn.commit()
                return self.last_inserted_id()
        else:
            return result['id']

    #insert inoto main second
    def putCardInfoMainJpSecond(self, item):
        sql = "SELECT id FROM mtg_card_main_second_jp WHERE mtg_card_main_second_id = %s AND delete_flag = 0"
        self.cursor.execute(sql, (
            item['mtg_card_main_second_id']
        ))
        result = self.cursor.fetchone()
        if result is None:
            try:
                if 'text_jp' not in item:
                    item['text_jp'] = '';

                if 'flavor_text_jp' not in item:
                    item['flavor_text_jp'] = '';

                self.cursor.execute("""INSERT INTO mtg_card_main_second_jp
                    (mtg_card_main_second_id, text_jp, flavor_text_jp)
                    VALUE(%s, %s, %s)""",
                    (item['mtg_card_main_second_id'],
                    item['text_jp'],
                    item['flavor_text_jp']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
                sys.exit()
            else:
                self.conn.commit()
                return self.last_inserted_id()
        else:
            return result['id']

    #insert inoto sub
    def putCardInfoSub(self, item):
        sql = "SELECT id FROM mtg_card_sub WHERE mtg_card_main_id = %s AND delete_flag = 0"
        self.cursor.execute(sql, (item['mtg_card_main_id']))
        result = self.cursor.fetchone()
        if result is None:
            try:
                self.cursor.execute("""INSERT INTO mtg_card_sub (mtg_card_main_id, flavor_text, artist, rarity, set_number)
                    VALUE(%s, %s, %s, %s, %s)""",
                    (item['mtg_card_main_id'],
                    item['flavor_text'],
                    item['artist'],
                    item['rarity'],
                    item['set_number']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
            else:
                self.conn.commit()

    #insert inoto sub set
    def putCardInfoSubSetName(self, item):
        sql = "SELECT id FROM mtg_card_sub_set_name WHERE mtg_card_main_id = %s AND set_name = %s AND delete_flag = 0"
        self.cursor.execute(sql, (
            item['mtg_card_main_id'],
            item['set_name']
        ))
        result = self.cursor.fetchone()
        if result is None:
            try:
                self.cursor.execute("""INSERT INTO mtg_card_sub_set_name (mtg_card_main_id, set_name)
                    VALUE(%s, %s)""",
                    (item['mtg_card_main_id'],
                    item['set_name']))
            except MySQLdb.Error as e:
                send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
                self.conn.rollback()
            else:
                self.conn.commit()

    #update second_cars_form
    def UpdateSecondCardForm(self, item):
        try:
            sql = "UPDATE mtg_card_main SET second_card_form = %s WHERE id = %s"
            self.cursor.execute(sql, (
                item['second_card_form'],
                item['id']
            ))
        except MySQLdb.Error as e:
            send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
            self.conn.rollback()
        else:
            self.conn.commit()

    #update obtain flag
    def updateObtainedFlag(self, id, image_jp, image_en):
        try:
            sql = "UPDATE mtg_card SET obtained_flag = 1 WHERE id = %s"
            self.cursor.execute(sql, (id))

            sql = "SELECT id FROM mtg_card_main WHERE mtg_card_id = %s"
            main_id = self.cursor.execute(sql, (id))
        except MySQLdb.Error as e:
            print('Error %d: %s' % (e.args[0], e.args[1]))
            send_error_mail('Error %d: %s' % (e.args[0], e.args[1]))
            self.conn.rollback()
        else:
            self.conn.commit()
