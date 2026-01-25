#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ULTIMATE DEEP RESEARCH                                      ║
║                                                                                ║
║  Maximum depth investigation of Satoshi/CFB connection                         ║
║  - Blockchain API integration                                                  ║
║  - Complete pattern verification                                               ║
║  - Exhaustive correlation analysis                                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import requests
import time
import struct
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict
import sys

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"
PATOSHI_FILE = DATA_DIR / "patoshi-addresses.json"
RESULTS_DIR = SCRIPT_DIR / "ultimate_research_results"
RESULTS_DIR.mkdir(exist_ok=True)

# APIs
MEMPOOL_API = "https://mempool.space/api"
BLOCKSTREAM_API = "https://blockstream.info/api"

# Rate limiting
API_DELAY = 0.5  # seconds between requests

# CFB Numbers
CFB_NUMBERS = [27, 37, 42, 127]
CFB_NUMBERS_EXTENDED = [27, 37, 42, 127, 576, 21, 33]

# Special addresses
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
GENESIS_PUBKEY = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"
BLOCK1_ADDRESS = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

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

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']
        self.stats = self._compute_stats()

    def _compute_stats(self):
        values = []
        for row in self.data:
            for v in row:
                if isinstance(v, int):
                    values.append(v)
        return {
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values),
            'count': len(values)
        }

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

def is_cfb(value: Optional[int]) -> bool:
    if value is None:
        return False
    return value in CFB_NUMBERS or -value in CFB_NUMBERS

# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKCHAIN API CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class BlockchainAPI:
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}

    def _get(self, url: str) -> Optional[Any]:
        if url in self.cache:
            return self.cache[url]

        try:
            time.sleep(API_DELAY)
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.cache[url] = data
                return data
            elif response.status_code == 429:
                print("  ⚠ Rate limited, waiting...")
                time.sleep(10)
                return self._get(url)
            else:
                return None
        except Exception as e:
            print(f"  ✗ API Error: {e}")
            return None

    def get_block(self, height: int) -> Optional[Dict]:
        """Get block data by height"""
        # First get block hash
        hash_data = self._get(f"{MEMPOOL_API}/block-height/{height}")
        if not hash_data:
            return None

        block_hash = hash_data if isinstance(hash_data, str) else None
        if not block_hash:
            return None

        # Then get block details
        return self._get(f"{MEMPOOL_API}/block/{block_hash}")

    def get_block_txs(self, block_hash: str) -> Optional[List]:
        """Get transactions in a block"""
        return self._get(f"{MEMPOOL_API}/block/{block_hash}/txs")

    def get_address(self, address: str) -> Optional[Dict]:
        """Get address info"""
        return self._get(f"{MEMPOOL_API}/address/{address}")

    def get_address_txs(self, address: str) -> Optional[List]:
        """Get address transactions"""
        return self._get(f"{MEMPOOL_API}/address/{address}/txs")

# ═══════════════════════════════════════════════════════════════════════════════
# DEEP RESEARCHER
# ═══════════════════════════════════════════════════════════════════════════════

