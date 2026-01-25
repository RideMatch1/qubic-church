#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DEEP GENESIS RESEARCH                                       ║
║                                                                                ║
║  CFB said: "The private key is hidden in the address itself"                  ║
║  Let's find it.                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import struct
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# DATA PATHS
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"
PATOSHI_FILE = DATA_DIR / "patoshi-addresses.json"

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Genesis Address
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

# Block 1 address (first Satoshi mining reward after genesis)
BLOCK1_ADDRESS = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"

# CFB Signature address
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"

# POCC (Proof of Capacity Consortium) - CFB related
POCC_ADDRESSES = [
    "1PoCC39H5PGnfBrXLkHxMqD3MQvPbBDqjQ",  # Known POCC address
]

# CFB Numbers
CFB_NUMBERS = [27, 37, 42, 127, 576]

# Known Matrix coordinates
KNOWN_COORDS = {
    (6, 33): "Core Computor / POCC",
    (45, 92): "CFB Genesis Entry",
    (82, 39): "Bridge Exit Node",
    (21, 21): "Memory Sector",
    (64, 64): "Vision Center",
}

# Base58 alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# ═══════════════════════════════════════════════════════════════════════════════
# BASE58 FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def base58_decode(s: str) -> bytes:
    """Decode Base58 string to bytes"""
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)

    # Convert to bytes
    result = []
    while num > 0:
        result.append(num % 256)
        num //= 256

    # Add leading zeros
    for char in s:
        if char == '1':
            result.append(0)
        else:
            break

    return bytes(reversed(result))

