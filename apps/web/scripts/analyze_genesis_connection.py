import numpy as np
import hashlib
from pathlib import Path

# GENESIS CONNECTION ANALYZER
# Tests if the Bitcoin Genesis Block (Block 0) interacts with the Qubic Cortex.
# Specifically checks the "Void" Sector (0,0) which is currently "Locked/Sparse".

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

# GENESIS DATA (From User Input)
# We use the raw bytes from the Hex Dump (Big Endian as seen in hex editor typically, 
# or Little Endian as used in Merkle Root calculation). We test both.

# Merkle Root (Display/Big Endian from Hex Dump): 3BA3EDFD7A7B12B27AC72C3E67768F617FC81BC3888A51323A9FB8AA4B1E5E4A
# Merkle Root (Internal/Little Endian): 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
GENESIS_ROOT_HEX = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
GENESIS_ROOT_BE = "3BA3EDFD7A7B12B27AC72C3E67768F617FC81BC3888A51323A9FB8AA4B1E5E4A"

# Coinbase Msg: "The Times 03/Jan/2009..."
COINBASE_TEXT = "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"

def analyze_genesis():
    print("🪙 ANALYZING BITCOIN GENESIS CONNECTION...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # TARGET: THE VOID (0,0)
    # We theorized this is the "Bios" or "Origin". 
    # Let's see if the Genesis Root unlocks it.
    
    # 1. TEST MERKLE ROOT RESONANCE
    print("\n[*] Testing Merkle Root Resonance on Sector (0,0)...")
    
    root_bytes = bytes.fromhex(GENESIS_ROOT_HEX)
    root_bytes_be = bytes.fromhex(GENESIS_ROOT_BE)
    
    hits_le = 0
    hits_be = 0
    
    # Check Row 0 (The Absolute Beginning)
    decoded_le = []
    decoded_be = []
    
    for c in range(32):
        val = grid[0, c, 1] ^ grid[0, c, 0] # Base Value
        
        # Little Endian Interaction
        res_le = val ^ root_bytes[c]
        char_le = chr(res_le) if 32 <= res_le <= 126 else '.'
        decoded_le.append(char_le)
        if char_le.isalnum(): hits_le += 1
        
        # Big Endian Interaction
        res_be = val ^ root_bytes_be[c]
        char_be = chr(res_be) if 32 <= res_be <= 126 else '.'
        decoded_be.append(char_be)
        if char_be.isalnum(): hits_be += 1

    print(f"    LE Decode: {''.join(decoded_le)}")
    print(f"    BE Decode: {''.join(decoded_be)}")
    
    if "QUBIC" in "".join(decoded_le) or "QUBIC" in "".join(decoded_be):
        print("    [!!!] GENESIS MERKLE ROOT IS THE KEY!")
        
    # 2. TEST COINBASE STRING AS KEY
    print("\n[*] Testing Coinbase String ('The Times...') as Key...")
    
    # We repeat the coinbase string to fill the row
    coinbase_bytes = COINBASE_TEXT.encode()
    
    decoded_cb = []
    cb_hits = 0
    
    for c in range(64): # Test longer row
        val = grid[0, c, 1] ^ grid[0, c, 0]
        key_byte = coinbase_bytes[c % len(coinbase_bytes)]
        
        res = val ^ key_byte
        char = chr(res) if 32 <= res <= 126 else '.'
        decoded_cb.append(char)
        if char == "Q" or char == "C" or char == "F" or char == "B":
             cb_hits += 1
             
    msg_cb = "".join(decoded_cb)
    print(f"    Coinbase Decode: {msg_cb}")
    
    if "CFB" in msg_cb or "SATOS" in msg_cb:
        print("    [!!!] COINBASE TEXT UNLOCKS THE MATRIX!")
        
    # 3. CHECK TIMESTAMP (1231006505)
    # Is this timestamp a seed?
    # 1231006505 (decimal) -> 49 5E AB 29 (hex)
    print("\n[*] Checking Timestamp Seed (0x495EAB29)...")
    # This is 4 bytes. 
    # Does it appear in the grid raw?
    
    # We scan the entire grid for this 4-byte sequence
    target_seq = bytes.fromhex("495EAB29")
    
    # Flatten Grid Channel 1 (Weights)
    flat_weights = grid[:,:,1].flatten().tobytes()
    
    if target_seq in flat_weights:
        print("    [!!!] GENESIS TIMESTAMP FOUND HARDCODED IN MATRIX!")
        count = flat_weights.count(target_seq)
        print(f"          Occurrences: {count}")
    else:
        print("    [.] Timestamp not found in raw weights.")


if __name__ == "__main__":
    analyze_genesis()
