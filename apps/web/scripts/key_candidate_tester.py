#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    KEY CANDIDATE TESTER                                        ║
║                                                                                ║
║  Test all private key candidates against known Bitcoin addresses               ║
║  - Genesis address                                                             ║
║  - Block 1 address                                                             ║
║  - 1CFB address                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# Try to import ecdsa for key operations
try:
    import ecdsa
    HAVE_ECDSA = True
except ImportError:
    HAVE_ECDSA = False
    print("⚠ ecdsa library not available - trying with hashlib only")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

# Target addresses
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
BLOCK1_ADDRESS = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"

# Known genesis pubkey (compressed and uncompressed)
GENESIS_PUBKEY_UNCOMPRESSED = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# secp256k1 curve order
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

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
    """RIPEMD160(SHA256(data))"""
    sha = hashlib.sha256(data).digest()
    ripemd = hashlib.new('ripemd160', sha).digest()
    return ripemd

def pubkey_to_address(pubkey: bytes) -> str:
    """Convert public key to Bitcoin address"""
    h160 = hash160(pubkey)
    versioned = b'\x00' + h160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

    def find_value(self, value: int) -> List[Tuple[int, int]]:
        results = []
        for row in range(128):
            for col in range(128):
                if self.data[row][col] == value:
                    results.append((row, col))
        return results

# ═══════════════════════════════════════════════════════════════════════════════
# KEY TESTER
# ═══════════════════════════════════════════════════════════════════════════════

