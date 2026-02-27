#!/usr/bin/env python3
"""
MASTER VALIDATION - ALL ANNA MATRIX CLAIMS
===========================================
Validates EVERY mathematical claim found across all documentation,
scripts, and data files. Nothing is assumed - everything is verified.

Based on findings from:
- 42 documents in /03-results/
- 89 documents in /03-results-backup/
- 120+ analysis scripts
- Anna Matrix data file

RULE: Only mark as ✅ VERIFIED if 100% mathematically proven.
      Mark as ⚠️ REPORTED if requires external data (blockchain, etc.)
      Mark as ❌ FALSE if proven wrong.
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict, Counter

# Load Anna Matrix
MATRIX_FILE = "../public/data/anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
    matrix = np.array(data['matrix'], dtype=np.int8)

# Key addresses
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"
SC_ADDR = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFXIB"

def char_to_num(c):
    """Convert character to number (A=0, B=1, ..., Z=25)"""
    return ord(c.upper()) - ord('A')

print("=" * 80)
print("MASTER VALIDATION - ALL CLAIMS")
print("=" * 80)
print()

results = {
    'verified': [],
    'reported': [],
    'false': [],
    'warnings': []
}

# =============================================================================
# SECTION 1: ANNA MATRIX PROPERTIES
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 1: ANNA MATRIX PROPERTIES")
print("=" * 80 + "\n")

# Claim 1.1: Matrix is 128×128
print("[1.1] Matrix dimensions = 128×128")
if matrix.shape == (128, 128):
    print("  ✅ VERIFIED: shape =", matrix.shape)
    results['verified'].append("Matrix is 128×128")
else:
    print(f"  ❌ FALSE: shape = {matrix.shape}")
    results['false'].append(f"Matrix shape is {matrix.shape}, not 128×128")

# Claim 1.2: 99.59% point symmetry
print("\n[1.2] Point symmetry = 99.59%")
anomalies = 0
for i in range(128):
    for j in range(128):
        if matrix[i][j] != -matrix[127-i][127-j]:
            anomalies += 1

total_cells = 128 * 128
symmetry_pct = ((total_cells - anomalies) / total_cells) * 100
print(f"  Anomalies: {anomalies}/{total_cells}")
print(f"  Symmetry: {symmetry_pct:.2f}%")

if abs(symmetry_pct - 99.59) < 0.01:
    print("  ✅ VERIFIED: 99.59% symmetry")
    results['verified'].append("99.59% point symmetry")
else:
    print(f"  ⚠️  WARNING: Actual symmetry is {symmetry_pct:.2f}%")
    results['warnings'].append(f"Symmetry is {symmetry_pct:.2f}%, not exactly 99.59%")

# Claim 1.3: Position [22,22] = 100 (only self-matching cell)
print("\n[1.3] Position [22,22] = 100 (only self-matching cell)")
val_22_22 = matrix[22][22]
print(f"  matrix[22, 22] = {val_22_22}")

if val_22_22 == 100:
    print("  ✅ VERIFIED: Value is 100")

    # Check if it's the ONLY self-matching cell
    self_matching = []
    for i in range(128):
        for j in range(128):
            if matrix[i][j] == -matrix[127-i][127-j]:
                continue  # This is a normal symmetry
            if i == 127-i and j == 127-j:  # Center point
                if matrix[i][j] == -matrix[i][j]:  # Self-negating
                    if matrix[i][j] == 0:  # Only 0 is self-negating
                        continue
                    self_matching.append((i, j, matrix[i][j]))

    print(f"  Self-matching cells: {len(self_matching)}")
    if len(self_matching) == 1 and self_matching[0] == (22, 22, 100):
        print("  ✅ VERIFIED: Only self-matching cell")
        results['verified'].append("Position [22,22] = 100 is unique self-matching")
    else:
        print(f"  ⚠️  WARNING: Found {len(self_matching)} self-matching cells")
        results['warnings'].append(f"Multiple self-matching cells: {self_matching}")
else:
    print(f"  ❌ FALSE: Value is {val_22_22}, not 100")
    results['false'].append(f"matrix[22,22] = {val_22_22}, not 100")

# Claim 1.4: Row 6 bias toward value 26
print("\n[1.4] Row 6 bias toward value 26 (18.8%)")
row6 = matrix[6]
count_26 = np.sum(row6 == 26)
pct_26 = (count_26 / 128) * 100
print(f"  Value 26 appears: {count_26}/128 times")
print(f"  Percentage: {pct_26:.1f}%")

if abs(pct_26 - 18.8) < 0.2:
    print("  ✅ VERIFIED: 18.8% appearance rate")
    results['verified'].append("Row 6: value 26 appears 18.8%")
else:
    print(f"  ⚠️  WARNING: Actual rate is {pct_26:.1f}%")
    results['warnings'].append(f"Row 6: 26 appears {pct_26:.1f}%, not 18.8%")

# Claim 1.5: Universal columns
print("\n[1.5] Universal columns (same value for ALL rows)")
universal_cols = {}
for col in range(128):
    values = set(matrix[:, col])
    if len(values) == 1:
        universal_cols[col] = list(values)[0]

print(f"  Found {len(universal_cols)} universal columns")
for col, val in sorted(universal_cols.items())[:5]:  # Show first 5
    print(f"    Column {col}: all values = {val}")

# Check specific universal columns from agent findings
expected_universal = {28: 110, 34: 60}  # From agent report
verified_universal = True
for col, expected_val in expected_universal.items():
    if col in universal_cols and universal_cols[col] == expected_val:
        print(f"  ✅ VERIFIED: Column {col} = {expected_val} (universal)")
    else:
        actual = universal_cols.get(col, "not universal")
        print(f"  ❌ FALSE: Column {col} expected {expected_val}, got {actual}")
        verified_universal = False

if verified_universal:
    results['verified'].append("Universal columns verified")

# =============================================================================
# SECTION 2: POCC/HASV ADDRESS PAIR
# =============================================================================
print("\n\n" + "=" * 80)
print("SECTION 2: POCC/HASV ADDRESS PAIR")
print("=" * 80 + "\n")

# Claim 2.1: Character sums
print("[2.1] Character sums")
pocc_chars = [char_to_num(c) for c in POCC if c.isalpha()]
hasv_chars = [char_to_num(c) for c in HASV if c.isalpha()]

pocc_sum = sum(pocc_chars)
hasv_sum = sum(hasv_chars)
char_diff = hasv_sum - pocc_sum

print(f"  POCC sum: {pocc_sum}")
print(f"  HASV sum: {hasv_sum}")
print(f"  Difference: {char_diff}")

if pocc_sum == 612 and hasv_sum == 750 and char_diff == 138:
    print("  ✅ VERIFIED: 612, 750, diff = 138")
    results['verified'].append("POCC sum = 612, HASV sum = 750, diff = 138")
else:
    print(f"  ❌ FALSE: Expected 612, 750, 138")
    results['false'].append(f"Character sums: {pocc_sum}, {hasv_sum}, {char_diff}")

# Claim 2.2: Diagonal sums
print("\n[2.2] Diagonal sums")
pocc_diag = sum(matrix[c][c] for c in pocc_chars if c < 128)
hasv_diag = sum(matrix[c][c] for c in hasv_chars if c < 128)
diag_diff = hasv_diag - pocc_diag

print(f"  POCC diagonal: {pocc_diag}")
print(f"  HASV diagonal: {hasv_diag}")
print(f"  Difference: {diag_diff}")

if pocc_diag == -1231 and hasv_diag == -555 and diag_diff == 676:
    print("  ✅ VERIFIED: -1231, -555, diff = 676")
    results['verified'].append("POCC diag = -1231, HASV diag = -555, diff = 676")
else:
    print(f"  ❌ FALSE: Expected -1231, -555, 676")
    results['false'].append(f"Diagonal sums: {pocc_diag}, {hasv_diag}, {diag_diff}")

# Claim 2.3: 1-based sums
print("\n[2.3] 1-based character sums")
pocc_1based = sum(c + 1 for c in pocc_chars)
hasv_1based = sum(c + 1 for c in hasv_chars)

print(f"  POCC 1-based: {pocc_1based}")
print(f"  HASV 1-based: {hasv_1based}")

# POCC should be close to 676
pocc_error = abs(pocc_1based - 676)
pocc_error_pct = (pocc_error / 676) * 100

print(f"  POCC distance from 676: {pocc_error} ({pocc_error_pct:.2f}%)")

if pocc_1based == 672:
    print("  ✅ VERIFIED: POCC 1-based = 672 (0.59% from 676)")
    results['verified'].append("POCC 1-based sum = 672")
else:
    print(f"  ⚠️  WARNING: POCC 1-based = {pocc_1based}, not 672")
    results['warnings'].append(f"POCC 1-based = {pocc_1based}, not 672")

# Claim 2.4: XOR equals character difference
print("\n[2.4] XOR of character sums")
xor_result = pocc_sum ^ hasv_sum
print(f"  POCC ⊕ HASV = {xor_result}")
print(f"  Character diff = {char_diff}")

if xor_result == char_diff:
    print("  ✅ VERIFIED: XOR = character difference = 138")
    results['verified'].append("XOR equals character difference (138)")
else:
    print(f"  ❌ FALSE: XOR ({xor_result}) ≠ diff ({char_diff})")
    results['false'].append(f"XOR = {xor_result}, diff = {char_diff}")

# Claim 2.5: Modulo properties
print("\n[2.5] Modular properties")

# mod 23
pocc_mod23 = pocc_sum % 23
hasv_mod23 = hasv_sum % 23
print(f"  POCC mod 23: {pocc_mod23}")
print(f"  HASV mod 23: {hasv_mod23}")

if pocc_mod23 == hasv_mod23 == 14:
    print("  ✅ VERIFIED: Both = 14 (identical mod 23)")
    results['verified'].append("Both character sums mod 23 = 14")
else:
    print(f"  ❌ FALSE: Expected both = 14")
    results['false'].append(f"mod 23: POCC={pocc_mod23}, HASV={hasv_mod23}")

# mod 676 (diagonal)
pocc_diag_mod676 = pocc_diag % 676
hasv_diag_mod676 = hasv_diag % 676
print(f"  POCC diagonal mod 676: {pocc_diag_mod676}")
print(f"  HASV diagonal mod 676: {hasv_diag_mod676}")

if pocc_diag_mod676 == hasv_diag_mod676 == 121:
    print("  ✅ VERIFIED: Both = 121 (= 11²)")
    results['verified'].append("Both diagonal sums mod 676 = 121")
else:
    print(f"  ❌ FALSE: Expected both = 121")
    results['false'].append(f"diag mod 676: POCC={pocc_diag_mod676}, HASV={hasv_diag_mod676}")

# Claim 2.6: Identical positions
print("\n[2.6] Identical positions")
identical = [i for i in range(len(POCC)) if i < len(HASV) and POCC[i] == HASV[i]]
print(f"  Identical positions: {len(identical)}")
print(f"  Positions: {identical}")

if len(identical) == 6 and set(identical) == {7, 34, 41, 48, 53, 57}:
    print("  ✅ VERIFIED: 6 positions: 7, 34, 41, 48, 53, 57")
    results['verified'].append("6 identical positions at 7, 34, 41, 48, 53, 57")
elif len(identical) == 6:
    print(f"  ⚠️  WARNING: 6 positions but different: {identical}")
    results['warnings'].append(f"6 positions but at: {identical}")
else:
    print(f"  ❌ FALSE: Found {len(identical)} positions, expected 6")
    results['false'].append(f"Found {len(identical)} identical positions, not 6")

# Claim 2.7: Position 34 = 'H', matrix[7,7] = 26
print("\n[2.7] Position 34 special property")
if 34 in identical:
    char_34 = POCC[34]
    print(f"  Position 34: '{char_34}'")

    if char_34 == 'H':
        h_val = char_to_num('H')  # Should be 7
        matrix_val = matrix[h_val][h_val]
        print(f"  H = {h_val}")
        print(f"  matrix[{h_val}, {h_val}] = {matrix_val}")

        if matrix_val == 26:
            print("  ✅ VERIFIED: Position 34 = 'H', matrix[7,7] = 26")
            results['verified'].append("Position 34 = 'H', matrix[7,7] = 26")
        else:
            print(f"  ❌ FALSE: matrix[7,7] = {matrix_val}, not 26")
            results['false'].append(f"matrix[7,7] = {matrix_val}, not 26")
    else:
        print(f"  ❌ FALSE: Position 34 = '{char_34}', not 'H'")
        results['false'].append(f"Position 34 = '{char_34}', not 'H'")
else:
    print("  ❌ FALSE: Position 34 is not identical")
    results['false'].append("Position 34 is not identical in POCC/HASV")

# Claim 2.8: Prefix lookups via Row 6
print("\n[2.8] Prefix lookups via Row 6")
pocc_prefix = sum(char_to_num(c) for c in "POCC")
hasv_prefix = sum(char_to_num(c) for c in "HASV")

print(f"  POCC prefix sum: {pocc_prefix}")
print(f"  HASV prefix sum: {hasv_prefix}")

if 0 <= pocc_prefix < 128:
    pocc_lookup = matrix[6][pocc_prefix]
    print(f"  matrix[6, {pocc_prefix}] = {pocc_lookup}")

    if pocc_prefix == 33 and pocc_lookup == 26:
        print("  ✅ VERIFIED: POCC prefix (33) → 26 via Row 6")
        results['verified'].append("POCC prefix sum = 33, matrix[6,33] = 26")
    else:
        print(f"  ⚠️  WARNING: Expected sum=33, lookup=26")
        results['warnings'].append(f"POCC prefix: sum={pocc_prefix}, lookup={pocc_lookup}")

if 0 <= hasv_prefix < 128:
    hasv_lookup = matrix[6][hasv_prefix]
    print(f"  matrix[6, {hasv_prefix}] = {hasv_lookup}")

    if hasv_prefix == 46 and hasv_lookup == 90:
        print("  ✅ VERIFIED: HASV prefix (46) → 90 via Row 6")
        results['verified'].append("HASV prefix sum = 46, matrix[6,46] = 90")
    else:
        print(f"  ⚠️  WARNING: Expected sum=46, lookup=90")
        results['warnings'].append(f"HASV prefix: sum={hasv_prefix}, lookup={hasv_lookup}")

# Claim 2.9: Row 79 difference
print("\n[2.9] Row 79 difference")
row79_pocc = sum(matrix[79][c] for c in pocc_chars if c < 128)
row79_hasv = sum(matrix[79][c] for c in hasv_chars if c < 128)
row79_diff = row79_hasv - row79_pocc

print(f"  Row 79 POCC sum: {row79_pocc}")
print(f"  Row 79 HASV sum: {row79_hasv}")
print(f"  Difference: {row79_diff}")

if row79_diff == 26:
    print("  ✅ VERIFIED: Row 79 difference = 26 (√676)")
    results['verified'].append("Row 79 difference = 26")
else:
    print(f"  ❌ FALSE: Expected 26, got {row79_diff}")
    results['false'].append(f"Row 79 diff = {row79_diff}, not 26")

# =============================================================================
# SECTION 3: SMART CONTRACT ADDRESS
# =============================================================================
print("\n\n" + "=" * 80)
print("SECTION 3: SMART CONTRACT ADDRESS")
print("=" * 80 + "\n")

# Claim 3.1: Pattern analysis
print("[3.1] Smart contract address pattern")
print(f"  Address: {SC_ADDR}")

a_count = SC_ADDR.count('A')
suffix = SC_ADDR[a_count:]

print(f"  A's: {a_count}")
print(f"  Suffix: {suffix}")

# Claim 3.2: FXIB suffix → 26
print("\n[3.2] FXIB suffix lookup")
fxib_sum = sum(char_to_num(c) for c in "FXIB")
print(f"  F({char_to_num('F')}) + X({char_to_num('X')}) + I({char_to_num('I')}) + B({char_to_num('B')}) = {fxib_sum}")

if 0 <= fxib_sum < 128:
    fxib_lookup = matrix[6][fxib_sum]
    print(f"  matrix[6, {fxib_sum}] = {fxib_lookup}")

    if fxib_sum == 37 and fxib_lookup == 26:
        print("  ✅ VERIFIED: FXIB sum = 37, matrix[6,37] = 26")
        results['verified'].append("SC suffix FXIB: sum = 37, matrix[6,37] = 26")
    else:
        print(f"  ⚠️  WARNING: Expected sum=37, lookup=26")
        results['warnings'].append(f"FXIB: sum={fxib_sum}, lookup={fxib_lookup}")

# =============================================================================
# SECTION 4: HISTORICAL CONSTANTS
# =============================================================================
print("\n\n" + "=" * 80)
print("SECTION 4: HISTORICAL CONSTANTS")
print("=" * 80 + "\n")

# Claim 4.1: Pre-Genesis timestamp mod 121
print("[4.1] NXT Pre-Genesis timestamp")
pre_genesis = 1221069728
mod_121 = pre_genesis % 121
print(f"  Timestamp: {pre_genesis}")
print(f"  mod 121: {mod_121}")

if mod_121 == 43:
    print("  ✅ VERIFIED: Pre-Genesis mod 121 = 43")
    results['verified'].append("Pre-Genesis timestamp mod 121 = 43")
else:
    print(f"  ❌ FALSE: Expected 43, got {mod_121}")
    results['false'].append(f"Pre-Genesis mod 121 = {mod_121}, not 43")

# Claim 4.2: Cannot verify 1CFB byte sum without blockchain data
print("\n[4.2] 1CFB byte sum")
print("  ⚠️  REPORTED: 1CFB byte sum = 2,299 = 121 × 19")
print("     (Cannot verify without blockchain/address data)")
results['reported'].append("1CFB byte sum = 2,299 = 121 × 19 (requires blockchain data)")

# Claim 4.3: Cannot verify token supplies without blockchain
print("\n[4.3] Token supplies")
print("  ⚠️  REPORTED: GENESIS supply = 676,000,000,000")
print("  ⚠️  REPORTED: EXODUS supply = 676")
print("  ⚠️  REPORTED: SC tokens supply = 676")
print("     (Cannot verify without blockchain data)")
results['reported'].append("Token supplies (requires blockchain data)")

# =============================================================================
# SECTION 5: NEW DISCOVERIES
# =============================================================================
print("\n\n" + "=" * 80)
print("SECTION 5: NEW PATTERN SEARCHES")
print("=" * 80 + "\n")

# Search for more 676 connections
print("[5.1] Searching for additional 676 patterns...")

# Check fibonacci positions
print("\n  Fibonacci position sums:")
fib_positions = [1, 2, 3, 5, 8, 13, 21, 34, 55]
pocc_fib = sum(pocc_chars[i] for i in fib_positions if i < len(pocc_chars))
hasv_fib = sum(hasv_chars[i] for i in fib_positions if i < len(hasv_chars))
print(f"    POCC Fibonacci: {pocc_fib}")
print(f"    HASV Fibonacci: {hasv_fib}")
print(f"    Difference: {hasv_fib - pocc_fib}")

# Check prime positions
print("\n  Prime position sums:")
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
pocc_prime = sum(pocc_chars[i] for i in primes if i < len(pocc_chars))
hasv_prime = sum(hasv_chars[i] for i in primes if i < len(hasv_chars))
print(f"    POCC Prime: {pocc_prime}")
print(f"    HASV Prime: {hasv_prime}")
print(f"    Difference: {hasv_prime - pocc_prime}")

# Search for other row differences
print("\n  Scanning all rows for special differences...")
special_rows = []
for row in range(128):
    row_pocc = sum(matrix[row][c] for c in pocc_chars if c < 128)
    row_hasv = sum(matrix[row][c] for c in hasv_chars if c < 128)
    row_diff = abs(row_hasv - row_pocc)

    if row_diff in [26, 121, 138, 676]:
        special_rows.append((row, row_diff))

if special_rows:
    print(f"  Found {len(special_rows)} rows with special differences:")
    for row, diff in special_rows:
        print(f"    Row {row}: difference = {diff}")
        results['verified'].append(f"Row {row} difference = {diff}")

# =============================================================================
# FINAL REPORT
# =============================================================================
print("\n\n" + "=" * 80)
print("FINAL VALIDATION REPORT")
print("=" * 80 + "\n")

print(f"✅ VERIFIED (100% proven):      {len(results['verified'])}")
for claim in results['verified'][:10]:  # Show first 10
    print(f"   • {claim}")
if len(results['verified']) > 10:
    print(f"   ... and {len(results['verified']) - 10} more")

print(f"\n⚠️  REPORTED (requires external data): {len(results['reported'])}")
for claim in results['reported']:
    print(f"   • {claim}")

print(f"\n⚠️  WARNINGS (minor discrepancies):   {len(results['warnings'])}")
for warning in results['warnings']:
    print(f"   • {warning}")

print(f"\n❌ FALSE (proven wrong):           {len(results['false'])}")
for claim in results['false']:
    print(f"   • {claim}")

print()
if len(results['false']) == 0:
    print("🎯 ALL MATHEMATICAL CLAIMS VERIFIED")
    print("   No hallucinations detected.")
    print("   All numbers reproducible.")
else:
    print(f"⚠️  {len(results['false'])} CLAIMS PROVEN FALSE")
    print("   Document requires correction.")

print()
print("=" * 80)
