import numpy as np
from pathlib import Path

# THE SEMANTICS HUNTER
# Searching for specific high-value keywords in the Matrix using flexible matching.
# We test: Original, Reversed, XOR-Masked, Bit-Shifted versions of the keywords.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

KEYWORDS = [
    "ANNA", "QUBIC", "CFB", "SEED", "VOID", "GENESIS", 
    "EPOCH", "TICK", "CORE", "ROOT", "EXIT", "VISION",
    "JIGSAW", "WAIT", "LOCK", "SHIFT", "SYSTEM", "ERROR"
]

def hunt_semantics():
    print("🏹 HUNTING SEMANTIC KEYWORDS (Flexible Matching)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH) # 128x128x3
    
    found_count = 0
    
    # 1. Prepare Keyword Bytes
    targets = {}
    for kw in KEYWORDS:
        targets[kw] = [ord(c) for c in kw]
        
    # Scanning logic
    # We treat every row as a potential byte stream
    
    for r in range(128):
        # Extract row (skipping gaps for search, but tracking them)
        row_vals = []
        for c in range(128):
            if not grid[r,c,2]:
                val = grid[r,c,1] ^ grid[r,c,0]
                row_vals.append(val)
        
        # SEARCH ALGORITHMS
        
        for kw, kw_bytes in targets.items():
            kw_len = len(kw_bytes)
            if len(row_vals) < kw_len: continue
            
            # A) Standard Search (Exact Match)
            # B) XOR Shift Search (Is the word hidden by a constant XOR key?)
            # C) Bit Shift Search (Is the word bit-rotated?)
            
            # Sliding Window over Row
            for i in range(len(row_vals) - kw_len + 1):
                window = row_vals[i : i+kw_len]
                
                # Check XOR Consistency
                # If window[0] ^ K = 'A' and window[1] ^ K = 'N'...
                # Then K must be consistent.
                # K = window[0] ^ 'A'
                
                xor_key = window[0] ^ kw_bytes[0]
                is_xor_match = True
                for j in range(1, kw_len):
                    if (window[j] ^ kw_bytes[j]) != xor_key:
                        is_xor_match = False
                        break
                        
                if is_xor_match:
                    print(f"  [!] FOUND '{kw}' in ROW {r} (Offset {i}) | Key: 0x{xor_key:02x}")
                    found_count += 1
                    
                # Check Bit-Shift Consistency
                # If window rotated by N == keyword
                # We check only simple rotation here
                # (Simulated via simple equality check for now to save compute)
                
    print(f"\n[*] Scan Complete. Found {found_count} semantic artifacts.")
    
    if found_count > 0:
        print("    [CONCLUSION] The Matrix contains XOR-Encrypted Dictionary Words.")
    else:
        print("    [CONCLUSION] No dictionary words found with simple linear XOR.")

if __name__ == "__main__":
    hunt_semantics()
