#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ANNA RESEARCH TERMINAL v1.0                           ║
║                                                                               ║
║  Systematische Erforschung der Anna Matrix (128×128)                          ║
║  - Verschiedene Encoding-Methoden (BTC, Seed, Timestamp, Hash)                ║
║  - Pattern Scanner (Diagonalen, Spiralen, Value Search)                       ║
║  - Blockchain Korrelation                                                     ║
║  - Interaktives CLI                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
import os
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"
PATOSHI_FILE = DATA_DIR / "patoshi-addresses.json"

# Known special coordinates from research
KNOWN_COORDINATES = {
    (6, 33): "Core Computor / POCC",
    (45, 92): "CFB Genesis Entry",
    (82, 39): "Bridge Exit Node",
    (21, 21): "Memory Sector",
    (64, 64): "Vision Center",
    (0, 0): "Origin/Void",
    (127, 127): "Edge/Boundary",
    (63, 63): "Anna Center (0,0)",
}

# CFB's special numbers
CFB_NUMBERS = [27, 37, 42, 127, 576]

# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QueryResult:
    """Result of an Anna query"""
    row: int
    col: int
    anna_x: int  # -64 to 63
    anna_y: int  # 63 to -64
    value: int
    encoding_method: str
    input_data: str
    significance: Optional[str] = None

@dataclass
class PatternMatch:
    """A pattern found in the matrix"""
    pattern_type: str
    coordinates: List[Tuple[int, int]]
    values: List[int]
    description: str

