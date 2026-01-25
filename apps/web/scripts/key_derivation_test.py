#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PRIVATE KEY DERIVATION TEST                                 ║
║                                                                                ║
║  Testing various methods to derive private keys from Genesis/CFB patterns     ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from typing import Optional

# Try to import bitcoin library for address derivation
try:
    import ecdsa
    HAVE_ECDSA = True
except ImportError:
    HAVE_ECDSA = False
    print("Note: ecdsa library not available, skipping key validation")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"
BLOCK1_ADDRESS = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# secp256k1 curve order
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

CFB_NUMBERS = [27, 37, 42, 127]

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

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

    def get_row(self, row: int):
        return [self.query(row, c) for c in range(128)]

# ═══════════════════════════════════════════════════════════════════════════════
# KEY DERIVATION METHODS
# ═══════════════════════════════════════════════════════════════════════════════

class KeyDeriver:
    def __init__(self):
        print("═" * 70)
        print("           PRIVATE KEY DERIVATION TEST")
        print("═" * 70)
        self.matrix = Matrix()
        self.candidates = []

    def add_candidate(self, name: str, key_bytes: bytes, method: str):
        """Add a candidate private key"""
        # Ensure 32 bytes
        if len(key_bytes) < 32:
            key_bytes = key_bytes.rjust(32, b'\x00')
        elif len(key_bytes) > 32:
            key_bytes = key_bytes[:32]

        key_int = int.from_bytes(key_bytes, 'big')

        if 1 <= key_int < SECP256K1_ORDER:
            self.candidates.append({
                'name': name,
                'key_hex': key_bytes.hex(),
                'method': method,
                'valid_range': True
            })
            print(f"  ✓ {name}: {key_bytes.hex()[:32]}...")
        else:
            print(f"  ✗ {name}: Out of valid range")

    def derive_from_genesis_hash160(self):
        """Method 1: Direct hash160 extensions"""
        print("\n" + "─" * 70)
        print("METHOD 1: Genesis hash160 extensions")
        print("─" * 70)

        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]

        # SHA256 extension
        extended = hashlib.sha256(genesis_h160).digest()
        self.add_candidate("Genesis-SHA256", extended, "SHA256(hash160)")

        # Double SHA256
        extended2 = hashlib.sha256(hashlib.sha256(genesis_h160).digest()).digest()
        self.add_candidate("Genesis-DoubleSHA", extended2, "DoubleSHA256(hash160)")

        # Hash160 + reversed
        combined = genesis_h160 + genesis_h160[::-1][:12]
        self.add_candidate("Genesis-WithReverse", combined, "hash160 + reverse[:12]")

    def derive_from_xor_patterns(self):
        """Method 2: XOR patterns between addresses"""
        print("\n" + "─" * 70)
        print("METHOD 2: XOR patterns")
        print("─" * 70)

        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]
        cfb_h160 = base58_decode(CFB_ADDRESS)[1:21]
        block1_h160 = base58_decode(BLOCK1_ADDRESS)[1:21]

        # Genesis XOR 1CFB
        xor1 = bytes(a ^ b for a, b in zip(genesis_h160, cfb_h160))
        extended1 = hashlib.sha256(xor1).digest()
        self.add_candidate("Genesis-XOR-CFB-SHA", extended1, "SHA256(Genesis XOR CFB)")

        # Genesis XOR Block1
        xor2 = bytes(a ^ b for a, b in zip(genesis_h160, block1_h160))
        extended2 = hashlib.sha256(xor2).digest()
        self.add_candidate("Genesis-XOR-Block1-SHA", extended2, "SHA256(Genesis XOR Block1)")

        # All three XORed
        xor3 = bytes(a ^ b ^ c for a, b, c in zip(genesis_h160, cfb_h160, block1_h160))
        extended3 = hashlib.sha256(xor3).digest()
        self.add_candidate("Triple-XOR-SHA", extended3, "SHA256(Genesis XOR CFB XOR Block1)")

    def derive_from_matrix_values(self):
        """Method 3: Matrix value derivation"""
        print("\n" + "─" * 70)
        print("METHOD 3: Matrix-based derivation")
        print("─" * 70)

        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]

        # Use matrix values at hash160 byte coordinates
        matrix_key = bytearray(32)
        for i in range(20):
            row = genesis_h160[i] % 128
            col = genesis_h160[(i+1) % 20] % 128
            value = self.matrix.query(row, col)
            if value is not None:
                # Convert signed value to unsigned byte
                matrix_key[i] = (genesis_h160[i] ^ (value & 0xFF)) & 0xFF

        # Fill remaining with CFB-related values
        for i in range(20, 32):
            j = i - 20
            # Use CFB numbers as modifiers
            cfb_mod = CFB_NUMBERS[j % len(CFB_NUMBERS)]
            matrix_key[i] = (genesis_h160[j] ^ cfb_mod) & 0xFF

        self.add_candidate("Matrix-XOR-Key", bytes(matrix_key), "Matrix values XOR hash160")

        # Use known coordinates
        known_coords = [(6,33), (45,92), (82,39), (21,21), (64,64)]
        coord_key = bytearray(32)
        for i, (r, c) in enumerate(known_coords):
            v = self.matrix.query(r, c) or 0
            coord_key[i*2] = r
            coord_key[i*2 + 1] = (c ^ (v & 0xFF)) & 0xFF

        # Fill rest with hash
        seed = bytes(coord_key[:10])
        fill = hashlib.sha256(seed).digest()
        for i in range(10, 32):
            coord_key[i] = fill[i-10]

        self.add_candidate("KnownCoords-Key", bytes(coord_key), "Known matrix coordinates")

    def derive_from_cfb_numbers(self):
        """Method 4: CFB numbers encoding"""
        print("\n" + "─" * 70)
        print("METHOD 4: CFB numbers encoding")
        print("─" * 70)

        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]

        # XOR with 27 (CFB's main number)
        xor27 = bytes((b ^ 27) & 0xFF for b in genesis_h160)
        extended = hashlib.sha256(xor27).digest()
        self.add_candidate("Genesis-XOR-27-SHA", extended, "SHA256(hash160 XOR 27)")

        # XOR with pattern [27, 37, 42, 127]
        pattern = [27, 37, 42, 127]
        xor_pattern = bytes((genesis_h160[i] ^ pattern[i % 4]) & 0xFF for i in range(20))
        extended2 = hashlib.sha256(xor_pattern).digest()
        self.add_candidate("Genesis-XOR-Pattern-SHA", extended2, "SHA256(hash160 XOR CFB pattern)")

    def derive_from_timestamp(self):
        """Method 5: Genesis timestamp encoding"""
        print("\n" + "─" * 70)
        print("METHOD 5: Timestamp encoding")
        print("─" * 70)

        genesis_timestamp = 1231006505  # Genesis block timestamp
        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]

        # Timestamp as seed
        ts_bytes = genesis_timestamp.to_bytes(4, 'big')
        seed = ts_bytes * 5  # 20 bytes
        xored = bytes((a ^ b) & 0xFF for a, b in zip(genesis_h160, seed))
        extended = hashlib.sha256(xored).digest()
        self.add_candidate("Timestamp-XOR-SHA", extended, "SHA256(hash160 XOR timestamp)")

        # Block 9 timestamp (gives 27 in matrix)
        block9_ts = 1231473279
        ts9_bytes = block9_ts.to_bytes(4, 'big')
        seed9 = ts9_bytes * 5
        xored9 = bytes((a ^ b) & 0xFF for a, b in zip(genesis_h160, seed9))
        extended9 = hashlib.sha256(xored9).digest()
        self.add_candidate("Block9TS-XOR-SHA", extended9, "SHA256(hash160 XOR block9_ts)")

    def derive_from_address_string(self):
        """Method 6: Address string as seed"""
        print("\n" + "─" * 70)
        print("METHOD 6: Address string encoding")
        print("─" * 70)

        # Genesis address as UTF-8
        genesis_bytes = GENESIS_ADDRESS.encode('utf-8')
        key1 = hashlib.sha256(genesis_bytes).digest()
        self.add_candidate("Genesis-String-SHA", key1, "SHA256(address string)")

        # Combined addresses
        combined = (GENESIS_ADDRESS + CFB_ADDRESS).encode('utf-8')
        key2 = hashlib.sha256(combined).digest()
        self.add_candidate("Combined-String-SHA", key2, "SHA256(Genesis + CFB)")

        # "Satoshi Nakamoto" + Genesis
        satoshi = ("Satoshi Nakamoto" + GENESIS_ADDRESS).encode('utf-8')
        key3 = hashlib.sha256(satoshi).digest()
        self.add_candidate("Satoshi-Genesis-SHA", key3, 'SHA256("Satoshi Nakamoto" + Genesis)')

    def test_candidates(self):
        """Test if any candidate produces Genesis address"""
        if not HAVE_ECDSA:
            print("\n  ⚠ Cannot test candidates without ecdsa library")
            return

        print("\n" + "═" * 70)
        print("TESTING CANDIDATE KEYS")
        print("═" * 70)

        for candidate in self.candidates:
            if not candidate['valid_range']:
                continue

            try:
                key_bytes = bytes.fromhex(candidate['key_hex'])
                key_int = int.from_bytes(key_bytes, 'big')

                # Create private key
                signing_key = ecdsa.SigningKey.from_secret_exponent(key_int, curve=ecdsa.SECP256k1)
                verifying_key = signing_key.get_verifying_key()

                # Get uncompressed public key (04 + x + y)
                pubkey = b'\x04' + verifying_key.to_string()

                # Get address
                address = pubkey_to_address(pubkey)

                # Also try compressed
                x = verifying_key.to_string()[:32]
                y_int = int.from_bytes(verifying_key.to_string()[32:], 'big')
                prefix = b'\x02' if y_int % 2 == 0 else b'\x03'
                compressed_pubkey = prefix + x
                compressed_address = pubkey_to_address(compressed_pubkey)

                match_marker = ""
                if address == GENESIS_ADDRESS:
                    match_marker = " ★★★ GENESIS MATCH (uncompressed)!"
                elif compressed_address == GENESIS_ADDRESS:
                    match_marker = " ★★★ GENESIS MATCH (compressed)!"

                print(f"\n  {candidate['name']}:")
                print(f"    Method: {candidate['method']}")
                print(f"    Address (uncomp): {address}{match_marker}")
                print(f"    Address (comp):   {compressed_address}")

            except Exception as e:
                print(f"\n  {candidate['name']}: Error - {e}")

    def run(self):
        """Run all derivation methods"""
        self.derive_from_genesis_hash160()
        self.derive_from_xor_patterns()
        self.derive_from_matrix_values()
        self.derive_from_cfb_numbers()
        self.derive_from_timestamp()
        self.derive_from_address_string()

        print(f"\n  Total candidates: {len(self.candidates)}")
        print(f"  Valid range: {sum(1 for c in self.candidates if c['valid_range'])}")

        self.test_candidates()

        # Save candidates
        output_file = SCRIPT_DIR / "key_candidates.json"
        with open(output_file, 'w') as f:
            json.dump(self.candidates, f, indent=2)
        print(f"\n  Candidates saved to: {output_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    deriver = KeyDeriver()
    deriver.run()
