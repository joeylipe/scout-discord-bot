# Scout 🐻

Scout is a personal Discord bot built with Python and [discord.py](https://discordpy.readthedocs.io/).

The goal of Scout is to monitor useful information and provide helpful updates directly in Discord.

## 🎮 Free Games

Scout's first major feature is free-game monitoring across PC game stores.

Scout currently checks for **free-to-keep games** — games that can be claimed for free and kept permanently once claimed.

### Supported Stores

* Epic Games Store
* Steam

### Current Commands

* `!ping` — Checks whether Scout is online and responds with its latency.
* `!free_games` — Checks supported stores for currently available free-to-keep games and displays them in Discord.

## 🚧 Project Status

Scout is currently in active development.

The initial bot infrastructure and free-game monitoring for Epic Games Store and Steam are working locally in a private Discord test server.

More stores and features will be added incrementally as they are developed and tested.

## 🛠️ Built With

* Python
* discord.py
* Git / GitHub
* REST APIs

## 📌 Current Status

Scout is connected to a private Discord test server and is currently being developed locally.

### Working

* Discord bot connection
* Bot status and latency reporting
* `!ping` command
* Epic Games Store free-game detection
* Steam free-to-keep detection
* Free-game expiration dates
* Discord game embeds
* Game artwork and store links

### Planned

* GOG free-game monitoring
* itch.io free-game monitoring
* Additional Scout commands
* Automatic free-game notifications
* Slash commands

Scout is being built incrementally, with each feature tested before moving on to the next.