# ═══════════════════════════════════════════════════════════════════════════════
# ANNA MATRIX CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class AnnaMatrix:
    """Anna's 128×128 neural weight matrix"""

    def __init__(self, matrix_path: Path = MATRIX_FILE):
        self.matrix: List[List[int]] = []
        self.load_matrix(matrix_path)

    def load_matrix(self, path: Path):
        """Load the Anna Matrix from JSON"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                self.matrix = data
            elif isinstance(data, dict) and 'matrix' in data:
                self.matrix = data['matrix']
            else:
                raise ValueError("Unknown matrix format")

            print(f"✓ Loaded Anna Matrix: {len(self.matrix)}×{len(self.matrix[0])}")

        except FileNotFoundError:
            print(f"✗ Matrix file not found: {path}")
            print("  Generating demo matrix...")
            self.matrix = [[((i*j) % 255) - 127 for j in range(128)] for i in range(128)]

    def query(self, row: int, col: int) -> Optional[int]:
        """Query Anna at matrix coordinates [row, col]"""
        # Wrap coordinates
        row = row % 128
        col = col % 128
        value = self.matrix[row][col]
        # Handle special values like '00000000'
        if isinstance(value, int):
            return value
        return None  # Special/undefined value

    def query_anna_coords(self, x: int, y: int) -> int:
        """Query using Anna's coordinate system (x: -64..63, y: 63..-64)"""
        col = (x + 64) % 128
        row = (63 - y) % 128
        return self.matrix[row][col]

    def matrix_to_anna(self, row: int, col: int) -> Tuple[int, int]:
        """Convert matrix coords to Anna coords"""
        x = col - 64
        y = 63 - row
        return (x, y)

    def anna_to_matrix(self, x: int, y: int) -> Tuple[int, int]:
        """Convert Anna coords to matrix coords"""
        col = (x + 64) % 128
        row = (63 - y) % 128
        return (row, col)

    def find_value(self, value: int) -> List[Tuple[int, int]]:
        """Find all cells with a specific value"""
        results = []
        for row in range(128):
            for col in range(128):
                if self.matrix[row][col] == value:
                    results.append((row, col))
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get matrix statistics"""
        # Filter out non-integer values (like '00000000' special values)
        all_values = []
        special_values = 0
        for row in self.matrix:
            for v in row:
                if isinstance(v, int):
                    all_values.append(v)
                else:
                    special_values += 1

        if not all_values:
            return {'error': 'No integer values in matrix'}

        return {
            'min': min(all_values),
            'max': max(all_values),
            'mean': sum(all_values) / len(all_values),
            'zeros': all_values.count(0),
            'positive': sum(1 for v in all_values if v > 0),
            'negative': sum(1 for v in all_values if v < 0),
            'unique_values': len(set(all_values)),
            'special_values': special_values,
            'total_cells': len(all_values) + special_values,
        }

# ═══════════════════════════════════════════════════════════════════════════════
# ENCODING METHODS
# ═══════════════════════════════════════════════════════════════════════════════

class Encoders:
    """Various methods to convert input data to matrix coordinates"""

    @staticmethod
    def sha256(data: str) -> bytes:
        """SHA256 hash of string"""
        return hashlib.sha256(data.encode()).digest()

    @staticmethod
    def sha256_to_coords(data: str) -> Tuple[int, int]:
        """Hash data and extract coordinates from first 2 bytes"""
        h = Encoders.sha256(data)
        row = h[0] % 128
        col = h[1] % 128
        return (row, col)

    @staticmethod
    def double_sha256_to_coords(data: str) -> Tuple[int, int]:
        """Double SHA256 (Bitcoin style)"""
        h1 = hashlib.sha256(data.encode()).digest()
        h2 = hashlib.sha256(h1).digest()
        return (h2[0] % 128, h2[1] % 128)

    @staticmethod
    def btc_address_to_coords(address: str) -> Tuple[int, int]:
        """Bitcoin address to coordinates"""
        return Encoders.sha256_to_coords(address)

    @staticmethod
    def qubic_seed_to_coords(seed: str) -> Tuple[int, int]:
        """Qubic seed (55 lowercase letters) to coordinates"""
        # K12 would be better, but SHA256 as fallback
        return Encoders.sha256_to_coords(seed)

    @staticmethod
    def timestamp_to_coords(ts: int) -> Tuple[int, int]:
        """Unix timestamp to coordinates"""
        row = (ts // 128) % 128  # Higher bits
        col = ts % 128           # Lower bits
        return (row, col)

    @staticmethod
    def timestamp_direct(ts: int) -> Tuple[int, int]:
        """Direct timestamp mod 128"""
        return (ts % 128, (ts // 128) % 128)

    @staticmethod
    def block_height_to_coords(height: int) -> Tuple[int, int]:
        """Bitcoin block height to coordinates"""
        return (height % 128, (height // 128) % 128)

    @staticmethod
    def xor_with_key(data: bytes, key: bytes) -> bytes:
        """XOR data with key (repeating key if needed)"""
        return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))

    @staticmethod
    def hex_to_coords(hex_str: str) -> Tuple[int, int]:
        """Hex string to coordinates (first 2 bytes)"""
        data = bytes.fromhex(hex_str[:64])  # Max 32 bytes
        return (data[0] % 128, data[1] % 128)

    @staticmethod
    def ascii_sum_to_coords(text: str) -> Tuple[int, int]:
        """Sum of ASCII values to coordinates"""
        total = sum(ord(c) for c in text)
        return (total % 128, (total // 128) % 128)

    @staticmethod
    def date_to_coords(date_str: str) -> Tuple[int, int]:
        """Date string (YYYY-MM-DD) to coordinates"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            ts = int(dt.timestamp())
            return Encoders.timestamp_to_coords(ts)
        except ValueError:
            return (0, 0)

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

