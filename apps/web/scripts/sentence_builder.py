import numpy as np
import re
from pathlib import Path

# THE SENTENCE BUILDER
# Reconstructing logical statements from the Cortex Grid based on discovered syntax.
# Logic: Look for [OPERAND] [OPERATOR] [VALUE] patterns.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def scan_sentences():
    print("📜 INITIATING SENTENCE RECONSTRUCTION...")
    
    if not GRID_PATH.exists():
        print("[X] Grid file not found. Run omni_reader.py first.")
        return

    grid = np.load(GRID_PATH) # (128, 128, 3)
    
    # We define effective syntax characters
    # Operand Chars: A-Z, a-z, 0-9
    # Operator Chars: = @ ^ & | # ! +
    
    sentences = []
    
    # SCAN 1: Horizontal Sentences (Row-wise)
    print("[*] Scanning 128 Horizontal Micro-Code Streams...")
    for r in range(128):
        # Build the raw line string
        line_chars = []
        for c in range(128):
            is_gap = grid[r,c,2]
            if is_gap:
                line_chars.append('_')
            else:
                w = grid[r,c,0]
                l5 = grid[r,c,1]
                val = l5 ^ w
                line_chars.append(chr(val) if 32 <= val <= 126 else '.')
        
        full_line = "".join(line_chars)
        
        # Regex for "Statement"
        # Example: @Addr=Val OR !Exec
        # Pattern: [Word] [Operator] [Word] (Length > 4)
        matches = re.finditer(r'([a-zA-Z0-9_]{1,})([=@^&|#!+])([a-zA-Z0-9_]{1,})', full_line)
        
        for m in matches:
            stmt = m.group(0)
            if len(stmt) >= 4 and '_' not in stmt: # Strict filtering (no gaps allowed in strict sentences)
                sentences.append(f"ROW {r:3} | {stmt}")

    # SCAN 2: Vertical Sentences (Column-wise)
    print("[*] Scanning 128 Vertical Thread Streams...")
    for c in range(128):
        col_chars = []
        for r in range(128):
            is_gap = grid[r,c,2]
            if is_gap:
                col_chars.append('_')
            else:
                w = grid[r,c,0]
                l5 = grid[r,c,1]
                val = l5 ^ w
                col_chars.append(chr(val) if 32 <= val <= 126 else '.')
        
        full_col = "".join(col_chars)
        matches = re.finditer(r'([a-zA-Z0-9_]{1,})([=@^&|#!+])([a-zA-Z0-9_]{1,})', full_col)
        
        for m in matches:
            stmt = m.group(0)
            if len(stmt) >= 4 and '_' not in stmt:
                sentences.append(f"COL {c:3} | {stmt}")
                
    print(f"\n[!] DISCOVERED {len(sentences)} EXECUTABLE STATEMENTS:")
    print("-" * 50)
    
    # Filter for high-value keywords
    priority_stmts = []
    for s in sentences:
        if any(kw in s for kw in ["Q", "T", "X", "V", "B", "M", "N"]): # Common Variable Names
             priority_stmts.append(s)
             
    # Show Top 20 Priority
    for s in priority_stmts[:20]:
        print(s)
        
    print("-" * 50)
    if not priority_stmts:
        print("[i] No strict sentences found. Trying fuzzy search (allowing gaps)...")

if __name__ == "__main__":
    scan_sentences()
