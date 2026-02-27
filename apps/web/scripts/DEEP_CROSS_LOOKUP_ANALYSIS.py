#!/usr/bin/env python3
"""
CROSS-LOOKUP ANALYSIS (NEVER TESTED BEFORE)
============================================
Instead of diagonal lookups matrix[x][x], compute CROSS lookups:
  matrix[POCC[i]][HASV[i]]  and  matrix[HASV[i]][POCC[i]]

This uses the OFF-DIAGONAL elements of the 26x26 submatrix,
which are completely independent from diagonal sums.

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-10
"""

import json
import numpy as np
from pathlib import Path
import time

# =============================================================================
# LOAD DATA
# =============================================================================
MATRIX_FILE = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
matrix = np.array(data['matrix'], dtype=np.int64)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def c2n(c):
    return ord(c) - ord('A')

pocc_nums = np.array([c2n(c) for c in POCC])
hasv_nums = np.array([c2n(c) for c in HASV])

print("=" * 70)
print("CROSS-LOOKUP ANALYSIS")
print("=" * 70)
print()

# =============================================================================
# COMPUTE CROSS-LOOKUPS
# =============================================================================
# Forward: matrix[POCC[i]][HASV[i]] — use POCC letter as row, HASV letter as col
cross_ph = np.array([int(matrix[pocc_nums[i]][hasv_nums[i]]) for i in range(60)])

# Reverse: matrix[HASV[i]][POCC[i]] — use HASV letter as row, POCC letter as col
cross_hp = np.array([int(matrix[hasv_nums[i]][pocc_nums[i]]) for i in range(60)])

# Symmetric sum: matrix[P][H] + matrix[H][P]
cross_sym = cross_ph + cross_hp

# At identical positions, both are diagonal: matrix[x][x]
identical_mask = pocc_nums == hasv_nums
n_identical = identical_mask.sum()

print("Position-by-position cross-lookups (first 20):")
print(f"{'Pos':>3} {'P':>3} {'H':>3} {'M[P][H]':>8} {'M[H][P]':>8} {'Sum':>6} {'Note'}")
print("-" * 55)
for i in range(20):
    note = "DIAG" if pocc_nums[i] == hasv_nums[i] else ""
    print(f"{i:3d} {chr(pocc_nums[i]+65):>3} {chr(hasv_nums[i]+65):>3} "
          f"{cross_ph[i]:8d} {cross_hp[i]:8d} {cross_sym[i]:6d} {note}")
print("...")
print()

# =============================================================================
# AGGREGATE METRICS
# =============================================================================
sum_ph = int(cross_ph.sum())
sum_hp = int(cross_hp.sum())
sum_sym = int(cross_sym.sum())
diff_cross = int(sum_ph - sum_hp)

print("AGGREGATE CROSS-LOOKUP METRICS:")
print(f"  sum(M[P][H]): {sum_ph}")
print(f"  sum(M[H][P]): {sum_hp}")
print(f"  Symmetric sum: {sum_sym}")
print(f"  Difference (P→H - H→P): {diff_cross}")
print()

# Check for "interesting" values
interesting = [676, 338, 138, 69, 26, 121, 0, 256, 512, 576, 46, 33, 90]
print("Check against interesting numbers:")
for val in interesting:
    for name, observed in [("sum_PH", sum_ph), ("sum_HP", sum_hp),
                           ("sym_sum", sum_sym), ("diff", diff_cross)]:
        if observed == val:
            print(f"  !!! {name} = {val} !!!")
        if val != 0 and observed % val == 0:
            print(f"  {name} ({observed}) mod {val} = 0 (= {observed // val} x {val})")
print()

# =============================================================================
# DETAILED ANALYSIS
# =============================================================================
print("STATISTICAL PROPERTIES:")
print(f"  cross_ph: mean={cross_ph.mean():.2f}, std={cross_ph.std():.2f}, "
      f"min={cross_ph.min()}, max={cross_ph.max()}")
print(f"  cross_hp: mean={cross_hp.mean():.2f}, std={cross_hp.std():.2f}, "
      f"min={cross_hp.min()}, max={cross_hp.max()}")
