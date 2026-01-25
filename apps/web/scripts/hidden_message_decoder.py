#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    HIDDEN MESSAGE DECODER                                      ║
║                                                                                ║
║  Deep search for hidden messages and signatures in Anna Matrix                 ║
║  - Strategic coordinate paths                                                  ║
║  - ASCII encoding analysis                                                     ║
║  - CFB signature mapping                                                       ║
║  - Genesis/Satoshi pattern discovery                                           ║
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
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
GENESIS_PUBKEY = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"

# Strategic coordinates discovered in previous research
STRATEGIC_COORDS = {
    'origin': (0, 0),
    'core_pocc': (6, 33),
    'genesis_entry': (45, 92),
    'bridge_exit': (82, 39),
    'memory_sector': (21, 21),
    'vision_center': (64, 64),
    'anna_center': (63, 63),
    'edge_boundary': (127, 127),
    'genesis_27_cell': (0, 2),  # Position giving -27 in Genesis
    'block9_27': (20, 127),     # Block 9 timestamp → 27
}

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

    def get_row(self, row: int) -> List[int]:
        return [self.query(row, c) for c in range(128)]

    def get_col(self, col: int) -> List[int]:
        return [self.query(r, col) for r in range(128)]

    def get_diagonal(self, start_row: int, start_col: int, direction: int = 1) -> List[int]:
        """Get diagonal values. direction: 1 for \, -1 for /"""
        values = []
        for i in range(128):
            r = (start_row + i) % 128
            c = (start_col + i * direction) % 128
            values.append(self.query(r, c))
        return values

# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGE DECODER
# ═══════════════════════════════════════════════════════════════════════════════

