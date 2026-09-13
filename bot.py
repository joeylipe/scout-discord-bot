import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"Scout is online as {bot.user}")


bot.run(token)