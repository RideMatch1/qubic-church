#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    SYSTEMATIC ANNA MATRIX EXPLORATION                          ║
║                                                                                ║
║  Automated comprehensive analysis of correlations                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Import from our research terminal
from anna_research_terminal import (
    AnnaMatrix, Encoders, PatternScanner, BlockchainCorrelator,
    KNOWN_COORDINATES, CFB_NUMBERS, DATA_DIR
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

RESULTS_DIR = Path(__file__).parent / "systematic_scan_results"
RESULTS_DIR.mkdir(exist_ok=True)

# Early Bitcoin blocks with known timestamps (from blockchain)
EARLY_BLOCKS = [
    (0, "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", 1231006505),
    (1, "00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048", 1231469665),
    (9, "000000008d9dc510f23c2657fc4f67bea30078cc05a90eb89e84cc475c080805", 1231473279),
    (27, None, 1231497905),  # CFB's number
    (37, None, 1231499035),  # CFB's number
    (42, None, 1231501875),  # CFB's number
    (127, None, 1231556806), # Power of 2 - 1
    (128, None, 1231557415), # Power of 2
    (170, "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee", 1231731025),
    (256, None, 1231773061), # Power of 2
    (576, None, 1232049795), # CFB's event number
    (1000, None, 1232346606),
    (2016, None, 1233061996), # Difficulty adjustment period
    (21000, None, None),      # First halving block
]

# CFB related strings to test
CFB_STRINGS = [
    "Come-from-Beyond",
    "CFB",
    "Sergey Ivancheglo",
    "NXT",
    "IOTA",
    "Qubic",
    "JINN",
    "Abra",
    "Aigarth",
    "Anna",
    "BCNext",
    "ANN",
    "jl777",  # Known collaborator
    "The Butterfly Effect",
]

# Known significant Bitcoin addresses
STRATEGIC_ADDRESSES = [
    ("Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
    ("Block 1", "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"),
    ("CFB Signature", "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"),
    ("Satoshi Return?", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEMATIC EXPLORATION CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class SystematicExplorer:
    def __init__(self):
        print("═" * 70)
        print("         SYSTEMATIC ANNA MATRIX EXPLORATION")
        print("═" * 70)

        self.matrix = AnnaMatrix()
        self.scanner = PatternScanner(self.matrix)
        self.correlator = BlockchainCorrelator(self.matrix)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'discoveries': [],
            'patterns': [],
            'correlations': [],
            'statistics': {},
        }

    def log_discovery(self, category: str, description: str, data: dict):
        """Log a potentially significant discovery"""
        discovery = {
            'category': category,
            'description': description,
            'data': data
        }
        self.results['discoveries'].append(discovery)
        print(f"\n  ★ DISCOVERY [{category}]: {description}")
        for k, v in data.items():
            print(f"      {k}: {v}")

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 1: CFB Numbers Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def scan_cfb_numbers(self):
        """Comprehensive analysis of CFB's special numbers"""
        print("\n" + "─" * 70)
        print("SCAN 1: CFB NUMBERS ANALYSIS")
        print("─" * 70)

        cfb_analysis = {}

        for num in CFB_NUMBERS:
            if not (-128 <= num <= 127):
                continue

            coords = self.matrix.find_value(num)
            cfb_analysis[num] = {
                'count': len(coords),
                'sample_coords': coords[:10],
            }

            print(f"\n  Value {num:+4d}: {len(coords)} cells")

            # Check if any known coordinates have this value
            for coord, desc in KNOWN_COORDINATES.items():
                value = self.matrix.query(coord[0], coord[1])
                if value == num:
                    self.log_discovery('cfb_value', f"Known coord {desc} has CFB value {num}", {
                        'coordinate': coord,
                        'value': num,
                        'description': desc
                    })

        # Check negative variants
        print("\n  Negative variants:")
        for num in CFB_NUMBERS:
            if not (-128 <= -num <= 127):
                continue
            coords = self.matrix.find_value(-num)
            print(f"    Value {-num:+4d}: {len(coords)} cells")

        self.results['cfb_analysis'] = cfb_analysis

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 2: Block Timestamp Correlation
    # ───────────────────────────────────────────────────────────────────────────

    def scan_block_timestamps(self):
        """Correlate early block timestamps with Anna Matrix"""
        print("\n" + "─" * 70)
        print("SCAN 2: BLOCK TIMESTAMP CORRELATION")
        print("─" * 70)

        timestamp_results = []

        for block_height, block_hash, timestamp in EARLY_BLOCKS:
            if timestamp is None:
                continue

            # Try different encoding methods
            encodings = {
                'ts_mod': Encoders.timestamp_to_coords(timestamp),
                'ts_direct': Encoders.timestamp_direct(timestamp),
                'block_height': Encoders.block_height_to_coords(block_height),
            }

            if block_hash:
                encodings['block_hash'] = Encoders.hex_to_coords(block_hash)

            print(f"\n  Block {block_height} (ts={timestamp}):")

            for encoding_name, (row, col) in encodings.items():
                value = self.matrix.query(row, col)
                anna_x, anna_y = self.matrix.matrix_to_anna(row, col)

                result = {
                    'block': block_height,
                    'timestamp': timestamp,
                    'encoding': encoding_name,
                    'coords': (row, col),
                    'anna': (anna_x, anna_y),
                    'value': value,
                }
                timestamp_results.append(result)

                sig_marker = ""
                if value in CFB_NUMBERS or -value in CFB_NUMBERS:
                    sig_marker = " ★★★ CFB NUMBER!"
                    self.log_discovery('timestamp_cfb', f"Block {block_height} -> {value}", result)
                elif (row, col) in KNOWN_COORDINATES:
                    sig_marker = f" ★ {KNOWN_COORDINATES[(row, col)]}"

                print(f"    {encoding_name:15s}: [{row:3d},{col:3d}] = {value:+4d}{sig_marker}")

        self.results['timestamp_correlation'] = timestamp_results

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 3: CFB Strings Hash Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def scan_cfb_strings(self):
        """Hash CFB-related strings and check values"""
        print("\n" + "─" * 70)
        print("SCAN 3: CFB STRINGS HASH ANALYSIS")
        print("─" * 70)

        string_results = []

        for string in CFB_STRINGS:
            row, col = Encoders.sha256_to_coords(string)
            value = self.matrix.query(row, col)
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)

            # Also try lowercase
            row_l, col_l = Encoders.sha256_to_coords(string.lower())
            value_l = self.matrix.query(row_l, col_l)

            result = {
                'string': string,
                'coords': (row, col),
                'value': value,
                'lowercase_coords': (row_l, col_l),
                'lowercase_value': value_l,
            }
            string_results.append(result)

            sig_marker = ""
            if value in CFB_NUMBERS or -value in CFB_NUMBERS:
                sig_marker = " ★★★ CFB NUMBER!"
                self.log_discovery('string_cfb', f'"{string}" -> {value}', result)
            elif (row, col) in KNOWN_COORDINATES:
                sig_marker = f" ★ {KNOWN_COORDINATES[(row, col)]}"

            print(f"\n  \"{string}\":")
            print(f"    SHA256:    [{row:3d},{col:3d}] = {value:+4d}{sig_marker}")
            if value_l != value:
                print(f"    lowercase: [{row_l:3d},{col_l:3d}] = {value_l:+4d}")

        self.results['string_analysis'] = string_results

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 4: Strategic Bitcoin Addresses
    # ───────────────────────────────────────────────────────────────────────────

    def scan_strategic_addresses(self):
        """Check strategic Bitcoin addresses"""
        print("\n" + "─" * 70)
        print("SCAN 4: STRATEGIC BITCOIN ADDRESSES")
        print("─" * 70)

        address_results = []

        for label, address in STRATEGIC_ADDRESSES:
            row, col = Encoders.btc_address_to_coords(address)
            value = self.matrix.query(row, col)
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)

            # Double SHA256 (Bitcoin style)
            row2, col2 = Encoders.double_sha256_to_coords(address)
            value2 = self.matrix.query(row2, col2)

            result = {
                'label': label,
                'address': address,
                'sha256_coords': (row, col),
                'sha256_value': value,
                'double_sha256_coords': (row2, col2),
                'double_sha256_value': value2,
            }
            address_results.append(result)

            print(f"\n  {label}: {address[:20]}...")

            for enc, (r, c), v in [('SHA256', (row, col), value), ('Double SHA256', (row2, col2), value2)]:
                sig_marker = ""
                if v in CFB_NUMBERS or -v in CFB_NUMBERS:
                    sig_marker = " ★★★ CFB NUMBER!"
                    self.log_discovery('address_cfb', f'{label} -> {v}', result)
                elif (r, c) in KNOWN_COORDINATES:
                    sig_marker = f" ★ {KNOWN_COORDINATES[(r, c)]}"
                print(f"    {enc:15s}: [{r:3d},{c:3d}] = {v:+4d}{sig_marker}")

        self.results['address_analysis'] = address_results

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 5: Patoshi Pattern Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def scan_patoshi_patterns(self):
        """Analyze patterns in Patoshi addresses"""
        print("\n" + "─" * 70)
        print("SCAN 5: PATOSHI PATTERN ANALYSIS")
        print("─" * 70)

        addresses = []
        for addr_data in self.correlator.patoshi_addresses[:500]:
            if isinstance(addr_data, dict):
                addresses.append(addr_data.get('address', ''))
            else:
                addresses.append(addr_data)

        results = self.correlator.correlate_addresses(addresses)

        # Analyze value distribution
        value_counts = defaultdict(int)
        coord_usage = defaultdict(int)

        for r in results:
            if r.value is not None:
                value_counts[r.value] += 1
            coord_usage[(r.row, r.col)] += 1

        print(f"\n  Analyzed {len(results)} Patoshi addresses")

        # Most common values
        sorted_values = sorted(value_counts.items(), key=lambda x: -x[1])[:15]
        print("\n  Most common values:")
        for val, count in sorted_values:
            pct = (count / len(results)) * 100
            cfb_marker = " ★ CFB" if val in CFB_NUMBERS else ""
            print(f"    {val:+4d}: {count:4d} ({pct:5.1f}%){cfb_marker}")

        # Check for collision clusters
        sorted_coords = sorted(coord_usage.items(), key=lambda x: -x[1])[:10]
        print("\n  Most hit coordinates:")
        for (row, col), count in sorted_coords:
            if count > 1:
                value = self.matrix.query(row, col)
                known = KNOWN_COORDINATES.get((row, col), "")
                print(f"    [{row:3d},{col:3d}] = {value:+4d}: {count} addresses{' ★ ' + known if known else ''}")

        self.results['patoshi_analysis'] = {
            'count': len(results),
            'value_distribution': dict(value_counts),
            'top_values': sorted_values,
            'coordinate_collisions': [(list(c), n) for c, n in sorted_coords if n > 1],
        }

        # Check if value 48 is significant
        if value_counts.get(48, 0) > 10:
            self.log_discovery('patoshi_pattern', f"Value 48 appears {value_counts[48]} times in Patoshi addresses", {
                'value': 48,
                'count': value_counts[48],
                'percentage': (value_counts[48] / len(results)) * 100
            })

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 6: Diagonal Pattern Search
    # ───────────────────────────────────────────────────────────────────────────

    def scan_diagonals(self):
        """Scan diagonals for patterns"""
        print("\n" + "─" * 70)
        print("SCAN 6: DIAGONAL PATTERN SEARCH")
        print("─" * 70)

        diagonal_patterns = []

        # Main diagonal (0,0) to (127,127)
        main_diag = self.scanner.scan_diagonal(0, 0, 'down-right')
        values = [v for _, v in main_diag if v is not None]

        print(f"\n  Main diagonal (0,0 → 127,127):")
        print(f"    Sum: {sum(values)}, Mean: {sum(values)/len(values):.2f}")
        print(f"    Min: {min(values)}, Max: {max(values)}")

        # Count CFB numbers on diagonal
        cfb_on_diag = sum(1 for v in values if v in CFB_NUMBERS)
        if cfb_on_diag > 0:
            print(f"    CFB numbers on diagonal: {cfb_on_diag}")

        # Anti-diagonal (0,127) to (127,0)
        anti_diag = self.scanner.scan_diagonal(0, 127, 'down-left')
        anti_values = [v for _, v in anti_diag if v is not None]

        print(f"\n  Anti-diagonal (0,127 → 127,0):")
        print(f"    Sum: {sum(anti_values)}, Mean: {sum(anti_values)/len(anti_values):.2f}")
        print(f"    Min: {min(anti_values)}, Max: {max(anti_values)}")

        # Check for symmetry
        if values == anti_values:
            self.log_discovery('diagonal_symmetry', 'Main and anti-diagonal are identical', {})
        elif values == anti_values[::-1]:
            self.log_discovery('diagonal_symmetry', 'Diagonals are mirror images', {})

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 7: Known Coordinates Deep Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def scan_known_coordinates(self):
        """Deep analysis of known significant coordinates"""
        print("\n" + "─" * 70)
        print("SCAN 7: KNOWN COORDINATES DEEP ANALYSIS")
        print("─" * 70)

        for (row, col), description in KNOWN_COORDINATES.items():
            value = self.matrix.query(row, col)
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)

            print(f"\n  {description}:")
            print(f"    Matrix[{row},{col}] = {value}")
            print(f"    Anna({anna_x:+d},{anna_y:+d}) = {value}")

            # Get neighbors
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (row + dr) % 128, (col + dc) % 128
                    nv = self.matrix.query(nr, nc)
                    neighbors.append(nv)

            print(f"    Neighbors: {neighbors}")
            print(f"    Neighbor sum: {sum(n for n in neighbors if n is not None)}")

            # Check if value is a CFB number
            if value in CFB_NUMBERS:
                self.log_discovery('known_cfb', f'{description} has CFB value {value}', {
                    'coordinate': (row, col),
                    'value': value,
                    'description': description
                })

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 8: XOR Layer Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def scan_xor_layers(self):
        """Analyze XOR transformations of the matrix"""
        print("\n" + "─" * 70)
        print("SCAN 8: XOR LAYER ANALYSIS")
        print("─" * 70)

        xor_keys = [0, 7, 13, 27, 33, 37, 42, 127]

        for key in xor_keys:
            # XOR all values with key
            xor_values = []
            cfb_count = 0

            for row in range(128):
                for col in range(128):
                    v = self.matrix.query(row, col)
                    if v is not None:
                        xored = v ^ key if v >= 0 else -((-v) ^ key)
                        xor_values.append(xored)
                        if xored in CFB_NUMBERS or -xored in CFB_NUMBERS:
                            cfb_count += 1

            print(f"\n  XOR with {key}:")
            print(f"    CFB number hits: {cfb_count}")
            print(f"    Sum: {sum(xor_values)}")

    # ───────────────────────────────────────────────────────────────────────────
    # SCAN 9: Date-based Analysis
    # ───────────────────────────────────────────────────────────────────────────

    def scan_important_dates(self):
        """Check important dates in crypto history"""
        print("\n" + "─" * 70)
        print("SCAN 9: IMPORTANT DATES ANALYSIS")
        print("─" * 70)

        important_dates = [
            ("2008-08-18", "bitcoin.org registered"),
            ("2008-10-31", "Bitcoin whitepaper"),
            ("2009-01-03", "Genesis block"),
            ("2009-01-09", "Bitcoin v0.1 released"),
            ("2009-01-12", "First BTC transaction"),
            ("2010-05-22", "Bitcoin Pizza Day"),
            ("2012-11-28", "First halving"),
            ("2013-11-24", "NXT announced"),
            ("2017-06-11", "IOTA launch"),
            ("2018-04-01", "Qubic announced"),
        ]

        for date_str, event in important_dates:
            row, col = Encoders.date_to_coords(date_str)
            value = self.matrix.query(row, col)

            sig_marker = ""
            if value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS):
                sig_marker = " ★★★ CFB NUMBER!"
                self.log_discovery('date_cfb', f'{event} ({date_str}) -> {value}', {
                    'date': date_str,
                    'event': event,
                    'value': value
                })
            elif (row, col) in KNOWN_COORDINATES:
                sig_marker = f" ★ {KNOWN_COORDINATES[(row, col)]}"

            print(f"  {date_str} ({event}):")
            print(f"    [{row:3d},{col:3d}] = {value}{sig_marker}")

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL SCANS
    # ───────────────────────────────────────────────────────────────────────────

    def run_all_scans(self):
        """Execute all systematic scans"""
        print("\n" + "═" * 70)
        print("           BEGINNING SYSTEMATIC EXPLORATION")
        print("═" * 70)

        self.scan_cfb_numbers()
        self.scan_block_timestamps()
        self.scan_cfb_strings()
        self.scan_strategic_addresses()
        self.scan_patoshi_patterns()
        self.scan_diagonals()
        self.scan_known_coordinates()
        self.scan_xor_layers()
        self.scan_important_dates()

        # Summary
        print("\n" + "═" * 70)
        print("           EXPLORATION COMPLETE")
        print("═" * 70)

        print(f"\n  Total discoveries: {len(self.results['discoveries'])}")

        if self.results['discoveries']:
            print("\n  DISCOVERY SUMMARY:")
            for d in self.results['discoveries']:
                print(f"    [{d['category']}] {d['description']}")

        # Save results
        output_file = RESULTS_DIR / f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

        return self.results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    explorer = SystematicExplorer()
    explorer.run_all_scans()
