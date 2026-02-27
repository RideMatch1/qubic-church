#!/usr/bin/env python3
"""
02_POINT_SYMMETRY_DEEP.py
=========================
Deep analysis of the Anna Matrix's point symmetry property.

KEY PROPERTY: For 99.58% of cells, matrix[r,c] + matrix[127-r, 127-c] = -1 (exact).
68 cells are exceptions.

This script verifies the symmetry rule, extracts and analyzes all exceptions,
proves that column-sum and row-sum symmetry are mathematical consequences of
point symmetry, and computes information-theoretic measures.

Seed: 42 | Controls: 10,000 random placements for spatial tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.matrix_loader import load_matrix
from lib.statistical_tests import TestReport
from lib.control_generator import generate_symmetric
import numpy as np
import json
from collections import Counter
from datetime import datetime


SEED = 42
N_SPATIAL_CONTROLS = 10_000
OUTPUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "02_POINT_SYMMETRY_DEEP_RESULTS.json")


def section_header(title):
    """Print a section header."""
    print()
    print("=" * 80)
    print(f"  SECTION: {title}")
    print("=" * 80)
    print()


# ==============================================================================
#  LOAD MATRIX
# ==============================================================================

print("Loading Anna Matrix...")
M = load_matrix(verify_hash=True)
N = 128  # matrix dimension
TOTAL_CELLS = N * N  # 16384
print(f"Matrix loaded: {M.shape}, dtype={M.dtype}")
print(f"Value range: [{M.min()}, {M.max()}]")
print()


# ==============================================================================
#  SECTION 1: VERIFY THE SYMMETRY RULE
# ==============================================================================

section_header("1. VERIFY THE SYMMETRY RULE")

# Compute the sum matrix: S[r,c] = M[r,c] + M[127-r, 127-c]
# The "mirror" of M is M flipped along both axes (180-degree rotation).
M_rotated = M[::-1, ::-1]
S = M + M_rotated

symmetric_mask = (S == -1)
n_symmetric = int(symmetric_mask.sum())
n_exceptions = TOTAL_CELLS - n_symmetric
pct_symmetric = 100.0 * n_symmetric / TOTAL_CELLS

print(f"For each cell (r,c), compute: matrix[r,c] + matrix[127-r, 127-c]")
print(f"  Cells where sum == -1 (symmetric): {n_symmetric}")
print(f"  Cells where sum != -1 (exceptions): {n_exceptions}")
print(f"  Symmetry rate: {pct_symmetric:.2f}%")
print()
print(f"Claim verification: 99.58% symmetric")
print(f"  Observed: {pct_symmetric:.2f}%")
print(f"  Match: {'YES' if abs(pct_symmetric - 99.58) < 0.01 else 'CLOSE' if abs(pct_symmetric - 99.58) < 0.1 else 'NO'}")
print()

# Verify that the number of exceptions is even (they must come in pairs)
print(f"Number of exceptions: {n_exceptions}")
print(f"  Is even (required for pairing): {n_exceptions % 2 == 0}")


# ==============================================================================
#  SECTION 2: EXTRACT ALL 68 EXCEPTION CELLS
# ==============================================================================

section_header("2. EXTRACT ALL EXCEPTION CELLS")

exception_cells = []
for r in range(N):
    for c in range(N):
        if S[r, c] != -1:
            exception_cells.append({
                "r": int(r),
                "c": int(c),
                "value": int(M[r, c]),
                "mirror_value": int(M[N - 1 - r, N - 1 - c]),
                "actual_sum": int(S[r, c]),
                "deviation_from_minus1": int(S[r, c] - (-1)),
            })

print(f"Total exception cells found: {len(exception_cells)}")
print()

# Extract unique pairs: (r,c) and (127-r, 127-c) are partners.
# To avoid duplicates, only keep the pair where (r,c) < (127-r, 127-c) lexicographically.
exception_pairs = []
seen = set()
for ex in exception_cells:
    r, c = ex["r"], ex["c"]
    r2, c2 = N - 1 - r, N - 1 - c
    key = (min((r, c), (r2, c2)), max((r, c), (r2, c2)))
    if key not in seen:
        seen.add(key)
        # Find the partner exception data
        partner = None
        for ex2 in exception_cells:
            if ex2["r"] == r2 and ex2["c"] == c2:
                partner = ex2
                break
        exception_pairs.append({
            "cell_A": {"r": r, "c": c, "value": int(M[r, c])},
            "cell_B": {"r": r2, "c": c2, "value": int(M[r2, c2])},
            "sum": int(S[r, c]),
            "deviation": int(S[r, c] - (-1)),
        })

print(f"Unique exception pairs: {len(exception_pairs)}")
print()

# List all pairs
print("All exception pairs:")
print(f"{'#':>3}  {'Cell A':>12}  {'Val A':>6}  {'Cell B':>12}  {'Val B':>6}  {'Sum':>5}  {'Dev':>5}")
print("-" * 70)
for i, pair in enumerate(exception_pairs):
    a = pair["cell_A"]
    b = pair["cell_B"]
    print(f"{i+1:3d}  ({a['r']:3d},{a['c']:3d})  {a['value']:6d}  "
          f"({b['r']:3d},{b['c']:3d})  {b['value']:6d}  {pair['sum']:5d}  {pair['deviation']:+5d}")

print()

# Check for diagonal exceptions (r == c)
diagonal_exceptions = [ex for ex in exception_cells if ex["r"] == ex["c"]]
print(f"Exceptions on the main diagonal (r == c): {len(diagonal_exceptions)}")
if diagonal_exceptions:
    for ex in diagonal_exceptions:
        print(f"  ({ex['r']}, {ex['c']}): value={ex['value']}, "
              f"mirror=({N-1-ex['r']}, {N-1-ex['c']}), sum={ex['actual_sum']}")
else:
    print("  None.")

# Check for anti-diagonal exceptions (r + c == 127)
antidiag_exceptions = [ex for ex in exception_cells if ex["r"] + ex["c"] == N - 1]
print(f"Exceptions on the anti-diagonal (r + c == 127): {len(antidiag_exceptions)}")
if antidiag_exceptions:
    for ex in antidiag_exceptions:
        # On the anti-diagonal, the mirror of (r,c) is (127-r, 127-c).
        # If r+c=127, then 127-r + 127-c = 254 - 127 = 127, so mirror is also on anti-diagonal.
        # Furthermore, the mirror of (r, 127-r) is (127-r, r), which is distinct unless r=63.5.
        print(f"  ({ex['r']}, {ex['c']}): value={ex['value']}, sum={ex['actual_sum']}")


# ==============================================================================
#  SECTION 3: SPATIAL PATTERN OF EXCEPTIONS
# ==============================================================================

section_header("3. SPATIAL PATTERN OF EXCEPTIONS")

exception_rows = [ex["r"] for ex in exception_cells]
exception_cols = [ex["c"] for ex in exception_cells]

row_counts = Counter(exception_rows)
col_counts = Counter(exception_cols)

unique_exception_rows = sorted(row_counts.keys())
unique_exception_cols = sorted(col_counts.keys())

print(f"Rows containing exceptions: {len(unique_exception_rows)}")
print(f"  Rows: {unique_exception_rows}")
print()
print(f"Columns containing exceptions: {len(unique_exception_cols)}")
print(f"  Columns: {unique_exception_cols}")
print()

print("Row histogram (row: count):")
for r in unique_exception_rows:
    bar = "#" * row_counts[r]
    print(f"  Row {r:3d}: {row_counts[r]:2d} {bar}")

print()
print("Column histogram (col: count):")
for c in unique_exception_cols:
    bar = "#" * col_counts[c]
    print(f"  Col {c:3d}: {col_counts[c]:2d} {bar}")

print()

# Clustering analysis: compute the spread of exception positions
# Use the number of distinct rows/cols as a measure of spread
n_distinct_rows = len(unique_exception_rows)
n_distinct_cols = len(unique_exception_cols)

# Also compute the bounding box
row_span = max(exception_rows) - min(exception_rows) if exception_rows else 0
col_span = max(exception_cols) - min(exception_cols) if exception_cols else 0
print(f"Bounding box: rows [{min(exception_rows)}, {max(exception_rows)}] "
      f"(span={row_span}), cols [{min(exception_cols)}, {max(exception_cols)}] (span={col_span})")
print()

# Monte Carlo test: randomly place 34 pairs with point symmetry constraint,
# measure how many distinct rows are occupied. Compare to observed.
print(f"Monte Carlo spatial test ({N_SPATIAL_CONTROLS:,} random placements of 34 pairs)...")
rng = np.random.default_rng(SEED)

observed_n_distinct_rows = n_distinct_rows
observed_n_distinct_cols = n_distinct_cols

control_n_distinct_rows = np.zeros(N_SPATIAL_CONTROLS, dtype=int)
control_n_distinct_cols = np.zeros(N_SPATIAL_CONTROLS, dtype=int)
control_max_per_row = np.zeros(N_SPATIAL_CONTROLS, dtype=int)
control_max_per_col = np.zeros(N_SPATIAL_CONTROLS, dtype=int)

n_pairs = len(exception_pairs)

for trial in range(N_SPATIAL_CONTROLS):
    # Generate 34 random positions for Cell A where (r,c) < (127-r, 127-c)
    # Simplification: pick 34 random cells from the "upper" half
    trial_rows = set()
    trial_cols = set()
    trial_row_counts = Counter()
    trial_col_counts = Counter()

    # Pick 34 random cells (without replacement from the upper-half set)
    # Upper half: all (r,c) where (r,c) < (127-r, 127-c) lexicographically
    # For efficiency, just pick 34 random (r,c) pairs from all 16384 cells
    # and deduplicate with their mirrors (this approximation is fine for spread metrics)
    indices = rng.choice(TOTAL_CELLS, size=n_pairs, replace=False)
    for idx in indices:
        r = idx // N
        c = idx % N
        r2, c2 = N - 1 - r, N - 1 - c

        trial_rows.add(r)
        trial_rows.add(r2)
        trial_cols.add(c)
        trial_cols.add(c2)
        trial_row_counts[r] += 1
        trial_row_counts[r2] += 1
        trial_col_counts[c] += 1
        trial_col_counts[c2] += 1

    control_n_distinct_rows[trial] = len(trial_rows)
    control_n_distinct_cols[trial] = len(trial_cols)
    control_max_per_row[trial] = max(trial_row_counts.values()) if trial_row_counts else 0
    control_max_per_col[trial] = max(trial_col_counts.values()) if trial_col_counts else 0

# Report
report = TestReport(
    title="Point Symmetry Exception Spatial Pattern Tests",
    n_controls=N_SPATIAL_CONTROLS,
    seed=SEED,
    alpha=0.05,
)

report.add_test(
    name="n_distinct_exception_rows",
    null_hypothesis="Exception rows are randomly distributed",
    observed=observed_n_distinct_rows,
    control_values=control_n_distinct_rows,
    alternative="two-sided",
    unit="rows",
)

report.add_test(
    name="n_distinct_exception_cols",
    null_hypothesis="Exception columns are randomly distributed",
    observed=observed_n_distinct_cols,
    control_values=control_n_distinct_cols,
    alternative="two-sided",
    unit="cols",
)

observed_max_per_row = max(row_counts.values()) if row_counts else 0
observed_max_per_col = max(col_counts.values()) if col_counts else 0

report.add_test(
    name="max_exceptions_per_row",
    null_hypothesis="No row has unusually many exceptions",
    observed=observed_max_per_row,
    control_values=control_max_per_row,
    alternative="greater",
    unit="exceptions",
)

report.add_test(
    name="max_exceptions_per_col",
    null_hypothesis="No column has unusually many exceptions",
    observed=observed_max_per_col,
    control_values=control_max_per_col,
    alternative="greater",
    unit="exceptions",
)

report.print_report()


# ==============================================================================
#  SECTION 4: INFORMATION CONTENT CALCULATION
# ==============================================================================

section_header("4. INFORMATION CONTENT CALCULATION")

# Due to point symmetry, the matrix is determined by roughly half its cells.
# The "independent" cells are those (r,c) where (r,c) < (127-r, 127-c),
# plus the 34 exception pairs require both values to be stored.

# Count independent cells
n_independent_half = 0
independent_values = []
for r in range(N):
    for c in range(N):
        r2, c2 = N - 1 - r, N - 1 - c
        if (r, c) < (r2, c2):
            n_independent_half += 1
            independent_values.append(int(M[r, c]))

# For the non-exception cells, knowing one half determines the other.
# For exception cells, both values are needed.
# Total independent values = n_independent_half + n_exception_pairs (the "extra" info from exceptions)
# Actually: n_independent_half already includes cells that are part of exception pairs.
# The symmetry rule determines the mirror for non-exception cells.
# For exception cells, the mirror is NOT determined by the rule, so we need to store both.
# But we already store one side in the independent half. The "extra" info is the 34 deviations.

n_independent_cells = n_independent_half  # One from each pair
# The 34 exception deviations are additional bits needed beyond the symmetry assumption
n_extra_for_exceptions = n_pairs  # 34 deviations needed

print(f"Total cells: {TOTAL_CELLS}")
print(f"Independent half (one from each symmetric pair): {n_independent_half}")
print(f"Exception pairs requiring deviation storage: {n_pairs}")
print()
print(f"If you know the symmetry rule + the independent half + the {n_pairs} deviations,")
print(f"you can reconstruct the entire matrix.")
print()

# Shannon entropy of the independent half
independent_arr = np.array(independent_values)
value_counts = Counter(independent_values)
total_indep = len(independent_arr)
probs = np.array([count / total_indep for count in value_counts.values()])
shannon_entropy = -np.sum(probs * np.log2(probs))
max_entropy = np.log2(len(value_counts))  # uniform over observed values
max_entropy_256 = np.log2(256)  # uniform over all 256 possible byte values

print(f"Independent half value distribution:")
print(f"  Count: {total_indep}")
print(f"  Min: {independent_arr.min()}, Max: {independent_arr.max()}")
print(f"  Mean: {independent_arr.mean():.4f}, Std: {independent_arr.std():.4f}")
print(f"  Unique values: {len(value_counts)}")
print()
print(f"Shannon entropy of independent half:")
print(f"  H = {shannon_entropy:.4f} bits per value")
print(f"  Max entropy (uniform over {len(value_counts)} observed values): {max_entropy:.4f} bits")
print(f"  Max entropy (uniform over 256 byte values): {max_entropy_256:.4f} bits")
print(f"  Efficiency (H / 8.0): {shannon_entropy / 8.0:.4f}")
print()

# Compare to random: generate a random 8192-value sequence with uniform [-128, 127]
rng_info = np.random.default_rng(SEED)
n_info_controls = 1000
control_entropies = np.zeros(n_info_controls)
for i in range(n_info_controls):
    rand_vals = rng_info.integers(-128, 128, size=total_indep)
    rc = Counter(rand_vals.tolist())
    rp = np.array([count / total_indep for count in rc.values()])
    control_entropies[i] = -np.sum(rp * np.log2(rp))

print(f"Comparison to random {total_indep}-value sequences (uniform [-128, 127]):")
print(f"  Anna independent half entropy:  {shannon_entropy:.4f} bits")
print(f"  Random control mean entropy:    {control_entropies.mean():.4f} bits")
print(f"  Random control std:             {control_entropies.std():.4f} bits")
print(f"  Random control range:           [{control_entropies.min():.4f}, {control_entropies.max():.4f}]")
print()

# Total information content
total_bits_needed = total_indep * shannon_entropy + n_pairs * np.log2(256)
total_bits_raw = TOTAL_CELLS * 8
compression_ratio = total_bits_needed / total_bits_raw

print(f"Information content:")
print(f"  Raw matrix storage: {TOTAL_CELLS} cells x 8 bits = {total_bits_raw} bits")
print(f"  With symmetry: {total_indep} independent values x {shannon_entropy:.2f} bits "
      f"+ {n_pairs} deviations x 8 bits = {total_bits_needed:.0f} bits")
print(f"  Compression ratio: {compression_ratio:.4f} ({compression_ratio*100:.2f}%)")


# ==============================================================================
#  SECTION 5: COLUMN SUM CONSEQUENCE PROOF
# ==============================================================================

section_header("5. COLUMN SUM CONSEQUENCE PROOF")

print("THEOREM: If matrix[r,c] + matrix[127-r, 127-c] = -1 for most cells,")
print("then Col[i] + Col[127-i] ~= -128.")
print()
print("PROOF:")
print("  Col[i] = sum_{r=0}^{127} matrix[r, i]")
print("  Col[127-i] = sum_{r=0}^{127} matrix[r, 127-i]")
print()
print("  Substitute r' = 127 - r in the second sum:")
print("  Col[127-i] = sum_{r'=0}^{127} matrix[127-r', 127-i]")
print()
print("  Therefore:")
print("  Col[i] + Col[127-i] = sum_{r=0}^{127} [matrix[r, i] + matrix[127-r, 127-i]]")
print()
print("  For each r, if the point symmetry rule holds at cell (r, i):")
print("    matrix[r, i] + matrix[127-r, 127-i] = -1")
print()
print("  So Col[i] + Col[127-i] = sum_{r=0}^{127} (-1 + delta(r,i))")
print("  where delta(r,i) = 0 if the rule holds at (r,i), else the deviation.")
print()
print("  = -128 + sum of deviations at exceptions in column i and its mirror.")
print()
print("  QED: Column-sum symmetry is a DIRECT CONSEQUENCE of point symmetry.")
print()

# Now compute the exact prediction for each column pair
col_sums = M.sum(axis=0)

print(f"{'Col i':>6} {'Col 127-i':>10} {'Sum_i':>7} {'Sum_{127-i}':>12} {'Actual+':>9} {'Predicted':>10} {'Match':>6}")
print("-" * 70)

col_pair_results = []
for i in range(N // 2):
    j = N - 1 - i
    actual_sum = int(col_sums[i] + col_sums[j])

    # Predicted: -128 + sum of deviations at exceptions in columns i and j
    # Find all exceptions in column i: these are cells (r, i) where S[r, i] != -1
    # The deviation at (r, i) is S[r, i] - (-1) = S[r, i] + 1
    deviation_sum = 0
    for r in range(N):
        if S[r, i] != -1:
            deviation_sum += int(S[r, i] + 1)
        # Note: we only need column i, not column j, because the sum
        # Col[i] + Col[127-i] = sum_r (M[r,i] + M[127-r, 127-i])
        # and each term corresponds to checking S[r,i].
        # S[r,i] = M[r,i] + M[127-r, 127-i], so the exception info is already
        # captured by iterating over all r for column i.

    predicted = -128 + deviation_sum
    match = "YES" if actual_sum == predicted else "NO"

    col_pair_results.append({
        "col_i": i,
        "col_j": j,
        "sum_i": int(col_sums[i]),
        "sum_j": int(col_sums[j]),
        "actual_combined": actual_sum,
        "predicted": predicted,
        "deviation_sum": deviation_sum,
        "match": match,
    })

    print(f"{i:6d} {j:10d} {int(col_sums[i]):7d} {int(col_sums[j]):12d} "
          f"{actual_sum:9d} {predicted:10d} {match:>6}")

all_col_match = all(r["match"] == "YES" for r in col_pair_results)
print()
print(f"All column pairs match prediction: {all_col_match}")
print()
if all_col_match:
    print("CONCLUSION: Column-sum symmetry (Col[i] + Col[127-i] = -128 + exceptions)")
    print("is a PROVEN MATHEMATICAL CONSEQUENCE of point symmetry.")
    print("It is NOT an independent discovery.")
else:
    print("WARNING: Some column pairs do not match. Investigate discrepancies.")


# ==============================================================================
#  SECTION 6: ROW SUM CONSEQUENCE PROOF
# ==============================================================================

section_header("6. ROW SUM CONSEQUENCE PROOF")

print("THEOREM: If matrix[r,c] + matrix[127-r, 127-c] = -1 for most cells,")
print("then Row[r] + Row[127-r] ~= -128.")
print()
print("PROOF (analogous to column proof):")
print("  Row[r] = sum_{c=0}^{127} matrix[r, c]")
print("  Row[127-r] = sum_{c=0}^{127} matrix[127-r, c]")
print()
print("  Substitute c' = 127 - c in the second sum:")
print("  Row[127-r] = sum_{c'=0}^{127} matrix[127-r, 127-c']")
print()
print("  Therefore:")
print("  Row[r] + Row[127-r] = sum_{c=0}^{127} [matrix[r, c] + matrix[127-r, 127-c]]")
print()
print("  = -128 + sum of deviations at exceptions in row r.")
print()
print("  QED: Row-sum symmetry is also a DIRECT CONSEQUENCE of point symmetry.")
print()

row_sums = M.sum(axis=1)

print(f"{'Row r':>6} {'Row 127-r':>10} {'Sum_r':>7} {'Sum_{127-r}':>12} {'Actual+':>9} {'Predicted':>10} {'Match':>6}")
print("-" * 70)

row_pair_results = []
for r in range(N // 2):
    r2 = N - 1 - r
    actual_sum = int(row_sums[r] + row_sums[r2])

    # Predicted: -128 + sum of deviations at exceptions in row r
    deviation_sum = 0
    for c in range(N):
        if S[r, c] != -1:
            deviation_sum += int(S[r, c] + 1)

    predicted = -128 + deviation_sum
    match = "YES" if actual_sum == predicted else "NO"

    row_pair_results.append({
        "row_r": r,
        "row_r2": r2,
        "sum_r": int(row_sums[r]),
        "sum_r2": int(row_sums[r2]),
        "actual_combined": actual_sum,
        "predicted": predicted,
        "deviation_sum": deviation_sum,
        "match": match,
    })

    print(f"{r:6d} {r2:10d} {int(row_sums[r]):7d} {int(row_sums[r2]):12d} "
          f"{actual_sum:9d} {predicted:10d} {match:>6}")

all_row_match = all(r["match"] == "YES" for r in row_pair_results)
print()
print(f"All row pairs match prediction: {all_row_match}")
print()
if all_row_match:
    print("CONCLUSION: Row-sum symmetry (Row[r] + Row[127-r] = -128 + exceptions)")
    print("is a PROVEN MATHEMATICAL CONSEQUENCE of point symmetry.")
    print("It is NOT an independent discovery.")
else:
    print("WARNING: Some row pairs do not match. Investigate discrepancies.")


# ==============================================================================
#  SECTION 7: EXCEPTION VALUE ANALYSIS
# ==============================================================================

section_header("7. EXCEPTION VALUE ANALYSIS")

deviations = [pair["deviation"] for pair in exception_pairs]
sums = [pair["sum"] for pair in exception_pairs]

deviations_arr = np.array(deviations)
sums_arr = np.array(sums)

print(f"Exception pair deviations from -1:")
print(f"  Count: {len(deviations)}")
print(f"  Values: {sorted(deviations)}")
print()
print(f"Statistics of deviations:")
print(f"  Mean: {deviations_arr.mean():.4f}")
print(f"  Std:  {deviations_arr.std():.4f}")
print(f"  Min:  {deviations_arr.min()}")
print(f"  Max:  {deviations_arr.max()}")
print(f"  Sum:  {deviations_arr.sum()}")
print()

print(f"Actual sums (matrix[r,c] + matrix[127-r, 127-c]) at exception pairs:")
print(f"  Values: {sorted(sums)}")
print()

# Distribution of deviation values
deviation_dist = Counter(deviations)
print("Deviation distribution:")
for val in sorted(deviation_dist.keys()):
    count = deviation_dist[val]
    bar = "#" * count
    print(f"  {val:+4d}: {count:3d} {bar}")

print()

# Distribution of actual sums at exceptions
sum_dist = Counter(sums)
print("Actual sum distribution at exceptions:")
for val in sorted(sum_dist.keys()):
    count = sum_dist[val]
    bar = "#" * count
    print(f"  {val:+4d}: {count:3d} {bar}")

print()

# Are deviations symmetric around 0?
positive_devs = sum(1 for d in deviations if d > 0)
negative_devs = sum(1 for d in deviations if d < 0)
zero_devs = sum(1 for d in deviations if d == 0)
print(f"Deviation sign analysis:")
print(f"  Positive: {positive_devs}")
print(f"  Negative: {negative_devs}")
print(f"  Zero:     {zero_devs} (deviation=0 means sum=-1, should not appear here)")
print()

# Check if deviations form any arithmetic or geometric pattern
print("Sorted deviations:")
sorted_devs = sorted(deviations)
print(f"  {sorted_devs}")
print()

# Check differences between consecutive sorted deviations
if len(sorted_devs) > 1:
    diffs = [sorted_devs[i+1] - sorted_devs[i] for i in range(len(sorted_devs)-1)]
    print(f"Consecutive differences in sorted deviations:")
    print(f"  {diffs}")
    print(f"  Unique differences: {sorted(set(diffs))}")
    print()

# Check if any deviation appears exactly twice (as expected from the pairing)
print("Note: Each exception cell (r,c) has deviation S[r,c]+1.")
print("Its mirror (127-r, 127-c) has S[127-r, 127-c] = S[r,c] (same sum).")
print("So exception pairs always share the same deviation value.")
print("The 34 pairs yield 34 deviation values (one per pair).")
print()

# All unique deviations and how many pairs have each
pair_dev_dist = Counter(deviations)
print("How many exception PAIRS have each deviation value:")
for val in sorted(pair_dev_dist.keys()):
    count = pair_dev_dist[val]
    print(f"  Deviation {val:+4d}: {count} pair(s)")


# ==============================================================================
#  SECTION 8: SAVE RESULTS
# ==============================================================================

section_header("8. SAVE RESULTS")

results = {
    "title": "Point Symmetry Deep Analysis of the Anna Matrix",
    "timestamp": datetime.now().isoformat(),
    "seed": SEED,
    "matrix_shape": [N, N],
    "total_cells": TOTAL_CELLS,

    "section_1_symmetry_verification": {
        "n_symmetric_cells": n_symmetric,
        "n_exception_cells": n_exceptions,
        "symmetry_percentage": round(pct_symmetric, 4),
        "claim_99_58_verified": abs(pct_symmetric - 99.58) < 0.1,
    },

    "section_2_exceptions": {
        "n_exception_cells": n_exceptions,
        "n_unique_pairs": len(exception_pairs),
        "pairs": exception_pairs,
        "diagonal_exceptions": len(diagonal_exceptions),
        "antidiagonal_exceptions": len(antidiag_exceptions),
    },

    "section_3_spatial_pattern": {
        "n_distinct_exception_rows": n_distinct_rows,
        "n_distinct_exception_cols": n_distinct_cols,
        "exception_rows": unique_exception_rows,
        "exception_cols": unique_exception_cols,
        "row_histogram": {str(k): v for k, v in sorted(row_counts.items())},
        "col_histogram": {str(k): v for k, v in sorted(col_counts.items())},
        "bounding_box": {
            "row_min": min(exception_rows),
            "row_max": max(exception_rows),
            "row_span": row_span,
            "col_min": min(exception_cols),
            "col_max": max(exception_cols),
            "col_span": col_span,
        },
        "monte_carlo_tests": {
            "n_controls": N_SPATIAL_CONTROLS,
            "observed_distinct_rows": observed_n_distinct_rows,
            "control_mean_distinct_rows": float(control_n_distinct_rows.mean()),
            "control_std_distinct_rows": float(control_n_distinct_rows.std()),
            "observed_distinct_cols": observed_n_distinct_cols,
            "control_mean_distinct_cols": float(control_n_distinct_cols.mean()),
            "control_std_distinct_cols": float(control_n_distinct_cols.std()),
        },
    },

    "section_4_information_content": {
        "n_independent_half": n_independent_half,
        "n_extra_for_exceptions": n_pairs,
        "shannon_entropy_bits": round(float(shannon_entropy), 4),
        "max_entropy_observed_values": round(float(max_entropy), 4),
        "max_entropy_256_values": round(float(max_entropy_256), 4),
        "independent_half_stats": {
            "mean": round(float(independent_arr.mean()), 4),
            "std": round(float(independent_arr.std()), 4),
            "min": int(independent_arr.min()),
            "max": int(independent_arr.max()),
            "unique_values": len(value_counts),
        },
        "control_entropy_mean": round(float(control_entropies.mean()), 4),
        "control_entropy_std": round(float(control_entropies.std()), 4),
        "total_bits_with_symmetry": round(float(total_bits_needed), 0),
        "total_bits_raw": total_bits_raw,
        "compression_ratio": round(float(compression_ratio), 4),
    },

    "section_5_column_sum_proof": {
        "all_predictions_match": all_col_match,
        "conclusion": (
            "Column-sum symmetry is a proven mathematical consequence of point symmetry"
            if all_col_match else
            "Discrepancies found - requires investigation"
        ),
        "column_pairs": col_pair_results,
    },

    "section_6_row_sum_proof": {
        "all_predictions_match": all_row_match,
        "conclusion": (
            "Row-sum symmetry is a proven mathematical consequence of point symmetry"
            if all_row_match else
            "Discrepancies found - requires investigation"
        ),
        "row_pairs": row_pair_results,
    },

    "section_7_exception_values": {
        "deviations": deviations,
        "deviation_stats": {
            "mean": round(float(deviations_arr.mean()), 4),
            "std": round(float(deviations_arr.std()), 4),
            "min": int(deviations_arr.min()),
            "max": int(deviations_arr.max()),
            "sum": int(deviations_arr.sum()),
        },
        "deviation_distribution": {str(k): v for k, v in sorted(deviation_dist.items())},
        "sum_distribution": {str(k): v for k, v in sorted(sum_dist.items())},
        "positive_deviations": positive_devs,
        "negative_deviations": negative_devs,
    },

    "key_conclusions": [
        f"Point symmetry holds for {pct_symmetric:.2f}% of cells ({n_symmetric}/{TOTAL_CELLS})",
        f"{n_exceptions} exception cells form {len(exception_pairs)} mirror pairs",
        "Column-sum symmetry (Col[i] + Col[127-i] = -128) is a CONSEQUENCE of point symmetry, not independent",
        "Row-sum symmetry (Row[r] + Row[127-r] = -128) is a CONSEQUENCE of point symmetry, not independent",
        f"Matrix information content is ~{compression_ratio*100:.1f}% of raw storage due to symmetry",
        f"Shannon entropy of independent half: {shannon_entropy:.4f} bits/value",
    ],
}

with open(OUTPUT_JSON, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {OUTPUT_JSON}")
print()

# Final summary
print("=" * 80)
print("  FINAL SUMMARY")
print("=" * 80)
print()
for i, conclusion in enumerate(results["key_conclusions"], 1):
    print(f"  {i}. {conclusion}")
print()
print("Analysis complete.")
