"""
Executive Committee Analysis
============================

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Strategic nodes are converted to matrix indices for comparison with hash-derived coords.
"""
import json
import hashlib
from pathlib import Path
import math

# Import correct coordinate transformation
try:
    from anna_matrix_utils import anna_to_matrix
except ImportError:
    def anna_to_matrix(x, y):
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col

# Paths
GAR_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_analysis.json")
BIN_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")

# CORRECTED: Strategic nodes defined in Anna coordinates
STRATEGIC_ANNA = {
    "ENTRY": (45, 92),
    "CORE": (6, 33),
    "EXIT": (82, 39),
    "MEMORY": (21, 21),
    "VISION": (64, 64),
    "ORACLE": (127, 0),
    "VOID": (0, 0)
}

# Convert to matrix indices for comparison with hash-derived coordinates
STRATEGIC_NODES = {}
for name, (anna_x, anna_y) in STRATEGIC_ANNA.items():
    row, col = anna_to_matrix(anna_x, anna_y)
    STRATEGIC_NODES[name] = (row, col)
# Results:
# ENTRY:  matrix[99][109]
# CORE:   matrix[30][70]
# EXIT:   matrix[24][18]
# MEMORY: matrix[42][85]
# VISION: matrix[127][0]
# ORACLE: matrix[63][63]
# VOID:   matrix[63][64]

def btc_privkey_to_qubic_seed(hex_key: str) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    num = int(hex_key, 16)
    seed = ""
    for _ in range(55):
        seed += alphabet[num % 26]
        num //= 26
    return seed

def calculate_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def find_executive_committee():
    print("[*] Identifying the 'Executive Committee' (Shadow Keys closest to AI Cores)...")
    
    with open(BIN_FILE, "rb") as f:
        data = f.read()
    
    key_size = 32
    num_keys = len(data) // key_size
    
    committee = {}
    
    for i in range(num_keys):
        key_bytes = data[i*key_size : (i+1)*key_size]
        hex_key = key_bytes.hex()
        seed = btc_privkey_to_qubic_seed(hex_key)
        
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        row = h[0] % 128
        col = h[1] % 128
        coord = (row, col)
        
        for name, target in STRATEGIC_NODES.items():
            dist = calculate_distance(coord, target)
            if name not in committee or dist < committee[name]['dist']:
                committee[name] = {
                    "key_index": i,
                    "coord": coord,
                    "dist": dist,
                    "privkey": hex_key,
                    "seed": seed,
                    "id_range": [i*128, (i+1)*128]
                }
                
    print("\n[!] EXECUTIVE COMMITTEE FORMED:")
    for name, info in committee.items():
        print(f"  - {name:7} | Key {info['key_index']:3} | Coord {info['coord']} | Dist {info['dist']:5.2f} | Range {info['id_range']}")

    # Save to file
    with open("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/executive_committee.json", "w") as f:
        json.dump(committee, f, indent=2)

if __name__ == "__main__":
    find_executive_committee()
