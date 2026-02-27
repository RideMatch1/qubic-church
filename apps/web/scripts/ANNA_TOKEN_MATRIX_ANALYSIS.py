#!/usr/bin/env python3
"""
===============================================================================
        ANNA TOKEN ISSUER ADDRESS - MATRIX ANALYSIS
===============================================================================
Analyzes the ANNA token issuer address against the Anna Matrix,
comparing properties with known POCC and HASV addresses.

Token: ANNA
Market Cap: $17.3K
Circulating Supply: 33,299,999,900
Max Supply: 900,000,000,000
Total Supply: 33,299,999,900
Issue Date: 2026-01-23 20:37:45
Issuer: HIFUSWQYNUZTSDRPXZOXXIWUPWTAOVJUTCVLFIHLHARCXSARRTGCJLGGAREO
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import random
import math

# Setup paths
script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
output_path = script_dir / "ANNA_TOKEN_RESULTS.json"

# Load matrix
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int16)

# Addresses
ANNA_ISSUER = "HIFUSWQYNUZTSDRPXZOXXIWUPWTAOVJUTCVLFIHLHARCXSARRTGCJLGGAREO"
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    """A=0, B=1, ..., Z=25"""
    return ord(c.upper()) - ord('A')

# Set deterministic seed for Monte Carlo
np.random.seed(42)
random.seed(42)

print("=" * 80)
print("    ANNA TOKEN ISSUER ADDRESS - MATRIX ANALYSIS")
print("=" * 80)
print(f"Date: {datetime.now().isoformat()}")
print(f"ANNA:  {ANNA_ISSUER}")
print(f"POCC:  {POCC}")
print(f"HASV:  {HASV}")
print()

results = {
    "analysis_date": datetime.now().isoformat(),
    "addresses": {
        "ANNA_ISSUER": ANNA_ISSUER,
        "POCC": POCC,
        "HASV": HASV
    },
    "token_info": {
        "name": "ANNA",
        "market_cap_usd": 17300,
        "circulating_supply": 33299999900,
        "max_supply": 900000000000,
        "total_supply": 33299999900,
        "issue_date": "2026-01-23T20:37:45"
    }
}

# ============================================================================
# ANALYSIS 1: Diagonal Sum
# ============================================================================
print("\n" + "=" * 80)
print("[1] DIAGONAL SUM COMPUTATION")
print("=" * 80)

anna_vals = [char_to_num(c) for c in ANNA_ISSUER]
pocc_vals = [char_to_num(c) for c in POCC]
hasv_vals = [char_to_num(c) for c in HASV]

anna_diag = sum(int(matrix[v][v]) for v in anna_vals)
pocc_diag = sum(int(matrix[v][v]) for v in pocc_vals)
hasv_diag = sum(int(matrix[v][v]) for v in hasv_vals)

print(f"  ANNA diagonal sum: {anna_diag}")
print(f"  POCC diagonal sum: {pocc_diag}")
print(f"  HASV diagonal sum: {hasv_diag}")
print()

# Show diagonal values used per character
anna_diag_detail = [(c, char_to_num(c), int(matrix[char_to_num(c)][char_to_num(c)])) for c in ANNA_ISSUER]
print(f"  ANNA diagonal breakdown (first 20):")
for c, v, d in anna_diag_detail[:20]:
    print(f"    {c} -> matrix[{v},{v}] = {d}")
print(f"    ... (total 60 characters)")
print(f"  Sum = {anna_diag}")

results["diagonal_sum"] = {
    "ANNA": anna_diag,
    "POCC": pocc_diag,
    "HASV": hasv_diag,
    "diagonal_entries_used": {chr(65+i): int(matrix[i][i]) for i in range(26)}
}

# ============================================================================
# ANALYSIS 2: Character Sums
# ============================================================================
print("\n" + "=" * 80)
print("[2] CHARACTER SUM (A=0 and A=1 based)")
print("=" * 80)

anna_sum0 = sum(anna_vals)
anna_sum1 = sum(v + 1 for v in anna_vals)
pocc_sum0 = sum(pocc_vals)
pocc_sum1 = sum(v + 1 for v in pocc_vals)
hasv_sum0 = sum(hasv_vals)
hasv_sum1 = sum(v + 1 for v in hasv_vals)

print(f"  A=0 based:")
print(f"    ANNA: {anna_sum0}")
print(f"    POCC: {pocc_sum0}")
print(f"    HASV: {hasv_sum0}")
print()
print(f"  A=1 based:")
print(f"    ANNA: {anna_sum1}")
print(f"    POCC: {pocc_sum1}")
print(f"    HASV: {hasv_sum1}")

results["character_sums"] = {
    "A0_based": {"ANNA": anna_sum0, "POCC": pocc_sum0, "HASV": hasv_sum0},
    "A1_based": {"ANNA": anna_sum1, "POCC": pocc_sum1, "HASV": hasv_sum1}
}

# ============================================================================
# ANALYSIS 3: Diagonal Sum Comparison with POCC and HASV
# ============================================================================
print("\n" + "=" * 80)
print("[3] DIAGONAL SUM DIFFERENCES")
print("=" * 80)

anna_vs_pocc = anna_diag - pocc_diag
anna_vs_hasv = anna_diag - hasv_diag
pocc_vs_hasv = hasv_diag - pocc_diag

print(f"  ANNA - POCC = {anna_diag} - ({pocc_diag}) = {anna_vs_pocc}")
print(f"  ANNA - HASV = {anna_diag} - ({hasv_diag}) = {anna_vs_hasv}")
print(f"  HASV - POCC = {hasv_diag} - ({pocc_diag}) = {pocc_vs_hasv}  (known: 676)")
print()

# Check if differences relate to 676
print(f"  ANNA-POCC / 676 = {anna_vs_pocc / 676:.6f}")
print(f"  ANNA-HASV / 676 = {anna_vs_hasv / 676:.6f}")
print(f"  ANNA-POCC mod 676 = {anna_vs_pocc % 676}")
print(f"  ANNA-HASV mod 676 = {anna_vs_hasv % 676}")

results["diagonal_differences"] = {
    "ANNA_minus_POCC": anna_vs_pocc,
    "ANNA_minus_HASV": anna_vs_hasv,
    "HASV_minus_POCC": pocc_vs_hasv,
    "ANNA_minus_POCC_div_676": round(anna_vs_pocc / 676, 6),
    "ANNA_minus_HASV_div_676": round(anna_vs_hasv / 676, 6),
    "ANNA_minus_POCC_mod_676": anna_vs_pocc % 676,
    "ANNA_minus_HASV_mod_676": anna_vs_hasv % 676
}

# ============================================================================
# ANALYSIS 4: Diagonal Sum mod 26 = 17?
# ============================================================================
print("\n" + "=" * 80)
print("[4] DIAGONAL SUM mod 26 CHECK (POCC & HASV both = 17)")
print("=" * 80)

anna_mod26 = anna_diag % 26
pocc_mod26 = pocc_diag % 26
hasv_mod26 = hasv_diag % 26

print(f"  ANNA diagonal mod 26 = {anna_mod26}")
print(f"  POCC diagonal mod 26 = {pocc_mod26}")
print(f"  HASV diagonal mod 26 = {hasv_mod26}")
print()
match_mod26 = anna_mod26 == 17
print(f"  ANNA matches POCC/HASV (mod 26 = 17)? {'YES' if match_mod26 else 'NO'}")

results["mod_26_check"] = {
    "ANNA": anna_mod26,
    "POCC": pocc_mod26,
    "HASV": hasv_mod26,
    "target": 17,
    "ANNA_matches": match_mod26
}

# ============================================================================
# ANALYSIS 5: Diagonal Sum mod 676 = 121?
# ============================================================================
print("\n" + "=" * 80)
print("[5] DIAGONAL SUM mod 676 CHECK (POCC & HASV both = 121)")
print("=" * 80)

anna_mod676 = anna_diag % 676
pocc_mod676 = pocc_diag % 676
hasv_mod676 = hasv_diag % 676

print(f"  ANNA diagonal mod 676 = {anna_mod676}")
print(f"  POCC diagonal mod 676 = {pocc_mod676}")
print(f"  HASV diagonal mod 676 = {hasv_mod676}")
print()
match_mod676 = anna_mod676 == 121
print(f"  ANNA matches POCC/HASV (mod 676 = 121)? {'YES' if match_mod676 else 'NO'}")
print(f"  Note: 121 = 11^2, 676 = 26^2")

results["mod_676_check"] = {
    "ANNA": anna_mod676,
    "POCC": pocc_mod676,
    "HASV": hasv_mod676,
    "target": 121,
    "ANNA_matches": match_mod676,
    "note": "121 = 11^2, 676 = 26^2"
}

# ============================================================================
# ANALYSIS 6: Character Sum mod 23
# ============================================================================
print("\n" + "=" * 80)
print("[6] CHARACTER SUM mod 23 CHECK (POCC & HASV both = 14)")
print("=" * 80)

anna_charmod23 = anna_sum0 % 23
pocc_charmod23 = pocc_sum0 % 23
hasv_charmod23 = hasv_sum0 % 23

print(f"  ANNA sum(A=0) mod 23 = {anna_charmod23}")
print(f"  POCC sum(A=0) mod 23 = {pocc_charmod23}")
print(f"  HASV sum(A=0) mod 23 = {hasv_charmod23}")
print()
match_mod23 = anna_charmod23 == 14
print(f"  ANNA matches POCC/HASV (mod 23 = 14)? {'YES' if match_mod23 else 'NO'}")

results["mod_23_check"] = {
    "ANNA": anna_charmod23,
    "POCC": pocc_charmod23,
    "HASV": hasv_charmod23,
    "target": 14,
    "ANNA_matches": match_mod23
}

# ============================================================================
# ANALYSIS 7: Identical Positions
# ============================================================================
print("\n" + "=" * 80)
print("[7] IDENTICAL POSITION COUNT")
print("=" * 80)

anna_pocc_matches = [(i, ANNA_ISSUER[i]) for i in range(60) if ANNA_ISSUER[i] == POCC[i]]
anna_hasv_matches = [(i, ANNA_ISSUER[i]) for i in range(60) if ANNA_ISSUER[i] == HASV[i]]
pocc_hasv_matches = [(i, POCC[i]) for i in range(60) if POCC[i] == HASV[i]]

print(f"  ANNA vs POCC: {len(anna_pocc_matches)} identical positions")
if anna_pocc_matches:
    print(f"    Positions: {[(pos, char) for pos, char in anna_pocc_matches]}")
print()
print(f"  ANNA vs HASV: {len(anna_hasv_matches)} identical positions")
if anna_hasv_matches:
    print(f"    Positions: {[(pos, char) for pos, char in anna_hasv_matches]}")
print()
print(f"  POCC vs HASV: {len(pocc_hasv_matches)} identical positions (reference)")
if pocc_hasv_matches:
    print(f"    Positions: {[(pos, char) for pos, char in pocc_hasv_matches]}")

# Expected identical positions for random 60-char A-Z strings
expected_random = 60 / 26
print(f"\n  Expected identical positions for random A-Z addresses: {expected_random:.2f}")

# Three-way matches
triple_matches = [(i, ANNA_ISSUER[i]) for i in range(60)
                  if ANNA_ISSUER[i] == POCC[i] == HASV[i]]
print(f"\n  Three-way matches (ANNA=POCC=HASV): {len(triple_matches)}")
if triple_matches:
    print(f"    Positions: {triple_matches}")

results["identical_positions"] = {
    "ANNA_vs_POCC": {
        "count": len(anna_pocc_matches),
        "positions": [{"pos": pos, "char": char} for pos, char in anna_pocc_matches]
    },
    "ANNA_vs_HASV": {
        "count": len(anna_hasv_matches),
        "positions": [{"pos": pos, "char": char} for pos, char in anna_hasv_matches]
    },
    "POCC_vs_HASV": {
        "count": len(pocc_hasv_matches),
        "positions": [{"pos": pos, "char": char} for pos, char in pocc_hasv_matches]
    },
    "triple_matches": {
        "count": len(triple_matches),
        "positions": [{"pos": pos, "char": char} for pos, char in triple_matches]
    },
    "expected_random": round(expected_random, 2)
}

# ============================================================================
# ANALYSIS 8: Supply Number Analysis
# ============================================================================
print("\n" + "=" * 80)
print("[8] SUPPLY NUMBER ANALYSIS")
print("=" * 80)

max_supply = 900_000_000_000
circ_supply = 33_299_999_900
total_supply = 33_299_999_900

print(f"  Max Supply:         {max_supply:>20,}")
print(f"  Circulating Supply: {circ_supply:>20,}")
print(f"  Total Supply:       {total_supply:>20,}")
print()

# Factor analysis
print("  Max Supply factorization:")
n = max_supply
factors = {}
temp = n
for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
    while temp % p == 0:
        factors[p] = factors.get(p, 0) + 1
        temp //= p
if temp > 1:
    factors[temp] = 1
print(f"    {max_supply} = {' x '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(factors.items()))}")
print(f"    = 9 x 10^11")
print()

# Check for 676 encoding
print("  676 relationship checks:")
print(f"    900,000,000,000 / 676 = {max_supply / 676:,.6f}")
print(f"    900,000,000,000 mod 676 = {max_supply % 676}")
print(f"    33,299,999,900 / 676 = {circ_supply / 676:,.6f}")
print(f"    33,299,999,900 mod 676 = {circ_supply % 676}")
print()

# Check ratio
ratio = max_supply / circ_supply
print(f"  Max / Circulating = {ratio:.6f}")
print(f"  Circulating / Max = {circ_supply / max_supply:.10f}")
print(f"  Circulating as % of Max = {circ_supply / max_supply * 100:.6f}%")
print()

# Check for significant digit patterns
print("  Digit analysis:")
print(f"    900 billion -> 9 * 10^11")
print(f"    33.3 billion -> 333 * 10^8 - 100 (approx)")
print(f"    33,299,999,900 = 33,300,000,000 - 100")
print(f"    33,300,000,000 / 676 = {33_300_000_000 / 676:,.6f}")
print(f"    33,300,000,000 mod 676 = {33_300_000_000 % 676}")
print()

# Check key numbers
print("  Key number checks:")
print(f"    900 mod 676 = {900 % 676}")
print(f"    900 - 676 = {900 - 676} = 224")
print(f"    333 mod 26 = {333 % 26}")
print(f"    333 mod 676 = {333 % 676}")
print(f"    9 * 26^2 = {9 * 676} = {9 * 676}")
print(f"    Max supply = 9 * 10^11 = {9 * 10**11}")
print(f"    sqrt(900) = {math.sqrt(900)} = 30")
print(f"    26 * 30 = {26 * 30}")
print(f"    676 * 30 = {676 * 30}")
print()

# Check if circulating encodes something
print("  Circulating supply deeper analysis:")
print(f"    33,299,999,900 / 26 = {circ_supply / 26:,.6f}")
print(f"    33,299,999,900 mod 26 = {circ_supply % 26}")
print(f"    33,299,999,900 / 128 = {circ_supply / 128:,.6f}")
print(f"    33,299,999,900 mod 128 = {circ_supply % 128}")

# Percentage burned vs max
burned = max_supply - circ_supply
print(f"\n  Tokens not circulating: {burned:,}")
print(f"    {burned} / 676 = {burned / 676:,.6f}")
print(f"    {burned} mod 676 = {burned % 676}")

supply_analysis = {
    "max_supply": max_supply,
    "circulating_supply": circ_supply,
    "max_div_676": round(max_supply / 676, 6),
    "max_mod_676": max_supply % 676,
    "circ_div_676": round(circ_supply / 676, 6),
    "circ_mod_676": circ_supply % 676,
    "ratio_max_to_circ": round(ratio, 6),
    "circ_pct_of_max": round(circ_supply / max_supply * 100, 6),
    "key_observations": {
        "900_mod_676": 900 % 676,
        "900_minus_676": 224,
        "333_mod_26": 333 % 26,
        "9_times_676": 9 * 676,
        "sqrt_900": 30,
        "not_circulating": burned,
        "not_circulating_mod_676": burned % 676,
        "33300000000_mod_676": 33_300_000_000 % 676,
        "circ_mod_26": circ_supply % 26,
        "circ_mod_128": circ_supply % 128
    }
}
results["supply_analysis"] = supply_analysis

# ============================================================================
# ANALYSIS 9: 900 billion and 33.3 billion in terms of 676
# ============================================================================
print("\n" + "=" * 80)
print("[9] SUPPLY IN TERMS OF 676")
print("=" * 80)

print(f"  900,000,000,000 = {max_supply // 676} * 676 + {max_supply % 676}")
print(f"  33,299,999,900  = {circ_supply // 676} * 676 + {circ_supply % 676}")
print()
print(f"  900,000,000,000 / 676^2 = {max_supply / (676**2):,.6f}")
print(f"  900,000,000,000 / 676^3 = {max_supply / (676**3):,.6f}")
print(f"  33,299,999,900 / 676^2 = {circ_supply / (676**2):,.6f}")
print(f"  33,299,999,900 / 676^3 = {circ_supply / (676**3):,.6f}")
print()

# Check if ratio relates to 676
print(f"  Ratio: {max_supply}/{circ_supply} = {ratio:.10f}")
print(f"  Ratio * 676 = {ratio * 676:.6f}")
print(f"  Ratio * 26 = {ratio * 26:.6f}")
print(f"  1/ratio * 676 = {676 / ratio:.6f}")
print()

# Check 26-related decompositions
print(f"  26-based decomposition:")
print(f"    900 billion = {max_supply // (26**6)} * 26^6 + remainder")
print(f"    26^6 = {26**6}")
print(f"    26^7 = {26**7}")
print(f"    900 billion / 26^6 = {max_supply / (26**6):,.6f}")
print(f"    900 billion / 26^7 = {max_supply / (26**7):,.6f}")

results["supply_676_analysis"] = {
    "max_supply_676_quotient": max_supply // 676,
    "max_supply_676_remainder": max_supply % 676,
    "circ_supply_676_quotient": circ_supply // 676,
    "circ_supply_676_remainder": circ_supply % 676,
    "max_div_676_squared": round(max_supply / (676**2), 6),
    "circ_div_676_squared": round(circ_supply / (676**2), 6),
    "ratio_times_676": round(ratio * 676, 6),
    "ratio_times_26": round(ratio * 26, 6)
}

# ============================================================================
# ANALYSIS 10: Monte Carlo Simulation
# ============================================================================
print("\n" + "=" * 80)
print("[10] MONTE CARLO SIMULATION (1000 random addresses)")
print("=" * 80)

N_SIMULATIONS = 1000

def generate_random_address():
    """Generate a random 60-character A-Z string (Qubic address format)."""
    return ''.join(chr(random.randint(0, 25) + ord('A')) for _ in range(60))

def compute_diagonal_sum(address):
    """Compute diagonal sum for an address."""
    return sum(int(matrix[char_to_num(c)][char_to_num(c)]) for c in address)

def compute_char_sum(address, base=0):
    """Compute character sum (A=base)."""
    return sum(char_to_num(c) + base for c in address)

def count_matches(addr1, addr2):
    """Count identical positions between two addresses."""
    return sum(1 for i in range(min(len(addr1), len(addr2))) if addr1[i] == addr2[i])

print(f"  Generating {N_SIMULATIONS} random 60-char addresses...")

random_diag_sums = []
random_char_sums_0 = []
random_char_sums_1 = []
random_mod26_matches_17 = 0
random_mod676_matches_121 = 0
random_mod23_matches_14 = 0
random_both_mod26_and_mod676 = 0
random_all_three_mods = 0
random_pocc_pos_matches = []
random_hasv_pos_matches = []

for i in range(N_SIMULATIONS):
    addr = generate_random_address()

    d_sum = compute_diagonal_sum(addr)
    c_sum_0 = compute_char_sum(addr, base=0)
    c_sum_1 = compute_char_sum(addr, base=1)

    random_diag_sums.append(d_sum)
    random_char_sums_0.append(c_sum_0)
    random_char_sums_1.append(c_sum_1)

    m26 = d_sum % 26
    m676 = d_sum % 676
    m23 = c_sum_0 % 23

    if m26 == 17:
        random_mod26_matches_17 += 1
    if m676 == 121:
        random_mod676_matches_121 += 1
    if m23 == 14:
        random_mod23_matches_14 += 1
    if m26 == 17 and m676 == 121:
        random_both_mod26_and_mod676 += 1
    if m26 == 17 and m676 == 121 and m23 == 14:
        random_all_three_mods += 1

    random_pocc_pos_matches.append(count_matches(addr, POCC))
    random_hasv_pos_matches.append(count_matches(addr, HASV))

random_diag_sums = np.array(random_diag_sums)
random_char_sums_0 = np.array(random_char_sums_0)
random_pocc_pos_matches = np.array(random_pocc_pos_matches)
random_hasv_pos_matches = np.array(random_hasv_pos_matches)

print(f"\n  Diagonal Sum Distribution:")
print(f"    Mean:   {np.mean(random_diag_sums):.2f}")
print(f"    Std:    {np.std(random_diag_sums):.2f}")
print(f"    Min:    {np.min(random_diag_sums)}")
print(f"    Max:    {np.max(random_diag_sums)}")
print(f"    Median: {np.median(random_diag_sums):.1f}")
print()

# Z-scores
diag_mean = np.mean(random_diag_sums)
diag_std = np.std(random_diag_sums)
anna_z = (anna_diag - diag_mean) / diag_std if diag_std > 0 else 0
pocc_z = (pocc_diag - diag_mean) / diag_std if diag_std > 0 else 0
hasv_z = (hasv_diag - diag_mean) / diag_std if diag_std > 0 else 0

print(f"  Z-scores (diagonal sum):")
print(f"    ANNA: {anna_z:.4f}  (diagonal sum = {anna_diag})")
print(f"    POCC: {pocc_z:.4f}  (diagonal sum = {pocc_diag})")
print(f"    HASV: {hasv_z:.4f}  (diagonal sum = {hasv_diag})")
print()

# Character sum distribution
char_mean = np.mean(random_char_sums_0)
char_std = np.std(random_char_sums_0)
anna_char_z = (anna_sum0 - char_mean) / char_std if char_std > 0 else 0
pocc_char_z = (pocc_sum0 - char_mean) / char_std if char_std > 0 else 0
hasv_char_z = (hasv_sum0 - char_mean) / char_std if char_std > 0 else 0

print(f"  Character Sum Distribution (A=0):")
print(f"    Mean:   {char_mean:.2f}")
print(f"    Std:    {char_std:.2f}")
print(f"  Z-scores (char sum):")
print(f"    ANNA: {anna_char_z:.4f}  (char sum = {anna_sum0})")
print(f"    POCC: {pocc_char_z:.4f}  (char sum = {pocc_sum0})")
print(f"    HASV: {hasv_char_z:.4f}  (char sum = {hasv_sum0})")
print()

# Modular property frequencies
print(f"  Modular Property Frequencies (out of {N_SIMULATIONS}):")
print(f"    diag mod 26 = 17:  {random_mod26_matches_17} ({random_mod26_matches_17/N_SIMULATIONS*100:.1f}%)")
print(f"      Expected: {N_SIMULATIONS/26:.1f} ({100/26:.1f}%)")
print(f"    diag mod 676 = 121: {random_mod676_matches_121} ({random_mod676_matches_121/N_SIMULATIONS*100:.1f}%)")
print(f"      Expected: {N_SIMULATIONS/676:.2f} ({100/676:.2f}%)")
print(f"    char_sum mod 23 = 14: {random_mod23_matches_14} ({random_mod23_matches_14/N_SIMULATIONS*100:.1f}%)")
print(f"      Expected: {N_SIMULATIONS/23:.1f} ({100/23:.1f}%)")
print()
print(f"  Joint probabilities:")
print(f"    mod 26=17 AND mod 676=121: {random_both_mod26_and_mod676} ({random_both_mod26_and_mod676/N_SIMULATIONS*100:.2f}%)")
print(f"      Note: mod 676=121 implies mod 26 = 121 mod 26 = {121 % 26}")
if 121 % 26 == 17:
    print(f"      Since 121 mod 26 = 17, mod 676=121 is a STRICTER condition that implies mod 26=17")
print(f"    ALL THREE (mod26=17, mod676=121, mod23=14): {random_all_three_mods} ({random_all_three_mods/N_SIMULATIONS*100:.2f}%)")
expected_joint = N_SIMULATIONS / (676 * 23)
print(f"      Expected if independent: {expected_joint:.4f} ({100 / (676 * 23):.4f}%)")
print()

# Position match statistics
print(f"  Position Match Statistics:")
print(f"    ANNA vs POCC: {len(anna_pocc_matches)} identical positions")
print(f"    Random vs POCC: mean={np.mean(random_pocc_pos_matches):.2f}, "
      f"std={np.std(random_pocc_pos_matches):.2f}, "
      f"max={np.max(random_pocc_pos_matches)}")
pocc_match_z = (len(anna_pocc_matches) - np.mean(random_pocc_pos_matches)) / np.std(random_pocc_pos_matches) if np.std(random_pocc_pos_matches) > 0 else 0
print(f"    ANNA vs POCC z-score: {pocc_match_z:.4f}")
print()
print(f"    ANNA vs HASV: {len(anna_hasv_matches)} identical positions")
print(f"    Random vs HASV: mean={np.mean(random_hasv_pos_matches):.2f}, "
      f"std={np.std(random_hasv_pos_matches):.2f}, "
      f"max={np.max(random_hasv_pos_matches)}")
hasv_match_z = (len(anna_hasv_matches) - np.mean(random_hasv_pos_matches)) / np.std(random_hasv_pos_matches) if np.std(random_hasv_pos_matches) > 0 else 0
print(f"    ANNA vs HASV z-score: {hasv_match_z:.4f}")
print()

# How many random addresses also have all three mod properties?
anna_has_mod26 = anna_mod26 == 17
anna_has_mod676 = anna_mod676 == 121
anna_has_mod23 = anna_charmod23 == 14

property_count = sum([anna_has_mod26, anna_has_mod676, anna_has_mod23])
print(f"  ANNA address properties matched: {property_count}/3")
print(f"    mod 26 = 17:  {'YES' if anna_has_mod26 else 'NO'}")
print(f"    mod 676 = 121: {'YES' if anna_has_mod676 else 'NO'}")
print(f"    char mod 23 = 14: {'YES' if anna_has_mod23 else 'NO'}")

# Compute percentile of ANNA diagonal sum
anna_percentile = np.sum(random_diag_sums <= anna_diag) / N_SIMULATIONS * 100
print(f"\n  ANNA diagonal sum percentile: {anna_percentile:.1f}%")

results["monte_carlo"] = {
    "n_simulations": N_SIMULATIONS,
    "diagonal_sum_distribution": {
        "mean": round(float(np.mean(random_diag_sums)), 2),
        "std": round(float(np.std(random_diag_sums)), 2),
        "min": int(np.min(random_diag_sums)),
        "max": int(np.max(random_diag_sums)),
        "median": round(float(np.median(random_diag_sums)), 1)
    },
    "z_scores_diagonal": {
        "ANNA": round(anna_z, 4),
        "POCC": round(pocc_z, 4),
        "HASV": round(hasv_z, 4)
    },
    "char_sum_distribution": {
        "mean": round(float(char_mean), 2),
        "std": round(float(char_std), 2)
    },
    "z_scores_char_sum": {
        "ANNA": round(anna_char_z, 4),
        "POCC": round(pocc_char_z, 4),
        "HASV": round(hasv_char_z, 4)
    },
    "modular_frequencies": {
        "mod26_eq_17": {
            "count": random_mod26_matches_17,
            "pct": round(random_mod26_matches_17 / N_SIMULATIONS * 100, 2),
            "expected_pct": round(100 / 26, 2)
        },
        "mod676_eq_121": {
            "count": random_mod676_matches_121,
            "pct": round(random_mod676_matches_121 / N_SIMULATIONS * 100, 2),
            "expected_pct": round(100 / 676, 2)
        },
        "charsum_mod23_eq_14": {
            "count": random_mod23_matches_14,
            "pct": round(random_mod23_matches_14 / N_SIMULATIONS * 100, 2),
            "expected_pct": round(100 / 23, 2)
        },
        "all_three": {
            "count": random_all_three_mods,
            "pct": round(random_all_three_mods / N_SIMULATIONS * 100, 4),
            "expected_pct": round(100 / (676 * 23), 4)
        }
    },
    "position_matches": {
        "ANNA_vs_POCC": {
            "actual": len(anna_pocc_matches),
            "random_mean": round(float(np.mean(random_pocc_pos_matches)), 2),
            "random_std": round(float(np.std(random_pocc_pos_matches)), 2),
            "z_score": round(pocc_match_z, 4)
        },
        "ANNA_vs_HASV": {
            "actual": len(anna_hasv_matches),
            "random_mean": round(float(np.mean(random_hasv_pos_matches)), 2),
            "random_std": round(float(np.std(random_hasv_pos_matches)), 2),
            "z_score": round(hasv_match_z, 4)
        }
    },
    "anna_diagonal_percentile": round(anna_percentile, 1),
    "anna_properties_matched": {
        "mod26_eq_17": anna_has_mod26,
        "mod676_eq_121": anna_has_mod676,
        "charsum_mod23_eq_14": anna_has_mod23,
        "total_matched": property_count
    }
}

# ============================================================================
# ADDITIONAL: Cross-matrix lookups (ANNA address pair coordinates)
# ============================================================================
print("\n" + "=" * 80)
print("[BONUS] ANNA ADDRESS - MATRIX PAIR LOOKUPS")
print("=" * 80)

# Map consecutive character pairs to matrix coordinates
anna_pair_values = []
for i in range(0, 58, 2):
    r = char_to_num(ANNA_ISSUER[i])
    c = char_to_num(ANNA_ISSUER[i + 1])
    val = int(matrix[r][c])
    anna_pair_values.append(val)
    if i < 20:
        print(f"  [{i:2d}] {ANNA_ISSUER[i]}{ANNA_ISSUER[i+1]} -> matrix[{r},{c}] = {val}")

print(f"  ...")
print(f"  Pair sum: {sum(anna_pair_values)}")
print(f"  Pair sum mod 676: {sum(anna_pair_values) % 676}")
print(f"  Pair sum mod 26: {sum(anna_pair_values) % 26}")

results["pair_analysis"] = {
    "pair_sum": sum(anna_pair_values),
    "pair_sum_mod_676": sum(anna_pair_values) % 676,
    "pair_sum_mod_26": sum(anna_pair_values) % 26,
    "pairs": [{"chars": ANNA_ISSUER[i:i+2], "row": char_to_num(ANNA_ISSUER[i]),
               "col": char_to_num(ANNA_ISSUER[i+1]), "value": anna_pair_values[i//2]}
              for i in range(0, 58, 2)]
}

# ============================================================================
# ADDITIONAL: ANNA prefix analysis
# ============================================================================
print("\n" + "=" * 80)
print("[BONUS] PREFIX ANALYSIS")
print("=" * 80)

# The address starts with HIFU
anna_prefix = ANNA_ISSUER[:4]
anna_prefix_sum = sum(char_to_num(c) for c in anna_prefix)
print(f"  ANNA issuer prefix: {anna_prefix}")
print(f"  Prefix sum (A=0): H({char_to_num('H')}) + I({char_to_num('I')}) + F({char_to_num('F')}) + U({char_to_num('U')}) = {anna_prefix_sum}")
print(f"  POCC prefix sum: P({char_to_num('P')}) + O({char_to_num('O')}) + C({char_to_num('C')}) + C({char_to_num('C')}) = {sum(char_to_num(c) for c in 'POCC')}")
print(f"  HASV prefix sum: H({char_to_num('H')}) + A({char_to_num('A')}) + S({char_to_num('S')}) + V({char_to_num('V')}) = {sum(char_to_num(c) for c in 'HASV')}")
print()
print(f"  matrix[6, {anna_prefix_sum}] = {int(matrix[6][anna_prefix_sum])}")

results["prefix_analysis"] = {
    "ANNA_issuer_prefix": anna_prefix,
    "ANNA_prefix_sum": anna_prefix_sum,
    "POCC_prefix_sum": sum(char_to_num(c) for c in "POCC"),
    "HASV_prefix_sum": sum(char_to_num(c) for c in "HASV"),
    "matrix_6_anna_prefix": int(matrix[6][anna_prefix_sum])
}

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("    SUMMARY OF FINDINGS")
print("=" * 80)
print()
print(f"  ANNA issuer diagonal sum: {anna_diag}")
print(f"  POCC diagonal sum:        {pocc_diag}")
print(f"  HASV diagonal sum:        {hasv_diag}")
print(f"  Diff HASV-POCC:           {pocc_vs_hasv} (= 676 = 26^2)")
print(f"  Diff ANNA-POCC:           {anna_vs_pocc}")
print(f"  Diff ANNA-HASV:           {anna_vs_hasv}")
print()
print(f"  mod 26 = 17:   ANNA={'YES' if anna_has_mod26 else 'NO'}  POCC=YES  HASV=YES")
print(f"  mod 676 = 121: ANNA={'YES' if anna_has_mod676 else 'NO'}  POCC=YES  HASV=YES")
print(f"  char mod 23=14: ANNA={'YES' if anna_has_mod23 else 'NO'}  POCC=YES  HASV=YES")
print()
print(f"  Position matches: ANNA-POCC={len(anna_pocc_matches)}, ANNA-HASV={len(anna_hasv_matches)}, POCC-HASV={len(pocc_hasv_matches)}")
print(f"  ANNA diagonal z-score: {anna_z:.4f}")
print(f"  ANNA char sum z-score: {anna_char_z:.4f}")
print()

# Significance assessment
sig_flags = []
if anna_has_mod26:
    sig_flags.append("mod 26 = 17 (shared with POCC/HASV)")
if anna_has_mod676:
    sig_flags.append("mod 676 = 121 (shared with POCC/HASV)")
if anna_has_mod23:
    sig_flags.append("char sum mod 23 = 14 (shared with POCC/HASV)")
if abs(anna_z) > 2:
    sig_flags.append(f"diagonal sum is {abs(anna_z):.1f} sigma from random mean")
if len(anna_pocc_matches) > 5 or len(anna_hasv_matches) > 5:
    sig_flags.append(f"high position match count")

if sig_flags:
    print("  SIGNIFICANT FINDINGS:")
    for f in sig_flags:
        print(f"    - {f}")
else:
    print("  No statistically significant anomalies detected.")
    print("  The ANNA issuer address does not share the characteristic")
    print("  modular properties of POCC and HASV.")

results["summary"] = {
    "significant_findings": sig_flags,
    "properties_shared_with_pocc_hasv": property_count,
    "anna_diagonal_z_score": round(anna_z, 4),
    "anna_charsum_z_score": round(anna_char_z, 4),
    "conclusion": "SHARES_PROPERTIES" if property_count >= 2 else "INDEPENDENT" if property_count == 0 else "PARTIAL_MATCH"
}

# Save results
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n  Results saved to: {output_path}")
print("=" * 80)
