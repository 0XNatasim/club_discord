import os
import secrets
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from eth_account.messages import encode_defunct
from eth_account import Account
from utils import owns_ens_subdomain

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
MEMBER_ROLE_ID = os.getenv("MEMBER_ROLE_ID")
PORT = int(os.getenv("PORT", 5000))

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
        # https://discord.com/developers/docs/resources/guild#add-guild-member-role
        url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{discord_id}/roles/{MEMBER_ROLE_ID}"
        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json"
        }
        resp = requests.put(url, headers=headers)
        if resp.status_code not in [204, 201]:
            return jsonify({"error": "verified but role assignment failed", "details": resp.text}), 500
    except Exception as e:
        return jsonify({"error": "verified but role assignment failed", "details": str(e)}), 500

    return jsonify({"ok": True, "address": address})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)