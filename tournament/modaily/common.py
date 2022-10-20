import re
import smtplib 
import datetime
from email.mime.text import MIMEText
from db_connection import MySQLPipeline
from selenium.common.exceptions import NoSuchElementException

#DB
DB = MySQLPipeline()

with_standing = ["daily", "ptq", "mocs"]
need_rounds_cal = ["ptq", "mocs"]

#要素が存在するかのチェック
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

#player情報
def get_all_players_from_decklists(decklist):
    players = []
    rank = 1
    for header in decklist:
        title = header.find_element_by_xpath('.//span/h4').get_attribute('innerText').strip()
        score = re.sub('\)', '', re.sub(r'^[a-zA-Z0-9_-].*\(', '', title))
        win_points = int(re.sub(r'-[0-9]{1,}.*$', '', score).strip()) * 3
        #引き分けの場合
        if score.count('-') == 2:
            draw = int(re.sub(r'^[0-9]{1,}-[0-9]{1,}-', '', score).strip()) * 1
            win_pointspoints = win_pointspoints + draw
            
        players.append({
            "rank" : rank,
            "name" : re.sub(r'\s\(.*$', '', title).strip(),
            "points" : win_points,
            "omwp" : 0,
            "gwp" : 0,
            "ogwp" : 0
        })
        rank += 1
    return players

#player情報登録
def get_all_players_from_standing(standing):
    start = 4
    end = len(standing.find_elements_by_xpath('.//tr'))
    players = []
    while start <= end:
        rank_xpath = './/tr[' + str(start) + ']/th'
        name_xpath = './/tr[' + str(start + 1) + ']/td[2]'
        points_xpath = './/tr[' + str(start + 2) + ']/td[2]'
        omwp_xpath = './/tr[' + str(start + 3) + ']/td[2]'
        gwp_xpath = './/tr[' + str(start + 4) + ']/td[2]'
        ogwp_xpath = './/tr[' + str(start + 5) + ']/td[2]'

        players.append({
            "rank" : standing.find_element_by_xpath(rank_xpath).get_attribute('innerText').strip(),
            "name" : standing.find_element_by_xpath(name_xpath).get_attribute('innerText').strip(),
            "points" : standing.find_element_by_xpath(points_xpath).get_attribute('innerText').strip(),
            "omwp" : standing.find_element_by_xpath(omwp_xpath).get_attribute('innerText').strip(),
            "gwp" : standing.find_element_by_xpath(gwp_xpath).get_attribute('innerText').strip(),
            "ogwp" : standing.find_element_by_xpath(ogwp_xpath).get_attribute('innerText').strip()
        })
        start += 7
    return players

#top8入れ替え
def switch_top_eight(decklists, players):
    top_eight = {}
    i = 0
    for decklist in decklists:
        try:
            player_with_record = decklist.find_element_by_xpath('.//span[@class="deck-meta"]/h4').get_attribute('innerHTML').strip()
            player_name = re.sub(r'\(.*$', '', player_with_record).strip()
            player_rank = re.sub('[a-zA-Z]{,2}\s[a-zA-Z].*$', '', re.sub(r'^.*\(', '', player_with_record).strip()).strip()
        
            top_eight[player_name] = player_rank

            i += 1
            if i == 9:
                raise Exception
        except Exception:
            pass
    i = 0
    add_points = 9
    new_list = []
    for player in players:
        name = player['name']
        if name in top_eight:
            new_list.append({
                "rank" : top_eight[name],
                "name" : player['name'],
                "points" : int(player['points']) + int(add_points),
                "omwp" : player['omwp'],
                "gwp" : player['gwp'],
                "ogwp" : player['ogwp']
            })
            add_points -= 3
        else:
            new_list.append({
                "rank" : player['rank'],
                "name" : player_name,
                "points" : int(player['points']),
                "omwp" : player['omwp'],
                "gwp" : player['gwp'],
                "ogwp" : player['ogwp']
            })
        i += 1
    return new_list

#tournamt
def get_tournament(xpath, rounds, tour_type, format_id):
    tour = {}
    for decklist in xpath:
        if tour_type in with_standing:
            try:
                player_with_record = decklist.find_element_by_xpath('.//span[@class="deck-meta"]/h4').get_attribute('innerHTML').strip()
            except Exception as e:
                send_mail(e.args, date)
            
            if tour_type in need_rounds_cal and rounds != None:
                rounds = 0
            else:
                rounds = re.sub(r'-[0-9]{1,}.*$', '',re.sub(r'\)', '' ,re.sub(r'^.*\s\(', '', player_with_record))).strip()
            
            try:
                title = decklist.find_element_by_xpath('.//span[@class="deck-meta"]/h5').get_attribute('innerHTML').strip()
            except Exception as e:
                send_mail(e.args, date)
            
            start = title[-10:]
            year = start[-4:]
            month = start[:5]
            start = year + "/" + month
            end = start
        else:
            meta = xpath['meta']
            url = meta.get_attribute('content').strip()
            start = url[-10:]
            end = start
            rounds = xpath['rounds']
            rounds = re.sub(r'-[0-9]{1,}.*$', '',re.sub(r'\)', '' ,re.sub(r'^.*\s\(', '', rounds))).strip()
            x = re.search(r'mtgo-standings/[a-zA-Z0-9]{1,}-.*[0-9]{4,}-[0-9]{2,}-[0-9]{2,}$', url).start()
            title = re.sub('mtgo-standings/', '', url[int(x):])
            
        tour = {
            "name" : title,
            "start" : start,
            "end" : end,
            "rounds" : rounds,
            "format" : format_id,
            "country_id" : 1
        }
        break;
    return tour

