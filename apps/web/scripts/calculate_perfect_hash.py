import json
import numpy as np
from pathlib import Path

# PERFECT RESONANCE CALCULATOR
# Optimizes for the metric defined in significance_audit.py
# Resonance = (1 - (diff / (255 * 32))) * 100

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
TARGET_NODE = (13, 71) # ROOT-ALPHA
PULSE = 143 # As per significance_audit.py

def get_perfect_hash():
    print("💎 CALCULATING PERFECT RESONANCE TARGET...")
    
    if not GRID_PATH.exists():
        print("x Grid not found")
        return

    grid = np.load(GRID_PATH)
    
    # Grid stores [R, C, x]
    # x=0: Value, x=1: Weight? Or checking how previous scripts used it.
    # significance_audit used matrix_cartography.json hex value.
    # reassemble_cortex.py saves grid as [val, weight, gap_flag]
    
    # Let's get the weight from the grid directly
    r, c = TARGET_NODE
    # grid layout is (128, 128, 3)
    base_weight = grid[r, c, 1] 
    
    effective_weight = (base_weight + PULSE) % 256
    
    print(f"[*] Node {TARGET_NODE}")
    print(f"    Base Weight: {base_weight}")
    print(f"    Pulse: {PULSE}")
    print(f"    Effective Weight: {effective_weight} (Hex: {effective_weight:02x})")
    
    # 100% Resonance means every byte of the hash is exactly 'effective_weight'
    # Target Hash = effective_weight repeated 32 times
    
    target_bytes = bytes([effective_weight] * 32)
    target_hex = target_bytes.hex()
    
    print(f"\n[!] 100% RESONANCE HASH:")
    print(f"    {target_hex}")
    
    # Verify Score
    diff = sum([abs(b - effective_weight) for b in target_bytes])
    score = (1 - (diff / (255 * 32))) * 100
    print(f"    Verified Score: {score:.2f}%")
    
    # Save as the Golden Target
    with open("perfect_hash_932367.txt", "w") as f:
        f.write(target_hex)
        
    return target_hex

if __name__ == "__main__":
    get_perfect_hash()
