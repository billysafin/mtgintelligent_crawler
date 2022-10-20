#-*- coding: utf-8 -*-
from common import check_exists_by_xpath
import re

#wisdom
wisdomguide_url = 'http://whisper.wisdom-guild.net/card/'

def escape(s, quoted=u'\'"\\', escape=u'\\'):
    return re.sub(
        u'[%s]' % re.escape(quoted),
        lambda mo: escape + mo.group(),
        s)

def getvalue(v):
    if type(v) is not str:
        return v[0]
    else:
        return v

#データ準備
def processMainDict(card_detail):
    to_main = {}
    if 'colors' in card_detail:
        colors = []
        for color in card_detail['colors']:
            colors.append(getvalue(color))
                
        to_main['color'] = ','.join(colors)
    else:
        to_main['color'] = 'Colorless'

    if 'cmc' in card_detail:
        to_main['converted_mana_cost'] = card_detail['cmc']
    else:
        to_main['converted_mana_cost'] = 0
    if 'manaCost' in card_detail:
        to_main['mana_cost'] = card_detail['manaCost']
    else:
        to_main['mana_cost'] = ''
    if 'type' in card_detail:
        to_main['type'] = escape(card_detail['type'])
    else:
        to_main['type'] = ''
    if 'power' in card_detail:
        to_main['power'] = escape(card_detail['power'])
    else:
        to_main['power'] = ''
    if 'toughness' in card_detail:
        to_main['thoughness'] = escape(card_detail['toughness'])
    else:
        to_main['thoughness'] = ''
    if 'loyalty' in card_detail:
        to_main['loyalty'] = card_detail['loyalty']
    else:
        to_main['loyalty'] = ''
    if 'text' in card_detail:
        to_main['text_en'] = escape(card_detail['text'])
    else:
        to_main['text_en'] = ''
    
    return to_main

