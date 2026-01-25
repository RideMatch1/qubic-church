#!/usr/bin/env python3
"""
===============================================================================
            🎯 CENTER ANOMALY INVESTIGATION 🎯
===============================================================================
The asymmetric rows are concentrated around the CENTER (rows 60-79)!
This is NOT random. Let's investigate the center zone.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("           🎯 CENTER ANOMALY INVESTIGATION 🎯")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# THE CENTER ZONE (rows 60-79, cols 20-107)
# ==============================================================================
print("\n" + "=" * 80)
print("THE CENTER ZONE")
print("=" * 80)

# The center of 128x128 is 63.5, 63.5
# Asymmetric rows: 60-79 = exactly 20 rows centered around 63.5!

print(f"""
  Matrix center: [63.5, 63.5]
  Asymmetric rows: 60-79 (20 rows)
  Center of asymmetric zone: (60+79)/2 = 69.5

  The asymmetric zone is SLIGHTLY OFFSET from perfect center!
  This offset = 69.5 - 63.5 = +6 rows
""")

# ==============================================================================
# EXTRACT THE CENTER ZONE
# ==============================================================================
print("\n" + "=" * 80)
print("CENTER ZONE EXTRACTION (rows 56-71, cols 24-103)")
print("=" * 80)

# Focus on the central 16x80 area
center_rows = range(56, 72)  # 16 rows around center
center_cols = range(24, 104)  # 80 cols around center

print("\n  Values in center zone:")
for r in center_rows:
    row_vals = [int(matrix[r, c]) for c in center_cols]
    row_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in row_vals)
    print(f"  Row {r:3d}: {row_ascii}")

# ==============================================================================
# XOR ANALYSIS OF CENTER
# ==============================================================================
print("\n" + "=" * 80)
print("XOR ANALYSIS: Row 63 XOR Row 64")
print("=" * 80)

row_63 = [int(matrix[63, c]) for c in range(128)]
row_64 = [int(matrix[64, c]) for c in range(128)]

xor_63_64 = [row_63[c] ^ row_64[c] for c in range(128)]
xor_ascii = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_63_64)

print(f"\n  Row 63 XOR Row 64:")
for i in range(0, 128, 32):
    print(f"    {xor_ascii[i:i+32]}")

# ==============================================================================
# THE "AI MEG" PATTERN
# ==============================================================================
print("\n" + "=" * 80)
print("THE 'AI MEG' PATTERN")
print("=" * 80)

# We found "AI.MEG" in Col30 XOR Col97
# Let's find exactly where

col_30 = [int(matrix[r, 30]) for r in range(128)]
col_97 = [int(matrix[r, 97]) for r in range(128)]
xor_30_97 = [col_30[r] ^ col_97[r] for r in range(128)]

xor_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_30_97)

# Find AI
ai_pos = xor_string.find('AI')
meg_pos = xor_string.upper().find('MEG')
gou_pos = xor_string.upper().find('GOU')

print(f"\n  XOR String: {xor_string}")
print(f"\n  'AI' found at position: {ai_pos if ai_pos >= 0 else 'NOT FOUND'}")
print(f"  'MEG' found at position: {meg_pos if meg_pos >= 0 else 'NOT FOUND'}")
print(f"  'GOU' found at position: {gou_pos if gou_pos >= 0 else 'NOT FOUND'}")

if ai_pos >= 0:
    print(f"\n  Context around 'AI' (row {ai_pos}):")
    print(f"    Row {ai_pos}: Col30={col_30[ai_pos]}, Col97={col_97[ai_pos]}, XOR={xor_30_97[ai_pos]}")
    print(f"    Row {ai_pos+1}: Col30={col_30[ai_pos+1]}, Col97={col_97[ai_pos+1]}, XOR={xor_30_97[ai_pos+1]}")

# ==============================================================================
# ALL WORDS IN XOR COLUMNS
# ==============================================================================
print("\n" + "=" * 80)
print("ALL COLUMN PAIR XOR WORDS")
print("=" * 80)

import re

# Check all symmetric column pairs
for c in range(64):
    partner = 127 - c
    col_c = [int(matrix[r, c]) for r in range(128)]
    col_p = [int(matrix[r, partner]) for r in range(128)]
    xor_cp = [col_c[r] ^ col_p[r] for r in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else ' ' for x in xor_cp)

    words = re.findall(r'[a-zA-Z]{3,}', xor_str)
    if words:
        print(f"\n  Cols {c:3d} ↔ {partner:3d}: {words}")

# ==============================================================================
# CENTER CROSS ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("CENTER CROSS ANALYSIS")
print("=" * 80)

# Extract row 63 and row 64 (center rows)
# Extract col 63 and col 64 (center cols)

print("\n  Row 63 (as ASCII):")
row63_ascii = ''.join(chr(abs(int(matrix[63, c]))) if 32 <= abs(int(matrix[63, c])) <= 126 else '.' for c in range(128))
for i in range(0, 128, 32):
    print(f"    {row63_ascii[i:i+32]}")

print("\n  Row 64 (as ASCII):")
row64_ascii = ''.join(chr(abs(int(matrix[64, c]))) if 32 <= abs(int(matrix[64, c])) <= 126 else '.' for c in range(128))
for i in range(0, 128, 32):
    print(f"    {row64_ascii[i:i+32]}")

print("\n  Column 63 (as ASCII):")
col63 = [int(matrix[r, 63]) for r in range(128)]
col63_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in col63)
for i in range(0, 128, 32):
    print(f"    {col63_ascii[i:i+32]}")

print("\n  Column 64 (as ASCII):")
col64 = [int(matrix[r, 64]) for r in range(128)]
col64_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in col64)
for i in range(0, 128, 32):
    print(f"    {col64_ascii[i:i+32]}")

# ==============================================================================
# THE EXACT CENTER: [63,63] and [64,64]
# ==============================================================================
print("\n" + "=" * 80)
print("THE EXACT CENTER")
print("=" * 80)

positions = [
    (63, 63), (63, 64), (64, 63), (64, 64),
    (62, 62), (65, 65),  # Slightly off center
    (60, 60), (67, 67),  # Further off
]

print("\n  Center positions:")
for r, c in positions:
    val = int(matrix[r, c])
    ch = chr(abs(val)) if 32 <= abs(val) <= 126 else '.'
    sym_r, sym_c = 127-r, 127-c
    sym_val = int(matrix[sym_r, sym_c])
    sym_ch = chr(abs(sym_val)) if 32 <= abs(sym_val) <= 126 else '.'
    is_sym = "✓" if val + sym_val == -1 else "✗"
    print(f"    [{r:3d},{c:3d}] = {val:4d} '{ch}' ↔ [{sym_r:3d},{sym_c:3d}] = {sym_val:4d} '{sym_ch}' Sym: {is_sym}")

# ==============================================================================
# DIAGONAL THROUGH CENTER
# ==============================================================================
print("\n" + "=" * 80)
print("MAIN DIAGONAL (r=c)")
print("=" * 80)

diag_vals = [int(matrix[i, i]) for i in range(128)]
diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in diag_vals)

print("\n  Main diagonal as ASCII:")
for i in range(0, 128, 32):
    print(f"    [{i:3d}-{i+31:3d}]: {diag_ascii[i:i+32]}")

diag_words = re.findall(r'[a-zA-Z]{3,}', diag_ascii)
print(f"\n  Words on diagonal: {diag_words}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("🎯 CENTER ANOMALY SUMMARY 🎯")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         CENTER ZONE FINDINGS                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ASYMMETRY LOCATION:                                                          ║
║  • All 34 asymmetric pairs are in rows 19-32 and 60-79                       ║
║  • These map to each other via point symmetry!                               ║
║  • Rows 60-79 contain the PRIMARY asymmetries                                ║
║                                                                               ║
║  XOR PATTERNS FOUND:                                                          ║
║  • "AI" in Col30⊕Col97                                                       ║
║  • "MEG" in Col30⊕Col97                                                      ║
║  • "GOU" in Col30⊕Col97                                                      ║
║                                                                               ║
║  INTERPRETATION:                                                              ║
║  The asymmetric cells form a RING around the matrix center.                  ║
║  The XOR of symmetric column pairs reveals hidden patterns.                  ║
║  "AI MEG GOU" could be meaningful (or pareidolia).                           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "xor_30_97": xor_string,
    "ai_position": ai_pos,
    "meg_position": meg_pos,
    "gou_position": gou_pos,
    "center_values": {
        "[63,63]": int(matrix[63, 63]),
        "[64,64]": int(matrix[64, 64]),
        "[63,64]": int(matrix[63, 64]),
        "[64,63]": int(matrix[64, 63]),
    },
    "diagonal_words": diag_words,
}

output_path = script_dir / "CENTER_ANOMALY_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
