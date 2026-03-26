import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dinner")
    async def dinner(self, ctx):
        await ctx.send("You eat dinner with Jay-Z Again.")

    @commands.command(name="ping")
    async def pingcmd(self, ctx):
        """the best command in existence"""
        await ctx.send(ctx.author.mention)

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")




async def setup(bot):
        # finally, adding the cog to the bot
    await bot.add_cog(Basic(bot=bot))