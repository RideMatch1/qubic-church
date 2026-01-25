"""
Check Gap Keys
==============

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Note: The hash-based mapping (seed -> matrix position) produces matrix indices directly.
"""
import json
import hashlib
from pathlib import Path

# Import correct coordinate transformation
try:
    from anna_matrix_utils import anna_to_matrix, matrix_to_anna
except ImportError:
    def anna_to_matrix(x, y):
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col
    def matrix_to_anna(row, col):
        x = col - 64
        y = 63 - row
        return x, y

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

def check_gap_overlap():
    print("[*] Checking overlap between 185 Legacy Keys and the 24% Matrix Gap...")
    
    with open(GAP_JSON, "r") as f:
        gap_data = json.load(f)
    gap_coords = set(tuple(c) for c in gap_data.get("gap_coordinates", []))
    
    with open(BIN_FILE, "rb") as f:
        data = f.read()
    
    key_size = 32
    num_keys = len(data) // key_size
    
    hits = []
    for i in range(num_keys):
        key_bytes = data[i*key_size : (i+1)*key_size]
        hex_key = key_bytes.hex()
        seed = btc_privkey_to_qubic_seed(hex_key)
        
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        row = h[0] % 128
        col = h[1] % 128
        coord = (row, col)
        
        if coord in gap_coords:
            hits.append({
                "index": i,
                "coord": coord,
                "privkey": hex_key
            })
            
    print(f"[+] Found {len(hits)} direct hits into the Protected Gap!")
    for h in hits:
        print(f"    - Key {h['index']} maps to GAP COORD {h['coord']} (PrivKey: {h['privkey'][:16]}...)")

if __name__ == "__main__":
    check_gap_overlap()
