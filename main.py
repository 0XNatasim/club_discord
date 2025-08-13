import os
import logging
import threading
from dotenv import load_dotenv

# --- Discord bot imports ---
import discord
from discord import app_commands

# --- Flask imports ---
from flask import Flask, request, jsonify, send_from_directory
import secrets
from eth_account.messages import encode_defunct
from eth_account import Account
from utils import owns_ens_subdomain

load_dotenv()

# --- Discord bot setup ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BASE_URL = os.getenv("BASE_URL")
GUILD_ID = os.getenv("GUILD_ID")
MEMBER_ROLE_ID = os.getenv("MEMBER_ROLE_ID")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="verify", description="Verify your wallet with MetaMask", guild=discord.Object(id=GUILD_ID))
async def verify_command(interaction: discord.Interaction):
    verify_url = f"{BASE_URL.rstrip('/')}/verify.html?id={interaction.user.id}"
    await interaction.response.send_message(f"Click here to verify your wallet:\n{verify_url}", ephemeral=True)

@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user}")
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        logging.info("Slash commands synced.")
    except Exception as e:
        logging.exception("Failed to sync commands: %s", e)

def start_discord_bot():
    if not DISCORD_TOKEN:
        logging.error("DISCORD_TOKEN is not set.")
        exit(1)
    bot.run(DISCORD_TOKEN)

# --- Flask webserver setup ---
PORT = int(os.getenv("PORT", 5000))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
MEMBER_ROLE_ID = os.getenv("MEMBER_ROLE_ID")

nonces = {}
app = Flask(__name__, static_folder=".")

@app.route("/verify.html")
def serve_verify_html():
    return send_from_directory(".", "verify.html")

@app.route("/request-nonce")
def request_nonce():
    discord_id = request.args.get("discordId")
    if not discord_id:
        return jsonify({"error": "missing discordId"}), 400

    nonce = secrets.token_hex(16)
    nonces[discord_id] = nonce
    message = f"ENS Club verification — Discord ID: {discord_id}\nNonce: {nonce}\nDo not share this message."
    return jsonify({"nonce": nonce, "message": message})

@app.route("/submit-signature", methods=["POST"])
def submit_signature():
    data = request.get_json()
    discord_id = data.get("discordId")
    address = data.get("address")
    signature = data.get("signature")

    if not (discord_id and address and signature):
        return jsonify({"error": "missing fields"}), 400

    nonce = nonces.get(discord_id)
    if not nonce:
        return jsonify({"error": "no pending nonce"}), 400

    message = f"ENS Club verification — Discord ID: {discord_id}\nNonce: {nonce}\nDo not share this message."
    encoded_message = encode_defunct(text=message)
    try:
        recovered_address = Account.recover_message(encoded_message, signature=signature)
    except Exception as e:
        return jsonify({"error": "invalid signature", "details": str(e)}), 400

    if recovered_address.lower() != address.lower():
        return jsonify({"error": "signature does not match address"}), 400

    del nonces[discord_id]

    # ENS ownership check
    if not owns_ens_subdomain(address):
        return jsonify({"error": "You do not own a valid subdomain"}), 403

    # Assign Discord role using REST API
    try:
        url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{discord_id}/roles/{MEMBER_ROLE_ID}"
        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json"
        }
        import requests
        resp = requests.put(url, headers=headers)
        if resp.status_code not in [204, 201]:
            return jsonify({"error": "verified but role assignment failed", "details": resp.text}), 500
    except Exception as e:
        return jsonify({"error": "verified but role assignment failed", "details": str(e)}), 500

    return jsonify({"ok": True, "address": address})

def start_flask():
    app.run(host="0.0.0.0", port=PORT)

# --- Launch both services ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    start_discord_bot()