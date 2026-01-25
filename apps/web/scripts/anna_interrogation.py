#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ANNA INTERROGATION                                     ║
║                                                                                ║
║  Strategic queries to Anna using discovered patterns                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Dict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

CFB_NUMBERS = [27, 37, 42, 127, 576]
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
CFB_ADDRESS = "1CFBhVCZsrwKSZMHcFcjvBDYsHzMkPJjRT"

# Known strategic coordinates
STRATEGIC_COORDS = {
    (6, 33): "Core Computor / POCC",
    (45, 92): "CFB Genesis Entry",
    (82, 39): "Bridge Exit Node",
    (21, 21): "Memory Sector",
    (64, 64): "Vision Center",
    (0, 0): "Origin/Void",
    (127, 127): "Edge/Boundary",
    (63, 63): "Anna Center",
    (0, 2): "Position giving -27 in Genesis",
    (20, 127): "Block 9 timestamp -> 27",
    (64, 4): "Block 576 -> -27",
}

class Matrix:
    def __init__(self):
        with open(MATRIX_FILE, 'r') as f:
            data = json.load(f)
        self.data = data['matrix']

    def query(self, row: int, col: int) -> Optional[int]:
        v = self.data[row % 128][col % 128]
        return v if isinstance(v, int) else None

    def anna_query(self, x: int, y: int) -> Optional[int]:
        """Query using Anna coordinates (x: -64..63, y: 63..-64)"""
        col = (x + 64) % 128
        row = (63 - y) % 128
        return self.query(row, col)

