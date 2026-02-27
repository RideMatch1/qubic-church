#!/usr/bin/env python3
"""
FINAL DOCUMENT VERIFICATION
============================
Verifies EVERY single number in POCC_HASV_COMPLETE_ANALYSIS.txt
against the Anna Matrix and actual calculations.

This is the final stamp of approval before publication.
"""

import json
import numpy as np

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
print("FINAL DOCUMENT VERIFICATION")
print("=" * 80)
print()
print("Verifying every number in POCC_HASV_COMPLETE_ANALYSIS.txt")
print()

errors = []
verified = []

# ============================================================================
# SECTION 3.1: CHARACTER SUMS
# ============================================================================
print("[3.1] CHARACTER SUMS")
print("-" * 60)

pocc_chars = [char_to_num(c) for c in POCC if c.isalpha()]
hasv_chars = [char_to_num(c) for c in HASV if c.isalpha()]

pocc_sum = sum(pocc_chars)
hasv_sum = sum(hasv_chars)
diff = hasv_sum - pocc_sum

print(f"POCC sum: {pocc_sum}")
print(f"Document claims: 612")
if pocc_sum == 612:
    print("✅ VERIFIED")
    verified.append("POCC sum = 612")
else:
    print(f"❌ ERROR: Document says 612, actual is {pocc_sum}")
    errors.append(f"POCC sum: claimed 612, actual {pocc_sum}")

print()
print(f"HASV sum: {hasv_sum}")
print(f"Document claims: 750")
if hasv_sum == 750:
    print("✅ VERIFIED")
    verified.append("HASV sum = 750")
else:
    print(f"❌ ERROR: Document says 750, actual is {hasv_sum}")
    errors.append(f"HASV sum: claimed 750, actual {hasv_sum}")

print()
print(f"Difference: {diff}")
print(f"Document claims: 138")
if diff == 138:
    print("✅ VERIFIED")
    verified.append("Difference = 138")
else:
    print(f"❌ ERROR: Document says 138, actual is {diff}")
    errors.append(f"Difference: claimed 138, actual {diff}")

# ============================================================================
# SECTION 3.2: XOR
# ============================================================================
print()
print("[3.2] XOR")
print("-" * 60)

xor = pocc_sum ^ hasv_sum
print(f"XOR: {xor}")
print(f"Document claims: 138")
if xor == 138:
    print("✅ VERIFIED")
    verified.append("XOR = 138")
else:
    print(f"❌ ERROR: Document says 138, actual is {xor}")
    errors.append(f"XOR: claimed 138, actual {xor}")

# ============================================================================
# SECTION 3.3: 1-BASED SUMS
# ============================================================================
print()
print("[3.3] 1-BASED SUMS")
print("-" * 60)

pocc_1based = sum(c + 1 for c in pocc_chars)
hasv_1based = sum(c + 1 for c in hasv_chars)

print(f"POCC 1-based: {pocc_1based}")
print(f"Document claims: 672")
if pocc_1based == 672:
    print("✅ VERIFIED")
    verified.append("POCC 1-based = 672")
else:
    print(f"❌ ERROR: Document says 672, actual is {pocc_1based}")
    errors.append(f"POCC 1-based: claimed 672, actual {pocc_1based}")

print()
distance = abs(pocc_1based - 676)
error_pct = (distance / 676) * 100
print(f"Distance from 676: {distance}")
print(f"Error percentage: {error_pct:.2f}%")
print(f"Document claims: 0.59%")
if abs(error_pct - 0.59) < 0.01:
    print("✅ VERIFIED")
    verified.append("Error = 0.59%")
else:
    print(f"❌ ERROR: Document says 0.59%, actual is {error_pct:.2f}%")
    errors.append(f"Error %: claimed 0.59%, actual {error_pct:.2f}%")

# ============================================================================
# SECTION 3.4: IDENTICAL POSITIONS
# ============================================================================
print()
print("[3.4] IDENTICAL POSITIONS")
print("-" * 60)

