import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import io
import aiohttp

url = "https://api.scryfall.com/cards/"

class Scryfall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @commands.command(name="random")
    async def random(self, ctx):
        response = await self.bot.http_get_json(url + "random")

        image_url = response["image_uris"]["normal"]
        image_response = await self.bot.http_get_img(image_url)
        image_file = discord.File(io.BytesIO(image_response), filename="card.png")

        await ctx.send("From my orb, I fetch the following portent:")
        await ctx.send("**" + response["name"] + "**", file=image_file)

    
    @commands.group()
    async def commander(self, ctx):
        if ctx.invoked_subcommand is None:
            # default behavior is fetch any commander
            response = await self.bot.http_get_json(url + "random?q=is%3Acommander")

            image_url = response["image_uris"]["normal"]
            image_response = await self.bot.http_get_img(image_url)
            image_file = discord.File(io.BytesIO(image_response), filename="card.png")

            await ctx.send("From my orb, I fetch the following commander:")
            await ctx.send("**" + response["name"] + "**", file=image_file)
    
    @commander.command(name="gruul")
    async def gruul(self, ctx): 
        response = await self.bot.http_get_json(url + "random?q=id%3DGR+is%3Acommander")

        image_url = response["image_uris"]["normal"]
        image_response = await self.bot.http_get_img(image_url)
        image_file = discord.File(io.BytesIO(image_response), filename="card.png")

        await ctx.send("I look into the swirling portents, and I fetch the following Gruul commander:")
        await ctx.send("**" + response["name"] + "**", file=image_file)




async def setup(bot):
        # finally, adding the cog to the bot
    await bot.add_cog(Scryfall(bot=bot))