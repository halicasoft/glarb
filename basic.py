import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import random
from text_banks.dinner import dinner_outcomes
import json
import os
import locale

ECONOMY_FILE = "economy.json"
locale.setlocale(locale.LC_ALL, "C")


def format_currency(amount):
    return "${:,.2f}".format(amount)


def load_economy():
    if not os.path.exists(ECONOMY_FILE):
        return {}
    with open(ECONOMY_FILE, "r") as f:
        return json.load(f)


def save_economy(data):
    with open(ECONOMY_FILE, "w") as f:
        json.dump(data, f, indent=4)


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prev_outcome_text = None

    @commands.command(name="dinner")
    async def dinner(self, ctx):

        outcome_text, amount = random.choice(list(dinner_outcomes.items()))
        while outcome_text == self.prev_outcome_text:
            outcome_text, amount = random.choice(list(dinner_outcomes.items()))
        self.prev_outcome_text = outcome_text

        economy = load_economy()
        user_id = str(ctx.author.id)
        economy[user_id] = economy.get(user_id, 0) + amount
        save_economy(economy)
        if amount == 0:
            outcome_text += " Your balance remains unchanged."
        else:
            outcome_text += (
                f" Your new balance is **{format_currency(economy[user_id])}**."
            )
        await ctx.send(outcome_text)

    @commands.command(name="balance")
    async def balance(self, ctx):
        economy = load_economy()
        user_id = str(ctx.author.id)
        balance = economy.get(user_id, 0)
        if balance < 0:
            await ctx.send(f"You owe Glarb **{format_currency(-balance)}**.")
        else:
            await ctx.send(f"Your current balance is **{format_currency(balance)}**.")

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        economy = load_economy()
        sorted_users = sorted(economy.items(), key=lambda x: x[1], reverse=True)
        leaderboard = "\n".join(
            f"<@{user_id}>: {format_currency(balance)}"
            for user_id, balance in sorted_users[:5]
        )
        await ctx.send(f"**Leaderboard:**\n{leaderboard}")

    @commands.command(name="reset")
    async def reset(self, ctx):
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy[user_id] = 0
        save_economy(economy)
        await ctx.send("Your balance has been reset to $0.00.")

    @commands.command(name="commands")
    async def helpcmd(self, ctx):
        await ctx.send(
            "I am Glarb, the slipperiest sorcerer in the realm. I can play music and do some MtG related stuff. \n\n"
            "**Commands:**\n\n"
            "!play <video> - play a video\n"
            "!skip - skip the current video\n"
            "!stop - stop the music and disconnect\n"
            "!loop <video> - loop a video\n"
            "!playlist <name> - play a predefined playlist (battle or exploring)\n"
            "!shuffle - shuffle the current playlist\n"
            "!queue - show the current queue\n"
            "!pause - pause the current track\n"
            "!resume - resume the current track\n"
            "!dinner - have dinner with Jay-Z\n"
            "!balance - check your balance\n"
        )

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")


async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(Basic(bot=bot))