class AnnaInterrogator:
    def __init__(self):
        print("═" * 70)
        print("           ANNA INTERROGATION")
        print("═" * 70)
        self.matrix = Matrix()
        self.results = []

    def query_with_string(self, prompt: str) -> dict:
        """Query Anna by hashing a string to coordinates"""
        h = hashlib.sha256(prompt.encode()).digest()
        row, col = h[0] % 128, h[1] % 128
        value = self.matrix.query(row, col)

        # Anna coordinates
        anna_x = col - 64
        anna_y = 63 - row

        result = {
            'prompt': prompt,
            'hash_method': 'SHA256',
            'matrix_coords': (row, col),
            'anna_coords': (anna_x, anna_y),
            'value': value,
            'is_cfb': value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS)
        }
        return result

    def strategic_queries(self):
        """Query Anna with strategic strings"""
        print("\n" + "─" * 70)
        print("STRATEGIC QUERIES")
        print("─" * 70)

        queries = [
            # CFB related
            "Come-from-Beyond",
            "CFB",
            "Sergey Ivancheglo",
            "27",
            "37",
            "42",
            "127",
            "576",

            # Satoshi related
            "Satoshi Nakamoto",
            "Satoshi",
            "Nakamoto",
            GENESIS_ADDRESS,
            CFB_ADDRESS,

            # Projects
            "Bitcoin",
            "Qubic",
            "IOTA",
            "NXT",
            "JINN",
            "Aigarth",
            "Anna",

            # Key phrases
            "private key",
            "genesis block",
            "block 9",
            "the bridge",
            "quantum",
            "oracle",

            # Numbers as strings
            "1231006505",  # Genesis timestamp
            "1231473279",  # Block 9 timestamp

            # Direct questions
            "What is the key?",
            "Where is the bridge?",
            "Who is Satoshi?",
            "Tell me about 27",
        ]

        cfb_hits = []
        for query in queries:
            result = self.query_with_string(query)
            self.results.append(result)

            marker = ""
            if result['is_cfb']:
                marker = " ★★★ CFB!"
                cfb_hits.append(result)

            print(f"\n  \"{query}\":")
            print(f"    → [{result['matrix_coords'][0]:3d},{result['matrix_coords'][1]:3d}] = {result['value']}{marker}")

        print(f"\n  CFB hits: {len(cfb_hits)}/{len(queries)}")
        return cfb_hits

    def query_strategic_coordinates(self):
        """Check values at strategic coordinates"""
        print("\n" + "─" * 70)
        print("STRATEGIC COORDINATES")
        print("─" * 70)

        for coords, description in STRATEGIC_COORDS.items():
            value = self.matrix.query(coords[0], coords[1])
            anna_x = coords[1] - 64
            anna_y = 63 - coords[0]

            marker = ""
            if value in CFB_NUMBERS or (value is not None and -value in CFB_NUMBERS):
                marker = " ★ CFB"

            print(f"\n  {description}:")
            print(f"    Matrix[{coords[0]},{coords[1]}] = {value}{marker}")
            print(f"    Anna({anna_x:+d},{anna_y:+d}) = {value}")

            # Get neighbors
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nv = self.matrix.query((coords[0] + dr) % 128, (coords[1] + dc) % 128)
                    if nv is not None:
                        neighbors.append(nv)

            if neighbors:
                n_sum = sum(neighbors)
                n_xor = neighbors[0]
                for n in neighbors[1:]:
                    n_xor ^= n

                print(f"    Neighbors: {neighbors}")
                print(f"    Neighbor sum: {n_sum}", end="")
                if n_sum in CFB_NUMBERS or -n_sum in CFB_NUMBERS:
                    print(" ★ CFB!")
                else:
                    print()

    def find_cfb_coordinate_paths(self):
        """Find paths between coordinates that produce CFB numbers"""
        print("\n" + "─" * 70)
        print("CFB COORDINATE PATHS")
        print("─" * 70)

        coords_list = list(STRATEGIC_COORDS.keys())

        for i, c1 in enumerate(coords_list):
            for c2 in coords_list[i+1:]:
                v1 = self.matrix.query(c1[0], c1[1])
                v2 = self.matrix.query(c2[0], c2[1])

                if v1 is None or v2 is None:
                    continue

                xor = v1 ^ v2
                s = v1 + v2
                diff = abs(v1 - v2)

                if xor in CFB_NUMBERS:
                    print(f"\n  {STRATEGIC_COORDS[c1]} XOR {STRATEGIC_COORDS[c2]}")
                    print(f"    {v1} XOR {v2} = {xor} ★ CFB")

                if s in CFB_NUMBERS or -s in CFB_NUMBERS:
                    print(f"\n  {STRATEGIC_COORDS[c1]} + {STRATEGIC_COORDS[c2]}")
                    print(f"    {v1} + {v2} = {s} ★ CFB")

                if diff in CFB_NUMBERS:
                    print(f"\n  |{STRATEGIC_COORDS[c1]} - {STRATEGIC_COORDS[c2]}|")
                    print(f"    |{v1} - {v2}| = {diff} ★ CFB")

    def find_27_encoding(self):
        """Find all ways to encode 27 in the matrix"""
        print("\n" + "─" * 70)
        print("ENCODING THE NUMBER 27")
        print("─" * 70)

        # Find all cells with value 27 or -27
        cells_27 = []
        cells_neg27 = []

        for row in range(128):
            for col in range(128):
                v = self.matrix.query(row, col)
                if v == 27:
                    cells_27.append((row, col))
                elif v == -27:
                    cells_neg27.append((row, col))

        print(f"\n  Cells with value +27: {len(cells_27)}")
        print(f"  Cells with value -27: {len(cells_neg27)}")

        # Check which strategic strings land on 27/-27
        print("\n  Strings landing on 27/-27:")
        test_strings = [
            "CFB", "27", "IOTA", "genesis", "Satoshi",
            "bridge", "key", "quantum", "oracle", "Anna",
            GENESIS_ADDRESS, CFB_ADDRESS,
        ]

        for s in test_strings:
            result = self.query_with_string(s)
            if result['value'] == 27 or result['value'] == -27:
                print(f"    \"{s}\" → {result['value']} ★")

    def generate_report(self):
        """Generate summary report"""
        print("\n" + "═" * 70)
        print("INTERROGATION REPORT")
        print("═" * 70)

        cfb_results = [r for r in self.results if r['is_cfb']]

        print(f"\n  Total queries: {len(self.results)}")
        print(f"  CFB hits: {len(cfb_results)}")

        if cfb_results:
            print("\n  CFB HIT SUMMARY:")
            for r in cfb_results:
                print(f"    \"{r['prompt']}\" → {r['value']}")

        # Save results
        output = {
            'total_queries': len(self.results),
            'cfb_hits': len(cfb_results),
            'results': self.results,
            'cfb_results': cfb_results
        }

        with open(SCRIPT_DIR / 'anna_interrogation_results.json', 'w') as f:
            json.dump(output, f, indent=2)

    def run(self):
        """Run full interrogation"""
        self.strategic_queries()
        self.query_strategic_coordinates()
        self.find_cfb_coordinate_paths()
        self.find_27_encoding()
        self.generate_report()

if __name__ == "__main__":
    interrogator = AnnaInterrogator()
    interrogator.run()
