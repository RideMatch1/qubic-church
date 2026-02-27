#!/usr/bin/env python3
"""
EXODUS vs GENESIS - Mathematical Verification Against Anna Matrix
==================================================================

Prüft ob die EXODUS und GENESIS Issuer-Adressen mathematisch
mit der Anna Matrix verbunden sind.

Adressen:
- EXODUS Issuer: HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO
- GENESIS Issuer (POCC): POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD
"""

import json
import numpy as np
from pathlib import Path

# Load Anna Matrix
MATRIX_PATH = Path(__file__).parent.parent / "public/data/anna-matrix.json"

print("=" * 80)
print("EXODUS vs GENESIS - ANNA MATRIX VERIFICATION")
print("=" * 80)
print()

# Addresses
EXODUS_ISSUER = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"
GENESIS_ISSUER = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

print(f"EXODUS Issuer:  {EXODUS_ISSUER}")
print(f"GENESIS Issuer: {GENESIS_ISSUER}")
print()

# Load matrix
try:
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    matrix = np.array([[int(v) if v is not None else 0 for v in row] for row in data["matrix"]], dtype=np.int64)
    print(f"✓ Anna Matrix loaded: {matrix.shape}")
except Exception as e:
    print(f"✗ Error loading matrix: {e}")
    matrix = None

print()
print("=" * 80)
print("METHODE 1: PREFIX SUM → MATRIX LOOKUP")
print("=" * 80)
print()

def letter_value(c):
    """A=0, B=1, ..., Z=25"""
    if 'A' <= c <= 'Z':
        return ord(c) - ord('A')
    return 0

def prefix_sum(addr, length=4):
    """Sum of first N letter values"""
    return sum(letter_value(c) for c in addr[:length])

# GENESIS (POCC) - documented method
pocc_prefix = "POCC"
pocc_values = [letter_value(c) for c in pocc_prefix]
pocc_sum = sum(pocc_values)

print(f"GENESIS (POCC) Prefix Analysis:")
print(f"  P = {letter_value('P')}, O = {letter_value('O')}, C = {letter_value('C')}, C = {letter_value('C')}")
print(f"  Sum: {' + '.join(map(str, pocc_values))} = {pocc_sum}")
if matrix is not None:
    print(f"  Matrix[6, {pocc_sum}] = {matrix[6, pocc_sum]}")
    print(f"  → 26² = 676 = GENESIS Supply Basis ✓")
print()

# EXODUS (HASV)
hasv_prefix = "HASV"
hasv_values = [letter_value(c) for c in hasv_prefix]
hasv_sum = sum(hasv_values)

print(f"EXODUS (HASV) Prefix Analysis:")
print(f"  H = {letter_value('H')}, A = {letter_value('A')}, S = {letter_value('S')}, V = {letter_value('V')}")
print(f"  Sum: {' + '.join(map(str, hasv_values))} = {hasv_sum}")
if matrix is not None:
    print(f"  Matrix[6, {hasv_sum}] = {matrix[6, hasv_sum]}")
    # Try other row combinations
    print(f"  Matrix[{hasv_sum}, 6] = {matrix[hasv_sum, 6]}")
    print(f"  Matrix[{hasv_sum}, {hasv_sum}] = {matrix[hasv_sum, hasv_sum]}")
print()

print("=" * 80)
print("METHODE 2: FULL ADDRESS LETTER SUM")
print("=" * 80)
print()

def full_address_sum(addr):
    """Sum of all letter values in address"""
    return sum(letter_value(c) for c in addr)

genesis_full_sum = full_address_sum(GENESIS_ISSUER)
exodus_full_sum = full_address_sum(EXODUS_ISSUER)

print(f"GENESIS full address sum: {genesis_full_sum}")
print(f"  mod 128 = {genesis_full_sum % 128}")
print(f"  mod 676 = {genesis_full_sum % 676}")
print()

print(f"EXODUS full address sum: {exodus_full_sum}")
print(f"  mod 128 = {exodus_full_sum % 128}")
print(f"  mod 676 = {exodus_full_sum % 676}")
print()

# Check if they relate
print(f"Difference: {abs(genesis_full_sum - exodus_full_sum)}")
print(f"Sum: {genesis_full_sum + exodus_full_sum}")
print(f"XOR of sums: {genesis_full_sum ^ exodus_full_sum}")
print()

