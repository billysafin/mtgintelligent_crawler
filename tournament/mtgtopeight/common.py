from db_connection import MySQLPipeline
import urllib.request
from email.mime.text import MIMEText
import smtplib
import re

from selenium.common.exceptions import NoSuchElementException
#DB
DB = MySQLPipeline()

def getStartingQueryE():
    return DB.get_starting_query_e()

def checkURL(url):
    try:
        f = urllib.request.urlopen(url)
        f.close()
        return True
    except urllib.request.HTTPError:
        return None
    
#要素が存在するかのチェック
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return None
    return True

#cardを登録
def insert_card(card):
    return DB.mtg_card_process(card)

def insert_tour(tour):
    return DB.tournament_process(tour)

def insert_player(player):
   return DB.player_process(player)

def player_record_process(record):
    return DB.player_record_process(record)
    
def meta_name_process(meta_info):
    return DB.meta_name_process(meta_info)
    
def mtg_decklist_process(list):
    return DB.mtg_decklist_process(list)
    
def mtg_decklist_detail_process(detail):
    return DB.mtg_decklist_detail_process(detail)

#decklist
def get_decklist(driver):
    main = []
    side = []
    
    flag_side = None
    tds = driver.find_elements_by_xpath('//html/body/div[3]/div/table/tbody/tr/td[2]/table[2]/tbody/tr/td/table/tbody/tr/td[@valign="top"]')
    for td in tds:
        trs = td.find_elements_by_xpath('.//table/tbody/tr')
        
        for tr in trs:
            line = tr.find_element_by_xpath('.//td').get_attribute('innerText').strip()
            if re.match(r'SIDEBOARD', line) and flag_side is None:
                flag_side = True;
                continue
            elif re.search(r'COMMANDER', line) or re.search(r'OTHER SPELLS', line) or re.search(r'LANDS', line) or re.search(r'CREATURES', line) or re.search('INSTANTS and SORC', line):
                continue
            else:
                detail = tr.find_element_by_xpath('.//td/div').get_attribute('innerText')
                total = re.search(r'^[0-9]{1,}\s', detail)
                name = re.sub(total.group(), '', detail).strip()
                total = total.group().strip()
                
                card_id = insert_card(name)
                
                use_card = {
                    "name"    : name, 
                    "count"   : total,
                    "card_id" : card_id
                }
                
                if flag_side is not None:
                    side.append(use_card)
                else:
                    main.append(use_card)
                    
    return {
        "main"  : main
        ,"side" : side
    }
    
def get_related(driver, checked_players):
    xpath = '//*[@id="top8_list"]/div'
    if check_exists_by_xpath(driver, xpath) == None:
        xpath = '//html/body/div[3]/div/table/tbody/tr/td[1]/div/div'
        if check_exists_by_xpath(driver, xpath) == None:
            return None
        
        if check_exists_by_xpath(driver, xpath + '/select/option') is not None:
            return None
    
    divs = driver.find_elements_by_xpath(xpath)
    links = []
    for div in divs:
        player = div.find_element_by_xpath('.//div[3]').get_attribute('innerText')
        
        if player in checked_players:
            continue
        
        links.append(div.find_element_by_xpath('.//div[2]/a').get_attribute("href").strip())
    return links

#mail
def send_mail(args, date):
    msg = MIMEText('ERROR: ' + '\n'.join(args))
    msg['Subject'] = 'MtgIntelligence Error mtg top 8'
    msg['From']    = 'crawler@mtgintelligence.com'
    msg['To']      = 'billysafina@yahoo.co.jp'

    s = smtplib.SMTP() 
    s.connect()
    s.sendmail(msg['From'], ['billysafina@yahoo.co.jp'], msg.as_string() )
    s.close()