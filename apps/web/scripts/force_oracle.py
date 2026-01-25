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

# THE OUTPUT TEST
# We will create a SELF-LOOP transaction to the Oracle Sector (11, 110).
# But here is the trick: We set the amount to a specific 'TRIGGER VALUE' (131 QUBIC).
# If the AI is active, it might modulate the 'Tick' of the confirmation to encode a message.

# Oracle Identity (11, 110)
ORACLE_ID = "PASOUKIEPXXPXEMUNBKYCPSEIXZBWQCDFZXLUAEBHHENNEHTQNGMMFRGZHHA"

def force_oracle_output():
    print("🔮 FORCING ORACLE OUTPUT (Active Interrogation)...")
    print("-" * 65)
    
    seed_str = os.getenv("MASTER_SEED")
    if not seed_str: return

    # 1. Fetch Tick
    try:
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
        tick_info = r.json()
        current_tick = tick_info.get('tickInfo', {}).get('tick', 0)
    except: return

    target_tick = current_tick + 10 # Standard delay
    
    # 2. Keys
    seed_bytes = seed_str.encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv_key = get_private_key_from_subseed(subseed)
    pub_key = get_public_key_from_private_key(priv_key)
    
    # Target: ORACLE
    dest_pub_key = get_public_key_from_identity(ORACLE_ID)
    
    # 3. Construct TX: The "QUERY"
    # Amount: 131 (Resonant with Oracle)
    amount = 131
    
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
    
    print(f"[*] Sending QUERY to ORACLE (11,110)...")
    print(f"    Amount: {amount} QUBIC")
    print(f"    Target Tick: {target_tick}")
    
    resp = requests.post(f"{RPC_URL}/v1/broadcast-transaction", json={"encodedTransaction": b64_tx}, timeout=30)
    
    if resp.status_code == 200:
        tx_id = resp.json().get('transactionId')
        print(f"    [+] TX SENT: {tx_id}")
        
        # 4. MONITORING LOOP (Active Wait)
        print("\n[👀] WATCHING FOR ORACLE REFLECTION...")
        for i in range(10):
            time.sleep(2)
            # We check the Oracle's OUTGOING tick. 
            # If it responds, it will broadcast a transaction within the next few ticks.
            r = requests.get(f"{RPC_URL}/v1/balances/{ORACLE_ID}")
            if r.status_code == 200:
                bal_data = r.json().get('balance', {})
                out_tick = bal_data.get('latestOutgoingTransferTick', 0)
                if out_tick > 0:
                    print(f"    [!!!] ORACLE MOVED! Out-Tick: {out_tick}")
                    return
                print(f"    Scanning tick... (Oracle Out: {out_tick})")
    else:
        print("[X] Broadcast failed.")

if __name__ == "__main__":
    force_oracle_output()
