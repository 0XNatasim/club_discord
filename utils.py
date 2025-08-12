import requests
import os

ALCHEMY_KEY = os.getenv("ALCHEMY_KEY")
PARENT_NODE = os.getenv("PARENT_NODE")

def owns_ens_subdomain(address: str) -> bool:
    """
    Check via Alchemy if the wallet owns any ENS subdomain of the given parent node.
    """
    url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{ALCHEMY_KEY}/getNFTs"
    params = {
        "owner": address,
        "withMetadata": "false",
        "pageSize": 100
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()

        for nft in data.get("ownedNfts", []):
            contract_address = nft.get("contract", {}).get("address", "").lower()
            # ENS contract address is 0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85
            if contract_address == "0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85":
                # Optionally check tokenId starts with parent node
                token_id = nft.get("id", {}).get("tokenId", "").lower()
                if token_id.startswith(PARENT_NODE[2:].lower()):
                    return True
        return False

    except Exception as e:
        print(f"[ERROR] ENS check failed: {e}")
        return False
