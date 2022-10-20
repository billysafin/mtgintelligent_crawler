# -*- coding: utf-8 -*-
#scrapyではなくseleniumで取得しています
import datetime
import pymysql as MySQLdb
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#db接続
class MySQLStorePipeline():
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
    
    def process(self, item):
        sql = "SELECT COUNT(*) as count FROM mtg_reading WHERE published = %s AND title = %s"
        self.cursor.execute(sql, (item['published'], item['title']))
        result = self.cursor.fetchall()
        if result[0]['count'] == 0:
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

def processPage(driver):
    #全てが表示されるまで待つ
    try:
        articles = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="topicsside"]/ul/li'))
        )
        return articles
    except:
        return False

def scrapying(driver):
    item = {}
    item ['link'] = driver.find_element_by_xpath('.//p[@class="txt"]/a').get_attribute("href")
    item ['title'] = driver.find_element_by_xpath('.//p[@class="txt"]/a').get_attribute("innerHTML")
    published = driver.find_element_by_xpath('.//p[@class="date"]').get_attribute('innerHTML')
    published = re.sub(r'月', '-', re.sub(r'年', '-', re.sub(r'日', '', published)))
    item ['published'] = published
    aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    item ['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
    item['source_from'] = 1
    return item

def inserting(item):
    #DB
    DB = MySQLStorePipeline()
    try:
        DB.process(item)
        return True
    except:
        return False


#下準備
url = "http://mtg-jp.com/reading/"
des_cap = dict(DesiredCapabilities.PHANTOMJS)
des_cap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36")
driver = webdriver.PhantomJS(desired_capabilities=des_cap)
driver.get(url)

articles = processPage(driver)
if articles == False:
    driver.quit()
    sys.exit()

for article in articles:
    item = scrapying(article)
    
    if item['title'] == '《巨森の予見者、ニッサ》スケッチアート＆コンセプトアート':
        continue
    
    if item['link'] == 'http://mtg-news.net/archives/17489':
        continue
    
    if item['published'] =='0000-00-00':
        continue
    
    yesterday = datetime.date.today() - datetime.timedelta(1),
    two_days_ago = datetime.date.today() - datetime.timedelta(2)
    date_check = [
        datetime.date.today().strftime('%Y-%m-%d'),
        yesterday[0].strftime('%Y-%m-%d'),
        two_days_ago.strftime('%Y-%m-%d')
    ]
    if item['published'] in date_check:
        result = inserting(item)
        if result == False:
            driver.quit()
            sys.exit()
