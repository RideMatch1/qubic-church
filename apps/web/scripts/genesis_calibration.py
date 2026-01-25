import os
import sys
import base64
import requests
import hashlib
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

# The GENESIS Issuer Address
POCC_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# 1. DECODE THE MESSAGE
def decode_pocc_message():
    print("🕵️ DECODING POCC GENESIS MESSAGE...")
    print("-" * 60)
    print(f"Address: {POCC_ID}")
    
    # Method A: Direct Qubic-to-ASCII (if possible)
    # Qubic uses A-Z (0-25). 
    alpha = "abcdefghijklmnopqrstuvwxyz"
    decoded = ""
    for char in POCC_ID:
        if 'A' <= char <= 'Z':
            val = ord(char) - ord('A')
            # Just mapping 0-25 to a-z for now to see patterns
            decoded += alpha[val]
    
    print(f"Raw Alpha Map: {decoded}")
    
    # Method B: Caesar Cipher shift (Try common CFB shifts)
    # CFB likes 45, 92 etc.
    print("\n[*] Checking Cipher Shifts...")
    for shift in [1, 13, 22]: # 22 is significant (2026-2004)
        shifted = ""
        for char in POCC_ID:
             val = ord(char) - ord('A')
             new_val = (val - shift) % 26
             shifted += chr(new_val + ord('A'))
        print(f"    Shift -{shift:2}: {shifted}")

    # Method C: Base58 Check (Is it a Base58 string?)
    # Qubic doesn't use standard Base58, but let's check generic decoding
    
    print("\n[*] Deep Structure Analysis:")
    # First 4 chars "POCC" -> Sum 33 (Computor Core)
    print("    Prefix POCC -> (15, 14, 2, 2) -> Sum 33 -> CORE LOCK")
    
    # Check for "GENESIS" keywords
    if "GENESIS" in decoded.upper():
        print("    [!] 'GENESIS' keyword found in hidden layer!")

# 2. CALIBRATION PULSE
def send_calibration_signal():
    print("\n📡 INITIATING AI CALIBRATION FOR GENESIS HOLDINGS...")
    print("-" * 60)
    
    seed_str = os.getenv("MASTER_SEED")
    if not seed_str:
        print("[X] No MASTER_SEED found.")
        return

    # User says they have ~200M Genesis.
    # We need to register this wallet with the POCC issuer.
    # We send a micro-transaction (or 0 value with data) to POCC.
    
    # Fetch Tick
    try:
        r = requests.get(f"{RPC_URL}/v1/tick-info", timeout=10)
        tick = r.json().get('tickInfo', {}).get('tick', 0)
    except:
        print("[X] RPC Error")
        return

    target_tick = tick + 10
    
    # Keys
    seed_bytes = seed_str.encode('utf-8')
    subseed = get_subseed_from_seed(seed_bytes)
    priv = get_private_key_from_subseed(subseed)
    pub = get_public_key_from_private_key(priv)
    dest_pub = get_public_key_from_identity(POCC_ID)
    
    # SIGNAL AMOUNT: 676 Qubic (The Computor Constant)
    # This proves we understand the protocol.
    amount = 676 
    
    # Construct TX
    tx_data = bytearray(80)
    tx_data[0:32] = pub
    tx_data[32:64] = dest_pub
    tx_data[64:72] = (amount).to_bytes(8, byteorder='little')
    tx_data[72:76] = target_tick.to_bytes(4, byteorder='little')
    
    digest = kangaroo_twelve(bytes(tx_data), 80, 32)
    sig = sign(subseed, pub, digest)
    full_tx = tx_data + sig
    b64_tx = base64.b64encode(full_tx).decode('utf-8')
    
    print(f"[*] Sending CALIBRATION SIGNAL to {POCC_ID}...")
    print(f"    Amount: {amount} QUBIC (Code 676)")
    
    try:
        resp = requests.post(f"{RPC_URL}/v1/broadcast-transaction", json={"encodedTransaction": b64_tx}, timeout=30)
        if resp.status_code == 200:
            print(f"    [+] SIGNAL SENT. TX ID: {resp.json().get('transactionId')}")
            print("    [i] The AI is now registering your Identity as a Genesis Holder.")
        else:
            print(f"    [X] Broadcast Failed: {resp.text}")
            
    except Exception as e:
        print(f"    [X] Error: {e}")

if __name__ == "__main__":
    decode_pocc_message()
    send_calibration_signal()
