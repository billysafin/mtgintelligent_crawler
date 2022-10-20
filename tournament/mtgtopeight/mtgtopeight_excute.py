#-*- coding: utf-8 -*-
import datetime
import sys
from common import *
from setting import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import traceback
import gc

player_unknwon_loop = 1

def excution(driver, qury_e):
    check_xpath = '//html/body/div[3]/div/table/tbody/tr/td[2]/table[2]'
    if check_exists_by_xpath(driver, check_xpath) == True:
        try:
            tour = {}
            record = {}
            meta_info = {}

            tour_name = driver.find_element_by_xpath('//html/body/div[3]/div/div/table/tbody/tr/td[1]')
            tour['name'] = tour_name.get_attribute('innerText').strip()

            tour_details = driver.find_element_by_xpath('//html/body/div[3]/div/table/tbody/tr/td[1]/div/table[1]')

            tour['format'] = None
            tour_format = tour_details.find_element_by_xpath('.//td').get_attribute('innerText')

            for key, value in FORMATS.items():
                if re.match(key, tour_format):
                    tour['format'] = value
                    break

            if tour['format'] is None:
                tour['format'] = 9

            _tour_date = tour_details.find_element_by_xpath('.//tbody/tr/td').get_attribute('innerText')
            tour_date = re.search(r'\n[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}\n$', _tour_date)

            if tour_date is None:
                tour_date = re.search(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}\n', _tour_date)

            dates = re.sub('\n', '', tour_date.group()).split('/')
            tour['start'] = re.sub('\n', '', dates[2]) + '-' + re.sub('\n', '', dates[1]) + '-' + re.sub('\n', '', dates[0])
            tour['end'] = tour['start']
            tour['country_id'] = 4
            tour['rounds'] = 0
            if qury_e is not None:
                tour['memo'] = 'MTGTOP8-' + str(qury_e)
            else:
                tour['memo'] = ''

            tour_id = insert_tour(tour)

            rank_deck_player = driver.find_element_by_xpath('//html/body/div[3]/div/div/table/tbody/tr/td[2]').get_attribute('innerText')
            global player_unknwon_loop
            if re.search('Top 8', rank_deck_player) is not None:
                rank_deck_player = re.sub(r'\s\[.*\]\s', '', rank_deck_player)
                rank_deck_player = re.sub(r'\[', '', rank_deck_player)
                rank_deck_player = re.sub(r'#', '', rank_deck_player)
                rank_deck_player = re.sub(r'-$', '', rank_deck_player)

                player = re.search(r'\s-.*$', rank_deck_player)

                if player is None:
                    player = None
                else:
                    player = re.sub('\s-', '', player.group()).strip()

                if player is None or player == '':
                    player = 'UNKOWN' + '-' + str(qury_e) + '-' + str(player_unknwon_loop)
                    player_unknwon_loop += 1
                rank_deck = re.sub('\s-\s$', '', rank_deck_player)
                rank = re.search(r'#[0-9]{1,}\s', rank_deck)

                if rank is None:
                    record['rank'] = 0
                    meta_info['name'] = re.sub(r'#', '', rank_deck).strip()
                else:
                    record['rank'] = rank.strip()
                    meta_info['name'] = re.sub(rank.group(), '', rank_deck).strip()
            else:
                player = re.search(r'\s-\s[a-zA-Z0-9].*$', re.sub('"', '', rank_deck_player))
                if player == None or player == '':
                    player = 'UNKOWN' + '-' + str(qury_e) + '-' + str(player_unknwon_loop)
                    player_unknwon_loop += 1
                    rank_deck = re.sub('\s-.*$', '', rank_deck_player)
                else:
                    player = re.sub(r'^\s-\s', '', player.group())
                    rank_deck = re.sub('\s-\s' + player, '', rank_deck_player)

                if re.search(r'#[0-9]{1,}-', rank_deck):
                    rank = re.search(r'#[0-9]{1,}-', rank_deck)
                    record['rank'] = re.sub('#', '', re.sub('-', '', rank.group())).strip()
                    delete_rank = re.search(r'#[0-9]{1,}-[0-9]{1,}\s', rank_deck)
                    meta_info['name'] = re.sub(delete_rank.group(), '', rank_deck)
                else:
                    rank = re.search(r'#[0-9]{1,}\s', rank_deck)

                    if rank is None:
                        record['rank'] = 0
                        meta_info['name'] = re.sub('-$', '', re.sub(r'#', '', rank_deck)).strip()
                    else:
                        meta_info['name'] = re.sub(rank.group(), '', rank_deck)
                        record['rank'] = re.sub('#', '', rank.group()).strip()


            CHECKED_PLAYER.append(player)
            player_id = insert_player(player)

            meta_info['mtg_format_id'] = tour['format']
            meta_id = meta_name_process(meta_info)

            record['player_id'] = player_id
            record['tournament_id'] = tour_id
            record['omwp'] = 0
            record['gwp'] = 0
            record['ogwp'] = 0
            record['points'] = 0
            player_record_process(record)

            decklist_id = mtg_decklist_process({
                'player_id'      : player_id
                ,'tournament_id' : tour_id
                ,'meta_deck_name_id' : meta_id
            })

            decklist = get_decklist(driver)

            for main in decklist['main']:
                detail = {
                    'decklist_id'            : decklist_id
                    ,'mtg_decklist_where_id' : 1
                    ,'used_amount'           : main['count']
                    ,'card_id'               : main['card_id']
                }
                mtg_decklist_detail_process(detail)

            for side in decklist['side']:
                detail = {
                    'decklist_id'            : decklist_id
                    ,'mtg_decklist_where_id' : 2
                    ,'used_amount'           : side['count']
                    ,'card_id'               : side['card_id']
                }
                mtg_decklist_detail_process(detail)
        except Exception as e:
            traceback.print_exc()
            send_mail(e.args, datetime.datetime.today())
            return e.args

    return None

def main():
    #url
    url = 'http://www.mtgtop8.com/event?e='

    #headless chrome
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')

    qury_e = getStartingQueryE()

    if qury_e is None:
        qury_e = 1;

    while True:
        gc.collect()
        targetUrl = url + str(qury_e)
        if checkURL(targetUrl) is None:
            driver.quit()
            sys.exit()

        #main
        driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=opts)
        driver.get(targetUrl)

        if excution(driver, qury_e) is not None:
            driver.quit()
            sys.exit()

        #other
        related_links = get_related(driver, CHECKED_PLAYER)
        driver.quit()

        if related_links is not None:
            for link in related_links:
                gc.collect()
                driver = webdriver.Chrome(chrome_options=opts)
                driver.get(link)

                if excution(driver, None) is not None:
                    driver.quit()
                    sys.exit()

                driver.quit()

        qury_e += 1

if __name__ == '__main__':
    main()
    try:
        subprocess.call("pgrep chrome | xargs kill -9")
    except:
        pass
