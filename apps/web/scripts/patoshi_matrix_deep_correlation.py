#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PATOSHI-MATRIX DEEP CORRELATION                             ║
║                                                                                ║
║  Exhaustive analysis of 21,953 Patoshi records against Anna Matrix            ║
║  - Multiple encoding methods for each pubkey                                   ║
║  - Block height correlations                                                   ║
║  - Temporal pattern analysis                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from collections import defaultdict, Counter
import statistics

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"
PATOSHI_FILE = DATA_DIR / "patoshi-addresses.json"

CFB_NUMBERS = [27, 37, 42, 127]
CFB_NUMBERS_EXTENDED = [27, 37, 42, 127, 576, 21, 33]

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']
        self._build_value_index()

    def _build_value_index(self):
        """Pre-index all values for fast lookup"""
        self.value_index = defaultdict(list)
        for row in range(128):
            for col in range(128):
                v = self.data[row][col]
                if isinstance(v, int):
                    self.value_index[v].append((row, col))

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

    def get_row(self, row: int) -> List[int]:
        return [self.query(row, c) for c in range(128)]

    def get_col(self, col: int) -> List[int]:
        return [self.query(r, col) for r in range(128)]

def is_cfb(value: Optional[int]) -> bool:
    if value is None:
        return False
    return value in CFB_NUMBERS or -value in CFB_NUMBERS

# ═══════════════════════════════════════════════════════════════════════════════
# PATOSHI ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

