#-*- coding: utf-8 -*-
from db_connection import MySQLPipeline
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from setting import USER_AGENT
from mtgsdk import Card
from card_processing import mainProcess, secondProcess
from common import getImage
import re
import sys
import gc

#DB
DB = MySQLPipeline()

def combineSplitCards(left, right):
    if 'name' in left:
        left['name'] = left['name'] + ' // ' + right['name']
    
    if 'colors' in left:
        left['colors'].append(right['colors'])
        
    if 'cmc' in left:
        left['cmc'] = left['cmc'] + right['cmc']
    
    if 'manaCost' in left:
        left['manaCost'] = left['manaCost'] + ' // ' + right['manaCost']
    
    if 'type' in left:
        left['type'] = left['type'] + ' // ' + right['type']
        
    if 'power' in left:
        left['power'] = left['power'] + ' // ' + right['power']
        
    if 'toughness' in left:
        left['toughness'] = left['toughness'] + ' // ' + right['toughness']
        
    if 'loyalty' in left:
        left['loyalty'] = left['loyalty'] + ' // ' + right['loyalty']
        
    if 'text' in left:
        left['text'] = left['text'] + ' // ' + right['text']
        
    return left
    
    
    return card_info

def _identifyTheCard(splited):
    left = []
    left_info = Card.where(name=splited[0]).array()
    if len(left_info) is 0 or left_info is None:
            return None
       
    info = None
    for info in left_info:
        if 'number' not in info:
            continue
        
        if info['number'].find('a') == -1 and info['number'].find('b'):
            continue
        
        left.append(info)
    
    right = Card.where(name=splited[1]).array()
    if len(right) is 0 or right is None:
        return None
    
    for info in right:
        if 'number' not in info:
            continue
        
        if info['number'].find('a') is not -1:
            pair_number = re.sub(r'a', 'b', info['number'])
        else:
            pair_number = re.sub(r'b', 'a', info['number'])
                
        for card in left:
            if pair_number == card['number']:
                combined_info = combineSplitCards(card, info)
                return [combined_info]
    return None

def getCardInfo(each_card):
    #process card name
    card = {}
    card['name'] = re.sub(r'Æ', 'ae', each_card['name'])
    card['id']   = each_card['id']
    
    #for split cards
    splited = card['name'].split(' // ')
    
    if len(splited) == 1:
      splited = card['name'].split(' / ')
    
    #カード情報
    if len(splited) >= 2:
        card_info = _identifyTheCard(splited)
    else:
        card_info = Card.where(name=card['name']).array()
    
    #カード情報がない場合
    if  card_info is None:
        return None
    
    if len(card_info) is 0:
        return None

    #似たような名前のカード対策
    latest_card_info = []
    for info in card_info:
        if info['name'] == card['name']:
            latest_card_info = info

    #カード情報がない場合
    if latest_card_info is 0 or latest_card_info is None:
        return None
    
    return {
        'latest_card_info' : latest_card_info,
        'card'             : card
    }
    
def main():
    #selenium準備 phantom js
    des_cap = dict(DesiredCapabilities.PHANTOMJS)
    des_cap["phantomjs.page.settings.userAgent"] = (USER_AGENT)
    driver = webdriver.PhantomJS(desired_capabilities=des_cap)
    driver.implicitly_wait(10)

    #dbから取得リストを取得
    cards = DB.getAllUpdateList()

    image_jp = ''
    image_en = ''
    for each_card in cards:
        gc.collect()
        
        #main card info
        main = getCardInfo(each_card)
        
        #card info none
        if main is None:
            continue
        
        #get main and img
        main_info = mainProcess(driver, main['card'], main['latest_card_info'])
        
        #second card info
        second_info = {}
        if 'names' in main['latest_card_info']:
            second_each_card = {
                'name' : main['latest_card_info']['names'][1],
                'id'   : each_card['id']
            }
            second = getCardInfo(second_each_card)

            #get second and img
            second_info = secondProcess(driver, second['card'], second['latest_card_info'])
        
        #DB insert
        #main
        main_id = DB.putCardInfoMain(main_info['main_en'])
        
        main_info['main_jp']['mtg_card_main_id'] = main_id
        DB.putCardInfoMainJp(main_info['main_jp'])
        
        #sub
        main_info['sub']['mtg_card_main_id'] = main_id
        
        DB.putCardInfoSub(main_info['sub'])
        main_info['sub_set_name']['mtg_card_main_id'] = main_id
        DB.putCardInfoSubSetName(main_info['sub_set_name'])
        
        #obtain img
        if main_info['img_info']['en_url'] is not None and main_info['img_info']['en_url'] is not '':
            image_jp = getImage(main_info['img_info']['en_url'], main['card']['name'], 'en')
        if main_info['img_info']['jp_url'] is not None and main_info['img_info']['jp_url'] is not '':
            image_en = getImage(main_info['img_info']['jp_url'], main['card']['name'], 'jp')
        
        #flip cards
        if len(second_info) is not int(0):
            second_info['main_second']['mtg_card_main_id'] = main_id
            second_id = DB.putCardInfoMainSecond(second_info['main_second'])
            second_info['main_second_jp']['mtg_card_main_second_id'] = second_id
            
            DB.putCardInfoMainJpSecond(second_info['main_second_jp'])
        
            #second_card_form_update
            item = {
                'second_card_form'  : second_id,
                'id'                : main_id
            }
            DB.UpdateSecondCardForm(item)
        
            #img
            if second_info['img_info']['en_url'] is not None and second_info['img_info']['en_url'] is not '':
                _ = getImage(second_info['img_info']['en_url'], main['card']['name'], 'en')
            if second_info['img_info']['jp_url'] is not None and second_info['img_info']['jp_url'] is not '':
                _ = getImage(second_info['img_info']['jp_url'], main['card']['name'], 'ja')
            
        #update obtain flag
        DB.updateObtainedFlag(each_card['id'], image_jp, image_en)
        
    #終了
    driver.quit()
    sys.exit()

if __name__ == '__main__':
    main()