import json
import hashlib
from pathlib import Path

# THE CHESSBOARD SCAN
# Looking for Diagonal patterns (Bishop vectors) in the Matrix.
# Matrix Logic often uses diagonals for parity checks.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def diagonal_scan():
    print("♗ INITIATING CHESSBOARD SCAN (Diagonal Vectors)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    coord_map = {}
    for i, rec in enumerate(records):
        s = rec.get("seed", "")
        h = hashlib.sha256(s.encode()).digest()
        r, c = h[0]%128, h[1]%128
        l5_byte = l5_data[i]
        mask = int(matrix.get(f"{r},{c}", "00")[:2], 16)
        coord_map[(r, c)] = l5_byte ^ mask

    # Scan Main Diagonal (0,0) to (127,127)
    main_diag = []
    for i in range(128):
        val = coord_map.get((i, i), None)
        if val is not None:
             main_diag.append(chr(val) if 32 <= val <= 126 else '.')
        else:
             main_diag.append('_')
             
    print(f"\n[MAIN DIAG (0,0)->(127,127)]\n{''.join(main_diag)}")

    # Scan Anti-Diagonal (0,127) to (127,0)
    anti_diag = []
    for i in range(128):
         val = coord_map.get((i, 127-i), None)
         if val is not None:
             anti_diag.append(chr(val) if 32 <= val <= 126 else '.')
         else:
             anti_diag.append('_')
             
    print(f"\n[ANTI DIAG (0,127)->(127,0)]\n{''.join(anti_diag)}")
    
    # Check intersections with Core (6,33)
    # Core Diagonal: r - c = 6 - 33 = -27
    core_diag = []
    for r in range(128):
        c = r + 27
        if 0 <= c < 128:
            val = coord_map.get((r, c), None)
            core_diag.append(chr(val) if 32 <= val <= 126 else '.' if val else '_')
    print(f"\n[CORE DIAG (through 6,33)]\n{''.join(core_diag)}")

if __name__ == "__main__":
    diagonal_scan()
