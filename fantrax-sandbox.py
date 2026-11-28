import os
import pickle
import time
from dotenv import load_dotenv
import datetime as dt

from requests import Session
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from fantraxapi import League, NotLoggedIn, api
from fantraxapi.api import Method

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

username = os.getenv('FN_USER') # Provide your Fantrax Username here
password = os.getenv('FN_PW') # Provide your Fantrax Password here
cookie_filepath = "fantraxloggedin.cookie" # Name of the saved Cookie file

old_request = api.request # Saves the old function


def new_request(league: "League", methods: list[Method] | Method) -> dict:
    try:
        if not league.logged_in:
            add_cookie_to_session(league.session) # Tries the login function when not logged in
        return old_request(league, methods) # Run old function
    except NotLoggedIn:
        add_cookie_to_session(league.session, ignore_cookie=True) # Adds/refreshes the cookie when NotLoggedIn is raised
        return new_request(league, methods) # Rerun the request

print(f'trying to req')
api.request = new_request # replace the old function with the new function


def add_cookie_to_session(session: Session, ignore_cookie: bool = False) -> None:
    if not ignore_cookie and os.path.exists(cookie_filepath):
        with open(cookie_filepath, "rb") as f:
            for cookie in pickle.load(f):
                session.cookies.set(cookie["name"], cookie["value"])
    else:
        service = Service(ChromeDriverManager().install())

        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--window-size=1920,1600")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")

        with webdriver.Chrome(service=service, options=options) as driver:
            print(f'visiting fantrax.com')
            driver.get("https://www.fantrax.com/login")
            username_box = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@formcontrolname='email']")))
            print(f'entering user')
            username_box.send_keys(username)
            password_box = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@formcontrolname='password']")))
            print(f'entering pw')
            password_box.send_keys(password)
            print(f'sending')
            password_box.send_keys(Keys.ENTER)
            time.sleep(5)
            cookies = driver.get_cookies()
            with open(cookie_filepath, "wb") as cookie_file:
                pickle.dump(driver.get_cookies(), cookie_file)
            print(f'setting cookies')
            for cookie in cookies:
                session.cookies.set(cookie["name"], cookie["value"])

league_id = os.getenv('LEAGUE_ID')

my_league = League(league_id)

dt_now = dt.datetime.now()
print(f"------------ Night report for {dt_now.strftime('%A')} ------------")
print("-------------------------------------------------")
by_team = my_league.live_scores(scoring_date=dt.date(2026, 11, 20))


rows = [(team_id, p) for team_id, players in by_team.items() for p in players]
rows.sort(key=lambda row: row[1].points, reverse=True)

best, worst = rows[0], rows[-1]

best_team = my_league.team(best[0])

print(f"Top performer: {best[1]} with {int(best[1].points)} points!! {best_team} fans rejoice!")
print(f"Bottom performance: {worst[1]} with {int(worst[1].points)} points!! What a stinker!!")

