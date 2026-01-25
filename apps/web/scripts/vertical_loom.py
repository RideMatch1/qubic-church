import json
import hashlib
from pathlib import Path

# THE VERTICAL LOOM
# Reading the Matrix Column-by-Column (Vertical Data Streams).
# This tests the hypothesis that Qubic uses "Lochkarten Logic" (Punch Card).

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def vertical_decode():
    print("🧵 INITIATING VERTICAL LOOM (Column-by-Column Decode)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    # Pre-calculate mapping for speed
    coord_map = {} # (r, c) -> (l5_byte, mask, is_gap)
    
    for i, rec in enumerate(records):
        s = rec.get("seed", "")
        h = hashlib.sha256(s.encode()).digest()
        r, c = h[0]%128, h[1]%128
        
        l5_byte = l5_data[i]
        mask = int(matrix.get(f"{r},{c}", "00")[:2], 16)
        coord_map[(r, c)] = (l5_byte, mask, False)

    # Scan interesting columns
    # Column 33 (Core Column)
    # Column 71 (Root Column)
    target_cols = [33, 71, 92]
    
    for c_target in target_cols:
        col_buffer = []
        for r in range(128):
            if (r, c_target) in coord_map:
                l5_byte, mask, _ = coord_map[(r, c_target)]
                val = l5_byte ^ mask
                col_buffer.append(chr(val) if 32 <= val <= 126 else '.')
            else:
                col_buffer.append('_') # Gap
        
        full_col = "".join(col_buffer)
        print(f"\n[COL {c_target:3}] {full_col}")
        
        # Check for vertical patterns
        if "ANNA" in full_col or "CORE" in full_col:
            print("    [!] VERTICAL PLAINTEXT FOUND")

if __name__ == "__main__":
    vertical_decode()
