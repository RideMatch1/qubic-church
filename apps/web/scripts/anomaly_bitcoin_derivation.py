#!/usr/bin/env python3
"""
ANOMALY BITCOIN KEY DERIVATION
==============================

Derives potential Bitcoin private keys from the 68 Anna Matrix anomaly cells.

Anomaly Facts:
- 68 cells break the 99.6% point-symmetry
- Column 22: 13 anomalies at rows 20-32
- Column 97: 14 anomalies at rows 48-64
- Position [22,22] = +100 is the only self-match

Target: Find keys that generate 1CFB or related addresses
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Try to import required libraries
try:
    from ecdsa import SigningKey, SECP256k1
    HAVE_ECDSA = True
except ImportError:
    HAVE_ECDSA = False
    print("Warning: ecdsa library not available")

try:
    import base58
    HAVE_BASE58 = True
except ImportError:
    HAVE_BASE58 = False

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
ANOMALY_FILE = DATA_DIR / "anna-matrix-anomalies.json"

# Base58 alphabet for manual encoding if needed
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# secp256k1 order
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Known addresses to check against
KNOWN_ADDRESSES = [
    "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT",  # CFB main
    "1CFBpdLNULnV1F1frie8rHU9DqwufEiQXU",  # Best candidate from prior analysis
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis
    "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",  # Block 1
    "1CFBjSVcKwVmsLJeKAmHcZUpiFjBZchPDV",
    "1CFBYPRm2KaMT3E3RcCcuVad8n6M2ptHVW",
    "1CFBFt9tZinRkEtWfSTPSjipU8Ee98tJvv",
    "1CFBNezXLEeD5L9XME3LyckDqvZ6A8pwbm",
    "1CFBK3qzZLSaVsabrkPbzR2Fcdbxkp9wud",
    "1CFBJC5HAHQXBdq8MHzkdKz2owT3DWTZhE",
]


def base58_encode_manual(data: bytes) -> str:
    """Manual base58 encoding"""
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


def private_key_to_address(private_key_bytes: bytes) -> Optional[Dict]:
    """Convert private key to Bitcoin addresses (compressed and uncompressed)"""
    if not HAVE_ECDSA:
        return None

    # Validate key is in valid range
    key_int = int.from_bytes(private_key_bytes, 'big')
    if key_int < 1 or key_int >= SECP256K1_ORDER:
        return None

    try:
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Uncompressed public key (04 + x + y)
        pubkey_uncompressed = b'\x04' + vk.to_string()

        # Compressed public key (02/03 + x)
        x = vk.to_string()[:32]
        y_int = int.from_bytes(vk.to_string()[32:], 'big')
        prefix = b'\x02' if y_int % 2 == 0 else b'\x03'
        pubkey_compressed = prefix + x

        # Hash160
        h160_u = hash160(pubkey_uncompressed)
        h160_c = hash160(pubkey_compressed)

        # Create addresses
        def make_address(h160):
            versioned = b'\x00' + h160
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            if HAVE_BASE58:
                return base58.b58encode(versioned + checksum).decode('utf-8')
            else:
                return base58_encode_manual(versioned + checksum)

        addr_u = make_address(h160_u)
        addr_c = make_address(h160_c)

        # WIF format
        extended = b'\x80' + private_key_bytes
        extended_c = b'\x80' + private_key_bytes + b'\x01'
        wif_checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
        wif_c_checksum = hashlib.sha256(hashlib.sha256(extended_c).digest()).digest()[:4]

        if HAVE_BASE58:
            wif = base58.b58encode(extended + wif_checksum).decode('utf-8')
            wif_c = base58.b58encode(extended_c + wif_c_checksum).decode('utf-8')
        else:
            wif = base58_encode_manual(extended + wif_checksum)
            wif_c = base58_encode_manual(extended_c + wif_c_checksum)

        return {
            'address_uncompressed': addr_u,
            'address_compressed': addr_c,
            'hash160_uncompressed': h160_u.hex(),
            'hash160_compressed': h160_c.hex(),
            'wif_uncompressed': wif,
            'wif_compressed': wif_c,
            'private_key_hex': private_key_bytes.hex(),
        }
    except Exception as e:
        return None


class AnomalyBitcoinDerivation:
    """Derive Bitcoin keys from Anna Matrix anomalies"""

    def __init__(self):
        print("=" * 80)
        print("ANOMALY BITCOIN KEY DERIVATION")
        print("=" * 80)
        print()

        self.anomaly_data = self.load_anomaly_data()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'source': 'anna-matrix-anomalies.json',
            'total_anomalies': 68,
            'methods_tested': 0,
            'keys_generated': 0,
            'matches_found': [],
            'near_matches': [],
            'candidates': [],
            'method_results': {}
        }

    def load_anomaly_data(self) -> Dict:
        """Load anomaly data from JSON"""
        print(f"Loading anomaly data from: {ANOMALY_FILE}")
        with open(ANOMALY_FILE, 'r') as f:
            data = json.load(f)

        print(f"  Total anomalies: {data['statistics']['anomalyCells']}")
        print(f"  Special position [22,22] value: {data['specialPosition']['value']}")
        print()
        return data

    def generate_key_candidates(self) -> List[Tuple[str, bytes, str]]:
        """Generate key candidates using various methods
        Returns: List of (method_name, key_bytes, description)
        """
        candidates = []
        anomalies = self.anomaly_data['anomalies']
        special = self.anomaly_data['specialPosition']

        print("Generating key candidates from anomaly patterns...")
        print("-" * 80)

        # ================================================================
        # METHOD 1: Concatenate anomaly values as bytes (signed to unsigned)
        # ================================================================
        print("  [1] Concatenating anomaly values as bytes...")

        # All 68 values as signed bytes (+128 to make unsigned)
        values = [(a['value'] + 128) % 256 for a in anomalies]

        # First 32 anomaly values
        if len(values) >= 32:
            key1a = bytes(values[:32])
            candidates.append(('values_first_32', key1a, 'First 32 anomaly values'))

        # Last 32 anomaly values
        if len(values) >= 32:
            key1b = bytes(values[-32:])
            candidates.append(('values_last_32', key1b, 'Last 32 anomaly values'))

        # SHA256 of all values
        all_values = bytes(values)
        candidates.append(('values_sha256', hashlib.sha256(all_values).digest(),
                          'SHA256 of all 68 anomaly values'))

        # Double SHA256
        candidates.append(('values_sha256_double', hashlib.sha256(hashlib.sha256(all_values).digest()).digest(),
                          'Double SHA256 of all values'))

        # ================================================================
        # METHOD 2: Use anomaly positions as coordinates
        # ================================================================
        print("  [2] Using anomaly positions as coordinates...")

        # Concatenate row,col pairs
        positions = []
        for a in anomalies:
            positions.extend([a['pos'][0], a['pos'][1]])

        if len(positions) >= 32:
            candidates.append(('positions_first_32', bytes(positions[:32]),
                              'First 32 position coordinates'))
            candidates.append(('positions_sha256', hashlib.sha256(bytes(positions)).digest(),
                              'SHA256 of all position coordinates'))

        # Use positions XOR values
        pos_val_xor = []
        for a in anomalies:
            xor_val = (a['pos'][0] ^ a['pos'][1] ^ ((a['value'] + 128) % 256)) % 256
            pos_val_xor.append(xor_val)
        if len(pos_val_xor) >= 32:
            candidates.append(('pos_val_xor', bytes(pos_val_xor[:32]),
                              'Position XOR value for each anomaly'))

        # ================================================================
        # METHOD 3: XOR combinations of values
        # ================================================================
        print("  [3] XOR combinations of values...")

        # Column 22 values XOR
        col22_values = [a['value'] for a in anomalies if a['pos'][1] == 22]
        if col22_values:
            xor_result = 0
            for v in col22_values:
                xor_result ^= (v + 128) % 256
            xor_expanded = bytes([xor_result] * 32)
            candidates.append(('col22_xor_expanded', xor_expanded,
                              f'Column 22 XOR result ({xor_result}) expanded'))
            candidates.append(('col22_xor_sha256', hashlib.sha256(bytes([(v+128)%256 for v in col22_values])).digest(),
                              'SHA256 of Column 22 values'))

        # Column 97 values XOR
        col97_values = [a['value'] for a in anomalies if a['pos'][1] == 97]
        if col97_values:
            xor_result = 0
            for v in col97_values:
                xor_result ^= (v + 128) % 256
            candidates.append(('col97_xor_sha256', hashlib.sha256(bytes([(v+128)%256 for v in col97_values])).digest(),
                              'SHA256 of Column 97 values'))

        # XOR all values together
        full_xor = 0
        for a in anomalies:
            full_xor ^= (a['value'] + 128) % 256
        candidates.append(('all_values_xor', hashlib.sha256(bytes([full_xor] * 32)).digest(),
                          f'All values XOR ({full_xor}) -> SHA256'))

        # XOR pairs (value with mirror value)
        pair_xors = []
        for a in anomalies:
            xor = ((a['value'] + 128) % 256) ^ ((a['mirrorValue'] + 128) % 256)
            pair_xors.append(xor)
        if len(pair_xors) >= 32:
            candidates.append(('pair_xors', bytes(pair_xors[:32]),
                              'XOR of value with mirror value'))

        # ================================================================
        # METHOD 4: SHA256 of the anomaly pattern
        # ================================================================
        print("  [4] SHA256 of anomaly patterns...")

        # Pattern as JSON string
        pattern_str = json.dumps(self.anomaly_data['anomalies'], sort_keys=True)
        candidates.append(('pattern_sha256', hashlib.sha256(pattern_str.encode()).digest(),
                          'SHA256 of full anomaly pattern'))

        # Pattern of sums
        sums = [(a['sum'] + 256) % 512 for a in anomalies]  # Keep more range
        sums_bytes = []
        for s in sums:
            sums_bytes.append(s % 256)
        if len(sums_bytes) >= 32:
            candidates.append(('sums_first_32', bytes(sums_bytes[:32]),
                              'First 32 sum values'))
        candidates.append(('sums_sha256', hashlib.sha256(bytes(sums_bytes)).digest(),
                          'SHA256 of all sum values'))

        # ================================================================
        # METHOD 5: Use [22,22] = 100 as a seed
        # ================================================================
        print("  [5] Using [22,22] = 100 as seed...")

        # Various encodings of 100
        candidates.append(('seed_100', hashlib.sha256(b'100').digest(),
                          'SHA256 of "100"'))
        candidates.append(('seed_100_bytes', hashlib.sha256(bytes([100])).digest(),
                          'SHA256 of byte 100'))

        # 100 repeated
        candidates.append(('seed_100_x32', bytes([100] * 32),
                          '100 repeated 32 times'))

        # Position + value combined
        seed_22_22_100 = bytes([22, 22, 100, 22, 22, 100] * 5 + [22, 22])
        candidates.append(('seed_22_22_100', hashlib.sha256(seed_22_22_100).digest(),
                          'Pattern [22,22,100] SHA256'))

        # The special position properties
        coord_sum = special['properties']['coordinateSum']  # 127
        value_xor_127 = special['properties']['valueXor127']  # 27

        candidates.append(('special_coords', hashlib.sha256(bytes([22, 22, 100, coord_sum, value_xor_127])).digest(),
                          f'Special coords: [22,22,100,{coord_sum},{value_xor_127}]'))

        # ================================================================
        # METHOD 6: Column-specific derivations
        # ================================================================
        print("  [6] Column-specific derivations...")

        key_columns = self.anomaly_data['keyColumns']

        for col_info in key_columns:
            col = col_info['column']
            rows = col_info['rows']

            # Extract values for this column
            col_values = []
            for a in anomalies:
                if a['pos'][1] == col:
                    col_values.append((a['value'] + 128) % 256)

            if col_values:
                # Direct bytes (padded if needed)
                if len(col_values) >= 32:
                    candidates.append((f'col{col}_direct', bytes(col_values[:32]),
                                      f'Column {col} values direct'))
                else:
                    # Pad with column number
                    padded = col_values + [col] * (32 - len(col_values))
                    candidates.append((f'col{col}_padded', bytes(padded),
                                      f'Column {col} values padded'))

                # SHA256
                candidates.append((f'col{col}_sha256', hashlib.sha256(bytes(col_values)).digest(),
                                  f'Column {col} values SHA256'))

                # With rows included
                row_col_data = []
                for r in rows:
                    row_col_data.extend([r, col])
                candidates.append((f'col{col}_with_rows', hashlib.sha256(bytes(row_col_data)).digest(),
                                  f'Column {col} with row positions SHA256'))

        # ================================================================
        # METHOD 7: Mathematical relationships
        # ================================================================
        print("  [7] Mathematical relationships...")

        # 22 + 97 = 119 (col arithmetic from patterns)
        candidates.append(('col_arithmetic_119', hashlib.sha256(bytes([119] * 32)).digest(),
                          'Column arithmetic 22+97=119'))

        # 22 XOR 97 = 119
        candidates.append(('col_xor_119', hashlib.sha256(bytes([22 ^ 97] * 32)).digest(),
                          'Column XOR 22^97=119'))

        # The -121 values (appears twice at positions [23,22] and [29,22])
        neg_121 = (-121 + 256) % 256  # = 135
        candidates.append(('neg121_seed', hashlib.sha256(bytes([neg_121] * 32)).digest(),
                          'Value -121 (Qubic constant) as seed'))

        # Combined value -121 from 1CFB connection
        combined = self.anomaly_data['connectionTo1CFB']['combinedValue']  # -121
        candidates.append(('cfb_combined', hashlib.sha256(str(combined).encode()).digest(),
                          f'CFB combined value {combined}'))

        # ================================================================
        # METHOD 8: Mirror relationships
        # ================================================================
        print("  [8] Mirror relationships...")

        # Mirror column pairs
        mirror_data = []
        for a in anomalies:
            mirror_data.extend([a['pos'][0], a['pos'][1], a['mirrorPos'][0], a['mirrorPos'][1]])
        candidates.append(('mirror_positions', hashlib.sha256(bytes(mirror_data)).digest(),
                          'All position + mirror position data'))

        # Sum of 200 at [22,22] (only matching value)
        candidates.append(('sum_200_seed', hashlib.sha256(bytes([200] * 32)).digest(),
                          'Sum 200 (22,22 special) as seed'))

        # ================================================================
        # METHOD 9: Connection to 1CFB/1CFI positions
        # ================================================================
        print("  [9] 1CFB/1CFI position encodings...")

        cfb_conn = self.anomaly_data['connectionTo1CFB']

        # 1cfi position [91, 20]
        cfi_pos = cfb_conn['1cfi']['position']
        candidates.append(('1cfi_position', hashlib.sha256(bytes(cfi_pos * 16)).digest(),
                          f'1cfi position {cfi_pos}'))

        # 1cfb position [45, 92]
        cfb_pos = cfb_conn['1cfb']['position']
        candidates.append(('1cfb_position', hashlib.sha256(bytes(cfb_pos * 16)).digest(),
                          f'1cfb position {cfb_pos}'))

        # Combined positions
        combined_pos = cfi_pos + cfb_pos
        candidates.append(('cfb_cfi_combined', hashlib.sha256(bytes(combined_pos * 8)).digest(),
                          'Combined CFI+CFB positions'))

        # Matrix values at those positions
        cfi_val = cfb_conn['1cfi']['matrixValue']  # -3
        cfb_val = cfb_conn['1cfb']['matrixValue']  # -118
        candidates.append(('cfb_cfi_values', hashlib.sha256(bytes([
            (cfi_val + 128) % 256,
            (cfb_val + 128) % 256
        ] * 16)).digest(), f'CFI value {cfi_val}, CFB value {cfb_val}'))

        # ================================================================
        # METHOD 10: Quadrant and distribution analysis
        # ================================================================
        print("  [10] Quadrant distribution...")

        quad = self.anomaly_data['quadrantDistribution']
        quad_data = bytes([quad['NW'], quad['NE'], quad['SW'], quad['SE']] * 8)
        candidates.append(('quadrant_dist', hashlib.sha256(quad_data).digest(),
                          f'Quadrant distribution NW:{quad["NW"]} NE:{quad["NE"]}'))

        # All in upper half
        candidates.append(('upper_half', hashlib.sha256(b'upper_half_only').digest(),
                          'Marker for upper half distribution'))

        # ================================================================
        # METHOD 11: Statistical signatures
        # ================================================================
        print("  [11] Statistical signatures...")

        stats = self.anomaly_data['statistics']
        stats_data = bytes([
            stats['totalCells'] % 256,
            (stats['totalCells'] >> 8) % 256,
            stats['symmetricCells'] % 256,
            (stats['symmetricCells'] >> 8) % 256,
            stats['anomalyCells'],
            stats['anomalyPairs'],
        ] * 5 + [68, 34])
        candidates.append(('statistics', hashlib.sha256(stats_data).digest(),
                          'Statistical signature of anomaly data'))

        # ================================================================
        # METHOD 12: Entropy-based derivations
        # ================================================================
        print("  [12] Entropy-based derivations...")

        # Use anomaly values as entropy source with different hash functions
        all_data = bytes([(a['value'] + 128) % 256 for a in anomalies])

        candidates.append(('sha3_256', hashlib.sha3_256(all_data).digest(),
                          'SHA3-256 of all anomaly values'))
        candidates.append(('blake2b', hashlib.blake2b(all_data, digest_size=32).digest(),
                          'BLAKE2b of all anomaly values'))
        candidates.append(('blake2s', hashlib.blake2s(all_data).digest(),
                          'BLAKE2s of all anomaly values'))

        # HMAC with 100 as key
        import hmac
        candidates.append(('hmac_100', hmac.new(bytes([100]), all_data, hashlib.sha256).digest(),
                          'HMAC-SHA256 with key=100'))

        # ================================================================
        # METHOD 13: Positional encodings
        # ================================================================
        print("  [13] Positional encodings...")

        # Row sequence from column 22 anomalies
        col22_rows = [a['pos'][0] for a in anomalies if a['pos'][1] == 22]  # [20-32]
        if len(col22_rows) >= 13:
            row_pattern = bytes(col22_rows + [0] * (32 - len(col22_rows)))
            candidates.append(('col22_rows', row_pattern, 'Column 22 row positions'))
            candidates.append(('col22_rows_sha256', hashlib.sha256(bytes(col22_rows)).digest(),
                              'Column 22 rows SHA256'))

        # Row sequence from column 97
        col97_rows = [a['pos'][0] for a in anomalies if a['pos'][1] == 97]
        if col97_rows:
            candidates.append(('col97_rows_sha256', hashlib.sha256(bytes(col97_rows)).digest(),
                              'Column 97 rows SHA256'))

        # ================================================================
        # METHOD 14: Binary pattern encoding
        # ================================================================
        print("  [14] Binary pattern encodings...")

        # Treat positive/negative as bits
        bits = []
        for a in anomalies:
            bits.append(1 if a['value'] >= 0 else 0)
        # Pack into bytes
        bit_bytes = []
        for i in range(0, len(bits), 8):
            byte_val = 0
            for j, b in enumerate(bits[i:i+8]):
                byte_val |= (b << (7 - j))
            bit_bytes.append(byte_val)
        if len(bit_bytes) >= 8:
            padded = bit_bytes + [0] * (32 - len(bit_bytes))
            candidates.append(('sign_bits', bytes(padded[:32]),
                              'Sign bits (pos=1, neg=0) packed'))

        # ================================================================
        # METHOD 15: Coordinate mathematics
        # ================================================================
        print("  [15] Coordinate mathematics...")

        # Sum of all row coordinates
        row_sum = sum(a['pos'][0] for a in anomalies)
        col_sum = sum(a['pos'][1] for a in anomalies)
        candidates.append(('coord_sums', hashlib.sha256(f"{row_sum}:{col_sum}".encode()).digest(),
                          f'Row sum {row_sum}, Col sum {col_sum}'))

        # Product of special position
        candidates.append(('22x22', hashlib.sha256(str(22 * 22).encode()).digest(),
                          '22 * 22 = 484'))

        # 127 (coordinate sum at special position)
        candidates.append(('coord_127', bytes([127] * 32),
                          'Coordinate sum 127 repeated'))

        # ================================================================
        # METHOD 16: 0x7b prefix targeting (1CFB addresses have hash160 starting with 7b)
        # ================================================================
        print("  [16] Targeting 0x7b hash160 prefix...")

        # 1CFB addresses have hash160 starting with 0x7b
        # Try seeds that might produce this
        for i in range(256):
            seed = bytes([0x7b, i] + [0x7b ^ i] * 30)
            candidates.append((f'7b_seed_{i}', seed,
                              f'0x7b targeting seed variant {i}'))

        # ================================================================
        # METHOD 17: Anomaly row sequences
        # ================================================================
        print("  [17] Anomaly row sequences...")

        # Extract all unique row numbers
        rows = sorted(set(a['pos'][0] for a in anomalies))
        if len(rows) >= 32:
            candidates.append(('unique_rows', bytes(rows[:32]),
                              'First 32 unique row numbers'))
        candidates.append(('all_rows_sha256', hashlib.sha256(bytes(rows)).digest(),
                          'SHA256 of all unique rows'))

        # Row differences (delta encoding)
        if len(rows) > 1:
            deltas = [rows[i+1] - rows[i] for i in range(len(rows)-1)]
            if len(deltas) < 32:
                deltas = deltas + [0] * (32 - len(deltas))
            candidates.append(('row_deltas', bytes(deltas[:32]),
                              'Row position differences'))

        # ================================================================
        # METHOD 18: Value gradients
        # ================================================================
        print("  [18] Value gradients...")

        values = [a['value'] for a in anomalies]
        if len(values) > 1:
            gradients = [abs(values[i+1] - values[i]) % 256 for i in range(len(values)-1)]
            if len(gradients) < 32:
                gradients = gradients + [0] * (32 - len(gradients))
            candidates.append(('value_gradients', bytes(gradients[:32]),
                              'Value gradient sequence'))

        # ================================================================
        # METHOD 19: Magic numbers from anomaly data
        # ================================================================
        print("  [19] Magic numbers...")

        magic_nums = [
            68,   # Total anomalies
            34,   # Anomaly pairs
            22,   # Special column
            97,   # Second key column
            100,  # Special value
            127,  # Coordinate sum at [22,22]
            27,   # Value XOR 127 at special position
            119,  # 22 + 97 = 22 XOR 97
            13,   # Col 22 count
            14,   # Col 97 count
            200,  # Sum at special position
            121,  # Qubic constant (abs)
        ]

        candidates.append(('magic_numbers', hashlib.sha256(bytes(magic_nums * 3)[:32]).digest(),
                          'SHA256 of magic numbers'))
        candidates.append(('magic_direct', bytes((magic_nums * 3)[:32]),
                          'Magic numbers direct'))

        # ================================================================
        # METHOD 20: Inverse and complement operations
        # ================================================================
        print("  [20] Inverse and complement operations...")

        all_vals = bytes([(a['value'] + 128) % 256 for a in anomalies])

        # Bitwise NOT
        inverted = bytes([~b & 0xFF for b in all_vals])
        candidates.append(('inverted_sha256', hashlib.sha256(inverted).digest(),
                          'SHA256 of bitwise NOT values'))

        # Reverse order
        reversed_vals = all_vals[::-1]
        candidates.append(('reversed_sha256', hashlib.sha256(reversed_vals).digest(),
                          'SHA256 of reversed values'))

        # Both
        inv_rev = inverted[::-1]
        candidates.append(('inv_rev_sha256', hashlib.sha256(inv_rev).digest(),
                          'SHA256 of inverted then reversed'))

        # ================================================================
        # METHOD 21: Column arithmetic progressions
        # ================================================================
        print("  [21] Column arithmetic progressions...")

        # 22 -> 97 progression
        col_prog = []
        for i in range(32):
            val = (22 + (i * (97 - 22) // 31)) % 256
            col_prog.append(val)
        candidates.append(('col_progression', bytes(col_prog),
                          '22 to 97 arithmetic progression'))

        # ================================================================
        # METHOD 22: Combined CFB/anomaly signatures
        # ================================================================
        print("  [22] Combined CFB/anomaly signatures...")

        cfb_conn = self.anomaly_data['connectionTo1CFB']

        # Combine 1CFI method (step27 + XOR13) with anomaly data
        step27_data = []
        for i, a in enumerate(anomalies):
            step27_data.append((a['value'] + 27 + i) % 256)
        candidates.append(('step27_anomaly', hashlib.sha256(bytes(step27_data)).digest(),
                          'Step27 applied to anomaly values'))

        # XOR13 variant
        xor13_data = []
        for a in anomalies:
            xor13_data.append(((a['value'] + 128) ^ 13) % 256)
        candidates.append(('xor13_anomaly', hashlib.sha256(bytes(xor13_data)).digest(),
                          'XOR13 applied to anomaly values'))

        # ================================================================
        # METHOD 23: Layer/depth encodings
        # ================================================================
        print("  [23] Layer/depth encodings...")

        # Use row as "layer" number
        layer_encoded = []
        for a in anomalies:
            layer = a['pos'][0]
            val = (a['value'] + 128) % 256
            layer_encoded.append((layer ^ val) % 256)
        if len(layer_encoded) >= 32:
            candidates.append(('layer_xor', bytes(layer_encoded[:32]),
                              'Layer (row) XOR value encoding'))

        # ================================================================
        # METHOD 24: Anomaly centroid
        # ================================================================
        print("  [24] Anomaly centroid calculations...")

        avg_row = sum(a['pos'][0] for a in anomalies) // len(anomalies)
        avg_col = sum(a['pos'][1] for a in anomalies) // len(anomalies)
        avg_val = sum((a['value'] + 128) % 256 for a in anomalies) // len(anomalies)

        centroid = bytes([avg_row, avg_col, avg_val] * 10 + [avg_row, avg_col])
        candidates.append(('centroid', centroid,
                          f'Centroid: row={avg_row}, col={avg_col}, val={avg_val}'))

        centroid_sha = hashlib.sha256(f"{avg_row}:{avg_col}:{avg_val}".encode()).digest()
        candidates.append(('centroid_sha256', centroid_sha,
                          'Centroid SHA256'))

        # ================================================================
        # METHOD 25: Anomaly spread/variance
        # ================================================================
        print("  [25] Anomaly spread/variance...")

        vals = [(a['value'] + 128) % 256 for a in anomalies]
        mean_val = sum(vals) // len(vals)
        variance = sum((v - mean_val) ** 2 for v in vals) // len(vals)

        var_seed = bytes([variance % 256, (variance >> 8) % 256] * 16)
        candidates.append(('variance_seed', var_seed,
                          f'Variance-based seed (var={variance})'))

        print()
        print(f"  Total candidates generated: {len(candidates)}")
        print("-" * 80)

        return candidates

    def test_candidates(self, candidates: List[Tuple[str, bytes, str]]):
        """Test all candidates and check for address matches"""
        print()
        print("Testing candidates against known addresses...")
        print("-" * 80)

        if not HAVE_ECDSA:
            print("ERROR: Cannot test without ecdsa library")
            return

        for method_name, key_bytes, description in candidates:
            self.results['methods_tested'] += 1

            # Ensure 32 bytes
            if len(key_bytes) < 32:
                key_bytes = key_bytes + bytes(32 - len(key_bytes))
            elif len(key_bytes) > 32:
                key_bytes = key_bytes[:32]

            result = private_key_to_address(key_bytes)
            if result is None:
                continue

            self.results['keys_generated'] += 1

            entry = {
                'method': method_name,
                'description': description,
                'key_hex': result['private_key_hex'],
                'address_uncompressed': result['address_uncompressed'],
                'address_compressed': result['address_compressed'],
                'hash160_u': result['hash160_uncompressed'],
                'hash160_c': result['hash160_compressed'],
                'wif_compressed': result['wif_compressed'],
            }

            # Check for exact matches
            for known_addr in KNOWN_ADDRESSES:
                if result['address_uncompressed'] == known_addr:
                    print(f"\n*** MATCH FOUND (uncompressed)! ***")
                    print(f"    Method: {method_name}")
                    print(f"    Address: {known_addr}")
                    print(f"    Key: {result['private_key_hex']}")
                    self.results['matches_found'].append({
                        **entry,
                        'match_type': 'uncompressed',
                        'matched_address': known_addr
                    })

                if result['address_compressed'] == known_addr:
                    print(f"\n*** MATCH FOUND (compressed)! ***")
                    print(f"    Method: {method_name}")
                    print(f"    Address: {known_addr}")
                    print(f"    Key: {result['private_key_hex']}")
                    self.results['matches_found'].append({
                        **entry,
                        'match_type': 'compressed',
                        'matched_address': known_addr
                    })

            # Check for near matches (prefix matches)
            for known_addr in KNOWN_ADDRESSES:
                if known_addr.startswith('1CFB'):
                    # Check if generated address also starts with 1CFB
                    if result['address_compressed'].startswith('1CFB'):
                        self.results['near_matches'].append({
                            'method': method_name,
                            'generated': result['address_compressed'],
                            'target': known_addr,
                            'match_length': 4,
                            'type': 'compressed'
                        })
                    if result['address_uncompressed'].startswith('1CFB'):
                        self.results['near_matches'].append({
                            'method': method_name,
                            'generated': result['address_uncompressed'],
                            'target': known_addr,
                            'match_length': 4,
                            'type': 'uncompressed'
                        })

            self.results['candidates'].append(entry)

            # Store in method results
            self.results['method_results'][method_name] = {
                'address_c': result['address_compressed'],
                'address_u': result['address_uncompressed'],
                'prefix_c': result['address_compressed'][:5],
                'prefix_u': result['address_uncompressed'][:5],
            }

        print()
        print(f"  Methods tested: {self.results['methods_tested']}")
        print(f"  Keys generated: {self.results['keys_generated']}")
        print(f"  Exact matches: {len(self.results['matches_found'])}")
        print(f"  Near matches (1CFB prefix): {len(self.results['near_matches'])}")

    def analyze_prefixes(self):
        """Analyze address prefixes to find patterns"""
        print()
        print("Analyzing address prefixes...")
        print("-" * 80)

        prefix_counts = {}
        for entry in self.results['candidates']:
            for addr_type in ['address_compressed', 'address_uncompressed']:
                addr = entry[addr_type]
                prefix = addr[:4]
                if prefix not in prefix_counts:
                    prefix_counts[prefix] = {'compressed': 0, 'uncompressed': 0}
                if 'compressed' in addr_type:
                    prefix_counts[prefix]['compressed'] += 1
                else:
                    prefix_counts[prefix]['uncompressed'] += 1

        # Sort by total count
        sorted_prefixes = sorted(prefix_counts.items(),
                                  key=lambda x: x[1]['compressed'] + x[1]['uncompressed'],
                                  reverse=True)

        print("  Top 10 prefixes:")
        for prefix, counts in sorted_prefixes[:10]:
            total = counts['compressed'] + counts['uncompressed']
            print(f"    {prefix}: {total} (c:{counts['compressed']}, u:{counts['uncompressed']})")

        self.results['prefix_analysis'] = dict(sorted_prefixes[:20])

        # Check for 1CFB specifically
        cfb_count = prefix_counts.get('1CFB', {'compressed': 0, 'uncompressed': 0})
        print()
        print(f"  1CFB prefix: {cfb_count['compressed'] + cfb_count['uncompressed']} addresses")
        if cfb_count['compressed'] + cfb_count['uncompressed'] > 0:
            print("  1CFB addresses found:")
            for entry in self.results['candidates']:
                if entry['address_compressed'].startswith('1CFB'):
                    print(f"    [{entry['method']}] {entry['address_compressed']}")
                if entry['address_uncompressed'].startswith('1CFB'):
                    print(f"    [{entry['method']}] {entry['address_uncompressed']}")

    def save_results(self):
        """Save results to JSON file"""
        output_file = SCRIPT_DIR / 'ANOMALY_BITCOIN_DERIVATION.json'

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print()
        print(f"Results saved to: {output_file}")

    def run(self):
        """Execute the full derivation process"""
        candidates = self.generate_key_candidates()
        self.test_candidates(candidates)
        self.analyze_prefixes()
        self.save_results()

        # Final summary
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"  Anomalies analyzed: {self.anomaly_data['statistics']['anomalyCells']}")
        print(f"  Methods tested: {self.results['methods_tested']}")
        print(f"  Keys generated: {self.results['keys_generated']}")
        print(f"  Exact matches: {len(self.results['matches_found'])}")
        print(f"  Near matches: {len(self.results['near_matches'])}")

        if self.results['matches_found']:
            print()
            print("*** MATCHES FOUND! ***")
            for match in self.results['matches_found']:
                print(f"  Method: {match['method']}")
                print(f"  Address: {match['matched_address']}")
                print(f"  Private Key: {match['key_hex']}")
                print(f"  WIF: {match['wif_compressed']}")
                print()

        print("=" * 80)


if __name__ == "__main__":
    derivation = AnomalyBitcoinDerivation()
    derivation.run()
