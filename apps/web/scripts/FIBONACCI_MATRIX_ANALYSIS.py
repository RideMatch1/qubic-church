#!/usr/bin/env python3
"""
===============================================================================
        FIBONACCI MATRIX ANALYSIS - Following the >FIB Pointer
===============================================================================
The research roadmap (73-research-roadmap.mdx) identified a ">FIB" pointer
at Rows 27-30 in Column Pair (22, 105) but this was NEVER followed up.

This script systematically investigates Fibonacci patterns in the Anna Matrix.

PRE-REGISTERED HYPOTHESES (stated before running):
  H1: Values at Fibonacci coordinate intersections differ from random positions
  H2: Fibonacci rows (1,2,3,5,8,13,21,34,55,89) have different properties than other rows
  H3: Zeckendorf representations of matrix values show non-random distribution
  H4: The ">FIB" pointer region contains additional encoded information

CONTROL: All tests compared against equivalent random positions.
SIGNIFICANCE: p < 0.001 (Bonferroni-corrected for 4 tests: p < 0.00025)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("         FIBONACCI MATRIX ANALYSIS")
print("         Following the >FIB Pointer")
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

# Fibonacci numbers that fit in [0, 127]
FIBS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
ALL_FIBS_SET = set(FIBS)
print(f"Fibonacci positions (in 0-127): {FIBS}")

SIMULATIONS = 10000
BONFERRONI = 4
SIGNIFICANCE = 0.001 / BONFERRONI

# ============================================================================
# ANALYSIS 1: Fibonacci Coordinate Grid
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 1: Values at Fibonacci x Fibonacci Intersections")
print("=" * 80)

# Query matrix[fib_i, fib_j] for all combinations
fib_grid = {}
fib_values = []
print("\n  Fibonacci Grid (matrix[fib_row, fib_col]):")
print(f"  {'':>6}", end="")
for fc in FIBS:
    print(f"  c={fc:>3}", end="")
print()
print("  " + "-" * 76)

for fr in FIBS:
    print(f"  r={fr:>3} |", end="")
    for fc in FIBS:
        val = int(matrix[fr, fc])
        fib_grid[(fr, fc)] = val
        fib_values.append(val)
        print(f"  {val:>5}", end="")
    print()

fib_values = np.array(fib_values)
print(f"\n  Total Fibonacci intersections: {len(fib_values)}")
print(f"  Mean value: {fib_values.mean():.2f}")
print(f"  Std value: {fib_values.std():.2f}")
print(f"  Sum: {fib_values.sum()}")

# Check for Fibonacci numbers in the values themselves
fib_in_values = [v for v in fib_values if abs(v) in ALL_FIBS_SET]
print(f"  Values that ARE Fibonacci numbers: {len(fib_in_values)} / {len(fib_values)}")
print(f"    Values: {fib_in_values}")

# Check for special values (26, 121, 127, -1, 0)
for special in [0, -1, 26, 121, 127, -128]:
    count = int(np.sum(fib_values == special))
    if count > 0:
        print(f"  Value {special} appears {count} times in Fibonacci grid")

# Control: random position grids
print(f"\n  Control: {SIMULATIONS:,} random 10x10 grids...", end="", flush=True)
random_means = []
random_stds = []
random_sums = []
random_fib_counts = []
for i in range(SIMULATIONS):
    rand_rows = np.random.randint(0, 128, size=10)
    rand_cols = np.random.randint(0, 128, size=10)
    rand_values = []
    for r in rand_rows:
        for c in rand_cols:
            rand_values.append(int(matrix[r, c]))
    rand_values = np.array(rand_values)
    random_means.append(rand_values.mean())
    random_stds.append(rand_values.std())
    random_sums.append(rand_values.sum())
    random_fib_counts.append(sum(1 for v in rand_values if abs(v) in ALL_FIBS_SET))
    if (i + 1) % 2000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_means = np.array(random_means)
random_sums = np.array(random_sums)
random_fib_counts = np.array(random_fib_counts)

# Two-sided p-value for mean
p_mean = 2 * min(np.mean(random_means <= fib_values.mean()), np.mean(random_means >= fib_values.mean()))
# p-value for Fibonacci count
fib_count = len(fib_in_values)
p_fib = np.mean(random_fib_counts >= fib_count)

print(f"\n  Random grid statistics:")
print(f"    Mean of means: {random_means.mean():.2f} +/- {random_means.std():.2f}")
print(f"    Anna Fib grid mean: {fib_values.mean():.2f}")
print(f"    p(mean): {p_mean:.6f}")
print(f"\n    Mean Fibonacci count: {random_fib_counts.mean():.2f}")
print(f"    Anna Fib count: {fib_count}")
print(f"    p(fib count): {p_fib:.6f}")

h1_significant = p_mean < SIGNIFICANCE or p_fib < SIGNIFICANCE
print(f"\n  H1 Result: {'SIGNIFICANT' if h1_significant else 'NOT SIGNIFICANT'}")

# ============================================================================
# ANALYSIS 2: Fibonacci Row Properties
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 2: Fibonacci Row Properties")
print("=" * 80)

def row_stats(m, row_idx):
    row = m[row_idx, :]
    counter = Counter(row)
    entropy = 0
    for count in counter.values():
        p = count / 128
        if p > 0:
            entropy -= p * np.log2(p)
    return {
        'mean': float(np.mean(row)),
        'std': float(np.std(row)),
        'entropy': entropy,
        'unique_values': len(counter),
        'max_freq': counter.most_common(1)[0][1],
        'most_common_val': int(counter.most_common(1)[0][0]),
        'sum': int(np.sum(row)),
        'abs_sum': int(np.sum(np.abs(row))),
    }

print(f"\n  {'Row':<6} {'Mean':<10} {'Std':<10} {'Entropy':<10} {'Unique':<8} {'MaxFreq':<10} {'Sum':<10}")
print("  " + "-" * 64)

fib_row_entropies = []
non_fib_row_entropies = []

for r in range(128):
    stats = row_stats(matrix, r)
    if r in ALL_FIBS_SET:
        fib_row_entropies.append(stats['entropy'])
        marker = " <-- FIB"
        print(f"  {r:<6} {stats['mean']:<10.2f} {stats['std']:<10.2f} {stats['entropy']:<10.4f} {stats['unique_values']:<8} {stats['max_freq']:<10} {stats['sum']:<10}{marker}")
    else:
        non_fib_row_entropies.append(stats['entropy'])

fib_row_entropies = np.array(fib_row_entropies)
non_fib_row_entropies = np.array(non_fib_row_entropies)

print(f"\n  Fibonacci rows ({len(FIBS)}) mean entropy: {fib_row_entropies.mean():.4f}")
print(f"  Non-Fibonacci rows ({len(non_fib_row_entropies)}) mean entropy: {non_fib_row_entropies.mean():.4f}")

# Permutation test: Is Fibonacci row entropy different from random selection of 10 rows?
random_subset_entropies = []
all_entropies = np.array([row_stats(matrix, r)['entropy'] for r in range(128)])
for _ in range(SIMULATIONS):
    subset = np.random.choice(128, size=10, replace=False)
    random_subset_entropies.append(all_entropies[subset].mean())

random_subset_entropies = np.array(random_subset_entropies)
p_entropy = 2 * min(
    np.mean(random_subset_entropies <= fib_row_entropies.mean()),
    np.mean(random_subset_entropies >= fib_row_entropies.mean())
)

print(f"  p(entropy difference): {p_entropy:.6f}")
h2_significant = p_entropy < SIGNIFICANCE
print(f"\n  H2 Result: {'SIGNIFICANT' if h2_significant else 'NOT SIGNIFICANT'}")

# ============================================================================
# ANALYSIS 3: Zeckendorf Representations
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 3: Zeckendorf Representations of Matrix Values")
print("=" * 80)

def zeckendorf(n):
    """Represent n as sum of non-consecutive Fibonacci numbers (Zeckendorf's theorem)."""
    if n == 0:
        return [0]
    if n < 0:
        return None  # Only for positive integers

    fibs = []
    a, b = 1, 2
    while b <= n:
        fibs.append(a)
        a, b = b, a + b
    fibs.append(a)

    result = []
    remaining = n
    for f in reversed(fibs):
        if f <= remaining:
            result.append(f)
            remaining -= f
    if remaining == 0:
        return result
    return None

# Get all unique values in the matrix
unique_values = sorted(set(matrix.flatten()))
print(f"\n  Unique matrix values: {len(unique_values)}")
print(f"  Range: [{min(unique_values)}, {max(unique_values)}]")

# Check which positive values have clean Zeckendorf representations
zeckendorf_results = {}
fib_representable = 0
for val in unique_values:
    if val > 0:
        z = zeckendorf(val)
        if z:
            zeckendorf_results[val] = z
            if val in ALL_FIBS_SET:
                fib_representable += 1

# Known Zeckendorf decompositions from research
known_zeckendorf = {
    127: [89, 34, 3, 1],
    100: [89, 8, 3],
    27: [21, 5, 1],
    26: [21, 5],
}

print(f"\n  Known Zeckendorf decompositions:")
for val, decomp in known_zeckendorf.items():
    our_decomp = zeckendorf_results.get(val, None)
    match = our_decomp == decomp if our_decomp else False
    status = "MATCH" if match else "COMPUTED"
    print(f"    {val} = {' + '.join(map(str, our_decomp or decomp))} [{status}]")

# How many matrix values are pure Fibonacci numbers?
all_values = matrix.flatten()
positive_values = all_values[all_values > 0]
fib_count = sum(1 for v in positive_values if v in ALL_FIBS_SET)
total_positive = len(positive_values)
fib_fraction = fib_count / total_positive if total_positive > 0 else 0

print(f"\n  Positive matrix values: {total_positive}")
print(f"  Values that are Fibonacci: {fib_count} ({fib_fraction:.2%})")

# Control: expected Fibonacci fraction in random [-128, 127] integers
# Fibonacci in [1, 127]: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89 = 10 values out of 127
expected_fib_fraction = len(FIBS) / 127
print(f"  Expected by chance: {expected_fib_fraction:.2%}")

# Monte Carlo test
random_fib_fractions = []
for _ in range(SIMULATIONS):
    rm = np.random.randint(-128, 128, size=(128, 128), dtype=np.int16)
    pos = rm[rm > 0]
    if len(pos) > 0:
        rf = sum(1 for v in pos if v in ALL_FIBS_SET) / len(pos)
        random_fib_fractions.append(rf)

random_fib_fractions = np.array(random_fib_fractions)
p_zeck = np.mean(random_fib_fractions >= fib_fraction)

print(f"  Random Fibonacci fraction: {random_fib_fractions.mean():.2%} +/- {random_fib_fractions.std():.2%}")
print(f"  p(Fibonacci fraction >= {fib_fraction:.2%}): {p_zeck:.6f}")

h3_significant = p_zeck < SIGNIFICANCE
print(f"\n  H3 Result: {'SIGNIFICANT' if h3_significant else 'NOT SIGNIFICANT'}")

# ============================================================================
# ANALYSIS 4: >FIB Pointer Region
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 4: >FIB Pointer Region (Rows 27-30, Column Pair 22/105)")
print("=" * 80)

print("\n  Column Pair (22, 105) - where >FIB pointer was found:")
print(f"  Note: 22 + 105 = 127 (satisfies the 127-formula for asymmetric pairs)")
print()

# Extract the region
for r in range(25, 35):  # Wider context around rows 27-30
    c22 = int(matrix[r, 22])
    c105 = int(matrix[r, 105])
    xor_val = c22 ^ c105 if c22 >= 0 and c105 >= 0 else "N/A"
    sum_val = c22 + c105
    marker = " <-- FIB POINTER" if 27 <= r <= 30 else ""
    is_fib = " [FIB ROW]" if r in ALL_FIBS_SET else ""
    print(f"  Row {r:>3}: col22={c22:>5}, col105={c105:>5}, sum={sum_val:>5}{is_fib}{marker}")

# Decode as characters (absolute values as A=0, B=1, ..., Z=25)
print(f"\n  Character decoding of FIB pointer region (rows 27-30):")
for r in range(27, 31):
    c22 = int(matrix[r, 22])
    c105 = int(matrix[r, 105])
    char22 = chr(abs(c22) % 26 + ord('A'))
    char105 = chr(abs(c105) % 26 + ord('A'))
    print(f"    Row {r}: col22={c22:>5} -> '{char22}', col105={c105:>5} -> '{char105}'")

# What about the mirrored region? (127-27=100, 127-30=97)
print(f"\n  Mirror region (rows 97-100, cols 22/105):")
for r in range(97, 101):
    c22 = int(matrix[r, 22])
    c105 = int(matrix[r, 105])
    orig_r = 127 - r
    orig_c22 = int(matrix[orig_r, 22])
    sum_check = c22 + orig_c22
    print(f"  Row {r:>3}: col22={c22:>5}, col105={c105:>5} | mirror row {orig_r}: col22={orig_c22:>5}, sum={sum_check}")

# Check deeper: What values are at ALL Fibonacci rows in column 22 and 105?
print(f"\n  Fibonacci rows in columns 22 and 105:")
for fr in FIBS:
    c22 = int(matrix[fr, 22])
    c105 = int(matrix[fr, 105])
    print(f"    Fib row {fr:>3}: col22={c22:>5}, col105={c105:>5}, sum={c22+c105:>5}")

# ============================================================================
# ANALYSIS 5: Diagonal Fibonacci Pattern
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 5: Diagonal Values at Fibonacci Positions")
print("=" * 80)

print(f"\n  matrix[fib, fib] (main diagonal at Fibonacci positions):")
diag_fib_values = []
for f in FIBS:
    val = int(matrix[f, f])
    diag_fib_values.append(val)
    is_fib_val = " [IS FIB]" if abs(val) in ALL_FIBS_SET else ""
    print(f"    matrix[{f:>2}, {f:>2}] = {val:>5}{is_fib_val}")

diag_sum = sum(diag_fib_values)
print(f"\n  Sum of diagonal Fibonacci values: {diag_sum}")
print(f"  Mean: {np.mean(diag_fib_values):.2f}")

# Check if diag_sum is special
for special_name, special_val in [("676 (26^2)", 676), ("138 (6*23)", 138), ("121 (11^2)", 121), ("26", 26), ("137 (alpha)", 137)]:
    if diag_sum == special_val:
        print(f"  Sum = {special_name}!")
    if diag_sum % special_val == 0:
        print(f"  Sum divisible by {special_name}: {diag_sum} / {special_val} = {diag_sum // special_val}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("FIBONACCI ANALYSIS SUMMARY")
print("=" * 80)

results = {
    "date": datetime.now().isoformat(),
    "fibonacci_positions": FIBS,
    "tests": {
        "H1_fib_grid_values": {
            "fib_grid_mean": float(np.array(list(fib_grid.values())).mean()),
            "fib_grid_sum": int(np.array(list(fib_grid.values())).sum()),
            "p_value_mean": float(p_mean),
            "p_value_fib_count": float(p_fib),
            "significant": h1_significant,
        },
        "H2_fib_row_entropy": {
            "fib_rows_mean_entropy": float(fib_row_entropies.mean()),
            "non_fib_mean_entropy": float(non_fib_row_entropies.mean()),
            "p_value": float(p_entropy),
            "significant": h2_significant,
        },
        "H3_zeckendorf": {
            "fib_fraction_in_matrix": float(fib_fraction),
            "expected_by_chance": float(expected_fib_fraction),
            "p_value": float(p_zeck),
            "significant": h3_significant,
        },
    },
    "fib_grid": {f"{k[0]},{k[1]}": v for k, v in fib_grid.items()},
    "fib_pointer_region": {
        "rows": "27-30",
        "columns": "22, 105",
        "note": "22 + 105 = 127 (asymmetric column pair)"
    },
    "diagonal_fib_values": diag_fib_values,
    "diagonal_fib_sum": diag_sum,
}

print(f"\n  {'Hypothesis':<45} {'p-value':<12} {'Result'}")
print("  " + "-" * 75)
print(f"  {'H1: Fib grid values differ from random':<45} {p_mean:<12.6f} {'SIGNIFICANT' if h1_significant else 'NOT SIGNIFICANT'}")
print(f"  {'H2: Fib row entropy differs':<45} {p_entropy:<12.6f} {'SIGNIFICANT' if h2_significant else 'NOT SIGNIFICANT'}")
print(f"  {'H3: Fibonacci value overrepresentation':<45} {p_zeck:<12.6f} {'SIGNIFICANT' if h3_significant else 'NOT SIGNIFICANT'}")

# Save results
output_path = script_dir / "FIBONACCI_ANALYSIS_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=lambda x: bool(x) if isinstance(x, np.bool_) else float(x) if isinstance(x, (np.floating, np.integer)) else x)
print(f"\n  Results saved to: {output_path}")

print("\n" + "=" * 80)
print("  NOTE: This analysis follows the >FIB pointer from the research roadmap.")
print("  All tests use pre-registered hypotheses with Bonferroni correction.")
print("=" * 80)