print(f"  cross_sym: mean={cross_sym.mean():.2f}, std={cross_sym.std():.2f}")
print()

# Correlation between cross_ph and cross_hp
if cross_ph.std() > 0 and cross_hp.std() > 0:
    corr = np.corrcoef(cross_ph, cross_hp)[0, 1]
    print(f"  Correlation(M[P][H], M[H][P]): {corr:.4f}")
print()

# At identical positions
print(f"At {n_identical} identical positions:")
ident_ph = cross_ph[identical_mask]
ident_hp = cross_hp[identical_mask]
print(f"  Values: {ident_ph.tolist()}")
print(f"  Sum: {ident_ph.sum()}")
print(f"  These are DIAGONAL values: matrix[x][x] for x in {pocc_nums[identical_mask].tolist()}")
print()

# At NON-identical positions
non_ident_ph = cross_ph[~identical_mask]
non_ident_hp = cross_hp[~identical_mask]
print(f"At {60 - n_identical} non-identical positions:")
print(f"  sum(M[P][H]): {non_ident_ph.sum()}")
print(f"  sum(M[H][P]): {non_ident_hp.sum()}")
print(f"  Symmetric sum: {(non_ident_ph + non_ident_hp).sum()}")
print()

# =============================================================================
# MATRIX SYMMETRY CHECK
# =============================================================================
# Anna Matrix has 99.58% point symmetry: M[r,c] + M[127-r, 127-c] ≈ -1
# For the 26x26 submatrix (rows/cols 0-25), check:
# M[i][j] + M[25-i][25-j] = ?
print("SYMMETRY CHECK (26x26 submatrix):")
sym_check = []
for i in range(26):
    for j in range(26):
        if i != j:  # off-diagonal only
            sym_val = int(matrix[i][j]) + int(matrix[25-i][25-j])
            sym_check.append(sym_val)

sym_arr = np.array(sym_check)
print(f"  M[i][j] + M[25-i][25-j] for all off-diagonal pairs:")
print(f"  Mean: {sym_arr.mean():.2f}")
print(f"  Most common: {np.bincount(sym_arr - sym_arr.min()).argmax() + sym_arr.min()}")
print(f"  = -1 count: {(sym_arr == -1).sum()} / {len(sym_arr)}")
print()

# Does M[P[i]][H[i]] ≈ -M[H[i]][P[i]] due to antisymmetry?
# If M[r,c] ≈ -M[c,r] (antisymmetric), then cross_ph ≈ -cross_hp
anti_sym_test = cross_ph + cross_hp  # should be near 0 if antisymmetric
print("ANTISYMMETRY TEST (M[P][H] + M[H][P]):")
print(f"  Sum of (M[P][H] + M[H][P]): {anti_sym_test.sum()}")
print(f"  Mean: {anti_sym_test.mean():.2f}")
print(f"  If antisymmetric, sum should be near 0.")
print(f"  Actual: {anti_sym_test.sum()} (deviation: {abs(anti_sym_test.sum())}")
print()

# =============================================================================
# MONTE CARLO COMPARISON
# =============================================================================
print("=" * 70)
print("MONTE CARLO: 1,000,000 Random Pairs")
print("=" * 70)
print()

N_MC = 1_000_000
np.random.seed(42)
start_time = time.time()

mc_sum_ph = np.zeros(N_MC, dtype=np.int64)
mc_sum_hp = np.zeros(N_MC, dtype=np.int64)
mc_sym = np.zeros(N_MC, dtype=np.int64)
mc_diff = np.zeros(N_MC, dtype=np.int64)

batch_size = 100_000
for batch_start in range(0, N_MC, batch_size):
    bs = min(batch_size, N_MC - batch_start)
    a1 = np.random.randint(0, 26, (bs, 60))
    a2 = np.random.randint(0, 26, (bs, 60))

    for trial_idx in range(bs):
        ph_vals = np.array([int(matrix[a1[trial_idx, i]][a2[trial_idx, i]]) for i in range(60)])
        hp_vals = np.array([int(matrix[a2[trial_idx, i]][a1[trial_idx, i]]) for i in range(60)])
        idx = batch_start + trial_idx
        mc_sum_ph[idx] = ph_vals.sum()
        mc_sum_hp[idx] = hp_vals.sum()
        mc_sym[idx] = (ph_vals + hp_vals).sum()
        mc_diff[idx] = ph_vals.sum() - hp_vals.sum()

