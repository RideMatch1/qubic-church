#!/usr/bin/env python3
"""
===============================================================================
        ADDRESS PAIR SCANNER - Testing POCC/HASV Uniqueness
===============================================================================
The strongest finding is the POCC/HASV mathematical connection (15+ proofs).
But is this genuinely unique, or do MANY Qubic address pairs show similar patterns?

This script generates thousands of random Qubic-format address pairs and checks
if they show the same mathematical connections as POCC/HASV.

PRE-REGISTERED HYPOTHESES:
  H1: The POCC/HASV diagonal difference of 676 is rare among random pairs
  H2: Having char diff = XOR = 138 simultaneously is rare
  H3: Having >= 6 identical character positions is rare
  H4: Having >= 3 matching modular properties (mod 6, 23, 46) is rare
  H5: The combined pattern (ALL of the above) is extremely rare

SIGNIFICANCE: p < 0.001 (Bonferroni-corrected for 5 tests: p < 0.0002)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime
from functools import reduce

script_dir = Path(__file__).parent

print("=" * 80)
print("         ADDRESS PAIR SCANNER")
print("         Testing POCC/HASV Uniqueness")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int16)
print(f"Matrix loaded: {matrix.shape}")

SIMULATIONS = 100000
BONFERRONI = 5
SIGNIFICANCE = 0.001 / BONFERRONI

# ============================================================================
# REFERENCE: POCC/HASV Properties
# ============================================================================
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_val(c):
    return ord(c.upper()) - ord('A')

def address_properties(addr1, addr2, m):
    """Compute all mathematical properties between two addresses."""
    # Character sums
    sum1 = sum(char_val(c) for c in addr1)
    sum2 = sum(char_val(c) for c in addr2)
    char_diff = abs(sum2 - sum1)

    # Diagonal sums
    diag1 = sum(int(m[char_val(c), char_val(c)]) for c in addr1)
    diag2 = sum(int(m[char_val(c), char_val(c)]) for c in addr2)
    diag_diff = abs(diag2 - diag1)

    # XOR of character sums
    xor_val = sum1 ^ sum2

    # Identical positions
    identical = sum(1 for a, b in zip(addr1, addr2) if a == b)

    # Modular properties
    mod_matches = 0
    for mod_val in [6, 23, 46]:
        if sum1 % mod_val == sum2 % mod_val:
            mod_matches += 1

    # Diagonal mod 676
    diag_mod_match = (diag1 % 676) == (diag2 % 676)

    return {
        'char_diff': char_diff,
        'diag_diff': diag_diff,
        'xor': xor_val,
        'identical_positions': identical,
        'mod_matches': mod_matches,
        'diag_mod_676_match': diag_mod_match,
        'char_diff_equals_xor': char_diff == xor_val,
    }

# Compute POCC/HASV reference properties
ref = address_properties(POCC, HASV, matrix)

print(f"\n  POCC/HASV Reference Properties:")
print(f"    Character sum difference: {ref['char_diff']}")
print(f"    Diagonal difference: {ref['diag_diff']}")
print(f"    XOR: {ref['xor']}")
print(f"    Char diff == XOR: {ref['char_diff_equals_xor']}")
print(f"    Identical positions: {ref['identical_positions']}")
print(f"    Modular matches (mod 6,23,46): {ref['mod_matches']}/3")
print(f"    Diagonal mod 676 match: {ref['diag_mod_676_match']}")

# ============================================================================
# SCAN: Random Address Pairs
# ============================================================================
print(f"\n  Scanning {SIMULATIONS:,} random address pairs...", end="", flush=True)

def random_qubic_address(length=60):
    return ''.join(chr(np.random.randint(0, 26) + ord('A')) for _ in range(length))

# Track how many random pairs match each property
count_diag_676 = 0
count_char_xor_match = 0
count_identical_ge6 = 0
count_mod_ge3 = 0
count_all_combined = 0
count_diag_mod_match = 0

random_diag_diffs = []
random_char_diffs = []
random_identical_counts = []
random_mod_match_counts = []

for i in range(SIMULATIONS):
    addr1 = random_qubic_address()
    addr2 = random_qubic_address()
    props = address_properties(addr1, addr2, matrix)

    random_diag_diffs.append(props['diag_diff'])
    random_char_diffs.append(props['char_diff'])
    random_identical_counts.append(props['identical_positions'])
    random_mod_match_counts.append(props['mod_matches'])

    if props['diag_diff'] == 676:
        count_diag_676 += 1
    if props['char_diff_equals_xor']:
        count_char_xor_match += 1
    if props['identical_positions'] >= 6:
        count_identical_ge6 += 1
    if props['mod_matches'] >= 3:
        count_mod_ge3 += 1
    if props['diag_mod_676_match']:
        count_diag_mod_match += 1

    # Combined: ALL properties match
    if (props['diag_diff'] == 676 and
        props['char_diff_equals_xor'] and
        props['identical_positions'] >= 6 and
        props['mod_matches'] >= 3):
        count_all_combined += 1

    if (i + 1) % 10000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_diag_diffs = np.array(random_diag_diffs)
random_char_diffs = np.array(random_char_diffs)
random_identical_counts = np.array(random_identical_counts)
random_mod_match_counts = np.array(random_mod_match_counts)

# ============================================================================
# RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

p1 = count_diag_676 / SIMULATIONS
p2 = count_char_xor_match / SIMULATIONS
p3 = count_identical_ge6 / SIMULATIONS
p4 = count_mod_ge3 / SIMULATIONS
p5 = count_all_combined / SIMULATIONS

print(f"\n  {'Property':<45} {'POCC/HASV':<12} {'Random':<20} {'p-value':<12}")
print("  " + "-" * 90)
print(f"  {'H1: Diagonal diff = 676':<45} {'676':<12} {f'mean={random_diag_diffs.mean():.0f}':<20} {p1:<12.8f}")
print(f"  {'H2: Char diff == XOR':<45} {'Yes':<12} {f'{count_char_xor_match}/{SIMULATIONS}':<20} {p2:<12.8f}")
print(f"  {'H3: Identical positions >= 6':<45} {ref['identical_positions']:<12} {f'mean={random_identical_counts.mean():.1f}':<20} {p3:<12.8f}")
mod_matches_str = str(ref['mod_matches']) + '/3'
mod_ge3_str = str(count_mod_ge3) + '/' + str(SIMULATIONS)
print(f"  {'H4: Mod matches >= 3/3':<45} {mod_matches_str:<12} {mod_ge3_str:<20} {p4:<12.8f}")
print(f"  {'H5: ALL combined':<45} {'Yes':<12} {f'{count_all_combined}/{SIMULATIONS}':<20} {p5:<12.8f}")

print(f"\n  Additional statistics:")
print(f"    Diagonal diff distribution: mean={random_diag_diffs.mean():.0f}, std={random_diag_diffs.std():.0f}, max={random_diag_diffs.max()}")
print(f"    Identical positions distribution: mean={random_identical_counts.mean():.1f}, max={random_identical_counts.max()}")
print(f"    Mod matches distribution: {dict(Counter(random_mod_match_counts))}")
print(f"    Diagonal mod 676 match: {count_diag_mod_match}/{SIMULATIONS} ({count_diag_mod_match/SIMULATIONS:.4%})")

# ============================================================================
# SIGNIFICANCE ASSESSMENT
# ============================================================================
print("\n" + "=" * 80)
print("SIGNIFICANCE ASSESSMENT")
print("=" * 80)

tests = [
    ("H1: Diagonal diff = 676", p1),
    ("H2: Char diff == XOR", p2),
    ("H3: Identical positions >= 6", p3),
    ("H4: Mod matches >= 3/3", p4),
    ("H5: ALL combined", p5),
]

print(f"\n  Bonferroni-corrected threshold: p < {SIGNIFICANCE:.6f}")
for name, p in tests:
    sig = "SIGNIFICANT" if p < SIGNIFICANCE else "NOT SIGNIFICANT"
    print(f"  {name:<35} p = {p:.8f}  {sig}")

# Combined significance (if individual tests are independent)
if all(p > 0 for _, p in tests[:4]):
    combined_p = p1 * p2 * p3 * p4  # Product of independent probabilities
    print(f"\n  Combined independent probability: {combined_p:.2e}")
    print(f"  1 in {1/combined_p:.0f} random pairs would match ALL 4 properties")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

is_unique = count_all_combined == 0
if is_unique:
    print(f"\n  RESULT: POCC/HASV combination is UNIQUE")
    print(f"  None of {SIMULATIONS:,} random pairs matched all properties simultaneously.")
    print(f"  This STRONGLY suggests deliberate design.")
else:
    print(f"\n  RESULT: POCC/HASV combination is NOT UNIQUE")
    print(f"  {count_all_combined} of {SIMULATIONS:,} random pairs matched all properties.")
    print(f"  The pattern may be less special than previously thought.")

# Save results
results = {
    "date": datetime.now().isoformat(),
    "simulations": SIMULATIONS,
    "significance_threshold": SIGNIFICANCE,
    "reference_pocc_hasv": ref,
    "random_pair_counts": {
        "diag_676": count_diag_676,
        "char_xor_match": count_char_xor_match,
        "identical_ge6": count_identical_ge6,
        "mod_ge3": count_mod_ge3,
        "diag_mod_match": count_diag_mod_match,
        "all_combined": count_all_combined,
    },
    "p_values": {
        "H1_diag_676": float(p1),
        "H2_char_xor": float(p2),
        "H3_identical": float(p3),
        "H4_mod_matches": float(p4),
        "H5_combined": float(p5),
    },
    "distributions": {
        "diag_diff_mean": float(random_diag_diffs.mean()),
        "diag_diff_std": float(random_diag_diffs.std()),
        "identical_mean": float(random_identical_counts.mean()),
    },
    "is_unique": is_unique,
}

output_path = script_dir / "ADDRESS_PAIR_SCANNER_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to: {output_path}")