identical = [i for i in range(60) if POCC[i] == HASV[i]]
print(f"Identical positions: {identical}")
print(f"Document claims: [7, 34, 41, 48, 53, 57]")
if identical == [7, 34, 41, 48, 53, 57]:
    print("✅ VERIFIED")
    verified.append("6 identical positions at correct locations")
else:
    print(f"❌ ERROR: Mismatch in positions")
    errors.append(f"Identical positions: claimed [7,34,41,48,53,57], actual {identical}")

print()
position_sum = sum(identical)
print(f"Sum of positions: {position_sum}")
print(f"Document claims: 240")
if position_sum == 240:
    print("✅ VERIFIED")
    verified.append("Position sum = 240")
else:
    print(f"❌ ERROR: Document says 240, actual is {position_sum}")
    errors.append(f"Position sum: claimed 240, actual {position_sum}")

print()
mod_26 = position_sum % 26
print(f"240 mod 26: {mod_26}")
print(f"Document claims: 6")
if mod_26 == 6:
    print("✅ VERIFIED (self-referential!)")
    verified.append("240 mod 26 = 6")
else:
    print(f"❌ ERROR: Document says 6, actual is {mod_26}")
    errors.append(f"240 mod 26: claimed 6, actual {mod_26}")

# ============================================================================
# SECTION 4.1: DIAGONAL SUMS
# ============================================================================
print()
print("[4.1] DIAGONAL SUMS")
print("-" * 60)

pocc_diag = sum(matrix[c][c] for c in pocc_chars if c < 128)
hasv_diag = sum(matrix[c][c] for c in hasv_chars if c < 128)
diag_diff = hasv_diag - pocc_diag

print(f"POCC diagonal: {pocc_diag}")
print(f"Document claims: -1,231")
if pocc_diag == -1231:
    print("✅ VERIFIED")
    verified.append("POCC diagonal = -1,231")
else:
    print(f"❌ ERROR: Document says -1,231, actual is {pocc_diag}")
    errors.append(f"POCC diagonal: claimed -1231, actual {pocc_diag}")

print()
print(f"HASV diagonal: {hasv_diag}")
print(f"Document claims: -555")
if hasv_diag == -555:
    print("✅ VERIFIED")
    verified.append("HASV diagonal = -555")
else:
    print(f"❌ ERROR: Document says -555, actual is {hasv_diag}")
    errors.append(f"HASV diagonal: claimed -555, actual {hasv_diag}")

print()
print(f"Difference: {diag_diff}")
print(f"Document claims: 676")
if diag_diff == 676:
    print("✅ VERIFIED - EXACT!")
    verified.append("Diagonal difference = 676 EXACT")
else:
    print(f"❌ ERROR: Document says 676, actual is {diag_diff}")
    errors.append(f"Diagonal diff: claimed 676, actual {diag_diff}")

# ============================================================================
# SECTION 4.2: ROW 6 PROPERTIES
# ============================================================================
print()
print("[4.2] ROW 6 PROPERTIES")
print("-" * 60)

row6 = matrix[6]
count_26 = np.sum(row6 == 26)
pct_26 = (count_26 / 128) * 100

print(f"Value 26 in Row 6: {count_26}/128 times")
print(f"Percentage: {pct_26:.1f}%")
print(f"Document claims: 18.8%")
if abs(pct_26 - 18.8) < 0.1:
    print("✅ VERIFIED")
    verified.append("Row 6: value 26 appears 18.8%")
else:
    print(f"❌ ERROR: Document says 18.8%, actual is {pct_26:.1f}%")
    errors.append(f"Row 6 %: claimed 18.8%, actual {pct_26:.1f}%")

print()
pocc_prefix = sum(char_to_num(c) for c in "POCC")
print(f"POCC prefix sum: {pocc_prefix}")
print(f"Document claims: 33")
if pocc_prefix == 33:
    print("✅ VERIFIED")
    verified.append("POCC prefix = 33")
else:
    print(f"❌ ERROR: Document says 33, actual is {pocc_prefix}")
    errors.append(f"POCC prefix: claimed 33, actual {pocc_prefix}")

print()
lookup_33 = matrix[6][33]
print(f"matrix[6, 33]: {lookup_33}")
print(f"Document claims: 26")
if lookup_33 == 26:
    print("✅ VERIFIED")
    verified.append("matrix[6,33] = 26")
