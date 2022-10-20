#-*- coding: utf-8 -*-
import pymysql as MySQLdb
import sys
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

    def last_inserted_id(self):
         sql = "SELECT LAST_INSERT_ID() as lid"
         self.cursor.execute(sql)
         id = self.cursor.fetchone()
         return id['lid']

    def getAllSets(self):
        sql = "SELECT * FROM mtg_edition WHERE delete_flag = 0 AND obtained_flag = 0"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def getimageIdsBycardId(self, cardId):
        sql = "SELECT i.id as lids FROM mtg_card_image i INNER JOIN mtg_card c ON i.mtg_card_id = c.id WHERE c.id = " + str(cardId)
        self.cursor.execute(sql)
        ids = self.cursor.fetchall()
        
        if ids is None:
            return None
        else:
            if len(ids) >= 2:
                return True
            elif len(ids) == 1:
                return False
            elif len(ids) == 0:
                return None
            else:
                return None

    def getCardIdByName(self, cardName):
        sql = 'SELECT id as lid FROM mtg_card WHERE name = "' + str(cardName) + '" and delete_flag = 0'
        self.cursor.execute(sql)
        id = self.cursor.fetchone()

        if id is None:
            sql = 'INSERT INTO mtg_card (name) VALUES ("' + str(cardName) + '")'
            self.cursor.execute(sql)
            self.cursor.fetchone()
            lid = self.last_inserted_id()
            
            return lid

        return id['lid']

    def updateImage(self, cardId, file_name, langId, setId, setNumber):
        sql = 'INSERT INTO mtg_card_image (mtg_card_id, edition_id, country_id, image, set_number) VALUES (' + str(cardId) + ',' + str(setId)  + ',' + str(langId) + ',"' + str(file_name) + '", ' + str(setNumber) + ')'
        try:
            self.cursor.execute(sql)
        except MySQLdb.Error as e:
            self.conn.rollback()
            return None
        else:
            self.conn.commit()
            return self.last_inserted_id()
        
    def updateObtainedFoag(self, short):
        sql = 'UPDATE mtg_edition SET obtained_flag = 1 WHERE short = "' + short + '"'
        try:
            self.cursor.execute(sql)
        except MySQLdb.Error as e:
            self.conn.rollback()
        else:
            self.conn.commit()