class DeepResearcher:
    def __init__(self):
        print("═" * 70)
        print("           ULTIMATE DEEP RESEARCH")
        print("           Satoshi/CFB Connection Investigation")
        print("═" * 70)

        self.matrix = Matrix()
        self.api = BlockchainAPI()
        self.discoveries = []
        self.verified = []
        self.patterns = defaultdict(list)

        # Load Patoshi data
        with open(PATOSHI_FILE, 'r') as f:
            patoshi_data = json.load(f)
        self.patoshi_records = patoshi_data.get('records', [])
        print(f"✓ Loaded {len(self.patoshi_records)} Patoshi records")
        print(f"✓ Matrix stats: {self.matrix.stats}")

    def log_discovery(self, category: str, title: str, data: dict, verified: bool = False):
        discovery = {
            'category': category,
            'title': title,
            'data': data,
            'verified': verified,
            'timestamp': datetime.now().isoformat()
        }
        self.discoveries.append(discovery)
        if verified:
            self.verified.append(discovery)
        marker = "✓ VERIFIED" if verified else "★ DISCOVERY"
        print(f"\n  {marker}: [{category}] {title}")
        for k, v in list(data.items())[:5]:
            print(f"      {k}: {v}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 1: VERIFY ALL PREVIOUS FINDINGS
    # ───────────────────────────────────────────────────────────────────────────

    def verify_previous_findings(self):
        """Verify all discoveries from previous research"""
        print("\n" + "═" * 70)
        print("PHASE 1: VERIFYING PREVIOUS FINDINGS")
        print("═" * 70)

        # 1. Verify Patoshi -27 over-representation
        print("\n[1] Verifying Patoshi -27 over-representation...")
        value_counts = defaultdict(int)
        total = 0

        for record in self.patoshi_records:
            pubkey = record.get('pubkey', '')
            if not pubkey:
                continue

            h = hashlib.sha256(pubkey.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            value = self.matrix.query(row, col)

            if value is not None:
                value_counts[value] += 1
                total += 1

        expected = total / 256
        minus27_count = value_counts.get(-27, 0)
        ratio = minus27_count / expected if expected > 0 else 0

        self.log_discovery('patoshi', f'-27 appears {ratio:.2f}x expected', {
            'count': minus27_count,
            'expected': round(expected, 1),
            'ratio': round(ratio, 2),
            'total_samples': total
        }, verified=(ratio > 5))

        # 2. Verify Genesis address position 2 -> -27
        print("\n[2] Verifying Genesis address position 2 -> -27...")
        positions = [BASE58_ALPHABET.index(c) for c in GENESIS_ADDRESS]
        pos2 = positions[2]  # Position 2
        row, col = pos2 % 128, 2 % 128
        value = self.matrix.query(row, col)

        self.log_discovery('genesis', f'Position 2 -> {value}', {
            'address': GENESIS_ADDRESS,
            'position': 2,
            'base58_value': pos2,
            'matrix_coords': (row, col),
            'matrix_value': value
        }, verified=(value == -27))

        # 3. Verify 1CFB XOR = 27
        print("\n[3] Verifying 1CFB hash160 XOR = 27...")
        cfb_h160 = base58_decode(CFB_ADDRESS)[1:21]
        xor_all = 0
        for b in cfb_h160:
            xor_all ^= b

        self.log_discovery('cfb', f'1CFB XOR all bytes = {xor_all}', {
            'address': CFB_ADDRESS,
            'hash160': cfb_h160.hex(),
            'xor_result': xor_all
        }, verified=(xor_all == 27))

        # 4. Verify Vision Center neighbors = 27
        print("\n[4] Verifying Vision Center neighbors sum = 27...")
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nv = self.matrix.query(64 + dr, 64 + dc)
                if nv is not None:
                    neighbors.append(nv)
        neighbor_sum = sum(neighbors)

        self.log_discovery('matrix', f'Vision Center neighbors sum = {neighbor_sum}', {
            'center_coords': (64, 64),
            'center_value': self.matrix.query(64, 64),
            'neighbors': neighbors,
            'sum': neighbor_sum
        }, verified=(neighbor_sum == 27))

        # 5. Verify Block 9 timestamp -> 27
        print("\n[5] Verifying Block 9 timestamp -> 27...")
        block9_ts = 1231473279
        row = (block9_ts >> 7) % 128
        col = block9_ts % 128
        value = self.matrix.query(row, col)

        self.log_discovery('timestamp', f'Block 9 timestamp -> {value}', {
            'timestamp': block9_ts,
            'encoding': 'shift',
            'coords': (row, col),
            'value': value
        }, verified=(value == 27))

        # 6. Verify "IOTA" -> -27
        print("\n[6] Verifying 'IOTA' hash -> -27...")
        h = hashlib.sha256("IOTA".encode()).digest()
        row, col = h[0] % 128, h[1] % 128
        value = self.matrix.query(row, col)

        self.log_discovery('string', f'"IOTA" -> {value}', {
            'string': 'IOTA',
            'coords': (row, col),
            'value': value
        }, verified=(value == -27))

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 2: BLOCKCHAIN DEEP DIVE
    # ───────────────────────────────────────────────────────────────────────────

    def blockchain_deep_dive(self):
        """Fetch and analyze real blockchain data"""
        print("\n" + "═" * 70)
        print("PHASE 2: BLOCKCHAIN DEEP DIVE")
        print("═" * 70)

        # Analyze first 100 blocks
        print("\n[1] Analyzing first 100 blocks...")
        block_results = []
        cfb_blocks = []

        for height in range(100):
            print(f"\r  Fetching block {height}...", end="", flush=True)

            block = self.api.get_block(height)
            if not block:
                continue

            timestamp = block.get('timestamp', 0)

            # Test all encoding methods
            encodings = {
                'ts_mod': ((timestamp // 128) % 128, timestamp % 128),
                'ts_shift': ((timestamp >> 7) % 128, timestamp % 128),
                'height': (height % 128, (height // 128) % 128),
            }

            for method, (row, col) in encodings.items():
                value = self.matrix.query(row, col)
                result = {
                    'block': height,
                    'timestamp': timestamp,
                    'method': method,
                    'coords': (row, col),
                    'value': value
                }
                block_results.append(result)

                if is_cfb(value):
                    cfb_blocks.append(result)

        print(f"\n  Analyzed 100 blocks, {len(cfb_blocks)} hit CFB numbers")

        if cfb_blocks:
            print("\n  CFB-hitting blocks:")
            for r in cfb_blocks[:20]:
                print(f"    Block {r['block']}: {r['method']} -> [{r['coords'][0]},{r['coords'][1]}] = {r['value']}")

        # Save results
        self.patterns['block_analysis'] = block_results
        self.patterns['cfb_blocks'] = cfb_blocks

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 3: PATOSHI FORENSICS
    # ───────────────────────────────────────────────────────────────────────────

    def patoshi_forensics(self):
        """Deep analysis of Patoshi mining patterns"""
        print("\n" + "═" * 70)
        print("PHASE 3: PATOSHI FORENSICS")
        print("═" * 70)

        # Analyze block distribution of CFB-hitting pubkeys
        print("\n[1] Analyzing CFB-hitting pubkeys by block...")
        cfb_by_block = defaultdict(list)
        all_values = defaultdict(int)

        for record in self.patoshi_records:
            pubkey = record.get('pubkey', '')
            block = record.get('blockHeight', 0)

            if not pubkey:
                continue

            h = hashlib.sha256(pubkey.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            value = self.matrix.query(row, col)

            if value is not None:
                all_values[value] += 1
                if is_cfb(value):
                    cfb_by_block[block].append((pubkey[:20], value))

        print(f"  Blocks with CFB-hitting pubkeys: {len(cfb_by_block)}")

        # Find patterns in block numbers
        cfb_block_numbers = sorted(cfb_by_block.keys())
        if cfb_block_numbers:
            print(f"  First 20 CFB blocks: {cfb_block_numbers[:20]}")

            # Check differences
            diffs = [cfb_block_numbers[i+1] - cfb_block_numbers[i]
                     for i in range(min(50, len(cfb_block_numbers)-1))]

            cfb_diffs = [d for d in diffs if d in CFB_NUMBERS_EXTENDED]
            if cfb_diffs:
                self.log_discovery('patoshi', f'Block differences contain CFB numbers', {
                    'cfb_differences': cfb_diffs,
                    'sample_diffs': diffs[:20]
                })

        # Value distribution analysis
        print("\n[2] Value distribution analysis...")
        sorted_values = sorted(all_values.items(), key=lambda x: -x[1])[:20]
        total = sum(v for _, v in all_values.items())
        expected = total / 256

        print(f"  Total: {total}, Expected per value: {expected:.1f}")
        print("  Top 20 values:")
        for val, count in sorted_values:
            ratio = count / expected
            cfb_marker = " ★★★ CFB" if is_cfb(val) else ""
            print(f"    {val:+4d}: {count:5d} ({ratio:.2f}x){cfb_marker}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 4: XOR NETWORK MAPPING
    # ───────────────────────────────────────────────────────────────────────────

    def map_xor_network(self):
        """Map the complete XOR relationship network"""
        print("\n" + "═" * 70)
        print("PHASE 4: XOR NETWORK MAPPING")
        print("═" * 70)

        # Find all value pairs that XOR to CFB numbers
        print("\n[1] Finding XOR pairs...")
        all_values = set()
        for row in range(128):
            for col in range(128):
                v = self.matrix.query(row, col)
                if v is not None:
                    all_values.add(v)

        xor_pairs = defaultdict(list)
        for target in CFB_NUMBERS:
            for v1 in all_values:
                v2_needed = v1 ^ target
                if v2_needed in all_values:
                    xor_pairs[target].append((v1, v2_needed))

        for target in CFB_NUMBERS:
            print(f"\n  Pairs XORing to {target}: {len(xor_pairs[target])}")
            for v1, v2 in xor_pairs[target][:5]:
                print(f"    {v1:+4d} XOR {v2:+4d} = {target}")

        # Find coordinate pairs
        print("\n[2] Finding coordinate XOR patterns...")
        coord_xors = []
        for r1 in range(128):
            for c1 in range(128):
                v1 = self.matrix.query(r1, c1)
                if v1 is None:
                    continue

                # Check adjacent cells
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    r2, c2 = (r1 + dr) % 128, (c1 + dc) % 128
                    v2 = self.matrix.query(r2, c2)
                    if v2 is None:
                        continue

                    xor = v1 ^ v2
                    if xor in CFB_NUMBERS:
                        coord_xors.append({
                            'coord1': (r1, c1),
                            'coord2': (r2, c2),
                            'v1': v1,
                            'v2': v2,
                            'xor': xor
                        })

        print(f"  Adjacent pairs XORing to CFB: {len(coord_xors)}")
        for p in coord_xors[:10]:
            print(f"    [{p['coord1'][0]},{p['coord1'][1]}]={p['v1']} XOR [{p['coord2'][0]},{p['coord2'][1]}]={p['v2']} = {p['xor']}")

        self.patterns['xor_network'] = {
            'pairs': dict(xor_pairs),
            'coord_xors': coord_xors[:100]
        }

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 5: MESSAGE DECODING
    # ───────────────────────────────────────────────────────────────────────────

    def decode_hidden_messages(self):
        """Search for hidden messages in patterns"""
        print("\n" + "═" * 70)
        print("PHASE 5: MESSAGE DECODING")
        print("═" * 70)

        # 1. Genesis pubkey analysis
        print("\n[1] Analyzing Genesis pubkey...")
        genesis_pubkey_bytes = bytes.fromhex(GENESIS_PUBKEY)
        print(f"  Genesis pubkey length: {len(genesis_pubkey_bytes)} bytes")

        # Map each byte to matrix
        pubkey_values = []
        for i, byte in enumerate(genesis_pubkey_bytes):
            row = byte % 128
            col = (i * 7) % 128  # Prime offset
            value = self.matrix.query(row, col)
            pubkey_values.append(value)

        # Check for ASCII patterns
        ascii_chars = []
        for v in pubkey_values:
            if v is not None and 32 <= (v + 128) % 256 <= 126:
                ascii_chars.append(chr((v + 128) % 256))

        if ascii_chars:
            message = ''.join(ascii_chars[:50])
            print(f"  Potential ASCII from pubkey: {message}")

        # 2. Path analysis between known coordinates
        print("\n[2] Analyzing paths between strategic coordinates...")
        strategic = {
            'core': (6, 33),
            'genesis_entry': (45, 92),
            'bridge_exit': (82, 39),
            'memory': (21, 21),
            'vision': (64, 64),
        }

        for name1, coord1 in strategic.items():
            for name2, coord2 in strategic.items():
                if name1 >= name2:
                    continue

                # Get values along path
                path_values = []
                r1, c1 = coord1
                r2, c2 = coord2
                steps = max(abs(r2-r1), abs(c2-c1))

                if steps == 0:
                    continue

                for i in range(steps + 1):
                    r = r1 + (r2-r1) * i // steps
                    c = c1 + (c2-c1) * i // steps
                    v = self.matrix.query(r, c)
                    if v is not None:
                        path_values.append(v)

                if path_values:
                    path_sum = sum(path_values)
                    path_xor = path_values[0]
                    for v in path_values[1:]:
                        path_xor ^= v

                    if path_sum in CFB_NUMBERS or path_xor in CFB_NUMBERS:
                        self.log_discovery('path', f'{name1} -> {name2} encodes CFB', {
                            'from': name1,
                            'to': name2,
                            'sum': path_sum,
                            'xor': path_xor
                        })

        # 3. Check for "CFB" or "27" in various encodings
        print("\n[3] Searching for signature patterns...")

        # Row 27
        row27 = [self.matrix.query(27, c) for c in range(128)]
        row27_valid = [v for v in row27 if v is not None]
        print(f"  Row 27 sum: {sum(row27_valid)}")

        # Column 27
        col27 = [self.matrix.query(r, 27) for r in range(128)]
        col27_valid = [v for v in col27 if v is not None]
        print(f"  Col 27 sum: {sum(col27_valid)}")

        # Diagonal through (27, 27)
        diag27 = [self.matrix.query(i, i) for i in range(128)]
        diag27_valid = [v for v in diag27 if v is not None]
        print(f"  Main diagonal sum: {sum(diag27_valid)}")
        print(f"  Value at (27,27): {self.matrix.query(27, 27)}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 6: EXHAUSTIVE ENCODING TESTS
    # ───────────────────────────────────────────────────────────────────────────

    def exhaustive_encoding_tests(self):
        """Test all possible encoding methods"""
        print("\n" + "═" * 70)
        print("PHASE 6: EXHAUSTIVE ENCODING TESTS")
        print("═" * 70)

        test_inputs = [
            # Addresses
            GENESIS_ADDRESS,
            CFB_ADDRESS,
            BLOCK1_ADDRESS,

            # Pubkeys
            GENESIS_PUBKEY,

            # Strings
            "Satoshi Nakamoto",
            "Come-from-Beyond",
            "CFB",
            "Bitcoin",
            "Qubic",
            "IOTA",

            # Numbers
            "27",
            "1231006505",  # Genesis timestamp
            "1231473279",  # Block 9 timestamp

            # Phrases
            "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks",
        ]

        encodings = {
            'sha256': lambda x: hashlib.sha256(x.encode() if isinstance(x, str) else x).digest()[:2],
            'double_sha256': lambda x: hashlib.sha256(hashlib.sha256(x.encode() if isinstance(x, str) else x).digest()).digest()[:2],
            'md5': lambda x: hashlib.md5(x.encode() if isinstance(x, str) else x).digest()[:2],
            'ascii_sum': lambda x: bytes([(sum(ord(c) for c in x) % 128), ((sum(ord(c) for c in x) // 128) % 128)]) if isinstance(x, str) else b'\x00\x00',
        }

        print("\n  Testing all encodings...")
        cfb_hits = []

        for inp in test_inputs:
            for method, func in encodings.items():
                try:
                    result = func(inp)
                    row, col = result[0] % 128, result[1] % 128
                    value = self.matrix.query(row, col)

                    if is_cfb(value):
                        cfb_hits.append({
                            'input': inp[:30] if len(inp) > 30 else inp,
                            'method': method,
                            'coords': (row, col),
                            'value': value
                        })
                except Exception:
                    pass

        print(f"\n  CFB hits: {len(cfb_hits)}")
        for hit in cfb_hits:
            print(f"    {hit['input'][:20]}... ({hit['method']}) -> {hit['value']}")
            self.log_discovery('encoding', f"{hit['input'][:20]} -> {hit['value']}", hit)

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 7: BUILD COMPLETE CFB MAP
    # ───────────────────────────────────────────────────────────────────────────

    def build_cfb_map(self):
        """Build complete map of CFB number occurrences"""
        print("\n" + "═" * 70)
        print("PHASE 7: COMPLETE CFB MAP")
        print("═" * 70)

        cfb_map = {}
        for target in CFB_NUMBERS:
            coords_pos = self.matrix.find_value(target)
            coords_neg = self.matrix.find_value(-target)

            cfb_map[target] = {
                'positive_count': len(coords_pos),
                'negative_count': len(coords_neg),
                'positive_coords': coords_pos[:20],
                'negative_coords': coords_neg[:20],
            }

            print(f"\n  Value {target}:")
            print(f"    Positive (+{target}): {len(coords_pos)} cells")
            print(f"    Negative (-{target}): {len(coords_neg)} cells")

            # Check for patterns in coordinates
            if coords_pos:
                rows = [c[0] for c in coords_pos]
                cols = [c[1] for c in coords_pos]
                print(f"    Row range: {min(rows)}-{max(rows)}")
                print(f"    Col range: {min(cols)}-{max(cols)}")

        self.patterns['cfb_map'] = cfb_map

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL PHASES
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self):
        """Execute complete research"""
        start_time = time.time()

        try:
            self.verify_previous_findings()
            self.blockchain_deep_dive()
            self.patoshi_forensics()
            self.map_xor_network()
            self.decode_hidden_messages()
            self.exhaustive_encoding_tests()
            self.build_cfb_map()
        except KeyboardInterrupt:
            print("\n  ⚠ Interrupted by user")

        # Final Report
        duration = time.time() - start_time
        print("\n" + "═" * 70)
        print("           RESEARCH COMPLETE")
        print("═" * 70)

        print(f"\n  Duration: {duration:.1f} seconds")
        print(f"  Total discoveries: {len(self.discoveries)}")
        print(f"  Verified findings: {len(self.verified)}")

        if self.verified:
            print("\n  VERIFIED FINDINGS:")
            for v in self.verified:
                print(f"    ✓ [{v['category']}] {v['title']}")

        if self.discoveries:
            print(f"\n  ALL DISCOVERIES ({len(self.discoveries)}):")
            for d in self.discoveries[:20]:
                marker = "✓" if d['verified'] else "★"
                print(f"    {marker} [{d['category']}] {d['title']}")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_discoveries': len(self.discoveries),
            'verified_count': len(self.verified),
            'discoveries': self.discoveries,
            'verified': self.verified,
            'patterns': dict(self.patterns)
        }

        output_file = RESULTS_DIR / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

        return output

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    researcher = DeepResearcher()
    researcher.run_all()