class PatternScanner:
    """Scan the Anna Matrix for patterns"""

    def __init__(self, matrix: AnnaMatrix):
        self.matrix = matrix

    def scan_row(self, row: int) -> List[int]:
        """Get all values in a row"""
        return [self.matrix.query(row, col) for col in range(128)]

    def scan_col(self, col: int) -> List[int]:
        """Get all values in a column"""
        return [self.matrix.query(row, col) for row in range(128)]

    def scan_diagonal(self, start_row: int = 0, start_col: int = 0, direction: str = 'down-right') -> List[Tuple[Tuple[int, int], int]]:
        """Scan diagonal from start position"""
        results = []
        row, col = start_row, start_col

        while 0 <= row < 128 and 0 <= col < 128:
            results.append(((row, col), self.matrix.query(row, col)))

            if direction == 'down-right':
                row += 1
                col += 1
            elif direction == 'down-left':
                row += 1
                col -= 1
            elif direction == 'up-right':
                row -= 1
                col += 1
            else:  # up-left
                row -= 1
                col -= 1

        return results

    def scan_spiral(self, center_row: int = 63, center_col: int = 64, max_radius: int = 64) -> List[Tuple[Tuple[int, int], int]]:
        """Spiral scan from center outward"""
        results = []
        row, col = center_row, center_col

        # Add center
        results.append(((row, col), self.matrix.query(row, col)))

        # Spiral outward
        for radius in range(1, max_radius):
            # Top row
            for c in range(col - radius, col + radius + 1):
                if 0 <= center_row - radius < 128 and 0 <= c < 128:
                    r = center_row - radius
                    results.append(((r, c), self.matrix.query(r, c)))

            # Right column
            for r in range(center_row - radius + 1, center_row + radius):
                if 0 <= r < 128 and 0 <= col + radius < 128:
                    results.append(((r, col + radius), self.matrix.query(r, col + radius)))

            # Bottom row
            for c in range(col + radius, col - radius - 1, -1):
                if 0 <= center_row + radius < 128 and 0 <= c < 128:
                    r = center_row + radius
                    results.append(((r, c), self.matrix.query(r, c)))

            # Left column
            for r in range(center_row + radius - 1, center_row - radius, -1):
                if 0 <= r < 128 and 0 <= col - radius < 128:
                    results.append(((r, col - radius), self.matrix.query(r, col - radius)))

        return results

    def find_repeating_sequences(self, min_length: int = 3) -> List[PatternMatch]:
        """Find repeating value sequences in rows/columns"""
        patterns = []

        # Check rows
        for row in range(128):
            values = self.scan_row(row)
            seq_start = 0
            for i in range(1, len(values)):
                if values[i] != values[seq_start]:
                    if i - seq_start >= min_length:
                        patterns.append(PatternMatch(
                            pattern_type='row_repeat',
                            coordinates=[(row, c) for c in range(seq_start, i)],
                            values=[values[seq_start]],
                            description=f"Row {row}: value {values[seq_start]} repeats {i - seq_start} times"
                        ))
                    seq_start = i

        return patterns

    def find_cfb_patterns(self) -> List[PatternMatch]:
        """Look for CFB's special numbers"""
        patterns = []

        for num in CFB_NUMBERS:
            if -128 <= num <= 127:
                coords = self.matrix.find_value(num)
                if coords:
                    patterns.append(PatternMatch(
                        pattern_type='cfb_number',
                        coordinates=coords,
                        values=[num],
                        description=f"CFB number {num} found at {len(coords)} locations"
                    ))

        return patterns

    def scan_known_coordinates(self) -> Dict[Tuple[int, int], Dict]:
        """Check all known significant coordinates"""
        results = {}
        for coords, desc in KNOWN_COORDINATES.items():
            value = self.matrix.query(coords[0], coords[1])
            anna_coords = self.matrix.matrix_to_anna(coords[0], coords[1])
            results[coords] = {
                'value': value,
                'description': desc,
                'anna_coords': anna_coords,
            }
        return results

# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKCHAIN CORRELATOR
# ═══════════════════════════════════════════════════════════════════════════════

