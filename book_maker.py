from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime

import time
import re
import os
import time
from db import database


class bookMaker:
    def __init__(self):
        self.vig_price_difference = 0.1
        self.data = []
        self.sporty_bet_url = os.getenv("SPORTYBET_URL")
        self.searched_event = []
        self.eventDate = 0
        self.event_from_pinnacle = {}
        self.found_element = ""
        self.longestPhraseHometeam =""
        self.longest_phrase_home_team = ""
        self.longest_phrase_away_team = ""
        self.drive = any
        
    def open_browser(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    def open_site(self):
        self.driver.get('https://www.sportybet.com/ng/m/')
        time.sleep(15)
        
    def login(self):
        self.driver.find_element(By.CLASS_NAME,'m-btn-login').click();
        time.sleep(5)
        self.driver.find_element(By.CLASS_NAME, "m-input-wap").send_keys("8135715285")
        self.driver.find_element(By.CLASS_NAME, "m-input-wap__password").send_keys('Adinoyi7#')
        time.sleep(5)
        self.driver.find_element(By.CLASS_NAME, 'login-btn').click()
        
        time.sleep(5)
        print("loged in")
        
    def find_element_cont(self, name):        
        elements = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.m-market'))
        )
        
        for i,element in enumerate(elements):
            if len(self.found_element) == 0:
                child_element = element.find_element(By.CSS_SELECTOR, '.text')
                if child_element.text == name:
                    print("found")
                    self.found_element = "found the element"
                    return element
                else:
                    if len(self.found_element) == 0:
                        self.scroll_view(name)    
            
        
    def search_match(self):
        search_phrase = self.get_correct_team_names()
        self.driver.find_element(By.CLASS_NAME, "m-icon-search").click()
        time.sleep(15)
        self.driver.find_element(By.CLASS_NAME, "m-input-wap").send_keys(search_phrase)
        time.sleep(10)
        print("Searches for events")
        
    def store_event(self, event):
        self.event_from_pinnacle = event
    
    def select_event(self, index):
        try:
            # Wait for the elements to be present
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.team'))
            )
            
            if len(elements) > index:
                # Click the element at the specified index
                elements[index].click()
                time.sleep(3)  # Wait for 3 seconds
                print("Selects events")
        except Exception as e:
            print(e)

    def scroll_view(self, name):        
        self.driver.execute_script(f"window.scrollBy(0, 200);")
        if len(self.found_element) == 0:
            self.find_element_cont(name)
            
            
        
    def select_all_tag(self):
        time.sleep(3)
        
        elements = self.driver.find_elements(By.CSS_SELECTOR, '.m-sport-group-item')
        
        for element in elements:
            if "All" in element.text:
                element.click()
    
    
    def get_correct_team_names(self, home, away)-> str: 
        home_name = re.sub(r'[^a-zA-Z]', ' ', home).split()
        away_name = re.sub(r'[^a-zA-Z]', ' ', away).split()
        self.longest_phrase_home_team = home_name[0]
        self.longest_phrase_away_team = away_name[0]

        for name in home_name:
            if len(name) > len(self.longest_phrase_home_team):
                self.longest_phrase_home_team = name

        for name in away_name:
            if len(name) > len(self.longest_phrase_away_team):
                self.longest_phrase_away_team = name

        return f"{self.longest_phrase_home_team} {self.longest_phrase_away_team}"

    def compare_sporty_events_with_pinnacle(self, index):
        if len(self.searched_event) > 0:
            event_hour, event_minute = self.searched_event[index]['time'].split(':')
            event_date = datetime.fromtimestamp(int(self.event_from_pinnacle['starts']) / 1000)
            
            if ((self.longest_phrase_home_team in self.searched_event[index]['home'] or 
                self.searched_event[index]['home'] == self.event_from_pinnacle['home']) and
                (self.longest_phrase_away_team in self.searched_event[index]['away'] or 
                self.searched_event[index]['away'] == self.event_from_pinnacle['away']) and
                (event_date.hour == int(event_hour)) and
                (event_date.minute == int(event_minute))):
                return True
            else:
                return False
        else:
            return False

    def get_event(self):
        # Wait for the '.team' elements to be present
        team_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.team'))
        )
        event_names = [element.text for element in team_elements]

        # Wait for the '.m-time' elements to be present
        time_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-time'))
        )
        times_of_event = [element.text for element in time_elements]

        # Wait for the '.m-date' elements to be present
        date_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-date'))
        )
        dates_of_event = [element.text[:5] for element in date_elements]

        if len(times_of_event) == len(dates_of_event) and \
           (len(dates_of_event) == len(event_names) // 2) and \
           len(times_of_event) > 0:
            for i in range(0, len(event_names), 2):
                self.searched_event.append({
                    'home': event_names[i],
                    'away': event_names[i + 1],
                    'time': times_of_event[i // 2],
                    'date': dates_of_event[i // 2]
                })
        

    def sort_football_bets_base_on_outcome(self):
        if self.event_from_pinnacle['lineType'] == 'money_line':
            self.place_bet_for_moneyline()
        elif self.event_from_pinnacle['lineType'] == 'total':
            self.sort_total_bets()
        elif self.event_from_pinnacle['lineType'] == 'spread':
            self.sort_spreads_bet()
        else:
            self.default()

    def sort_basketball_bets_base_on_outcome(self):
        if self.event_from_pinnacle['lineType'] == 'money_line':
            self.place_bet_for_moneyline_basketball()
        elif self.event_from_pinnacle['lineType'] == 'total':
            self.sort_basketball_total_bets()
        elif self.event_from_pinnacle['lineType'] == 'spread':
            self.place_bet_for_basketball_handicap()
        else:
            self.default()

    def sort_tennis_bets_base_on_outcome(self):
        if self.event_from_pinnacle['lineType'] == 'money_line':
            self.place_bet_for_moneyline_tennis()
        elif self.event_from_pinnacle['lineType'] == 'total':
            self.place_tennis_bets_for_full_total()
        elif self.event_from_pinnacle['lineType'] == 'spread':
            self.place_bet_for_tennis_handicap()
        else:
            self.default()
            
    def sort_total_bets(self):
        if self.event_from_pinnacle['points'] % 1 == 0:
            self.place_bet_for_asian_total()
        elif self.event_from_pinnacle['points'] % 1 == 0.5:
            self.place_bet_for_normal_total()
        else:
            self.default()

    def sort_basketball_total_bets(self):
        if self.event_from_pinnacle['periodNumber'] == '0':
            self.place_basketball_bets_total_for_full_match()
        elif self.event_from_pinnacle['periodNumber'] == 1:
            self.place_basketball_bets_total_for_half_match()
        else:
            self.default()

    def sort_spreads_bet(self):
        if self.event_from_pinnacle['points'] % 1 == 0.5:
            self.place_bet_for_asian_handicap()
        else:
            self.default()

    def sort_basketball_spreads_bet(self):
        if self.event_from_pinnacle['points'] % 1 == 0.5:
            self.place_bet_for_basketball_handicap()
        else:
            self.default()

    def place_bet_for_moneyline(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for i,element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "1X2":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-cell')
                for i,row in enumerate(contents_row):
                    if len(contents_row) > 0:
                        info_tag = row.find_elements(By.TAG_NAME, 'em')
                        if len(info_tag) == 2:
                            check_if_draw_win_or_lose = info_tag[0].text
                            vig_price_from_sportybet = info_tag[1].text
                            if (check_if_draw_win_or_lose == "Draw" and
                                self.event_from_pinnacle['outcome'] == "" and
                                self.event_from_pinnacle['points'] == "0"):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
                            elif (check_if_draw_win_or_lose == "Home" and
                                  self.event_from_pinnacle['outcome'] == "home" and
                                  self.event_from_pinnacle['points'] == ""):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
                            elif (check_if_draw_win_or_lose == "Away" and
                                  self.event_from_pinnacle['outcome'] == "away" and
                                  self.event_from_pinnacle['points'] == ""):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
                                
    def place_bet_for_normal_total(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for i,element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Over/Under":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for j,row in enumerate(contents_row):
                    content = row.find_elements(By.TAG_NAME, 'em')
                    content_label = content[0].text
                    if content_label == self.event_from_pinnacle['points']:
                        if self.event_from_pinnacle['outcome'] == "under":
                            content_value = content[2].text
                            self.final_check_on_bet(content_value, content[2], "goalline")
                        elif self.event_from_pinnacle['outcome'] == "over":
                            content_value = content[1].text
                            self.final_check_on_bet(content_value, content[1], "goalline")
        
    def place_bet_for_asian_total(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for element in elements:
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Asian Over/Under":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for row in contents_row:
                    content = row.find_elements(By.TAG_NAME, 'em')
                    content_label = content[0].text
                    if content_label == self.event_from_pinnacle['points']:
                        if self.event_from_pinnacle['outcome'] == "under":
                            content_value = content[2].text
                            self.final_check_on_bet(content_value, content[2], "goalline")
                        elif self.event_from_pinnacle['outcome'] == "over":
                            content_value = content[1].text
                            self.final_check_on_bet(content_value, content[1], "goalline")
                                                    
    def place_bet_for_asian_handicap(self):
        element = self.find_element_cont("Asian Handicap")
        contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
        for content_row in contents_row:
            content = content_row.find_elements(By.CSS_SELECTOR, '.m-table-cell')
            if self.event_from_pinnacle['outcome'] == "home" and len(content)> 0 and len(content_row) > 0:
                content_section = content[0].find_elements(By.TAG_NAME, 'em')
                if content_section:
                    content_value_holder = content_section[0]
                    content_label = content_value_holder.text
                    if content_label == self.event_from_pinnacle['points']:
                        content_value_holder = content[1]
                        content_value = content_value_holder.text
                        self.final_check_on_bet(content_value, content_value_holder, "outcome")
            elif self.event_from_pinnacle['outcome'] == "away" and len(content)> 0 and len(content_row) > 0:
                content_section = content[1].find_elements(By.TAG_NAME, 'em')
                if content_section:
                    content_value_holder = content_section[0]
                    content_label = content_value_holder.text
                    if content_label == self.event_from_pinnacle['points']:
                        content_value_holder = content[1]
                        content_value = content_value_holder.text
                        self.final_check_on_bet(content_value, content_value_holder, "outcome")

    # basketball
    
    def place_bet_for_moneyline_basketball(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for j, element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Winner (incl. overtime)":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-cell')
                for k, row in enumerate(contents_row):
                    if len(contents_row) > 0:
                        info_tag = row.find_elements(By.TAG_NAME, 'em')
                        if len(info_tag) == 2:
                            check_if_draw_win_or_lose = info_tag[0].text
                            vig_price_from_sportybet = info_tag[1].text
                            if (check_if_draw_win_or_lose == "Home" and
                                  self.event_from_pinnacle['outcome'] == "home" and
                                  self.event_from_pinnacle['points'] == ""):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
                            elif (check_if_draw_win_or_lose == "Away" and
                                  self.event_from_pinnacle['outcome'] == "away" and
                                  self.event_from_pinnacle['points'] == ""):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
       
    
    def place_bet_for_basketball_handicap(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for k,element in enumerate(elements):
            child_elements = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_elements.text
            if child_element_name == "Asian Handicap" or "Handicap (incl. overtime)":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for content_row in contents_row:
                    content = content_row.find_elements(By.CSS_SELECTOR, '.m-table-cell')
                    if self.event_from_pinnacle['outcome'] == "home" and len(content)> 0 and len(content_row) > 0:
                        content_section = content[0].find_elements(By.TAG_NAME, 'em')
                        if content_section:
                            content_value_holder = content_section[0]
                            content_label = content_value_holder.text
                            if content_label == self.event_from_pinnacle['points']:
                                content_value_holder = content[1]
                                content_value = content_value_holder.text
                                self.final_check_on_bet(content_value, content_value_holder, "outcome")
                    elif self.event_from_pinnacle['outcome'] == "away" and len(content)> 0 and len(content_row) > 0:
                        content_section = content[1].find_elements(By.TAG_NAME, 'em')
                        if content_section:
                            content_value_holder = content_section[0]
                            content_label = content_value_holder.text
                            if content_label == self.event_from_pinnacle['points']:
                                content_value_holder = content[1]
                                content_value = content_value_holder.text
                                self.final_check_on_bet(content_value, content_value_holder, "outcome")

    def place_basketball_bets_total_for_full_match(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for k,element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Over/Under (incl. overtime)":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for m,row in enumerate(contents_row):
                    content = row.find_elements(By.TAG_NAME, 'em')
                    content_label = content[0].text
                    if content_label == self.event_from_pinnacle['points']:
                        if self.event_from_pinnacle['outcome'] == "under":
                            content_value = content[2].text
                            self.final_check_on_bet(content_value, content[2], "goalline")
                        elif self.event_from_pinnacle['outcome'] == "over":
                            content_value = content[1].text
                            self.final_check_on_bet(content_value, content[1], "goalline")
                
        
    def place_basketball_bets_total_for_half_match(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for k,element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "1st Half - Over/Under":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for j,row in enumerate(contents_row):
                    content = row.find_elements(By.TAG_NAME, 'em')
                    content_label = content[0].text
                    if content_label == self.event_from_pinnacle['points']:
                        if self.event_from_pinnacle['outcome'] == "under":
                            content_value = content[2].text
                            self.final_check_on_bet(content_value, content[2], "goalline")
                        elif self.event_from_pinnacle['outcome'] == "over":
                            content_value = content[1].text
                            self.final_check_on_bet(content_value, content[1], "goalline")
        
# tenis

    def place_tennis_bets_for_full_total(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for i,element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Total Games":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for j,row in enumerate(contents_row):
                    content = row.find_elements(By.TAG_NAME, 'em')
                    content_label = content[0].text
                    if content_label == self.event_from_pinnacle['points']:
                        if self.event_from_pinnacle['outcome'] == "under":
                            content_value = content[2].text
                            self.final_check_on_bet(content_value, content[2], "goalline")
                        elif self.event_from_pinnacle['outcome'] == "over":
                            content_value = content[1].text
                            self.final_check_on_bet(content_value, content[1], "goalline")
    
    def place_bet_for_moneyline_tennis(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for j, element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Winner":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-cell')
                for k, row in enumerate(contents_row):
                    if len(contents_row) > 0:
                        info_tag = row.find_elements(By.TAG_NAME, 'em')
                        if len(info_tag) == 2:
                            check_if_draw_win_or_lose = info_tag[0].text
                            vig_price_from_sportybet = info_tag[1].text
                            if (check_if_draw_win_or_lose == "Home" and
                                  self.event_from_pinnacle['outcome'] == "home" and
                                  self.event_from_pinnacle['points'] == ""):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
                            elif (check_if_draw_win_or_lose == "Away" and
                                  self.event_from_pinnacle['outcome'] == "away" and
                                  self.event_from_pinnacle['points'] == ""):
                                self.final_check_on_bet(vig_price_from_sportybet, row, "outcome")
       
    def place_bet_for_tennis_handicap(self):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.m-detail-market-default'))
        )
        for k,element in enumerate(elements):
            child_element = element.find_element(By.CSS_SELECTOR, '.text')
            child_element_name = child_element.text
            if child_element_name == "Game handicap" and self.event_from_pinnacle["periodNumber"] == "0":
                contents_row = element.find_elements(By.CSS_SELECTOR, '.m-table-row')
                for k,content_row in enumerate(contents_row):
                    content = content_row.find_elements(By.CSS_SELECTOR, '.m-table-cell')
                    if self.event_from_pinnacle['outcome'] == "home" and len(content)> 0 and len(content_row) > 0:
                        content_section = content[0].find_elements(By.TAG_NAME, 'em')
                        if content_section:
                            content_value_holder = content_section[0]
                            content_label = content_value_holder.text
                            if content_label == self.event_from_pinnacle['points']:
                                content_value_holder = content[1]
                                content_value = content_value_holder.text
                                self.final_check_on_bet(content_value, content_value_holder, "outcome")
                    elif self.event_from_pinnacle['outcome'] == "away" and len(content)> 0 and len(content_row) > 0:
                        content_section = content[1].find_elements(By.TAG_NAME, 'em')
                        if content_section:
                            content_value_holder = content_section[0]
                            content_label = content_value_holder.text
                            if content_label == self.event_from_pinnacle['points']:
                                content_value_holder = content[1]
                                content_value = content_value_holder.text
                                self.final_check_on_bet(content_value, content_value_holder, "outcome")

       
        
    def compare_bet_price(self, value):
        # Replace with your logic for comparing prices
        difference = 0.1
        return value - float(self.event_from_pinnacle['noVigPrice']) >= difference

    def wait(self, milliseconds):
        time.sleep(milliseconds)

    def activate_bet(self):
        self.driver.find_element(By.CLASS_NAME, "m-pay-text").click()
        time.sleep(2)
        self.driver.find_element(By.CLASS_NAME, "af-button").click()
        time.sleep(3)
        self.driver.find_element(By.CLASS_NAME, "af-button").click()
        print("bet plced succesfully")
        
    def to_home(self):
        self.driver.find_element(By.CLASS_NAME, 'home-icon').click()
        

    def final_check_on_bet(self, value, event, game_type):
        db = database()
        db.create_table()
        try:
            if self.compare_bet_price(float(value)):
                print("Vig price valid")
                ID = f"{self.event_from_pinnacle['home']}-{self.event_from_pinnacle['away']}-{self.event_from_pinnacle['starts']}"
                row = db.get_entry(ID)
                print("Got DB records")
                if row:
                    if (row[0] == 1 and game_type == "outcome") or \
                            (row[1] == 1 and game_type == "goalline") or \
                            (row[0] == 1 and row[1] == 1):
                        print("Cannot bet on this event")
                    elif (row[0] == 0) or (row[1] == 0):
                        event.click()
                        self.wait(2)
                        self.activate_bet()
                        db.update_record({"id":ID,"update": game_type})
                else:
                    event.click()
                    self.wait(2)
                    self.activate_bet()
                    db.insert(ID, {
                        "outcome": True if game_type == "outcome" else False,
                        "gameline": True if game_type == "goalline" else False
                    }, time.time())
                    self.wait(2)
                    db.insert(ID, {"update": game_type}, time.time())
        except Exception as e:
            print(e)
        finally:
            db.close_connection()

    def default():
        print("defult")
        
    def close_browser(self):
        self.driver.quit()
        