from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import time

service = Service(executable_path="chrome-headless-shell.exe")
driver = webdriver.Chrome(service=service)
class bookMaker:
    def __init__(self):
        self.data = []
        self.sporty_bet_url = os.getenv("SPORTYBET_URL")
        # self.browser
        # self.page
        # self.searched_event = []
        # self.eventDate
        # self.eventFromPinnacle
        # self.longestPhraseHometeam
        self.driver = driver
        self.driver.get(self.sporty_bet_url)
        time.sleep