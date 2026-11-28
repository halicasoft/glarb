import discord
from discord.ext import commands
import os
import os
import pickle
import time
from dotenv import load_dotenv
import datetime as dt
from datetime import timedelta
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
from fantraxapi.exceptions import DateNotInSeason
from zoneinfo import ZoneInfo
import random

from text_banks.players import MATCH_REPORTS, fetch_dialogue


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

username = os.getenv('FN_USER')
password = os.getenv('FN_PW') 
cookie_filepath = "fantraxloggedin.cookie" 

old_request = api.request 

league_id = os.getenv('LEAGUE_ID')



class Fantrax(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        api.request = new_request
        self.my_league = League(league_id)

    async def cog_load(self):
        print(f"Connecting to fantrax api...")
        # api.request = new_request
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @commands.command(name="lastnight")
    async def lastnight(self, ctx):
        # api.request = new_request # replace the old function with the new function
        dt_yday = (dt.datetime.now(ZoneInfo("America/New_York")) - timedelta(days=1)).date()
        try:
            by_team = self.my_league.live_scores(scoring_date=dt_yday)
        except DateNotInSeason:
                    await ctx.send("I don't think there were any games played yesterday.")
                    return
        rows = [(team_id, p) for team_id, players in by_team.items() for p in players]
        rows.sort(key=lambda row: row[1].points, reverse=True)
        best, worst = rows[0], rows[-1]
        best_team = self.my_league.team(best[0])
        worst_team = self.my_league.team(worst[0])
        report_template = random.choice(list(MATCH_REPORTS))
        intro = random.choice(list(fetch_dialogue))
        message = report_template.format(
            title=f"**League report for {dt_yday}:**\n",
            intro=intro,
            best_team=best_team,
            worst_team=worst_team,
            best=best,
            worst=worst
        )
        await ctx.send(
                            # f"**NOA recap for {dt_yday.strftime('%A')}**\n"
                            # f"Top performer: {best[1].name} with {int(best[1].points)} points!! {best_team} fans rejoice!\n"
                            # f"Bottom performance: {worst[1].name} with {int(worst[1].points)} points!! What a stinker!!\n"
                        message    
                         )

    
        
def new_request(league: "League", methods: list[Method] | Method) -> dict:
    try:
        if not league.logged_in:
            add_cookie_to_session(league.session) # Tries the login function when not logged in
        return old_request(league, methods) # Run old function
    except NotLoggedIn:
        add_cookie_to_session(league.session, ignore_cookie=True) # Adds/refreshes the cookie when NotLoggedIn is raised
        return new_request(league, methods) # Rerun the request


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

    
async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(Fantrax(bot=bot))