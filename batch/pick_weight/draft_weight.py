#!/usr/local/bin/python
# -*- coding: utf-8 -*-

weightTxt = "./draft_weight.txt"
SQL_SETTING = {
    'SQL_DB'    :'scrapy',
    'SQL_HOST'  :'10.20.0.1',
    'SQL_USER'  :'mtgstats',
    'SQL_PASSWD':'mtgstats',
    'SQL_CHAR'  :'utf8'
}

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

     def getCardIdByName(cardName):
         sql = "SELECT id FROM mtg_card WHERE name = %s and delete_flag = 0"
         self.cursor.execute(sql)
         id = self.cursor.fetchone()
         return id['lid']

     def updateDraftPickWeight(mtg_card_id, edition_id, pick_weight):
         sql = "INSERT INTO mtg_draft_pick_weight (mtg_card_id, edition_id, pick_weight)"
         sql += " VALUES (%s,%s,%s)"

         try:
             self.cursor.execute(sql,
             (mtg_card_id,
             edition_id,,
             pick_weight))
         except MySQLdb.Error as e:
             self.conn.rollback()
             return None
         else:
             self.conn.commit()
             return self.last_inserted_id()

def main():
    f = open(weightTxt)
    lines = f.readlines()
    f.close()

    failed = ''
    for line in lines:
        card = line.split(',')

        cardId = getCardIdByName(card[1])

        if cardId is None:
            failed += line + '\n\r'
            continue

        result = updateDraftPickWeight(cardId, card[0], card[2])

        if result is None:
            failed += line + '\n\r'
            continue

    print(failed)

if __name__ == '__main__':
    main()
