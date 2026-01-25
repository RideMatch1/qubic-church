import numpy as np
import re
from pathlib import Path

# THE FUZZY SENTENCE READER
# Reconstructing logic patterns by treating Gaps ('_') as Wildcards.
# Logic: If we see "A_B", we check if the surrounding context implies syntax.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def fuzzy_scan():
    print("🌫️ INITIATING FUZZY LOGIC SCAN (Gap-Bridging)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)

    reconstructed_logic = []
    
    # SCAN HORIZONTAL
    print("[*] Bridging Horizontal Gaps...")
    for r in range(128):
        line_chars = []
        for c in range(128):
            if grid[r,c,2]: # Gap
                line_chars.append('?') # Wildcard
            else:
                val = grid[r,c,1] ^ grid[r,c,0]
                line_chars.append(chr(val) if 32 <= val <= 126 else '.')
        
        full_line = "".join(line_chars)
        
        # Look for patterns like "Val?Op?Val" or "Op?Val"
        # Regex: Word + (Wildcard) + Operator + (Wildcard) + Word
        # Example: X?^Y -> X (gap hidden) ^ Y
        
        # We search for potentially broken sentences:
        # e.g. "S?T?A?T?E?=?O?K"
        
        matches = re.finditer(r'([a-zA-Z0-9]{1,})([\?]+)([=@^&|#!+])([\?]*)([a-zA-Z0-9]{1,})', full_line)
        for m in matches:
            reconstructed_logic.append(f"ROW {r:3} | {m.group(0)}")
            
    # SCAN VERTICAL
    print("[*] Bridging Vertical Gaps...")
    for c in range(128):
        col_chars = []
        for r in range(128):
            if grid[r,c,2]:
                col_chars.append('?')
            else:
                val = grid[r,c,1] ^ grid[r,c,0]
                col_chars.append(chr(val) if 32 <= val <= 126 else '.')
        
        full_col = "".join(col_chars)
        matches = re.finditer(r'([a-zA-Z0-9]{1,})([\?]+)([=@^&|#!+])([\?]*)([a-zA-Z0-9]{1,})', full_col)
        for m in matches:
            reconstructed_logic.append(f"COL {c:3} | {m.group(0)}")

    print(f"\n[!] RECONSTRUCTED {len(reconstructed_logic)} BRIDGE STATEMENTS:")
    print("-" * 50)
    
    # Filter only interesting ones (Length > 5)
    long_stmts = [s for s in reconstructed_logic if len(s.split('|')[1].strip()) > 5]
    
    for s in long_stmts[:25]:
        # Beautify: Replace ? with _
        clean_s = s.replace('?', '_')
        print(clean_s)

if __name__ == "__main__":
    fuzzy_scan()
