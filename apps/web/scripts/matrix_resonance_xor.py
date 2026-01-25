"""
Matrix Resonance XOR
====================

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

def seed_to_coordinates(seed: str) -> tuple[int, int]:
    """
    Map a seed to matrix coordinates via SHA256 hash.

    Returns (row, col) matrix indices directly.
    Use matrix_to_anna(row, col) to get Anna coordinates.
    """
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    row = h[0] % 128
    col = h[1] % 128
    return (row, col)

def run_matrix_resonance_xor():
    print("[*] Running Matrix-Resonance XOR (Self-Masking Audit)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix_data = json.load(f)
        
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    decrypted = bytearray()
    
    for i, record in enumerate(records):
        seed = record.get("seed", "")
        r, c = seed_to_coordinates(seed)
        coord_key = f"{r},{c}"
        
        # Get hex key for this coordinate
        mined_hex = matrix_data.get(coord_key, "00")
        mask = int(mined_hex[:2], 16) # First byte of the private key
        
        # XOR the L5 byte with its coordinate mask
        decrypted.append(l5_data[i] ^ mask)
        
    # Search for known signatures
    targets = [b"1CFB", b"1CFi", b"QUBIC", b"ANNA", b"CFB"]
    for t in targets:
        pos = decrypted.find(t)
        if pos != -1:
            print(f"[!!!] FOUND SIGNATURE: {t.decode()} at ID index {pos}")
            snippet = decrypted[max(0, pos-20) : pos+40].decode('ascii', errors='ignore')
            print(f"    Context: [...{snippet}...]")

    # Check for readability
    text = decrypted.decode('ascii', errors='ignore')
    print(f"\n[*] Sample Resonance Text: {text[:200]}")

if __name__ == "__main__":
    run_matrix_resonance_xor()
