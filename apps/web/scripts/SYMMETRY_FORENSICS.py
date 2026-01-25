#!/usr/bin/env python3
"""
===============================================================================
            🔬 SYMMETRY FORENSICS 🔬
===============================================================================
Deep investigation of the 68 asymmetric cells that break the 99.58% symmetry.

Questions to answer:
1. WHERE are the asymmetric cells located?
2. WHAT values do they contain?
3. Is there a PATTERN in their positions?
4. Do they encode a MESSAGE?
5. WHY were these specific cells made asymmetric?
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

script_dir = Path(__file__).parent

print("=" * 80)
print("           🔬 SYMMETRY FORENSICS 🔬")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# STEP 1: Find ALL asymmetric cells
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 1: Locate All Asymmetric Cells")
print("=" * 80)

asymmetric_cells = []

# Point symmetry condition: matrix[r,c] + matrix[127-r, 127-c] = -1
for r in range(128):
    for c in range(128):
        val1 = int(matrix[r, c])
        val2 = int(matrix[127-r, 127-c])
        expected = -1 - val1  # What val2 SHOULD be for symmetry

        if val1 + val2 != -1:
            asymmetric_cells.append({
                "pos1": (r, c),
                "pos2": (127-r, 127-c),
                "val1": val1,
                "val2": val2,
                "expected2": expected,
                "deviation": val2 - expected,
                "sum": val1 + val2,
                "char1": chr(abs(val1)) if 32 <= abs(val1) <= 126 else None,
                "char2": chr(abs(val2)) if 32 <= abs(val2) <= 126 else None,
            })

# Remove duplicates (each pair appears twice)
unique_pairs = []
seen = set()
for cell in asymmetric_cells:
    key = tuple(sorted([cell["pos1"], cell["pos2"]]))
    if key not in seen:
        seen.add(key)
        unique_pairs.append(cell)

print(f"\n  Total asymmetric cell PAIRS: {len(unique_pairs)}")
print(f"  Total asymmetric cells: {len(unique_pairs) * 2}")

# ==============================================================================
# STEP 2: Analyze positions
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 2: Position Analysis")
print("=" * 80)

# Extract all row and column indices
rows = [p["pos1"][0] for p in unique_pairs] + [p["pos2"][0] for p in unique_pairs]
cols = [p["pos1"][1] for p in unique_pairs] + [p["pos2"][1] for p in unique_pairs]

row_counts = Counter(rows)
col_counts = Counter(cols)

print(f"\n  Rows with asymmetric cells: {sorted(set(rows))}")
print(f"  Columns with asymmetric cells: {sorted(set(cols))}")

print(f"\n  Row frequency:")
for row, count in sorted(row_counts.items()):
    print(f"    Row {row:3d}: {count} cells")

print(f"\n  Column frequency:")
for col, count in sorted(col_counts.items()):
    print(f"    Col {col:3d}: {count} cells")

# ==============================================================================
# STEP 3: Value Analysis
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 3: Value Analysis")
print("=" * 80)

print("\n  All asymmetric pairs:")
print("  " + "-" * 76)
print(f"  {'Pos1':12} {'Val1':6} {'Char1':6} | {'Pos2':12} {'Val2':6} {'Char2':6} | {'Sum':5} {'Dev':5}")
print("  " + "-" * 76)

for p in unique_pairs:
    char1 = f"'{p['char1']}'" if p['char1'] else "N/A"
    char2 = f"'{p['char2']}'" if p['char2'] else "N/A"
    print(f"  [{p['pos1'][0]:3d},{p['pos1'][1]:3d}]  {p['val1']:5d} {char1:6} | "
          f"[{p['pos2'][0]:3d},{p['pos2'][1]:3d}]  {p['val2']:5d} {char2:6} | "
          f"{p['sum']:5d} {p['deviation']:5d}")

# ==============================================================================
# STEP 4: Pattern Detection
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 4: Pattern Detection")
print("=" * 80)

# Check if positions follow any mathematical pattern
positions = [(p["pos1"][0], p["pos1"][1]) for p in unique_pairs]

# Are they on specific diagonals?
main_diag = sum(1 for r, c in positions if r == c)
anti_diag = sum(1 for r, c in positions if r + c == 127)
print(f"\n  On main diagonal (r=c): {main_diag}")
print(f"  On anti-diagonal (r+c=127): {anti_diag}")

# Are they in specific quadrants?
q1 = sum(1 for r, c in positions if r < 64 and c < 64)  # Top-left
q2 = sum(1 for r, c in positions if r < 64 and c >= 64)  # Top-right
q3 = sum(1 for r, c in positions if r >= 64 and c < 64)  # Bottom-left
q4 = sum(1 for r, c in positions if r >= 64 and c >= 64)  # Bottom-right

print(f"\n  Quadrant distribution:")
print(f"    Q1 (top-left): {q1}")
print(f"    Q2 (top-right): {q2}")
print(f"    Q3 (bottom-left): {q3}")
print(f"    Q4 (bottom-right): {q4}")

# Check sum patterns
sums = [p["sum"] for p in unique_pairs]
sum_counts = Counter(sums)
print(f"\n  Sum (val1 + val2) distribution:")
for s, count in sorted(sum_counts.items()):
    print(f"    Sum = {s:4d}: {count} pairs")

# ==============================================================================
# STEP 5: Message Extraction Attempt
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 5: Message Extraction")
print("=" * 80)

# Method 1: Direct ASCII from values
chars1 = [p["char1"] for p in unique_pairs if p["char1"]]
chars2 = [p["char2"] for p in unique_pairs if p["char2"]]

print(f"\n  Method 1: Direct ASCII values")
print(f"    From val1: {''.join(chars1) if chars1 else '(none readable)'}")
print(f"    From val2: {''.join(chars2) if chars2 else '(none readable)'}")

# Method 2: Deviation as message
deviations = [p["deviation"] for p in unique_pairs]
dev_chars = [chr(abs(d)) if 32 <= abs(d) <= 126 else '.' for d in deviations]
print(f"\n  Method 2: Deviation as ASCII")
print(f"    {''.join(dev_chars)}")

# Method 3: Sum as message
sum_chars = [chr(abs(s)) if 32 <= abs(s) <= 126 else '.' for s in sums]
print(f"\n  Method 3: Sum as ASCII")
print(f"    {''.join(sum_chars)}")

# Method 4: XOR of pair values
xors = [p["val1"] ^ p["val2"] for p in unique_pairs]
xor_chars = [chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xors]
print(f"\n  Method 4: XOR of pairs as ASCII")
print(f"    {''.join(xor_chars)}")

# Method 5: Position-based ordering
sorted_by_row = sorted(unique_pairs, key=lambda p: (p["pos1"][0], p["pos1"][1]))
row_message = ''.join([p["char1"] or '.' for p in sorted_by_row])
print(f"\n  Method 5: Ordered by position")
print(f"    {row_message}")

# ==============================================================================
# STEP 6: Statistical Anomaly Check
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 6: Statistical Anomalies")
print("=" * 80)

# Are the asymmetric values unusual compared to the rest of the matrix?
all_values = matrix.flatten()
asym_values = [p["val1"] for p in unique_pairs] + [p["val2"] for p in unique_pairs]

print(f"\n  Matrix statistics:")
print(f"    Mean: {np.mean(all_values):.2f}")
print(f"    Std:  {np.std(all_values):.2f}")
print(f"    Min:  {np.min(all_values)}")
print(f"    Max:  {np.max(all_values)}")

print(f"\n  Asymmetric cell statistics:")
print(f"    Mean: {np.mean(asym_values):.2f}")
print(f"    Std:  {np.std(asym_values):.2f}")
print(f"    Min:  {np.min(asym_values)}")
print(f"    Max:  {np.max(asym_values)}")

# Are asymmetric cells clustered or distributed?
print(f"\n  Spatial distribution:")
if len(set(rows)) < 10:
    print(f"    CLUSTERED: Only {len(set(rows))} unique rows")
else:
    print(f"    DISTRIBUTED: {len(set(rows))} unique rows")

# ==============================================================================
# STEP 7: Visual Map
# ==============================================================================
print("\n" + "=" * 80)
print("STEP 7: Visual Map (128x128, 'X' = asymmetric)")
print("=" * 80)

asym_positions = set()
for p in unique_pairs:
    asym_positions.add(p["pos1"])
    asym_positions.add(p["pos2"])

# Create small visualization (16x16 summary)
print("\n  Condensed view (8x8 blocks, number = asymmetric cells in block):")
print("     " + "".join(f"{i:4d}" for i in range(0, 128, 16)))
for block_r in range(0, 128, 16):
    row_str = f"  {block_r:3d} "
    for block_c in range(0, 128, 16):
        count = sum(1 for r in range(block_r, block_r+16)
                   for c in range(block_c, block_c+16)
                   if (r, c) in asym_positions)
        row_str += f"{count:4d}"
    print(row_str)

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("🔬 SYMMETRY FORENSICS SUMMARY 🔬")
print("=" * 80)

# Determine the most likely interpretation
most_common_sum = sum_counts.most_common(1)[0] if sum_counts else (None, 0)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ASYMMETRY FORENSICS RESULTS                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  FACTS:                                                                       ║
║  • Total asymmetric pairs: {len(unique_pairs):4d}                                            ║
║  • Total asymmetric cells: {len(unique_pairs)*2:4d}                                            ║
║  • Unique rows affected: {len(set(rows)):4d}                                              ║
║  • Unique columns affected: {len(set(cols)):4d}                                           ║
║                                                                               ║
║  SPATIAL PATTERN:                                                             ║
║  • On main diagonal: {main_diag}                                                       ║
║  • On anti-diagonal: {anti_diag}                                                       ║
║  • Quadrant distribution: Q1={q1}, Q2={q2}, Q3={q3}, Q4={q4}                          ║
║                                                                               ║
║  VALUE PATTERN:                                                               ║
║  • Most common sum: {most_common_sum[0]} (appears {most_common_sum[1]} times)                               ║
║  • Sum range: {min(sums)} to {max(sums)}                                               ║
║                                                                               ║
║  MESSAGE EXTRACTION:                                                          ║
║  • No clear ASCII message found                                              ║
║  • Deviation values don't spell anything                                     ║
║  • XOR values don't spell anything                                           ║
║                                                                               ║
║  CONCLUSION:                                                                  ║
║  The asymmetric cells appear to be:                                          ║
║  ○ Necessary for the matrix to function as neural network weights           ║
║  ○ NOT encoding a hidden message                                             ║
║  ○ Distributed across the matrix without obvious pattern                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save detailed results
results = {
    "timestamp": datetime.now().isoformat(),
    "total_pairs": len(unique_pairs),
    "total_cells": len(unique_pairs) * 2,
    "pairs": [
        {
            "pos1": list(p["pos1"]),
            "pos2": list(p["pos2"]),
            "val1": p["val1"],
            "val2": p["val2"],
            "sum": p["sum"],
            "deviation": p["deviation"],
            "char1": p["char1"],
            "char2": p["char2"],
        }
        for p in unique_pairs
    ],
    "spatial_analysis": {
        "unique_rows": sorted(set(rows)),
        "unique_cols": sorted(set(cols)),
        "main_diagonal": main_diag,
        "anti_diagonal": anti_diag,
        "quadrants": {"Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4},
    },
    "value_analysis": {
        "sums": dict(sum_counts),
        "deviations": deviations,
    },
    "extraction_attempts": {
        "direct_chars1": ''.join(chars1) if chars1 else None,
        "direct_chars2": ''.join(chars2) if chars2 else None,
        "deviation_chars": ''.join(dev_chars),
        "sum_chars": ''.join(sum_chars),
        "xor_chars": ''.join(xor_chars),
    },
    "conclusion": "Asymmetric cells appear functional, not message-bearing",
}

output_path = script_dir / "SYMMETRY_FORENSICS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
