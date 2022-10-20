#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from db_connection import MySQLPipeline
import requests
import hashlib
import subprocess
import os
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import gc

DOMAIN = "https://magiccards.info"
LANGS = ['en', 'jp']
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
    cardName = ''

    for lang in LANGS:
        gc.collect()

        url = DOMAIN + '/' + setShort + '/' + lang + '/' + str(setNumber) + '.html'

        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--no-sandbox')

        driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=opts)
        driver.get(url)

        page = processPage(driver, '/html/body/script')
        if page is None:
            driver.close()
            driver.quit()
            return None

        exists = processPage(driver, '/html/body/table[3]/tbody/tr/td[1]/img')
        if exists is None:
            driver.close()
            driver.quit()
            return None

        imgSrc = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[1]/img').get_attribute('src')

        if lang == 'en':
            exists = processPage(driver, '/html/body/table[3]/tbody/tr/td[1]/img')
            if exists is None:
                driver.close()
                driver.quit()
                return None

            cardName = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[1]/img').get_attribute('alt')

        cardId = DB.getCardIdByName(cardName)
        isExists = DB.getimageIdsBycardId(cardId)
        if lang == 'en':
            if isExists == False:
                driver.close()
                driver.quit()
                continue
            elif isExists == True:
                driver.close()
                driver.quit()
                break

        res = requests.get(imgSrc, stream=True)
        file_name = ''
        if res.status_code == 200:
            tdatetime = dt.now()
            tstr = tdatetime.strftime('%Y%m%d%H%M%S%f')
            file_name = cardName.lower() + '_' + lang + '_' + tstr
            file_name = hashlib.md5(file_name.encode('utf-8')).hexdigest() + '.png'

            with open(file_name, 'wb') as file:
              for chunk in res.iter_content(chunk_size=1048576):
                  file.write(chunk)
                  command = ['swift', 'upload', 'mtg_public', file_name, '-q', '-R', '3']
                  subprocess.call(command)
                  os.remove(file_name)

        if lang == 'en':
           langId = 3
        elif lang == 'jp':
           langId = 2
        else:
           langId = 4

        result = DB.updateImage(cardId, file_name, langId, setId, setNumber)

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
                DB.updateObtainedFoag(set['short'])
                break
            i += 1

    try:
        subprocess.call("pgrep chrome | xargs kill -9")
    except:
        pass
