# ==============================
# IMPORTS
# ==============================

import os
import requests

from datetime import datetime, timezone 

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

    print()
    print("╔══════════════════════════════════════════════╗")
    print("║                                              ║")
    print("║                    🐻 SCOUT                  ║")
    print("║                                              ║")
    print("║             Discord Monitoring Bot           ║")
    print("║                                              ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  Status       ONLINE                         ║")
    print(f"║  Bot          {str(bot.user):<30}║")
    print("║  Discord      CONNECTED                      ║")
    print(f"║  Latency      {round(bot.latency * 1000)} ms{'':<24}║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print("[SCOUT] Connection established.")
    print("[SCOUT] Commands loaded.")
    print("[SCOUT] Ready.")
    print()

# ==============================
# #1 CORE / UTILITY COMMANDS
# ==============================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

# ==============================
# #2 FREE GAMES
# ==============================
# ==============================
# #2 FREE GAMES
# ==============================

def get_epic_free_games():

    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data["data"]["Catalog"]["searchStore"]["elements"]


def get_game_image(game):

    key_images = game.get("keyImages", [])

    preferred_types = [
        "OfferImageWide",
        "DieselStoreFrontWide",
        "OfferImageTall"
    ]

    for image_type in preferred_types:

        for image in key_images:

            if image.get("type") == image_type:
                return image.get("url")

    return None

def get_game_url(game):

    # Epic's catalog mapping contains the actual public product-page slug.
    catalog_ns = game.get("catalogNs", {})
    mappings = catalog_ns.get("mappings", [])

    for mapping in mappings:

        if mapping.get("pageType") == "productHome":

            page_slug = mapping.get("pageSlug")

            if page_slug:
                return f"https://store.epicgames.com/p/{page_slug}"

    # Some games expose the mapping through offerMappings instead.
    offer_mappings = game.get("offerMappings", [])

    for mapping in offer_mappings:

        if mapping.get("pageType") == "productHome":

            page_slug = mapping.get("pageSlug")

            if page_slug:
                return f"https://store.epicgames.com/p/{page_slug}"

    # Fallback
    return "https://store.epicgames.com/"


@bot.command()
async def free_games(ctx):

    games = get_epic_free_games()

    free_games_found = []

    for game in games:

        promotions = game.get("promotions")

        if not promotions:
            continue

        for promotion in promotions.get("promotionalOffers", []):

            for offer in promotion.get("promotionalOffers", []):

                discount = offer.get("discountSetting", {}).get("discountPercentage")

                if discount == 0:

                    free_games_found.append({
                        "game": game,
                        "offer": offer
                    })

                    break

            if free_games_found and free_games_found[-1]["game"] == game:
                break

    if not free_games_found:

        await ctx.send(
            "🐻 **Scout**\n"
            "No free games found on the Epic Games Store right now."
        )

        return

    for item in free_games_found:

        game = item["game"]
        offer = item["offer"]

        title = game.get("title", "Unknown Game")
        description = game.get(
            "description",
            "No description available."
        )

        game_url = get_game_url(game)
        image_url = get_game_image(game)

        # ------------------------------
        # ORIGINAL PRICE
        # ------------------------------

        price_info = game.get("price", {})
        total_price = price_info.get("totalPrice", {})
        original_price = total_price.get("originalPrice")

        if original_price is not None:

            original_price = original_price / 100
            original_price_text = f"${original_price:,.2f}"

        else:

            original_price_text = "Price unavailable"

        # ------------------------------
        # END DATE
        # ------------------------------

        end_date = offer.get("endDate")

        if end_date:

            end_datetime = datetime.fromisoformat(
                end_date.replace("Z", "+00:00")
            )

            end_timestamp = int(end_datetime.timestamp())

            available_until = f"<t:{end_timestamp}:R>"

        else:

            available_until = "Unknown"

        # ------------------------------
        # DISCORD EMBED
        # ------------------------------

        embed = discord.Embed(
            title=f"🎮 {title}",
            description=description,
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Store",
            value="Epic Games Store",
            inline=False
        )

        embed.add_field(
            name="Was",
            value=f"~~{original_price_text}~~",
            inline=True
        )

        embed.add_field(
            name="Price",
            value="**FREE**",
            inline=True
        )

        embed.add_field(
            name="Available Until",
            value=available_until,
            inline=False
        )

        if image_url:
            embed.set_image(url=image_url)

        embed.add_field(
            name="🔗 View game on Epic Games Store",
            value=f"[Open {title}]({game_url})",
            inline=False
        )

        await ctx.send(embed=embed)
# ==============================
# START SCOUT
# ==============================

bot.run(token)