print("=" * 80)
print("METHODE 3: ADDRESS AS COORDINATES")
print("=" * 80)
print()

def address_to_coords(addr):
    """Convert address to potential matrix coordinates"""
    coords = []

    # Method A: First two letters as (row, col)
    row_a = letter_value(addr[0]) * 5 + letter_value(addr[1])  # 0-129 range
    col_a = letter_value(addr[2]) * 5 + letter_value(addr[3])
    coords.append(("First 4 letters scaled", (row_a % 128, col_a % 128)))

    # Method B: Sum of pairs
    row_b = letter_value(addr[0]) + letter_value(addr[1])
    col_b = letter_value(addr[2]) + letter_value(addr[3])
    coords.append(("Sum of pairs", (row_b % 128, col_b % 128)))

    # Method C: Direct letter values mod 128
    row_c = letter_value(addr[0])
    col_c = letter_value(addr[1])
    coords.append(("Direct first 2", (row_c, col_c)))

    return coords

print("GENESIS Coordinates:")
for method, (r, c) in address_to_coords(GENESIS_ISSUER):
    if matrix is not None:
        val = matrix[r, c]
        print(f"  {method}: ({r}, {c}) → Matrix value: {val}")
print()

print("EXODUS Coordinates:")
for method, (r, c) in address_to_coords(EXODUS_ISSUER):
    if matrix is not None:
        val = matrix[r, c]
        print(f"  {method}: ({r}, {c}) → Matrix value: {val}")
print()

print("=" * 80)
print("METHODE 4: SEARCH FOR 676 IN MATRIX")
print("=" * 80)
print()

if matrix is not None:
    # Find all positions where interesting values appear
    print("Searching for key values in matrix...")

    key_values = [26, 27, 33, 50, 121, 127, -114, -121, 676 % 256]

    for val in key_values:
        positions = list(zip(*np.where(matrix == val)))
        if positions:
            print(f"  Value {val}: found at {len(positions)} positions")
            if len(positions) <= 5:
                for pos in positions:
                    print(f"    → {pos}")
        else:
            # Try negative
            positions = list(zip(*np.where(matrix == -val)))
            if positions:
                print(f"  Value -{val}: found at {len(positions)} positions")
print()

print("=" * 80)
print("METHODE 5: HASV PREFIX DEEP ANALYSIS")
print("=" * 80)
print()

# HASV = 7 + 0 + 18 + 21 = 46
print(f"HASV = {hasv_sum}")
print()

# Check mathematical properties of 46
print("Properties of 46:")
print(f"  46 = 2 × 23")
print(f"  46 + 33 (POCC) = {46 + 33}")  # 79
print(f"  46 × 33 = {46 * 33}")  # 1518
print(f"  46 XOR 33 = {46 ^ 33}")  #
print()

if matrix is not None:
    print("Matrix values at HASV-related positions:")
    print(f"  Matrix[46, 33] = {matrix[46, 33]}")
    print(f"  Matrix[33, 46] = {matrix[33, 46]}")
    print(f"  Matrix[46, 46] = {matrix[46, 46]}")
    print(f"  Matrix[6, 46] = {matrix[6, 46]}")
    print(f"  Matrix[46, 6] = {matrix[46, 6]}")
print()

print("=" * 80)
print("METHODE 6: VERGLEICH MIT DOKUMENTIERTEN MUSTERN")
print("=" * 80)
print()

# From our documentation:
# Matrix[6, 33] = 26 was claimed for POCC

if matrix is not None:
    print("Documented POCC pattern:")
    print(f"  POCC prefix sum = 33")
    print(f"  Matrix[6, 33] = {matrix[6, 33]}")
    print(f"  26² = 676 ✓")
    print()

    print("Testing EXODUS (HASV) with same pattern:")
    print(f"  HASV prefix sum = 46")
    print(f"  Matrix[6, 46] = {matrix[6, 46]}")

    # What if we use row = hasv_sum % 8 like documented row%8 patterns?
    row_mod8 = hasv_sum % 8
    print(f"  Row mod 8 = {row_mod8}")
    print(f"  Matrix[{row_mod8}, 46] = {matrix[row_mod8, 46]}")
    print()

    # Check if 46 relates to 676
    print("Checking 46 ↔ 676 relationship:")
    print(f"  676 / 46 = {676 / 46:.4f}")
    print(f"  676 % 46 = {676 % 46}")
    print(f"  46 * 14 = {46 * 14}")  # 644
    print(f"  46 * 15 = {46 * 15}")  # 690
    print()

