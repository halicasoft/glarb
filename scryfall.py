from random import random

import discord
from discord.ext import commands
from dotenv import load_dotenv
import io
import random

url = "https://api.scryfall.com/cards/"

fetch_dialogue = [
    "I gaze into the swirling portents, and I see the following omen:", 
    "From the mists of my orb, a vision emerges:", 
    "I look into the tea leaves, and the tea looks back:", 
    "The entrails of some poor soul foretell this future calamity:",
    "My dowsing rod entreats this drop of knowledge to the surface:"]

wubrg_values = [
    'W',
    'U',
    'B',
    'R',
    'G'
]

GUILD_NAMES = {
    "WHITE": "W",
    "BLUE": "U",
    "BLACK": "B",
    "RED": "R",
    "GREEN": "G",
    # 2 colour
    'AZORIUS': 'WU',
    'DIMIR': 'UB',
    'RAKDOS': 'BR',
    'GRUUL': 'RG',
    'SELESNYA': 'WG',
    'ORZHOV': 'WB',
    'IZZET': 'UR',
    'GOLGARI': 'BG',
    'BOROS': 'WR',
    'SIMIC': 'UG',
    # 3 colour
    'BANT': 'WUG',
    'ESPER': 'WUB',
    'GRIXIS': 'UBR',
    'JUND': 'BRG',
    'NAYA': 'WRG',
    'MARDU': 'WBR',
    'TEMUR': 'URG',
    'ABZAN': 'WBG',
    'JESKAI': 'WUR',
    'SULTAI': 'UBG',
    # 4 colour
    'YORE': 'WUBR',
    'GLINT': 'UBRG',
    'DUNE': 'WBRG',
    'INK': 'WURG',
    'WITCH': 'WUBG',
    # 5 colour
    'WUBRG': 'WUBRG',
}

class Scryfall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    """

    fetch commander command process:

    capitalise
    ↓
    check if guild name. if so return value
    ↓
    if not guild name: WUBRG sort and check again. glarb error if no
    ↓
    pass normalised value into scryfall
    ↓
    reclaim key and pass back to user
    """


    @commands.command()
    async def commander(self, ctx, identity: str = None):

        if identity is None:

            # default behavior is fetch any commander
            response = await self.bot.http_get(url + "random?q=is%3Acommander", "json")

            image_url = response["image_uris"]["normal"]
            image_response = await self.bot.http_get(image_url, "img")
            image_file = discord.File(io.BytesIO(image_response), filename="card.png")

            await ctx.send(random.choice(fetch_dialogue) + "\n**" + response["name"] + "**", file=image_file)
            return

        normalised = identity.upper()   

        if normalised in GUILD_NAMES:
            normalised = GUILD_NAMES[normalised]
        else:
            normalised = ''.join(sorted(normalised, key=lambda x: wubrg_values.index(x)))
            if normalised not in GUILD_NAMES.values():
                await ctx.send("Invalid identity. Please provide a WUBRG combination or guild name.")
                return

        prefix = random.choice(fetch_dialogue)
        
        card, search_id = await self.get_random_commander(normalised)
        await ctx.send(f"{prefix} your random {search_id[0].capitalize()} commander is: **{card['name']}**\n{card['scryfall_uri']}")

    async def get_random_commander(self, identity: str):

        if identity in GUILD_NAMES.values():
                    search_id = [key for key, value in GUILD_NAMES.items() if value == identity]     
        
        url = f'https://api.scryfall.com/cards/random?q=id%3D{identity}+is%3Acommander'
        data = await self.bot.http_get(url, return_type="json")

        return data, search_id

async def setup(bot):
    await bot.add_cog(Scryfall(bot=bot))