else:
    print(f"❌ ERROR: Document says 26, actual is {lookup_33}")
    errors.append(f"matrix[6,33]: claimed 26, actual {lookup_33}")

print()
hasv_prefix = sum(char_to_num(c) for c in "HASV")
print(f"HASV prefix sum: {hasv_prefix}")
print(f"Document claims: 46")
if hasv_prefix == 46:
    print("✅ VERIFIED")
    verified.append("HASV prefix = 46")
else:
    print(f"❌ ERROR: Document says 46, actual is {hasv_prefix}")
    errors.append(f"HASV prefix: claimed 46, actual {hasv_prefix}")

print()
lookup_46 = matrix[6][46]
print(f"matrix[6, 46]: {lookup_46}")
print(f"Document claims: 90")
if lookup_46 == 90:
    print("✅ VERIFIED")
    verified.append("matrix[6,46] = 90")
else:
    print(f"❌ ERROR: Document says 90, actual is {lookup_46}")
    errors.append(f"matrix[6,46]: claimed 90, actual {lookup_46}")

# ============================================================================
# SECTION 4.3: MODULAR PROPERTIES
# ============================================================================
print()
print("[4.3] MODULAR PROPERTIES")
print("-" * 60)

print("Character sums:")
for mod in [6, 23, 46]:
    pocc_mod = pocc_sum % mod
    hasv_mod = hasv_sum % mod
    print(f"  mod {mod}: POCC={pocc_mod}, HASV={hasv_mod}")
    if pocc_mod == hasv_mod:
        print(f"    ✅ VERIFIED: Both = {pocc_mod}")
        verified.append(f"Both mod {mod} = {pocc_mod}")
    else:
        print(f"    ❌ ERROR: Not identical!")
        errors.append(f"mod {mod}: POCC={pocc_mod}, HASV={hasv_mod}")

print()
print("Diagonal sums:")
for mod in [26, 676]:
    pocc_diag_mod = pocc_diag % mod
    hasv_diag_mod = hasv_diag % mod
    print(f"  mod {mod}: POCC={pocc_diag_mod}, HASV={hasv_diag_mod}")
    if pocc_diag_mod == hasv_diag_mod:
        result = "11²" if mod == 676 and pocc_diag_mod == 121 else pocc_diag_mod
        print(f"    ✅ VERIFIED: Both = {result}")
        verified.append(f"Both diagonal mod {mod} = {pocc_diag_mod}")
    else:
        print(f"    ❌ ERROR: Not identical!")
        errors.append(f"diag mod {mod}: POCC={pocc_diag_mod}, HASV={hasv_diag_mod}")

# ============================================================================
# SECTION 4.4: POSITION 34
# ============================================================================
print()
print("[4.4] POSITION 34")
print("-" * 60)

char_34 = POCC[34]
print(f"POCC[34]: '{char_34}'")
print(f"HASV[34]: '{HASV[34]}'")
print(f"Document claims: Both = 'H'")

if char_34 == 'H' and HASV[34] == 'H':
    print("✅ VERIFIED: Both = 'H'")
    verified.append("Position 34 = 'H' (both)")

    h_val = char_to_num('H')
    matrix_h = matrix[h_val][h_val]
    print(f"H = {h_val}")
    print(f"matrix[{h_val}, {h_val}] = {matrix_h}")
    print(f"Document claims: 26")

    if matrix_h == 26:
        print("✅ VERIFIED")
        verified.append("matrix[7,7] = 26")
    else:
        print(f"❌ ERROR: Document says 26, actual is {matrix_h}")
        errors.append(f"matrix[7,7]: claimed 26, actual {matrix_h}")
else:
    print(f"❌ ERROR: Position 34 mismatch")
    errors.append(f"Position 34: claimed 'H' (both), actual POCC={char_34}, HASV={HASV[34]}")

# ============================================================================
# SECTION 4.5: ROW 79
# ============================================================================
print()
print("[4.5] ROW 79")
print("-" * 60)