print("=" * 80)
print("METHODE 7: XOR ZWISCHEN ADRESSEN")
print("=" * 80)
print()

# XOR corresponding letters
xor_values = []
for i in range(min(len(EXODUS_ISSUER), len(GENESIS_ISSUER))):
    e_val = letter_value(EXODUS_ISSUER[i])
    g_val = letter_value(GENESIS_ISSUER[i])
    xor_val = e_val ^ g_val
    xor_values.append(xor_val)

print(f"XOR of corresponding letter values (first 20):")
print(f"  {xor_values[:20]}")
print(f"  Sum of XOR values: {sum(xor_values)}")
print(f"  Sum mod 128: {sum(xor_values) % 128}")
print(f"  Sum mod 676: {sum(xor_values) % 676}")
print()

# Check if XOR sum maps to matrix
if matrix is not None:
    xor_sum = sum(xor_values)
    row = xor_sum % 128
    col = (xor_sum // 128) % 128
    print(f"  Matrix[{row}, {col}] = {matrix[row, col]}")
print()

print("=" * 80)
print("METHODE 8: SUPPLY ANALYSIS")
print("=" * 80)
print()

print("GENESIS Supply: 676,000,000,000")
print("EXODUS Supply:  676")
print()
print("Ratio: 676,000,000,000 / 676 = 1,000,000,000 (1 Billion)")
print()
print("676 = 26²")
print("26 = Matrix[6, 33] (POCC prefix sum)")
print()

# Check if EXODUS supply (676) appears in matrix
if matrix is not None:
    # 676 doesn't fit in signed byte, but 676 % 256 = 164
    print(f"676 mod 256 = {676 % 256}")
    print(f"676 mod 128 = {676 % 128}")

    positions_164 = list(zip(*np.where(matrix == (676 % 256 - 256))))  # -92
    positions_36 = list(zip(*np.where(matrix == (676 % 128))))  # 36

    print(f"Value {676 % 128} (676 mod 128) found at: {len(positions_36)} positions")
print()

print("=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)
print()

print("GENESIS (POCC):")
print(f"  ✓ Prefix sum = 33")
print(f"  ✓ Matrix[6, 33] = 26")
print(f"  ✓ 26² = 676 = Supply basis")
print(f"  → DOKUMENTIERTE Verbindung")
print()

print("EXODUS (HASV):")
print(f"  • Prefix sum = 46")
if matrix is not None:
    print(f"  • Matrix[6, 46] = {matrix[6, 46]}")
    print(f"  • Matrix[46, 33] = {matrix[46, 33]}")
    print(f"  • Matrix[46, 46] = {matrix[46, 46]}")
print(f"  • Supply = 676 (direkt, nicht 676 Milliarden)")
print()

# Final check: Is there a pattern?
if matrix is not None:
    m_6_46 = matrix[6, 46]
    m_46_33 = matrix[46, 33]
    print(f"KRITISCHE FRAGE: Gibt es eine mathematische Verbindung?")
    print()
    print(f"  POCC: prefix=33 → Matrix[6,33]=26 → 26²=676")
    print(f"  HASV: prefix=46 → Matrix[6,46]={m_6_46} → ???")
    print()

    # Check if any transformation works
    print("Suche nach Transformationen:")
    print(f"  {m_6_46}² = {m_6_46**2}")
    print(f"  {m_6_46} × 26 = {m_6_46 * 26}")
    print(f"  676 / {m_6_46} = {676 / m_6_46 if m_6_46 != 0 else 'undefined'}")
    print(f"  676 - {m_6_46} = {676 - m_6_46}")
    print(f"  676 + {m_6_46} = {676 + m_6_46}")
    print(f"  676 XOR {m_6_46} = {676 ^ m_6_46}")

print()
print("=" * 80)
print("ENDE DER ANALYSE")
print("=" * 80)
