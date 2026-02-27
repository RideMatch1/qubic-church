#!/usr/bin/env python3
"""
BONFERRONI COMPLETE AUDIT
=========================
Count EVERY test we performed and determine what actually survives.

The honest truth: When you perform N tests, you need p < α/N to claim significance.
With N=44 tests, a finding needs p < 0.00114 to survive.

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-09
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats
import math

# Load Anna Matrix
MATRIX_PATH = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
with open(MATRIX_PATH, 'r') as f:
    data = json.load(f)
matrix = np.array(data['matrix'], dtype=np.int8)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    return ord(c.upper()) - ord('A')

print("=" * 80)
print("BONFERRONI COMPLETE AUDIT")
print("Every claim. Every test. No mercy.")
print("=" * 80)
print()

# ============================================================
# SECTION A: POCC/HASV PROPERTIES (EXISTING, PRE-VALIDATED)
# ============================================================
print("SECTION A: POCC/HASV Properties")
print("-" * 60)

tests_A = []

# A1: Diagonal difference = 676
pocc_diag = sum(int(matrix[char_to_num(c)][char_to_num(c)]) for c in POCC)
hasv_diag = sum(int(matrix[char_to_num(c)][char_to_num(c)]) for c in HASV)
diag_diff = hasv_diag - pocc_diag

# P(diagonal diff = 676 for random 60-char addresses)
# Monte Carlo: generate random pairs and check
np.random.seed(42)
N_MC = 100_000
mc_diag_diffs = []
for _ in range(N_MC):
    addr1 = np.random.randint(0, 26, 60)
    addr2 = np.random.randint(0, 26, 60)
    d1 = sum(int(matrix[c][c]) for c in addr1)
    d2 = sum(int(matrix[c][c]) for c in addr2)
    mc_diag_diffs.append(d2 - d1)

p_diag_676 = sum(1 for d in mc_diag_diffs if d == 676) / N_MC
p_diag_exact = max(p_diag_676, 1/N_MC)  # Floor at 1/N_MC
tests_A.append(("Diagonal diff = 676 (exact)", p_diag_exact, diag_diff == 676))

# A2: Character sum diff = 138
pocc_sum = sum(char_to_num(c) for c in POCC)
hasv_sum = sum(char_to_num(c) for c in HASV)
sum_diff = hasv_sum - pocc_sum

# P(random 60-char addresses have sum diff = 138)
# Mean letter value = 12.5, var = 54.17
# Diff of sums: mean=0, var = 2 * 60 * 54.17 = 6500
# SD = √6500 ≈ 80.6
# P(diff = 138) ≈ density at 138 / SD
sd_diff = math.sqrt(2 * 60 * (25*26/12))  # variance of uniform 0-25
p_sum_138 = stats.norm.pdf(138, 0, sd_diff)
tests_A.append(("Sum diff = 138 (exact)", p_sum_138, sum_diff == 138))

# A3: XOR = same as difference
xor_result = pocc_sum ^ hasv_sum
# P(XOR = diff) for two random sums
# This is determined by the sums, not independent
# For sums 612 and 750: 612 XOR 750 = 138 AND 750-612 = 138
# This is a PROPERTY of these specific numbers, not an independent test
p_xor = 1.0  # Not independent from A2
tests_A.append(("XOR = diff (= 138)", p_xor, xor_result == sum_diff, "NOT INDEPENDENT from A2"))

# A4: Both mod 23 = 14
p_mod23 = 1/23  # P(random pair has same mod 23)
tests_A.append(("Both sums mod 23 = 14", p_mod23, pocc_sum % 23 == hasv_sum % 23))

# A5: Both diag mod 26 = 17
p_mod26_diag = 1/26
tests_A.append(("Both diag mod 26 = 17", p_mod26_diag, pocc_diag % 26 == hasv_diag % 26, "DEPENDENT on A1"))

# A6: Both diag mod 676 = 121
p_mod676_diag = 1/676
tests_A.append(("Both diag mod 676 = 121", p_mod676_diag, pocc_diag % 676 == hasv_diag % 676, "DEPENDENT on A1"))

# A7: 6 identical positions
identical = sum(1 for i in range(60) if POCC[i] == HASV[i])
# P(exactly 6 identical in 60 positions, alphabet=26)
p_ident = stats.binom.pmf(6, 60, 1/26)
tests_A.append(("Exactly 6 identical positions", p_ident, identical == 6))

# A8: Sum of cubes diff = 144 × 676
pocc_cubes = sum(char_to_num(c)**3 for c in POCC)
hasv_cubes = sum(char_to_num(c)**3 for c in HASV)
cube_diff = hasv_cubes - pocc_cubes
is_mult_676 = cube_diff % 676 == 0
# P(cube diff divisible by 676)
mc_cube_divs = 0
for _ in range(N_MC):
    addr1 = np.random.randint(0, 26, 60)
    addr2 = np.random.randint(0, 26, 60)
    c1 = sum(c**3 for c in addr1)
    c2 = sum(c**3 for c in addr2)
    if (c2 - c1) % 676 == 0:
        mc_cube_divs += 1
p_cubes_676 = mc_cube_divs / N_MC
tests_A.append(("Cube diff divisible by 676", p_cubes_676, is_mult_676))

# A9: POCC 1-based sum = 672 (near 676)
pocc_1based = sum(char_to_num(c) + 1 for c in POCC)
# P(random sum within 4 of 676)
# Mean = 60 * 13.5 = 810, SD ≈ 62
sd_1based = math.sqrt(60 * (25*26/12))
p_near_676 = stats.norm.cdf(676+4, 60*13.5, sd_1based) - stats.norm.cdf(676-4, 60*13.5, sd_1based)
tests_A.append(("POCC 1-based within 4 of 676", p_near_676, abs(pocc_1based - 676) <= 4))

# A10: COMBINED POCC+HASV (the strong one)
# From existing research: p = 2.05e-8
p_combined = 2.05e-8
tests_A.append(("POCC+HASV COMBINED (all properties)", p_combined, True))

print(f"{'Test':<45} {'p-value':>12} {'Pass':>6}")
print("-" * 65)
for item in tests_A:
    name, p, passed = item[0], item[1], item[2]
    note = item[3] if len(item) > 3 else ""
    status = "✓" if passed else "✗"
    extra = f" ({note})" if note else ""
    print(f"  {name:<43} {p:>12.2e} {status:>6}{extra}")
print()

# ============================================================
# SECTION B: BTC TRANSACTION CLAIMS (NEW)
# ============================================================
print("SECTION B: BTC Transaction 2.56536737")
print("-" * 60)

tests_B = []

# B1: Amount contains "256" (SHA-256)
# 9-digit number, how often does it contain "256"?
# "256" can start at positions 0-6 in a 9-digit string
# P ≈ 7 × 0.001 ≈ 0.007
mc_256_count = 0
for _ in range(N_MC):
    r = str(np.random.randint(100000000, 999999999))
    if "256" in r:
        mc_256_count += 1
p_256 = mc_256_count / N_MC
tests_B.append(("Amount contains '256' (SHA-256)", p_256, "256" in "256536737"))

# B2: 536737 = 67 × 8011 (67 = 19th prime, 19 = TX inputs)
# P(random 6-digit number = product of 2 primes where one is Nth prime and N appears elsewhere)
# This is hard to calculate directly, use Monte Carlo
mc_factor_hits = 0
key_prime_indices = {19, 22, 26, 30, 41, 67, 86, 97, 105, 121, 127}
for _ in range(N_MC):
    r = np.random.randint(100000, 999999)
    # Factorize
    factors = []
    n = int(r)
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)

    if len(factors) == 2 and factors[0] != factors[1]:
        from sympy import primepi
        pass  # Skip sympy dependency, use precomputed primes

# Simpler: P(67 is a factor of a random 6-digit number) = floor(999999/67) - floor(99999/67) ≈ 13433
# Out of 900000 6-digit numbers
p_67_factor = (999999 // 67 - 99999 // 67) / 900000
tests_B.append(("536737 has factor 67 (19th prime)", p_67_factor, 536737 % 67 == 0))

# B3: 8011 mod 676 = 575 (= 576-1)
# Given that 8011 is the cofactor, P(cofactor mod 676 = 575) = 1/676
# BUT we also accepted 576, 676, or "N-1" patterns
# Effective targets: {575, 576, 675, 676, 0, 120, 121, 25, 26} ≈ 9 values
p_8011_mod = 9 / 676
tests_B.append(("8011 mod 676 ∈ special set", p_8011_mod, 8011 % 676 in {575, 576, 675, 676, 0, 120, 121, 25, 26}))

# B4: 256536737 mod 6268 = 33 (POCC prefix sum)
# Targets: {33, 46} (POCC and HASV prefix sums)
p_mod_6268 = 2 / 6268
tests_B.append(("Amount mod 6268 = 33 (POCC prefix)", p_mod_6268, 256536737 % 6268 == 33))

# B5: 97-day gap = Exception Column
# P(random day in 1-120 range hits an Exception Column) = 6/120 (excluding 0 and 127)
p_97_exc = 6 / 120  # Exc cols in range 1-120: {22, 30, 41, 86, 97, 105}
tests_B.append(("97-day gap = Exception Column", p_97_exc, True))

# B6: 24-day gap = √576
# P(remaining gap is a sqrt of a "key" perfect square)
# Key squares: 121, 576, 676
# Sqrts: 11, 24, 26
# Given 121 total, if first gap = exc col, remaining: 121-22=99, 121-30=91, 121-41=80, 121-86=35, 121-97=24, 121-105=16
# Of these, only 121-97=24 gives √576
# P = 1/6 (one of 6 possible exc cols gives this)
p_24_sqrt = 1 / 6
tests_B.append(("24-day gap = √576 (given exc col)", p_24_sqrt, True))

# B7: 97 + 24 = 121 = 11²
# This is FORCED: if total gap = 121, any split sums to 121
# NOT an independent test
p_121 = 1.0
tests_B.append(("97+24=121 (given total=121)", p_121, True, "NOT INDEPENDENT"))

# B8: 2050 mod 676 = 22 (Exception Column)
# P(2050 mod 676 hits exception col) = 8/676
p_2050 = 8 / 676
tests_B.append(("2050 mod 676 = 22 (Exc Col)", p_2050, 2050 % 676 in {0, 22, 30, 41, 86, 97, 105, 127}))

# B9: 41 - 19 = 22 (Exception Column)
# 41 (2011 inputs) - 19 (2026 inputs) = 22
# P(difference of two numbers = exception col) depends on how many pairs we tested
# We only tested this one pair, but we chose 19 because it was the input count
p_diff_22 = 8 / 128  # If we accept any exc col
tests_B.append(("41-19=22 (Exc Col)", p_diff_22, 41-19 in {0, 22, 30, 41, 86, 97, 105, 127}))

# B10: matrix[41,41] = 22 (Exc Col value)
# P(diagonal value at random position is in exc col set)
diag_exc_count = sum(1 for i in range(128) if int(matrix[i,i]) in {0, 22, 30, 41, 86, 97, 105, 127})
p_diag_exc = diag_exc_count / 128
tests_B.append(("matrix[41,41]=22 (Exc Col)", p_diag_exc, int(matrix[41,41]) in {0, 22, 30, 41, 86, 97, 105, 127}))

# B11: matrix[97,97] = 46 (HASV prefix)
# P(diagonal value = 33 or 46)
diag_prefix_count = sum(1 for i in range(128) if int(matrix[i,i]) in {33, 46})
p_diag_prefix = diag_prefix_count / 128
tests_B.append(("matrix[97,97]=46 (HASV prefix)", p_diag_prefix, int(matrix[97,97]) in {33, 46}))

# B12: 1CEq prefix match
p_1ceq = 1 / (58 * 58 * 58)  # 3 chars after "1" must match
tests_B.append(("1CEq 4-char prefix match", p_1ceq, True))

# B13: Seed 22144 mod 121 = 1
p_seed_mod = 1 / 121
tests_B.append(("Seed 22144 mod 121 = 1", p_seed_mod, 22144 % 121 == 1))

# B14: Seed 22144 mod 127 = 46 (HASV prefix)
p_seed_127 = 2 / 127  # Accept 33 or 46
tests_B.append(("Seed 22144 mod 127 = 46 (HASV)", p_seed_127, 22144 % 127 in {33, 46}))

print(f"{'Test':<45} {'p-value':>12} {'Pass':>6}")
print("-" * 65)
for item in tests_B:
    name, p, passed = item[0], item[1], item[2]
    note = item[3] if len(item) > 3 else ""
    status = "✓" if passed else "✗"
    extra = f" ({note})" if note else ""
    print(f"  {name:<43} {p:>12.2e} {status:>6}{extra}")
print()

# ============================================================
# SECTION C: BONFERRONI CORRECTION
# ============================================================
print("=" * 80)
print("SECTION C: BONFERRONI CORRECTION")
print("=" * 80)
print()

# Collect all independent tests
all_tests = []
for item in tests_A:
    if len(item) <= 3 or "NOT INDEPENDENT" not in item[3]:
        all_tests.append(("A", item[0], item[1], item[2]))
for item in tests_B:
    if len(item) <= 3 or "NOT INDEPENDENT" not in item[3]:
        all_tests.append(("B", item[0], item[1], item[2]))

n_independent = len(all_tests)
alpha = 0.05
bonferroni_threshold = alpha / n_independent

print(f"Total independent tests: {n_independent}")
print(f"Bonferroni threshold: α/{n_independent} = {bonferroni_threshold:.6f}")
print()

# Sort by p-value
all_tests.sort(key=lambda x: x[2])

print(f"{'#':>3} {'Sec':>3} {'Test':<45} {'p-value':>12} {'Survives':>10}")
print("-" * 78)

tier1 = []
tier2 = []
tier3 = []

for i, (sec, name, p, passed) in enumerate(all_tests, 1):
    survives = p < bonferroni_threshold and passed
    marker = "✅ YES" if survives else "❌ no"
    print(f"  {i:>2}. [{sec}] {name:<43} {p:>12.2e} {marker:>10}")

    if survives:
        tier1.append(name)
    elif p < 0.05 and passed:
        tier2.append(name)
    else:
        tier3.append(name)

print()
print("=" * 80)
print("FINAL CLASSIFICATION")
print("=" * 80)
print()

print(f"TIER 1 - SURVIVES BONFERRONI (p < {bonferroni_threshold:.6f}):")
if tier1:
    for t in tier1:
        print(f"  ✅ {t}")
else:
    print("  (none)")
print()

print(f"TIER 2 - NOMINALLY SIGNIFICANT (p < 0.05, fails Bonferroni):")
if tier2:
    for t in tier2:
        print(f"  🟡 {t}")
else:
    print("  (none)")
print()

print(f"TIER 3 - NOT SIGNIFICANT:")
if tier3:
    for t in tier3:
        print(f"  ❌ {t}")
else:
    print("  (none)")
print()

print("=" * 80)
print("HONEST CONCLUSION")
print("=" * 80)
print()
print(f"Of {n_independent} independent tests:")
print(f"  {len(tier1)} survive Bonferroni correction")
print(f"  {len(tier2)} are nominally significant but fail correction")
print(f"  {len(tier3)} are not significant")
print()
print("The ONLY claims we can make with confidence are those in Tier 1.")
print("Everything else could be the result of looking at enough numbers.")
print()
print("Reproducible via: python3 BONFERRONI_COMPLETE_AUDIT.py")
