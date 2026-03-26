import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import aiohttp
import logging

# idea of events vs commands. Events are when things happen, but commands are like talking directly to the bot
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(handlers=[handler], level=logging.INFO)
discord.utils.setup_logging()

class Glarb(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        await self.load_extension("basic")
        await self.load_extension("scryfall")
        print("Loaded cogs!")
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        await super().close()
    
    async def http_get_json(self, url):
        async with self.session.get(url) as response:
            return await response.json()
    async def http_get_img(self, url):
        async with self.session.get(url) as response:
            return await response.read()

async def main():
     bot = Glarb()
     async with bot:
          await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    