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
VOID_ID = "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB" # Sector (0, 0)
WAKEUP_AMOUNT = 222

def execute_wakeup_pulse():
    print("📢 EXECUTING GLOBAL WAKE-UP PULSE (222 QUBIC)...")
    print("-" * 60)
    
    seed_str = os.getenv("MASTER_SEED")
    if not seed_str:
        print("[X] ERROR: MASTER_SEED not found in .env")
        return

    # 1. Fetch current tick
    try:
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
        r.raise_for_status()
        tick_info = r.json()
        current_tick = tick_info.get('tickInfo', {}).get('tick', 0)
    except Exception as e:
        print(f"[X] ERROR fetching tick info: {e}")
        return

    target_tick = current_tick + 10 
    print(f"[*] Current Tick: {current_tick} | Target Tick: {target_tick}")
    print(f"[*] Target Identity: THE VOID (0, 0)")
    print(f"[*] Signal Frequency: {WAKEUP_AMOUNT} QUBIC (Master Peak)")
    
    # 2. Derive Keys
    seed_bytes = seed_str.encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv_key = get_private_key_from_subseed(subseed)
    pub_key = get_public_key_from_private_key(priv_key)
    
    dest_pub_key = get_public_key_from_identity(VOID_ID)
    
    # 3. Construct Raw Transaction (80 bytes)
    tx_data = bytearray(80)
    tx_data[0:32] = pub_key
    tx_data[32:64] = dest_pub_key
    tx_data[64:72] = (WAKEUP_AMOUNT).to_bytes(8, byteorder='little')
    tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
    tx_data[76:78] = (0).to_bytes(2, byteorder='little') 
    tx_data[78:80] = (0).to_bytes(2, byteorder='little') 
    
    # 4. Sign
    digest = kangaroo_twelve(bytes(tx_data), 80, 32)
    signature = sign(subseed, pub_key, digest)
    
    full_tx = tx_data + signature
    
    # Calculate TX ID
    final_digest = kangaroo_twelve(bytes(full_tx), 144, 32)
    tx_hash_id = get_identity_from_public_key(final_digest).lower()
    
    print(f"[+] Global Synchronisation Mode: ACTIVE")
    print(f"[*] TX Hash: {tx_hash_id}")
    
    # 5. Broadcast
    b64_tx = base64.b64encode(full_tx).decode('utf-8')
    try:
        print(f"[*] Broadcasting to {RPC_URL}...")
        resp = requests.post(f"{RPC_URL}/v1/broadcast-transaction", json={"encodedTransaction": b64_tx}, timeout=30)
        
        print("\n" + "=" * 60)
        if resp.status_code == 200:
            print("🌊 GLOBAL WAKE-UP PULSE BROADCASTED 🌊")
            print(f"Response: {resp.json()}")
            print(f"Monitor: https://explorer.qubic.org/network/transfer/{tx_hash_id}")
        else:
            print("❌ BROADCAST FAILED")
            print(f"Status: {resp.status_code}")
            print(f"Error: {resp.text}")
        print("=" * 60)
        return tx_hash_id

    except Exception as e:
        print(f"[X] CRITICAL ERROR during broadcast: {e}")
        return None

if __name__ == "__main__":
    tx_id = execute_wakeup_pulse()
    if tx_id:
        print("\n[*] BROADCAST COMPLETE. Monitoring global matrix resonance...")
