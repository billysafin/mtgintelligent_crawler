#-*- coding: utf-8 -*-
import datetime
import sys
from common import *
from setting import USER_AGENT
from selenium import webdriver
from setting import FORMAT
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
'''
TODO

ROUNDS calculated as - problem
'''

def main():
    #引数があるかのチェック
    argvs = sys.argv
    argc = len(argvs)
    
    if argc != 2:
        send_mail('引数がありませんぜよ!', datetime.datetime.today())
        sys.exit()

    if argvs[1] == 'standard':
        mo_format = FORMAT['standard']
        format_id = 1
    elif argvs[1] == 'modern':
        mo_format = FORMAT['modern']
        format_id = 2
    elif argvs[1] == 'legacy':
        mo_format = FORMAT['legacy']
        format_id = 3
    elif argvs[1] == 'vintage':
        mo_format = FORMAT['vintage']
        format_id = 4
    else:
        send_mail('引数が間違ったフォーマットです', datetime.datetime.today())
        sys.exit()
    
    #phantom js
    des_cap = dict(DesiredCapabilities.PHANTOMJS)
    des_cap["phantomjs.page.settings.userAgent"] = (USER_AGENT)

    check_xpath = '//*[@id="content-detail-page-of-an-article"]/div[1]/ul/li[1]/a'

    starting_date = datetime.date.today() + datetime.timedelta(days=-1)
    starting_date = starting_date.strftime("%Y-%m-%d")

    date = datetime.datetime.strptime(starting_date, "%Y-%m-%d")
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    
    #メイン処理部分
    while date < tomorrow:
        target_date = date.strftime("%Y-%m-%d")

        #driver再起動
        driver = webdriver.PhantomJS(desired_capabilities=des_cap)
        driver.implicitly_wait(10)

        #standard daily
        driver.get(mo_format['daily'] + target_date)
        if check_exists_by_xpath(driver, check_xpath) == True:
            
            try:
                #players
                standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[3]/div/div/table[1]/tbody')
            except Exception as e:
                send_mail(e.args, date)

            players = get_all_players_from_standing(standing)

            try:
                #tournament
                decklists = driver.find_elements_by_xpath('//*[@class="deck-group"]')
            except Exception as e:
                send_mail(e.args, target_date)

            tournament = get_tournament(decklists, None, "daily", format_id)
            #decklist
            decklists_details = get_decklists(decklists)

            #players,records
            #decklistをDBに投入
            insert_data(tournament, players, decklists_details)

        #league
        driver.get(mo_format['league_one'] + target_date)
        if check_exists_by_xpath(driver, check_xpath) == True:
            
            try:
                #tournament
                meta = driver.find_element_by_xpath('//html/head/meta[@property="og:url"]')
                rounds = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[2]/div[1]/div[1]/div[1]/div[1]/span/h4').get_attribute('innerText') 
            except Exception as e:
                send_mail(e.args, target_date)

            xpath = {
                "meta" : meta,
                "rounds" : rounds
            }
            tournament = get_tournament(xpath, None, "league", format_id)

            try:
                #decklist
                decklists = driver.find_elements_by_xpath('//*[@class="deck-group"]')
            except Exception as e:
                send_mail(e.args, target_date)

            decklists_details = get_decklists(decklists)
            #players (name only)
            players = get_all_players_from_decklists(decklists)

            #players,records
            #decklistをDBに投入
            insert_data(tournament, players, decklists_details)

        #league
        driver.get(mo_format['league_two'] + target_date)
        if check_exists_by_xpath(driver, check_xpath) == True:
            
            try:
                #tournament
                meta = driver.find_element_by_xpath('//html/head/meta[@property="og:url"]')
                rounds = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[2]/div[1]/div[1]/div[1]/div[1]/span/h4').get_attribute('innerText') 
            except Exception as e:
                send_mail(e.args, target_date)

            xpath = {
                "meta" : meta,
                "rounds" : rounds
            }
            tournament = get_tournament(xpath, None, "league", format_id)

            try:
                #decklist
                decklists = driver.find_elements_by_xpath('//*[@class="deck-group"]')
            except Exception as e:
                send_mail(e.args, target_date)

            decklists_details = get_decklists(decklists)
            #players (name only)
            players = get_all_players_from_decklists(decklists)

            #players,records
            #decklistをDBに投入
            insert_data(tournament, players, decklists_details) 

        #ptq
        driver.get(mo_format['ptq'] + target_date)
        if check_exists_by_xpath(driver, check_xpath) == True:
            
            try:
                #players
                if check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[4]/div/div/table[1]/tbody') == False:
                    standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[3]/div/div/table[1]/tbody')
                else:
                    standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[4]/div/div/table[1]/tbody')
            except Exception as e:
                send_mail(e.args, target_date)

            players = get_all_players_from_standing(standing)

            try:
                #ptq用に順位の入れ替え
                decklists = driver.find_elements_by_xpath('//*[@class="deck-group"]')
            except Exception as e:
                send_mail(e.args, target_date)

            players = switch_top_eight(decklists, players)

            #tournament
            tournament = get_tournament(decklists, None, "ptq", format_id)

            #decklist
            decklists_details = get_decklists(decklists)

            #players,records
            #decklistをDBに投入
            insert_data(tournament, players, decklists_details)

        #magic online championship
        driver.get(mo_format['mocs'] + target_date)
        if check_exists_by_xpath(driver, check_xpath) == True:    
            #players
            checked_stand = check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[4]/div/div/table[1]/tbody')

            try:
                if checked_stand == False:
                    result_one = check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[5]/div/div/table[1]/tbody')
                    if result_one == True:
                        standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[5]/div/div/table[1]/tbody')
                    else:
                        result_two = check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[3]/div/div/table[1]/tbody')
                        if result_two == True:
                            standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[3]/div/div/table[1]/tbody')
                        else:
                            standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[35]/div/div/table[1]/tbody')        
                else:
                    standing = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[4]/div/div/table[1]/tbody')
            except Exception as e:
                send_mail(e.args, target_date)


            players = get_all_players_from_standing(standing)

            try:
                #ptq用に順位の入れ替え
                decklists = driver.find_elements_by_xpath('//*[@class="deck-group"]')
            except Exception as e:
                send_mail(e.args, target_date)

            checked_round = check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[4]/div/div/table[2]/tbody/tr[1]/td[3]')

            try:
                if checked_round == False:
                    result_one = check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[5]/div/div/table[2]/tbody/tr[1]/td[3]')
                    if result_one == True:
                        rounds = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[5]/div/div/table[2]/tbody/tr[1]/td[3]').get_attribute('innerText')
                    else:
                        result_two = check_exists_by_xpath(driver, '//*[@id="content-detail-page-of-an-article"]/div[5]/div/div/table[2]/tbody/tr[1]/td[3]')
                        if result_two == True:
                            rounds = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[3]/div/div/table[2]/tbody/tr[1]/td[3]').get_attribute('innerText')
                else:
                    rounds = driver.find_element_by_xpath('//*[@id="content-detail-page-of-an-article"]/div[4]/div/div/table[2]/tbody/tr[1]/td[3]').get_attribute('innerText')
            except Exception as e:
                send_mail(e.args, target_date)

            players = switch_top_eight(decklists, players)

            #tournament
            tournament = get_tournament(decklists, rounds, 'mocs', format_id)

            #decklist
            decklists_details = get_decklists(decklists)

            #players,records
            #decklistをDBに投入
            insert_data(tournament, players, decklists_details)

        #日付追加
        date = date + datetime.timedelta(days=1)
        driver.quit()

    #終了
    driver.quit()
    sys.exit()

if __name__ == '__main__':
    main()
