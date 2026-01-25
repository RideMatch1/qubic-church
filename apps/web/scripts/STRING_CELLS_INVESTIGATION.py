#!/usr/bin/env python3
"""
===============================================================================
            🔤 STRING CELLS INVESTIGATION 🔤
===============================================================================
The Anna-Matrix contains 26 cells with string values ("00000000") instead of
integers. Where are they? What pattern do they form?
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re

script_dir = Path(__file__).parent

print("=" * 80)
print("           🔤 STRING CELLS INVESTIGATION 🔤")
print("           Finding the 26 mysterious string cells")
print("=" * 80)

# Load matrix (raw, without conversion)
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

raw_matrix = data["matrix"]

# ==============================================================================
# FIND ALL STRING CELLS
# ==============================================================================
print("\n" + "=" * 80)
print("LOCATING STRING CELLS")
print("=" * 80)

string_cells = []
for r in range(128):
    for c in range(128):
        val = raw_matrix[r][c]
        if isinstance(val, str):
            string_cells.append({
                "row": r,
                "col": c,
                "value": val,
                "partner_row": 127 - r,
                "partner_col": 127 - c,
            })

print(f"\n  Found {len(string_cells)} string cells:")
print("  " + "-" * 60)

for cell in string_cells:
    r, c = cell["row"], cell["col"]
    val = cell["value"]
    partner_r, partner_c = cell["partner_row"], cell["partner_col"]
    partner_val = raw_matrix[partner_r][partner_c]

    print(f"  [{r:3d},{c:3d}] = '{val}' | Partner [{partner_r:3d},{partner_c:3d}] = {partner_val}")

# ==============================================================================
# ANALYZE POSITIONS
# ==============================================================================
print("\n" + "=" * 80)
print("POSITION ANALYSIS")
print("=" * 80)

rows = [c["row"] for c in string_cells]
cols = [c["col"] for c in string_cells]

print(f"\n  Row distribution:")
print(f"    Unique rows: {sorted(set(rows))}")
print(f"    Row range: {min(rows)} to {max(rows)}")

print(f"\n  Column distribution:")
print(f"    Unique cols: {sorted(set(cols))}")
print(f"    Col range: {min(cols)} to {max(cols)}")

# Check if they form a pattern
print(f"\n  Pattern check:")
print(f"    All in same row? {'YES' if len(set(rows)) == 1 else 'NO'}")
print(f"    All in same col? {'YES' if len(set(cols)) == 1 else 'NO'}")
print(f"    On main diagonal? {'YES' if all(r == c for r, c in zip(rows, cols)) else 'NO'}")
print(f"    On anti-diagonal? {'YES' if all(r + c == 127 for r, c in zip(rows, cols)) else 'NO'}")

# Check row + col sums
sums = [r + c for r, c in zip(rows, cols)]
print(f"\n  Row + Col sums: {sorted(set(sums))}")

# ==============================================================================
# SYMMETRY CHECK
# ==============================================================================
print("\n" + "=" * 80)
print("SYMMETRY CHECK")
print("=" * 80)

# Are string cells symmetric?
symmetric_pairs = 0
for cell in string_cells:
    r, c = cell["row"], cell["col"]
    partner_r, partner_c = 127 - r, 127 - c

    # Check if partner is also a string
    partner_val = raw_matrix[partner_r][partner_c]
    if isinstance(partner_val, str):
        symmetric_pairs += 1

print(f"\n  String cells with string partners: {symmetric_pairs}/{len(string_cells)}")

# ==============================================================================
# DECODE THE STRING VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("STRING VALUE ANALYSIS")
print("=" * 80)

unique_values = set(c["value"] for c in string_cells)
print(f"\n  Unique string values: {unique_values}")

for val in unique_values:
    cells_with_val = [c for c in string_cells if c["value"] == val]
    print(f"\n  Value '{val}':")
    print(f"    Count: {len(cells_with_val)}")
    print(f"    Positions: {[(c['row'], c['col']) for c in cells_with_val]}")

    # Try to interpret
    if val == "00000000":
        print(f"    Interpretation: 8 zeros = NULL/empty?")
        print(f"    Binary: 00000000 = 0")
        print(f"    Hex: 0x00000000")
        print(f"    ASCII: 8 x NUL character")

# ==============================================================================
# VISUAL MAP
# ==============================================================================
print("\n" + "=" * 80)
print("VISUAL MAP (128x128 grid, 'S' = string cell)")
print("=" * 80)

# Create a simplified 16x16 view (each cell = 8x8 block)
block_map = [[' ' for _ in range(16)] for _ in range(16)]

for cell in string_cells:
    block_r = cell["row"] // 8
    block_c = cell["col"] // 8
    block_map[block_r][block_c] = 'S'

print("\n  16x16 block view (each block = 8x8 cells):")
print("  " + "".join(f"{i:2}" for i in range(16)))
print("  " + "-" * 32)
for r, row in enumerate(block_map):
    print(f"  {r:2}|" + " ".join(row))

# ==============================================================================
# RELATIONSHIP TO KNOWN HOTSPOTS
# ==============================================================================
print("\n" + "=" * 80)
print("RELATIONSHIP TO KNOWN HOTSPOTS")
print("=" * 80)

# Known hotspots: Col30↔97, Col22↔105
hotspot_cols = [22, 30, 97, 105]

string_in_hotspots = [c for c in string_cells if c["col"] in hotspot_cols or c["row"] in hotspot_cols]
print(f"\n  String cells in hotspot columns/rows: {len(string_in_hotspots)}")
for c in string_in_hotspots:
    print(f"    [{c['row']},{c['col']}]")

# ==============================================================================
# MATHEMATICAL PROPERTIES
# ==============================================================================
print("\n" + "=" * 80)
print("MATHEMATICAL PROPERTIES")
print("=" * 80)

# Check if positions have special properties
print("\n  Position properties:")
for cell in string_cells[:10]:  # First 10
    r, c = cell["row"], cell["col"]
    print(f"    [{r},{c}]: r+c={r+c}, r*c={r*c}, r^c={r^c}, |r-c|={abs(r-c)}")

# Check for Fibonacci positions
fib = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
fib_positions = [(c["row"], c["col"]) for c in string_cells if c["row"] in fib or c["col"] in fib]
print(f"\n  Cells at Fibonacci row/col: {fib_positions}")

# Check for prime positions
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

prime_positions = [(c["row"], c["col"]) for c in string_cells if is_prime(c["row"]) or is_prime(c["col"])]
print(f"  Cells at prime row/col: {len(prime_positions)} cells")

# ==============================================================================
# XOR WITH NEIGHBORS
# ==============================================================================
print("\n" + "=" * 80)
print("NEIGHBOR ANALYSIS")
print("=" * 80)

# Convert matrix for neighbor analysis
def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

int_matrix = np.array([[safe_int(v) for v in row] for row in raw_matrix])

print("\n  Neighbors of string cells (treating string as 0):")
for cell in string_cells[:5]:  # First 5
    r, c = cell["row"], cell["col"]
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 128 and 0 <= nc < 128:
                neighbors.append(int_matrix[nr, nc])

    avg_neighbor = np.mean(neighbors)
    print(f"    [{r},{c}]: neighbors avg = {avg_neighbor:.1f}, neighbors = {neighbors}")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("🔤 STRING CELLS INVESTIGATION COMPLETE 🔤")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         STRING CELLS FINDINGS                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  BASIC FACTS:                                                                 ║
║  • Total string cells: {len(string_cells):2}                                               ║
║  • Unique values: {str(unique_values)[:45]:45}     ║
║  • Row range: {min(rows):3} to {max(rows):3}                                            ║
║  • Col range: {min(cols):3} to {max(cols):3}                                            ║
║                                                                               ║
║  SYMMETRY:                                                                    ║
║  • Cells with string partners: {symmetric_pairs}/{len(string_cells)}                              ║
║                                                                               ║
║  PATTERN:                                                                     ║
║  • Same row: {'YES' if len(set(rows)) == 1 else 'NO ':3}                                                     ║
║  • Same col: {'YES' if len(set(cols)) == 1 else 'NO ':3}                                                     ║
║  • In hotspot cols: {len(string_in_hotspots):2}                                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "total_string_cells": len(string_cells),
    "string_cells": string_cells,
    "unique_values": list(unique_values),
    "row_range": [min(rows), max(rows)],
    "col_range": [min(cols), max(cols)],
    "symmetric_pairs": symmetric_pairs,
    "in_hotspot_cols": len(string_in_hotspots),
}

output_path = script_dir / "STRING_CELLS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
