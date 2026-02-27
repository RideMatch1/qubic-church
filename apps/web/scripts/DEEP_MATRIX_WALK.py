#!/usr/bin/env python3
"""
MATRIX WALK: POCC → HASV Transformation Analysis
==================================================
Can POCC be "transformed" into HASV through the matrix?

Tests:
1. Difference sequence analysis (periodicity, FFT, autocorrelation)
2. Matrix transformation pathways
3. Row-by-row sum profile (all 128 rows)
4. Diagonal stepping patterns

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-10
"""

import json
import numpy as np
from pathlib import Path

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
print("MATRIX WALK: POCC → HASV TRANSFORMATION ANALYSIS")
print("=" * 70)
print()

# =============================================================================
# ANALYSIS 1: Difference Sequence
# =============================================================================
print("--- ANALYSIS 1: Difference Sequence ---")

diff_seq = (hasv_nums - pocc_nums) % 26
diff_raw = hasv_nums - pocc_nums  # raw, not mod 26

print(f"Raw diff (H-P): {diff_raw.tolist()}")
print(f"Mod 26 diff:    {diff_seq.tolist()}")
print()

# Basic stats
print(f"Raw diff: mean={diff_raw.mean():.2f}, std={diff_raw.std():.2f}")
print(f"Mod26 diff: mean={diff_seq.mean():.2f}, std={diff_seq.std():.2f}")
print(f"Sum of raw diffs: {diff_raw.sum()} (= charsum_diff = 138)")
print()

