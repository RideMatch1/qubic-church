#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DEEP XOR NETWORK ANALYSIS                                   ║
║                                                                                ║
║  Analyze the XOR relationships in the Anna Matrix                             ║
║  Focus on Vision Center (-70) and CFB number patterns                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

CFB_NUMBERS = {27, 37, 42, 127}
CFB_SIGNED = {27, -27, 37, -37, 42, -42, 127, -127}

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX UTILITIES
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

class XORNetworkAnalyzer:
    def __init__(self):
        print("═" * 70)
        print("           DEEP XOR NETWORK ANALYSIS")
        print("═" * 70)
        self.matrix = load_matrix()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'vision_center_analysis': {},
            'xor_to_cfb': [],
            'xor_chains': [],
            'hidden_patterns': [],
            'statistics': {},
        }

    def get_value(self, row: int, col: int) -> int:
        """Get matrix value with wrap-around"""
        return self.matrix[row % 128][col % 128]

    def analyze_vision_center(self):
        """Deep analysis of Vision Center (-70) at [64, 64]"""
        print("\n" + "─" * 70)
        print("VISION CENTER ANALYSIS (-70 at [64, 64])")
        print("─" * 70)

        vision_value = self.get_value(64, 64)
        print(f"\n  Vision Center value: {vision_value}")

        # Find all cells that XOR with Vision Center to produce CFB
        xor_to_cfb = defaultdict(list)

        for row in range(128):
            for col in range(128):
                value = self.get_value(row, col)
                xor_result = value ^ vision_value

                if xor_result in CFB_NUMBERS or xor_result in {-27 & 0xFF, -37 & 0xFF, -42 & 0xFF}:
                    xor_to_cfb[xor_result].append({
                        'pos': [row, col],
                        'value': value,
                        'xor': xor_result,
                    })

        print(f"\n  Cells that XOR with Vision Center to produce CFB numbers:")
        total_xor_cfb = 0
        for cfb_num, cells in sorted(xor_to_cfb.items()):
            print(f"    XOR → {cfb_num}: {len(cells)} cells")
            total_xor_cfb += len(cells)

        print(f"  Total: {total_xor_cfb} cells XOR to CFB numbers")

        self.results['vision_center_analysis'] = {
            'position': [64, 64],
            'value': vision_value,
            'xor_to_cfb_count': total_xor_cfb,
            'breakdown': {str(k): len(v) for k, v in xor_to_cfb.items()},
            'sample_cells': {str(k): v[:5] for k, v in xor_to_cfb.items()},
        }

        # Analyze the geometric distribution
        print("\n  Geometric distribution of Vision XOR cells:")
        quadrants = {'NW': 0, 'NE': 0, 'SW': 0, 'SE': 0}
        for cfb_num, cells in xor_to_cfb.items():
            for cell in cells:
                r, c = cell['pos']
                if r < 64 and c < 64:
                    quadrants['NW'] += 1
                elif r < 64 and c >= 64:
                    quadrants['NE'] += 1
                elif r >= 64 and c < 64:
                    quadrants['SW'] += 1
                else:
                    quadrants['SE'] += 1

        for q, count in quadrants.items():
            print(f"    {q}: {count} cells")

        self.results['vision_center_analysis']['quadrant_distribution'] = quadrants

    def build_xor_graph(self):
        """Build a graph of XOR relationships between cells"""
        print("\n" + "─" * 70)
        print("XOR RELATIONSHIP GRAPH")
        print("─" * 70)

        # Find all pairs that XOR to CFB numbers
        cfb_pairs = []

        print("\n  Scanning for cell pairs that XOR to CFB numbers...")
        for r1 in range(128):
            for c1 in range(128):
                v1 = self.get_value(r1, c1)
                # Only check neighbors to avoid O(n^4)
                for dr in range(-3, 4):
                    for dc in range(-3, 4):
                        if dr == 0 and dc == 0:
                            continue
                        r2, c2 = (r1 + dr) % 128, (c1 + dc) % 128
                        v2 = self.get_value(r2, c2)
                        xor = v1 ^ v2

                        if abs(xor) in CFB_NUMBERS:
                            cfb_pairs.append({
                                'cell1': [r1, c1, v1],
                                'cell2': [r2, c2, v2],
                                'xor': xor,
                                'distance': abs(dr) + abs(dc),
                            })

        print(f"  Found {len(cfb_pairs)} adjacent cell pairs that XOR to CFB")

        # Categorize by XOR result
        by_xor = defaultdict(list)
        for pair in cfb_pairs:
            by_xor[pair['xor']].append(pair)

        print("\n  Breakdown by XOR result:")
        for xor_val, pairs in sorted(by_xor.items(), key=lambda x: -len(x[1])):
            print(f"    XOR = {xor_val}: {len(pairs)} pairs")

        self.results['xor_to_cfb'] = {
            'total_pairs': len(cfb_pairs),
            'by_result': {str(k): len(v) for k, v in by_xor.items()},
            'samples': cfb_pairs[:20],
        }

    def trace_xor_chains(self):
        """Trace XOR chains through the matrix"""
        print("\n" + "─" * 70)
        print("XOR CHAIN TRACING")
        print("─" * 70)

        # Start from cells with CFB values and follow XOR chains
        starting_points = []
        for r in range(128):
            for c in range(128):
                v = self.get_value(r, c)
                if v in CFB_SIGNED:
                    starting_points.append((r, c, v))

        print(f"\n  Found {len(starting_points)} CFB-value cells as starting points")

        # Trace chains from a sample of starting points
        chains = []
        for start_r, start_c, start_v in starting_points[:20]:
            chain = self._trace_chain(start_r, start_c, max_length=15)
            if len(chain) > 3:
                chains.append({
                    'start': [start_r, start_c, start_v],
                    'length': len(chain),
                    'path': chain,
                    'returns_to_cfb': chain[-1]['value'] in CFB_SIGNED if chain else False,
                })

        # Count chains that return to CFB
        return_chains = [c for c in chains if c['returns_to_cfb']]
        print(f"  Chains traced: {len(chains)}")
        print(f"  Chains returning to CFB: {len(return_chains)}")

        self.results['xor_chains'] = {
            'total_traced': len(chains),
            'returning_to_cfb': len(return_chains),
            'sample_chains': chains[:10],
        }

    def _trace_chain(self, start_r: int, start_c: int, max_length: int = 20) -> List[Dict]:
        """Trace a single XOR chain"""
        chain = []
        visited = set()
        r, c = start_r, start_c

        for _ in range(max_length):
            if (r, c) in visited:
                break
            visited.add((r, c))

            current_val = self.get_value(r, c)
            chain.append({'pos': [r, c], 'value': current_val})

            # Find best neighbor (one that XORs to interesting value)
            best_next = None
            best_score = -1

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (r + dr) % 128, (c + dc) % 128
                    if (nr, nc) in visited:
                        continue

                    nv = self.get_value(nr, nc)
                    xor = current_val ^ nv

                    # Score based on CFB relevance
                    score = 0
                    if abs(xor) in CFB_NUMBERS:
                        score = 100
                    elif abs(nv) in CFB_NUMBERS:
                        score = 50
                    elif xor == 0:
                        score = 10

                    if score > best_score:
                        best_score = score
                        best_next = (nr, nc)

            if best_next is None:
                break
            r, c = best_next

        return chain

    def find_hidden_patterns(self):
        """Search for hidden patterns in XOR relationships"""
        print("\n" + "─" * 70)
        print("HIDDEN PATTERN SEARCH")
        print("─" * 70)

        patterns = []

        # Pattern 1: Symmetric XOR pairs
        print("\n  [1] Searching for symmetric XOR pairs...")
        symmetric_pairs = []
        for r in range(64):
            for c in range(64):
                v1 = self.get_value(r, c)
                v2 = self.get_value(127 - r, 127 - c)  # Point symmetric
                xor = v1 ^ v2

                if abs(xor) in CFB_NUMBERS:
                    symmetric_pairs.append({
                        'pos1': [r, c],
                        'pos2': [127 - r, 127 - c],
                        'v1': v1,
                        'v2': v2,
                        'xor': xor,
                    })

        print(f"      Found {len(symmetric_pairs)} point-symmetric pairs XORing to CFB")
        patterns.append({
            'type': 'symmetric_xor_pairs',
            'count': len(symmetric_pairs),
            'samples': symmetric_pairs[:10],
        })

        # Pattern 2: Row/Column XOR sums
        print("\n  [2] Analyzing row XOR sums...")
        row_xor_sums = []
        for r in range(128):
            row_xor = 0
            for c in range(128):
                row_xor ^= self.get_value(r, c)
            if abs(row_xor) in CFB_NUMBERS or row_xor == 0:
                row_xor_sums.append({'row': r, 'xor_sum': row_xor})

        print(f"      Rows with CFB XOR sum: {len(row_xor_sums)}")
        patterns.append({
            'type': 'row_xor_sums',
            'cfb_rows': row_xor_sums,
        })

        # Pattern 3: Diagonal XOR patterns
        print("\n  [3] Analyzing diagonal XOR patterns...")
        diag_patterns = []
        for start in range(128):
            diag_xor = 0
            for i in range(128):
                diag_xor ^= self.get_value((start + i) % 128, i)
            if abs(diag_xor) in CFB_NUMBERS:
                diag_patterns.append({'start': start, 'xor': diag_xor})

        print(f"      Diagonals with CFB XOR: {len(diag_patterns)}")
        patterns.append({
            'type': 'diagonal_xor',
            'cfb_diagonals': diag_patterns,
        })

        # Pattern 4: 3x3 block XOR analysis
        print("\n  [4] Analyzing 3x3 block XORs...")
        block_cfb = []
        for r in range(0, 126, 3):
            for c in range(0, 126, 3):
                block_xor = 0
                for dr in range(3):
                    for dc in range(3):
                        block_xor ^= self.get_value(r + dr, c + dc)
                if abs(block_xor) in CFB_NUMBERS:
                    block_cfb.append({'pos': [r, c], 'xor': block_xor})

        print(f"      3x3 blocks with CFB XOR: {len(block_cfb)}")
        patterns.append({
            'type': 'block_3x3_xor',
            'cfb_blocks': block_cfb[:20],
        })

        self.results['hidden_patterns'] = patterns

    def compute_statistics(self):
        """Compute XOR-related statistics"""
        print("\n" + "─" * 70)
        print("XOR STATISTICS")
        print("─" * 70)

        # Global XOR of entire matrix
        global_xor = 0
        for r in range(128):
            for c in range(128):
                global_xor ^= self.get_value(r, c)

        print(f"\n  Global matrix XOR: {global_xor}")

        # Quadrant XORs
        quadrant_xors = {}
        for qname, (r_start, r_end, c_start, c_end) in [
            ('NW', (0, 64, 0, 64)),
            ('NE', (0, 64, 64, 128)),
            ('SW', (64, 128, 0, 64)),
            ('SE', (64, 128, 64, 128)),
        ]:
            qxor = 0
            for r in range(r_start, r_end):
                for c in range(c_start, c_end):
                    qxor ^= self.get_value(r, c)
            quadrant_xors[qname] = qxor
            cfb_flag = "★ CFB!" if abs(qxor) in CFB_NUMBERS else ""
            print(f"    {qname} quadrant XOR: {qxor} {cfb_flag}")

        # XOR frequency distribution
        xor_freq = defaultdict(int)
        for r in range(128):
            for c in range(127):
                xor_val = self.get_value(r, c) ^ self.get_value(r, c + 1)
                xor_freq[abs(xor_val)] += 1

        cfb_xor_counts = {n: xor_freq.get(n, 0) for n in CFB_NUMBERS}
        print(f"\n  Adjacent horizontal XOR frequency for CFB numbers:")
        for n, count in sorted(cfb_xor_counts.items()):
            print(f"    XOR = {n}: {count} occurrences")

        self.results['statistics'] = {
            'global_xor': global_xor,
            'quadrant_xors': quadrant_xors,
            'cfb_xor_frequency': cfb_xor_counts,
        }

    def run(self):
        """Run full XOR network analysis"""
        self.analyze_vision_center()
        self.build_xor_graph()
        self.trace_xor_chains()
        self.find_hidden_patterns()
        self.compute_statistics()

        # Summary
        print("\n" + "═" * 70)
        print("XOR NETWORK ANALYSIS SUMMARY")
        print("═" * 70)

        print(f"\n  Vision Center XOR to CFB: {self.results['vision_center_analysis'].get('xor_to_cfb_count', 0)} cells")
        print(f"  Adjacent CFB XOR pairs: {self.results['xor_to_cfb'].get('total_pairs', 0)}")
        print(f"  Chains returning to CFB: {self.results['xor_chains'].get('returning_to_cfb', 0)}")
        print(f"  Hidden patterns found: {len(self.results['hidden_patterns'])}")

        # Save results
        output_file = SCRIPT_DIR / 'XOR_NETWORK_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n  Results saved to: {output_file}")

        return self.results

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    analyzer = XORNetworkAnalyzer()
    analyzer.run()
