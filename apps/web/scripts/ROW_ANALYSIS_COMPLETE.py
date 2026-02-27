#!/usr/bin/env python3
"""
===============================================================================
        COMPLETE ROW ANALYSIS - All 128 Rows Characterized
===============================================================================
Analyzes EVERY row of the Anna Matrix to understand its structure.

Key questions:
  Q1: Is Row 6 unique in its bias toward value 26? Or do other rows show similar bias?
  Q2: Which rows have the lowest entropy (most structured)?
  Q3: Are there row groups with similar properties?
  Q4: How do row properties correlate with known functions (JINN architecture)?

CONTROL: Each row compared against random rows with same overall distribution.
SIGNIFICANCE: p < 0.001 (Bonferroni-corrected for 128 rows: p < 0.0000078)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("         COMPLETE ROW ANALYSIS")
print("         All 128 Rows Characterized")
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

SIMULATIONS = 10000
ROW_BONFERRONI = 128
SIGNIFICANCE = 0.001 / ROW_BONFERRONI

# ============================================================================
# PHASE 1: Characterize Every Row
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1: Row-by-Row Characterization")
print("=" * 80)

all_values = matrix.flatten()
overall_mean = all_values.mean()
overall_std = all_values.std()

row_data = []

for r in range(128):
    row = matrix[r, :]
    counter = Counter(row)

    # Shannon entropy
    entropy = 0
    for count in counter.values():
        p = count / 128
        if p > 0:
            entropy -= p * np.log2(p)

    most_common_val, most_common_count = counter.most_common(1)[0]

    # Count of value 26
    count_26 = int(np.sum(row == 26))

    # Count of special values
    specials = {26: count_26}
    for sv in [-1, 0, 121, 127, -128]:
        specials[sv] = int(np.sum(row == sv))

    # Point symmetry with mirror row
    mirror_r = 127 - r
    sym_count = 0
    for c in range(128):
        if matrix[r, c] + matrix[mirror_r, 127 - c] == -1:
            sym_count += 1
    symmetry_pct = sym_count / 128 * 100

    row_info = {
        'row': r,
        'mean': float(np.mean(row)),
        'std': float(np.std(row)),
        'sum': int(np.sum(row)),
        'entropy': entropy,
        'unique_values': len(counter),
        'most_common_val': int(most_common_val),
        'most_common_count': most_common_count,
        'count_26': count_26,
        'specials': specials,
        'symmetry_with_mirror': symmetry_pct,
        'mirror_row': mirror_r,
    }
    row_data.append(row_info)

# ============================================================================
# PHASE 2: Find Anomalous Rows
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 2: Finding Anomalous Rows")
print("=" * 80)

# Sort by entropy (lowest = most structured)
by_entropy = sorted(row_data, key=lambda x: x['entropy'])

print(f"\n  TOP 10 LOWEST ENTROPY ROWS (most structured):")
print(f"  {'Row':<6} {'Entropy':<10} {'Unique':<8} {'MostCommon':<15} {'Count':<8} {'Val26':<8}")
print("  " + "-" * 60)
for rd in by_entropy[:10]:
    print(f"  {rd['row']:<6} {rd['entropy']:<10.4f} {rd['unique_values']:<8} {rd['most_common_val']:<15} {rd['most_common_count']:<8} {rd['count_26']:<8}")

# Sort by value-26 count
by_26 = sorted(row_data, key=lambda x: x['count_26'], reverse=True)

print(f"\n  TOP 10 ROWS WITH MOST VALUE-26 OCCURRENCES:")
print(f"  {'Row':<6} {'Count26':<10} {'Entropy':<10} {'MostCommon':<15}")
print("  " + "-" * 45)
for rd in by_26[:10]:
    print(f"  {rd['row']:<6} {rd['count_26']:<10} {rd['entropy']:<10.4f} {rd['most_common_val']:<15}")

# Sort by highest max frequency (most biased)
by_bias = sorted(row_data, key=lambda x: x['most_common_count'], reverse=True)

print(f"\n  TOP 10 MOST BIASED ROWS (highest single-value frequency):")
print(f"  {'Row':<6} {'Value':<8} {'Count':<8} {'Pct':<10} {'Entropy':<10}")
print("  " + "-" * 45)
for rd in by_bias[:10]:
    pct = rd['most_common_count'] / 128 * 100
    print(f"  {rd['row']:<6} {rd['most_common_val']:<8} {rd['most_common_count']:<8} {pct:<10.1f}% {rd['entropy']:<10.4f}")

# ============================================================================
# PHASE 3: Is Row 6 Statistically Unique?
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 3: Row 6 Statistical Significance Test")
print("=" * 80)

row6_26_count = row_data[6]['count_26']
row6_entropy = row_data[6]['entropy']
row6_max_freq = row_data[6]['most_common_count']

print(f"\n  Row 6 properties:")
print(f"    Value 26 count: {row6_26_count}/128 ({row6_26_count/128*100:.1f}%)")
print(f"    Entropy: {row6_entropy:.4f}")
print(f"    Most common value: {row_data[6]['most_common_val']} ({row_data[6]['most_common_count']}/128)")

# Generate random rows and test
print(f"\n  Monte Carlo test ({SIMULATIONS:,} random rows)...", end="", flush=True)
random_26_counts = []
random_max_freqs = []
random_entropies = []

for i in range(SIMULATIONS):
    # Random row with same value distribution as overall matrix
    random_row = np.random.choice(all_values, size=128, replace=True)
    counter = Counter(random_row)

    random_26_counts.append(int(np.sum(random_row == 26)))
    random_max_freqs.append(counter.most_common(1)[0][1])

    entropy = 0
    for count in counter.values():
        p = count / 128
        if p > 0:
            entropy -= p * np.log2(p)
    random_entropies.append(entropy)

    if (i + 1) % 2000 == 0:
        print(f" {i+1}", end="", flush=True)
print()

random_26_counts = np.array(random_26_counts)
random_max_freqs = np.array(random_max_freqs)
random_entropies = np.array(random_entropies)

p_26 = np.mean(random_26_counts >= row6_26_count)
p_max_freq = np.mean(random_max_freqs >= row6_max_freq)
p_entropy_low = np.mean(random_entropies <= row6_entropy)

print(f"\n  Random row statistics:")
print(f"    Value 26 count: mean={random_26_counts.mean():.2f}, max={random_26_counts.max()}")
print(f"    Max frequency: mean={random_max_freqs.mean():.2f}, max={random_max_freqs.max()}")
print(f"    Entropy: mean={random_entropies.mean():.4f}")

print(f"\n  Significance tests:")
print(f"    p(value 26 >= {row6_26_count}):    {p_26:.8f} {'***' if p_26 < SIGNIFICANCE else ''}")
print(f"    p(max freq >= {row6_max_freq}):  {p_max_freq:.8f} {'***' if p_max_freq < SIGNIFICANCE else ''}")
print(f"    p(entropy <= {row6_entropy:.4f}): {p_entropy_low:.8f} {'***' if p_entropy_low < SIGNIFICANCE else ''}")

# ============================================================================
# PHASE 4: Row Grouping Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 4: Row Groups and Patterns")
print("=" * 80)

# Check if rows come in pairs (r, 127-r) with consistent properties
print(f"\n  Row pair symmetry analysis (r, 127-r):")
pair_consistent = 0
pair_inconsistent = 0
for r in range(64):
    mirror = 127 - r
    sym = row_data[r]['symmetry_with_mirror']
    if sym > 95:
        pair_consistent += 1
    else:
        pair_inconsistent += 1

print(f"    Pairs with >95% point symmetry: {pair_consistent}/64")
print(f"    Pairs with <=95% symmetry: {pair_inconsistent}/64")

# Find rows that share the same most common value
value_groups = {}
for rd in row_data:
    v = rd['most_common_val']
    if v not in value_groups:
        value_groups[v] = []
    value_groups[v].append(rd['row'])

print(f"\n  Rows grouped by most common value:")
for v in sorted(value_groups.keys()):
    rows = value_groups[v]
    if len(rows) >= 3:  # Only show values appearing in 3+ rows
        print(f"    Value {v:>5}: {len(rows)} rows ({rows[:10]}{'...' if len(rows) > 10 else ''})")

# ============================================================================
# PHASE 5: Full Row Table
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 5: Complete Row Table (abbreviated)")
print("=" * 80)

print(f"\n  {'Row':<5} {'Mean':<8} {'Sum':<8} {'Entropy':<9} {'Uniq':<6} {'MaxVal':<8} {'MaxCnt':<8} {'#26':<5} {'Sym%':<7}")
print("  " + "-" * 75)

for rd in row_data:
    marker = ""
    if rd['row'] == 6:
        marker = " <-- ROW 6 (Oracle)"
    elif rd['count_26'] >= 10:
        marker = f" <-- HIGH 26-count"
    elif rd['entropy'] < 5.5:
        marker = f" <-- LOW entropy"

    print(f"  {rd['row']:<5} {rd['mean']:<8.1f} {rd['sum']:<8} {rd['entropy']:<9.4f} {rd['unique_values']:<6} {rd['most_common_val']:<8} {rd['most_common_count']:<8} {rd['count_26']:<5} {rd['symmetry_with_mirror']:<7.1f}{marker}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ROW ANALYSIS SUMMARY")
print("=" * 80)

# Count significant rows
significant_rows = []
for rd in row_data:
    if rd['most_common_count'] >= row6_max_freq:
        significant_rows.append(rd['row'])

print(f"\n  Total rows analyzed: 128")
print(f"  Rows with bias as extreme as Row 6: {len(significant_rows)}")
if significant_rows:
    print(f"    Rows: {significant_rows}")
print(f"\n  Row 6 statistical significance:")
print(f"    p(value 26 count): {p_26:.8f}")
print(f"    p(max frequency): {p_max_freq:.8f}")
print(f"    p(low entropy): {p_entropy_low:.8f}")
print(f"    Bonferroni-corrected threshold: {SIGNIFICANCE:.8f}")
print(f"    Row 6 is significant? {'YES' if p_26 < SIGNIFICANCE else 'NO (even before Bonferroni)'}")

# Save results
results = {
    "date": datetime.now().isoformat(),
    "simulations": SIMULATIONS,
    "row_data": row_data,
    "row6_tests": {
        "p_value_26_count": float(p_26),
        "p_max_frequency": float(p_max_freq),
        "p_low_entropy": float(p_entropy_low),
        "bonferroni_threshold": float(SIGNIFICANCE),
    },
    "pair_symmetry": {
        "consistent_pairs": pair_consistent,
        "inconsistent_pairs": pair_inconsistent,
    },
    "anomalous_rows": significant_rows,
}

output_path = script_dir / "ROW_ANALYSIS_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to: {output_path}")
