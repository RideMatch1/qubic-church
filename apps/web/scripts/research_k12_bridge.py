#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    K12 QUBIC BRIDGE RESEARCH                                   ║
║                                                                                ║
║  Test if Anna Matrix seeds can derive valid Qubic IDs via K12 hashing         ║
║  This could prove the mathematical bridge between Bitcoin and Qubic           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Try to import K12 - may need installation
try:
    from Crypto.Hash import KangarooTwelve as K12
    HAVE_K12 = True
except ImportError:
    HAVE_K12 = False
    print("⚠ KangarooTwelve not available - using SHA3-256 as fallback")

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

# Qubic alphabet for ID encoding
QUBIC_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def load_matrix() -> List[List[int]]:
    """Load Anna Matrix and convert any string values to integers"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)

    # Convert any string values to integers (some cells contain '00000000')
    matrix = []
    for row in data['matrix']:
        clean_row = []
        for v in row:
            if isinstance(v, str):
                clean_row.append(0)  # Treat string markers as 0
            else:
                clean_row.append(int(v))
        matrix.append(clean_row)
    return matrix

def k12_hash(data: bytes, output_length: int = 32) -> bytes:
    """Compute K12 hash (or SHA3-256 fallback)"""
    if HAVE_K12:
        h = K12.new()
        h.update(data)
        return h.read(output_length)
    else:
        # Fallback to SHA3-256
        return hashlib.sha3_256(data).digest()[:output_length]

def bytes_to_qubic_id(data: bytes) -> str:
    """Convert bytes to Qubic ID format (60 lowercase letters)"""
    # Qubic IDs are 60 characters from the alphabet a-z
    # Each character represents ~4.7 bits
    result = []

    # Convert bytes to a large integer
    num = int.from_bytes(data, 'big')

    # Convert to base-26
    for _ in range(60):
        result.append(QUBIC_ALPHABET[num % 26])
        num //= 26

    return ''.join(reversed(result))

def matrix_row_to_seed(matrix: List[List[int]], row: int) -> bytes:
    """Convert matrix row to seed bytes"""
    return bytes((v + 128) % 256 for v in matrix[row])

def matrix_col_to_seed(matrix: List[List[int]], col: int) -> bytes:
    """Convert matrix column to seed bytes"""
    return bytes((matrix[r][col] + 128) % 256 for r in range(128))

def matrix_diagonal_to_seed(matrix: List[List[int]], start: int = 0) -> bytes:
    """Convert matrix diagonal to seed bytes"""
    values = []
    for i in range(128):
        row = (start + i) % 128
        col = i
        values.append((matrix[row][col] + 128) % 256)
    return bytes(values)

# ═══════════════════════════════════════════════════════════════════════════════
# K12 BRIDGE RESEARCH
# ═══════════════════════════════════════════════════════════════════════════════

class K12BridgeResearch:
    def __init__(self):
        print("═" * 70)
        print("           K12 QUBIC BRIDGE RESEARCH")
        print("═" * 70)
        self.matrix = load_matrix()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'k12_available': HAVE_K12,
            'seeds_tested': 0,
            'qubic_ids_generated': [],
            'cfb_related_ids': [],
            'patterns_found': [],
        }

    def generate_strategic_seeds(self) -> List[Tuple[str, bytes]]:
        """Generate seeds from strategic matrix locations"""
        seeds = []

        # 1. CFB rows (27, 37, 42, 127)
        print("\n  [1] Generating CFB row seeds...")
        for cfb_row in [27, 37, 42, 127]:
            seed = matrix_row_to_seed(self.matrix, cfb_row)
            seeds.append((f'row_{cfb_row}', seed))

        # 2. CFB columns
        print("  [2] Generating CFB column seeds...")
        for cfb_col in [27, 37, 42, 127]:
            seed = matrix_col_to_seed(self.matrix, cfb_col)
            seeds.append((f'col_{cfb_col}', seed))

        # 3. Diagonals from CFB starting points
        print("  [3] Generating diagonal seeds...")
        for start in [0, 27, 37, 42, 64]:
            seed = matrix_diagonal_to_seed(self.matrix, start)
            seeds.append((f'diag_{start}', seed))

        # 4. Special rows (Vision, Memory, Exit, Anna centers)
        print("  [4] Generating special region seeds...")
        special_rows = {
            'vision_center': 64,
            'anna_center': 69,
            'memory': 28,
            'exit': 113,
        }
        for name, row in special_rows.items():
            seed = matrix_row_to_seed(self.matrix, row)
            seeds.append((f'special_{name}', seed))

        # 5. Coordinate-based seeds
        print("  [5] Generating coordinate-based seeds...")
        # (27, 37), (37, 42), (42, 127), etc.
        cfb_pairs = [(27, 37), (37, 42), (42, 127), (27, 42), (27, 127)]
        for r, c in cfb_pairs:
            # Create seed from 3x3 neighborhood
            values = []
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    values.append((self.matrix[(r+dr) % 128][(c+dc) % 128] + 128) % 256)
            # Pad to 32 bytes
            while len(values) < 32:
                values.extend(values[:32-len(values)])
            seeds.append((f'coord_{r}_{c}', bytes(values[:32])))

        # 6. XOR-combined seeds
        print("  [6] Generating XOR-combined seeds...")
        row27 = matrix_row_to_seed(self.matrix, 27)
        row37 = matrix_row_to_seed(self.matrix, 37)
        row42 = matrix_row_to_seed(self.matrix, 42)

        xor_27_37 = bytes(a ^ b for a, b in zip(row27, row37))
        xor_all = bytes(a ^ b ^ c for a, b, c in zip(row27, row37, row42))
        seeds.append(('xor_27_37', xor_27_37))
        seeds.append(('xor_27_37_42', xor_all))

        # 7. CFB string hashes
        print("  [7] Generating CFB string hash seeds...")
        cfb_strings = ['CFB', 'SATOSHI', 'BITCOIN', 'ANNA', 'qubic', 'IOTA']
        for s in cfb_strings:
            h = hashlib.sha256(s.encode()).digest()
            seeds.append((f'string_{s}', h))

        print(f"\n  Generated {len(seeds)} strategic seeds")
        return seeds

    def derive_qubic_ids(self, seeds: List[Tuple[str, bytes]]) -> List[Dict]:
        """Derive Qubic IDs from seeds using K12"""
        print("\n" + "═" * 70)
        print("DERIVING QUBIC IDS")
        print("═" * 70)

        qubic_ids = []

        for name, seed in seeds:
            # Ensure seed is 32 bytes
            if len(seed) < 32:
                seed = seed + bytes(32 - len(seed))
            elif len(seed) > 32:
                seed = seed[:32]

            # K12 hash
            k12_out = k12_hash(seed, 32)

            # Convert to Qubic ID
            qubic_id = bytes_to_qubic_id(k12_out)

            # Check for CFB patterns in the ID
            cfb_patterns = []
            if 'cfb' in qubic_id:
                cfb_patterns.append('cfb')
            if qubic_id.count('z') >= 5:  # z = 27th letter (close to 27)
                cfb_patterns.append('high_z_count')

            entry = {
                'name': name,
                'seed_hex': seed.hex()[:32] + '...',
                'k12_hex': k12_out.hex()[:32] + '...',
                'qubic_id': qubic_id,
                'cfb_patterns': cfb_patterns,
            }

            qubic_ids.append(entry)
            self.results['seeds_tested'] += 1

            if cfb_patterns:
                self.results['cfb_related_ids'].append(entry)
                print(f"  ★ {name}: {qubic_id[:20]}... (CFB: {cfb_patterns})")
            else:
                print(f"    {name}: {qubic_id[:20]}...")

        return qubic_ids

    def analyze_id_patterns(self, qubic_ids: List[Dict]):
        """Analyze patterns in generated Qubic IDs"""
        print("\n" + "═" * 70)
        print("PATTERN ANALYSIS")
        print("═" * 70)

        # Character frequency analysis
        all_chars = ''.join(entry['qubic_id'] for entry in qubic_ids)
        char_freq = {}
        for c in QUBIC_ALPHABET:
            char_freq[c] = all_chars.count(c)

        # Expected frequency (uniform distribution)
        expected = len(all_chars) / 26

        # Find over/under-represented characters
        anomalies = []
        for c, count in sorted(char_freq.items(), key=lambda x: x[1], reverse=True):
            ratio = count / expected
            if ratio > 1.3 or ratio < 0.7:
                anomalies.append({'char': c, 'count': count, 'ratio': round(ratio, 2)})

        print(f"\n  Character distribution anomalies:")
        for a in anomalies[:10]:
            print(f"    '{a['char']}' ({ord(a['char'])-ord('a')+1}): {a['ratio']}x expected")

        self.results['patterns_found'].append({
            'type': 'character_frequency',
            'anomalies': anomalies[:10],
        })

        # Check for common prefixes/suffixes
        prefixes = {}
        suffixes = {}
        for entry in qubic_ids:
            qid = entry['qubic_id']
            prefix = qid[:4]
            suffix = qid[-4:]
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            suffixes[suffix] = suffixes.get(suffix, 0) + 1

        common_prefixes = [p for p, c in prefixes.items() if c > 1]
        common_suffixes = [s for s, c in suffixes.items() if c > 1]

        if common_prefixes:
            print(f"\n  Common prefixes: {common_prefixes}")
            self.results['patterns_found'].append({
                'type': 'common_prefixes',
                'values': common_prefixes,
            })

        if common_suffixes:
            print(f"  Common suffixes: {common_suffixes}")
            self.results['patterns_found'].append({
                'type': 'common_suffixes',
                'values': common_suffixes,
            })

    def test_known_qubic_seeds(self):
        """Test against known Qubic seeds from data file"""
        print("\n" + "═" * 70)
        print("TESTING AGAINST KNOWN QUBIC SEEDS")
        print("═" * 70)

        # Load Qubic seeds if available
        qubic_seeds_file = DATA_DIR / "qubic-seeds.json"
        if not qubic_seeds_file.exists():
            print("  ⚠ qubic-seeds.json not found")
            return

        with open(qubic_seeds_file, 'r') as f:
            known_seeds = json.load(f)

        print(f"  Loaded {len(known_seeds)} known Qubic seeds")

        # Extract just the seed strings for comparison
        known_set = set()
        if isinstance(known_seeds, list):
            for entry in known_seeds[:1000]:  # Sample first 1000
                if isinstance(entry, dict) and 'seed' in entry:
                    known_set.add(entry['seed'])
                elif isinstance(entry, str):
                    known_set.add(entry)

        print(f"  Comparing against {len(known_set)} unique seeds...")

        # Check if any of our generated seeds match
        matches = []
        for entry in self.results.get('qubic_ids_generated', []):
            if entry['qubic_id'] in known_set:
                matches.append(entry)
                print(f"  ★★★ MATCH: {entry['name']} → {entry['qubic_id'][:30]}...")

        if not matches:
            print("  No direct matches found (expected for random seeds)")

        self.results['known_seed_matches'] = matches

    def run(self):
        """Run full K12 bridge research"""
        # Generate seeds
        seeds = self.generate_strategic_seeds()

        # Derive Qubic IDs
        qubic_ids = self.derive_qubic_ids(seeds)
        self.results['qubic_ids_generated'] = qubic_ids

        # Analyze patterns
        self.analyze_id_patterns(qubic_ids)

        # Test against known seeds
        self.test_known_qubic_seeds()

        # Summary
        print("\n" + "═" * 70)
        print("K12 BRIDGE RESEARCH SUMMARY")
        print("═" * 70)
        print(f"\n  Seeds tested: {self.results['seeds_tested']}")
        print(f"  CFB-related IDs: {len(self.results['cfb_related_ids'])}")
        print(f"  Patterns found: {len(self.results['patterns_found'])}")
        print(f"  K12 available: {HAVE_K12}")

        # Save results
        output_file = SCRIPT_DIR / 'K12_BRIDGE_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n  Results saved to: {output_file}")

        return self.results

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    research = K12BridgeResearch()
    research.run()
