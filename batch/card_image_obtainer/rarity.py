#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import pymysql as MySQLdb
import requests
import hashlib
import subprocess
import os
import re
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import gc

class MySQLPipeline():
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

    def updateRarity(self, set_id, setNumber, rarity_code):
        sql = 'UPDATE  mtg_card_image SET rarity = "' + str(rarity_code) + '" WHERE '
        sql += 'set_number = "' + str(setNumber) + '" AND edition_id = "' + str(set_id) + '"'
        try:
            self.cursor.execute(sql)
        except MySQLdb.Error as e:
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True

    def checkNeedUpdate(self, set_id, setNumber):
        sql = 'SELECT rarity FROM mtg_card_image WHERE set_number = "'
        sql += str(setNumber) + '" AND edition_id = "' + str(set_id) + '"'

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        need = False
        for row in rows:
            if row['rarity'] == 0:
                need = True

        return need

    def getAllSets(self):
        sql = "SELECT * FROM mtg_edition WHERE delete_flag = 0 AND obtained_flag = 1 AND is_booster = 1"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

DOMAIN = "https://magiccards.info"
DB = MySQLPipeline()

def processPage(driver, target):
    try:
        page = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, target))
        )
        return page
    except (TimeoutException, NoSuchElementException):
        return None
    except:
        return None


def getAllSets():
    return getAllShortNames()

def process(setShort, setId, setNumber):
    gc.collect()

    url = DOMAIN + '/' + setShort + '/en/' + str(setNumber) + '.html'
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')

    driver = webdriver.Chrome(chrome_options=opts)
    driver.get(url)

    if DB.checkNeedUpdate(setId, setNumber) == False:
        print(url)

        page = processPage(driver, '/html/body/h1')
        if page is not None:
            h1_tag = driver.find_element_by_xpath('/html/body/h1').get_attribute('innerHTML')
            if h1_tag == 'Your query did not match any cards.':
                driver.close()
                driver.quit()
                return None
        else:
            return False

    exists = processPage(driver, '/html/body/table[3]/tbody/tr/td[3]/small/b[2]')
    if exists is None:
        driver.close()
        driver.quit()
        return None

    rarity = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/small/b[2]').get_attribute('innerHTML')
    rarity = re.sub(r'^.*\(', '', rarity)
    rarity = re.sub(r'\).*$', '', rarity)

    if rarity == 'Mythic Rare':
        rarity_code = 1
    elif rarity == 'Rare':
        rarity_code = 2
    elif rarity == 'Uncommon':
        rarity_code = 3
    elif rarity == 'Common':
        rarity_code = 4
    elif rarity == 'Special':
        rarity_code = 5
    else:
        rarity_code = 6

    result = DB.updateRarity(setId, setNumber, rarity_code)

    driver.close()
    driver.quit()
    return True

if __name__ == '__main__':
    mtgSets = DB.getAllSets()

    for set in mtgSets:
        i = 1
        while True:
            result = process(set['short'], set['id'], i)
            if result is None:
                break
            i += 1

    try:
        subprocess.call("pgrep chrome | xargs kill -9")
    except:
        pass
