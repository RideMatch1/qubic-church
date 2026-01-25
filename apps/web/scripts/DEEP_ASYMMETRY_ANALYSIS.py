#!/usr/bin/env python3
"""
===============================================================================
            DEEP ASYMMETRY ANALYSIS
===============================================================================
Analyze all 68 asymmetric cells in detail.
What values do they have? Is there a pattern?
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

script_dir = Path(__file__).parent

print("=" * 80)
print("           DEEP ASYMMETRY ANALYSIS")
print("           Analyzing 68 asymmetric cells")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
raw_matrix = data["matrix"]

# ==============================================================================
# FIND ALL ASYMMETRIC CELLS
# ==============================================================================
print("\n" + "=" * 80)
print("FINDING ASYMMETRIC CELLS")
print("=" * 80)

asymmetric_cells = []

for r in range(64):  # Only check first half to avoid duplicates
    for c in range(128):
        partner_r, partner_c = 127 - r, 127 - c
        val = matrix[r, c]
        partner_val = matrix[partner_r, partner_c]

        if val + partner_val != -1:
            # Check if either is a string
            is_string = isinstance(raw_matrix[r][c], str) or isinstance(raw_matrix[partner_r][partner_c], str)

            asymmetric_cells.append({
                "pos": (r, c),
                "partner_pos": (partner_r, partner_c),
                "value": int(val),
                "partner_value": int(partner_val),
                "sum": int(val + partner_val),
                "expected_sum": -1,
                "deviation": int(val + partner_val + 1),
                "is_string": is_string,
                "xor": int(val) ^ int(partner_val),
            })

print(f"\n  Total asymmetric cell pairs: {len(asymmetric_cells)}")
print(f"  Total asymmetric cells: {len(asymmetric_cells) * 2}")

# ==============================================================================
# CATEGORIZE BY COLUMN
# ==============================================================================
print("\n" + "=" * 80)
print("DISTRIBUTION BY COLUMN")
print("=" * 80)

col_distribution = Counter(cell["pos"][1] for cell in asymmetric_cells)
col_distribution.update(cell["partner_pos"][1] for cell in asymmetric_cells)

print(f"\n  Columns with asymmetric cells:")
for col, count in col_distribution.most_common():
    partner_col = 127 - col
    print(f"    Col {col:3} (↔{partner_col:3}): {count} cells")

# ==============================================================================
# ANALYZE VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("VALUE ANALYSIS")
print("=" * 80)

values = [cell["value"] for cell in asymmetric_cells]
partner_values = [cell["partner_value"] for cell in asymmetric_cells]
sums = [cell["sum"] for cell in asymmetric_cells]
deviations = [cell["deviation"] for cell in asymmetric_cells]

print(f"\n  Value statistics:")
print(f"    Values range: {min(values)} to {max(values)}")
print(f"    Partner values range: {min(partner_values)} to {max(partner_values)}")
print(f"    Sums: {sorted(set(sums))}")
print(f"    Deviations from -1: {sorted(set(deviations))}")

# Most common sums
sum_counts = Counter(sums)
print(f"\n  Sum distribution:")
for s, count in sum_counts.most_common():
    print(f"    Sum = {s:4d} (deviation = {s+1:+d}): {count} pairs")

# ==============================================================================
# STRING CELLS VS NON-STRING
# ==============================================================================
print("\n" + "=" * 80)
print("STRING VS NON-STRING ASYMMETRIC CELLS")
print("=" * 80)

string_asym = [c for c in asymmetric_cells if c["is_string"]]
non_string_asym = [c for c in asymmetric_cells if not c["is_string"]]

print(f"\n  String-related asymmetric pairs: {len(string_asym)}")
print(f"  Non-string asymmetric pairs: {len(non_string_asym)}")

if non_string_asym:
    print(f"\n  Non-string asymmetric cells (pure numeric asymmetry):")
    for cell in non_string_asym[:20]:
        r, c = cell["pos"]
        val = cell["value"]
        pval = cell["partner_value"]
        ch = chr(abs(val)) if 32 <= abs(val) <= 126 else '.'
        pch = chr(abs(pval)) if 32 <= abs(pval) <= 126 else '.'
        print(f"    [{r:3},{c:3}]={val:4d}'{ch}' ↔ [{127-r:3},{127-c:3}]={pval:4d}'{pch}' sum={cell['sum']:+d}")

# ==============================================================================
# XOR PATTERN
# ==============================================================================
print("\n" + "=" * 80)
print("XOR PATTERN OF ASYMMETRIC CELLS")
print("=" * 80)

xor_values = [cell["xor"] for cell in asymmetric_cells]
xor_counts = Counter(xor_values)

print(f"\n  XOR value distribution:")
for xor, count in xor_counts.most_common(10):
    ch = chr(abs(xor)) if 32 <= abs(xor) <= 126 else '.'
    print(f"    XOR = {xor:4d} = '{ch}': {count} pairs")

# ==============================================================================
# GEOMETRIC PATTERN
# ==============================================================================
print("\n" + "=" * 80)
print("GEOMETRIC PATTERN")
print("=" * 80)

# Plot positions
rows = [c["pos"][0] for c in asymmetric_cells]
cols = [c["pos"][1] for c in asymmetric_cells]

print(f"\n  Asymmetric cell positions (first half):")
print(f"    Row range: {min(rows)} to {max(rows)}")
print(f"    Col range: {min(cols)} to {max(cols)}")
print(f"    Centroid: ({np.mean(rows):.1f}, {np.mean(cols):.1f})")

# Check if they form lines
print(f"\n  Row + Col sums (diagonal check):")
diag_sums = Counter(r + c for r, c in zip(rows, cols))
for s, count in diag_sums.most_common(5):
    print(f"    r + c = {s}: {count} cells")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("DEEP ASYMMETRY ANALYSIS COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ASYMMETRY SUMMARY                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  TOTAL:                                                                       ║
║  • Asymmetric pairs: {len(asymmetric_cells):3}                                               ║
║  • Total asymmetric cells: {len(asymmetric_cells)*2:3}                                          ║
║                                                                               ║
║  BREAKDOWN:                                                                   ║
║  • String-related: {len(string_asym):3} pairs                                               ║
║  • Pure numeric: {len(non_string_asym):3} pairs                                                ║
║                                                                               ║
║  COLUMNS WITH MOST ASYMMETRY:                                                 ║
║  • {list(col_distribution.most_common(3))}                                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save
results = {
    "timestamp": datetime.now().isoformat(),
    "total_pairs": len(asymmetric_cells),
    "total_cells": len(asymmetric_cells) * 2,
    "string_related": len(string_asym),
    "pure_numeric": len(non_string_asym),
    "column_distribution": dict(col_distribution),
    "sum_distribution": dict(sum_counts),
    "cells": asymmetric_cells,
}

with open(script_dir / "DEEP_ASYMMETRY_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved")
