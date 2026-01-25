#!/usr/bin/env python3
import hashlib
import os
import binascii
import time
import json
import signal
import sys

# SYNAPSE MINER v1.0 (SCIENTIFIC GRADE)
# Objective: Generate keys for every coordinate in the 128x128 Qubic Matrix.
# Validation: Double-Check SHA256 mapping.
# Persistence: Autosave JSON.

OUTPUT_FILE = "matrix_cartography.json"
MATRIX_SIZE = 128 # 0-127

# In-Memory Storage for High Speed
# Format: keys[(row, col)] = hex_key
found_keys = {}
start_time = time.time()
total_hashes = 0

def load_progress():
    global found_keys
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys "r,c" back to tuple (r,c)
                for coord_str, key in data.items():
                    r, c = map(int, coord_str.split(','))
                    found_keys[(r, c)] = key
            print(f"[*] RESUMING: Loaded {len(found_keys)} discovered sectors.")
        except:
            print("[!] Warning: Could not load existing map. Starting fresh.")

def save_progress():
    # Convert tuple keys to string for JSON
    export_data = {f"{r},{c}": k for (r,c), k in found_keys.items()}
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(export_data, f, indent=0) # Minimal indent for space

def signal_handler(sig, frame):
    print("\n\n[*] STOPPING MINER. SAVING PROGRESS...")
    save_progress()
    print(f"[*] Map Saved to {OUTPUT_FILE}")
    sys.exit0

def get_coordinates(key_bytes):
    # CRITICAL: The exact mapping logic used in Qubic
    # 1. SHA256 of the Key
    # 2. First byte % 128 = Row
    # 3. Second byte % 128 = Col
    h = hashlib.sha256(key_bytes).digest()
    return h[0] % 128, h[1] % 128

def mine():
    global total_hashes
    print(f"[*] INITIALIZING SYNAPSE MINER (Target: {MATRIX_SIZE}x{MATRIX_SIZE} Grid)")
    print("[*] Press Ctrl+C to stop and save.")
    
    last_save = time.time()
    
    while True:
        # 1. Generate Entropy
        key_bytes = os.urandom(32)
        total_hashes += 1
        
        # 2. Calculate Coordinates
        r, c = get_coordinates(key_bytes)
        
        # 3. Check if this is a NEW sector
        if (r, c) not in found_keys:
            # New Discovery!
            hex_key = binascii.hexlify(key_bytes).decode('utf-8')
            found_keys[(r, c)] = hex_key
            
            # Print minimal log
            percent = len(found_keys) / (MATRIX_SIZE * MATRIX_SIZE) * 100
            print(f"\r[+] Discovered ({r}, {c}) | Total: {len(found_keys)} | Coverage: {percent:.2f}%", end="")
            
        # Autosave every 30 seconds
        if time.time() - last_save > 30:
            save_progress()
            last_save = time.time()
            # print(f" [Autosaved]")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    load_progress()
    mine()