class PatoshiMatrixAnalyzer:
    def __init__(self):
        print("═" * 70)
        print("           PATOSHI-MATRIX DEEP CORRELATION")
        print("═" * 70)

        self.matrix = Matrix()

        # Load Patoshi data
        with open(PATOSHI_FILE, 'r') as f:
            patoshi_data = json.load(f)
        self.records = patoshi_data.get('records', [])
        print(f"✓ Loaded {len(self.records)} Patoshi records")

        self.discoveries = []
        self.statistics = {}

    def log_discovery(self, title: str, data: dict):
        self.discoveries.append({'title': title, 'data': data})
        print(f"\n  ★★★ {title}")
        for k, v in list(data.items())[:5]:
            val_str = str(v)[:60] + "..." if len(str(v)) > 60 else str(v)
            print(f"      {k}: {val_str}")

    # ───────────────────────────────────────────────────────────────────────────
    # ENCODING METHODS
    # ───────────────────────────────────────────────────────────────────────────

    def encode_pubkey_methods(self, pubkey: str) -> Dict[str, Tuple[int, int, Optional[int]]]:
        """Apply all encoding methods to a pubkey"""
        results = {}

        if not pubkey:
            return results

        # Method 1: SHA256 of pubkey string (current method)
        h = hashlib.sha256(pubkey.encode()).digest()
        row, col = h[0] % 128, h[1] % 128
        results['sha256'] = (row, col, self.matrix.query(row, col))

        # Method 2: Double SHA256
        h2 = hashlib.sha256(h).digest()
        row, col = h2[0] % 128, h2[1] % 128
        results['double_sha256'] = (row, col, self.matrix.query(row, col))

        # Method 3: MD5
        m = hashlib.md5(pubkey.encode()).digest()
        row, col = m[0] % 128, m[1] % 128
        results['md5'] = (row, col, self.matrix.query(row, col))

        # Method 4: Raw bytes (if hex)
        if len(pubkey) >= 4 and all(c in '0123456789abcdefABCDEF' for c in pubkey[:4]):
            try:
                raw = bytes.fromhex(pubkey)
                if len(raw) >= 2:
                    row, col = raw[0] % 128, raw[1] % 128
                    results['raw_bytes'] = (row, col, self.matrix.query(row, col))

                    # Also try middle bytes
                    mid = len(raw) // 2
                    row, col = raw[mid] % 128, raw[mid+1] % 128
                    results['mid_bytes'] = (row, col, self.matrix.query(row, col))

                    # XOR of all bytes
                    xor_val = 0
                    for b in raw:
                        xor_val ^= b
                    row, col = xor_val % 128, (xor_val // 2) % 128
                    results['xor_all'] = (row, col, self.matrix.query(row, col))
            except:
                pass

        # Method 5: ASCII sum
        ascii_sum = sum(ord(c) for c in pubkey)
        row, col = ascii_sum % 128, (ascii_sum // 128) % 128
        results['ascii_sum'] = (row, col, self.matrix.query(row, col))

        return results

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 1: VALUE DISTRIBUTION
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_value_distribution(self):
        """Comprehensive value distribution analysis"""
        print("\n" + "═" * 70)
        print("PHASE 1: VALUE DISTRIBUTION ANALYSIS")
        print("═" * 70)

        # Collect values per encoding method
        method_values = defaultdict(lambda: defaultdict(int))
        method_totals = defaultdict(int)

        for record in self.records:
            pubkey = record.get('pubkey', '')
            if not pubkey:
                continue

            encodings = self.encode_pubkey_methods(pubkey)
            for method, (row, col, value) in encodings.items():
                if value is not None:
                    method_values[method][value] += 1
                    method_totals[method] += 1

        # Analyze each method
        for method in ['sha256', 'double_sha256', 'raw_bytes', 'xor_all', 'ascii_sum']:
            if method not in method_totals:
                continue

            values = method_values[method]
            total = method_totals[method]
            expected = total / 256

            print(f"\n  Method: {method}")
            print(f"  Total samples: {total}, Expected per value: {expected:.1f}")

            # Sort by count
            sorted_vals = sorted(values.items(), key=lambda x: -x[1])[:15]

            print("  Top 15 values:")
            cfb_over_represented = []

            for val, count in sorted_vals:
                ratio = count / expected
                marker = ""
                if is_cfb(val):
                    marker = " ★★★ CFB"
                    if ratio > 2:
                        cfb_over_represented.append((val, count, ratio))
                print(f"    {val:+4d}: {count:5d} ({ratio:.2f}x){marker}")

            # Check specifically for CFB numbers
            print("\n  CFB numbers specifically:")
            for cfb in [-127, -42, -37, -27, 27, 37, 42, 127]:
                count = values.get(cfb, 0)
                ratio = count / expected if expected > 0 else 0
                marker = " ★" if ratio > 2 else ""
                print(f"    {cfb:+4d}: {count:5d} ({ratio:.2f}x){marker}")

            if cfb_over_represented:
                self.log_discovery(f'{method}: CFB over-representation', {
                    'method': method,
                    'cfb_values': cfb_over_represented,
                    'total': total
                })

        # Store for later
        self.statistics['method_values'] = dict(method_values)

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 2: BLOCK HEIGHT CORRELATION
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_block_correlations(self):
        """Analyze correlations between block heights and matrix values"""
        print("\n" + "═" * 70)
        print("PHASE 2: BLOCK HEIGHT CORRELATION")
        print("═" * 70)

        # Group records by whether they hit CFB numbers
        cfb_blocks = []
        non_cfb_blocks = []

        for record in self.records:
            pubkey = record.get('pubkey', '')
            block = record.get('blockHeight', 0)
            if not pubkey:
                continue

            h = hashlib.sha256(pubkey.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            value = self.matrix.query(row, col)

            if is_cfb(value):
                cfb_blocks.append(block)
            else:
                non_cfb_blocks.append(block)

        print(f"\n  CFB-hitting blocks: {len(cfb_blocks)}")
        print(f"  Non-CFB blocks: {len(non_cfb_blocks)}")

        if cfb_blocks:
            # Statistical comparison
            cfb_mean = statistics.mean(cfb_blocks)
            cfb_median = statistics.median(cfb_blocks)
            non_cfb_mean = statistics.mean(non_cfb_blocks) if non_cfb_blocks else 0
            non_cfb_median = statistics.median(non_cfb_blocks) if non_cfb_blocks else 0

            print(f"\n  CFB blocks - Mean: {cfb_mean:.1f}, Median: {cfb_median}")
            print(f"  Non-CFB blocks - Mean: {non_cfb_mean:.1f}, Median: {non_cfb_median}")

            # Check for block clustering
            cfb_sorted = sorted(cfb_blocks)
            gaps = [cfb_sorted[i+1] - cfb_sorted[i] for i in range(len(cfb_sorted)-1)]
            gap_counts = Counter(gaps)

            print("\n  Most common gaps between CFB blocks:")
            for gap, count in gap_counts.most_common(10):
                marker = " ★ CFB gap" if gap in CFB_NUMBERS_EXTENDED else ""
                print(f"    Gap {gap}: {count} occurrences{marker}")

            # Check for CFB gaps
            cfb_gaps = [g for g in gap_counts if g in CFB_NUMBERS_EXTENDED]
            if cfb_gaps:
                self.log_discovery('Block gaps contain CFB numbers', {
                    'cfb_gaps': {g: gap_counts[g] for g in cfb_gaps},
                    'total_cfb_blocks': len(cfb_blocks)
                })

            # Block ranges with high CFB density
            print("\n  CFB density by block range:")
            range_size = 1000
            range_counts = defaultdict(int)
            for b in cfb_blocks:
                range_counts[b // range_size] += 1

            total_by_range = defaultdict(int)
            for record in self.records:
                b = record.get('blockHeight', 0)
                total_by_range[b // range_size] += 1

            for r in sorted(range_counts.keys())[:15]:
                count = range_counts[r]
                total = total_by_range[r]
                pct = (count / total * 100) if total > 0 else 0
                bar = "█" * int(pct / 2)
                print(f"    {r*range_size:6d}-{(r+1)*range_size-1:6d}: {count:4d}/{total:4d} ({pct:5.1f}%) {bar}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 3: MATRIX ROW/COLUMN ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_matrix_distribution(self):
        """Analyze which matrix rows/cols Patoshi pubkeys hit most"""
        print("\n" + "═" * 70)
        print("PHASE 3: MATRIX ROW/COLUMN ANALYSIS")
        print("═" * 70)

        row_counts = defaultdict(int)
        col_counts = defaultdict(int)
        cell_counts = defaultdict(int)

        for record in self.records:
            pubkey = record.get('pubkey', '')
            if not pubkey:
                continue

            h = hashlib.sha256(pubkey.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            row_counts[row] += 1
            col_counts[col] += 1
            cell_counts[(row, col)] += 1

        # Row analysis
        print("\n  Most hit rows:")
        expected_per_row = len(self.records) / 128
        for row, count in sorted(row_counts.items(), key=lambda x: -x[1])[:10]:
            ratio = count / expected_per_row
            row_sum = sum(v for v in self.matrix.get_row(row) if v is not None)
            cfb_in_row = sum(1 for v in self.matrix.get_row(row) if is_cfb(v))
            print(f"    Row {row:3d}: {count:4d} hits ({ratio:.2f}x), sum={row_sum}, CFB cells={cfb_in_row}")

        # Column analysis
        print("\n  Most hit columns:")
        expected_per_col = len(self.records) / 128
        for col, count in sorted(col_counts.items(), key=lambda x: -x[1])[:10]:
            ratio = count / expected_per_col
            col_sum = sum(v for v in self.matrix.get_col(col) if v is not None)
            cfb_in_col = sum(1 for v in self.matrix.get_col(col) if is_cfb(v))
            print(f"    Col {col:3d}: {count:4d} hits ({ratio:.2f}x), sum={col_sum}, CFB cells={cfb_in_col}")

        # Check row 27 and col 27 specifically
        print(f"\n  Row 27 hits: {row_counts.get(27, 0)} (expected: {expected_per_row:.1f})")
        print(f"  Col 27 hits: {col_counts.get(27, 0)} (expected: {expected_per_col:.1f})")
        print(f"  Row 37 hits: {row_counts.get(37, 0)}")
        print(f"  Col 37 hits: {col_counts.get(37, 0)}")

        # Most hit specific cells
        print("\n  Most hit matrix cells:")
        for (row, col), count in sorted(cell_counts.items(), key=lambda x: -x[1])[:15]:
            value = self.matrix.query(row, col)
            marker = " ★ CFB" if is_cfb(value) else ""
            print(f"    [{row:3d},{col:3d}] = {value:+4d}: {count:3d} hits{marker}")

        # Store for later
        self.statistics['row_counts'] = dict(row_counts)
        self.statistics['col_counts'] = dict(col_counts)

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 4: XOR PATTERN ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_xor_patterns(self):
        """Analyze XOR patterns between consecutive Patoshi pubkeys"""
        print("\n" + "═" * 70)
        print("PHASE 4: XOR PATTERN ANALYSIS")
        print("═" * 70)

        # Sort by block height
        sorted_records = sorted(self.records, key=lambda r: r.get('blockHeight', 0))

        xor_results = defaultdict(int)
        value_xors = []

        for i in range(len(sorted_records) - 1):
            pk1 = sorted_records[i].get('pubkey', '')
            pk2 = sorted_records[i+1].get('pubkey', '')

            if not pk1 or not pk2:
                continue

            # Get matrix values for consecutive pubkeys
            h1 = hashlib.sha256(pk1.encode()).digest()
            h2 = hashlib.sha256(pk2.encode()).digest()

            v1 = self.matrix.query(h1[0] % 128, h1[1] % 128)
            v2 = self.matrix.query(h2[0] % 128, h2[1] % 128)

            if v1 is not None and v2 is not None:
                xor = v1 ^ v2
                xor_results[xor] += 1
                value_xors.append({
                    'block1': sorted_records[i].get('blockHeight', 0),
                    'block2': sorted_records[i+1].get('blockHeight', 0),
                    'v1': v1,
                    'v2': v2,
                    'xor': xor
                })

        print(f"\n  Total consecutive pairs analyzed: {len(value_xors)}")

        # Find CFB XOR results
        print("\n  Most common XOR results:")
        for xor_val, count in sorted(xor_results.items(), key=lambda x: -x[1])[:15]:
            marker = " ★★★ CFB" if xor_val in CFB_NUMBERS else ""
            print(f"    XOR = {xor_val:4d}: {count:5d} times{marker}")

        # Specifically check CFB XOR results
        print("\n  CFB number XOR results:")
        for cfb in CFB_NUMBERS:
            count = xor_results.get(cfb, 0)
            expected = len(value_xors) / 256
            ratio = count / expected if expected > 0 else 0
            print(f"    XOR = {cfb:3d}: {count:5d} ({ratio:.2f}x expected)")

            if ratio > 2:
                self.log_discovery(f'Consecutive XOR = {cfb} over-represented', {
                    'cfb': cfb,
                    'count': count,
                    'expected': round(expected, 1),
                    'ratio': round(ratio, 2)
                })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 5: SPECIFIC PATTERN SEARCH
    # ───────────────────────────────────────────────────────────────────────────

    def search_specific_patterns(self):
        """Search for known patterns like "27 sequence" in data"""
        print("\n" + "═" * 70)
        print("PHASE 5: SPECIFIC PATTERN SEARCH")
        print("═" * 70)

        # Find sequences of blocks where value = 27 or -27
        sorted_records = sorted(self.records, key=lambda r: r.get('blockHeight', 0))

        current_sequence = []
        all_sequences = []

        for record in sorted_records:
            pubkey = record.get('pubkey', '')
            block = record.get('blockHeight', 0)

            if not pubkey:
                continue

            h = hashlib.sha256(pubkey.encode()).digest()
            value = self.matrix.query(h[0] % 128, h[1] % 128)

            if value == 27 or value == -27:
                current_sequence.append(block)
            else:
                if len(current_sequence) > 1:
                    all_sequences.append(current_sequence.copy())
                current_sequence = []

        if len(current_sequence) > 1:
            all_sequences.append(current_sequence)

        print(f"\n  Sequences of consecutive blocks hitting 27/-27: {len(all_sequences)}")
        if all_sequences:
            print("  Longest sequences:")
            for seq in sorted(all_sequences, key=len, reverse=True)[:10]:
                print(f"    Length {len(seq)}: blocks {seq[0]} to {seq[-1]}")

        # Look for block numbers that are themselves CFB numbers
        print("\n  Blocks with CFB block numbers:")
        cfb_block_pubkeys = []
        for record in self.records:
            block = record.get('blockHeight', 0)
            if block in CFB_NUMBERS_EXTENDED:
                pubkey = record.get('pubkey', '')
                h = hashlib.sha256(pubkey.encode()).digest()
                value = self.matrix.query(h[0] % 128, h[1] % 128)
                cfb_block_pubkeys.append({
                    'block': block,
                    'value': value,
                    'is_cfb': is_cfb(value)
                })
                marker = " ★ also CFB value!" if is_cfb(value) else ""
                print(f"    Block {block}: matrix value = {value}{marker}")

        if any(p['is_cfb'] for p in cfb_block_pubkeys):
            self.log_discovery('CFB block numbers have CFB values', {
                'blocks': cfb_block_pubkeys
            })

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self):
        """Execute all analyses"""
        self.analyze_value_distribution()
        self.analyze_block_correlations()
        self.analyze_matrix_distribution()
        self.analyze_xor_patterns()
        self.search_specific_patterns()

        # Summary
        print("\n" + "═" * 70)
        print("           ANALYSIS COMPLETE")
        print("═" * 70)

        print(f"\n  Total discoveries: {len(self.discoveries)}")

        if self.discoveries:
            print("\n  DISCOVERIES:")
            for d in self.discoveries:
                print(f"    ★ {d['title']}")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(self.records),
            'discoveries': self.discoveries,
            'statistics': self.statistics
        }

        output_file = SCRIPT_DIR / 'patoshi_matrix_correlation_results.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    analyzer = PatoshiMatrixAnalyzer()
    analyzer.run_all()
