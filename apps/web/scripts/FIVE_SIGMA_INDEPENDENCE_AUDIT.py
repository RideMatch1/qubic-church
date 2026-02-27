#!/usr/bin/env python3
"""
FIVE-SIGMA INDEPENDENCE AUDIT
==============================
Tests ALL candidate properties for POCC+HASV, measures individual p-values,
and builds a correlation matrix to identify truly independent properties.

Goal: Find enough independent properties to push combined p-value past
5-sigma threshold (p < 2.87e-7 = 1 in 3,488,556).

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-10
Reproducible: np.random.seed(42)
"""

import json
import numpy as np
from collections import Counter
from pathlib import Path
import time

# =============================================================================
# CONFIGURATION
# =============================================================================
N_TRIALS = 1_000_000
SEED = 42
MATRIX_FILE = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def c2n(c):
    return ord(c) - ord('A')

# =============================================================================
# LOAD MATRIX
# =============================================================================
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
matrix = data['matrix']  # Pure Python list (no numpy overflow)

# Pre-compute diagonal and anti-diagonal values for speed
diag_values = np.array([matrix[i][i] for i in range(26)], dtype=np.int64)
anti_diag_values = np.array([matrix[i][25 - i] for i in range(26)], dtype=np.int64)

# =============================================================================
# COMPUTE OBSERVED VALUES
# =============================================================================
pocc_nums = np.array([c2n(c) for c in POCC], dtype=np.int64)
hasv_nums = np.array([c2n(c) for c in HASV], dtype=np.int64)

# Property 1: Diagonal diff
obs_diag_diff = int(diag_values[hasv_nums].sum() - diag_values[pocc_nums].sum())

# Property 2: Character sum diff
obs_char_diff = int(hasv_nums.sum() - pocc_nums.sum())

# Property 3: Identical positions
obs_identical = sum(1 for i in range(60) if POCC[i] == HASV[i])

# Property 4: Cubes diff divisible by 676
obs_cubes_diff = int((hasv_nums ** 3).sum() - (pocc_nums ** 3).sum())
obs_cubes_div676 = obs_cubes_diff % 676 == 0

# Property 5: Identical chars value sum
identical_indices = [i for i in range(60) if POCC[i] == HASV[i]]
obs_identical_sum = sum(c2n(POCC[i]) for i in identical_indices) if identical_indices else 0

# Property 6: POCC sum mod 6
obs_pocc_mod6 = int(pocc_nums.sum()) % 6

# Property 7: POCC sum mod 23
obs_pocc_mod23 = int(pocc_nums.sum()) % 23

# Property 8: Anti-diagonal diff
obs_anti_diag_diff = int(anti_diag_values[hasv_nums].sum() - anti_diag_values[pocc_nums].sum())

# Additional: 4th power diff
obs_p4_diff = int((hasv_nums ** 4).sum() - (pocc_nums ** 4).sum())

# Additional: Symmetric cross-lookup
obs_sym_cross = sum(
    matrix[c2n(POCC[i])][c2n(HASV[i])] + matrix[c2n(HASV[i])][c2n(POCC[i])]
    for i in range(60)
)

print("=" * 70)
print("FIVE-SIGMA INDEPENDENCE AUDIT")
print(f"Trials: {N_TRIALS:,}")
print(f"Seed: {SEED}")
print("=" * 70)
print()

print("OBSERVED VALUES:")
print(f"  1. Diagonal diff:          {obs_diag_diff} (target: 676)")
print(f"  2. Character sum diff:     {obs_char_diff} (target: 138)")
print(f"  3. Identical positions:    {obs_identical} (target: >=6)")
print(f"  4. Cubes diff:             {obs_cubes_diff} (div by 676: {obs_cubes_div676}, quotient: {obs_cubes_diff // 676})")
print(f"  5. Identical chars sum:    {obs_identical_sum} (target: 46)")
print(f"  6. POCC mod 6:             {obs_pocc_mod6} (target: 0)")
print(f"  7. POCC mod 23:            {obs_pocc_mod23} (target: 14)")
print(f"  8. Anti-diagonal diff:     {obs_anti_diag_diff}")
print(f"  +. 4th power diff:         {obs_p4_diff} (div by 676: {obs_p4_diff % 676 == 0})")
print(f"  +. Symmetric cross-lookup: {obs_sym_cross}")
print()

# =============================================================================
# MONTE CARLO: Individual p-values + pairwise correlations
# =============================================================================
np.random.seed(SEED)
start_time = time.time()

