# ==============================
# IMPORTS
# ==============================

import os
import re
import json
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

# ------------------------------
# FREE GAME DATA
# ------------------------------

class FreeGame:

    def __init__(
        self,
        title,
        description,
        store,
        original_price,
        url,
        image_url,
        available_until=None
    ):

        self.title = title
        self.description = description
        self.store = store
        self.original_price = original_price
        self.url = url
        self.image_url = image_url
        self.available_until = available_until


# ------------------------------
# EPIC
# ------------------------------

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

                discount = offer.get(
                    "discountSetting",
                    {}
                ).get(
                    "discountPercentage"
                )

                if discount == 0:

                    free_games_found.append(
                        FreeGame(
                            title=game.get(
                                "title",
                                "Unknown Game"
                            ),
                            description=game.get(
                                "description",
                                "No description available."
                            ),
                            store="Epic Games Store",
                            original_price=(
                                game.get("price", {})
                                .get("totalPrice", {})
                                .get("originalPrice")
                            ),
                            url=get_game_url(game),
                            image_url=get_game_image(game),
                            available_until=offer.get("endDate")
                        )
                    )

                    break

            if (
                free_games_found
                and free_games_found[-1].title == game.get("title")
            ):
                break

    # ------------------------------
    # STEAM
    # ------------------------------

    candidates = get_steam_free_candidates()

    for app_id in candidates:

        app = get_steam_app_details(app_id)

        if not app:
            continue

        if is_steam_free_to_keep(app):

            price_info = app.get("price_overview")

            original_price = None

            if price_info:
                original_price = price_info.get("initial")

            free_games_found.append(
                FreeGame(
                    title=app.get(
                        "name",
                        "Unknown Game"
                    ),
                    description=app.get(
                        "short_description",
                        "No description available."
                    ),
                    store="Steam",
                    original_price=original_price,
                    url=(
                        f"https://store.steampowered.com/app/"
                        f"{app.get('steam_appid')}/"
                    ),
                    image_url=app.get(
                        "header_image"
                    ),
                    available_until=get_steam_promotion_end(
                        app.get("steam_appid")
                    )
                )
            )

    if not free_games_found:

        await ctx.send(
            "🐻 **Scout**\n"
            "No free games found right now."
        )

        return

    for game in free_games_found:

        title = game.title
        description = game.description
        game_url = game.url
        image_url = game.image_url

        original_price = game.original_price

        if original_price is not None:

            original_price = original_price / 100
            original_price_text = f"${original_price:,.2f}"

        else:

            original_price_text = "Price unavailable"

        end_date = game.available_until

        if end_date:

            end_datetime = datetime.fromisoformat(
                end_date.replace("Z", "+00:00")
            )

            end_timestamp = int(
                end_datetime.timestamp()
            )

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
            value=game.store,
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
            name=f"🔗 View game on {game.store}",
            value=f"[Open {title}]({game_url})",
            inline=False
        )

        await ctx.send(embed=embed)


# ------------------------------
# STEAM
# ------------------------------

def get_steam_free_candidates():

    url = "https://store.steampowered.com/search/results/"

    response = requests.get(
        url,
        params={
            "query": "",
            "start": 0,
            "count": 100,
            "infinite": 1,
            "cc": "us",
            "l": "english",
            "specials": 1,
            "maxprice": "free",
            "hidef2p": 1,
            "json": 1
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    html = data.get(
        "results_html",
        ""
    )

    app_ids = []

    matches = re.findall(
        r'data-ds-appid="(\d+)"',
        html
    )

    for app_id in matches:

        app_id = int(app_id)

        if app_id not in app_ids:
            app_ids.append(app_id)

    return app_ids


def get_steam_app_details(app_id):

    url = "https://store.steampowered.com/api/appdetails"

    response = requests.get(
        url,
        params={
            "appids": app_id,
            "cc": "us",
            "l": "english"
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    app_data = data.get(
        str(app_id),
        {}
    )

    if not app_data.get("success"):
        return None

    return app_data.get("data")


def get_steam_promotion_end(app_id):

    url = "https://api.steampowered.com/IStoreBrowseService/GetItems/v1"

    request_data = {
        "ids": [
            {
                "appid": app_id
            }
        ],
        "context": {
            "language": "english",
            "country_code": "US",
            "steam_realm": 1
        },
        "data_request": {
            "include_all_purchase_options": True
        }
    }

    response = requests.get(
        url,
        params={
            "input_json": json.dumps(request_data)
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    store_items = data.get(
        "response",
        {}
    ).get(
        "store_items",
        []
    )

    if not store_items:
        return None

    purchase_option = store_items[0].get(
        "best_purchase_option",
        {}
    )

    free_to_keep_ends = purchase_option.get(
        "free_to_keep_ends"
    )

    if not free_to_keep_ends:
        return None

    return datetime.fromtimestamp(
        free_to_keep_ends,
        tz=timezone.utc
    ).isoformat()


def get_steam_package_details(package_id):

    url = "https://store.steampowered.com/api/packagedetails"

    response = requests.get(
        url,
        params={
            "packageids": package_id,
            "cc": "us",
            "l": "english"
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    package_data = data.get(
        str(package_id),
        {}
    )

    if not package_data.get("success"):
        return None

    return package_data.get("data")


def is_steam_free_to_keep(app):

    if not app:
        return False

    if app.get("type") != "game":
        return False

    price_overview = app.get("price_overview")

    if not price_overview:
        return False

    if price_overview.get("discount_percent") != 100:
        return False

    packages = app.get("packages", [])

    for package_id in packages:

        package = get_steam_package_details(package_id)

        if not package:
            continue

        package_name = package.get(
            "name",
            ""
        ).lower()

        if "limited free promotional package" in package_name:
            return True

    return False


# ==============================
# START SCOUT
# ==============================

bot.run(token)