#-*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from setting import USER_AGENT
from db_connection import MySQLPipeline
import re, sys
import fake_useragent
import requests

search_word = '千葉県'
search_region = 'Chiba'

#DB
DB = MySQLPipeline()

#user-agent
ua = fake_useragent.UserAgent()

#to do class def化すること

#下準備
url = "http://locator.wizards.com/"
des_cap = dict(DesiredCapabilities.PHANTOMJS)
des_cap["phantomjs.page.settings.userAgent"] = (USER_AGENT)
driver = webdriver.PhantomJS(desired_capabilities=des_cap)
driver.get(url)

#search
try:
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'search_box'))
    )
    #都道府県ごとにに入力して、英語表記をjsに入れればおk？
    search_box.send_keys(search_word)
    driver.find_element(By.ID, 'search-btn').click()
except Exception as e:
    #to do log mail機能にしたい
    print("no search box!")
    print('=== エラー内容 ===')
    print('type:' + str(type(e)))
    driver.quit()
    sys.exit()

try:
    element = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, 'showMoreResultsLink'))
    )
except Exception as e:
    print("something went really wrong!")
    print(e)
    driver.quit()
    sys.exit()

#読み込みエラー対策
try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="showMoreResultsLink"]'))
    )
except TimeoutException:
    original_script = driver.find_element(By.XPATH)

#clcicking more results
while True:
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="showMoreResultsLink"]'))
        )
        element.click()
        style = driver.find_element_by_xpath('//*[@id="showMoreResultsLink"]').get_attribute('outerHTML')
        check = style.find('style="display: inline;"')
        if check is not -1:
            break
    except Exception as e:
        #to do log mail機能にしたい
        print("something went really wrong!")
        print(e)
        driver.quit()
        sys.exit()
    except StaleElementReferenceException:
        break

#obtaining all links
try:
    links = []
    links = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#locationContainer > div > div.result-info > a'))
    )
except TimeoutException:
    #to do log mail機能にしたい
    print("oh my god! can't find locations!")
    driver.quit()
    sys.exit()

#formatting all search result
for link in links:
    try:
        driver.get(link.get_attribute("href"))
    except:
        #to do log mail機能にしたい
        pprint(link.get_attribute("href"))
        print("oh my god! can't find any events!")
        driver.quit()
        sys.exit()
    try:
        script_url = driver.find_element(By.XPATH, '/html/body/script[13]').get_attribute('src')
        script = requests.get(script_url).text
        target = 'addr = event.Address;'
        replacer = 'addr = event.Address; addr.StateProvinceCode = ' + search_region
        #new_script = 'document.write(<script type="text\/javascript">' + script.replace(target, replacer, 1) + '<\/script>)'
        #driver.execute_script(new_script)
        new_script = script.replace(target, replacer, 1)
        driver.execute_script(new_script)
        events = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="event-table-content"]/dl[not(contains(@style, "display:none"))]'))
        )
    except TimeoutException:
        print("oh my god! can't obtain the script!")
        driver.quit()
        sys.exit()
    except StaleElementReferenceException:
        print("failed due to locator's bug")
        print(link)
        continue
    except Exception as e:
        #to do log mail機能にしたい
        print("unknown bug")
        print('=== エラー内容 ===')
        print('type:' + str(type(e)))
        print('e自身:' + str(e.args))
        driver.quit()
        sys.exit()

    #obtaining scheduals
    #data formatting for db insertation
    listing = []
    for event in events:
        pprint(event)
        driver.quit()
        sys.exit()
        
        listing = {}
        try:
            location_html = event.find_element_by_xpath('.//dd[@class="event-address"]').get_attribute('innerHTML')
            result = re.sub(r'<a .*./a>','',location_html)
            location = re.sub(r'<br>',' ',result).strip()
            listing = {
                'date':event.find_element_by_xpath('.//dd[@class="date"]/span').get_attribute('innerHTML'),
                'type':event.find_element_by_xpath('.//dd[@class="event-title"]/span').get_attribute('innerHTML'),
                'store':event.find_element_by_xpath('.//dd[@class="event-address"]/a').get_attribute('innerHTML'),
                'location':location,
                'format':event.find_element_by_xpath('.//dd[@class="event-legacy"]').get_attribute('innerHTML'),
                'email':event.find_element_by_xpath('.//dd[@class="event-mail"]/a').get_attribute('innerHTML')   
            }
            DB.store_process(listing)
        except StaleElementReferenceException:
            continue
driver.quit()
sys.exit()