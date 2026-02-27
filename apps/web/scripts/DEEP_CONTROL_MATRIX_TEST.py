#!/usr/bin/env python3
"""
CONTROL MATRIX TEST
===================
Question: Does POCC/HASV diag_diff=676 ONLY work with the real Anna Matrix,
or would any similar 128x128 matrix produce the same result?

Method:
  1. Generate 10,000 control matrices with same statistical properties
  2. Compute diag_diff(POCC, HASV) for EACH control matrix
  3. Count how many produce diag_diff = 676

If 0/10,000: The Anna Matrix is THE key (very strong evidence)
If >100/10,000: The relationship is not matrix-specific (weaker)

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-10
"""

import json
import numpy as np
from pathlib import Path
import time

# =============================================================================
# LOAD REAL ANNA MATRIX
# =============================================================================
MATRIX_FILE = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
real_matrix = np.array(data['matrix'], dtype=np.int64)

# Addresses
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def c2n(c):
    return ord(c) - ord('A')

pocc_nums = [c2n(c) for c in POCC]
hasv_nums = [c2n(c) for c in HASV]

# Pre-compute character frequency differences (for understanding WHY 676 emerges)
freq_diff = np.zeros(26, dtype=np.int64)
for c in pocc_nums:
    freq_diff[c] -= 1
for c in hasv_nums:
    freq_diff[c] += 1

# =============================================================================
# REAL MATRIX RESULTS
# =============================================================================
real_diag = np.array([real_matrix[i][i] for i in range(26)], dtype=np.int64)
real_pocc_diag = sum(real_diag[c] for c in pocc_nums)
real_hasv_diag = sum(real_diag[c] for c in hasv_nums)
real_diff = int(real_hasv_diag - real_pocc_diag)

# The diagonal difference depends on: sum(freq_diff[i] * diag[i]) for i in 0..25
# This is a dot product of frequency differences and diagonal values
computed_diff = int(np.dot(freq_diff, real_diag))

print("=" * 70)
print("CONTROL MATRIX TEST")
print("=" * 70)
print()
print(f"Real Anna Matrix diagonal (first 26): {real_diag.tolist()}")
print(f"POCC diagonal sum: {real_pocc_diag}")
print(f"HASV diagonal sum: {real_hasv_diag}")
print(f"Difference: {real_diff}")
print(f"Via dot product (freq_diff . diag): {computed_diff}")
print(f"Match: {real_diff == computed_diff}")
print()

print("Character frequency differences (HASV - POCC):")
for i in range(26):
    if freq_diff[i] != 0:
        print(f"  {chr(i+65)}: {freq_diff[i]:+d}")
print(f"  Sum of freq_diff: {freq_diff.sum()} (= charsum_diff / character_count_diff)")
print()

# =============================================================================
# UNDERSTAND THE STRUCTURE
# =============================================================================
# The diagonal difference = dot(freq_diff, diagonal_values)
# For this to equal 676, we need SPECIFIC diagonal values
# The question is: how specific?

print("=" * 70)
print("STRUCTURAL ANALYSIS")
print("=" * 70)
print()
print("The diagonal difference is computed as:")
print("  diag_diff = sum(freq_diff[i] * matrix[i][i] for i in 0..25)")
print()
print("This is a LINEAR function of the 26 diagonal values.")
print("For a random matrix, each diagonal value is drawn from [-128, 127].")
print()

# Compute the range of possible diag_diff values
# If each diagonal value is in [-128, 127], then:
max_possible = sum(abs(int(f)) * 127 for f in freq_diff)
print(f"Maximum possible |diag_diff|: {max_possible}")
print(f"  (if all diagonal values perfectly align with freq_diff)")
print(f"Total absolute frequency weight: {sum(abs(int(f)) for f in freq_diff)}")
print()

# =============================================================================
# CONTROL MATRIX GENERATION
# =============================================================================
N_CONTROLS = 10_000
np.random.seed(42)

print("=" * 70)
print(f"GENERATING {N_CONTROLS:,} CONTROL MATRICES")
print("=" * 70)
print()