def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58 string"""
    num = int.from_bytes(data, 'big')
    result = []
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(BASE58_ALPHABET[rem])

    # Add leading '1's for leading zero bytes
    for byte in data:
        if byte == 0:
            result.append('1')
        else:
            break

    return ''.join(reversed(result))

def address_to_hash160(address: str) -> bytes:
    """Extract HASH160 (RIPEMD160(SHA256(pubkey))) from address"""
    decoded = base58_decode(address)
    # Format: version (1 byte) + hash160 (20 bytes) + checksum (4 bytes)
    return decoded[1:21]

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX LOADER
# ═══════════════════════════════════════════════════════════════════════════════

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']
        print(f"✓ Loaded Anna Matrix: {len(self.data)}×{len(self.data[0])}")

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

    def get_row(self, row: int) -> List[int]:
        return [self.query(row, c) for c in range(128)]

    def get_col(self, col: int) -> List[int]:
        return [self.query(r, col) for r in range(128)]

# ═══════════════════════════════════════════════════════════════════════════════
# RESEARCH CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class GenesisResearcher:
    def __init__(self):
        print("═" * 70)
        print("           DEEP GENESIS RESEARCH")
        print("═" * 70)

        self.matrix = Matrix()
        self.discoveries = []

        # Load Patoshi data
        with open(PATOSHI_FILE, 'r') as f:
            patoshi = json.load(f)
        self.patoshi_records = patoshi.get('records', [])
        print(f"✓ Loaded {len(self.patoshi_records)} Patoshi records")

    def log_discovery(self, title: str, data: dict):
        """Log a discovery"""
        self.discoveries.append({'title': title, 'data': data})
        print(f"\n  ★★★ DISCOVERY: {title}")
        for k, v in data.items():
            print(f"      {k}: {v}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 1: Genesis Address Decoding
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_genesis_address(self):
        """Deep analysis of Genesis address structure"""
        print("\n" + "─" * 70)
        print("PHASE 1: GENESIS ADDRESS STRUCTURE ANALYSIS")
        print("─" * 70)

        addr = GENESIS_ADDRESS
        print(f"\n  Genesis Address: {addr}")
        print(f"  Length: {len(addr)} characters")

        # Decode to bytes
        decoded = base58_decode(addr)
        print(f"  Decoded length: {len(decoded)} bytes")
        print(f"  Hex: {decoded.hex()}")

        # Extract components
        version = decoded[0]
        hash160 = decoded[1:21]
        checksum = decoded[21:25]

        print(f"\n  Version byte: 0x{version:02x}")
        print(f"  HASH160: {hash160.hex()}")
        print(f"  Checksum: {checksum.hex()}")

        # Map each byte to Anna Matrix
        print("\n  Mapping bytes to Anna Matrix:")
        for i, byte in enumerate(hash160):
            row = byte % 128
            col = (byte >> 1) % 128  # Alternative: shift
            value = self.matrix.query(row, col)
            cfb_marker = " ★ CFB" if value in CFB_NUMBERS or -value in CFB_NUMBERS else ""
            print(f"    Byte {i:2d}: 0x{byte:02x} ({byte:3d}) → [{row:3d},{col:3d}] = {value:+4d}{cfb_marker}")

        # Check if hash160 bytes encode coordinates
        print("\n  Testing byte pairs as coordinates:")
        for i in range(0, 20, 2):
            row, col = hash160[i] % 128, hash160[i+1] % 128
            value = self.matrix.query(row, col)
            cfb_marker = " ★ CFB" if value in CFB_NUMBERS or -value in CFB_NUMBERS else ""
            print(f"    Bytes [{i},{i+1}]: [{row:3d},{col:3d}] = {value:+4d}{cfb_marker}")

            if value is not None and (value in CFB_NUMBERS or -value in CFB_NUMBERS):
                self.log_discovery(f"Genesis byte pair {i},{i+1} gives CFB number", {
                    'bytes': f"{hash160[i]:02x}{hash160[i+1]:02x}",
                    'coords': (row, col),
                    'value': value
                })

        # XOR analysis
        print("\n  XOR analysis of hash160:")
        xor_all = 0
        for byte in hash160:
            xor_all ^= byte
        print(f"    XOR of all bytes: {xor_all} (0x{xor_all:02x})")

        if xor_all in CFB_NUMBERS or 128 - xor_all in CFB_NUMBERS:
            self.log_discovery("Genesis hash160 XOR relates to CFB", {'xor': xor_all})

        # Sum analysis
        sum_all = sum(hash160)
        print(f"    Sum of all bytes: {sum_all}")
        print(f"    Sum mod 128: {sum_all % 128}")
        print(f"    Sum mod 256: {sum_all % 256}")

        row, col = sum_all % 128, (sum_all // 128) % 128
        value = self.matrix.query(row, col)
        print(f"    Sum → [{row},{col}] = {value}")

        if value in CFB_NUMBERS or -value in CFB_NUMBERS:
            self.log_discovery("Genesis hash160 sum gives CFB number", {
                'sum': sum_all,
                'coords': (row, col),
                'value': value
            })

        return hash160

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 2: Address Character Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_address_characters(self):
        """Analyze character patterns in Genesis address"""
        print("\n" + "─" * 70)
        print("PHASE 2: ADDRESS CHARACTER PATTERN ANALYSIS")
        print("─" * 70)

        addr = GENESIS_ADDRESS

        # Position in Base58 alphabet
        print("\n  Character → Base58 position → Matrix value:")
        positions = []
        for i, char in enumerate(addr):
            pos = BASE58_ALPHABET.index(char)
            positions.append(pos)
            row, col = pos % 128, i % 128
            value = self.matrix.query(row, col)
            cfb_marker = " ★" if value in CFB_NUMBERS or -value in CFB_NUMBERS else ""
            print(f"    '{char}' at [{i:2d}]: pos={pos:2d} → [{row:3d},{col:3d}] = {value:+4d}{cfb_marker}")

        # Check pairs of positions
        print("\n  Adjacent character pair analysis:")
        for i in range(len(positions) - 1):
            row, col = positions[i] % 128, positions[i+1] % 128
            value = self.matrix.query(row, col)
            if value is not None and (value in CFB_NUMBERS or -value in CFB_NUMBERS):
                self.log_discovery(f"Address chars {i},{i+1} give CFB", {
                    'chars': addr[i:i+2],
                    'positions': (positions[i], positions[i+1]),
                    'value': value
                })

        # XOR adjacent positions
        print("\n  XOR of adjacent position pairs:")
        for i in range(0, len(positions) - 1, 2):
            xor = positions[i] ^ positions[i+1]
            if xor in CFB_NUMBERS:
                self.log_discovery(f"Position XOR at {i} gives CFB", {
                    'positions': (positions[i], positions[i+1]),
                    'xor': xor
                })
                print(f"    pos[{i}] XOR pos[{i+1}] = {positions[i]} XOR {positions[i+1]} = {xor} ★ CFB")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 3: 1CFB Address Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_1cfb_address(self):
        """Deep analysis of 1CFB signature address"""
        print("\n" + "─" * 70)
        print("PHASE 3: 1CFB SIGNATURE ADDRESS ANALYSIS")
        print("─" * 70)

        addr = CFB_ADDRESS
        print(f"\n  CFB Address: {addr}")

        # Decode
        decoded = base58_decode(addr)
        hash160 = decoded[1:21]

        print(f"  HASH160: {hash160.hex()}")

        # Compare with Genesis
        genesis_hash = address_to_hash160(GENESIS_ADDRESS)

        print("\n  Comparing with Genesis hash160:")
        xor_result = bytes(a ^ b for a, b in zip(hash160, genesis_hash))
        print(f"    XOR result: {xor_result.hex()}")

        # Check XOR bytes for patterns
        print("\n  XOR bytes analysis:")
        for i, byte in enumerate(xor_result):
            if byte in CFB_NUMBERS or 128 - byte in [27, 37, 42]:
                print(f"    Byte {i}: {byte} ★ CFB related")

        # Map to matrix
        print("\n  1CFB hash160 → Matrix mapping:")
        values = []
        for i, byte in enumerate(hash160):
            row, col = byte % 128, (i * 7) % 128  # Using position offset
            value = self.matrix.query(row, col)
            values.append(value)
            if value is not None and (value in CFB_NUMBERS or -value in CFB_NUMBERS):
                print(f"    Byte {i}: [{row},{col}] = {value} ★ CFB")

        # Check if values spell something
        print(f"\n  Matrix values from 1CFB: {values[:10]}...")

        # Sum of values
        valid_values = [v for v in values if v is not None]
        if valid_values:
            print(f"  Sum of values: {sum(valid_values)}")
            print(f"  Sum mod 128: {sum(valid_values) % 128}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 4: Matrix Node Connections
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_matrix_nodes(self):
        """Analyze known matrix nodes and their connections"""
        print("\n" + "─" * 70)
        print("PHASE 4: MATRIX NODE CONNECTIONS")
        print("─" * 70)

        print("\n  Known significant nodes:")
        for coords, desc in KNOWN_COORDS.items():
            value = self.matrix.query(coords[0], coords[1])
            print(f"    {desc}:")
            print(f"      Coords: [{coords[0]},{coords[1]}]")
            print(f"      Value: {value}")

            # Get 8 neighbors
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (coords[0] + dr) % 128, (coords[1] + dc) % 128
                    nv = self.matrix.query(nr, nc)
                    neighbors.append(nv)

            print(f"      Neighbors: {neighbors}")
            print(f"      Neighbor sum: {sum(n for n in neighbors if n)}")

            # Check if neighbor sum is CFB related
            n_sum = sum(n for n in neighbors if n)
            if n_sum in CFB_NUMBERS or -n_sum in CFB_NUMBERS or n_sum % 27 == 0:
                self.log_discovery(f"{desc} neighbor sum is CFB related", {
                    'coords': coords,
                    'neighbor_sum': n_sum
                })

        # Check paths between nodes
        print("\n  Paths between nodes:")
        nodes = list(KNOWN_COORDS.keys())
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                # Manhattan distance
                dist = abs(n1[0] - n2[0]) + abs(n1[1] - n2[1])

                # Direct line values
                if n1[0] == n2[0]:  # Same row
                    line_values = [self.matrix.query(n1[0], c) for c in range(min(n1[1], n2[1]), max(n1[1], n2[1]) + 1)]
                elif n1[1] == n2[1]:  # Same column
                    line_values = [self.matrix.query(r, n1[1]) for r in range(min(n1[0], n2[0]), max(n1[0], n2[0]) + 1)]
                else:
                    line_values = []

                if line_values:
                    valid = [v for v in line_values if v is not None]
                    if valid:
                        print(f"    {KNOWN_COORDS[n1][:15]} → {KNOWN_COORDS[n2][:15]}")
                        print(f"      Distance: {dist}, Line sum: {sum(valid)}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 5: Patoshi Pattern Deep Dive
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_patoshi_patterns(self):
        """Look for hidden patterns in Patoshi data"""
        print("\n" + "─" * 70)
        print("PHASE 5: PATOSHI PATTERN DEEP DIVE")
        print("─" * 70)

        # Group by block height patterns
        print("\n  Analyzing block height patterns:")

        # Blocks that hit CFB numbers when hashed
        cfb_blocks = []
        for record in self.patoshi_records:
            block = record.get('blockHeight', 0)
            pubkey = record.get('pubkey', '')

            if not pubkey:
                continue

            # Hash pubkey
            h = hashlib.sha256(pubkey.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            value = self.matrix.query(row, col)

            if value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS):
                cfb_blocks.append((block, value, pubkey[:20]))

        print(f"\n  Blocks with pubkeys hitting CFB values: {len(cfb_blocks)}")

        # Check for block number patterns
        block_numbers = [b[0] for b in cfb_blocks]
        if block_numbers:
            print(f"    First 20 blocks: {block_numbers[:20]}")

            # Check differences
            diffs = [block_numbers[i+1] - block_numbers[i] for i in range(min(20, len(block_numbers)-1))]
            print(f"    Differences: {diffs}")

            # Any CFB numbers in differences?
            cfb_diffs = [d for d in diffs if d in CFB_NUMBERS]
            if cfb_diffs:
                self.log_discovery("Block differences contain CFB numbers", {
                    'cfb_diffs': cfb_diffs
                })

        # Check pubkey prefixes
        print("\n  Pubkey prefix analysis:")
        prefix_counts = {}
        for record in self.patoshi_records[:1000]:
            pubkey = record.get('pubkey', '')
            if pubkey:
                prefix = pubkey[:4]
                prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

        # Most common prefixes
        sorted_prefixes = sorted(prefix_counts.items(), key=lambda x: -x[1])[:10]
        print("    Most common prefixes:")
        for prefix, count in sorted_prefixes:
            print(f"      {prefix}: {count}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 6: Timestamp Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_timestamps(self):
        """Deep timestamp analysis"""
        print("\n" + "─" * 70)
        print("PHASE 6: TIMESTAMP DEEP ANALYSIS")
        print("─" * 70)

        # Key timestamps
        timestamps = [
            (0, 1231006505, "Genesis Block"),
            (1, 1231469665, "Block 1"),
            (9, 1231473279, "Block 9 - First TX"),
            (170, 1231731025, "Block 170 - Hal Finney"),
            (576, 1232049795, "Block 576 - CFB Event"),
        ]

        print("\n  Key block timestamps → Matrix:")
        for block, ts, desc in timestamps:
            # Various encodings
            row1 = ts % 128
            col1 = (ts // 128) % 128
            v1 = self.matrix.query(row1, col1)

            row2 = (ts >> 7) % 128
            col2 = ts % 128
            v2 = self.matrix.query(row2, col2)

            # Bytes of timestamp
            ts_bytes = struct.pack('>I', ts)
            row3, col3 = ts_bytes[0] % 128, ts_bytes[1] % 128
            v3 = self.matrix.query(row3, col3)

            print(f"\n    {desc} (block {block}, ts={ts}):")
            print(f"      ts mod: [{row1},{col1}] = {v1}")
            print(f"      ts shift: [{row2},{col2}] = {v2}")
            print(f"      ts bytes: [{row3},{col3}] = {v3}")

            for v in [v1, v2, v3]:
                if v in CFB_NUMBERS or (v is not None and -v in CFB_NUMBERS):
                    self.log_discovery(f"{desc} timestamp gives CFB", {
                        'block': block,
                        'timestamp': ts,
                        'value': v
                    })

        # Genesis timestamp special analysis
        print("\n  Genesis timestamp byte-level analysis:")
        genesis_ts = 1231006505
        ts_bytes = struct.pack('>I', genesis_ts)
        print(f"    Timestamp: {genesis_ts}")
        print(f"    Bytes (big-endian): {ts_bytes.hex()}")
        print(f"    Bytes (little-endian): {struct.pack('<I', genesis_ts).hex()}")

        # Each byte
        for i, b in enumerate(ts_bytes):
            print(f"      Byte {i}: {b} (0x{b:02x})")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 7: Private Key Hypothesis
    # ───────────────────────────────────────────────────────────────────────────

    def test_private_key_hypothesis(self):
        """Test if private key is encoded in address"""
        print("\n" + "─" * 70)
        print("PHASE 7: PRIVATE KEY IN ADDRESS HYPOTHESIS")
        print("─" * 70)

        addr = GENESIS_ADDRESS
        hash160 = address_to_hash160(addr)

        print(f"\n  Genesis hash160: {hash160.hex()}")
        print(f"  Length: {len(hash160) * 8} bits (160 bits)")
        print(f"  Private key needs: 256 bits")

        # Try extending hash160 to 256 bits
        print("\n  Extension methods:")

        # Method 1: SHA256 of hash160
        extended1 = hashlib.sha256(hash160).digest()
        print(f"    SHA256(hash160): {extended1.hex()}")

        # Method 2: Double SHA256
        extended2 = hashlib.sha256(hashlib.sha256(hash160).digest()).digest()
        print(f"    Double SHA256: {extended2.hex()}")

        # Method 3: Concatenate with reverse
        extended3 = hash160 + hash160[::-1][:12]
        print(f"    hash160 + reverse[:12]: {extended3.hex()}")

        # Method 4: XOR with matrix values at hash160 coordinates
        print("\n  Matrix XOR extension:")
        matrix_xor = bytearray(32)
        for i in range(20):
            row, col = hash160[i] % 128, hash160[(i+1) % 20] % 128
            value = self.matrix.query(row, col)
            if value is not None:
                matrix_xor[i] = (hash160[i] ^ (value & 0xFF)) & 0xFF

        # Fill remaining 12 bytes
        for i in range(20, 32):
            j = i - 20
            row, col = hash160[j] % 128, hash160[(j+10) % 20] % 128
            value = self.matrix.query(row, col)
            if value is not None:
                matrix_xor[i] = (hash160[j] ^ (value & 0xFF) ^ 0x27) & 0xFF

        print(f"    Matrix XOR: {bytes(matrix_xor).hex()}")

        # Check if any of these are valid-looking private keys
        print("\n  Testing as private keys (checking range):")
        for name, candidate in [("SHA256", extended1), ("DoubleSHA", extended2), ("MatrixXOR", bytes(matrix_xor))]:
            n = int.from_bytes(candidate, 'big')
            # secp256k1 order
            order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
            if 1 <= n < order:
                print(f"    {name}: Valid range ✓")
            else:
                print(f"    {name}: Out of range")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 8: Cross-Reference with Matrix Seeds
    # ───────────────────────────────────────────────────────────────────────────

    def cross_reference_matrix_seeds(self):
        """Compare matrix-derived patterns with Patoshi"""
        print("\n" + "─" * 70)
        print("PHASE 8: MATRIX SEEDS vs PATOSHI CROSS-REFERENCE")
        print("─" * 70)

        # Extract "seeds" from matrix - rows with special properties
        print("\n  Extracting matrix row signatures:")

        row_sigs = []
        for row in range(128):
            values = self.matrix.get_row(row)
            valid = [v for v in values if v is not None]
            if valid:
                sig = {
                    'row': row,
                    'sum': sum(valid),
                    'xor': 0,
                    'cfb_count': sum(1 for v in valid if v in CFB_NUMBERS or -v in CFB_NUMBERS)
                }
                for v in valid:
                    sig['xor'] ^= (v & 0xFF)
                row_sigs.append(sig)

        # Find rows with CFB-related properties
        print("\n  Rows with high CFB content:")
        cfb_rows = sorted(row_sigs, key=lambda x: -x['cfb_count'])[:10]
        for sig in cfb_rows:
            print(f"    Row {sig['row']:3d}: {sig['cfb_count']} CFB values, sum={sig['sum']}, xor={sig['xor']}")

        # Check if row sums relate to Patoshi block numbers
        print("\n  Checking if row sums match Patoshi blocks:")
        patoshi_blocks = set(r.get('blockHeight', 0) for r in self.patoshi_records)

        matches = []
        for sig in row_sigs:
            if sig['sum'] in patoshi_blocks or abs(sig['sum']) in patoshi_blocks:
                matches.append((sig['row'], sig['sum']))

        if matches:
            print(f"    Found {len(matches)} matches!")
            for row, block in matches[:10]:
                print(f"      Row {row} sum = Block {block}")
                self.log_discovery(f"Row {row} sum matches Patoshi block", {
                    'row': row,
                    'block': block
                })

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self):
        """Execute all research phases"""
        self.analyze_genesis_address()
        self.analyze_address_characters()
        self.analyze_1cfb_address()
        self.analyze_matrix_nodes()
        self.analyze_patoshi_patterns()
        self.analyze_timestamps()
        self.test_private_key_hypothesis()
        self.cross_reference_matrix_seeds()

        # Summary
        print("\n" + "═" * 70)
        print("           RESEARCH COMPLETE")
        print("═" * 70)

        print(f"\n  Total discoveries: {len(self.discoveries)}")
        if self.discoveries:
            print("\n  DISCOVERY SUMMARY:")
            for d in self.discoveries:
                print(f"    ★ {d['title']}")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'discoveries': self.discoveries
        }
        output_file = SCRIPT_DIR / "deep_genesis_results.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    researcher = GenesisResearcher()
    researcher.run_all()