class KeyCandidateTester:
    def __init__(self):
        print("═" * 70)
        print("           KEY CANDIDATE TESTER")
        print("═" * 70)
        self.matrix = Matrix()
        self.results = []
        self.target_addresses = [
            GENESIS_ADDRESS,
            BLOCK1_ADDRESS,
            CFB_ADDRESS,
        ]

    def generate_candidates(self) -> List[Tuple[str, bytes]]:
        """Generate all key candidates from matrix patterns"""
        candidates = []

        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]
        cfb_h160 = base58_decode(CFB_ADDRESS)[1:21]

        print("\n  Generating key candidates...")

        # 1. Direct matrix values as key
        print("    [1] Row 27 as key seed...")
        row27 = bytes((self.matrix.query(27, c) + 128) % 256 for c in range(32))
        candidates.append(('row_27_direct', row27))

        # 2. Column 27
        print("    [2] Column 27 as key seed...")
        col27 = bytes((self.matrix.query(r, 27) + 128) % 256 for r in range(32))
        candidates.append(('col_27_direct', col27))

        # 3. Diagonal through origin
        print("    [3] Main diagonal...")
        diag = bytes((self.matrix.query(i, i) + 128) % 256 for i in range(32))
        candidates.append(('diagonal', diag))

        # 4. Anti-diagonal
        print("    [4] Anti-diagonal...")
        anti_diag = bytes((self.matrix.query(i, 127-i) + 128) % 256 for i in range(32))
        candidates.append(('anti_diagonal', anti_diag))

        # 5. Vision center spiral
        print("    [5] Vision center spiral...")
        spiral = []
        for r in range(8):
            for i in range(4):
                v = self.matrix.query(64 - r + i, 64 - r + i)
                if v is not None:
                    spiral.append((v + 128) % 256)
        if len(spiral) >= 32:
            candidates.append(('vision_spiral', bytes(spiral[:32])))

        # 6. All -27 cells row coordinates
        print("    [6] -27 cell rows...")
        minus27_cells = self.matrix.find_value(-27)
        if len(minus27_cells) >= 32:
            candidates.append(('-27_rows', bytes(r for r, c in minus27_cells[:32])))

        # 7. All -27 cells column coordinates
        print("    [7] -27 cell columns...")
        if len(minus27_cells) >= 32:
            candidates.append(('-27_cols', bytes(c for r, c in minus27_cells[:32])))

        # 8. Genesis h160 XOR with row 27
        print("    [8] Genesis XOR row 27...")
        xored = bytes(a ^ b for a, b in zip(genesis_h160, row27[:20]))
        extended = hashlib.sha256(xored).digest()
        candidates.append(('genesis_xor_row27', extended))

        # 9. CFB h160 XOR with matrix
        print("    [9] CFB XOR diagonal...")
        cfb_xor = bytes(a ^ b for a, b in zip(cfb_h160, diag[:20]))
        extended2 = hashlib.sha256(cfb_xor).digest()
        candidates.append(('cfb_xor_diag', extended2))

        # 10. Timestamp-based
        print("    [10] Block 9 timestamp seed...")
        ts_seed = bytes([
            27, 37, 42, 127,  # CFB numbers
            20, 127,  # Block 9 coords
            0, 2,  # Genesis -27 coords
            81, 28,  # Block 27 coords
            64, 64,  # Vision center
        ])
        ts_extended = hashlib.sha256(ts_seed + genesis_h160).digest()
        candidates.append(('timestamp_seed', ts_extended))

        # 11. XOR of all CFB numbers
        print("    [11] CFB number pattern...")
        cfb_pattern = bytes([27, 37, 42, 127] * 8)
        cfb_extended = hashlib.sha256(cfb_pattern + genesis_h160).digest()
        candidates.append(('cfb_pattern', cfb_extended))

        # 12. "Satoshi" hashed
        print("    [12] 'Satoshi Nakamoto' seed...")
        satoshi = hashlib.sha256(b"Satoshi Nakamoto").digest()
        candidates.append(('satoshi_name', satoshi))

        # 13. Genesis address as UTF-8
        print("    [13] Genesis address as seed...")
        genesis_seed = hashlib.sha256(GENESIS_ADDRESS.encode()).digest()
        candidates.append(('genesis_address_hash', genesis_seed))

        # 14. Combined CFB+Genesis
        print("    [14] CFB + Genesis combined...")
        combined = hashlib.sha256(cfb_h160 + genesis_h160).digest()
        candidates.append(('cfb_genesis_combined', combined))

        # 15. Matrix cell (0,2) neighbors
        print("    [15] Genesis-27 cell neighborhood...")
        neighbors = []
        for dr in range(-4, 5):
            for dc in range(-4, 5):
                v = self.matrix.query(dr, 2 + dc)
                if v is not None:
                    neighbors.append((v + 128) % 256)
        if len(neighbors) >= 32:
            candidates.append(('genesis27_neighborhood', bytes(neighbors[:32])))

        # 16. Row that contains most -27 values
        print("    [16] Row with most -27 values...")
        row_counts = {}
        for r, c in minus27_cells:
            row_counts[r] = row_counts.get(r, 0) + 1
        if row_counts:
            best_row = max(row_counts.items(), key=lambda x: x[1])[0]
            row_values = bytes((self.matrix.query(best_row, c) + 128) % 256 for c in range(32))
            candidates.append((f'row_{best_row}_max27', row_values))

        # 17. Block heights as seed
        print("    [17] CFB block heights...")
        blocks = bytes([9, 27, 37, 42, 127, 170, 0, 1, 2, 3, 4, 5, 6, 7,
                       8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
        block_seed = hashlib.sha256(blocks).digest()
        candidates.append(('block_heights', block_seed))

        # 18. XOR chain from (0,2)
        print("    [18] XOR chain from Genesis-27...")
        chain_values = [self.matrix.query(0, 2)]
        row, col = 0, 2
        for _ in range(31):
            best_next = None
            best_score = -1
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (row + dr) % 128, (col + dc) % 128
                    v = self.matrix.query(nr, nc)
                    if v is not None:
                        score = abs(v) if abs(v) in [27, 37, 42, 127] else 0
                        if score > best_score:
                            best_score = score
                            best_next = (nr, nc, v)
            if best_next:
                row, col, v = best_next
                chain_values.append(v)
            else:
                break

        if len(chain_values) >= 32:
            chain_bytes = bytes((v + 128) % 256 for v in chain_values[:32])
            candidates.append(('xor_chain_genesis27', chain_bytes))

        print(f"\n  Generated {len(candidates)} key candidates")
        return candidates

    def test_candidate(self, name: str, key_bytes: bytes) -> Optional[str]:
        """Test a single key candidate"""
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b'\x00')
        elif len(key_bytes) > 32:
            key_bytes = key_bytes[:32]

        key_int = int.from_bytes(key_bytes, 'big')

        # Check valid range
        if key_int < 1 or key_int >= SECP256K1_ORDER:
            return None

        if not HAVE_ECDSA:
            return None

        try:
            # Create private key
            signing_key = ecdsa.SigningKey.from_secret_exponent(key_int, curve=ecdsa.SECP256k1)
            verifying_key = signing_key.get_verifying_key()

            # Uncompressed public key
            pubkey_uncompressed = b'\x04' + verifying_key.to_string()
            address_uncompressed = pubkey_to_address(pubkey_uncompressed)

            # Compressed public key
            x = verifying_key.to_string()[:32]
            y_int = int.from_bytes(verifying_key.to_string()[32:], 'big')
            prefix = b'\x02' if y_int % 2 == 0 else b'\x03'
            pubkey_compressed = prefix + x
            address_compressed = pubkey_to_address(pubkey_compressed)

            return {
                'uncompressed': address_uncompressed,
                'compressed': address_compressed
            }

        except Exception as e:
            return None

    def run_tests(self):
        """Test all candidates"""
        candidates = self.generate_candidates()

        print("\n" + "═" * 70)
        print("TESTING KEY CANDIDATES")
        print("═" * 70)

        if not HAVE_ECDSA:
            print("\n  ⚠ Cannot test keys without ecdsa library")
            print("  Install with: pip install ecdsa")
            return

        matches_found = []

        for name, key_bytes in candidates:
            result = self.test_candidate(name, key_bytes)

            if result is None:
                continue

            # Check for matches
            for addr in self.target_addresses:
                if result['uncompressed'] == addr:
                    print(f"\n  ★★★★★ MATCH FOUND (uncompressed)!")
                    print(f"    Candidate: {name}")
                    print(f"    Key: {key_bytes.hex()}")
                    print(f"    Address: {addr}")
                    matches_found.append((name, key_bytes, addr, 'uncompressed'))

                if result['compressed'] == addr:
                    print(f"\n  ★★★★★ MATCH FOUND (compressed)!")
                    print(f"    Candidate: {name}")
                    print(f"    Key: {key_bytes.hex()}")
                    print(f"    Address: {addr}")
                    matches_found.append((name, key_bytes, addr, 'compressed'))

            # Show some sample addresses
            self.results.append({
                'name': name,
                'key_hex': key_bytes.hex(),
                'address_uncompressed': result['uncompressed'],
                'address_compressed': result['compressed']
            })

        # Summary
        print("\n" + "═" * 70)
        print("TEST RESULTS")
        print("═" * 70)

        print(f"\n  Candidates tested: {len(self.results)}")
        print(f"  Matches found: {len(matches_found)}")

        if not matches_found:
            print("\n  No direct matches to target addresses.")
            print("\n  Sample generated addresses:")
            for r in self.results[:10]:
                print(f"\n    {r['name']}:")
                print(f"      Key: {r['key_hex'][:32]}...")
                print(f"      Addr (u): {r['address_uncompressed']}")
                print(f"      Addr (c): {r['address_compressed']}")

        # Check for similar addresses
        print("\n  Checking for similar addresses...")
        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]

        for r in self.results:
            test_h160 = base58_decode(r['address_uncompressed'])[1:21]
            matching_bytes = sum(1 for a, b in zip(genesis_h160, test_h160) if a == b)
            if matching_bytes >= 3:
                print(f"    {r['name']}: {matching_bytes} matching bytes with Genesis")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'candidates_tested': len(self.results),
            'matches_found': len(matches_found),
            'matches': matches_found,
            'results': self.results
        }

        output_file = SCRIPT_DIR / 'key_test_results.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tester = KeyCandidateTester()
    tester.run_tests()