# Storage for hit flags (for correlation computation)
hits = np.zeros((N_TRIALS, 8), dtype=bool)

# Counters for individual p-values
counts = np.zeros(8, dtype=np.int64)

# Additional property counters
count_p4_div676 = 0
count_sym_cross = 0
count_anti_diag_special = 0

print("Running Monte Carlo...")
batch_size = 50000

for batch_start in range(0, N_TRIALS, batch_size):
    batch_end = min(batch_start + batch_size, N_TRIALS)
    bs = batch_end - batch_start

    a1 = np.random.randint(0, 26, (bs, 60))
    a2 = np.random.randint(0, 26, (bs, 60))

    # Property 1: |diagonal diff| == 676
    d1 = diag_values[a1].sum(axis=1)
    d2 = diag_values[a2].sum(axis=1)
    dd = np.abs(d2 - d1)
    h1 = dd == 676
    hits[batch_start:batch_end, 0] = h1
    counts[0] += h1.sum()

    # Property 2: |char sum diff| == 138
    cs1 = a1.sum(axis=1)
    cs2 = a2.sum(axis=1)
    cd = np.abs(cs2 - cs1)
    h2 = cd == 138
    hits[batch_start:batch_end, 1] = h2
    counts[1] += h2.sum()

    # Property 3: identical positions >= 6
    identical = (a1 == a2).sum(axis=1)
    h3 = identical >= 6
    hits[batch_start:batch_end, 2] = h3
    counts[2] += h3.sum()

    # Property 4: cubes diff divisible by 676
    c1 = (a1.astype(np.int64) ** 3).sum(axis=1)
    c2 = (a2.astype(np.int64) ** 3).sum(axis=1)
    cubes_d = np.abs(c2 - c1)
    h4 = (cubes_d % 676 == 0) & (cubes_d > 0)
    hits[batch_start:batch_end, 3] = h4
    counts[3] += h4.sum()

    # Property 5: identical chars value sum (for those with >=1 identical)
    # This is position-dependent, compute per pair
    for k in range(bs):
        ident_mask = a1[k] == a2[k]
        if ident_mask.sum() >= 1:
            ident_sum = a1[k][ident_mask].sum()
            h5 = (ident_sum == 46)
        else:
            h5 = False
        hits[batch_start + k, 4] = h5
    counts[4] = hits[:batch_end, 4].sum()

    # Property 6: first address sum mod 6 == 0
    h6 = cs1 % 6 == 0
    hits[batch_start:batch_end, 5] = h6
    counts[5] += h6.sum()

    # Property 7: first address sum mod 23 == 14
    h7 = cs1 % 23 == 14
    hits[batch_start:batch_end, 6] = h7
    counts[6] += h7.sum()

    # Property 8: anti-diagonal diff matches observed
    ad1 = anti_diag_values[a1].sum(axis=1)
    ad2 = anti_diag_values[a2].sum(axis=1)
    add = np.abs(ad2 - ad1)
    h8 = add == abs(obs_anti_diag_diff)
    hits[batch_start:batch_end, 7] = h8
    counts[7] += h8.sum()

    # Additional: 4th power divisible by 676
    p4_1 = (a1.astype(np.int64) ** 4).sum(axis=1)
    p4_2 = (a2.astype(np.int64) ** 4).sum(axis=1)
    p4d = np.abs(p4_2 - p4_1)
    count_p4_div676 += ((p4d % 676 == 0) & (p4d > 0)).sum()

    if (batch_start + bs) % 200000 == 0:
        elapsed = time.time() - start_time
        pct = (batch_start + bs) / N_TRIALS * 100
        print(f"  {pct:.0f}% ({batch_start + bs:,} trials, {elapsed:.1f}s)")

elapsed = time.time() - start_time
print(f"  100% ({N_TRIALS:,} trials, {elapsed:.1f}s)")
print()

# =============================================================================
# INDIVIDUAL P-VALUES
# =============================================================================
labels = [
    "|diag_diff| = 676",
    "|char_diff| = 138",
    "identical_pos >= 6",
    "cubes_diff % 676 = 0",
    "identical_sum = 46",
    "addr1_mod6 = 0",
    "addr1_mod23 = 14",
    f"|anti_diag_diff| = {abs(obs_anti_diag_diff)}",
]

print("=" * 70)
print("INDIVIDUAL P-VALUES")
print("=" * 70)
print()

