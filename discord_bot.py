# discord_bot.py
import os
import logging
import asyncio

from dotenv import load_dotenv
load_dotenv()

import discord
from discord import app_commands

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
GUILD_ID = os.getenv("GUILD_ID")
MEMBER_ROLE_ID = os.getenv("MEMBER_ROLE_ID")
BASE_URL = os.getenv("BASE_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-bot")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="verify", description="Verify your wallet with MetaMask", guild=discord.Object(id=GUILD_ID))
async def verify_command(interaction: discord.Interaction):
    """Reply with ephemeral link to verification page"""
    user_id = interaction.user.id
    verify_url = f"{BASE_URL.rstrip('/')}/verify.html?id={user_id}"
    await interaction.response.send_message(f"Click here to verify your wallet:\n{verify_url}", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f"Logged in to Discord as {bot.user} (id: {bot.user.id})")
    try:
        # Sync commands to guild
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        logger.info("Slash commands synced.")
    except Exception as e:
        logger.exception("Failed to sync commands: %s", e)

async def start_discord_bot():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set.")
        raise SystemExit(1)
    await bot.start(DISCORD_TOKEN)
