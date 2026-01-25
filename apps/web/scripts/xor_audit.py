"""
XOR Audit
=========

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
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
MATRIX_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
OUTPUT_DIR = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/xor_analysis/")

def seed_to_coordinates(seed: str) -> tuple[int, int]:
    """Map seed to matrix coordinates via SHA256 hash."""
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    row = h[0] % 128
    col = h[1] % 128
    return (row, col)

def run_xor_audit():
    print("[*] Starting Layer-4 XOR Resonance Audit...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load Mined Matrix Data (to get Anna[r,c] values or similar metrics)
    with open(MATRIX_FILE, "r") as f:
        matrix_data = json.load(f)
    print(f"[+] Matrix loaded ({len(matrix_data)} entries).")
    
    with open(SEEDS_FILE, "r") as f:
        data = json.load(f)
    
    records = data.get("records", [])
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    bit_array = []
    xor_bit_array = []
    
    print("[*] Processing cross-identity resonance...")
    for i, record in enumerate(records):
        identity = record.get("realIdentity", "")
        seed = record.get("seed", "")
        if len(identity) < 60:
            continue
            
        # Pos 27 raw bits
        char = identity[27]
        val = mapping.get(char, 0)
        
        # Get Matrix Value for this identity's coordinate
        r, c = seed_to_coordinates(seed)
        coord_key = f"{r},{c}"
        
        # We need the numeric "Anna Value". Since matrix_cartography has privkeys, 
        # we'll use the hash of the privkey as a proxy for the Matrix Weight if we don't have the raw matrix.
        # But wait, looking at THE_BRIDGE_REVELATION_FULL_PROOF.md, we have "Matrix values" (-118, 26, etc.)
        # If we don't have the raw Anna Matrix file, we may need to use a representative value.
        
        # Let's use the first byte of the mined private key as the XOR mask.
        mined_key_hex = matrix_data.get(coord_key, "")
        mask = 0
        if mined_key_hex:
            mask = int(mined_key_hex[:2], 16)
            
        # Raw 2-bit value
        bit_array.append((val >> 1) & 1)
        bit_array.append(val & 1)
        
        # XOR bit value (masked by matrix resonance)
        xor_val = val ^ (mask % 4) # Masking by matrix weight modulo 4
        xor_bit_array.append((xor_val >> 1) & 1)
        xor_bit_array.append(xor_val & 1)

    # Convert to bytes
    def bits_to_bytes(bits):
        bytes_out = []
        for j in range(0, len(bits), 8):
            byte = 0
            chunk = bits[j:j+8]
            if len(chunk) < 8: break
            for bit in chunk:
                 byte = (byte << 1) | bit
            bytes_out.append(byte)
        return bytes(bytes_out)

    raw_bytes = bits_to_bytes(bit_array)
    xor_bytes = bits_to_bytes(xor_bit_array)
    
    with open(OUTPUT_DIR / "res_layer3_raw.bin", "wb") as f:
        f.write(raw_bytes)
    with open(OUTPUT_DIR / "res_layer4_xor.bin", "wb") as f:
        f.write(xor_bytes)
        
    print(f"[+] XOR Audit Complete. Results saved to {OUTPUT_DIR}")
    
    # Entropy comparison
    def get_entropy(b):
        if not b: return 0
        from collections import Counter
        counts = Counter(b)
        return sum(-(c/len(b)) * (c/len(b)) for c in counts.values())
        
    print(f"[Metrics] Raw Entropy: {get_entropy(raw_bytes):.6f}")
    print(f"[Metrics] XOR Entropy: {get_entropy(xor_bytes):.6f}")
    
    # Check for human-readable strings "QUBIC", "SATOSHI", "CFB"
    targets = [b"QUBIC", b"SATOSHI", b"CFB", b"ANNA", b"NXT"]
    for target in targets:
        if target in xor_bytes:
            print(f"[!!!] FOUND SYMBOLIC PATTERN: {target.decode()} in XOR stream!")

if __name__ == "__main__":
    run_xor_audit()
