# -*- coding: utf-8 -*-
#scrapyではなくseleniumで取得しています
import datetime
import pymysql as MySQLdb
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="grid-wrapper"]/div'))
        )
        return articles
    except:
        return False

def scrapying(driver):
    item = {}
    a_tag = driver.find_element_by_xpath('.//h2/a')
    item ['link'] = a_tag.get_attribute("href")
    item ['title'] = a_tag.get_attribute('innerHTML')
    published = driver.find_element_by_xpath('.//p[@class="post-meta"]').get_attribute('innerHTML')
    published = "".join(published)[1:27]
    published = re.sub(r'Publishedon', '', re.sub('\s+', '', published))
    item ['published'] = re.sub('日', '', re.sub(u'月', '-' ,re.sub(u'年', '-', published)))
    aDate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    item ['date'] = aDate.strftime("%Y/%m/%d %H:%M:%S")
    item['source_from'] = 8
    return item

def inserting(item):
    #DB
    if re.sub('/', '-', item['published']) == datetime.date.today().strftime('%Y-%m-%d'):
        return True
    
    if item['published'] == '0000-00-00':
        return False
    
    DB = MySQLStorePipeline()
    try:
        DB.process(item)
        return True
    except:
        return False


#下準備
url = "http://mtg-news.net/"
des_cap = dict(DesiredCapabilities.PHANTOMJS)
des_cap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36")
driver = webdriver.PhantomJS(desired_capabilities=des_cap)
driver.get(url)

#1ページ目
articles = processPage(driver)
if articles == False:
    print("error has occured #1")
    driver.quit()
    sys.exit()

for article in articles:
    item = scrapying(article)
    result = inserting(item)
    if result == False:
        print("error has occured during inserting to the db #1")
        driver.quit()
        sys.exit()

#2ページ目以降の処理
max_pagination = driver.find_element_by_xpath('//*[@id="grid-pagination"]/a[6]').get_attribute('innerHTML')

count = int("2")
while count < int(max_pagination):
    new_url = url + 'page/' + str(count) + '/'
    driver.get(new_url)
    articles = processPage(driver)
    if articles == False:
        print("error has occured #2")
        driver.quit()
        sys.exit()

    for mini_article in articles:
        mini_item = scrapying(mini_article)
        result = inserting(mini_item)
        if result == False:
            print("error has occured during inserting to the db #2")
            driver.quit()
            sys.exit()
    count += 1
    
print('============finised scrspying=================')