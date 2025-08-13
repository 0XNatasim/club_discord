import os
import logging
from dotenv import load_dotenv
import discord
from discord import app_commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BASE_URL = os.getenv("BASE_URL")
GUILD_ID = os.getenv("GUILD_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="verify", description="Verify your wallet with MetaMask", guild=discord.Object(id=GUILD_ID))
async def verify_command(interaction: discord.Interaction):
    verify_url = f"{BASE_URL}/verify.html?id={interaction.user.id}"
    await interaction.response.send_message(f"Click here to verify your wallet:\n{verify_url}", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user}")
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        logger.info("Slash commands synced.")
    except Exception as e:
        logger.exception("Failed to sync commands: %s", e)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set.")
        exit(1)
    bot.run(DISCORD_TOKEN)