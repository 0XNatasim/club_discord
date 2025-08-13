import requests
import os

ALCHEMY_KEY = os.getenv("ALCHEMY_KEY")
PARENT_NODE = os.getenv("PARENT_NODE")

ENS_WRAPPER_NFT_CONTRACT = "0xd4416b13d2b3a9abae7acd5d6c2bbdbe25686401"

def owns_ens_subdomain(address: str) -> bool:
    """
    Check via Alchemy if the wallet owns any ENS subdomain of the configured parent node,
    using the ENS Name Wrapper ERC-1155 contract.
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
            token_id = nft.get("id", {}).get("tokenId", "").lower()

            # Check ENS Name Wrapper contract
            if contract_address == ENS_WRAPPER_NFT_CONTRACT:
                # Token ID is a 256-bit hex string (subdomain nodehash)
                # Check if the last 64 chars match PARENT_NODE (without the '0x')
                if token_id[-64:] == PARENT_NODE[2:].lower():
                    return True
        return False

    except Exception as e:
        print(f"[ERROR] ENS check failed: {e}")
        return False