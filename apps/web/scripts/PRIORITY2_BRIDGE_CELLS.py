#!/usr/bin/env python3
"""
===============================================================================
        PRIORITY 2: THE 8 BRIDGE CELLS DEEP ANALYSIS
===============================================================================
Understand why exactly 8 positions contain value 127.
Decode the coordinates as potential message.
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗ ██████╗ ██╗██████╗  ██████╗ ███████╗     ██████╗███████╗██╗     ██╗     ███████╗
   ██╔══██╗██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝    ██╔════╝██╔════╝██║     ██║     ██╔════╝
   ██████╔╝██████╔╝██║██║  ██║██║  ███╗█████╗      ██║     █████╗  ██║     ██║     ███████╗
   ██╔══██╗██╔══██╗██║██║  ██║██║   ██║██╔══╝      ██║     ██╔══╝  ██║     ██║     ╚════██║
   ██████╔╝██║  ██║██║██████╔╝╚██████╔╝███████╗    ╚██████╗███████╗███████╗███████╗███████║
   ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝     ╚═════╝╚══════╝╚══════╝╚══════╝╚══════╝
                       PRIORITY 2: BRIDGE CELLS ANALYSIS
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# The 8 Bridge Cells (value = 127)
bridge_cells = [
    (17, 76),
    (20, 78),
    (20, 120),
    (21, 15),
    (42, 63),
    (51, 51),
    (57, 124),
    (81, 108),
]

# ==============================================================================
# PHASE 1: VERIFY AND MAP
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 1: VERIFICATION AND MAPPING")
print("=" * 80)

print("\n  The 8 Bridge Cells (value = 127):")
print("  " + "-" * 70)

for i, (r, c) in enumerate(bridge_cells, 1):
    val = int(matrix[r, c])
    partner_r, partner_c = 127 - r, 127 - c
    partner_val = int(matrix[partner_r, partner_c])

    print(f"\n  Bridge {i}:")
    print(f"    Position: ({r}, {c})")
    print(f"    Value: {val}")
    print(f"    Partner: ({partner_r}, {partner_c}) = {partner_val}")
    print(f"    Sum r+c: {r + c}")
    print(f"    Symmetry: {val} + {partner_val} = {val + partner_val}")

# ==============================================================================
# PHASE 2: COORDINATE ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 2: COORDINATE PATTERNS")
print("=" * 80)

rows = [r for r, c in bridge_cells]
cols = [c for r, c in bridge_cells]

print(f"\n  Row values: {rows}")
print(f"  Col values: {cols}")
print(f"  Row sum: {sum(rows)}")
print(f"  Col sum: {sum(cols)}")

# XOR all rows
row_xor = 0
for r in rows:
    row_xor ^= r
print(f"\n  XOR of all rows: {row_xor}")

# XOR all cols
col_xor = 0
for c in cols:
    col_xor ^= c
print(f"  XOR of all cols: {col_xor}")

# As ASCII
print(f"\n  Rows as ASCII:")
for r in rows:
    if 32 <= r <= 126:
        print(f"    {r} = '{chr(r)}'")
    else:
        print(f"    {r} = (non-printable)")

print(f"\n  Cols as ASCII:")
for c in cols:
    if 32 <= c <= 126:
        print(f"    {c} = '{chr(c)}'")
    else:
        print(f"    {c} = (non-printable)")

# Combined as string
row_ascii = ''.join(chr(r) if 32 <= r <= 126 else '?' for r in rows)
col_ascii = ''.join(chr(c) if 32 <= c <= 126 else '?' for c in cols)
print(f"\n  Rows as string: '{row_ascii}'")
print(f"  Cols as string: '{col_ascii}'")

# ==============================================================================
# PHASE 3: POSITION DIFFERENCES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3: POSITION DIFFERENCES")
print("=" * 80)

print("\n  Differences between consecutive positions:")
for i in range(len(bridge_cells) - 1):
    r1, c1 = bridge_cells[i]
    r2, c2 = bridge_cells[i + 1]
    dr, dc = r2 - r1, c2 - c1
    print(f"    ({r1},{c1}) → ({r2},{c2}): Δr={dr:+d}, Δc={dc:+d}")

# ==============================================================================
# PHASE 4: r+c SUMS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 4: r+c SUM ANALYSIS")
print("=" * 80)

sums = [r + c for r, c in bridge_cells]
print(f"\n  r+c values: {sums}")
print(f"  Sorted: {sorted(sums)}")
print(f"  Sum of sums: {sum(sums)}")
print(f"  Mean: {np.mean(sums):.2f}")

# Check for patterns
print(f"\n  As ASCII (if printable):")
for s in sums:
    if 32 <= s <= 126:
        print(f"    {s} = '{chr(s)}'")

# ==============================================================================
# PHASE 5: NEIGHBOR VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 5: NEIGHBOR ANALYSIS")
print("=" * 80)

print("\n  Values surrounding each bridge cell:")

for r, c in bridge_cells:
    neighbors = []
    neighbor_positions = [
        (r-1, c), (r+1, c), (r, c-1), (r, c+1),  # Adjacent
        (r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1)  # Diagonal
    ]

    for nr, nc in neighbor_positions:
        if 0 <= nr < 128 and 0 <= nc < 128:
            neighbors.append(int(matrix[nr, nc]))

    ascii_neighbors = ''.join(chr(abs(n)) if 32 <= abs(n) <= 126 else '.' for n in neighbors)
    print(f"\n  ({r}, {c}):")
    print(f"    Neighbors: {neighbors[:4]} (adjacent), {neighbors[4:]} (diagonal)")
    print(f"    As ASCII: '{ascii_neighbors}'")

# ==============================================================================
# PHASE 6: SPECIAL POSITION (42, 63)
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 6: THE ANSWER POSITION (42, 63)")
print("=" * 80)

r, c = 42, 63

print(f"""
  Position (42, 63) is SPECIAL:

  42 = "The Answer to Life, the Universe, and Everything" (Hitchhiker's Guide)
  63 = Center of 0-127 range (127/2 ≈ 63.5)
  42 + 63 = 105

  Binary:
    42 = 0010 1010
    63 = 0011 1111 (all lower 6 bits set)

  XOR: 42 ^ 63 = {42 ^ 63}
  AND: 42 & 63 = {42 & 63}
  OR:  42 | 63 = {42 | 63}
""")

# Cross through (42, 63)
print("  Row 42 values around column 63:")
row42_around = [int(matrix[42, c]) for c in range(58, 69)]
print(f"    Cols 58-68: {row42_around}")

print("\n  Column 63 values around row 42:")
col63_around = [int(matrix[r, 63]) for r in range(37, 48)]
print(f"    Rows 37-47: {col63_around}")

# ==============================================================================
# PHASE 7: DIAGONAL POSITION (51, 51)
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 7: DIAGONAL POSITION (51, 51)")
print("=" * 80)

print(f"""
  Position (51, 51) is on the MAIN DIAGONAL:

  51 = 0011 0011 (binary pattern)
  51 + 51 = 102
  127 - 51 = 76

  Partner: (76, 76) = {int(matrix[76, 76])}

  This creates a symmetric anchor on the diagonal!
""")

# ==============================================================================
# PHASE 8: DECODE COORDINATES AS MESSAGE
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 8: COORDINATE MESSAGE DECODE")
print("=" * 80)

# Try various encodings
print("\n  Method 1: Rows as letters (a=0)")
row_letters = ''.join(chr(r % 26 + ord('a')) for r in rows)
print(f"    Rows mod 26: {row_letters}")

print("\n  Method 2: Cols as letters (a=0)")
col_letters = ''.join(chr(c % 26 + ord('a')) for c in cols)
print(f"    Cols mod 26: {col_letters}")

print("\n  Method 3: r+c as letters")
sum_letters = ''.join(chr((r+c) % 26 + ord('a')) for r, c in bridge_cells)
print(f"    (r+c) mod 26: {sum_letters}")

print("\n  Method 4: Interleaved")
interleaved = ''.join(f"{chr(r%26+ord('a'))}{chr(c%26+ord('a'))}" for r, c in bridge_cells)
print(f"    Interleaved: {interleaved}")

print("\n  Method 5: XOR pairs")
xor_vals = [r ^ c for r, c in bridge_cells]
print(f"    r XOR c: {xor_vals}")
xor_ascii = ''.join(chr(x) if 32 <= x <= 126 else '.' for x in xor_vals)
print(f"    As ASCII: '{xor_ascii}'")

# ==============================================================================
# PHASE 9: FIBONACCI/PRIME CHECK
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 9: SPECIAL NUMBER CHECK")
print("=" * 80)

fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]
powers_of_2 = [1, 2, 4, 8, 16, 32, 64, 128]

print("\n  Checking coordinates against special sequences:")

for r, c in bridge_cells:
    properties = []
    if r in fibs:
        properties.append(f"row {r} is Fibonacci")
    if c in fibs:
        properties.append(f"col {c} is Fibonacci")
    if r in primes:
        properties.append(f"row {r} is Prime")
    if c in primes:
        properties.append(f"col {c} is Prime")
    if r in powers_of_2:
        properties.append(f"row {r} is Power of 2")
    if c in powers_of_2:
        properties.append(f"col {c} is Power of 2")

    if properties:
        print(f"\n  ({r}, {c}):")
        for p in properties:
            print(f"    ★ {p}")

# ==============================================================================
# PHASE 10: BINARY ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 10: BINARY ANALYSIS")
print("=" * 80)

print("\n  Binary representation of coordinates:")
for r, c in bridge_cells:
    r_bin = format(r, '07b')
    c_bin = format(c, '07b')
    combined = r_bin + c_bin
    print(f"    ({r:3d}, {c:3d}): r={r_bin}, c={c_bin}, combined={combined}")

# Combine all as one binary string
all_binary = ''.join(format(r, '07b') + format(c, '07b') for r, c in bridge_cells)
print(f"\n  All coordinates as binary: {all_binary[:56]}...")
print(f"  Length: {len(all_binary)} bits")

# Try to decode as ASCII (8 bits each)
bytes_from_binary = [all_binary[i:i+8] for i in range(0, len(all_binary)-7, 8)]
ascii_from_binary = ''.join(chr(int(b, 2)) if int(b, 2) < 128 else '?' for b in bytes_from_binary)
print(f"  As ASCII: '{ascii_from_binary}'")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("BRIDGE CELLS ANALYSIS SUMMARY")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         BRIDGE CELLS DISCOVERIES                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  THE 8 BRIDGE CELLS:                                                          ║
║    All have value 127 (max positive signed byte)                              ║
║    All partners have value -128 (min negative signed byte)                    ║
║    127 + (-128) = -1 (point symmetry rule)                                    ║
║                                                                               ║
║  COORDINATE PATTERNS:                                                         ║
║    Row sum: {sum(rows):4d}                                                           ║
║    Col sum: {sum(cols):4d}                                                           ║
║    Row XOR: {row_xor:4d}                                                             ║
║    Col XOR: {col_xor:4d}                                                             ║
║                                                                               ║
║  SPECIAL POSITIONS:                                                           ║
║    (42, 63) = "The Answer" + "Center"                                         ║
║    (51, 51) = Diagonal anchor                                                 ║
║                                                                               ║
║  DECODED STRINGS:                                                             ║
║    Rows as ASCII: '{row_ascii}'                                               ║
║    Cols as ASCII: '{col_ascii}'                                               ║
║    r+c mod 26: '{sum_letters}'                                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "bridge_cells": bridge_cells,
    "row_values": rows,
    "col_values": cols,
    "row_sum": sum(rows),
    "col_sum": sum(cols),
    "row_xor": row_xor,
    "col_xor": col_xor,
    "special_positions": {
        "the_answer": (42, 63),
        "diagonal": (51, 51)
    },
    "decoded_strings": {
        "rows_ascii": row_ascii,
        "cols_ascii": col_ascii,
        "sum_letters": sum_letters
    }
}

with open(script_dir / "PRIORITY2_BRIDGE_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("✓ Results saved to PRIORITY2_BRIDGE_RESULTS.json")
