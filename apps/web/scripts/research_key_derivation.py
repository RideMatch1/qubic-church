#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    EXTENDED KEY DERIVATION RESEARCH                            ║
║                                                                                ║
║  Test advanced methods to derive Bitcoin private keys from Anna Matrix         ║
║  Goal: Find the key that generates Genesis address                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Try to import ecdsa
try:
    import ecdsa
    HAVE_ECDSA = True
except ImportError:
    HAVE_ECDSA = False
    print("⚠ ecdsa library not available")

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

# Target addresses
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
BLOCK1_ADDRESS = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"

# secp256k1 parameters
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def load_matrix() -> List[List[int]]:
    """Load Anna Matrix and convert any string values to integers"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)

    # Convert any string values to integers (some cells contain '00000000')
    matrix = []
    for row in data['matrix']:
        clean_row = []
        for v in row:
            if isinstance(v, str):
                clean_row.append(0)  # Treat string markers as 0
            else:
                clean_row.append(int(v))
        matrix.append(clean_row)
    return matrix

def base58_encode(data: bytes) -> str:
    num = int.from_bytes(data, 'big')
    result = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(BASE58_ALPHABET[rem])
    for byte in data:
        if byte == 0:
            result.append('1')
        else:
            break
    return ''.join(reversed(result))

def base58_decode(s: str) -> bytes:
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)
    result = []
    while num > 0:
        result.append(num % 256)
        num //= 256
    for char in s:
        if char == '1':
            result.append(0)
        else:
            break
    return bytes(reversed(result))

def hash160(data: bytes) -> bytes:
    sha = hashlib.sha256(data).digest()
    ripemd = hashlib.new('ripemd160', sha).digest()
    return ripemd

def pubkey_to_address(pubkey: bytes) -> str:
    h160 = hash160(pubkey)
    versioned = b'\x00' + h160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)

def key_to_address(key_bytes: bytes) -> Optional[Dict]:
    """Convert private key bytes to addresses"""
    if not HAVE_ECDSA:
        return None

    key_int = int.from_bytes(key_bytes, 'big')
    if key_int < 1 or key_int >= SECP256K1_ORDER:
        return None

    try:
        signing_key = ecdsa.SigningKey.from_secret_exponent(key_int, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()

        # Uncompressed
        pubkey_u = b'\x04' + verifying_key.to_string()
        addr_u = pubkey_to_address(pubkey_u)

        # Compressed
        x = verifying_key.to_string()[:32]
        y_int = int.from_bytes(verifying_key.to_string()[32:], 'big')
        prefix = b'\x02' if y_int % 2 == 0 else b'\x03'
        pubkey_c = prefix + x
        addr_c = pubkey_to_address(pubkey_c)

        return {
            'uncompressed': addr_u,
            'compressed': addr_c,
        }
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# KEY DERIVATION METHODS
# ═══════════════════════════════════════════════════════════════════════════════

class ExtendedKeyDerivation:
    def __init__(self):
        print("═" * 70)
        print("           EXTENDED KEY DERIVATION RESEARCH")
        print("═" * 70)
        self.matrix = load_matrix()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'methods_tested': 0,
            'candidates': [],
            'matches': [],
            'near_matches': [],
        }
        self.target_h160 = {
            'genesis': base58_decode(GENESIS_ADDRESS)[1:21],
            'block1': base58_decode(BLOCK1_ADDRESS)[1:21],
            'cfb': base58_decode(CFB_ADDRESS)[1:21],
        }

    def get_value(self, r: int, c: int) -> int:
        return self.matrix[r % 128][c % 128]

    def generate_candidates(self) -> List[Tuple[str, bytes]]:
        """Generate extended list of key candidates"""
        candidates = []
        print("\n  Generating extended key candidates...")

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 1: CFB coordinate combinations
        # ═══════════════════════════════════════════════════════════════════
        print("    [1] CFB coordinate combinations...")
        cfb_coords = [(27, 37), (37, 42), (42, 127), (27, 42), (27, 127), (37, 127)]

        for r, c in cfb_coords:
            # Direct values from coordinates
            seed = bytes([
                r, c,
                self.get_value(r, c) + 128,
                self.get_value(c, r) + 128,
            ] * 8)
            candidates.append((f'cfb_coord_{r}_{c}', hashlib.sha256(seed).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 2: Spiral paths from special locations
        # ═══════════════════════════════════════════════════════════════════
        print("    [2] Spiral path extractions...")
        spiral_starts = [(64, 64), (27, 27), (27, 37), (0, 0), (69, 69)]

        for sr, sc in spiral_starts:
            values = []
            r, c = sr, sc
            # Spiral outward
            for radius in range(1, 17):
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    for _ in range(radius):
                        values.append((self.get_value(r, c) + 128) % 256)
                        r = (r + dr) % 128
                        c = (c + dc) % 128
                        if len(values) >= 32:
                            break
                    if len(values) >= 32:
                        break
                if len(values) >= 32:
                    break
            candidates.append((f'spiral_{sr}_{sc}', bytes(values[:32])))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 3: Genesis timestamp encoded
        # ═══════════════════════════════════════════════════════════════════
        print("    [3] Genesis timestamp encodings...")
        genesis_timestamp = 1231006505  # Bitcoin genesis timestamp

        # Various encodings of the timestamp
        ts_bytes = genesis_timestamp.to_bytes(4, 'big')
        candidates.append(('genesis_ts_sha256', hashlib.sha256(ts_bytes).digest()))
        candidates.append(('genesis_ts_doubled', hashlib.sha256(hashlib.sha256(ts_bytes).digest()).digest()))

        # Timestamp with CFB numbers
        ts_cfb = ts_bytes + bytes([27, 37, 42, 127]) * 7
        candidates.append(('genesis_ts_cfb', hashlib.sha256(ts_cfb).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 4: Block 9 timestamp (first Satoshi TX)
        # ═══════════════════════════════════════════════════════════════════
        print("    [4] Block 9 timestamp encodings...")
        block9_ts = 1231473279

        b9_bytes = block9_ts.to_bytes(4, 'big')
        candidates.append(('block9_ts', hashlib.sha256(b9_bytes).digest()))

        # Combined with matrix coordinates
        b9_coords = bytes([20, 127])  # Block 9 maps to [20, 127] → +27
        candidates.append(('block9_with_coords', hashlib.sha256(b9_bytes + b9_coords).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 5: Matrix region hashes
        # ═══════════════════════════════════════════════════════════════════
        print("    [5] Matrix region hashes...")

        # CFB corner (rows 27-42, cols 27-42)
        cfb_corner = []
        for r in range(27, 43):
            for c in range(27, 43):
                cfb_corner.append((self.get_value(r, c) + 128) % 256)
        candidates.append(('cfb_corner_region', hashlib.sha256(bytes(cfb_corner)).digest()))

        # Vision center region (60-68, 60-68)
        vision_region = []
        for r in range(60, 69):
            for c in range(60, 69):
                vision_region.append((self.get_value(r, c) + 128) % 256)
        candidates.append(('vision_region', hashlib.sha256(bytes(vision_region)).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 6: XOR-derived keys
        # ═══════════════════════════════════════════════════════════════════
        print("    [6] XOR-derived keys...")

        # XOR of all CFB rows
        cfb_rows_xor = bytes([0] * 128)
        for cfb_row in [27, 37, 42]:
            row_bytes = bytes((self.get_value(cfb_row, c) + 128) % 256 for c in range(128))
            cfb_rows_xor = bytes(a ^ b for a, b in zip(cfb_rows_xor, row_bytes))
        candidates.append(('cfb_rows_xor', hashlib.sha256(cfb_rows_xor).digest()))

        # XOR of rows 27 and col 27
        row27 = bytes((self.get_value(27, c) + 128) % 256 for c in range(128))
        col27 = bytes((self.get_value(r, 27) + 128) % 256 for r in range(128))
        row_col_xor = bytes(a ^ b for a, b in zip(row27, col27))
        candidates.append(('row27_xor_col27', hashlib.sha256(row_col_xor).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 7: String-based seeds
        # ═══════════════════════════════════════════════════════════════════
        print("    [7] String-based seeds...")

        strings = [
            "Satoshi Nakamoto",
            "The Times 03/Jan/2009",
            "Chancellor on brink of second bailout for banks",
            "Bitcoin",
            "Genesis",
            "CFB",
            "Come-from-Beyond",
            "qubic",
            "IOTA",
            "Anna",
        ]

        for s in strings:
            h = hashlib.sha256(s.encode()).digest()
            candidates.append((f'string_{s[:10].replace(" ", "_")}', h))

            # Double SHA256
            h2 = hashlib.sha256(h).digest()
            candidates.append((f'string_double_{s[:10].replace(" ", "_")}', h2))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 8: Genesis address hash
        # ═══════════════════════════════════════════════════════════════════
        print("    [8] Address-derived keys...")

        genesis_h160 = self.target_h160['genesis']
        candidates.append(('genesis_h160_padded', genesis_h160 + bytes(12)))
        candidates.append(('genesis_h160_sha256', hashlib.sha256(genesis_h160).digest()))

        cfb_h160 = self.target_h160['cfb']
        candidates.append(('cfb_h160_sha256', hashlib.sha256(cfb_h160).digest()))

        # XOR of genesis and CFB h160
        xor_h160 = bytes(a ^ b for a, b in zip(genesis_h160, cfb_h160))
        candidates.append(('genesis_cfb_xor', hashlib.sha256(xor_h160).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 9: Mathematical combinations
        # ═══════════════════════════════════════════════════════════════════
        print("    [9] Mathematical combinations...")

        # CFB numbers in various arrangements
        cfb_pattern1 = bytes([27, 37, 42, 127] * 8)
        cfb_pattern2 = bytes([127, 42, 37, 27] * 8)  # Reversed
        cfb_pattern3 = bytes([27] * 8 + [37] * 8 + [42] * 8 + [127] * 8)

        candidates.append(('cfb_pattern_1', hashlib.sha256(cfb_pattern1).digest()))
        candidates.append(('cfb_pattern_2', hashlib.sha256(cfb_pattern2).digest()))
        candidates.append(('cfb_pattern_3', hashlib.sha256(cfb_pattern3).digest()))

        # CFB arithmetic
        for i in range(256):
            test = bytes([(27 + i) % 256, (37 + i) % 256, (42 + i) % 256, (127 + i) % 256] * 8)
            candidates.append((f'cfb_offset_{i}', hashlib.sha256(test).digest()))

        # ═══════════════════════════════════════════════════════════════════
        # METHOD 10: Diagonal extractions
        # ═══════════════════════════════════════════════════════════════════
        print("    [10] Diagonal extractions...")

        for offset in range(0, 128, 8):
            diag = []
            for i in range(32):
                r = (offset + i) % 128
                c = i
                diag.append((self.get_value(r, c) + 128) % 256)
            candidates.append((f'diag_offset_{offset}', bytes(diag)))

        print(f"\n    Total candidates generated: {len(candidates)}")
        return candidates

    def test_candidates(self, candidates: List[Tuple[str, bytes]]):
        """Test all candidates against target addresses"""
        print("\n" + "═" * 70)
        print("TESTING CANDIDATES")
        print("═" * 70)

        if not HAVE_ECDSA:
            print("\n  ⚠ Cannot test without ecdsa library")
            return

        targets = [GENESIS_ADDRESS, BLOCK1_ADDRESS, CFB_ADDRESS]

        for name, key_bytes in candidates:
            self.results['methods_tested'] += 1

            # Ensure 32 bytes
            if len(key_bytes) < 32:
                key_bytes = key_bytes.ljust(32, b'\x00')
            elif len(key_bytes) > 32:
                key_bytes = key_bytes[:32]

            result = key_to_address(key_bytes)
            if result is None:
                continue

            entry = {
                'name': name,
                'key_hex': key_bytes.hex()[:32] + '...',
                'addr_u': result['uncompressed'],
                'addr_c': result['compressed'],
            }
            self.results['candidates'].append(entry)

            # Check for matches
            for target in targets:
                if result['uncompressed'] == target:
                    print(f"\n  ★★★★★ MATCH (uncompressed)! {name} → {target}")
                    self.results['matches'].append({**entry, 'match_type': 'uncompressed', 'target': target})
                if result['compressed'] == target:
                    print(f"\n  ★★★★★ MATCH (compressed)! {name} → {target}")
                    self.results['matches'].append({**entry, 'match_type': 'compressed', 'target': target})

            # Check for near matches (same first bytes of hash160)
            for target_name, target_h160 in self.target_h160.items():
                test_h160_u = base58_decode(result['uncompressed'])[1:21]
                test_h160_c = base58_decode(result['compressed'])[1:21]

                matching_u = sum(1 for a, b in zip(target_h160, test_h160_u) if a == b)
                matching_c = sum(1 for a, b in zip(target_h160, test_h160_c) if a == b)

                if matching_u >= 3:
                    self.results['near_matches'].append({
                        'name': name,
                        'target': target_name,
                        'matching_bytes': matching_u,
                        'type': 'uncompressed',
                    })
                if matching_c >= 3:
                    self.results['near_matches'].append({
                        'name': name,
                        'target': target_name,
                        'matching_bytes': matching_c,
                        'type': 'compressed',
                    })

        print(f"\n  Tested {self.results['methods_tested']} candidates")

    def run(self):
        """Run extended key derivation research"""
        candidates = self.generate_candidates()
        self.test_candidates(candidates)

        # Summary
        print("\n" + "═" * 70)
        print("EXTENDED KEY DERIVATION SUMMARY")
        print("═" * 70)

        print(f"\n  Candidates tested: {self.results['methods_tested']}")
        print(f"  Direct matches: {len(self.results['matches'])}")
        print(f"  Near matches (≥3 bytes): {len(self.results['near_matches'])}")

        if self.results['near_matches']:
            print("\n  Best near matches:")
            for nm in sorted(self.results['near_matches'], key=lambda x: -x['matching_bytes'])[:10]:
                print(f"    {nm['name']}: {nm['matching_bytes']} bytes match {nm['target']}")

        # Save results
        output_file = SCRIPT_DIR / 'KEY_DERIVATION_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

        return self.results

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    research = ExtendedKeyDerivation()
    research.run()
