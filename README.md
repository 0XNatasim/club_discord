# Discord ENS Verifier

A Discord bot + verification webserver that lets members sign a message with MetaMask to prove ownership of a wallet that owns a subdomain of a configured ENS parent node. If verification passes, the bot assigns a Discord role (`Club Member`).

## Files
- `main.py` — entrypoint (starts Flask webserver and Discord bot in same process)
- `discord_bot.py` — Discord interaction handler and `/verify` command
- `webserver.py` — Flask server that exposes `/request-nonce` and `/submit-signature`
- `utils.py` — signature verification, ENS helpers, Discord role assignment
- `verify.html` — frontend page that requests signature via MetaMask
- `.env.example` — environment variables template
- `requirements.txt`

## How it works (flow)
1. User types `/verify` in your Discord server.
2. Bot replies with an ephemeral link to `https://<BASE_URL>/verify.html?id=<discord_id>`.
3. User opens link, connects MetaMask, signs a nonce message.
4. The frontend POSTs signature to `/submit-signature`.
5. Server verifies signature and attempts to confirm the wallet owns a subdomain of the configured `PARENT_NODE`.
6. If yes, server calls Discord REST to add the `MEMBER_ROLE_ID` to the Discord user.

## Important: ENS ownership checking limitations
This implementation uses reverse ENS records as a light-weight way to confirm ownership (i.e., it will succeed if the wallet has a reverse ENS name that is a subdomain of the configured parent node). Reverse records are common but not guaranteed.

If you need robust verification (scan all subdomains under a parent node and confirm ownership), you should:
- Use The Graph queries to index ENS subdomains of your parent node, or
- Use Alchemy / Covalent / custom indexer to list ownership of subdomain NFTs (if you mint subdomains as NFTs).
I can add an example using Alchemy APIs or a GraphQL query if you want.

## Deployment (Render)
1. Push repository to GitHub.
2. Create a new Web Service on Render, connect the GitHub repo.
3. Set the Build Command: `pip install -r requirements.txt`
4. Set the Start Command: `gunicorn main:app --bind 0.0.0.0:$PORT`  
   - **Alternative:** If you keep the current `start_flask_in_thread()` approach, you can set `Start Command` to `python main.py`.
5. Add environment variables from `.env.example` to Render's dashboard (DISCORD_TOKEN, CLIENT_ID, GUILD_ID, MEMBER_ROLE_ID, BASE_URL, ALCHEMY_API_URL, PARENT_NODE).
6. Deploy.

## Notes & next steps
- Production: Replace in-memory `nonces` with Redis or a DB for persistence and safety.
- Improve ENS ownership checking by indexing subdomains (TheGraph or Alchemy + NFT ownership).
- Add rate-limiting to endpoints, log events, and add monitoring.

---

If you want, I can:
- Add a `Procfile` or `render.yaml` for Render.
- Swap the Flask server to run under Gunicorn properly (instead of `app.run` in a thread).
- Implement a full Alchemy/TheGraph based ENS ownership check (I can generate the code and the exact queries).
- Add tests and a GitHub Actions CI workflow for deployment.

Which of those next steps should I do now? If you want the Alchemy/TheGraph extension, I’ll include full code snippets and exact API calls.  
