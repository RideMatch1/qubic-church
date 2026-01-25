import numpy as np
from pathlib import Path

# HASHRATE TUNER FOR BLOCK 932367
# Optimizes the Block Hash configuration to maximize the specific
# "Resonance Score" metric defined in previous analysis.
# Goal: Beat the "70%" benchmark.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

def tune_hash():
    print("🎛️ TUNING HASH FOR BLOCK 932367 (MAX RESONANCE)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # Target Region: Center 16x16 (Row 56-72, Col 56-72)
    start_r, start_c = 56, 72 # Wait, range is exclusive in python usually? 
    # Let's use 56 to 72 (16 items: 56..71)
    
    # Metric from analyze_block_932364:
    # Logic (&^|=!@) = 5 points
    # Alphanum = 1 point
    
    best_pulse = 0
    max_total_score = 0
    best_hash_bytes = bytearray(32)
    
    # 1. Iterate Pulses to find the best carrier frequency
    for pulse in range(256):
        
        current_hash = bytearray(32)
        total_score_for_pulse = 0
        
        # 2. Optimize each Hash Byte (0..31)
        for k in range(32):
            # Find relevant grid cells for this hash byte
            # (r*128 + c) % 32 == k
            # Since 128 is multiple of 32, this simplifies to c % 32 == k
            
            # Filter for cells IN THE CORE REGION
            relevant_nodes = []
            for r in range(56, 72):
                for c in range(56, 72):
                    if (c % 32) == k:
                        if not grid[r,c,2]:
                            val = grid[r,c,1] ^ grid[r,c,0]
                            relevant_nodes.append(val)
                            
            if not relevant_nodes:
                continue
                
            # Brute force best byte for this column-set
            best_b = 0
            best_b_score = -1
            
            for b_cand in range(256):
                score = 0
                for v in relevant_nodes:
                    # Resonance Calc
                    res = v ^ b_cand ^ pulse
                    char = chr(res) if 32 <= res <= 126 else '.'
                    
                    if char in "&^|=!@": score += 5
                    elif char.isalnum(): score += 1
                
                if score > best_b_score:
                    best_b_score = score
                    best_b = b_cand
            
            current_hash[k] = best_b
            total_score_for_pulse += best_b_score
            
        if total_score_for_pulse > max_total_score:
            max_total_score = total_score_for_pulse
            best_pulse = pulse
            best_hash_bytes = current_hash.copy()

    # Calculate Max Possible Score (Theoretical Perfect)
    # If every cell was Logic (5 pts)
    # 16x16 = 256 cells. 256 * 5 = 1280 max points.
    
    theoretical_max = 256 * 5
    percentage = (max_total_score / theoretical_max) * 100
    
    print("\n✅ OPTIMIZATION COMPLETE.")
    print(f"    Optimal Pulse: {best_pulse}")
    print(f"    Raw Score: {max_total_score} / {theoretical_max}")
    print(f"    Resonance Level: {percentage:.2f}%")
    
    hex_hash = best_hash_bytes.hex()
    print(f"    --------------------------------------------------")
    print(f"    TARGET HASH: {hex_hash}")
    print(f"    --------------------------------------------------")
    
    # Save this for the simulation
    with open("target_hash_932367.txt", "w") as f:
        f.write(hex_hash)

if __name__ == "__main__":
    tune_hash()
