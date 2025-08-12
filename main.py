import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BASE_URL = os.getenv("BASE_URL")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.slash_command(name="verify", description="Verify your wallet with MetaMask")
async def verify(ctx):
    verify_url = f"{BASE_URL}/verify.html?id={ctx.author.id}"
    await ctx.respond(f"Click here to verify your wallet:\n{verify_url}", ephemeral=True)

bot.run(DISCORD_TOKEN)
