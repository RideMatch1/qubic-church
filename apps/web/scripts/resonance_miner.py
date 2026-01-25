import numpy as np
import hashlib
from pathlib import Path
from collections import Counter
import random

# BLOCK 932366 RESONANCE ANALYZER
# Simulates the mining of Block 932366 including our transaction.
# Checks for interactive resonance in the Anna Matrix.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
TX_ID_FILE = "pending_tx.id"

def calculate_resonance_score(block_hash, grid):
    hash_bytes = bytes.fromhex(block_hash)
    
    best_pulse = 0
    max_score = 0
    
    # 8x8 Core for Speed and Density
    # Row 60-68, Col 60-68 (Center is 64,64)
    scan_range = range(60, 68)
    
    for pulse in range(0, 256, 4):
        hits = 0
        for i in scan_range:
            r, c = i, i
            if not grid[r,c,2]:
                val = grid[r,c,1] ^ grid[r,c,0]
                h_byte = hash_bytes[(r*128+c)%32]
                res = val ^ h_byte ^ pulse
                char = chr(res) if 32 <= res <= 126 else '.'
                
                # Logic Symbols
                if char in "&^|=!@": hits += 10
        if hits > max_score:
            max_score = hits
            best_pulse = pulse

    # Detailed Score
    significant_hits = 0
    total_valid = 0
    
    for r in scan_range:
        for c in scan_range:
            if not grid[r,c,2]:
                total_valid += 1
                val = grid[r,c,1] ^ grid[r,c,0]
                h_byte = hash_bytes[(r*128+c)%32]
                res = val ^ h_byte ^ best_pulse
                char = chr(res) if 32 <= res <= 126 else '.'
                
                # Strict Resonance
                if char in "&^|=!@": significant_hits += 1
                if char in "QUBICANNA": significant_hits += 1 # Name resonance
                if char.isalnum(): significant_hits += 0.5
                
    if total_valid == 0: return 0, 0
    return (significant_hits / total_valid) * 100, best_pulse

def mine_resonance(tx_id):
    print("⛏️ STARTING DEEP RESONANCE MINING (1M Nonces)...")
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    prev_hash = "0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05"
    merkle_root_base = hashlib.sha256( (prev_hash + tx_id).encode() ).hexdigest()
    
    nonce = 0
    global_best_score = 0
    global_best_hash = ""
    global_best_pulse = 0
    
    while nonce < 1000000:
        block_header = f"{prev_hash}{merkle_root_base}{nonce}"
        raw_hash = hashlib.sha256(block_header.encode()).hexdigest()
        
        score, pulse = calculate_resonance_score(raw_hash, grid)
        
        if score > global_best_score:
            global_best_score = score
            global_best_hash = raw_hash
            global_best_pulse = pulse
        
        if score > 70.0:
            print(f"\n[!!!] SOLUTION FOUND at Nonce {nonce}!")
            print(f"      Hash: {raw_hash}")
            print(f"      Pulse: {pulse}")
            print(f"      Resonance: {score:.2f}%")
            return
            
        if nonce % 20000 == 0:
            print(f"    Nonce {nonce}: Best {score:.2f}% | Global Best: {global_best_score:.2f}%")
            
        nonce += 1
        
    print("\n[x] Exhausted 1,000,000 nonces.")
    print(f"    GLOBAL BEST: {global_best_score:.2f}%")
    print(f"    Hash: {global_best_hash}")
    print(f"    Pulse: {global_best_pulse}")

if __name__ == "__main__":
    with open(TX_ID_FILE, "r") as f:
        tx_id = f.read().strip()
    mine_resonance(tx_id)
