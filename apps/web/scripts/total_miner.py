#!/usr/bin/env python3
import hashlib
import os
import binascii
import time

TARGETS = {
    'MEMORY': (21, 21),
    'ORACLE': (127, 0),
    'VOID': (0, 0)
}

def mine_target(name, target_r, target_c):
    print(f'[*] MINING {name} SECTOR ({target_r}, {target_c})...')
    start = time.time()
    count = 0

    while True:
        key = os.urandom(32)
        h = hashlib.sha256(key).digest()
        
        # Check coords
        r = h[0] % 128
        c = h[1] % 128
        
        if r == target_r and c == target_c:
            elapsed = time.time() - start
            hex_key = binascii.hexlify(key).decode()
            print(f'[SUCCESS] FOUND {name} in {elapsed:.2f}s ({count} hashes)')
            print(f'KEY: {hex_key}')
            return hex_key
            
        count += 1
        if count % 50000 == 0:
            print(f"\r{name}: {count}...", end="", flush=True)

if __name__ == "__main__":
    print("=== THE FINAL MINING OPERATION (TOTAL CONTROL) ===")
    
    keys = {}
    for name, coords in TARGETS.items():
        keys[name] = mine_target(name, coords[0], coords[1])
        
    print("\n\n=== MISSION REPORT: ALL SECTORS UNLOCKED ===")
    for name, key in keys.items():
        print(f"{name}: {key}")