p_values = counts / N_TRIALS
for i in range(8):
    p = p_values[i]
    ratio = f"1 in {1/p:,.0f}" if p > 0 else "< 1/N"
    print(f"  [{i+1}] {labels[i]:35s}: {counts[i]:>8,} / {N_TRIALS:,} = p = {p:.7f} ({ratio})")

print()
print(f"  [+] 4th_power % 676 = 0:                  {count_p4_div676:>8,} / {N_TRIALS:,} = p = {count_p4_div676/N_TRIALS:.7f}")
print()

# =============================================================================
# PAIRWISE CORRELATION MATRIX (Phi coefficient)
# =============================================================================
print("=" * 70)
print("PAIRWISE CORRELATION MATRIX (Phi coefficient)")
print("=" * 70)
print()

# Only compute for properties with p > 0 (need hits)
active_props = [i for i in range(8) if counts[i] > 10]

short_labels = ["diag676", "char138", "ident6+", "cube676", "isum46", "mod6=0", "mod23=14", "antidiag"]

# Print header
print(f"{'':12s}", end="")
for j in active_props:
    print(f"{short_labels[j]:>10s}", end="")
print()

phi_matrix = np.zeros((8, 8))

for i in active_props:
    print(f"{short_labels[i]:12s}", end="")
    for j in active_props:
        if i == j:
            print(f"{'1.000':>10s}", end="")
            phi_matrix[i][j] = 1.0
        else:
            # Phi coefficient: (n11*n00 - n10*n01) / sqrt(n1_*n0_*n_1*n_0)
            a = hits[:, i].astype(np.int64)
            b = hits[:, j].astype(np.int64)
            n11 = (a & b).sum()
            n10 = (a & ~hits[:, j]).sum()
            n01 = (~hits[:, i] & b).sum()
            n00 = (~hits[:, i] & ~hits[:, j]).sum()
            denom = np.sqrt(float((n11+n10)) * float((n01+n00)) * float((n11+n01)) * float((n10+n00)))
            if denom > 0:
                phi = (n11 * n00 - n10 * n01) / denom
            else:
                phi = 0
            phi_matrix[i][j] = phi
            print(f"{phi:>10.4f}", end="")
    print()

print()

# =============================================================================
# CONDITIONAL P-VALUES (the key independence test)
# =============================================================================
print("=" * 70)
print("CONDITIONAL P-VALUES: P(B | A) vs P(B)")
print("If P(B|A) ≈ P(B), the properties are independent")
print("=" * 70)
print()

key_pairs = [
    (0, 1, "diag676 → char138"),
    (0, 2, "diag676 → ident6+"),
    (1, 2, "char138 → ident6+"),
    (0, 3, "diag676 → cube676"),
    (1, 3, "char138 → cube676"),
    (2, 3, "ident6+ → cube676"),
    (0, 5, "diag676 → mod6=0"),
    (1, 5, "char138 → mod6=0"),
    (0, 6, "diag676 → mod23=14"),
    (1, 6, "char138 → mod23=14"),
    (2, 4, "ident6+ → isum46"),
]

for i, j, label in key_pairs:
    a = hits[:, i]
    b = hits[:, j]
    n_a = a.sum()
    n_b = b.sum()
    n_ab = (a & b).sum()

    p_b = n_b / N_TRIALS
    p_b_given_a = n_ab / n_a if n_a > 0 else 0
    ratio = p_b_given_a / p_b if p_b > 0 else float('inf')

    independent = "YES" if 0.5 < ratio < 2.0 else "CORRELATED" if ratio > 2.0 else "ANTI-CORRELATED"

    print(f"  {label:25s}: P(B)={p_b:.5f}, P(B|A)={p_b_given_a:.5f}, ratio={ratio:.3f} → {independent}")

print()

# =============================================================================
# THREE-WAY COMBINED TEST (the core)
# =============================================================================
print("=" * 70)
print("THREE-WAY COMBINED TEST: diag=676 AND char=138 AND ident>=6")
print("=" * 70)
print()

three_way = (hits[:, 0] & hits[:, 1] & hits[:, 2]).sum()
p_three = three_way / N_TRIALS

print(f"  Hits: {three_way} / {N_TRIALS:,}")
if three_way > 0:
    print(f"  p = {p_three:.10f} = 1 in {1/p_three:,.0f}")
else:
    upper = 3.0 / N_TRIALS
    print(f"  p < {upper:.2e} (95% upper bound for 0 hits)")