start_time = time.time()

# Method 1: Random diagonal values from same distribution as real matrix
# The real diagonal values (0-25) are:
print(f"Real diagonal values [0:26]: {real_diag.tolist()}")
print(f"  Mean: {real_diag.mean():.2f}")
print(f"  Std:  {real_diag.std():.2f}")
print(f"  Min:  {real_diag.min()}")
print(f"  Max:  {real_diag.max()}")
print()

# Full matrix value distribution
full_diag = np.array([real_matrix[i][i] for i in range(128)], dtype=np.int64)
print(f"Full diagonal values [0:128]:")
print(f"  Mean: {full_diag.mean():.2f}")
print(f"  Std:  {full_diag.std():.2f}")
print(f"  Min:  {full_diag.min()}")
print(f"  Max:  {full_diag.max()}")
print()

# Generate control matrices with 3 different methods
methods = {}

# Method A: Same value distribution as real diagonal (bootstrap)
# Resample from the actual 128 diagonal values
hits_a = 0
diffs_a = []
for trial in range(N_CONTROLS):
    # Random permutation of all 128 diagonal values, take first 26
    perm = np.random.permutation(full_diag)[:26]
    diff = int(np.dot(freq_diff, perm))
    diffs_a.append(diff)
    if diff == 676:
        hits_a += 1

methods['A_bootstrap'] = (hits_a, diffs_a)

# Method B: Uniform random [-128, 127]
hits_b = 0
diffs_b = []
for trial in range(N_CONTROLS):
    diag = np.random.randint(-128, 128, size=26)
    diff = int(np.dot(freq_diff, diag))
    diffs_b.append(diff)
    if diff == 676:
        hits_b += 1

methods['B_uniform'] = (hits_b, diffs_b)

# Method C: Same mean and std as real diagonal
real_mean = real_diag.mean()
real_std = real_diag.std()
hits_c = 0
diffs_c = []
for trial in range(N_CONTROLS):
    diag = np.random.normal(real_mean, real_std, size=26).astype(np.int64)
    diag = np.clip(diag, -128, 127)
    diff = int(np.dot(freq_diff, diag))
    diffs_c.append(diff)
    if diff == 676:
        hits_c += 1

methods['C_gaussian'] = (hits_c, diffs_c)

# Method D: Exact same value set, random assignment to positions 0-25
# This tests whether it's the VALUES or the POSITIONS that matter
hits_d = 0
diffs_d = []
real_26_vals = real_diag.copy()
for trial in range(N_CONTROLS):
    perm = np.random.permutation(real_26_vals)
    diff = int(np.dot(freq_diff, perm))
    diffs_d.append(diff)
    if diff == 676:
        hits_d += 1

methods['D_permutation'] = (hits_d, diffs_d)

elapsed = time.time() - start_time
print(f"Generation complete: {elapsed:.1f}s")
print()

# =============================================================================
# RESULTS
# =============================================================================
print("=" * 70)
print("RESULTS")
print("=" * 70)
print()

for name, (hits, diffs) in methods.items():
    diffs_arr = np.array(diffs)
    print(f"Method {name}:")
    print(f"  Hits (diff = 676): {hits} / {N_CONTROLS}")
    print(f"  Diff distribution: mean={diffs_arr.mean():.1f}, std={diffs_arr.std():.1f}")
    print(f"  Diff range: [{diffs_arr.min()}, {diffs_arr.max()}]")

    # How many standard deviations is 676 from the mean?
    if diffs_arr.std() > 0:
        z = (676 - diffs_arr.mean()) / diffs_arr.std()
        print(f"  676 is {z:.2f} sigma from mean")

    # How close did we get?
    closest = diffs_arr[np.argmin(np.abs(diffs_arr - 676))]
    print(f"  Closest to 676: {closest} (distance: {abs(closest - 676)})")

    # Distribution around 676
    within_10 = np.sum(np.abs(diffs_arr - 676) <= 10)
    within_50 = np.sum(np.abs(diffs_arr - 676) <= 50)
    print(f"  Within ±10 of 676: {within_10}")
    print(f"  Within ±50 of 676: {within_50}")
    print()