elapsed = time.time() - start_time
print(f"Monte Carlo complete: {elapsed:.1f}s")
print()

# Compare observed vs Monte Carlo distributions
for name, observed, mc_data in [
    ("sum(M[P][H])", sum_ph, mc_sum_ph),
    ("sum(M[H][P])", sum_hp, mc_sum_hp),
    ("Symmetric sum", sum_sym, mc_sym),
    ("Difference", diff_cross, mc_diff),
]:
    mc_mean = mc_data.mean()
    mc_std = mc_data.std()
    z = (observed - mc_mean) / mc_std if mc_std > 0 else 0
    percentile = (mc_data <= observed).mean() * 100
    # Exact match count
    exact_matches = (mc_data == observed).sum()
    p_exact = exact_matches / N_MC

    print(f"{name}:")
    print(f"  Observed: {observed}")
    print(f"  MC distribution: mean={mc_mean:.1f}, std={mc_std:.1f}")
    print(f"  Z-score: {z:.2f}")
    print(f"  Percentile: {percentile:.2f}%")
    print(f"  Exact matches: {exact_matches} / {N_MC:,} (p = {p_exact:.6f})")

    if abs(z) > 3:
        print(f"  >>> SIGNIFICANT (|z| > 3)! <<<")
    elif abs(z) > 2:
        print(f"  >>> NOTABLE (|z| > 2) <<<")
    print()

# =============================================================================
# SPECIAL: Cross-lookup difference and known numbers
# =============================================================================
print("=" * 70)
print("ADDITIONAL CROSS-LOOKUP TESTS")
print("=" * 70)
print()

# Test: sum of matrix[P[i]][H[i]] for positions where P[i] < H[i]
# vs positions where P[i] > H[i]
lt_mask = pocc_nums < hasv_nums
gt_mask = pocc_nums > hasv_nums
eq_mask = pocc_nums == hasv_nums

print(f"Position groups:")
print(f"  P[i] < H[i]: {lt_mask.sum()} positions, cross sum = {cross_ph[lt_mask].sum()}")
print(f"  P[i] > H[i]: {gt_mask.sum()} positions, cross sum = {cross_ph[gt_mask].sum()}")
print(f"  P[i] = H[i]: {eq_mask.sum()} positions, cross sum = {cross_ph[eq_mask].sum()}")
print()

# Positional cross-sum weighted by position index
weighted = sum(cross_ph[i] * i for i in range(60))
print(f"Position-weighted cross sum: {weighted}")
print(f"  mod 676: {weighted % 676}")
print(f"  mod 26: {weighted % 26}")
print()

# =============================================================================
# CONCLUSION
# =============================================================================
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

significant_metrics = []
for name, observed, mc_data in [
    ("sum(M[P][H])", sum_ph, mc_sum_ph),
    ("sum(M[H][P])", sum_hp, mc_sum_hp),
    ("Symmetric", sum_sym, mc_sym),
    ("Difference", diff_cross, mc_diff),
]:
    mc_std = mc_data.std()
    z = (observed - mc_data.mean()) / mc_std if mc_std > 0 else 0
    if abs(z) > 2:
        significant_metrics.append((name, observed, z))

if significant_metrics:
    print("SIGNIFICANT cross-lookup metrics found:")
    for name, val, z in significant_metrics:
        print(f"  {name} = {val} (z = {z:.2f})")
    print()
    print("These are INDEPENDENT from diagonal sums and could strengthen")
    print("the POCC/HASV proof if verified with Bonferroni correction.")
else:
    print("No significant cross-lookup metrics found.")
    print("Cross-lookups appear consistent with random pairs.")
    print("This is an honest null result.")

print()
print("=" * 70)
print("COMPLETE")
print("=" * 70)
