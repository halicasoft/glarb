import discord
from discord.ext import commands
import logging
import random
import json
import os
import aiohttp

class DnD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lastnight")
    async def lastnight(self, ctx, endpoint, query: str = None):

        if query is None:
            await ctx.send("Please provide a valid topic and query for DnD. available topics: spells, cover, equipment, conditions")
            return