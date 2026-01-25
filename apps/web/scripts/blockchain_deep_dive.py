#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    BLOCKCHAIN DEEP DIVE                                        ║
║                                                                                ║
║  Fixed API integration for deep blockchain analysis                            ║
║  - Proper handling of text vs JSON responses                                   ║
║  - Full early block analysis                                                   ║
║  - Transaction-level forensics                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import requests
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"
PATOSHI_FILE = DATA_DIR / "patoshi-addresses.json"

# APIs - Using multiple for redundancy
MEMPOOL_API = "https://mempool.space/api"
BLOCKSTREAM_API = "https://blockstream.info/api"

# Rate limiting
API_DELAY = 0.3  # seconds between requests

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
# FIXED BLOCKCHAIN API CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class BlockchainAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Research Bot)'
        })
        self.cache = {}
        self.request_count = 0
        self.last_request_time = 0

    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < API_DELAY:
            time.sleep(API_DELAY - elapsed)
        self.last_request_time = time.time()

    def _get_text(self, url: str) -> Optional[str]:
        """Get text response (for block hash endpoints)"""
        cache_key = f"text:{url}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            self._rate_limit()
            self.request_count += 1
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                text = response.text.strip()
                self.cache[cache_key] = text
                return text
            elif response.status_code == 429:
                print("  ⚠ Rate limited, waiting 10s...")
                time.sleep(10)
                return self._get_text(url)
            else:
                return None
        except Exception as e:
            print(f"  ✗ API Error (text): {e}")
            return None

    def _get_json(self, url: str) -> Optional[Any]:
        """Get JSON response"""
        cache_key = f"json:{url}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            self._rate_limit()
            self.request_count += 1
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = data
                return data
            elif response.status_code == 429:
                print("  ⚠ Rate limited, waiting 10s...")
                time.sleep(10)
                return self._get_json(url)
            else:
                return None
        except Exception as e:
            print(f"  ✗ API Error (json): {e}")
            return None

    def get_block_hash(self, height: int) -> Optional[str]:
        """Get block hash by height"""
        # Try mempool first
        hash_val = self._get_text(f"{MEMPOOL_API}/block-height/{height}")
        if hash_val and len(hash_val) == 64:
            return hash_val

        # Fallback to blockstream
        hash_val = self._get_text(f"{BLOCKSTREAM_API}/block-height/{height}")
        if hash_val and len(hash_val) == 64:
            return hash_val

        return None

    def get_block(self, height: int) -> Optional[Dict]:
        """Get full block data by height"""
        block_hash = self.get_block_hash(height)
        if not block_hash:
            return None

        # Get block details
        block = self._get_json(f"{MEMPOOL_API}/block/{block_hash}")
        if block:
            block['hash'] = block_hash
            return block

        # Fallback
        block = self._get_json(f"{BLOCKSTREAM_API}/block/{block_hash}")
        if block:
            block['hash'] = block_hash
            return block

        return None

    def get_block_txs(self, block_hash: str, start_index: int = 0) -> Optional[List]:
        """Get transactions in a block"""
        txs = self._get_json(f"{MEMPOOL_API}/block/{block_hash}/txs/{start_index}")
        if txs:
            return txs
        return self._get_json(f"{BLOCKSTREAM_API}/block/{block_hash}/txs/{start_index}")

    def get_address(self, address: str) -> Optional[Dict]:
        """Get address info"""
        addr = self._get_json(f"{MEMPOOL_API}/address/{address}")
        if addr:
            return addr
        return self._get_json(f"{BLOCKSTREAM_API}/address/{address}")

    def get_address_txs(self, address: str) -> Optional[List]:
        """Get address transactions"""
        txs = self._get_json(f"{MEMPOOL_API}/address/{address}/txs")
        if txs:
            return txs
        return self._get_json(f"{BLOCKSTREAM_API}/address/{address}/txs")

# ═══════════════════════════════════════════════════════════════════════════════
# DEEP BLOCKCHAIN RESEARCHER
# ═══════════════════════════════════════════════════════════════════════════════