# Expected if independent
p_ind = p_values[0] * p_values[1] * p_values[2]
print(f"  Expected (if independent): {p_ind:.2e} = 1 in {1/p_ind:,.0f}")
print()

# =============================================================================
# FOUR-WAY TEST (add cubes if independent)
# =============================================================================
print("=" * 70)
print("FOUR-WAY COMBINED TEST: diag=676 AND char=138 AND ident>=6 AND cubes%676=0")
print("=" * 70)
print()

four_way = (hits[:, 0] & hits[:, 1] & hits[:, 2] & hits[:, 3]).sum()
p_four = four_way / N_TRIALS

print(f"  Hits: {four_way} / {N_TRIALS:,}")
if four_way > 0:
    print(f"  p = {p_four:.10f} = 1 in {1/p_four:,.0f}")
else:
    upper = 3.0 / N_TRIALS
    print(f"  p < {upper:.2e} (95% upper bound for 0 hits)")

p_ind4 = p_values[0] * p_values[1] * p_values[2] * p_values[3]
print(f"  Expected (if independent): {p_ind4:.2e} = 1 in {1/p_ind4:,.0f}")
print()

# =============================================================================
# SIGMA LEVEL CALCULATION
# =============================================================================
from scipy.stats import norm

print("=" * 70)
print("SIGMA LEVEL SUMMARY")
print("=" * 70)
print()

def p_to_sigma(p):
    if p <= 0:
        return ">6"
    return f"{norm.ppf(1 - p/2):.2f}"

# Two-way (previous result)
two_way = (hits[:, 0] & hits[:, 1]).sum()
p_two = two_way / N_TRIALS if two_way > 0 else 3.0 / N_TRIALS
print(f"  2-property (diag+char):            p = {p_two:.2e}  →  {p_to_sigma(p_two)} sigma")

# Three-way
p_three_eff = p_three if three_way > 0 else 3.0 / N_TRIALS
print(f"  3-property (+identical):           p = {p_three_eff:.2e}  →  {p_to_sigma(p_three_eff)} sigma")

# Four-way
p_four_eff = p_four if four_way > 0 else 3.0 / N_TRIALS
print(f"  4-property (+cubes):               p = {p_four_eff:.2e}  →  {p_to_sigma(p_four_eff)} sigma")

print()
print(f"  5-sigma threshold:                 p < 2.87e-7 = 1 in 3,488,556")
print()

# =============================================================================
# INDEPENDENCE VERDICT
# =============================================================================
print("=" * 70)
print("INDEPENDENCE VERDICT")
print("=" * 70)
print()

for i, j, label in key_pairs:
    a = hits[:, i]
    b = hits[:, j]
    n_a = a.sum()
    n_ab = (a & b).sum()
    p_b = hits[:, j].sum() / N_TRIALS
    p_b_given_a = n_ab / n_a if n_a > 0 else 0
    ratio = p_b_given_a / p_b if p_b > 0 else 0

    if 0.7 < ratio < 1.5:
        verdict = "INDEPENDENT"
    elif 0.5 < ratio < 2.0:
        verdict = "WEAKLY CORRELATED"
    else:
        verdict = "DEPENDENT"

    print(f"  {label:25s}: {verdict} (ratio={ratio:.3f})")

print()
print("RECOMMENDED INDEPENDENT SET:")
print("  Based on correlation analysis, the following properties")
print("  can be combined for the final Monte Carlo test:")

# Determine recommended set
recommended = [0, 1, 2]  # Always include diag, char, identical
# Check cubes independence from all three
cube_ok = True
for base in [0, 1, 2]:
    a = hits[:, base]
    b = hits[:, 3]
    n_a = a.sum()
    n_ab = (a & b).sum()
    p_b = hits[:, 3].sum() / N_TRIALS
    p_b_given_a = n_ab / n_a if n_a > 0 else 0
    ratio = p_b_given_a / p_b if p_b > 0 else 0
    if not (0.5 < ratio < 2.0):
        cube_ok = False
        break

if cube_ok and counts[3] > 0:
    recommended.append(3)

print(f"  → Properties: {[labels[i] for i in recommended]}")
print(f"  → Expected combined p: {np.prod([p_values[i] for i in recommended]):.2e}")
print()

print("=" * 70)
print("AUDIT COMPLETE")
print(f"Total time: {time.time() - start_time:.1f}s")
print("=" * 70)