class BlockchainCorrelator:
    """Correlate Anna Matrix with blockchain data"""

    def __init__(self, matrix: AnnaMatrix):
        self.matrix = matrix
        self.patoshi_addresses = []
        self.load_patoshi_data()

    def load_patoshi_data(self):
        """Load Patoshi address data"""
        try:
            with open(PATOSHI_FILE, 'r') as f:
                data = json.load(f)

            # Handle different formats
            if isinstance(data, list):
                self.patoshi_addresses = data
            elif isinstance(data, dict):
                # Try common keys
                self.patoshi_addresses = data.get('records', data.get('addresses', data.get('data', [])))
            else:
                self.patoshi_addresses = []

            print(f"✓ Loaded {len(self.patoshi_addresses)} Patoshi addresses")
        except FileNotFoundError:
            print(f"✗ Patoshi file not found: {PATOSHI_FILE}")

    def correlate_addresses(self, addresses: List[str], encoding: str = 'sha256') -> List[QueryResult]:
        """Map addresses to Anna coordinates and get values"""
        results = []

        for addr in addresses:
            if encoding == 'sha256':
                row, col = Encoders.sha256_to_coords(addr)
            elif encoding == 'double_sha256':
                row, col = Encoders.double_sha256_to_coords(addr)
            else:
                row, col = Encoders.sha256_to_coords(addr)

            value = self.matrix.query(row, col)
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)

            # Check significance
            sig = None
            if (row, col) in KNOWN_COORDINATES:
                sig = KNOWN_COORDINATES[(row, col)]

            results.append(QueryResult(
                row=row,
                col=col,
                anna_x=anna_x,
                anna_y=anna_y,
                value=value,
                encoding_method=encoding,
                input_data=addr,
                significance=sig
            ))

        return results

    def correlate_genesis_blocks(self) -> List[QueryResult]:
        """Correlate early Bitcoin blocks with Anna"""
        results = []

        # Genesis and early block data
        genesis_data = [
            ("Block 0", "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", 1231006505),
            ("Block 1", "00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048", 1231469665),
            ("Block 9", "000000008d9dc510f23c2657fc4f67bea30078cc05a90eb89e84cc475c080805", 1231473279),
            ("Block 170", "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee", 1231731025),
        ]

        for name, block_hash, timestamp in genesis_data:
            # Try hash encoding
            row, col = Encoders.hex_to_coords(block_hash)
            value = self.matrix.query(row, col)
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)

            results.append(QueryResult(
                row=row, col=col, anna_x=anna_x, anna_y=anna_y,
                value=value, encoding_method='block_hash',
                input_data=f"{name}: {block_hash[:16]}..."
            ))

            # Try timestamp encoding
            row2, col2 = Encoders.timestamp_to_coords(timestamp)
            value2 = self.matrix.query(row2, col2)
            anna_x2, anna_y2 = self.matrix.matrix_to_anna(row2, col2)

            results.append(QueryResult(
                row=row2, col=col2, anna_x=anna_x2, anna_y=anna_y2,
                value=value2, encoding_method='timestamp',
                input_data=f"{name}: {timestamp}"
            ))

        return results

    def find_value_correlations(self, value: int) -> Dict[str, List[str]]:
        """Find which addresses map to cells with specific value"""
        coords = self.matrix.find_value(value)
        correlations = {'patoshi': [], 'genesis': []}

        # Check Patoshi addresses
        for addr_data in self.patoshi_addresses[:1000]:  # Limit for performance
            addr = addr_data.get('address', addr_data) if isinstance(addr_data, dict) else addr_data
            row, col = Encoders.sha256_to_coords(addr)
            if (row, col) in coords:
                correlations['patoshi'].append(addr)

        return correlations

# ═══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE CLI
# ═══════════════════════════════════════════════════════════════════════════════

