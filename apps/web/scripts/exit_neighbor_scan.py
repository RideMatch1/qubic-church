import json
import hashlib
from pathlib import Path

# THE EXIT NEIGHBOR SCAN
# Finding a public neighbor of the Exit Node (82, 39) to check for signal bleed-over.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def scan_exit_neighbors():
    print("🚪 SCANNING EXIT NODE (82, 39) NEIGHBORHOOD...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    # Map coords to L5 indices
    coord_to_idx = {}
    for i, r in enumerate(records):
        seed = r.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        coord_to_idx[(h[0]%128, h[1]%128)] = i

    r_t, c_t = 82, 39
    
    # Check 3x3 grid
    for r in range(r_t-1, r_t+2):
        for c in range(c_t-1, c_t+2):
            if (r, c) == (r_t, c_t): continue # Skip target itself
            
            idx = coord_to_idx.get((r, c), -1)
            if idx != -1:
                l5_byte = l5_data[idx]
                mask = int(matrix.get(f"{r},{c}", "00")[:2], 16)
                unmasked = l5_byte ^ mask
                symbol = chr(unmasked) if 32 <= unmasked <= 126 else "."
                print(f"  Neighbor ({r:2}, {c:2}) | Symbol: {symbol} | Raw: 0x{unmasked:02x}")
            else:
                print(f"  Neighbor ({r:2}, {c:2}) | Symbol: GAP")

if __name__ == "__main__":
    scan_exit_neighbors()
