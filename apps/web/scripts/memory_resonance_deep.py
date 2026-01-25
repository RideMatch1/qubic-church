"""
Memory Resonance Deep Analysis
==============================

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Note: seed_to_coordinates() maps hash bytes directly to matrix indices.
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

# Paths
L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
COMMITTEE_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/executive_committee.json")

def seed_to_coordinates(seed: str) -> tuple[int, int]:
    """
    Map a seed to matrix coordinates via SHA256 hash.
    Returns (row, col) matrix indices directly.
    """
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    row = h[0] % 128
    col = h[1] % 128
    return (row, col)

def run_memory_resonance_deep_audit():
    print("[*] Deep Resonance Audit on MEMORY SECTOR...")
    
    with open(COMMITTEE_JSON, "r") as f:
        committee = json.load(f)
    mem_info = committee.get("MEMORY", {})
    start, end = mem_info['id_range']

    with open(MATRIX_JSON, "r") as f:
        matrix_data = json.load(f)
        
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    decrypted = bytearray()
    
    for i in range(start, end):
        record = records[i]
        seed = record.get("seed", "")
        r, c = seed_to_coordinates(seed)
        coord_key = f"{r},{c}"
        
        mined_hex = matrix_data.get(coord_key, "00")
        mask = int(mined_hex[:2], 16)
        
        decrypted.append(l5_data[i] ^ mask)
        
    print(f"\n[!] MEMORY TEXT RECONSTRUCTED:")
    text = decrypted.decode('ascii', errors='ignore')
    print(f"[{text}]")
    print(f"Hex: {decrypted.hex()}")

if __name__ == "__main__":
    run_memory_resonance_deep_audit()
