#!/usr/bin/env python3
"""
DEEP PATTERN DISCOVERY
======================
Goes beyond known patterns to find NEW mathematical connections
that are 100% verifiable and reproducible.

Focus areas:
1. Cross-row patterns
2. Multiple address correlations
3. Hidden numerical relationships
4. Symmetry patterns
5. Modular arithmetic discoveries
"""

import json
import numpy as np
from collections import defaultdict, Counter

# Load Anna Matrix
MATRIX_FILE = "../public/data/anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
    matrix = np.array(data['matrix'], dtype=np.int8)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    return ord(c.upper()) - ord('A')

print("=" * 80)
print("DEEP PATTERN DISCOVERY")
print("=" * 80)
print()

discoveries = []

# =============================================================================
# DISCOVERY 1: Full Row Analysis for ALL Special Numbers
# =============================================================================
print("\n[DISCOVERY 1] Comprehensive Row Analysis")
print("-" * 60)

pocc_chars = [char_to_num(c) for c in POCC if c.isalpha()]
hasv_chars = [char_to_num(c) for c in HASV if c.isalpha()]

special_numbers = {26, 33, 46, 121, 138, 676}
row_findings = defaultdict(list)

for row in range(128):
    row_pocc = sum(matrix[row][c] for c in pocc_chars if c < 128)
    row_hasv = sum(matrix[row][c] for c in hasv_chars if c < 128)
    diff = row_hasv - row_pocc
    abs_diff = abs(diff)

    if abs_diff in special_numbers:
        row_findings[row].append({
            'pocc_sum': row_pocc,
            'hasv_sum': row_hasv,
            'diff': diff,
            'abs_diff': abs_diff
        })

print(f"Found {len(row_findings)} rows with special number differences:")
for row, findings in sorted(row_findings.items())[:10]:
    for finding in findings:
        print(f"  Row {row:3d}: POCC={finding['pocc_sum']:6d}, HASV={finding['hasv_sum']:6d}, diff={finding['diff']:5d}")
        discoveries.append(f"Row {row} difference = {finding['diff']}")

# =============================================================================
# DISCOVERY 2: Column Analysis
# =============================================================================
print("\n[DISCOVERY 2] Column Analysis")
print("-" * 60)

col_findings = defaultdict(list)

for col in range(128):
    col_pocc = sum(matrix[c][col] for c in pocc_chars if c < 128)
    col_hasv = sum(matrix[c][col] for c in hasv_chars if c < 128)
    diff = col_hasv - col_pocc
    abs_diff = abs(diff)

    if abs_diff in special_numbers:
        col_findings[col].append({
            'pocc_sum': col_pocc,
            'hasv_sum': col_hasv,
            'diff': diff,
            'abs_diff': abs_diff
        })

print(f"Found {len(col_findings)} columns with special number differences:")
for col, findings in sorted(col_findings.items())[:10]:
    for finding in findings:
        print(f"  Col {col:3d}: POCC={finding['pocc_sum']:6d}, HASV={finding['hasv_sum']:6d}, diff={finding['diff']:5d}")
        discoveries.append(f"Column {col} difference = {finding['diff']}")

# =============================================================================
# DISCOVERY 3: Position-Specific Matrix Lookups
# =============================================================================
print("\n[DISCOVERY 3] Position-Specific Patterns")
print("-" * 60)

# Check every position in both addresses
position_patterns = []

for i in range(min(len(POCC), len(HASV))):
    if i >= 60:  # Only first 60 chars
        break

    pocc_char = char_to_num(POCC[i])
    hasv_char = char_to_num(HASV[i])

    if pocc_char < 128 and hasv_char < 128:
        # Check diagonal
        pocc_diag_val = matrix[pocc_char][pocc_char]
        hasv_diag_val = matrix[hasv_char][hasv_char]

        # Check cross-lookup
        cross_val = matrix[pocc_char][hasv_char]

        # Look for special numbers
        if pocc_diag_val in special_numbers or hasv_diag_val in special_numbers:
            position_patterns.append({
                'pos': i,
                'pocc_char': POCC[i],
                'hasv_char': HASV[i],
                'pocc_diag': pocc_diag_val,
                'hasv_diag': hasv_diag_val
            })

        if cross_val in special_numbers:
            position_patterns.append({
                'pos': i,
                'cross_val': cross_val,
                'pocc_char': POCC[i],
                'hasv_char': HASV[i]
            })

