import numpy as np
from pathlib import Path

# THE GEMATRIA SCANNER (Letter Sums)
# Searching for sequences in the Matrix where the Sum(A=1..Z=26) equals specific constants.
# Target Constants: 27 (CFB), 43 (Genesis), 137 (Alpha), 576 (Block).

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

CONSTANTS = [27, 43, 137, 576]

def get_letter_value(c):
    # A=1, ..., Z=26
    # a=1, ..., z=26 (Case insensitive for gematria typically)
    if 'A' <= c <= 'Z': return ord(c) - 64
    if 'a' <= c <= 'z': return ord(c) - 96
    return 0

def gematria_scan():
    print("🔠 INITIATING GEMATRIA SCAN (Letter Sums)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)

    # Convert Grid to Char Plane
    char_grid = []
    for r in range(128):
        row_str = ""
        for c in range(128):
            if not grid[r,c,2]:
                val = grid[r,c,1] ^ grid[r,c,0]
                char = chr(val) if 32 <= val <= 126 else '.'
            else:
                char = '.'
            row_str += char
        char_grid.append(row_str)

    found_seqs = 0
    
    # Scan Rows for sub-sequences summing to constants
    for r_idx, row in enumerate(char_grid):
        # We look for contiguous alphabetic sequences
        # e.g. "ABC" -> 1+2+3 = 6
        
        # Sliding window, max length 20
        for start in range(128):
            current_sum = 0
            current_seq = ""
            
            for end in range(start, min(start+20, 128)):
                char = row[end]
                val = get_letter_value(char)
                
                if val == 0: break # Stop at non-letter
                
                current_sum += val
                current_seq += char
                
                if current_sum in CONSTANTS:
                    print(f"  [ROW {r_idx:3}] SUM {current_sum:3}: '{current_seq}' (Cols {start}-{end})")
                    found_seqs += 1
                
                if current_sum > max(CONSTANTS): break

    print(f"[*] Scan Complete. Found {found_seqs} Gematria artifacts.")
    
    # Interpretation
    if found_seqs > 0:
        print("    [CONCLUSION] The Matrix uses Gematria-based Checksums.")

if __name__ == "__main__":
    gematria_scan()
