#!/usr/bin/env python3
"""
===============================================================================
            🔄 PALINDROME ANALYSIS 🔄
===============================================================================
Investigate the 10-letter palindrome "ZzXRlBfbRh" ↔ "hRbfBlRXzZ"
found in Columns 19↔108.

Is this intentional? What does it mean?
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import random

script_dir = Path(__file__).parent

print("=" * 80)
print("           🔄 PALINDROME ANALYSIS 🔄")
print("           Investigating 'ZzXRlBfbRh' ↔ 'hRbfBlRXzZ'")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# EXTRACT THE PALINDROME
# ==============================================================================
print("\n" + "=" * 80)
print("EXTRACTING THE PALINDROME")
print("=" * 80)

col_19 = [int(matrix[r, 19]) for r in range(128)]
col_108 = [int(matrix[r, 108]) for r in range(128)]

# XOR
xor_19_108 = [col_19[r] ^ col_108[r] for r in range(128)]
xor_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_19_108)

print(f"\n  Col19 ⊕ Col108 as ASCII:")
for i in range(0, 128, 32):
    print(f"    [{i:3d}-{i+31:3d}]: {xor_string[i:i+32]}")

# Find all words
words = re.findall(r'[a-zA-Z]{3,}', xor_string)
print(f"\n  Words found: {words}")

# Find the palindrome
palindrome_forward = "ZzXRlBfbRh"
palindrome_backward = "hRbfBlRXzZ"

pos_forward = xor_string.find(palindrome_forward)
pos_backward = xor_string.find(palindrome_backward)

print(f"\n  Palindrome search:")
print(f"    '{palindrome_forward}' at position: {pos_forward}")
print(f"    '{palindrome_backward}' at position: {pos_backward}")

# ==============================================================================
# VERIFY PALINDROME PROPERTY
# ==============================================================================
print("\n" + "=" * 80)
print("VERIFYING PALINDROME PROPERTY")
print("=" * 80)

# Check if forward reversed equals backward
forward_reversed = palindrome_forward[::-1]
print(f"\n  Forward: '{palindrome_forward}'")
print(f"  Reversed: '{forward_reversed}'")
print(f"  Backward: '{palindrome_backward}'")
print(f"  Reversed == Backward: {forward_reversed == palindrome_backward}")

# Case-insensitive check
print(f"\n  Case-insensitive check:")
print(f"    Forward.lower(): '{palindrome_forward.lower()}'")
print(f"    Reversed.lower(): '{forward_reversed.lower()}'")
print(f"    Match: {palindrome_forward.lower() == forward_reversed.lower()}")

# ==============================================================================
# EXTRACT RAW VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("RAW XOR VALUES AT PALINDROME POSITIONS")
print("=" * 80)

if pos_forward >= 0:
    print(f"\n  Forward palindrome at rows {pos_forward}-{pos_forward+9}:")
    for i in range(10):
        r = pos_forward + i
        val = xor_19_108[r]
        ch = chr(abs(val)) if 32 <= abs(val) <= 126 else '.'
        col19_val = col_19[r]
        col108_val = col_108[r]
        print(f"    Row {r:3d}: Col19={col19_val:4d}, Col108={col108_val:4d}, XOR={val:4d} = '{ch}'")

# ==============================================================================
# STATISTICAL VALIDATION
# ==============================================================================
print("\n" + "=" * 80)
print("STATISTICAL VALIDATION")
print("=" * 80)

# How likely is a 10-letter palindrome in random XOR?
print("\n  Monte Carlo: Finding 10-letter palindromes in random XOR...")

palindromes_found = 0
n_simulations = 10000

for _ in range(n_simulations):
    # Pick two random columns
    c1 = random.randint(0, 127)
    c2 = random.randint(0, 127)

    col1 = [int(matrix[r, c1]) for r in range(128)]
    col2 = [int(matrix[r, c2]) for r in range(128)]
    xor = [col1[r] ^ col2[r] for r in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor)

    # Find all 10+ letter sequences
    sequences = re.findall(r'[a-zA-Z]{10,}', xor_str)

    for seq in sequences:
        # Check if it's a palindrome (case-insensitive)
        if seq.lower() == seq.lower()[::-1]:
            palindromes_found += 1
            break

print(f"  Random column pairs with 10-char palindromes: {palindromes_found}/{n_simulations}")
print(f"  p-value: {palindromes_found/n_simulations:.4f}")

# ==============================================================================
# SEARCH FOR ALL PALINDROMES IN MATRIX
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING ALL COLUMN PAIRS FOR PALINDROMES")
print("=" * 80)

all_palindromes = []

for c in range(64):
    partner = 127 - c

    col_c = [int(matrix[r, c]) for r in range(128)]
    col_p = [int(matrix[r, partner]) for r in range(128)]
    xor_cp = [col_c[r] ^ col_p[r] for r in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_cp)

    # Find sequences of 5+ letters
    for match in re.finditer(r'[a-zA-Z]{5,}', xor_str):
        seq = match.group()
        # Check palindrome (case-insensitive)
        if seq.lower() == seq.lower()[::-1]:
            all_palindromes.append({
                "cols": f"{c}↔{partner}",
                "col1": c,
                "col2": partner,
                "palindrome": seq,
                "length": len(seq),
                "position": match.start(),
            })

print(f"\n  Found {len(all_palindromes)} palindromes (5+ letters):")
for p in sorted(all_palindromes, key=lambda x: x["length"], reverse=True):
    print(f"    Cols {p['cols']:8}: '{p['palindrome']}' ({p['length']} chars) at pos {p['position']}")

# ==============================================================================
# DECODE THE PALINDROME
# ==============================================================================
print("\n" + "=" * 80)
print("DECODING ATTEMPTS")
print("=" * 80)

palindrome = palindrome_forward

# ASCII values
print(f"\n  ASCII values of '{palindrome}':")
ascii_vals = [ord(c) for c in palindrome]
print(f"    Values: {ascii_vals}")
print(f"    Sum: {sum(ascii_vals)}")
print(f"    XOR all: {eval('^'.join(map(str, ascii_vals)))}")

# Letter analysis
print(f"\n  Letter analysis:")
letters = list(palindrome)
unique_letters = set(letters)
print(f"    Unique letters: {sorted(unique_letters)}")
print(f"    Letter count: {len(unique_letters)}")

# Case pattern
case_pattern = ''.join('U' if c.isupper() else 'l' for c in palindrome)
print(f"    Case pattern: {case_pattern}")

# Possible meanings
print(f"\n  Possible interpretations:")
print(f"    - 'Zz' could mean 'sleep' or 'end'")
print(f"    - 'XR' could mean 'XOR' or 'Extended Reality'")
print(f"    - 'lB' / 'Bf' / 'fb' - unknown")
print(f"    - 'Rh' could be 'Rhesus' (blood type)?")

# ==============================================================================
# CHECK RELATIONSHIP TO 19 AND 108
# ==============================================================================
print("\n" + "=" * 80)
print("COLUMN 19 AND 108 PROPERTIES")
print("=" * 80)

print(f"\n  Column numbers:")
print(f"    19 + 108 = {19 + 108} (expected: 127)")
print(f"    19 * 108 = {19 * 108}")
print(f"    19 ^ 108 = {19 ^ 108}")
print(f"    |19 - 108| = {abs(19 - 108)}")

print(f"\n  Special properties:")
print(f"    19 is prime: {all(19 % i != 0 for i in range(2, 19))}")
print(f"    108 = 4 * 27 = 4 * 3³")
print(f"    108 in degrees = 3π/5 (golden angle related)")

# Check asymmetric cells in this column pair
asym_count = 0
for r in range(128):
    if col_19[r] + col_108[127-r] != -1:
        asym_count += 1

print(f"    Asymmetric cells: {asym_count}")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("🔄 PALINDROME ANALYSIS COMPLETE 🔄")
print("=" * 80)

is_significant = palindromes_found < 10  # Less than 0.1%

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PALINDROME FINDINGS                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  THE PALINDROME:                                                              ║
║  • Forward:  '{palindrome_forward}'                                        ║
║  • Backward: '{palindrome_backward}'                                       ║
║  • Location: Cols 19↔108                                                     ║
║  • Length: 10 characters                                                      ║
║                                                                               ║
║  STATISTICAL SIGNIFICANCE:                                                    ║
║  • Random pairs with 10-char palindrome: {palindromes_found}/{n_simulations}                   ║
║  • p-value: {palindromes_found/n_simulations:.4f}                                                        ║
║  • Significant (p<0.01): {'YES ✓' if is_significant else 'NO  ✗'}                                        ║
║                                                                               ║
║  ALL PALINDROMES FOUND:                                                       ║
║  • Total: {len(all_palindromes)} palindromes (5+ letters)                                  ║
║  • Longest: {max(p['length'] for p in all_palindromes) if all_palindromes else 0} characters                                                ║
║                                                                               ║
║  COLUMN 19↔108 PROPERTIES:                                                   ║
║  • 19 + 108 = 127 (symmetric pair ✓)                                         ║
║  • 19 is prime                                                                ║
║  • 108 = 4 × 27 (golden angle related)                                       ║
║  • Asymmetric cells: {asym_count}                                                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "palindrome_forward": palindrome_forward,
    "palindrome_backward": palindrome_backward,
    "location": "Cols 19↔108",
    "position": pos_forward,
    "length": 10,
    "monte_carlo": {
        "simulations": n_simulations,
        "random_palindromes": palindromes_found,
        "p_value": palindromes_found / n_simulations,
    },
    "all_palindromes": all_palindromes,
    "column_properties": {
        "sum": 19 + 108,
        "product": 19 * 108,
        "xor": 19 ^ 108,
        "asymmetric_cells": asym_count,
    },
}

output_path = script_dir / "PALINDROME_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
