#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DISCOVER MORE PATTERNS                                      ║
║                                                                                ║
║  Continue deep exploration of the Anna Matrix                                  ║
║  - Find more string → CFB correlations                                         ║
║  - Analyze special block numbers                                               ║
║  - Map coordinate symmetries                                                   ║
║  - Search for encoded messages                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

CFB_NUMBERS = [27, 37, 42, 127]
CFB_SET = set(CFB_NUMBERS + [-n for n in CFB_NUMBERS])

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX
# ═══════════════════════════════════════════════════════════════════════════════

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
# PATTERN DISCOVERER
# ═══════════════════════════════════════════════════════════════════════════════

class PatternDiscoverer:
    def __init__(self):
        print("═" * 70)
        print("           DISCOVER MORE PATTERNS")
        print("═" * 70)
        self.matrix = Matrix()
        self.discoveries = []

    def log_discovery(self, category: str, title: str, data: dict):
        self.discoveries.append({
            'category': category,
            'title': title,
            'data': data
        })
        print(f"\n  ★★★ [{category.upper()}] {title}")
        for k, v in list(data.items())[:3]:
            val_str = str(v)[:50]
            print(f"      {k}: {val_str}")

    # ───────────────────────────────────────────────────────────────────────────
    # STRING CORRELATIONS
    # ───────────────────────────────────────────────────────────────────────────

    def find_string_correlations(self):
        """Test many strings for CFB correlations"""
        print("\n" + "═" * 70)
        print("PHASE 1: EXTENSIVE STRING TESTING")
        print("═" * 70)

        # Categories of strings to test
        strings_to_test = [
            # People
            "Satoshi", "SATOSHI", "satoshi",
            "Nakamoto", "NAKAMOTO", "nakamoto",
            "Hal Finney", "HAL FINNEY",
            "Nick Szabo", "NICK SZABO",
            "Wei Dai", "WEI DAI",
            "Adam Back", "ADAM BACK",
            "CFB", "Come-from-Beyond", "come-from-beyond",
            "Sergey", "SERGEY", "Ivancheglo", "IVANCHEGLO",
            "Dominik", "DOMINIK", "Schiener", "SCHIENER",
            "David", "DAVID", "Sonstebo", "SONSTEBO",

            # Projects
            "Bitcoin", "BITCOIN", "bitcoin",
            "Qubic", "QUBIC", "qubic",
            "IOTA", "iota", "Iota",
            "NXT", "nxt", "Nxt",
            "JINN", "jinn", "Jinn",
            "Aigarth", "AIGARTH", "aigarth",
            "Anna", "ANNA", "anna",
            "Ethereum", "ETHEREUM",
            "Cardano", "CARDANO",

            # Technical terms
            "genesis", "GENESIS", "Genesis",
            "block", "BLOCK", "Block",
            "hash", "HASH", "Hash",
            "proof", "PROOF", "Proof",
            "work", "WORK", "Work",
            "key", "KEY", "Key",
            "private", "PRIVATE", "Private",
            "public", "PUBLIC", "Public",
            "address", "ADDRESS", "Address",
            "wallet", "WALLET", "Wallet",
            "bridge", "BRIDGE", "Bridge",
            "oracle", "ORACLE", "Oracle",
            "quantum", "QUANTUM", "Quantum",

            # Numbers as strings
            "27", "37", "42", "127", "576",
            "21", "33", "64", "128",
            "2009", "2016", "2024",

            # Phrases
            "The Times 03/Jan/2009",
            "Chancellor on brink",
            "second bailout for banks",
            "In cryptography we trust",
            "Vires in numeris",
            "The revolution will not be televised",

            # Dates
            "2009-01-03", "2009-01-09", "2009-01-12",
            "January 3, 2009",
            "03/Jan/2009",

            # Special strings
            "0x27", "0x42", "0x7f",
            "ASCII", "UTF8", "BASE58",
            "P2PKH", "P2SH", "ECDSA",
            "secp256k1", "SECP256K1",
            "SHA256", "RIPEMD160",

            # More CFB related
            "BCNext", "BCNEXT", "bcnext",
            "NEM", "nem", "Nem",
            "Ardor", "ARDOR", "ardor",
            "Burst", "BURST", "burst",
        ]

        cfb_hits = []
        for s in strings_to_test:
            h = hashlib.sha256(s.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            value = self.matrix.query(row, col)

            if value in CFB_SET:
                cfb_hits.append({
                    'string': s,
                    'coords': (row, col),
                    'value': value
                })
                print(f"    ★ \"{s}\" → [{row},{col}] = {value}")

        print(f"\n  Total CFB hits: {len(cfb_hits)} / {len(strings_to_test)}")

        # Analyze patterns in hits
        if cfb_hits:
            self.log_discovery('strings', f'{len(cfb_hits)} strings hash to CFB', {
                'strings': [h['string'] for h in cfb_hits],
                'values': [h['value'] for h in cfb_hits]
            })

        return cfb_hits

    # ───────────────────────────────────────────────────────────────────────────
    # SYMMETRY ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_symmetries(self):
        """Find symmetries in the matrix"""
        print("\n" + "═" * 70)
        print("PHASE 2: SYMMETRY ANALYSIS")
        print("═" * 70)

        # Check point symmetry around (64, 64)
        print("\n  Checking point symmetry around Vision Center (64,64)...")
        symmetric_count = 0
        anti_symmetric_count = 0

        for row in range(64):
            for col in range(128):
                v1 = self.matrix.query(row, col)
                v2 = self.matrix.query(127 - row, 127 - col)

                if v1 is not None and v2 is not None:
                    if v1 == v2:
                        symmetric_count += 1
                    elif v1 == -v2:
                        anti_symmetric_count += 1

        print(f"    Symmetric pairs (v1 == v2): {symmetric_count}")
        print(f"    Anti-symmetric pairs (v1 == -v2): {anti_symmetric_count}")

        # Check mirror symmetry
        print("\n  Checking horizontal mirror symmetry...")
        h_mirror_count = 0
        for row in range(64):
            for col in range(128):
                v1 = self.matrix.query(row, col)
                v2 = self.matrix.query(127 - row, col)
                if v1 is not None and v2 is not None and v1 == v2:
                    h_mirror_count += 1

        print(f"    Horizontal mirror pairs: {h_mirror_count}")

        # Check for CFB numbers in symmetric positions
        print("\n  CFB numbers in symmetric positions...")
        cfb_27_cells = self.matrix.find_value(27) + self.matrix.find_value(-27)

        symmetric_cfb = []
        for r, c in cfb_27_cells:
            # Check if opposite cell also has CFB
            opp_r, opp_c = 127 - r, 127 - c
            opp_v = self.matrix.query(opp_r, opp_c)
            if opp_v in CFB_SET:
                symmetric_cfb.append({
                    'pos1': (r, c),
                    'pos2': (opp_r, opp_c),
                    'v1': self.matrix.query(r, c),
                    'v2': opp_v
                })

        print(f"    Symmetric CFB pairs: {len(symmetric_cfb)}")

        if len(symmetric_cfb) > 10:
            self.log_discovery('symmetry', f'{len(symmetric_cfb)} symmetric CFB pairs', {
                'count': len(symmetric_cfb),
                'sample': symmetric_cfb[:5]
            })

    # ───────────────────────────────────────────────────────────────────────────
    # BLOCK NUMBER ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_special_blocks(self):
        """Analyze matrix values at special block number coordinates"""
        print("\n" + "═" * 70)
        print("PHASE 3: SPECIAL BLOCK NUMBER ANALYSIS")
        print("═" * 70)

        special_blocks = [
            (0, "Genesis"),
            (1, "First mined block"),
            (9, "First transaction"),
            (27, "CFB number"),
            (37, "CFB number"),
            (42, "CFB number / Answer"),
            (127, "CFB number"),
            (170, "First real transaction"),
            (210000, "First halving"),
            (256, "Power of 2"),
            (512, "Power of 2"),
            (576, "CFB extended"),
            (1000, "Milestone"),
        ]

        print("\n  Block numbers as matrix coordinates:")
        cfb_block_hits = []

        for block, desc in special_blocks:
            # Various encodings of block number
            encodings = {
                'direct': (block % 128, 0),
                'split': (block % 128, (block // 128) % 128),
                'reversed': (0, block % 128),
                'both': (block % 128, block % 128),
            }

            for method, (row, col) in encodings.items():
                value = self.matrix.query(row, col)
                is_cfb = value in CFB_SET if value else False

                if is_cfb:
                    cfb_block_hits.append({
                        'block': block,
                        'desc': desc,
                        'method': method,
                        'coords': (row, col),
                        'value': value
                    })
                    print(f"    ★ Block {block} ({desc}) [{method}]: [{row},{col}] = {value}")

        print(f"\n  CFB hits from block numbers: {len(cfb_block_hits)}")

        if cfb_block_hits:
            self.log_discovery('blocks', f'{len(cfb_block_hits)} block numbers encode CFB', {
                'hits': cfb_block_hits
            })

    # ───────────────────────────────────────────────────────────────────────────
    # ROW/COLUMN SUM PATTERNS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_row_column_sums(self):
        """Find rows/columns with CFB-related sums"""
        print("\n" + "═" * 70)
        print("PHASE 4: ROW/COLUMN SUM ANALYSIS")
        print("═" * 70)

        row_sums = []
        col_sums = []

        for i in range(128):
            row_vals = [self.matrix.query(i, j) for j in range(128)]
            row_sum = sum(v for v in row_vals if v is not None)
            row_sums.append((i, row_sum))

            col_vals = [self.matrix.query(j, i) for j in range(128)]
            col_sum = sum(v for v in col_vals if v is not None)
            col_sums.append((i, col_sum))

        # Find rows with CFB sums or CFB mod patterns
        print("\n  Rows with CFB-related sums:")
        for row, s in row_sums:
            if s in CFB_SET:
                print(f"    Row {row}: sum = {s} ★ direct CFB")
            elif s % 27 == 0 and s != 0:
                print(f"    Row {row}: sum = {s} (divisible by 27)")
            elif s % 37 == 0 and s != 0:
                print(f"    Row {row}: sum = {s} (divisible by 37)")
            elif abs(s) % 127 == 0 and s != 0:
                print(f"    Row {row}: sum = {s} (divisible by 127)")

        # Check if any row sum equals another CFB number
        print("\n  Row sums that equal block heights:")
        interesting_sums = [s for _, s in row_sums if 0 < s < 50000]
        for row, s in row_sums:
            if s == 21000 or s == 2100:  # Bitcoin supply related
                print(f"    Row {row}: sum = {s} ★ Bitcoin supply related")
            if s in [2009, 2016, 2024]:  # Years
                print(f"    Row {row}: sum = {s} ★ Year")

    # ───────────────────────────────────────────────────────────────────────────
    # DIAGONAL MESSAGES
    # ───────────────────────────────────────────────────────────────────────────

    def search_diagonal_messages(self):
        """Search for messages in diagonals"""
        print("\n" + "═" * 70)
        print("PHASE 5: DIAGONAL MESSAGE SEARCH")
        print("═" * 70)

        # Main diagonal (0,0) to (127,127)
        main_diag = [self.matrix.query(i, i) for i in range(128)]

        # Anti-diagonal (0,127) to (127,0)
        anti_diag = [self.matrix.query(i, 127-i) for i in range(128)]

        # Diagonal through (27, 27)
        diag_27 = [self.matrix.query(i, (i + 27 - 27) % 128) for i in range(128)]

        diagonals = [
            ('main', main_diag),
            ('anti', anti_diag),
            ('through_27', diag_27),
        ]

        print("\n  Diagonal CFB analysis:")
        for name, diag in diagonals:
            cfb_count = sum(1 for v in diag if v in CFB_SET)
            diag_sum = sum(v for v in diag if v is not None)
            print(f"    {name}: {cfb_count} CFB values, sum = {diag_sum}")

            if diag_sum in CFB_SET:
                self.log_discovery('diagonal', f'{name} diagonal sum is CFB', {
                    'diagonal': name,
                    'sum': diag_sum
                })

        # Try to decode as ASCII
        print("\n  Diagonal ASCII attempts:")
        for name, diag in diagonals:
            chars = []
            for v in diag:
                if v is not None:
                    c = (v + 128) % 256
                    if 32 <= c <= 126:
                        chars.append(chr(c))
                    else:
                        chars.append('.')

            message = ''.join(chars)
            # Look for readable substrings
            readable = []
            current = ""
            for c in message:
                if c != '.':
                    current += c
                else:
                    if len(current) >= 3:
                        readable.append(current)
                    current = ""

            if readable:
                print(f"    {name}: readable fragments: {readable[:5]}")

    # ───────────────────────────────────────────────────────────────────────────
    # XOR ALGEBRA
    # ───────────────────────────────────────────────────────────────────────────

    def explore_xor_algebra(self):
        """Find algebraic relationships via XOR"""
        print("\n" + "═" * 70)
        print("PHASE 6: XOR ALGEBRA")
        print("═" * 70)

        # Known important cells
        important_cells = {
            'genesis_27': (0, 2),
            'block9_27': (20, 127),
            'vision': (64, 64),
            'anna': (63, 63),
            'core': (6, 33),
            'memory': (21, 21),
            'block27': (81, 28),
        }

        print("\n  XOR combinations of important cells:")
        cell_values = {name: self.matrix.query(r, c) for name, (r, c) in important_cells.items()}

        for n1, v1 in cell_values.items():
            for n2, v2 in cell_values.items():
                if n1 >= n2 or v1 is None or v2 is None:
                    continue

                xor = v1 ^ v2
                if xor in CFB_SET:
                    print(f"    {n1} XOR {n2} = {v1} ^ {v2} = {xor} ★ CFB")
                    self.log_discovery('xor_algebra', f'{n1} XOR {n2} = {xor}', {
                        'cell1': n1,
                        'cell2': n2,
                        'v1': v1,
                        'v2': v2,
                        'xor': xor
                    })

        # Find cells that XOR with vision center to give CFB
        print("\n  Cells that XOR with Vision Center (64,64) to give CFB:")
        vision_val = self.matrix.query(64, 64)  # -70

        for row in range(128):
            for col in range(128):
                v = self.matrix.query(row, col)
                if v is not None:
                    xor = vision_val ^ v
                    if xor in CFB_SET:
                        print(f"    [{row},{col}] = {v}: {vision_val} ^ {v} = {xor}")

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self):
        """Execute all explorations"""
        self.find_string_correlations()
        self.analyze_symmetries()
        self.analyze_special_blocks()
        self.analyze_row_column_sums()
        self.search_diagonal_messages()
        self.explore_xor_algebra()

        # Summary
        print("\n" + "═" * 70)
        print("           DISCOVERY SUMMARY")
        print("═" * 70)

        print(f"\n  Total discoveries: {len(self.discoveries)}")

        if self.discoveries:
            print("\n  ALL DISCOVERIES:")
            for d in self.discoveries:
                print(f"    ★ [{d['category']}] {d['title']}")

        # Save
        output = {
            'timestamp': datetime.now().isoformat(),
            'discoveries': self.discoveries
        }

        output_file = SCRIPT_DIR / 'more_patterns_results.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    discoverer = PatternDiscoverer()
    discoverer.run_all()
