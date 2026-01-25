"""
Extract Legacy Keys
===================

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Note: The hash mapping produces matrix indices directly.
Strategic node detection now uses correct matrix indices converted from Anna coords.
"""
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

# Path to the binary data
BIN_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")
DOCS_DIR = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/docs/")

def btc_privkey_to_qubic_seed(hex_key: str) -> str:
    """
    Strict conversion: Bitcoin PrivKey (Hex) -> Qubic Seed (55 base26 chars)
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    num = int(hex_key, 16)
    seed = ""
    for _ in range(55):
        seed += alphabet[num % 26]
        num //= 26
    return seed

def extract_keys():
    print("[*] Extracting 185 Legacy Keys from Position 27 bitstream...")
    
    with open(BIN_FILE, "rb") as f:
        data = f.read()
    
    # 32 bytes per key
    key_size = 32
    num_keys = len(data) // key_size
    
    keys = []
    for i in range(num_keys):
        key_bytes = data[i*key_size : (i+1)*key_size]
        hex_key = key_bytes.hex()
        seed = btc_privkey_to_qubic_seed(hex_key)
        
        # Determine coordinate of this seed
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        row = h[0] % 128
        col = h[1] % 128
        
        keys.append({
            "index": i,
            "privkey": hex_key,
            "seed": seed,
            "coord": [row, col]
        })
        
    # Save as Markdown report
    report_file = DOCS_DIR / "legacy_keys_report.md"
    with open(report_file, "w") as f:
        f.write("# 📑 LEGACY KEYS REPORT: The 185 Bridge Seeds\n\n")
        f.write("These seeds were extracted from the **Position 27 Bitstream** across 24,000 identities.\n\n")
        f.write("| Index | Coordinate | Seed Sample | BTC PrivKey (Hex) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for k in keys[:50]: # First 50 for the report
            f.write(f"| {k['index']} | `({k['coord'][0]}, {k['coord'][1]})` | `{k['seed'][:10]}...` | `{k['privkey'][:16]}...` |\n")
            
        f.write("\n*(Full list truncated for brevity)*\n")

    print(f"[+] Extracted {len(keys)} keys. Report saved to {report_file}")
    
    # Check for strategic coordinate overlap
    # CORRECTED: Convert Anna coordinates to matrix indices for comparison
    # The hash-derived coords are matrix indices, so we convert strategic Anna coords
    strategic_anna_coords = {
        'Entry': (45, 92),
        'Core': (6, 33),
        'Exit': (82, 39),
        'Memory': (21, 21),
        'Vision': (64, 64),
        'Oracle': (127, 0),
        'Void': (0, 0)
    }

    # Convert to matrix indices: {(row, col): name}
    strategic_matrix_coords = {}
    for name, (anna_x, anna_y) in strategic_anna_coords.items():
        row, col = anna_to_matrix(anna_x, anna_y)
        strategic_matrix_coords[(row, col)] = f"{name} (Anna({anna_x}, {anna_y}))"

    for k in keys:
        coord = tuple(k['coord'])  # This is (row, col) from hash
        if coord in strategic_matrix_coords:
            print(f"[!!!] HIT: Key {k['index']} maps to STRATEGIC SECTOR: {strategic_matrix_coords[coord]} -> matrix{coord}")

if __name__ == "__main__":
    extract_keys()