print(f"Found {len(position_patterns)} positions with special diagonal/cross values")
for pattern in position_patterns[:10]:
    print(f"  Position {pattern['pos']}: {pattern}")

# =============================================================================
# DISCOVERY 4: Sum of Squares, Cubes, and Other Powers
# =============================================================================
print("\n[DISCOVERY 4] Power Analysis")
print("-" * 60)

# Sum of squares
pocc_squares = sum(c**2 for c in pocc_chars)
hasv_squares = sum(c**2 for c in hasv_chars)
squares_diff = hasv_squares - pocc_squares

print(f"Sum of squares:")
print(f"  POCC: {pocc_squares}")
print(f"  HASV: {hasv_squares}")
print(f"  Diff: {squares_diff}")

if abs(squares_diff) in special_numbers or squares_diff % 26 == 0 or squares_diff % 676 == 0:
    print(f"  ⚠️  Special property detected!")
    discoveries.append(f"Sum of squares diff = {squares_diff}")

# Sum of cubes
pocc_cubes = sum(c**3 for c in pocc_chars)
hasv_cubes = sum(c**3 for c in hasv_chars)
cubes_diff = hasv_cubes - pocc_cubes

print(f"\nSum of cubes:")
print(f"  POCC: {pocc_cubes}")
print(f"  HASV: {hasv_cubes}")
print(f"  Diff: {cubes_diff}")

if abs(cubes_diff) % 676 == 0:
    print(f"  ⚠️  Divisible by 676!")
    discoveries.append(f"Sum of cubes diff divisible by 676")

# =============================================================================
# DISCOVERY 5: Weighted Position Sums
# =============================================================================
print("\n[DISCOVERY 5] Weighted Position Analysis")
print("-" * 60)

# Weight by position index
pocc_weighted = sum((i + 1) * c for i, c in enumerate(pocc_chars))
hasv_weighted = sum((i + 1) * c for i, c in enumerate(hasv_chars))
weighted_diff = hasv_weighted - pocc_weighted

print(f"Position-weighted sums:")
print(f"  POCC: {pocc_weighted}")
print(f"  HASV: {hasv_weighted}")
print(f"  Diff: {weighted_diff}")
print(f"  Diff mod 676: {weighted_diff % 676}")
print(f"  Diff mod 26: {weighted_diff % 26}")

if weighted_diff % 676 in [0, 26, 121]:
    print(f"  ⚠️  Special modulo property!")
    discoveries.append(f"Weighted position diff mod 676 = {weighted_diff % 676}")

# =============================================================================
# DISCOVERY 6: Identical Position Deep Analysis
# =============================================================================
print("\n[DISCOVERY 6] Identical Positions Deep Dive")
print("-" * 60)

identical = [i for i in range(60) if POCC[i] == HASV[i]]
print(f"Identical positions: {identical}")

# Analyze the sum of identical position values
identical_chars = [char_to_num(POCC[i]) for i in identical]
identical_sum = sum(identical_chars)
identical_product = 1
for c in identical_chars:
    identical_product *= (c + 1)  # Use 1-based to avoid 0

print(f"Identical position characters: {[POCC[i] for i in identical]}")
print(f"Sum of identical char values: {identical_sum}")
print(f"Sum mod 26: {identical_sum % 26}")
print(f"Sum mod 676: {identical_sum % 676}")

# Sum of position indices
position_sum = sum(identical)
print(f"Sum of positions: {position_sum}")
print(f"Position sum mod 26: {position_sum % 26}")
print(f"Position sum mod 60: {position_sum % 60}")

if position_sum % 26 == 6:
    print(f"  ✅ VERIFIED: Position sum mod 26 = 6 (self-referential!)")
    discoveries.append("Position sum of 6 identical positions mod 26 = 6")

# =============================================================================
# DISCOVERY 7: Difference Position Analysis
# =============================================================================
print("\n[DISCOVERY 7] Difference Positions")
print("-" * 60)

different = [i for i in range(60) if POCC[i] != HASV[i]]
print(f"Different positions: {len(different)}/60")

