import discord
from discord.ext import commands
import logging
import random
import json
import os
<<<<<<< HEAD

# to do: error handling, refactor

ENDPOINTS = ["spells", "cover", "items", "conditions"]
=======
import aiohttp

# to do: error handling, refactor

ENDPOINTS = ["spells", "cover", "equipment", "conditions"]
>>>>>>> a692db0 (adding basic fantrax stuff and prep work)

class DnD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_for_fog(self, response):
        # this function needs cleaning up, check for fog properly, error handling etc
        response_str = "".join(item for item in response['desc'])
        response['desc'][0] = response_str.replace("fog", "frog")
        return response


    @commands.command(name="dnd")
    async def dnd(self, ctx, endpoint, query: str = None):
        #prob could do with a refactor and error handling 
<<<<<<< HEAD
        if query is None or endpoint not in ENDPOINTS:
            await ctx.send("Please provide a valid topic and query for DnD. available topics: spells, cover, items, conditions")
=======
        # this is gonna return a 404 a lot of the time unless the user writes something exact. so we need to handle this a lot better
        if query is None or endpoint not in ENDPOINTS:
            await ctx.send("Please provide a valid topic and query for DnD. available topics: spells, cover, equipment, conditions")
>>>>>>> a692db0 (adding basic fantrax stuff and prep work)
            return

        url = f"https://www.dnd5eapi.co/api/2014/{endpoint}/{query}"

<<<<<<< HEAD
        response = await self.bot.http_get(url, "json")
=======
        response = await self.bot.http_get(url, "json")            
>>>>>>> a692db0 (adding basic fantrax stuff and prep work)

        if endpoint == "spells":
            response = await self.check_for_fog(response)

        if response is None:
            await ctx.send("No results found for your query. you probably typed something wrong")
            return
        
        #to-do: set custom response formatting for different endpoints (as they have different relevant values)
        await ctx.send(f"**{response['name']}**\n{response['desc'][0]}")
<<<<<<< HEAD
    
=======
            
>>>>>>> a692db0 (adding basic fantrax stuff and prep work)
    @commands.command(name="roll")
    async def roll(self, ctx, dice: str):
        try:
            num_dice, num_sides = map(int, dice.split("d"))
            if num_sides > 500 or num_dice > 30:
                await ctx.send("glarb can't count that high")
                
            else:
                rolls = []
                for i in range(0, num_dice):
                    rolls.append(random.randint(1, num_sides))
                total = sum(rolls)
                await ctx.send(f"{ctx.author.mention} rolled **{total}** ({", ".join(map(str, rolls))}).")

        except ValueError:
            await ctx.send("invalid format - example accepted input: **2d6**")   


    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")


async def setup(bot):

    await bot.add_cog(DnD(bot=bot))
