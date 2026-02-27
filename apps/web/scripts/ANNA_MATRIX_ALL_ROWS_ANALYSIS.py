#!/usr/bin/env python3
"""
ANNA MATRIX - ALL 128 ROWS ANALYSIS
Check EVERY row for ARK/POCC/HASV patterns (not just Row 6 and 79)
"""

import json
import sys
from pathlib import Path
import numpy as np

# Addresses
ARK = "ARKMGCWFYEHJFAVSGKEXVWBGGXZAVLZNBDNBZEXTQBKLKRPEYPEIEKFHUPNG"
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    if c.isalpha():
        return ord(c.upper()) - ord('A')
    return 0

def load_anna_matrix():
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
        return np.array(data['matrix'], dtype=np.float64)

print("="*80)
print("ANNA MATRIX - COMPLETE 128-ROW ANALYSIS")
print("="*80)

# Load addresses and matrix
ark_chars = [char_to_num(c) for c in ARK if c.isalpha()]
pocc_chars = [char_to_num(c) for c in POCC if c.isalpha()]
hasv_chars = [char_to_num(c) for c in HASV if c.isalpha()]
matrix = load_anna_matrix()

print(f"\nAddress character counts:")
print(f"   ARK:  {len(ark_chars)} chars")
print(f"   POCC: {len(pocc_chars)} chars")
print(f"   HASV: {len(hasv_chars)} chars")

# ============================================================================
# SCAN ALL 128 ROWS
# ============================================================================
print(f"\n{'='*80}")
print("SCANNING ALL 128 ROWS FOR SPECIAL PATTERNS")
print(f"{'='*80}")

special_rows = []

for row in range(128):
    # Calculate sums for this row
    ark_sum = sum(matrix[row][c] for c in ark_chars if c < 128)
    pocc_sum = sum(matrix[row][c] for c in pocc_chars if c < 128)
    hasv_sum = sum(matrix[row][c] for c in hasv_chars if c < 128)

    # Calculate differences
    ark_pocc_diff = ark_sum - pocc_sum
    ark_hasv_diff = ark_sum - hasv_sum
    pocc_hasv_diff = pocc_sum - hasv_sum

    # Check for special values (multiples of key numbers)
    is_special = False
    reasons = []

    # Check if differences are multiples of 676, 138, 121, 26
    for target, name in [(676, "676"), (138, "138"), (121, "121"), (26, "26")]:
        if abs(ark_pocc_diff) % target == 0 and abs(ark_pocc_diff) > 0:
            is_special = True
            mult = int(ark_pocc_diff / target)
            reasons.append(f"ARK-POCC = {mult} × {name}")

        if abs(ark_hasv_diff) % target == 0 and abs(ark_hasv_diff) > 0:
            is_special = True
            mult = int(ark_hasv_diff / target)
            reasons.append(f"ARK-HASV = {mult} × {name}")

        if abs(pocc_hasv_diff) % target == 0 and abs(pocc_hasv_diff) > 0:
            is_special = True
            mult = int(pocc_hasv_diff / target)
            reasons.append(f"POCC-HASV = {mult} × {name}")

    # Check if any sum equals special values
    for val, name in [(676, "676"), (2028, "2028"), (121, "121"), (138, "138")]:
        if abs(ark_sum - val) < 1:
            is_special = True
            reasons.append(f"ARK sum ≈ {name}")
        if abs(pocc_sum - val) < 1:
            is_special = True
            reasons.append(f"POCC sum ≈ {name}")
        if abs(hasv_sum - val) < 1:
            is_special = True
            reasons.append(f"HASV sum ≈ {name}")

    if is_special:
        special_rows.append({
            'row': row,
            'ark_sum': ark_sum,
            'pocc_sum': pocc_sum,
            'hasv_sum': hasv_sum,
            'ark_pocc_diff': ark_pocc_diff,
            'ark_hasv_diff': ark_hasv_diff,
            'pocc_hasv_diff': pocc_hasv_diff,
            'reasons': reasons
        })

print(f"\n🎯 FOUND {len(special_rows)} SPECIAL ROWS!")

# Display special rows
for sr in special_rows[:20]:  # Show first 20
    print(f"\n{'─'*80}")
    print(f"ROW {sr['row']:3d}:")
    print(f"   ARK sum:  {sr['ark_sum']:8.0f}")
    print(f"   POCC sum: {sr['pocc_sum']:8.0f}")
    print(f"   HASV sum: {sr['hasv_sum']:8.0f}")
    print(f"   Reasons:")
    for reason in sr['reasons']:
        print(f"      ⭐ {reason}")

if len(special_rows) > 20:
    print(f"\n... and {len(special_rows) - 20} more special rows")

# ============================================================================
# FIND ROWS WITH VALUE 26 BIAS (like Row 6)
# ============================================================================
print(f"\n{'='*80}")
print("SEARCHING FOR OTHER ROWS WITH VALUE 26 BIAS")
print(f"{'='*80}")

value_26_rows = []

for row in range(128):
    count_26 = sum(1 for val in matrix[row] if abs(val - 26) < 0.1)
    percentage = count_26 / 128 * 100

    # Row 6 has 24/128 (18.8%)
    if percentage > 10:  # More than 10% is significant
        value_26_rows.append({
            'row': row,
            'count': count_26,
            'percentage': percentage
        })

print(f"\nRows with >10% value 26:")
for r in sorted(value_26_rows, key=lambda x: x['percentage'], reverse=True):
    stars = "⭐⭐⭐" if r['row'] == 6 else "⭐" if r['percentage'] > 15 else ""
    print(f"   Row {r['row']:3d}: {r['count']:2d}/128 ({r['percentage']:5.2f}%) {stars}")