row79_pocc = sum(matrix[79][c] for c in pocc_chars if c < 128)
row79_hasv = sum(matrix[79][c] for c in hasv_chars if c < 128)
row79_diff = row79_hasv - row79_pocc

print(f"Row 79 POCC: {row79_pocc}")
print(f"Row 79 HASV: {row79_hasv}")
print(f"Difference: {row79_diff}")
print(f"Document claims: 26")

if row79_diff == 26:
    print("✅ VERIFIED")
    verified.append("Row 79 difference = 26")
else:
    print(f"❌ ERROR: Document says 26, actual is {row79_diff}")
    errors.append(f"Row 79 diff: claimed 26, actual {row79_diff}")

# ============================================================================
# SECTION 5.1: CUBES
# ============================================================================
print()
print("[5.1] CUBES")
print("-" * 60)

pocc_cubes = sum(c**3 for c in pocc_chars)
hasv_cubes = sum(c**3 for c in hasv_chars)
cubes_diff = hasv_cubes - pocc_cubes

print(f"POCC cubes: {pocc_cubes}")
print(f"Document claims: 162,324")
if pocc_cubes == 162324:
    print("✅ VERIFIED")
    verified.append("POCC cubes = 162,324")
else:
    print(f"❌ ERROR: Document says 162,324, actual is {pocc_cubes}")
    errors.append(f"POCC cubes: claimed 162324, actual {pocc_cubes}")

print()
print(f"HASV cubes: {hasv_cubes}")
print(f"Document claims: 259,668")
if hasv_cubes == 259668:
    print("✅ VERIFIED")
    verified.append("HASV cubes = 259,668")
else:
    print(f"❌ ERROR: Document says 259,668, actual is {hasv_cubes}")
    errors.append(f"HASV cubes: claimed 259668, actual {hasv_cubes}")

print()
print(f"Difference: {cubes_diff}")
print(f"Document claims: 97,344")
if cubes_diff == 97344:
    print("✅ VERIFIED")
    verified.append("Cubes difference = 97,344")
else:
    print(f"❌ ERROR: Document says 97,344, actual is {cubes_diff}")
    errors.append(f"Cubes diff: claimed 97344, actual {cubes_diff}")

print()
division = cubes_diff / 676
print(f"97,344 ÷ 676 = {division}")
print(f"Document claims: 144 (= 12²)")
if division == 144:
    print("✅ VERIFIED - Perfect square!")
    verified.append("97,344 = 144 × 676")
else:
    print(f"❌ ERROR: Document says 144, actual is {division}")
    errors.append(f"Cubes/676: claimed 144, actual {division}")

# ============================================================================
# SECTION 5.4: IDENTICAL CHAR SUM
# ============================================================================
print()
print("[5.4] IDENTICAL CHARACTER SUM")
print("-" * 60)

identical_chars = [char_to_num(POCC[i]) for i in identical]
identical_sum = sum(identical_chars)

print(f"Characters at identical positions: {[POCC[i] for i in identical]}")
print(f"Sum: {identical_sum}")
print(f"Document claims: 46")

if identical_sum == 46:
    print("✅ VERIFIED")
    verified.append("Identical char sum = 46")
else:
    print(f"❌ ERROR: Document says 46, actual is {identical_sum}")
    errors.append(f"Identical char sum: claimed 46, actual {identical_sum}")

# ============================================================================
# FINAL REPORT
# ============================================================================
print()
print("=" * 80)
print("FINAL VERIFICATION REPORT")
print("=" * 80)
print()

print(f"✅ VERIFIED CLAIMS: {len(verified)}")
for claim in verified:
    print(f"   • {claim}")

print()
print(f"❌ ERRORS FOUND: {len(errors)}")
if errors:
    for error in errors:
        print(f"   • {error}")
else:
    print("   NONE - All numbers in document are correct!")

print()
if len(errors) == 0:
    print("🎯 DOCUMENT IS 100% ACCURATE")
    print("   Every number verified against Anna Matrix")
    print("   Ready for publication")
else:
    print(f"⚠️  DOCUMENT HAS {len(errors)} ERRORS")
    print("   Must be corrected before publication")

print()
print("=" * 80)
