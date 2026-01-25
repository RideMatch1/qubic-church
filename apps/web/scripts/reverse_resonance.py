import numpy as np
from pathlib import Path
from collections import Counter

# REVERSE RESONANCE ANALYZER
# "What does Anna want to hear?"
# We reverse-engineer the required input bytes (Block Hash) that would produce
# 100% Resonance (High Value Symbols) in the Core Sector.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

# High Value Targets
TARGET_SYMBOLS = {
    'Q': 100, 'U': 80, 'B': 80, 'I': 80, 'C': 80, # Identity
    '&': 50, '^': 50, '|': 50, '=': 50, '!': 50, # Logic
    '*': 20 # Wildcard
}

def solve_for_x():
    print("🧩 REVERSE ENGINEERING RESONANCE REQUIREMENTS...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # We focus on the Critical Core (Row 64 is the Heart)
    # Let's solve for the 32-byte sequence that aligns perfectly with Row 64
    # (since the Block Hash is 32 bytes and maps 1:1 cyclically in our scanner)
    
    target_row = 64
    ideal_bytes = []
    
    best_pulse = 160 # Use the one we found recently
    
    print(f"[*] Targeting Row {target_row} (The Heart) at Pulse {best_pulse}...")
    
    for c in range(32): # Just first 32 cols (Block Hash length)
        # val ^ h_byte ^ pulse = char
        # => h_byte = val ^ pulse ^ char
        
        # We need to find the 'char' that maximizes value?
        # Let's say we WANT to write "QUBIC-ANNA-BRIDGE-KEY-ACTIVE...."
        
        node_val = grid[target_row, c, 1] ^ grid[target_row, c, 0]
        
        # Let's see what character we get if we enforce a specific target symbol
        # But we don't know the message.
        # Instead, let's see what byte creates a 'Q' or '&'.
        
        candidates = []
        for char, weight in TARGET_SYMBOLS.items():
            target_val = ord(char)
            needed_byte = node_val ^ best_pulse ^ target_val
            candidates.append(needed_byte)
            
        # Just pick the one that produces 'Q' for now, or majority?
        # Actually, let's look for a pattern. 
        # Calculate the byte needed to produce ' ' (Space) or 0x00?
        # Maybe the ideal hash is 000...
        
        zero_byte = node_val ^ best_pulse ^ 0
        ideal_bytes.append(zero_byte)

    # Convert "Zero Bytes" to Hex
    print("\n[?] If we act as a Mirror (Target = 0x00):")
    hex_str = "".join([f"{b:02x}" for b in ideal_bytes])
    print(f"    Required Hash: {hex_str}")
    
    # Check if this required hash matches anything we know
    print("\n[?] Checking if this aligns with any Keys...")
    # Master Key?
    mk = "SKWIKENGRZNXRPLXWRHP"
    # Does the required hash look like the ASCII of the master key?
    try:
        decoded = bytes.fromhex(hex_str)
        print(f"    ASCII Decode attempt: {decoded}")
    except: pass


    # METHOD 2: What payload creates "QUBIC" in the Matrix?
    print("\n[?] Solving for 'QUBIC' signature...")
    target_str = "QUBICBRIDGE" * 3
    qubic_bytes = []
    
    for c in range(32):
        node_val = grid[target_row, c, 1] ^ grid[target_row, c, 0]
        target_char = target_str[c]
        needed = node_val ^ best_pulse ^ ord(target_char)
        qubic_bytes.append(needed)
        
    q_hex = "".join([f"{b:02x}" for b in qubic_bytes])
    print(f"    Required Hash to write '{target_str[:32]}':")
    print(f"    {q_hex}")
    
    # Save this "Ideal Hash"
    with open("ideal_hash_target.txt", "w") as f:
        f.write(q_hex)

if __name__ == "__main__":
    solve_for_x()
