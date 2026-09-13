# ==============================
# IMPORTS
# ==============================

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


# ==============================
# CONFIGURATION
# ==============================

load_dotenv()

token = os.getenv("DISCORD_TOKEN")


# ==============================
# DISCORD INTENTS
# ==============================

intents = discord.Intents.default()
intents.message_content = True


# ==============================
# BOT SETUP
# ==============================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==============================
# BOT EVENTS
# ==============================

@bot.event
async def on_ready():
    print(f"Scout is online as {bot.user}")


# ==============================
# #1 CORE / UTILITY COMMANDS
# ==============================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")


# ==============================
# START SCOUT
# ==============================

bot.run(token)