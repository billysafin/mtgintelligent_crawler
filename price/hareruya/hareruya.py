#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from db_connection import MySQLPipeline
import re
from urls import urls
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import gc
import sys

LANGS = ['JN','JP', 'EN']
STORE_ID = 2


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


def main(set_id, url, lang, edition_id):
    true_url = url + str('{0:06d}'.format(int(set_id))) + lang

    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.binary_location = '/usr/bin/google-chrome'

    print(true_url)

    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=opts)
    driver.get(true_url)

    page = processPage(driver, '//*[@id="item_info_right"]/form[1]/div[1]/div[1]/div[1]/span')

    print("page")
    print(page)

    if page is None:
        return 'ERROR'

    #get card id
    card_id = DB.getCardId(set_id, edition_id)

    print("card_id")
    print(card_id)

    if card_id is None:
        return 'ERROR'

    #price
    price = driver.find_element_by_xpath('//*[@id="item_info_right"]/form[1]/div[1]/div[1]/div[1]/span').get_attribute('innerText')
    price = re.sub(r',', '', re.sub('￥', '', re.sub(r'¥', '', price)))

    card_data = {
        "store_id"          : STORE_ID,
        "mtg_edition_id"    : edition_id,
        "mtg_card_id"       : card_id,
        "currency_id"       : 15,
        "price"             : price,
        "url"               : true_url
    }

    print(card_data)

    result = DB.InsertUpdatePrice(card_data)
    return result

if __name__ == '__main__':
    for edition_id in urls.keys():
        for lang in LANGS:
            set_id = 1
            while True:
                error = False
                gc.collect()

                error = main(set_id, urls[edition_id], lang, edition_id)
                if error is not None:
                    break
                set_id += 1
