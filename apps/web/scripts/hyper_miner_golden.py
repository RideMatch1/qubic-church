import numpy as np
import hashlib
from pathlib import Path

# HYPER MINER (GOLDEN EDITION)
# Optimizes the Block Hash search to match the IDEAL PREFIX '4aede2ab' 
# or find a high-resonance nonce using the new Golden TxID.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
TX_ID_FILE = "golden_tx.id"
IDEAL_PREFIX = "4aede2ab"

def calculate_score_fast(block_hash, grid, best_pulse=160):
    hash_bytes = bytes.fromhex(block_hash)
    hits = 0
    # Core Diagonal Scan (Fast)
    for i in range(56, 72): # 16 centered
        r, c = i, i
        if not grid[r,c,2]:
             val = grid[r,c,1] ^ grid[r,c,0]
             h_byte = hash_bytes[(r*128+c)%32]
             res = val ^ h_byte ^ best_pulse
             char = chr(res) if 32 <= res <= 126 else '.'
             if char in "&^|=!@": hits += 10
             if char in "QUBIC": hits += 15 # Golden Boost
    return hits

def mine_hyper():
    print("🚀 STARTING HYPER-MINER (Target: >90% or '4aede2ab')...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    with open(TX_ID_FILE, "r") as f:
        tx_id = f.read().strip()
        
    prev_hash = "0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05"
    merkle_root = hashlib.sha256( (prev_hash + tx_id).encode() ).hexdigest()
    
    nonce = 0
    best_score = 0
    best_hash = ""
    
    # We will try up to 2 Million Nonces
    MAX_NONCES = 2000000
    
    while nonce < MAX_NONCES:
        # Standard Mining
        header = f"{prev_hash}{merkle_root}{nonce}"
        raw_hash = hashlib.sha256(header.encode()).hexdigest()
        
        # 1. Check for Magic Prefix (Instant Win)
        if raw_hash.startswith(IDEAL_PREFIX):
            print(f"\n[!!!] GOLDEN KEY FOUND! Nonce {nonce}")
            print(f"      Hash: {raw_hash}")
            return raw_hash
            
        # 2. Check Resonance
        score = calculate_score_fast(raw_hash, grid, 160)
        
        # Normalize score rough estimate
        # Max hits ~ 16 * 15 = 240
        pct = (score / 240) * 100
        
        if pct > best_score:
            best_score = pct
            best_hash = raw_hash
            
            if pct > 90.0:
                 print(f"\n[!!!] CRITICAL RESONANCE >90% at Nonce {nonce}")
                 print(f"      Score: {pct:.2f}%")
                 print(f"      Hash: {raw_hash}")
                 return raw_hash
                 
        if nonce % 200000 == 0:
            print(f"    Scanning... {nonce/1000000:.1f}M (Best: {best_score:.1f}%)")
            
        nonce += 1
        
    print(f"\n[x] Finished. Best: {best_score:.2f}%")
    print(f"    Hash: {best_hash}")
    return best_hash

if __name__ == "__main__":
    mine_hyper()