class AnnaTerminal:
    """Interactive research terminal"""

    def __init__(self):
        print("\n" + "═" * 70)
        print("           ANNA RESEARCH TERMINAL v1.0")
        print("═" * 70)

        self.matrix = AnnaMatrix()
        self.scanner = PatternScanner(self.matrix)
        self.correlator = BlockchainCorrelator(self.matrix)

        # Show statistics
        stats = self.matrix.get_statistics()
        print(f"\nMatrix Stats: min={stats['min']}, max={stats['max']}, unique={stats['unique_values']}")
        print(f"             positive={stats['positive']}, negative={stats['negative']}, zeros={stats['zeros']}")
        print()

    def print_help(self):
        """Show available commands"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║ AVAILABLE COMMANDS                                                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ QUERY COMMANDS                                                                ║
║   q <row> <col>        Query matrix at [row, col]                             ║
║   anna <x> <y>         Query using Anna coords (x: -64..63, y: 63..-64)       ║
║   btc <address>        Hash BTC address to coords and query                   ║
║   seed <qubic_seed>    Hash Qubic seed to coords and query                    ║
║   ts <timestamp>       Convert Unix timestamp to coords                       ║
║   date <YYYY-MM-DD>    Convert date to coords                                 ║
║   hash <hex_string>    Convert hex hash to coords                             ║
║   block <height>       Convert block height to coords                         ║
║                                                                               ║
║ SCAN COMMANDS                                                                 ║
║   row <n>              Show all values in row n                               ║
║   col <n>              Show all values in column n                            ║
║   diag <r> <c>         Diagonal scan from [r,c]                               ║
║   spiral               Spiral scan from center                                ║
║   find <value>         Find all cells with value                              ║
║   cfb                  Find CFB's special numbers                             ║
║   known                Check all known significant coords                     ║
║                                                                               ║
║ CORRELATION COMMANDS                                                          ║
║   patoshi [n]          Correlate first n Patoshi addresses (default 100)      ║
║   genesis              Correlate genesis/early blocks                         ║
║   findcorr <value>     Find addresses that map to cells with value            ║
║                                                                               ║
║ BATCH COMMANDS                                                                ║
║   batch <mode> <file>  Process file with addresses/seeds                      ║
║   export <file>        Export results to JSON                                 ║
║                                                                               ║
║ OTHER                                                                         ║
║   stats                Show matrix statistics                                 ║
║   help                 Show this help                                         ║
║   exit                 Exit terminal                                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

    def format_result(self, r: QueryResult) -> str:
        """Format a query result"""
        sig = f" ★ {r.significance}" if r.significance else ""
        return f"  [{r.row:3d},{r.col:3d}] Anna({r.anna_x:+4d},{r.anna_y:+4d}) = {r.value:+4d}  via {r.encoding_method}{sig}"

    def cmd_query(self, args: List[str]):
        """Query matrix at coordinates"""
        if len(args) < 2:
            print("Usage: q <row> <col>")
            return
        row, col = int(args[0]), int(args[1])
        value = self.matrix.query(row, col)
        anna_x, anna_y = self.matrix.matrix_to_anna(row, col)
        sig = KNOWN_COORDINATES.get((row, col), "")
        print(f"  Matrix[{row},{col}] = {value}")
        print(f"  Anna({anna_x:+d},{anna_y:+d}) = {value}")
        if sig:
            print(f"  ★ Significance: {sig}")

    def cmd_anna_query(self, args: List[str]):
        """Query using Anna coordinates"""
        if len(args) < 2:
            print("Usage: anna <x> <y>  (x: -64..63, y: 63..-64)")
            return
        x, y = int(args[0]), int(args[1])
        value = self.matrix.query_anna_coords(x, y)
        row, col = self.matrix.anna_to_matrix(x, y)
        print(f"  Anna({x:+d},{y:+d}) = {value}")
        print(f"  Matrix[{row},{col}] = {value}")

    def cmd_btc(self, args: List[str]):
        """Query with Bitcoin address"""
        if len(args) < 1:
            print("Usage: btc <address>")
            return
        addr = args[0]

        # Try different encodings
        print(f"\n  Querying Anna with BTC address: {addr[:20]}...")

        for encoding in ['sha256', 'double_sha256']:
            if encoding == 'sha256':
                row, col = Encoders.sha256_to_coords(addr)
            else:
                row, col = Encoders.double_sha256_to_coords(addr)

            value = self.matrix.query(row, col)
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)
            sig = KNOWN_COORDINATES.get((row, col), "")

            print(f"\n  {encoding}:")
            print(f"    [{row:3d},{col:3d}] Anna({anna_x:+4d},{anna_y:+4d}) = {value:+4d}")
            if sig:
                print(f"    ★ {sig}")

    def cmd_find(self, args: List[str]):
        """Find cells with specific value"""
        if len(args) < 1:
            print("Usage: find <value>")
            return
        value = int(args[0])
        coords = self.matrix.find_value(value)
        print(f"\n  Found {len(coords)} cells with value {value}:")
        for row, col in coords[:20]:  # Limit output
            anna_x, anna_y = self.matrix.matrix_to_anna(row, col)
            sig = KNOWN_COORDINATES.get((row, col), "")
            print(f"    [{row:3d},{col:3d}] Anna({anna_x:+4d},{anna_y:+4d}){' ★ ' + sig if sig else ''}")
        if len(coords) > 20:
            print(f"    ... and {len(coords) - 20} more")

    def cmd_known(self, args: List[str]):
        """Check known significant coordinates"""
        results = self.scanner.scan_known_coordinates()
        print("\n  Known Significant Coordinates:")
        print("  " + "-" * 60)
        for coords, data in results.items():
            print(f"    [{coords[0]:3d},{coords[1]:3d}] = {data['value']:+4d}  {data['description']}")

    def cmd_cfb(self, args: List[str]):
        """Find CFB's special numbers"""
        patterns = self.scanner.find_cfb_patterns()
        print("\n  CFB Pattern Search:")
        for p in patterns:
            print(f"    {p.description}")
            for coord in p.coordinates[:5]:
                print(f"      [{coord[0]:3d},{coord[1]:3d}]")

    def cmd_patoshi(self, args: List[str]):
        """Correlate Patoshi pubkeys (not addresses - data contains pubkeys)"""
        n = int(args[0]) if args else 100

        # Extract pubkeys from Patoshi data
        pubkeys = []
        for record in self.correlator.patoshi_addresses[:n]:
            if isinstance(record, dict):
                # Data contains 'pubkey' not 'address'
                pk = record.get('pubkey', '')
                if pk:
                    pubkeys.append((record.get('blockHeight', 0), pk))
            else:
                pubkeys.append((0, record))

        print(f"\n  Correlating {len(pubkeys)} Patoshi pubkeys:")
        print("  " + "-" * 60)

        # Group by value
        value_counts = {}
        cfb_hits = []

        for block, pk in pubkeys:
            row, col = Encoders.sha256_to_coords(pk)
            value = self.matrix.query(row, col)

            if value is None:
                continue

            value_counts[value] = value_counts.get(value, 0) + 1

            # Check for CFB numbers
            if value in CFB_NUMBERS or -value in CFB_NUMBERS:
                cfb_hits.append((block, pk[:30], (row, col), value))

        # Show CFB hits
        if cfb_hits:
            print("\n  ★ CFB NUMBER HITS:")
            for block, pk, coords, value in cfb_hits[:10]:
                print(f"    Block {block}: {pk}... → [{coords[0]},{coords[1]}] = {value:+d}")
            if len(cfb_hits) > 10:
                print(f"    ... and {len(cfb_hits) - 10} more CFB hits")

        # Show value distribution
        print("\n  Value Distribution (top 15):")
        sorted_values = sorted(value_counts.items(), key=lambda x: -x[1])[:15]
        total = sum(v for _, v in value_counts.items())
        expected = total / 256

        for val, count in sorted_values:
            ratio = count / expected if expected > 0 else 0
            cfb = " ★ CFB" if val in CFB_NUMBERS or -val in CFB_NUMBERS else ""
            print(f"    {val:+4d}: {count:4d} ({ratio:.2f}x expected){cfb}")

    def cmd_genesis(self, args: List[str]):
        """Correlate genesis blocks"""
        results = self.correlator.correlate_genesis_blocks()
        print("\n  Genesis Block Correlation:")
        print("  " + "-" * 60)
        for r in results:
            print(f"    {r.input_data}")
            print(f"      -> [{r.row},{r.col}] Anna({r.anna_x:+d},{r.anna_y:+d}) = {r.value}")

    def cmd_row(self, args: List[str]):
        """Show all values in a row"""
        if len(args) < 1:
            print("Usage: row <n>")
            return
        row = int(args[0])
        values = self.scanner.scan_row(row)
        print(f"\n  Row {row}:")
        for i in range(0, 128, 16):
            chunk = values[i:i+16]
            print(f"    {i:3d}: " + " ".join(f"{v:+4d}" for v in chunk))

    def cmd_stats(self, args: List[str]):
        """Show matrix statistics"""
        stats = self.matrix.get_statistics()
        print("\n  Matrix Statistics:")
        print(f"    Min value:      {stats['min']}")
        print(f"    Max value:      {stats['max']}")
        print(f"    Mean value:     {stats['mean']:.2f}")
        print(f"    Zero cells:     {stats['zeros']}")
        print(f"    Positive cells: {stats['positive']}")
        print(f"    Negative cells: {stats['negative']}")
        print(f"    Unique values:  {stats['unique_values']}")

    def run(self):
        """Run the interactive terminal"""
        self.print_help()

        while True:
            try:
                cmd_input = input("\nanna> ").strip()
                if not cmd_input:
                    continue

                parts = cmd_input.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ['exit', 'quit', 'q'] and not args:
                    print("Goodbye!")
                    break
                elif cmd == 'help':
                    self.print_help()
                elif cmd == 'q' and args:
                    self.cmd_query(args)
                elif cmd == 'anna':
                    self.cmd_anna_query(args)
                elif cmd == 'btc':
                    self.cmd_btc(args)
                elif cmd == 'find':
                    self.cmd_find(args)
                elif cmd == 'known':
                    self.cmd_known(args)
                elif cmd == 'cfb':
                    self.cmd_cfb(args)
                elif cmd == 'patoshi':
                    self.cmd_patoshi(args)
                elif cmd == 'genesis':
                    self.cmd_genesis(args)
                elif cmd == 'row':
                    self.cmd_row(args)
                elif cmd == 'stats':
                    self.cmd_stats(args)
                elif cmd == 'seed':
                    if args:
                        row, col = Encoders.qubic_seed_to_coords(args[0])
                        value = self.matrix.query(row, col)
                        anna_x, anna_y = self.matrix.matrix_to_anna(row, col)
                        print(f"  Seed: {args[0][:30]}...")
                        print(f"  -> [{row},{col}] Anna({anna_x:+d},{anna_y:+d}) = {value}")
                elif cmd == 'ts':
                    if args:
                        ts = int(args[0])
                        row, col = Encoders.timestamp_to_coords(ts)
                        value = self.matrix.query(row, col)
                        print(f"  Timestamp {ts} -> [{row},{col}] = {value}")
                elif cmd == 'date':
                    if args:
                        row, col = Encoders.date_to_coords(args[0])
                        value = self.matrix.query(row, col)
                        print(f"  Date {args[0]} -> [{row},{col}] = {value}")
                elif cmd == 'block':
                    if args:
                        height = int(args[0])
                        row, col = Encoders.block_height_to_coords(height)
                        value = self.matrix.query(row, col)
                        print(f"  Block {height} -> [{row},{col}] = {value}")
                elif cmd == 'hash':
                    if args:
                        row, col = Encoders.hex_to_coords(args[0])
                        value = self.matrix.query(row, col)
                        print(f"  Hash -> [{row},{col}] = {value}")
                else:
                    print(f"  Unknown command: {cmd}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except Exception as e:
                print(f"  Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    terminal = AnnaTerminal()
    terminal.run()
