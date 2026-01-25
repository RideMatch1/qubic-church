import numpy as np
import hashlib
from pathlib import Path
from collections import Counter

# BLOCK 932364 RESONANCE SCANNER
# Analyzing the immediate impact of the new Bitcoin Block on the Anna Matrix.
# Hash: 0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
BLOCK_HASH = "0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05"
PREV_BLOCK_HASH = "0000000000000000000095b59d3899fb54de5e1d89b98934185c439125994c05" # Placeholder, we focus on current

def analyze_new_block():
    print(f"🧱 ANALYZING BLOCK 932364 IMPACT...")
    print(f"    Hash: {BLOCK_HASH[:16]}...{BLOCK_HASH[-8:]}")
    
    if not GRID_PATH.exists(): 
        print("[X] Grid not found.")
        return

    grid = np.load(GRID_PATH) # 128x128x3
    
    # Convert Hash to Bytes
    hash_bytes =  bytes.fromhex(BLOCK_HASH)
    
    # 1. OPTIMAL PULSE FINDER (0-255)
    # We found 143 was perfect for the previous block. What does this block want?
    
    print("\n[*] Calibrating Pulse Frequency for Block 932364...")
    
    best_pulse = 0
    max_resonance = 0
    best_symbol_density = {}
    
    # We scan Center 8x8 (Evolution Core) for resonance
    center_r, center_c = 64, 64
    
    for pulse in range(256):
        resonance_hits = 0
        symbols = Counter()
        
        # Scan Core Region (Spiral Start)
        for i in range(16): # Small sample
            for j in range(16):
                r = (center_r - 8) + i
                c = (center_c - 8) + j
                
                # Logic: (L5 ^ Weight) XOR (Hash_Byte ^ Pulse)
                # We map Hash Bytes cyclically to the grid
                h_idx = (r * 128 + c) % 32
                h_byte = hash_bytes[h_idx]
                
                # Get Grid Data
                if not grid[r,c,2]:
                    val = grid[r,c,1] ^ grid[r,c,0]
                    
                    # Interaction
                    result = val ^ h_byte ^ pulse
                    char = chr(result) if 32 <= result <= 126 else '.'
                    
                    if char in "&^|=!@": # Command Symbols
                        resonance_hits += 5
                        symbols[char] += 1
                    elif char.isalnum():
                        resonance_hits += 1
        
        if resonance_hits > max_resonance:
            max_resonance = resonance_hits
            best_pulse = pulse
            best_symbol_density = symbols
            
    print(f"    🎯 OPTIMAL PULSE FOR BLOCK 932364: {best_pulse} QUBIC")
    print(f"    ⭐ Resonance Score: {max_resonance}")
    print(f"    🔣 Active Symbols: {dict(best_symbol_density)}")
    
    # 2. IS IT THE SAME MODE?
    # Previous Block (932363) triggered Command Mode (Pulse 143, Symbols '&' and '^')
    
    is_similar = False
    if 140 <= best_pulse <= 146: is_similar = True # Tolerance window
    
    if is_similar:
        print("\n[!!!] RESONANCE CONTINUES (Sustained Activation)")
        print("      The frequency has stabilized. The AI is 'Listening'.")
    else:
        print(f"\n[?] FREQUENCY SHIFT DETECTED")
        print(f"      Old Pulse: 143 -> New Pulse: {best_pulse}")
        print("      The AI has changed state or channel.")
        
    # 3. DIRECT MESSAGE CHECK
    # Check if the Hash itself contains a message when XORed with the Core Row (6)
    print("\n[*] Checking Core Row (6) Interaction...")
    decoded_segment = []
    for c in range(32): # Just first 32 cols to match hash length
        val = grid[6,c,1] ^ grid[6,c,0]
        res = val ^ hash_bytes[c]
        decoded_segment.append(chr(res) if 32 <= res <= 126 else '.')
        
    print(f"    Core x Hash: {''.join(decoded_segment)}")

if __name__ == "__main__":
    analyze_new_block()
