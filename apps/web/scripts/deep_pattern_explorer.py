#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DEEP PATTERN EXPLORER                                       ║
║                                                                                ║
║  Advanced pattern discovery in Anna Matrix                                     ║
║  - XOR chain traversal                                                         ║
║  - Binary message extraction                                                   ║
║  - Advanced key derivation                                                     ║
║  - Qubic seed testing                                                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import struct
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
from datetime import datetime
from collections import defaultdict
import itertools

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"
PATOSHI_FILE = DATA_DIR / "patoshi-addresses.json"

CFB_NUMBERS = [27, 37, 42, 127]
CFB_SET = set(CFB_NUMBERS + [-n for n in CFB_NUMBERS])

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
GENESIS_PUBKEY = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"
GENESIS_TIMESTAMP = 1231006505
BLOCK9_TIMESTAMP = 1231473279

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast queries"""
        self.value_to_coords = defaultdict(list)
        self.all_values = set()

        for row in range(128):
            for col in range(128):
                v = self.data[row][col]
                if isinstance(v, int):
                    self.value_to_coords[v].append((row, col))
                    self.all_values.add(v)

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

    def find_value(self, value: int) -> List[Tuple[int, int]]:
        return self.value_to_coords.get(value, [])

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int, int]]:
        """Get all 8 neighbors with their values"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (row + dr) % 128, (col + dc) % 128
                v = self.query(nr, nc)
                if v is not None:
                    neighbors.append((nr, nc, v))
        return neighbors

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

# ═══════════════════════════════════════════════════════════════════════════════
# DEEP EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════