def mainProcess(driver, card, latest_card_info):
    main_en         = {}
    main_jp         = {}
    sub             = {}
    sub_set_name    = {}
    img_info        = {}
    japanese        = {}
    
    #main en
    main_en = processMainDict(latest_card_info)
    main_en['mtg_card_id']      = card['id']
    main_en['second_card_form'] = None
    
    #img en
    img_info['name'] = card['name']
    
    if 'imageUrl' in latest_card_info:
        img_info['en_url'] = latest_card_info['imageUrl']
    else:
        img_info['en_url'] = ''
    
    #sub
    if 'flavor' in latest_card_info:
        sub['flavor_text'] = escape(latest_card_info['flavor'])
    else:
        sub['flavor_text'] = ''
    if 'artist' in latest_card_info:
        sub['artist']      = escape(latest_card_info['artist'])
    else:
         sub['artist'] = ''
    if 'rarity' in latest_card_info:
        sub['rarity']      = latest_card_info['rarity']
    else:
        sub['rarity']      = ''
    if 'number' in latest_card_info:
        sub['set_number']  = latest_card_info['number']
    else:
        sub['set_number']  = ''
    
    #sub_set_name
    if 'printings' in latest_card_info:
        sub_set_name['set_name'] = ','.join(latest_card_info['printings'])
    else:
        sub_set_name['set_name'] = ''
    
    #japanese
    if 'foreignNames' in latest_card_info:
        for lang in latest_card_info['foreignNames']:
            if lang['language'] == 'Japanese':
                japanese = lang
                break

        if len(japanese) is not 0:
            main_jp['name_jp'] = escape(japanese['name'])

            #めんどいのでseleniumで逃げる
            cardname = card['name']
            driver.get(wisdomguide_url + cardname + '/')

            check_wisdom = '//*[@id="contents_noleft"]/div/div[2]/table/tbody'
            if check_exists_by_xpath(driver, check_wisdom) == True:
                if 'names' in latest_card_info:
                    if latest_card_info['layout'] == 'split':
                        _titles = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[1]/td'
                        titles = driver.find_elements_by_xpath(_titles)
                        i = 1
                        for title in titles:
                            name = title.get_attribute('innerText').strip()
                            if latest_card_info['name'] in name:
                                break
                            i += 1
                        _text = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[4]/td[' + str(i) + ']/p'
                        text_jp = []
                        text = driver.find_elements_by_xpath(_text)
                        for t in text:
                            text_jp.append(t.get_attribute('innerText').strip())
                        main_jp['text_jp'] = escape('\n'.join(text_jp))

                        flavors = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[6]/td[' + str(i) + ']/i'
                        sub_jps = driver.find_elements_by_xpath(flavors)
                        flavor_sub_jp = []
                        for flavor in sub_jps:
                            flavor_sub_jp.append(flavor.get_attribute('innerText').strip())
                        main_jp['flavor_text_jp'] = escape('\n'.join(flavor_sub_jp))         
                    elif latest_card_info['layout'] == 'double-faced' or latest_card_info['layout'] == 'flip' or latest_card_info['layout'] == 'meld':
                        first_title = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[1]/td'
                        title = driver.find_element_by_xpath(first_title).get_attribute('innerText').strip()

                        if latest_card_info['name'] in title:
                            text = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[4]/td/p'
                            flavors = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[7]/td/i'
                        else:
                            text = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[12]/td/p'
                            flavors = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[15]/td/i'

                        text_jp = []
                        _text_jp = driver.find_elements_by_xpath(text)
                        for jp in _text_jp:
                            text_jp.append(jp.get_attribute('innerText').strip())

                        if text_jp is not None:
                            main_jp['text_jp'] = escape('\n'.join(text_jp))
                        else:
                            main_jp['text_jp'] = ''

                        flavor_sub_jp = []
                        sub_jps = driver.find_elements_by_xpath(flavors)
                        for flavor in sub_jps:
                            flavor_sub_jp.append(flavor.get_attribute('innerText').strip())

                        if flavor_sub_jp is not None:
                            main_jp['flavor_text_jp'] = escape('\n'.join(flavor_sub_jp))
                        else:
                            main_jp['flavor_text_jp'] = ''                        
                else:
                    texts = driver.find_elements_by_xpath('//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[4]/td/p')
                    text_jp = []
                    for text in texts:
                        text_jp.append(text.get_attribute('innerText'))
                    main_jp['text_jp'] = escape('\n'.join(text_jp).strip())

                    sub_jp = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[7]/td/i'
                    sub_jps = driver.find_elements_by_xpath(sub_jp)
                    sub_text = []
                    for flavor in sub_jps:
                        sub_text.append(flavor.get_attribute('innerText').strip())

                    main_jp['flavor_text_jp'] = escape('\n'.join(sub_text))
            else:
                main_jp['name_jp'] = ''
                main_jp['text_jp'] = ''
                main_jp['flavor_text_jp'] = ''
        else:
            main_jp['name_jp'] = ''
            main_jp['text_jp'] = ''
            main_jp['flavor_text_jp'] = ''
    else:
        main_jp['name_jp'] = ''
        main_jp['text_jp'] = ''
        main_jp['flavor_text_jp'] = ''
            
    #img jp
    if len(japanese) is not 0:
        if 'imageUrl' in japanese:
            img_info['jp_url'] = japanese['imageUrl']
        else:
            img_info['jp_url'] = ''
    else:
        img_info['jp_url'] = ''
        
    return_values = {
        'main_en'         : main_en,
        'main_jp'         : main_jp,
        'sub'             : sub,
        'sub_set_name'    : sub_set_name,
        'img_info'        : img_info
    }
    
    return return_values
    