# ============================================================================
# FIND PERFECT EQUALITY ROWS
# ============================================================================
print(f"\n{'='*80}")
print("SEARCHING FOR ROWS WHERE ARK=POCC OR ARK=HASV")
print(f"{'='*80}")

equality_rows = []

for row in range(128):
    ark_sum = sum(matrix[row][c] for c in ark_chars if c < 128)
    pocc_sum = sum(matrix[row][c] for c in pocc_chars if c < 128)
    hasv_sum = sum(matrix[row][c] for c in hasv_chars if c < 128)

    if abs(ark_sum - pocc_sum) < 1:
        equality_rows.append((row, "ARK = POCC", ark_sum))
    elif abs(ark_sum - hasv_sum) < 1:
        equality_rows.append((row, "ARK = HASV", ark_sum))
    elif abs(pocc_sum - hasv_sum) < 1:
        equality_rows.append((row, "POCC = HASV", pocc_sum))

if equality_rows:
    print(f"\n🎯 Found {len(equality_rows)} rows with perfect equality!")
    for row, eq_type, value in equality_rows:
        print(f"   Row {row:3d}: {eq_type} (value={value:.0f})")
else:
    print(f"\n   No rows with perfect equality found")

# ============================================================================
# SUM ALL ROWS (find the "sum across all rows" pattern)
# ============================================================================
print(f"\n{'='*80}")
print("SUM ACROSS ALL ROWS")
print(f"{'='*80}")

ark_total = 0
pocc_total = 0
hasv_total = 0

for row in range(128):
    ark_total += sum(matrix[row][c] for c in ark_chars if c < 128)
    pocc_total += sum(matrix[row][c] for c in pocc_chars if c < 128)
    hasv_total += sum(matrix[row][c] for c in hasv_chars if c < 128)

print(f"\nTotal across all 128 rows:")
print(f"   ARK:  {ark_total:12.0f}")
print(f"   POCC: {pocc_total:12.0f}")
print(f"   HASV: {hasv_total:12.0f}")

print(f"\nDifferences:")
print(f"   ARK - POCC = {ark_total - pocc_total:12.0f}")
print(f"   ARK - HASV = {ark_total - hasv_total:12.0f}")
print(f"   POCC - HASV = {pocc_total - hasv_total:12.0f}")

# Check if divisible by special numbers
for diff, name in [(ark_total - pocc_total, "ARK-POCC"),
                   (ark_total - hasv_total, "ARK-HASV"),
                   (pocc_total - hasv_total, "POCC-HASV")]:
    print(f"\n{name}:")
    for divisor in [676, 138, 121, 26, 2028]:
        if abs(diff) % divisor == 0:
            print(f"   ⭐ Divisible by {divisor}! ({int(diff/divisor)} × {divisor})")

# ============================================================================
# FIND "INVERSE" ROWS (where differences flip sign)
# ============================================================================
print(f"\n{'='*80}")
print("FINDING COMPLEMENTARY ROW PAIRS")
print(f"{'='*80}")

# Get diagonal row difference (we know this)
diag_diff = sum(matrix[c][c] for c in ark_chars if c < 128) - \
            sum(matrix[c][c] for c in pocc_chars if c < 128)

print(f"\nDiagonal row difference (ARK-POCC): {diag_diff:.0f}")
print(f"Looking for row where (ARK-POCC) = {-diag_diff:.0f}...")

complementary_rows = []
for row in range(128):
    ark_sum = sum(matrix[row][c] for c in ark_chars if c < 128)
    pocc_sum = sum(matrix[row][c] for c in pocc_chars if c < 128)
    diff = ark_sum - pocc_sum

    if abs(diff + diag_diff) < 10:  # Close to negative of diagonal
        complementary_rows.append((row, diff))

if complementary_rows:
    print(f"\n🎯 Found {len(complementary_rows)} complementary rows!")
    for row, diff in complementary_rows:
        print(f"   Row {row:3d}: ARK-POCC = {diff:.0f} (complements diagonal)")
else:
    print(f"\n   No exact complement found")

# ============================================================================
# SUMMARY
# ============================================================================
print(f"\n{'='*80}")
print("SUMMARY OF DISCOVERIES")
print(f"{'='*80}")

print(f"""
📊 ALL-ROWS SCAN RESULTS:

1. SPECIAL ROWS FOUND: {len(special_rows)}
   Rows with multiples of 676, 138, 121, or 26

2. VALUE 26 BIAS ROWS: {len(value_26_rows)}
   Row 6: 24/128 (18.8%) ⭐⭐⭐ (KNOWN)
   {"Other rows: " + ", ".join([f"Row {r['row']}" for r in value_26_rows if r['row'] != 6]) if len(value_26_rows) > 1 else "No other biased rows"}

3. EQUALITY ROWS: {len(equality_rows)}
   {("Rows where ARK=POCC, ARK=HASV, or POCC=HASV" if equality_rows else "None found")}

4. TOTAL SUMS:
   Sum across all 128 rows shows global patterns

5. COMPLEMENTARY ROWS: {len(complementary_rows)}
   {"Rows that complement the diagonal" if complementary_rows else "None found"}

🎯 NEXT STEPS:
   - Investigate special rows in detail
   - Check if biased rows (like Row 6) encode messages
   - Look for patterns in row numbers themselves
   - Cross-reference with Bitcoin block heights?
""")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}")