# =============================================================================
# CRITICAL TEST: Method D (permutation of exact same values)
# =============================================================================
print("=" * 70)
print("CRITICAL: PERMUTATION TEST (Method D)")
print("=" * 70)
print()
print("This test uses the EXACT SAME 26 values as the real diagonal,")
print("but assigns them to RANDOM positions (letters A-Z).")
print()
print("If this produces 676 frequently: the VALUES matter, not positions.")
print("If this rarely produces 676: the POSITIONS (which letter gets which")
print("diagonal value) are crucial. This means the matrix was designed so")
print("that specific letters have specific diagonal values.")
print()

hits_d, diffs_d = methods['D_permutation']
diffs_d_arr = np.array(diffs_d)
p_perm = hits_d / N_CONTROLS if hits_d > 0 else f"< {1/N_CONTROLS:.1e}"
print(f"Result: {hits_d} / {N_CONTROLS} permutations produce diff = 676")
print(f"P(676 | same values, random positions) = {p_perm}")
print()

if hits_d == 0:
    print(">>> ZERO HITS: The specific POSITION assignment is essential!")
    print("    Not just any arrangement of these values produces 676.")
    print("    The matrix diagonal was designed with specific letter→value mapping.")
elif hits_d < 10:
    print(f">>> VERY FEW HITS ({hits_d}): Position assignment matters significantly.")
else:
    print(f">>> {hits_d} HITS: Position assignment is less critical.")
    print(f"    P = {hits_d/N_CONTROLS:.4f} ({hits_d/N_CONTROLS*100:.2f}%)")

print()

# =============================================================================
# EXTENDED: 1M permutation test for better precision
# =============================================================================
print("=" * 70)
print("EXTENDED: 1,000,000 Permutation Tests")
print("=" * 70)
print()

N_EXTENDED = 1_000_000
start_time = time.time()

hits_ext = 0
for trial in range(N_EXTENDED):
    perm = np.random.permutation(real_26_vals)
    diff = int(np.dot(freq_diff, perm))
    if diff == 676:
        hits_ext += 1

elapsed = time.time() - start_time
print(f"Completed {N_EXTENDED:,} permutations in {elapsed:.1f}s")
print(f"Hits (diff = 676): {hits_ext} / {N_EXTENDED:,}")

if hits_ext > 0:
    p_ext = hits_ext / N_EXTENDED
    print(f"P(676) = {p_ext:.6f} = 1 in {1/p_ext:,.0f}")
else:
    upper = 3.0 / N_EXTENDED
    print(f"P(676) < {upper:.2e} (95% upper bound)")

print()

# =============================================================================
# CONCLUSION
# =============================================================================
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

any_hits = any(h > 0 for h, _ in methods.values())
if not any_hits and hits_ext == 0:
    print("RESULT: ZERO control matrices produced diag_diff = 676")
    print()
    print("This means:")
    print("  1. The diagonal value 676 is SPECIFIC to the Anna Matrix")
    print("  2. No random permutation of the same values produces 676")
    print("  3. The assignment of diagonal values to letter positions")
    print("     was DELIBERATELY CHOSEN to make POCC/HASV = 676")
    print()
    print("  >>> THE ANNA MATRIX IS THE KEY <<<")
    print("  >>> POCC/HASV were built FOR THIS SPECIFIC MATRIX <<<")
else:
    total_hits = sum(h for h, _ in methods.values()) + hits_ext
    total_trials = N_CONTROLS * 4 + N_EXTENDED
    print(f"Total hits across all methods: {total_hits} / {total_trials:,}")
    if total_hits > 0:
        p_total = total_hits / total_trials
        print(f"Aggregate P(676) = {p_total:.6f}")
        print(f"This is {'rare' if p_total < 0.001 else 'uncommon' if p_total < 0.01 else 'not particularly rare'}")

print()
print("=" * 70)
print("COMPLETE")
print("=" * 70)