def secondProcess(driver, card, latest_card_info):
    img_info        = {}
    main_second     = {}
    main_second_jp  = {}
    japanese        = {}
    
    #main second en
    main_second = processMainDict(latest_card_info)
    main_second['mtg_card_main_id'] = card['id']
    
    #img en
    img_info['name'] = card['name']
    if 'imageUrl' in latest_card_info:
        img_info['en_url'] = latest_card_info['imageUrl']
    else:
        img_info['en_url'] = ''
    
    #japanese
    if 'foreignNames' in latest_card_info:
        for lang in latest_card_info['foreignNames']:
            if lang['language'] == 'Japanese':
                japanese = lang
                break

        if len(japanese) is not 0:
            main_second_jp['name_jp'] = escape(japanese['name'])

            #めんどいのでseleniumで逃げる
            cardname = re.sub(' ', '+', card['name']) 
            driver.get(wisdomguide_url + cardname + '/')

            check_wisdom = '//*[@id="contents_noleft"]/div/div[2]/table/tbody'
            if check_exists_by_xpath(driver, check_wisdom) == True:
                if 'names' in latest_card_info:
                    if latest_card_info['layout'] == 'split':
                        _titles = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[1]/td'
                        titles = driver.find_elements_by_xpath(_titles)
                        i = 1
                        for title in titles:
                            name = title.get_attribute('innerText').strip()
                            if latest_card_info['name'] in name:
                                break
                            i += 1
                        _text = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[4]/td[' + str(i) + ']/p'
                        text_jp = []
                        text = driver.find_elements_by_xpath(_text)
                        for t in text:
                            text_jp.append(t.get_attribute('innerText').strip())
                        main_second_jp['text_jp'] = escape('\n'.join(text_jp))

                        flavors = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[6]/td[' + str(i) + ']/i'
                        sub_jps = driver.find_elements_by_xpath(flavors)
                        flavor_sub_jp = []
                        for flavor in sub_jps:
                            flavor_sub_jp.append(flavor.get_attribute('innerText').strip())

                        main_second_jp['flavor_text_jp'] = '\n'.join(flavor_sub_jp)
                    elif latest_card_info['layout'] == 'double-faced' or latest_card_info['layout'] == 'flip':
                        first_title = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[1]/td'
                        title = driver.find_element_by_xpath(first_title).get_attribute('innerText').strip()

                        if latest_card_info['name'] in title:
                            text = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[4]/td/p'
                            flavors = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[7]/td/i'
                        else:
                            text = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[12]/td/p'
                            flavors = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[15]/td/i'

                        text_jp = []
                        _text_jp = driver.find_elements_by_xpath(text)
                        for jp in _text_jp:
                            text_jp.append(jp.get_attribute('innerText').strip())

                        if text_jp is not None:
                            main_second_jp['text_jp'] = escape('\n'.join(text_jp))
                        else:
                            main_second_jp['text_jp'] = ''

                        flavor_sub_jp = []
                        sub_jps = driver.find_elements_by_xpath(flavors)
                        for flavor in sub_jps:
                            flavor_sub_jp.append(flavor.get_attribute('innerText').strip())

                        if flavor_sub_jp is not None:
                            main_second_jp['flavor_text_jp'] = escape('\n'.join(flavor_sub_jp))
                        else:
                            main_second_jp['flavor_text_jp'] = ''                    
                    else:
                        texts = driver.find_elements_by_xpath('//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[4]/td/p')
                        text_jp = []
                        for text in texts:
                            text_jp.append(text.get_attribute('innerText'))
                        main_second_jp['text_jp'] = escape('\n'.join(text_jp).strip())

                        sub_jp = '//*[@id="contents_noleft"]/div/div[2]/table/tbody/tr[7]/td/i'
                        sub_jps = driver.find_elements_by_xpath(sub_jp)
                        sub_text = []
                        for flavor in sub_jps:
                            sub_text.append(flavor.get_attribute('innerText').strip())

                        main_second_jp['flavor_text_jp'] = escape('\n'.join(sub_text))
                else:
                    main_second_jp['name_jp'] = ''
                    main_second_jp['text_jp'] = ''
                    main_second_jp['flavor_text_jp'] = ''
            else:
                main_second_jp['name_jp'] = ''
                main_second_jp['text_jp'] = ''
                main_second_jp['flavor_text_jp'] = ''
        else:
            main_second_jp['name_jp'] = ''
            main_second_jp['text_jp'] = ''
            main_second_jp['flavor_text_jp'] = ''
    else:
        main_second_jp['name_jp'] = ''
        main_second_jp['text_jp'] = ''
        main_second_jp['flavor_text_jp'] = ''
         
    #img jp
    if len(japanese) is not 0:
        if 'imageUrl' in japanese:
            img_info['jp_url'] = japanese['imageUrl']
        else:
            img_info['jp_url'] = ''
    else:
        img_info['jp_url'] = ''
    
    return_values = {
        'main_second'     : main_second,
        'main_second_jp'  : main_second_jp,
        'img_info'        : img_info
    }
    
    return return_values
        
    