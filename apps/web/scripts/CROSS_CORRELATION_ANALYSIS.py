#!/usr/bin/env python3
"""
===============================================================================
            CROSS-CORRELATION ANALYSIS
===============================================================================
Find connections between all validated patterns:
1. Col30↔97 (AI.MEG.GOU)
2. Col19↔108 (10-char mirror)
3. Row15↔112 (28-char palindrome)
4. String cells (26 cells)
5. Asymmetric cells (68 total)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("           CROSS-CORRELATION ANALYSIS")
print("           Finding connections between patterns")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
raw_matrix = data["matrix"]

# ==============================================================================
# COLLECT ALL SIGNIFICANT POSITIONS
# ==============================================================================
print("\n" + "=" * 80)
print("COLLECTING SIGNIFICANT POSITIONS")
print("=" * 80)

# Pattern 1: AI.MEG.GOU in Col30⊕97 at rows 55-68
aimeg_positions = [(r, 30) for r in range(55, 69)] + [(r, 97) for r in range(55, 69)]

# Pattern 2: 10-char mirror in Col19⊕108 at rows 36-45
mirror_positions = [(r, 19) for r in range(36, 46)] + [(r, 108) for r in range(36, 46)]

# Pattern 3: 28-char palindrome in Row15⊕112 at cols 50-77
palindrome_positions = [(15, c) for c in range(50, 78)] + [(112, c) for c in range(50, 78)]

# Pattern 4: String cells
string_positions = []
for r in range(128):
    for c in range(128):
        if isinstance(raw_matrix[r][c], str):
            string_positions.append((r, c))

# Pattern 5: All asymmetric cells
asymmetric_positions = []
for r in range(128):
    for c in range(128):
        partner_r, partner_c = 127 - r, 127 - c
        if matrix[r, c] + matrix[partner_r, partner_c] != -1:
            asymmetric_positions.append((r, c))

print(f"\n  Pattern positions:")
print(f"    AI.MEG.GOU (Col30↔97, rows 55-68): {len(aimeg_positions)} cells")
print(f"    10-char mirror (Col19↔108, rows 36-45): {len(mirror_positions)} cells")
print(f"    28-char palindrome (Row15↔112, cols 50-77): {len(palindrome_positions)} cells")
print(f"    String cells: {len(string_positions)} cells")
print(f"    Asymmetric cells: {len(asymmetric_positions)} cells")

# ==============================================================================
# FIND OVERLAPS
# ==============================================================================
print("\n" + "=" * 80)
print("FINDING OVERLAPS")
print("=" * 80)

sets = {
    "AI.MEG": set(aimeg_positions),
    "Mirror": set(mirror_positions),
    "Palindrome": set(palindrome_positions),
    "String": set(string_positions),
    "Asymmetric": set(asymmetric_positions),
}

print(f"\n  Pairwise overlaps:")
patterns = list(sets.keys())
for i, p1 in enumerate(patterns):
    for p2 in patterns[i+1:]:
        overlap = sets[p1] & sets[p2]
        if overlap:
            print(f"    {p1} ∩ {p2}: {len(overlap)} cells")
            for pos in list(overlap)[:5]:
                print(f"      {pos}")
        else:
            print(f"    {p1} ∩ {p2}: 0 cells")

# ==============================================================================
# NUMERIC RELATIONSHIPS
# ==============================================================================
print("\n" + "=" * 80)
print("NUMERIC RELATIONSHIPS")
print("=" * 80)

# Key numbers from patterns
numbers = {
    "Col AI.MEG": (30, 97),
    "Col Mirror": (19, 108),
    "Row Palindrome": (15, 112),
    "AI.MEG rows": (55, 68),
    "Mirror rows": (36, 45),
    "Palindrome cols": (50, 77),
}

print(f"\n  Key numbers:")
for name, (a, b) in numbers.items():
    print(f"    {name}: {a}, {b}")
    print(f"      Sum: {a+b}, Diff: {abs(a-b)}, XOR: {a^b}, Product: {a*b}")

# Check for common relationships
print(f"\n  Cross-relationships:")
all_nums = [30, 97, 19, 108, 15, 112, 55, 68, 36, 45, 50, 77]
for i, n1 in enumerate(all_nums):
    for n2 in all_nums[i+1:]:
        if n1 + n2 == 127:
            print(f"    {n1} + {n2} = 127 (symmetric pair)")
        if n1 ^ n2 == 127:
            print(f"    {n1} XOR {n2} = 127")

# ==============================================================================
# ROW/COLUMN INTERSECTIONS
# ==============================================================================
print("\n" + "=" * 80)
print("CRITICAL INTERSECTIONS")
print("=" * 80)

# Where do the key rows/cols intersect?
key_rows = [15, 112, 55, 68, 36, 45]
key_cols = [30, 97, 19, 108, 50, 77]

print(f"\n  Values at key intersections:")
for r in key_rows[:4]:
    for c in key_cols[:4]:
        val = int(matrix[r, c])
        ch = chr(abs(val)) if 32 <= abs(val) <= 126 else '.'
        print(f"    [{r:3},{c:3}] = {val:4d} = '{ch}'")

# ==============================================================================
# DISTANCE ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("SPATIAL DISTANCE ANALYSIS")
print("=" * 80)

# Centroids of each pattern
def centroid(positions):
    if not positions:
        return (0, 0)
    rows = [p[0] for p in positions]
    cols = [p[1] for p in positions]
    return (np.mean(rows), np.mean(cols))

centroids = {name: centroid(list(positions)) for name, positions in sets.items()}

print(f"\n  Pattern centroids:")
for name, (r, c) in centroids.items():
    print(f"    {name}: ({r:.1f}, {c:.1f})")

# Distances between centroids
print(f"\n  Distances between pattern centroids:")
for i, (n1, c1) in enumerate(centroids.items()):
    for n2, c2 in list(centroids.items())[i+1:]:
        dist = np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
        print(f"    {n1} ↔ {n2}: {dist:.1f}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("CROSS-CORRELATION COMPLETE")
print("=" * 80)

# Find any strong correlations
correlations_found = []

# Check if any patterns share cells
for i, (n1, s1) in enumerate(sets.items()):
    for n2, s2 in list(sets.items())[i+1:]:
        overlap = s1 & s2
        if overlap:
            correlations_found.append({
                "pattern1": n1,
                "pattern2": n2,
                "overlap_count": len(overlap),
                "overlap_positions": list(overlap)[:10],
            })

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         CROSS-CORRELATION SUMMARY                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  OVERLAPPING PATTERNS: {len(correlations_found)}                                              ║
║                                                                               ║
║  KEY NUMERIC RELATIONSHIPS:                                                   ║
║  • 30 + 97 = 127 (Col AI.MEG symmetric)                                      ║
║  • 19 + 108 = 127 (Col Mirror symmetric)                                     ║
║  • 15 + 112 = 127 (Row Palindrome symmetric)                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save
results = {
    "timestamp": datetime.now().isoformat(),
    "pattern_sizes": {name: len(s) for name, s in sets.items()},
    "correlations": correlations_found,
    "centroids": {name: list(c) for name, c in centroids.items()},
    "key_numbers": numbers,
}

with open(script_dir / "CROSS_CORRELATION_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved")
