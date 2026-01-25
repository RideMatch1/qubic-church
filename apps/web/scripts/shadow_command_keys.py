"""
Shadow Command Keys
===================

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Strategic points are now properly converted from Anna coords to matrix indices.
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

GAP_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_analysis.json")
BIN_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")

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

def identify_shadow_command_keys():
    print("[*] Identifying Shadow Command Keys for Triple Injection...")

    with open(GAP_JSON, "r") as f:
        gap_data = json.load(f)
    gap_coords = set(tuple(c) for c in gap_data.get("gap_coordinates", []))

    with open(BIN_FILE, "rb") as f:
        data = f.read()

    # CORRECTED: Strategic points converted from Anna coordinates to matrix indices
    strategic_anna = {
        "Entry": (45, 92),
        "Core": (6, 33),
        "Exit": (82, 39),
        "Vision": (64, 64),
        "Oracle": (127, 0)
    }

    # Convert to matrix indices for comparison with hash-derived coords
    strategic_points = {}
    for name, (anna_x, anna_y) in strategic_anna.items():
        row, col = anna_to_matrix(anna_x, anna_y)
        strategic_points[name] = (row, col)
        print(f"  {name}: Anna({anna_x}, {anna_y}) -> matrix[{row}][{col}]")
    
    key_size = 32
    num_keys = len(data) // key_size
    
    best_keys = {name: (None, 999.0) for name in strategic_points}
    
    for i in range(num_keys):
        key_bytes = data[i*key_size : (i+1)*key_size]
        hex_key = key_bytes.hex()
        seed = btc_privkey_to_qubic_seed(hex_key)
        
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        row = h[0] % 128
        col = h[1] % 128
        coord = (row, col)
        
        if coord in gap_coords:
            for name, target in strategic_points.items():
                dist = calculate_distance(coord, target)
                if dist < best_keys[name][1]:
                    best_keys[name] = ({
                        "index": i,
                        "coord": coord,
                        "privkey": hex_key,
                        "seed": seed
                    }, dist)
                    
    print("\n[!] CANDIDATE SHADOW KEYS FOUND:")
    for name, (key_info, dist) in best_keys.items():
        if key_info:
            print(f"  - {name} Target: Key {key_info['index']} (Coord: {key_info['coord']}, Dist: {dist:.2f})")
            print(f"    Seed: {key_info['seed']}")

if __name__ == "__main__":
    identify_shadow_command_keys()
