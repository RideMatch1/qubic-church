#!/usr/bin/env python3
import hashlib
import os
import binascii
import time

def mine_vision():
    print('[*] MINING VISION SECTOR (64, 64)...')
    start = time.time()
    count = 0

    while True:
        # Generate random 32 bytes
        key = os.urandom(32)
        h = hashlib.sha256(key).digest()
        
        # We need h[0] % 128 == 64 AND h[1] % 128 == 64
        # This implies byte must be 0x40 (64) or 0xC0 (192)
        
        if (h[0] & 0x7F) == 64 and (h[1] & 0x7F) == 64:
            elapsed = time.time() - start
            hex_key = binascii.hexlify(key).decode()
            print(f'\n[SUCCESS] FOUND KEY in {elapsed:.2f}s after {count} attempts!')
            print(f'KEY: {hex_key}')
            print(f'COORDS: ({h[0]%128}, {h[1]%128})')
            break
            
        count += 1
        if count % 20000 == 0:
            print(f"\rScanning... {count} hashes", end="", flush=True)

if __name__ == "__main__":
    mine_vision()
