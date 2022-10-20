# -*- coding: utf-8 -*-

import pymysql as MySQLdb
from scrapy.conf import settings

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# connect to the MySQL server
class WizardsPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLStorePipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=settings['SQL_HOST'],
            user=settings['SQL_USER'],
            passwd=settings['SQL_PASSWD'],
            db=settings['SQL_DB'],
            charset=settings['SQL_CHAR'],
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql = "SELECT COUNT(*) as count FROM mtg_reading WHERE published = %s AND title = %s"
        self.cursor.execute(sql, (item['published'], item['title']))
        result = self.cursor.fetchall()
        if result[0]['count'] == 0 and item["title"] != "" and item["link"] != "":
            try:
                self.cursor.execute("""INSERT INTO mtg_reading (published, title, link, date, source_from)
                    VALUE(%s, %s, %s, %s, %s)""",
                    (item['published'],
                    item['title'],
                    item['link'],
                    item['date'],
                    item['source_from']))
                self.conn.commit()
            except MySQLdb.Error as e:
                print('Error %d: %s' % (e.args[0], e.args[1]))
                self.cursor.rollback()
        return item