class BlockchainDeepDive:
    def __init__(self):
        print("═" * 70)
        print("           BLOCKCHAIN DEEP DIVE")
        print("           Anna Matrix ↔ Bitcoin Correlation Analysis")
        print("═" * 70)

        self.matrix = Matrix()
        self.api = BlockchainAPI()
        self.discoveries = []
        self.block_data = []
        self.cfb_hits = []

        # Load Patoshi data
        with open(PATOSHI_FILE, 'r') as f:
            patoshi_data = json.load(f)
        self.patoshi_records = patoshi_data.get('records', [])
        self.patoshi_blocks = set(r.get('blockHeight', 0) for r in self.patoshi_records)
        print(f"✓ Loaded {len(self.patoshi_records)} Patoshi records")
        print(f"✓ Patoshi blocks: {len(self.patoshi_blocks)} unique")

    def log_discovery(self, category: str, title: str, data: dict):
        discovery = {
            'category': category,
            'title': title,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.discoveries.append(discovery)
        print(f"\n  ★★★ [{category.upper()}] {title}")
        for k, v in list(data.items())[:5]:
            print(f"      {k}: {v}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 1: FETCH AND ANALYZE FIRST 200 BLOCKS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_early_blocks(self, max_blocks: int = 200):
        """Fetch and analyze first N blocks"""
        print("\n" + "═" * 70)
        print(f"PHASE 1: ANALYZING FIRST {max_blocks} BLOCKS")
        print("═" * 70)

        for height in range(max_blocks):
            print(f"\r  Fetching block {height}/{max_blocks}...", end="", flush=True)

            block = self.api.get_block(height)
            if not block:
                print(f"\n  ⚠ Failed to fetch block {height}")
                continue

            timestamp = block.get('timestamp', 0)
            block_hash = block.get('hash', '')
            tx_count = block.get('tx_count', 0)
            is_patoshi = height in self.patoshi_blocks

            # Test multiple encoding methods for timestamp → matrix
            encodings = self._test_timestamp_encodings(timestamp, height)

            record = {
                'height': height,
                'timestamp': timestamp,
                'hash': block_hash,
                'tx_count': tx_count,
                'is_patoshi': is_patoshi,
                'encodings': encodings,
            }
            self.block_data.append(record)

            # Check for CFB hits
            for method, (row, col, value) in encodings.items():
                if is_cfb(value):
                    hit = {
                        'height': height,
                        'timestamp': timestamp,
                        'method': method,
                        'coords': (row, col),
                        'value': value,
                        'is_patoshi': is_patoshi
                    }
                    self.cfb_hits.append(hit)

        print(f"\n  ✓ Fetched {len(self.block_data)} blocks")
        print(f"  ✓ Found {len(self.cfb_hits)} CFB-hitting blocks")
        print(f"  ✓ API requests made: {self.api.request_count}")

        # Analyze patterns
        self._analyze_cfb_block_patterns()

    def _test_timestamp_encodings(self, timestamp: int, height: int) -> Dict:
        """Test all encoding methods for a timestamp"""
        encodings = {}

        # Method 1: timestamp mod 128
        row, col = (timestamp // 128) % 128, timestamp % 128
        value = self.matrix.query(row, col)
        encodings['ts_mod'] = (row, col, value)

        # Method 2: timestamp bit shift
        row, col = (timestamp >> 7) % 128, timestamp % 128
        value = self.matrix.query(row, col)
        encodings['ts_shift'] = (row, col, value)

        # Method 3: height encoding
        row, col = height % 128, (height // 128) % 128
        value = self.matrix.query(row, col)
        encodings['height'] = (row, col, value)

        # Method 4: timestamp bytes
        ts_bytes = timestamp.to_bytes(4, 'big')
        row, col = ts_bytes[0] % 128, ts_bytes[1] % 128
        value = self.matrix.query(row, col)
        encodings['ts_bytes'] = (row, col, value)

        # Method 5: XOR of timestamp bytes
        xor_val = ts_bytes[0] ^ ts_bytes[1] ^ ts_bytes[2] ^ ts_bytes[3]
        row, col = xor_val % 128, height % 128
        value = self.matrix.query(row, col)
        encodings['ts_xor'] = (row, col, value)

        # Method 6: timestamp % 128 for both row and col
        row, col = (timestamp % 128), ((timestamp // 128) % 128)
        value = self.matrix.query(row, col)
        encodings['ts_both_mod'] = (row, col, value)

        return encodings

    def _analyze_cfb_block_patterns(self):
        """Analyze patterns in CFB-hitting blocks"""
        print("\n" + "─" * 70)
        print("CFB BLOCK PATTERN ANALYSIS")
        print("─" * 70)

        if not self.cfb_hits:
            print("  No CFB hits found")
            return

        # Group by method
        by_method = defaultdict(list)
        for hit in self.cfb_hits:
            by_method[hit['method']].append(hit)

        print("\n  Hits by encoding method:")
        for method, hits in sorted(by_method.items(), key=lambda x: -len(x[1])):
            patoshi_count = sum(1 for h in hits if h['is_patoshi'])
            print(f"    {method}: {len(hits)} hits ({patoshi_count} Patoshi)")

        # Group by value
        by_value = defaultdict(list)
        for hit in self.cfb_hits:
            by_value[hit['value']].append(hit)

        print("\n  Hits by matrix value:")
        for value, hits in sorted(by_value.items()):
            blocks = [h['height'] for h in hits[:10]]
            print(f"    {value:+4d}: {len(hits)} blocks - {blocks}...")

        # Check for 27 specifically
        hits_27 = [h for h in self.cfb_hits if h['value'] == 27 or h['value'] == -27]
        if hits_27:
            print(f"\n  ★ Blocks hitting 27/-27: {len(hits_27)}")
            for h in hits_27[:10]:
                print(f"      Block {h['height']}: {h['method']} → {h['value']}")

            if len(hits_27) > 5:
                self.log_discovery('timestamp', f'{len(hits_27)} blocks encode 27', {
                    'block_count': len(hits_27),
                    'methods': list(set(h['method'] for h in hits_27)),
                    'blocks': [h['height'] for h in hits_27[:20]]
                })

        # Patoshi blocks specifically
        patoshi_hits = [h for h in self.cfb_hits if h['is_patoshi']]
        if patoshi_hits:
            print(f"\n  ★ Patoshi blocks hitting CFB: {len(patoshi_hits)}")
            for h in patoshi_hits[:10]:
                print(f"      Block {h['height']}: {h['method']} → {h['value']}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 2: TRANSACTION-LEVEL ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_cfb_block_transactions(self, max_blocks: int = 20):
        """Deep dive into transactions of CFB-hitting blocks"""
        print("\n" + "═" * 70)
        print("PHASE 2: TRANSACTION-LEVEL FORENSICS")
        print("═" * 70)

        if not self.cfb_hits:
            print("  No CFB blocks to analyze")
            return

        # Get unique block heights
        block_heights = list(set(h['height'] for h in self.cfb_hits))[:max_blocks]
        print(f"\n  Analyzing transactions in {len(block_heights)} CFB blocks...")

        tx_patterns = []
        for height in block_heights:
            # Find block hash
            block_info = next((b for b in self.block_data if b['height'] == height), None)
            if not block_info:
                continue

            block_hash = block_info.get('hash', '')
            if not block_hash:
                continue

            print(f"\r  Fetching txs for block {height}...", end="", flush=True)
            txs = self.api.get_block_txs(block_hash)
            if not txs:
                continue

            for tx in txs:
                # Analyze outputs
                for vout in tx.get('vout', []):
                    scriptpubkey = vout.get('scriptpubkey', '')
                    value = vout.get('value', 0)
                    address = vout.get('scriptpubkey_address', '')

                    if scriptpubkey:
                        # Hash scriptpubkey to matrix coords
                        h = hashlib.sha256(bytes.fromhex(scriptpubkey) if len(scriptpubkey) % 2 == 0 else b'').digest()
                        row, col = h[0] % 128, h[1] % 128
                        mat_val = self.matrix.query(row, col)

                        if is_cfb(mat_val):
                            tx_patterns.append({
                                'block': height,
                                'txid': tx.get('txid', '')[:16],
                                'address': address[:20] if address else 'N/A',
                                'value_sats': value,
                                'matrix_value': mat_val
                            })

        print(f"\n  ✓ Found {len(tx_patterns)} CFB-hitting transactions")

        if tx_patterns:
            print("\n  CFB-hitting transactions:")
            for p in tx_patterns[:15]:
                print(f"    Block {p['block']}: {p['address']}... → {p['matrix_value']}")

            if len(tx_patterns) > 5:
                self.log_discovery('transaction', f'{len(tx_patterns)} txs encode CFB numbers', {
                    'tx_count': len(tx_patterns),
                    'sample': tx_patterns[:10]
                })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 3: STRATEGIC ADDRESS VERIFICATION
    # ───────────────────────────────────────────────────────────────────────────

    def verify_strategic_addresses(self):
        """Verify strategic addresses via API"""
        print("\n" + "═" * 70)
        print("PHASE 3: STRATEGIC ADDRESS VERIFICATION")
        print("═" * 70)

        addresses = [
            (GENESIS_ADDRESS, "Genesis"),
            (CFB_ADDRESS, "1CFB"),
            (BLOCK1_ADDRESS, "Block 1"),
        ]

        for addr, name in addresses:
            print(f"\n  Verifying {name}: {addr[:20]}...")

            addr_data = self.api.get_address(addr)
            if not addr_data:
                print(f"    ✗ Failed to fetch")
                continue

            chain_stats = addr_data.get('chain_stats', {})
            mempool_stats = addr_data.get('mempool_stats', {})

            funded = chain_stats.get('funded_txo_sum', 0)
            spent = chain_stats.get('spent_txo_sum', 0)
            balance = funded - spent
            tx_count = chain_stats.get('tx_count', 0)

            print(f"    Balance: {balance / 1e8:.8f} BTC")
            print(f"    TX count: {tx_count}")
            print(f"    Total received: {funded / 1e8:.8f} BTC")
            print(f"    Total spent: {spent / 1e8:.8f} BTC")

            # Analyze address hash160 against matrix
            h160 = base58_decode(addr)[1:21]
            cfb_bytes = []
            for i, byte in enumerate(h160):
                row, col = byte % 128, i % 128
                val = self.matrix.query(row, col)
                if is_cfb(val):
                    cfb_bytes.append((i, byte, val))

            if cfb_bytes:
                print(f"    ★ {len(cfb_bytes)} bytes hit CFB in matrix")
                for i, byte, val in cfb_bytes[:5]:
                    print(f"      Byte {i}: 0x{byte:02x} → {val}")

                self.log_discovery('address', f'{name} has {len(cfb_bytes)} CFB-hitting bytes', {
                    'address': addr,
                    'balance_btc': balance / 1e8,
                    'cfb_bytes': cfb_bytes
                })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 4: TIMESTAMP CORRELATION ACROSS ALL DATA
    # ───────────────────────────────────────────────────────────────────────────

    def timestamp_correlation_analysis(self):
        """Deep analysis of timestamp → 27 correlation"""
        print("\n" + "═" * 70)
        print("PHASE 4: TIMESTAMP CORRELATION ANALYSIS")
        print("═" * 70)

        if not self.block_data:
            print("  No block data available")
            return

        # Specifically look for blocks encoding 27
        blocks_27 = []
        for block in self.block_data:
            for method, (row, col, value) in block['encodings'].items():
                if value == 27:
                    blocks_27.append({
                        'height': block['height'],
                        'timestamp': block['timestamp'],
                        'method': method,
                        'coords': (row, col),
                        'is_patoshi': block['is_patoshi']
                    })

        print(f"\n  Blocks encoding +27: {len(blocks_27)}")

        if blocks_27:
            # Check if there's a pattern in which method produces 27
            by_method = defaultdict(list)
            for b in blocks_27:
                by_method[b['method']].append(b['height'])

            print("\n  By method:")
            for method, heights in by_method.items():
                print(f"    {method}: blocks {heights[:10]}...")

                # Check for periodicity
                if len(heights) > 1:
                    diffs = [heights[i+1] - heights[i] for i in range(len(heights)-1)]
                    unique_diffs = set(diffs)
                    if len(unique_diffs) <= 3:
                        print(f"      → Period detected: {unique_diffs}")
                        if any(d in CFB_NUMBERS for d in unique_diffs):
                            self.log_discovery('timestamp', f'Block 27 period is CFB number', {
                                'method': method,
                                'periods': list(unique_diffs),
                                'blocks': heights
                            })

        # Check block 9 specifically (known to give 27)
        block9 = next((b for b in self.block_data if b['height'] == 9), None)
        if block9:
            print(f"\n  Block 9 (first Satoshi tx) analysis:")
            print(f"    Timestamp: {block9['timestamp']}")
            for method, (row, col, value) in block9['encodings'].items():
                marker = " ★ CFB!" if is_cfb(value) else ""
                print(f"    {method}: [{row},{col}] = {value}{marker}")

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self, max_blocks: int = 100):
        """Execute complete blockchain analysis"""
        start_time = time.time()

        try:
            self.analyze_early_blocks(max_blocks)
            self.analyze_cfb_block_transactions()
            self.verify_strategic_addresses()
            self.timestamp_correlation_analysis()
        except KeyboardInterrupt:
            print("\n  ⚠ Interrupted by user")
        except Exception as e:
            print(f"\n  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

        # Final Report
        duration = time.time() - start_time
        print("\n" + "═" * 70)
        print("           BLOCKCHAIN ANALYSIS COMPLETE")
        print("═" * 70)

        print(f"\n  Duration: {duration:.1f} seconds")
        print(f"  Blocks analyzed: {len(self.block_data)}")
        print(f"  CFB hits: {len(self.cfb_hits)}")
        print(f"  Discoveries: {len(self.discoveries)}")
        print(f"  API requests: {self.api.request_count}")

        if self.discoveries:
            print("\n  DISCOVERIES:")
            for d in self.discoveries:
                print(f"    ★ [{d['category']}] {d['title']}")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'blocks_analyzed': len(self.block_data),
            'cfb_hits': len(self.cfb_hits),
            'discoveries': self.discoveries,
            'block_data': self.block_data[:50],  # First 50 for reference
            'cfb_blocks': self.cfb_hits
        }

        output_file = SCRIPT_DIR / 'blockchain_deep_dive_results.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

        return output

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    max_blocks = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    researcher = BlockchainDeepDive()
    researcher.run_all(max_blocks=max_blocks)