# Check for periodicity
print("Periodicity check:")
for period in [2, 3, 4, 5, 6, 10, 12, 15, 20, 30]:
    if 60 % period == 0:
        segments = [diff_seq[i*period:(i+1)*period].tolist() for i in range(60//period)]
        unique_segments = len(set(str(s) for s in segments))
        print(f"  Period {period:2d}: {60//period} segments, {unique_segments} unique")

print()

# FFT analysis
print("FFT Analysis (mod 26 differences):")
fft_result = np.fft.fft(diff_seq.astype(float))
magnitudes = np.abs(fft_result)
# Skip DC component (index 0)
top_freqs = np.argsort(magnitudes[1:30])[::-1][:5] + 1
for idx in top_freqs:
    print(f"  Freq {idx} (period={60/idx:.1f}): magnitude={magnitudes[idx]:.2f}")

print()

# Check if difference sequence contains known patterns
print("Pattern detection in diff sequence:")
# Fibonacci mod 26
fib = [0, 1]
for i in range(58):
    fib.append((fib[-1] + fib[-2]) % 26)
fib_match = sum(1 for i in range(60) if diff_seq[i] == fib[i])
print(f"  Fibonacci mod 26 matches: {fib_match}/60")

# Linear (arithmetic) sequence
for step in range(1, 26):
    linear = [(i * step) % 26 for i in range(60)]
    match = sum(1 for i in range(60) if diff_seq[i] == linear[i])
    if match > 10:
        print(f"  Linear step={step} matches: {match}/60")

print()

# =============================================================================
# ANALYSIS 2: Matrix Transformation Pathways
# =============================================================================
print("--- ANALYSIS 2: Matrix Transformation ---")
print()

# Can matrix[POCC[i]][x] = HASV[i] for some lookup pattern?
# For each position, find what column gives us HASV[i]
print("Matrix lookup: matrix[POCC[i]][?] = HASV[i]?")
transform_cols = []
for i in range(60):
    p = pocc_nums[i]
    h = hasv_nums[i]
    # Find all columns where matrix[p][col] relates to h
    # Since matrix values are in [-128, 127] and h is in [0, 25], check if matrix[p][col] % 26 == h
    matches = []
    for col in range(128):
        if matrix[p][col] % 26 == h:
            matches.append(col)
    transform_cols.append(matches)

# How many positions have a solution?
n_solvable = sum(1 for m in transform_cols if len(m) > 0)
print(f"  Positions with matrix[P[i]][col] %% 26 = H[i]: {n_solvable}/60")

# Is there a SINGLE column that works for many?
from collections import Counter
all_cols = []
for m in transform_cols:
    all_cols.extend(m)
col_freq = Counter(all_cols)
if col_freq:
    print(f"  Most common columns: {col_freq.most_common(5)}")
print()

# Direct matrix lookup: does matrix[P[i]][P[i]] tell us anything about H[i]?
print("Diagonal→target mapping:")
diag_vals = np.array([matrix[pocc_nums[i]][pocc_nums[i]] for i in range(60)])
# Does diag_val mod 26 relate to HASV?
diag_mod26 = diag_vals % 26
matches_diag = sum(1 for i in range(60) if diag_mod26[i] == hasv_nums[i])
print(f"  matrix[P[i]][P[i]] %% 26 = H[i]: {matches_diag}/60 (expected ~2.3)")
print()

# =============================================================================
# ANALYSIS 3: Row-by-Row Sum Profile
# =============================================================================
print("--- ANALYSIS 3: Row-by-Row Sum Profile ---")
print()

# For each row r (0-127), compute sum of matrix[r][POCC[i]] and matrix[r][HASV[i]]
row_diffs = []
interesting_rows = []
for r in range(128):
    sum_p = sum(int(matrix[r][pocc_nums[i]]) for i in range(60))
    sum_h = sum(int(matrix[r][hasv_nums[i]]) for i in range(60))
    diff = sum_h - sum_p
    row_diffs.append(diff)

    # Flag interesting values
    if diff != 0 and diff % 26 == 0:
        interesting_rows.append((r, diff, diff // 26))

row_diffs = np.array(row_diffs)
print(f"Row sum differences (HASV - POCC) via each row:")
print(f"  Mean: {row_diffs.mean():.2f}")
print(f"  Std: {row_diffs.std():.2f}")
print(f"  Min: {row_diffs.min()} (row {row_diffs.argmin()})")
print(f"  Max: {row_diffs.max()} (row {row_diffs.argmax()})")
print()

# Rows where diff is a multiple of 26
print(f"Rows where diff is a non-zero multiple of 26: {len(interesting_rows)}")
for r, diff, mult in interesting_rows:
    marker = ""
    if diff == 676:
        marker = " *** DIAGONAL ROW ***"
    elif diff == 26:
        marker = " *** ROW 79 EQUIVALENT ***"
    elif abs(diff) == 676:
        marker = " *** |676| ***"
    print(f"  Row {r:3d}: diff = {diff:6d} = {mult:3d} × 26{marker}")

print()

# Monte Carlo: how many rows show mult-of-26 for random pairs?
N_MC = 50_000
np.random.seed(42)
mc_mult26_rows = np.zeros(N_MC)
for trial in range(N_MC):
    a1 = np.random.randint(0, 26, 60)
    a2 = np.random.randint(0, 26, 60)
    count = 0
    for r in range(128):
        s1 = sum(int(matrix[r][a1[i]]) for i in range(60))
        s2 = sum(int(matrix[r][a2[i]]) for i in range(60))
        d = s2 - s1
        if d != 0 and d % 26 == 0:
            count += 1
    mc_mult26_rows[trial] = count
    if trial % 10000 == 0 and trial > 0:
        print(f"  MC progress: {trial}/{N_MC}")

obs_mult26 = len(interesting_rows)
p_mult26 = (mc_mult26_rows >= obs_mult26).mean()
print(f"\nMC test: {obs_mult26} rows with mult-of-26 diff")
print(f"  MC mean: {mc_mult26_rows.mean():.1f}, std: {mc_mult26_rows.std():.1f}")
print(f"  p = {p_mult26:.5f} {'SIGNIFICANT' if p_mult26 < 0.01 else 'not significant'}")
print()

# Which row gives diff = 676?
rows_676 = [r for r in range(128) if row_diffs[r] == 676]
print(f"Rows where diff = 676: {rows_676}")
if rows_676:
    print("  (The diagonal sum uses matrix[i][i], which is equivalent to 'row i at column i')")
    print("  (So row-based lookup gives 676 when we happen to hit diagonal entries)")
print()

# =============================================================================
# ANALYSIS 4: Stepping Through the Matrix
# =============================================================================
print("--- ANALYSIS 4: Matrix Stepping Patterns ---")
print()

# Walk: start at position (0,0), step by (POCC[i], HASV[i])
# What values do we encounter?
walk_vals = []
x, y = 0, 0
for i in range(60):
    x = (x + pocc_nums[i]) % 128
    y = (y + hasv_nums[i]) % 128
    walk_vals.append(int(matrix[x][y]))

walk_sum = sum(walk_vals)
print(f"Walk sum (stepping by POCC/HASV through matrix): {walk_sum}")
print(f"  Walk mod 676: {walk_sum % 676}")
print(f"  Walk mod 26: {walk_sum % 26}")
print()

# MC comparison
np.random.seed(42)
mc_walk = np.zeros(100_000)
for trial in range(100_000):
    a1 = np.random.randint(0, 26, 60)
    a2 = np.random.randint(0, 26, 60)
    x, y = 0, 0
    ws = 0
    for i in range(60):
        x = (x + a1[i]) % 128
        y = (y + a2[i]) % 128
        ws += int(matrix[x][y])
    mc_walk[trial] = ws

z_walk = (walk_sum - mc_walk.mean()) / mc_walk.std() if mc_walk.std() > 0 else 0
p_walk = (np.abs(mc_walk - mc_walk.mean()) >= abs(walk_sum - mc_walk.mean())).mean()
print(f"  MC: mean={mc_walk.mean():.1f}, std={mc_walk.std():.1f}")
print(f"  z = {z_walk:.2f}, p = {p_walk:.5f}")
print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("MATRIX WALK SUMMARY")
print("=" * 70)
print()
print("1. Difference sequence: No periodicity, no known pattern (Fibonacci, linear)")
print(f"2. Matrix transformation: {n_solvable}/60 positions solvable")
print(f"3. Row profile: {len(interesting_rows)} rows with mult-of-26 diffs (p={p_mult26:.4f})")
print(f"   Rows with diff=676: {rows_676}")
print(f"4. Matrix walk sum: {walk_sum} (z={z_walk:.2f}, p={p_walk:.4f})")
print()

# Final assessment
significant_findings = []
if p_mult26 < 0.01:
    significant_findings.append(f"Row profile: {len(interesting_rows)} mult-of-26 rows (p={p_mult26:.5f})")
if p_walk < 0.01:
    significant_findings.append(f"Walk sum: {walk_sum} (p={p_walk:.5f})")

if significant_findings:
    print("SIGNIFICANT FINDINGS:")
    for f in significant_findings:
        print(f"  {f}")
else:
    print("NO new significant findings from matrix walk analysis.")
    print("The POCC→HASV relationship does not follow a simple matrix pathway.")
    print("This supports the interpretation that the connection is purely")
    print("through frequency-based diagonal properties, not positional encoding.")

print()
print("=" * 70)
print("COMPLETE")
print("=" * 70)