class DeepPatternExplorer:
    def __init__(self):
        print("═" * 70)
        print("           DEEP PATTERN EXPLORER")
        print("═" * 70)
        self.matrix = Matrix()
        self.discoveries = []

    def log_discovery(self, category: str, title: str, data: dict):
        self.discoveries.append({
            'category': category,
            'title': title,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        print(f"\n  ★★★ [{category.upper()}] {title}")
        for k, v in list(data.items())[:5]:
            val_str = str(v)[:60] + "..." if len(str(v)) > 60 else str(v)
            print(f"      {k}: {val_str}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 1: XOR CHAIN TRAVERSAL
    # ───────────────────────────────────────────────────────────────────────────

    def explore_xor_chains(self):
        """Follow XOR chains starting from CFB numbers"""
        print("\n" + "═" * 70)
        print("PHASE 1: XOR CHAIN TRAVERSAL")
        print("═" * 70)

        # Start from cells containing 27
        start_cells = self.matrix.find_value(27) + self.matrix.find_value(-27)
        print(f"\n  Starting cells with ±27: {len(start_cells)}")

        all_chains = []

        for start_row, start_col in start_cells[:50]:  # Limit to first 50
            chain = self._follow_xor_chain(start_row, start_col, max_length=20)
            if len(chain) > 3:
                all_chains.append(chain)

        # Analyze chains
        print(f"\n  Chains found (length > 3): {len(all_chains)}")

        # Find chains that return to CFB
        cfb_ending_chains = []
        for chain in all_chains:
            last_value = chain[-1]['value']
            if last_value in CFB_SET:
                cfb_ending_chains.append(chain)

        print(f"  Chains ending at CFB number: {len(cfb_ending_chains)}")

        if cfb_ending_chains:
            for chain in cfb_ending_chains[:5]:
                values = [c['value'] for c in chain]
                coords = [(c['row'], c['col']) for c in chain]
                print(f"\n    Chain: {values}")
                print(f"    Coords: {coords}")

                # Check if chain values spell something
                ascii_attempt = ''.join(chr((v + 128) % 256) if 32 <= (v + 128) % 256 <= 126 else '?' for v in values)
                print(f"    ASCII attempt: {ascii_attempt}")

            self.log_discovery('xor_chain', f'{len(cfb_ending_chains)} chains return to CFB', {
                'total_chains': len(all_chains),
                'cfb_ending': len(cfb_ending_chains),
                'sample': cfb_ending_chains[0] if cfb_ending_chains else None
            })

        # Find XOR loops
        self._find_xor_loops()

    def _follow_xor_chain(self, start_row: int, start_col: int, max_length: int = 20) -> List[dict]:
        """Follow XOR chain by always XORing with neighbor to find next CFB-related cell"""
        chain = []
        visited = set()
        row, col = start_row, start_col

        while len(chain) < max_length:
            value = self.matrix.query(row, col)
            if value is None or (row, col) in visited:
                break

            chain.append({'row': row, 'col': col, 'value': value})
            visited.add((row, col))

            # Find neighbor that XORs to something interesting
            neighbors = self.matrix.get_neighbors(row, col)
            best_neighbor = None
            best_score = -1

            for nr, nc, nv in neighbors:
                if (nr, nc) in visited:
                    continue

                xor_result = value ^ nv
                score = 0
                if xor_result in CFB_SET:
                    score = 100
                elif abs(xor_result) < 50:
                    score = 50 - abs(xor_result)

                if score > best_score:
                    best_score = score
                    best_neighbor = (nr, nc)

            if best_neighbor is None:
                break

            row, col = best_neighbor

        return chain

    def _find_xor_loops(self):
        """Find XOR loops that return to starting value"""
        print("\n  Searching for XOR loops...")

        loops_found = []

        # Check all pairs of adjacent cells
        for row in range(128):
            for col in range(128):
                v1 = self.matrix.query(row, col)
                if v1 is None:
                    continue

                for nr, nc, v2 in self.matrix.get_neighbors(row, col):
                    xor1 = v1 ^ v2

                    # Find third cell that completes loop
                    for nnr, nnc, v3 in self.matrix.get_neighbors(nr, nc):
                        if (nnr, nnc) == (row, col):
                            continue

                        xor2 = v2 ^ v3

                        # Check if XORing back to v1 gives CFB
                        xor3 = v3 ^ v1
                        total_xor = xor1 ^ xor2 ^ xor3

                        if total_xor in CFB_NUMBERS:
                            loops_found.append({
                                'cells': [(row, col), (nr, nc), (nnr, nnc)],
                                'values': [v1, v2, v3],
                                'xors': [xor1, xor2, xor3],
                                'total': total_xor
                            })

        print(f"  XOR loops producing CFB: {len(loops_found)}")

        if loops_found:
            for loop in loops_found[:5]:
                print(f"    Loop: {loop['values']} → XORs: {loop['xors']} → Total: {loop['total']}")

            self.log_discovery('xor_loop', f'{len(loops_found)} triangular XOR loops', {
                'count': len(loops_found),
                'sample': loops_found[:3]
            })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 2: BINARY MESSAGE EXTRACTION
    # ───────────────────────────────────────────────────────────────────────────

    def extract_binary_messages(self):
        """Look for binary messages encoded in the matrix"""
        print("\n" + "═" * 70)
        print("PHASE 2: BINARY MESSAGE EXTRACTION")
        print("═" * 70)

        # Method 1: Treat values as bits (positive = 1, negative = 0)
        print("\n  Method 1: Sign as bit...")
        bit_rows = []
        for row in range(128):
            bits = []
            for col in range(128):
                v = self.matrix.query(row, col)
                if v is not None:
                    bits.append('1' if v >= 0 else '0')
            bit_rows.append(''.join(bits))

        # Try to decode as ASCII
        for row_idx, bit_string in enumerate(bit_rows[:20]):
            # Take 8 bits at a time
            chars = []
            for i in range(0, len(bit_string) - 7, 8):
                byte_val = int(bit_string[i:i+8], 2)
                if 32 <= byte_val <= 126:
                    chars.append(chr(byte_val))

            message = ''.join(chars)
            if len(message) > 3 and any(c.isalpha() for c in message):
                print(f"    Row {row_idx}: {message[:50]}")

        # Method 2: Mod 2 as bit
        print("\n  Method 2: Value mod 2 as bit...")
        for row in range(10):
            bits = []
            for col in range(128):
                v = self.matrix.query(row, col)
                if v is not None:
                    bits.append(str(abs(v) % 2))

            # Decode
            bit_string = ''.join(bits)
            chars = []
            for i in range(0, len(bit_string) - 7, 8):
                byte_val = int(bit_string[i:i+8], 2)
                if 32 <= byte_val <= 126:
                    chars.append(chr(byte_val))

            message = ''.join(chars)
            if len(message) > 3:
                print(f"    Row {row}: {message[:40]}")

        # Method 3: Look for "CFB" pattern in binary
        print("\n  Method 3: Searching for 'CFB' pattern...")
        cfb_binary = ''.join(format(ord(c), '08b') for c in 'CFB')  # 010000110100011001000010
        print(f"    'CFB' in binary: {cfb_binary}")

        # Search in row bits
        for row_idx, bit_string in enumerate(bit_rows):
            if cfb_binary in bit_string:
                pos = bit_string.index(cfb_binary)
                print(f"    ★ Found 'CFB' in row {row_idx} at position {pos}!")
                self.log_discovery('binary', f"'CFB' found in row {row_idx}", {
                    'row': row_idx,
                    'position': pos
                })

        # Method 4: Row 27 special analysis
        print("\n  Method 4: Row 27 binary analysis...")
        row27_values = [self.matrix.query(27, c) for c in range(128)]
        row27_binary = ''.join('1' if v and v >= 0 else '0' for v in row27_values)

        # Try to decode
        chars = []
        for i in range(0, len(row27_binary) - 7, 8):
            byte_val = int(row27_binary[i:i+8], 2)
            if 32 <= byte_val <= 126:
                chars.append(chr(byte_val))
            else:
                chars.append('.')

        print(f"    Row 27 decoded: {''.join(chars)}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 3: ADVANCED KEY DERIVATION
    # ───────────────────────────────────────────────────────────────────────────

    def advanced_key_derivation(self):
        """Try advanced methods to derive private keys"""
        print("\n" + "═" * 70)
        print("PHASE 3: ADVANCED KEY DERIVATION")
        print("═" * 70)

        genesis_h160 = base58_decode(GENESIS_ADDRESS)[1:21]
        cfb_h160 = base58_decode(CFB_ADDRESS)[1:21]

        candidates = []

        # Method 1: Matrix values at CFB cells as key
        print("\n  Method 1: CFB cell values as key bytes...")
        cfb_cells = []
        for cfb in [27, 37, 42, 127]:
            cfb_cells.extend(self.matrix.find_value(cfb))
            cfb_cells.extend(self.matrix.find_value(-cfb))

        if len(cfb_cells) >= 32:
            key_bytes = bytes((self.matrix.query(r, c) + 128) % 256 for r, c in cfb_cells[:32])
            candidates.append(('cfb_cells', key_bytes))
            print(f"    Key from CFB cells: {key_bytes.hex()[:32]}...")

        # Method 2: Genesis h160 XOR with matrix-derived values
        print("\n  Method 2: Genesis XOR matrix pattern...")
        matrix_pattern = bytes(
            (self.matrix.query(i, i) + 128) % 256 if self.matrix.query(i, i) else 0
            for i in range(20)
        )
        xored = bytes(a ^ b for a, b in zip(genesis_h160, matrix_pattern))
        extended = hashlib.sha256(xored).digest()
        candidates.append(('genesis_xor_diag', extended))
        print(f"    Key: {extended.hex()[:32]}...")

        # Method 3: Block 9 timestamp + Genesis
        print("\n  Method 3: Timestamp combination...")
        ts_bytes = struct.pack('>I', BLOCK9_TIMESTAMP)
        combined = genesis_h160 + ts_bytes + bytes([27, 37, 42, 127])
        key3 = hashlib.sha256(combined).digest()
        candidates.append(('timestamp_combo', key3))
        print(f"    Key: {key3.hex()[:32]}...")

        # Method 4: XOR chain from (0,2) = -27
        print("\n  Method 4: XOR chain from Genesis-27 cell...")
        chain = self._follow_xor_chain(0, 2, max_length=32)
        if len(chain) >= 16:
            chain_bytes = bytes((c['value'] + 128) % 256 for c in chain[:32])
            if len(chain_bytes) < 32:
                chain_bytes = chain_bytes.ljust(32, b'\x00')
            candidates.append(('xor_chain_genesis', chain_bytes))
            print(f"    Key: {chain_bytes.hex()[:32]}...")

        # Method 5: Vision center neighbors expanded
        print("\n  Method 5: Vision center spiral...")
        spiral_values = []
        for radius in range(16):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    if abs(dr) == radius or abs(dc) == radius:
                        v = self.matrix.query(64 + dr, 64 + dc)
                        if v is not None:
                            spiral_values.append((v + 128) % 256)
                        if len(spiral_values) >= 32:
                            break
                if len(spiral_values) >= 32:
                    break
            if len(spiral_values) >= 32:
                break

        if len(spiral_values) >= 32:
            key5 = bytes(spiral_values[:32])
            candidates.append(('vision_spiral', key5))
            print(f"    Key: {key5.hex()[:32]}...")

        # Method 6: Row 27 values
        print("\n  Method 6: Row 27 as seed...")
        row27 = [self.matrix.query(27, c) for c in range(32)]
        row27_bytes = bytes((v + 128) % 256 if v else 0 for v in row27)
        candidates.append(('row_27', row27_bytes))
        print(f"    Key: {row27_bytes.hex()[:32]}...")

        # Method 7: All -27 cells coordinates
        print("\n  Method 7: -27 cell coordinates...")
        minus27_cells = self.matrix.find_value(-27)
        if len(minus27_cells) >= 16:
            coords_bytes = bytes(
                [r for r, c in minus27_cells[:16]] +
                [c for r, c in minus27_cells[:16]]
            )
            candidates.append(('-27_coords', coords_bytes))
            print(f"    Key: {coords_bytes.hex()[:32]}...")

        # Save candidates for potential testing
        print(f"\n  Total key candidates: {len(candidates)}")
        return candidates

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 4: TIMESTAMP FREQUENCY ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def timestamp_frequency_analysis(self):
        """Deep analysis of timestamp patterns"""
        print("\n" + "═" * 70)
        print("PHASE 4: TIMESTAMP FREQUENCY ANALYSIS")
        print("═" * 70)

        # Analyze Genesis and Block 9 timestamps
        timestamps = [
            ('Genesis', GENESIS_TIMESTAMP),
            ('Block 9', BLOCK9_TIMESTAMP),
        ]

        for name, ts in timestamps:
            print(f"\n  {name} Timestamp: {ts}")

            # Various encodings
            encodings = {
                'mod_128': (ts % 128, (ts // 128) % 128),
                'shift_7': ((ts >> 7) % 128, ts % 128),
                'bytes': (ts >> 24, (ts >> 16) & 0xFF),
                'xor_bytes': ((ts >> 24) ^ (ts & 0xFF), ((ts >> 16) & 0xFF) ^ ((ts >> 8) & 0xFF)),
            }

            for method, (row, col) in encodings.items():
                row, col = row % 128, col % 128
                value = self.matrix.query(row, col)
                is_cfb = value in CFB_SET if value else False
                marker = " ★ CFB!" if is_cfb else ""
                print(f"    {method}: [{row},{col}] = {value}{marker}")

        # Find all timestamps that would produce 27
        print("\n  Searching for timestamps producing 27...")

        # For ts_shift encoding: (ts >> 7) % 128 = 20, ts % 128 = 127
        # Gives [20, 127] = 27
        # So ts % 128 = 127 and (ts >> 7) % 128 = 20
        # ts = 128k + 127 and ts >> 7 = 128m + 20
        # ts = 16384m + 2560 + 127 = 16384m + 2687

        matching_timestamps = []
        for m in range(100):
            ts = 16384 * m + 2687
            if ts > 1230000000 and ts < 1240000000:  # Bitcoin era
                matching_timestamps.append(ts)

        print(f"    Timestamps in Bitcoin era producing 27: {len(matching_timestamps)}")
        for ts in matching_timestamps[:5]:
            from datetime import datetime as dt
            date = dt.fromtimestamp(ts)
            print(f"      {ts} = {date.isoformat()}")

        # Check which known timestamps produce CFB
        print("\n  Known timestamps analysis:")
        known_blocks = [
            (0, 1231006505, "Genesis"),
            (1, 1231469665, "Block 1"),
            (9, 1231473279, "Block 9 - First TX"),
            (27, 1231480988, "Block 27"),
            (37, 1231483940, "Block 37"),
            (42, 1231485598, "Block 42"),
            (127, 1231536800, "Block 127"),
            (170, 1231560220, "Block 170 - First TX"),
        ]

        for height, ts, name in known_blocks:
            row, col = (ts >> 7) % 128, ts % 128
            value = self.matrix.query(row, col)
            is_cfb = value in CFB_SET if value else False
            marker = " ★ CFB!" if is_cfb else ""
            print(f"    {name}: [{row},{col}] = {value}{marker}")

            if is_cfb:
                self.log_discovery('timestamp', f'{name} produces CFB value', {
                    'block': height,
                    'timestamp': ts,
                    'coords': (row, col),
                    'value': value
                })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 5: VALUE RELATIONSHIP NETWORK
    # ───────────────────────────────────────────────────────────────────────────

    def map_value_relationships(self):
        """Map relationships between matrix values"""
        print("\n" + "═" * 70)
        print("PHASE 5: VALUE RELATIONSHIP NETWORK")
        print("═" * 70)

        # Find all value pairs that produce CFB via different operations
        print("\n  Finding value relationships...")

        relationships = {
            'xor_27': [],
            'xor_37': [],
            'xor_42': [],
            'xor_127': [],
            'sum_27': [],
            'diff_27': [],
            'prod_mod_27': [],
        }

        all_values = sorted(self.matrix.all_values)

        for v1 in all_values:
            for v2 in all_values:
                if v1 >= v2:
                    continue

                if v1 ^ v2 == 27:
                    relationships['xor_27'].append((v1, v2))
                if v1 ^ v2 == 37:
                    relationships['xor_37'].append((v1, v2))
                if v1 ^ v2 == 42:
                    relationships['xor_42'].append((v1, v2))
                if v1 ^ v2 == 127:
                    relationships['xor_127'].append((v1, v2))
                if v1 + v2 == 27:
                    relationships['sum_27'].append((v1, v2))
                if abs(v1 - v2) == 27:
                    relationships['diff_27'].append((v1, v2))
                if (v1 * v2) % 127 == 27:
                    relationships['prod_mod_27'].append((v1, v2))

        for rel_type, pairs in relationships.items():
            print(f"    {rel_type}: {len(pairs)} pairs")
            if pairs and len(pairs) < 10:
                print(f"      Pairs: {pairs}")

        # Find the most "connected" values
        print("\n  Most connected values (appear in multiple relationships):")
        value_connections = defaultdict(int)
        for pairs in relationships.values():
            for v1, v2 in pairs:
                value_connections[v1] += 1
                value_connections[v2] += 1

        top_connected = sorted(value_connections.items(), key=lambda x: -x[1])[:15]
        for val, count in top_connected:
            is_cfb = val in CFB_SET
            marker = " ★ CFB" if is_cfb else ""
            print(f"      {val:+4d}: {count} connections{marker}")

        # Check if -27 and +26 relationship is special
        print("\n  Special relationship: -27 and +26...")
        minus27_coords = set(self.matrix.find_value(-27))
        plus26_coords = set(self.matrix.find_value(26))

        adjacent_pairs = 0
        for r1, c1 in minus27_coords:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    if ((r1 + dr) % 128, (c1 + dc) % 128) in plus26_coords:
                        adjacent_pairs += 1

        print(f"    Adjacent (-27, +26) pairs: {adjacent_pairs}")
        print(f"    -27 XOR 26 = {-27 ^ 26}")
        print(f"    -27 + 26 = {-27 + 26}")

        if adjacent_pairs > 10:
            self.log_discovery('relationship', f'{adjacent_pairs} adjacent (-27,+26) pairs', {
                'count': adjacent_pairs,
                'xor': -27 ^ 26,
                'sum': -27 + 26
            })

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self):
        """Execute all explorations"""
        self.explore_xor_chains()
        self.extract_binary_messages()
        key_candidates = self.advanced_key_derivation()
        self.timestamp_frequency_analysis()
        self.map_value_relationships()

        # Summary
        print("\n" + "═" * 70)
        print("           EXPLORATION COMPLETE")
        print("═" * 70)

        print(f"\n  Total discoveries: {len(self.discoveries)}")
        print(f"  Key candidates generated: {len(key_candidates)}")

        if self.discoveries:
            print("\n  DISCOVERIES:")
            for d in self.discoveries:
                print(f"    ★ [{d['category']}] {d['title']}")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'discoveries': self.discoveries,
            'key_candidates': [(name, key.hex()) for name, key in key_candidates]
        }

        output_file = SCRIPT_DIR / 'deep_pattern_results.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

        return key_candidates

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    explorer = DeepPatternExplorer()
    explorer.run_all()