# Character value differences at each different position
char_diffs = []
for i in different:
    pocc_val = char_to_num(POCC[i])
    hasv_val = char_to_num(HASV[i])
    char_diffs.append(hasv_val - pocc_val)

print(f"Sum of character differences: {sum(char_diffs)}")
print(f"Should equal total difference: {sum(hasv_chars) - sum(pocc_chars)}")

# Verify
if sum(char_diffs) == 138:
    print(f"  ✅ VERIFIED: Sum of all position diffs = 138")
    discoveries.append("Sum of position-by-position diffs = 138")

# =============================================================================
# DISCOVERY 8: Matrix Value Distribution Analysis
# =============================================================================
print("\n[DISCOVERY 8] Matrix Value Distribution in POCC/HASV")
print("-" * 60)

# Count occurrences of each matrix diagonal value
pocc_diag_values = [matrix[c][c] for c in pocc_chars if c < 128]
hasv_diag_values = [matrix[c][c] for c in hasv_chars if c < 128]

pocc_counter = Counter(pocc_diag_values)
hasv_counter = Counter(hasv_diag_values)

print("Most common diagonal values in POCC:")
for val, count in pocc_counter.most_common(5):
    print(f"  Value {val:4d}: appears {count} times")

print("\nMost common diagonal values in HASV:")
for val, count in hasv_counter.most_common(5):
    print(f"  Value {val:4d}: appears {count} times")

# Check for value 26 appearances
pocc_26_count = pocc_counter.get(26, 0)
hasv_26_count = hasv_counter.get(26, 0)
print(f"\nValue 26 appearances:")
print(f"  POCC: {pocc_26_count} times")
print(f"  HASV: {hasv_26_count} times")

# =============================================================================
# DISCOVERY 9: Modular Patterns Beyond Known
# =============================================================================
print("\n[DISCOVERY 9] Extended Modular Analysis")
print("-" * 60)

test_moduli = [6, 11, 13, 17, 19, 23, 26, 27, 33, 46, 121, 676]

modular_matches = []
for mod in test_moduli:
    pocc_mod = sum(pocc_chars) % mod
    hasv_mod = sum(hasv_chars) % mod

    if pocc_mod == hasv_mod:
        modular_matches.append((mod, pocc_mod))
        print(f"  mod {mod:3d}: IDENTICAL = {pocc_mod}")
        discoveries.append(f"Both addresses mod {mod} = {pocc_mod}")

# =============================================================================
# DISCOVERY 10: Prefix/Suffix Patterns
# =============================================================================
print("\n[DISCOVERY 10] Prefix/Suffix Analysis")
print("-" * 60)

# Check all 4-char windows
print("Checking all 4-character windows...")
window_findings = []

for start in range(57):  # 60 - 4 + 1
    pocc_window = POCC[start:start+4]
    hasv_window = HASV[start:start+4]

    pocc_sum = sum(char_to_num(c) for c in pocc_window if c.isalpha())
    hasv_sum = sum(char_to_num(c) for c in hasv_window if c.isalpha())

    # Look up in Row 6
    if 0 <= pocc_sum < 128 and 0 <= hasv_sum < 128:
        pocc_lookup = matrix[6][pocc_sum]
        hasv_lookup = matrix[6][hasv_sum]

        if pocc_lookup in special_numbers or hasv_lookup in special_numbers:
            window_findings.append({
                'start': start,
                'pocc_window': pocc_window,
                'hasv_window': hasv_window,
                'pocc_lookup': pocc_lookup,
                'hasv_lookup': hasv_lookup
            })

print(f"Found {len(window_findings)} windows with special Row 6 lookups")
for finding in window_findings[:10]:
    print(f"  Position {finding['start']}: '{finding['pocc_window']}' → {finding['pocc_lookup']}, "
          f"'{finding['hasv_window']}' → {finding['hasv_lookup']}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n\n" + "=" * 80)
print("DISCOVERY SUMMARY")
print("=" * 80)
print(f"\nTotal new patterns discovered: {len(discoveries)}")
print("\nTop discoveries:")
for i, discovery in enumerate(discoveries[:20], 1):
    print(f"  {i}. {discovery}")

print("\n" + "=" * 80)
print("All discoveries are 100% mathematically verifiable.")
print("No speculation. No interpretation. Pure numbers.")
print("=" * 80)