#cardを登録
def insert_cards(card):
    return DB.mtg_card_process(card)

#main board分解
def main_board_breakdown(main, date):
    items = []
    each_cards = []
    for block in main:
        try:
            counts_and_name = block.find_elements_by_xpath('.//span[@class="row"]')
        except Exception as e:
            send_mail(e.args, date)
        
        i = 1
        for cards in counts_and_name:
            i += 1
            use_card = {}
            if check_exists_by_xpath(cards, './/span[@class="card-name"]/a') == True:
                try:
                    name = cards.find_element_by_xpath('.//span[@class="card-name"]/a').get_attribute('innerHTML').strip()
                    url = cards.find_element_by_xpath('.//span[@class="card-name"]/a').get_attribute("href")
                except Exception as e:
                    send_mail(e.args, date)
            else:
                try:
                    name = cards.find_element_by_xpath('.//span[@class="card-name"]').get_attribute('innerHTML').strip()
                except Exception as e:
                    send_mail(e.args, date)
                
                url = None
            
            if check_exists_by_xpath(cards, './/span[@class="card-count"]') == True:
                try:
                    count = cards.find_element_by_xpath('.//span[@class="card-count"]').get_attribute('innerHTML').strip()
                except Exception as e:
                    send_mail(e.args, date)
            use_card = {
                "name" : name,
                "count" : count,
                "url" : url
            }
            card_id = insert_cards(use_card)
            use_card.update({"card_id" : card_id})
            each_cards.append(use_card)
    items.append({
        "cards" : each_cards
    })
    
    return items

def side_board_breakdown(side, date):
    items = []
    each_cards = []
    for item in side:
        if check_exists_by_xpath(item, './/span[@class="card-name"]/a') == True:
            try:
                name = item.find_element_by_xpath('.//span[@class="card-name"]/a').get_attribute('innerHTML').strip()
                url = item.find_element_by_xpath('.//span[@class="card-name"]/a').get_attribute("href")
            except Exception as e:
                send_mail(e.args, date)
        else:
            name = item.find_element_by_xpath('.//span[@class="card-name"]').get_attribute('innerHTML').strip()
            url = None

        if check_exists_by_xpath(item, './/span[@class="card-count"]') == True:
            try:
                count = item.find_element_by_xpath('.//span[@class="card-count"]').get_attribute('innerHTML').strip()
            except Exception as e:
                send_mail(e.args, date)
        use_card = {
            "name" : name,
            "count" : count,
            "url" : url
        }
            
        card_id = insert_cards(use_card)
        use_card.update({"card_id" : card_id})
        each_cards.append(use_card)
    items.append({
        "cards" : each_cards
    })
    return items

#decklits
def get_decklists(decklists):
    processed_decklists = []
    deck = []
    for decklist in decklists:
        main_xpath = './/div[2]/div[@class="deck-list-text"]/div[1]/div[contains(@class, "clearfix element")]'
        side_xpath = './/div[2]/div[@class="deck-list-text"]/div[2]/span[@class="row"]'
        
        try:
            main = decklist.find_elements_by_xpath(main_xpath)
            side = decklist.find_elements_by_xpath(side_xpath)
        except Exception as e:
            send_mail(e.args, date)

        try:
            title = decklist.find_element_by_xpath('.//span[@class="deck-meta"]/h4').get_attribute('innerText')
        except Exception as e:
            send_mail(e.args, date)
            
        player_name = re.sub(r'\s\([0-9a-zA-Z].*\)$', '', title).strip()
        
        main_items = main_board_breakdown(main, datetime.date.today().strftime("%Y-%m-%d"))
        side_items = side_board_breakdown(side, datetime.date.today().strftime("%Y-%m-%d"))

        processed_decklists.append({
            player_name : {
                "main" : main_items,
                "side" : side_items
            }
        })
    return processed_decklists

#player, records, decklist登録
def insert_data(tournament, players, decklists_details):
    tour_id = DB.tournament_process(tournament)
    player_ids = []
    player_decklist = {}
    detail = {}
    for player_each in players:
        #player
        player_id = DB.player_process(player_each['name'])
        player_each['player_id'] = player_id
        player_each['tournament_id'] = tour_id
        DB.player_record_process(player_each)

        #decklist
        player_decklist = {
            "player_id" : player_id,
            "tournament_id" : tour_id
        }
        decklist_id = DB.mtg_decklist_process(player_decklist)
        player_name_cap = player_each['name'].upper()
        
        for decklist in decklists_details:
            if player_name_cap in decklist:
                deck = decklist[player_name_cap]
                break
        
        for main_cards in deck['main'][0]['cards']:
            main_insert = {}
            main_insert = {
                "decklist_id" : decklist_id,
                "mtg_decklist_where_id" : 1,
                "used_amount" : main_cards['count'],
                "card_id" : main_cards['card_id']
            }
            DB.mtg_decklist_detail_process(main_insert)
        
        for side_cards in deck['side'][0]['cards']:
            side_insert = {}
            side_insert = {
                "decklist_id" : decklist_id,
                "mtg_decklist_where_id" : 2,
                "used_amount" : side_cards['count'],
                "card_id" : side_cards['card_id']
            }
            DB.mtg_decklist_detail_process(side_insert)

#mail
def send_mail(args, date):
    msg = MIMEText('ERROR: attepmted_date: ' + date + '\n' + '\n'.join(args))
    msg['Subject'] = 'MtgIntelligence Error'
    msg['From']    = 'crawler@mtgintelligence.com'
    msg['To']      = 'billysafina@yahoo.co.jp'

    s = smtplib.SMTP() 
    s.connect()
    s.sendmail(msg['From'], ['billysafina@yahoo.co.jp'], msg.as_string() )
    s.close()