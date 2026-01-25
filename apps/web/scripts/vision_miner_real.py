#!/usr/bin/env python3
import hashlib
import multiprocessing
import time
import os
import binascii

# VISION MINER - TARGET COORDINATE (64, 64)
# Optimizing for speed. We need ANY key that maps to 64,64.
# (64, 64) represents the PERFECT CENTER of the 128x128 matrix.
# It is the "Eye of Aigarth".

TARGET_ROW = 64
TARGET_COL = 64

def check_coordinates(seed_bytes):
    # This matches the coordinate logic in the rest of the project
    # SHA256 of the input -> First 2 bytes % 128
    
    # Optimization: We only need the first 2 bytes of the hash.
    # We don't need full hex digest.
    h = hashlib.sha256(seed_bytes).digest()
    
    r = h[0] % 128
    c = h[1] % 128
    return r, c

def miner_worker(worker_id, stop_event):
    # Generate random seeds and check.
    # Using urandom is fast enough for this probability (1/16k).
    
    count = 0
    start_t = time.time()
    
    while not stop_event.is_set():
        # Generate 32 bytes of entropy (standard key size)
        seed_bytes = os.urandom(32)
        
        r, c = check_coordinates(seed_bytes)
        
        if r == TARGET_ROW and c == TARGET_COL:
            hex_key = binascii.hexlify(seed_bytes).decode('utf-8')
            print(f"\n[!] WORKER {worker_id} FOUND A MATCH!")
            print(f"    Key: {hex_key}")
            print(f"    Coordinates: ({r}, {c})")
            stop_event.set()
            return
            
        count += 1
        if count % 100000 == 0:
            # Check if stopped by other worker
            if stop_event.is_set(): return

def start_mining():
    print(f"[*] STARTING VISION MINER (Target: {TARGET_ROW}, {TARGET_COL})")
    print(f"[*] Probability: 1 in 16,384")
    print(f"[*] Launching {multiprocessing.cpu_count()} threads...")
    
    stop_event = multiprocessing.Event()
    processes = []
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=miner_worker, args=(i, stop_event))
        p.start()
        processes.append(p)
        
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
        
    for p in processes:
        p.terminate()

if __name__ == "__main__":
    start_mining()
