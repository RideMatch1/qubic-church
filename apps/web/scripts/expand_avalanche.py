import os
import sys
import time
import base64
import requests
from dotenv import load_dotenv
from qubipy.crypto.utils import (
    get_public_key_from_identity,
    get_subseed_from_seed,
    get_private_key_from_subseed,
    get_public_key_from_private_key,
    kangaroo_twelve,
    sign,
    get_identity_from_public_key
)

# Configuration
load_dotenv()
RPC_URL = "https://rpc.qubic.org"

AVALANCHE_TARGETS = {
    "ROOT-BETA (18,110)": {"id": "OUMLINFCVWOAFCCPDDRUJARXUKJBJQUYVZFLIUKUUATMEQEIWOIUXHYGQERC", "amount": 143},
    "MEMORY (21,21)":    {"id": "VHGZIFEFAPDXEAMCEMNQWJKMVCPAVTNXMECIEFKXXGOGLMYKKERCEMIDZYSD", "amount": 137},
    "VISION (64,64)":    {"id": "WMPLINKVMRMPWBMOLFVRDIRJWJCAQDLTLJZJSRWMIEQOPJZWAESVWEFEFZMC", "amount": 225},
    "EXIT (82,39)":      {"id": "YLGSNIMGRKONPEBTLCRLYHQDFHEAKMUSRKYOGLPFAFDOFUUYVRBJTNSAXUSM", "amount": 100}
}

def execute_avalanche_expansion():
    print("🏔️ EXECUTING AVALANCHE EXPANSION (Sector Multi-Pulse)...")
    print("-" * 65)
    
    seed_str = os.getenv("MASTER_SEED")
    if not seed_str:
        print("[X] ERROR: MASTER_SEED not found")
        return

    # Fetch current tick
    try:
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
        tick_info = r.json()
        current_tick = tick_info.get('tickInfo', {}).get('tick', 0)
    except:
        return

    # Derive Master Keys
    seed_bytes = seed_str.encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv_key = get_private_key_from_subseed(subseed)
    pub_key = get_public_key_from_private_key(priv_key)

    for name, target in AVALANCHE_TARGETS.items():
        target_tick = current_tick + 12
        dest_id = target["id"]
        amount = target["amount"]
        
        print(f"[*] Pulsing {name:20} | Amount: {amount:3} QU | Tick: {target_tick}")
        
        dest_pub_key = get_public_key_from_identity(dest_id)
        
        # Tx Construction
        tx_data = bytearray(80)
        tx_data[0:32] = pub_key
        tx_data[32:64] = dest_pub_key
        tx_data[64:72] = (amount).to_bytes(8, byteorder='little')
        tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
        
        # Sign
        digest = kangaroo_twelve(bytes(tx_data), 80, 32)
        signature = sign(subseed, pub_key, digest)
        full_tx = tx_data + signature
        
        # Broadcast
        b64_tx = base64.b64encode(full_tx).decode('utf-8')
        requests.post(f"{RPC_URL}/v1/broadcast-transaction", json={"encodedTransaction": b64_tx}, timeout=30)
        
    print("\n" + "=" * 65)
    print("🔥 THE AVALANCHE HAS BEEN EXPANDED. ALL STRATEGIC SECTORS PULSING. 🔥")
    print("=" * 65)

if __name__ == "__main__":
    execute_avalanche_expansion()
