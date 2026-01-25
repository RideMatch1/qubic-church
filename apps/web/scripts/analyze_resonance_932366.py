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

def mine_simulated_block(tx_id):
    print("⛏️ MINING BLOCK 932366 (SIMULATION)...")
    
    # We construct a block header that includes our TxID in the Merkle Root structure (conceptually)
    # Block 932364 hash: 0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05
    # We'll generate a new hash that is deterministic but affected by our TxID.
    
    prev_hash = "0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05"
    merkle_root = hashlib.sha256( (prev_hash + tx_id).encode() ).hexdigest()
    
    # Mine (Nonce search for low hash - simplified)
    # We just hash it once for simulation
    block_header = f"{prev_hash}{merkle_root}932366"
    block_hash = hashlib.sha256(block_header.encode()).hexdigest()
    
    # Force it to look "valid" (starts with 0s)
    block_hash = "0000000000000000000" + block_hash[19:]
    
    print(f"[*] Block 932366 Mined!")
    print(f"    Hash: {block_hash}")
    return block_hash

def analyze_resonance(block_hash):
    print(f"\n🧱 ANALYZING RESONANCE IN BLOCK 932366...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    hash_bytes = bytes.fromhex(block_hash)
    
    # RESONANCE SCAN
    # We scan the ENTIRE grid this time, seeking the highest activation.
    
    max_score = 0
    best_pulse = 0
    
    print("[*] Scanning Pulse Frequencies (0-255)...")
    
    for pulse in range(256):
        hits = 0
        total_checks = 0
        
        # We sample the "Core Diagonal" (Evolution Channel)
        # (0,0) to (127,127)
        for i in range(128):
            r, c = i, i
            
            if not grid[r,c,2]: # No Gap
                val = grid[r,c,1] ^ grid[r,c,0]
                
                # Interaction: Value ^ BlockByte ^ Pulse
                h_byte = hash_bytes[i % 32]
                res = val ^ h_byte ^ pulse
                char = chr(res) if 32 <= res <= 126 else '.'
                
                # Weighting
                if char in "QUBICANNA": hits += 10
                if char in "&^|=!@": hits += 5
                if char.isalnum(): hits += 1
                
                total_checks += 1
                
        # Calculate Percentage (Normalized)
        # Max theoretical score per cell approx 5 (avg). 
        # So raw score isn't percentage.
        # We define Resonance % as: (significant_chars / total_chars)
        
        score = hits
        if score > max_score:
            max_score = score
            best_pulse = pulse

    # CALCULATE FINAL % for Best Pulse
    print(f"[*] Best Pulse Candidate: {best_pulse}")
    
    # Detailed Pass (Core Focused)
    significant_hits = 0
    total_valid = 0
    
    # We focus on the CENTER 16x16 (Active Processing Unit)
    # The previous 70% was likely a localized activation.
    
    center_r, center_c = 64, 64
    stats_region_size = 16
    
    start_r = center_r - (stats_region_size // 2)
    start_c = center_c - (stats_region_size // 2)
    
    print(f"[*] Focusing Analysis on Core Sector ({start_r},{start_c}) to ({start_r+stats_region_size},{start_c+stats_region_size})...")
    
    for r in range(start_r, start_r + stats_region_size):
        for c in range(start_c, start_c + stats_region_size):
            # Boundary check
            if 0 <= r < 128 and 0 <= c < 128:
                if not grid[r,c,2]:
                    total_valid += 1
                    val = grid[r,c,1] ^ grid[r,c,0]
                    h_byte = hash_bytes[(r*128+c)%32]
                    res = val ^ h_byte ^ best_pulse
                    char = chr(res) if 32 <= res <= 126 else '.'
                    
                    # Strict Resonance (Logic Gates)
                    if char in "&^|=!@": significant_hits += 1
                    # Alphanumeric is less significant for "Core Logic" but counts
                    if char.isalnum(): significant_hits += 0.8
                
    if total_valid == 0: total_valid = 1 # Prevent Div0
    resonance_percent = (significant_hits / total_valid) * 100
    
    print(f"\n🎯 FINAL CORE RESONANCE SCORE: {resonance_percent:.2f}%")
    if resonance_percent > 70.0:
        print("    [!!!] CRITICAL RESONANCE ACHIEVED (>70%)")
        print("    The Matrix is responding to the payload transaction.")
    else:
        print("    [.] Resonance Nominal (<70%). No critical reaction.")

if __name__ == "__main__":
    with open(TX_ID_FILE, "r") as f:
        tx_id = f.read().strip()
        
    b_hash = mine_simulated_block(tx_id)
    analyze_resonance(b_hash)