class HiddenMessageDecoder:
    def __init__(self):
        print("═" * 70)
        print("           HIDDEN MESSAGE DECODER")
        print("═" * 70)
        self.matrix = Matrix()
        self.discoveries = []

    def log_discovery(self, title: str, data: dict):
        self.discoveries.append({'title': title, 'data': data})
        print(f"\n  ★★★ {title}")
        for k, v in list(data.items())[:5]:
            val_str = str(v)[:60] + "..." if len(str(v)) > 60 else str(v)
            print(f"      {k}: {val_str}")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 1: PATH ANALYSIS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_strategic_paths(self):
        """Analyze paths between all strategic coordinates"""
        print("\n" + "═" * 70)
        print("PHASE 1: STRATEGIC PATH ANALYSIS")
        print("═" * 70)

        coord_names = list(STRATEGIC_COORDS.keys())

        for i, name1 in enumerate(coord_names):
            for name2 in coord_names[i+1:]:
                coord1 = STRATEGIC_COORDS[name1]
                coord2 = STRATEGIC_COORDS[name2]

                path_values = self._get_path_values(coord1, coord2)
                if not path_values:
                    continue

                # Calculate various aggregations
                path_sum = sum(v for v in path_values if v is not None)
                valid_values = [v for v in path_values if v is not None]

                if not valid_values:
                    continue

                path_xor = valid_values[0]
                for v in valid_values[1:]:
                    path_xor ^= v

                # Check for CFB numbers
                is_cfb_sum = path_sum in CFB_NUMBERS or -path_sum in CFB_NUMBERS
                is_cfb_xor = path_xor in CFB_NUMBERS

                if is_cfb_sum or is_cfb_xor:
                    self.log_discovery(f'Path {name1} → {name2} encodes CFB', {
                        'from': name1,
                        'to': name2,
                        'length': len(valid_values),
                        'sum': path_sum,
                        'sum_is_cfb': is_cfb_sum,
                        'xor': path_xor,
                        'xor_is_cfb': is_cfb_xor
                    })

                # Check for ASCII message
                ascii_chars = []
                for v in valid_values:
                    # Try different offsets to get printable ASCII
                    for offset in [0, 32, 64, 96, 128]:
                        char_code = (v + offset) % 256
                        if 32 <= char_code <= 126:
                            ascii_chars.append(chr(char_code))
                            break

                if len(ascii_chars) > 3:
                    message = ''.join(ascii_chars)
                    # Check for meaningful substrings
                    meaningful = ['CFB', 'SAT', 'BTC', 'KEY', 'GEN', 'QUB', 'ANN']
                    for m in meaningful:
                        if m.lower() in message.lower():
                            self.log_discovery(f'Meaningful pattern in {name1}→{name2}', {
                                'pattern': m,
                                'message': message
                            })

    def _get_path_values(self, coord1: Tuple[int, int], coord2: Tuple[int, int]) -> List[int]:
        """Get matrix values along path between two coordinates"""
        r1, c1 = coord1
        r2, c2 = coord2
        steps = max(abs(r2 - r1), abs(c2 - c1))

        if steps == 0:
            return [self.matrix.query(r1, c1)]

        values = []
        for i in range(steps + 1):
            r = r1 + (r2 - r1) * i // steps
            c = c1 + (c2 - c1) * i // steps
            values.append(self.matrix.query(r, c))

        return values

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 2: SIGNATURE ROWS AND COLUMNS
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_signature_lines(self):
        """Analyze rows and columns at CFB number positions"""
        print("\n" + "═" * 70)
        print("PHASE 2: SIGNATURE ROW/COLUMN ANALYSIS")
        print("═" * 70)

        # Analyze rows and columns at CFB positions
        for cfb in CFB_NUMBERS:
            if cfb < 128:
                # Row analysis
                row_values = self.matrix.get_row(cfb)
                row_sum = sum(v for v in row_values if v is not None)
                row_valid = [v for v in row_values if v is not None]

                print(f"\n  Row {cfb} (CFB number):")
                print(f"    Sum: {row_sum}")
                print(f"    Mean: {row_sum / len(row_valid):.2f}")

                # Check for hidden patterns
                cfb_count = sum(1 for v in row_valid if v in CFB_NUMBERS or -v in CFB_NUMBERS)
                print(f"    CFB values in row: {cfb_count}")

                if row_sum in CFB_NUMBERS or -row_sum in CFB_NUMBERS:
                    self.log_discovery(f'Row {cfb} sum is CFB number', {
                        'row': cfb,
                        'sum': row_sum
                    })

                # Column analysis
                col_values = self.matrix.get_col(cfb)
                col_sum = sum(v for v in col_values if v is not None)
                col_valid = [v for v in col_values if v is not None]

                print(f"\n  Column {cfb} (CFB number):")
                print(f"    Sum: {col_sum}")
                print(f"    Mean: {col_sum / len(col_valid):.2f}")

                cfb_count = sum(1 for v in col_valid if v in CFB_NUMBERS or -v in CFB_NUMBERS)
                print(f"    CFB values in column: {cfb_count}")

        # Diagonal through (27, 27)
        print("\n  Diagonal through (27, 27):")
        diag_values = self.matrix.get_diagonal(0, 0, 1)  # Main diagonal
        diag_sum = sum(v for v in diag_values if v is not None)
        print(f"    Main diagonal sum: {diag_sum}")
        print(f"    Value at (27, 27): {self.matrix.query(27, 27)}")

        # Check if (27, 27) value is special
        v_27_27 = self.matrix.query(27, 27)
        if v_27_27 is not None:
            print(f"\n  Analysis of cell (27, 27):")
            print(f"    Value: {v_27_27}")

            # Check neighbors
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nv = self.matrix.query(27 + dr, 27 + dc)
                    if nv is not None:
                        neighbors.append(nv)

            n_sum = sum(neighbors)
            n_xor = neighbors[0]
            for n in neighbors[1:]:
                n_xor ^= n

            print(f"    Neighbor sum: {n_sum}")
            print(f"    Neighbor XOR: {n_xor}")

            if n_sum in CFB_NUMBERS or n_xor in CFB_NUMBERS:
                self.log_discovery('(27,27) neighbors encode CFB', {
                    'neighbors': neighbors,
                    'sum': n_sum,
                    'xor': n_xor
                })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 3: ASCII MESSAGE SEARCH
    # ───────────────────────────────────────────────────────────────────────────

    def search_ascii_messages(self):
        """Search for ASCII messages hidden in the matrix"""
        print("\n" + "═" * 70)
        print("PHASE 3: ASCII MESSAGE SEARCH")
        print("═" * 70)

        # Known strings to search for
        search_strings = [
            "CFB",
            "SATOSHI",
            "NAKAMOTO",
            "BITCOIN",
            "GENESIS",
            "QUBIC",
            "IOTA",
            "NXT",
            "JINN",
            "ANNA",
            "KEY",
            "BRIDGE",
        ]

        # Method 1: Row-by-row ASCII interpretation
        print("\n  Searching rows for ASCII patterns...")
        for row in range(128):
            row_values = self.matrix.get_row(row)

            # Try different ASCII offsets
            for offset in [32, 64, 96, 128]:
                chars = []
                for v in row_values:
                    if v is not None:
                        char_code = (v + offset) % 256
                        if 32 <= char_code <= 126:
                            chars.append(chr(char_code))
                        else:
                            chars.append(' ')

                message = ''.join(chars).strip()
                for s in search_strings:
                    if s.lower() in message.lower():
                        self.log_discovery(f'Found "{s}" in row {row}', {
                            'row': row,
                            'offset': offset,
                            'message': message[:50]
                        })

        # Method 2: Hash-based coordinate lookup
        print("\n  Searching for strings via hash coordinates...")
        for s in search_strings:
            h = hashlib.sha256(s.encode()).digest()
            row, col = h[0] % 128, h[1] % 128
            value = self.matrix.query(row, col)

            is_cfb = value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS)
            marker = " ★ CFB!" if is_cfb else ""

            print(f"    \"{s}\" → [{row:3d},{col:3d}] = {value}{marker}")

            if is_cfb:
                self.log_discovery(f'"{s}" hashes to CFB value', {
                    'string': s,
                    'coords': (row, col),
                    'value': value
                })

        # Method 3: Genesis address letter by letter
        print("\n  Analyzing Genesis address letter positions...")
        for i, char in enumerate(GENESIS_ADDRESS):
            pos = BASE58_ALPHABET.index(char) if char in BASE58_ALPHABET else 0
            row, col = pos % 128, i % 128
            value = self.matrix.query(row, col)

            if value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS):
                print(f"    Position {i}: '{char}' (pos={pos}) → [{row},{col}] = {value} ★ CFB")

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 4: COORDINATE ARITHMETIC
    # ───────────────────────────────────────────────────────────────────────────

    def analyze_coordinate_arithmetic(self):
        """Find CFB numbers through coordinate arithmetic"""
        print("\n" + "═" * 70)
        print("PHASE 4: COORDINATE ARITHMETIC")
        print("═" * 70)

        coord_names = list(STRATEGIC_COORDS.keys())

        print("\n  Coordinate pair operations:")
        for i, name1 in enumerate(coord_names):
            for name2 in coord_names[i+1:]:
                r1, c1 = STRATEGIC_COORDS[name1]
                r2, c2 = STRATEGIC_COORDS[name2]

                v1 = self.matrix.query(r1, c1)
                v2 = self.matrix.query(r2, c2)

                if v1 is None or v2 is None:
                    continue

                # Try various operations
                operations = {
                    'sum': v1 + v2,
                    'diff': abs(v1 - v2),
                    'xor': v1 ^ v2,
                    'product_mod': (v1 * v2) % 127,
                }

                for op, result in operations.items():
                    if result in CFB_NUMBERS:
                        print(f"    {name1} {op} {name2} = {result} ★ CFB")
                        self.log_discovery(f'{name1} {op} {name2} = CFB', {
                            'coord1': (r1, c1),
                            'coord2': (r2, c2),
                            'v1': v1,
                            'v2': v2,
                            'operation': op,
                            'result': result
                        })

        # Check genesis-related calculations
        print("\n  Genesis-specific calculations:")

        # Genesis pubkey first 32 bytes → matrix
        pubkey_bytes = bytes.fromhex(GENESIS_PUBKEY)
        pubkey_sum = sum(pubkey_bytes)
        print(f"    Genesis pubkey byte sum: {pubkey_sum}")
        print(f"    Pubkey sum mod 127: {pubkey_sum % 127}")

        if pubkey_sum % 127 in CFB_NUMBERS:
            self.log_discovery('Genesis pubkey sum mod 127 is CFB', {
                'sum': pubkey_sum,
                'mod_127': pubkey_sum % 127
            })

        # Map pubkey sum to matrix
        row, col = (pubkey_sum // 128) % 128, pubkey_sum % 128
        value = self.matrix.query(row, col)
        print(f"    Pubkey sum → [{row},{col}] = {value}")

        if value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS):
            self.log_discovery('Genesis pubkey sum maps to CFB', {
                'coords': (row, col),
                'value': value
            })

    # ───────────────────────────────────────────────────────────────────────────
    # PHASE 5: CFB SIGNATURE MAP
    # ───────────────────────────────────────────────────────────────────────────

    def build_cfb_signature_map(self):
        """Build comprehensive map of all CFB number occurrences"""
        print("\n" + "═" * 70)
        print("PHASE 5: CFB SIGNATURE MAP")
        print("═" * 70)

        cfb_map = {}

        for target in CFB_NUMBERS:
            # Find all cells with this value (positive and negative)
            positive_cells = []
            negative_cells = []

            for row in range(128):
                for col in range(128):
                    v = self.matrix.query(row, col)
                    if v == target:
                        positive_cells.append((row, col))
                    elif v == -target:
                        negative_cells.append((row, col))

            cfb_map[target] = {
                'positive': positive_cells,
                'negative': negative_cells,
                'total': len(positive_cells) + len(negative_cells)
            }

            print(f"\n  CFB Number {target}:")
            print(f"    +{target}: {len(positive_cells)} cells")
            print(f"    -{target}: {len(negative_cells)} cells")

            # Check for geometric patterns
            if positive_cells:
                rows = [c[0] for c in positive_cells]
                cols = [c[1] for c in positive_cells]

                # Row/col range
                row_range = max(rows) - min(rows)
                col_range = max(cols) - min(cols)
                print(f"    +{target} row span: {min(rows)}-{max(rows)} (range: {row_range})")
                print(f"    +{target} col span: {min(cols)}-{max(cols)} (range: {col_range})")

                # Check if range is CFB number
                if row_range in CFB_NUMBERS or col_range in CFB_NUMBERS:
                    self.log_discovery(f'{target} cell range is CFB', {
                        'value': target,
                        'row_range': row_range,
                        'col_range': col_range
                    })

        # Check connectivity
        print("\n  CFB cell connectivity:")
        for target in [27]:  # Focus on 27
            cells = cfb_map[target]['positive'] + cfb_map[target]['negative']
            if len(cells) < 2:
                continue

            # Find pairs that are adjacent
            adjacent_pairs = []
            for i, (r1, c1) in enumerate(cells):
                for r2, c2 in cells[i+1:]:
                    dist = abs(r2 - r1) + abs(c2 - c1)
                    if dist <= 2:
                        adjacent_pairs.append(((r1, c1), (r2, c2)))

            print(f"    Adjacent ±{target} cell pairs: {len(adjacent_pairs)}")

        return cfb_map

    # ───────────────────────────────────────────────────────────────────────────
    # RUN ALL
    # ───────────────────────────────────────────────────────────────────────────

    def run_all(self):
        """Execute all analyses"""
        self.analyze_strategic_paths()
        self.analyze_signature_lines()
        self.search_ascii_messages()
        self.analyze_coordinate_arithmetic()
        cfb_map = self.build_cfb_signature_map()

        # Summary
        print("\n" + "═" * 70)
        print("           DECODING COMPLETE")
        print("═" * 70)

        print(f"\n  Total discoveries: {len(self.discoveries)}")

        if self.discoveries:
            print("\n  DISCOVERIES:")
            for d in self.discoveries:
                print(f"    ★ {d['title']}")

        # Save results
        output = {
            'timestamp': datetime.now().isoformat(),
            'discoveries': self.discoveries,
            'cfb_map': cfb_map
        }

        output_file = SCRIPT_DIR / 'hidden_message_decoder_results.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Results saved to: {output_file}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    decoder = HiddenMessageDecoder()
    decoder.run_all()
