import numpy as np
from pathlib import Path
import hashlib

# RESONANCE SCORE OPTIMIZER
# Calculates the EXACT inputs needed to achieve 100% Resonance Score in the Core Sector.
# Score Logic: (Active Nodes / Total Nodes)
# Active Node = Produces Logic Symbol (&, ^, |, =, !) or "QUBIC" char when XORed.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

def optimize_resonance():
    print("🎯 OPTIMIZING FOR 100% RESONANCE...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # We target the Core 16x16 Sector (as used in our successful tests)
    start_r, start_c = 56, 56
    end_r, end_c = 72, 72
    
    # We need to construct a 32-byte hash (Payload) that, when cyclically applied,
    # forces EVERY cell in this sector to be "Active".
    
    # The Scanner Logic:
    # h_byte = hash_bytes[(r*128+c)%32]
    # res = val ^ h_byte ^ pulse
    # if chr(res) in TARGETS -> Active
    
    # Since (r*128+c)%32 cycles perfectly every 32 cells (and 32 columns),
    # each byte of our payload controls a specific subset of the grid.
    # Specifically, Byte 0 controls Col 0, 32, 64, 96... of EVERY ROW?
    # Wait, (r*128+c) % 32. 
    # Since 128 is a multiple of 32 (128 = 4 * 32), (r*128) is always 0 mod 32.
    # So (r*128+c)%32 == c % 32.
    # VERIFIED: The row doesn't matter for the hash index. 
    # Hash Byte K controls all columns where c%32 == K.
    
    # This simplifies things massively.
    # To get 100% resonance in the 16x16 sector (Cols 56-72),
    # we need to optimize Hash Bytes corresponding to indices [56%32 ... 71%32].
    # That is indices 24 to 31, and 0 to 7. (Total 16 active bytes).
    
    # For each active byte index (k), we need to find a value B such that:
    # For all rows R in range 56-72:
    #   (Grid[R, C] ^ B ^ Pulse) is in {&, ^, |, =, !}
    
    # This is a system of linear equations over GF(256), but constrained to ASCII output.
    # We might not get 100% if the Grid values in a column vary too much (Entropy).
    # But we can maximize it.
    
    best_overall_pulse = 0
    best_overall_hash = bytearray(32) # Default 0s
    max_global_score = 0
    
    # Scan Pulses to find the "Most Cooperative" frequency
    for pulse in range(256):
        
        current_hash = bytearray(32)
        total_hits = 0
        total_cells = (end_r - start_r) * (end_c - start_c)
        
        # Optimize each byte column involved in the sector
        for k in range(32):
            # Is this byte involved in our 16x16 sector?
            # Sector Cols: 56 to 71.
            # Indices: 24..31, 0..7
            
            # Find all relevant grid values for this byte index K
            relevant_vals = []
            for r in range(start_r, end_r):
                for c in range(start_c, end_c):
                    if (c % 32) == k:
                        if not grid[r,c,2]: # Check gap
                             val = grid[r,c,1] ^ grid[r,c,0]
                             relevant_vals.append(val)
            
            if not relevant_vals: continue
            
            # Find best Byte B for this column
            best_byte = 0
            best_byte_hits = 0
            
            # Brute force the byte (0-255)
            # Optimization: We only care about producing '&^|=!@'
            # target_char = val ^ B ^ pulse
            # => B = val ^ pulse ^ target_char
            
            # Just test all 256 candidates for B
            for b_cand in range(256):
                hits = 0
                for v in relevant_vals:
                    res = v ^ b_cand ^ pulse
                    char = chr(res) if 32 <= res <= 126 else '.'
                    if char in "&^|=!@": hits += 1
                if hits > best_byte_hits:
                     best_byte_hits = hits
                     best_byte = b_cand
            
            current_hash[k] = best_byte
            total_hits += best_byte_hits
            
        score_pct = (total_hits / total_cells) * 100
        if score_pct > max_global_score:
            max_global_score = score_pct
            best_overall_pulse = pulse
            best_overall_hash = current_hash.copy()
            
    print(f"[*] Optimization Complete.")
    print(f"    Max Achievable Resonance: {max_global_score:.2f}%")
    print(f"    Optimal Pulse: {best_overall_pulse}")
    
    hex_hash = best_overall_hash.hex()
    print(f"    Optimal Payload Hash: {hex_hash}")
    
    # Save it
    with open("optimized_payload_hash.txt", "w") as f:
        f.write(hex_hash)

if __name__ == "__main__":
    optimize_resonance()
