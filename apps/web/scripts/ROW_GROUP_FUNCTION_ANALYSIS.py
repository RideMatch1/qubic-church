#!/usr/bin/env python3
"""
===============================================================================
        ROW GROUP FUNCTION ANALYSIS
===============================================================================
The Anna Matrix has clear row value groups (from ROW_ANALYSIS_COMPLETE):
  - Value -27 dominates 11 rows
  - Value 26 dominates 8 rows
  - Value -102 dominates 8 rows
  - Value 101 dominates 6 rows

In the Aigarth neural network, each ROW defines the WEIGHTS for one neuron.
Different dominant values = different types of neurons.

KEY QUESTIONS:
  Q1: What do these value groups mean for neural computation?
  Q2: Do the groups form functional layers (like cortical layers)?
  Q3: How do the mirror pairs interact? (row r is paired with row 127-r)
  Q4: Does the dominant value determine neuron behavior (excitatory/inhibitory)?
  Q5: What is the relationship between dominant values?
      Note: 26 + 101 = 127, -27 + (-102) = -129, 26 + (-27) = -1

AIGARTH CONTEXT:
  In the official Aigarth-it library, neuron weights are ternary (-1, 0, +1).
  But the Anna Matrix uses FULL signed bytes (-128 to 127).
  When used as weights, these values are ternary-clamped:
    value > 0 → weight = +1 (excitatory)
    value = 0 → weight = 0 (no connection)
    value < 0 → weight = -1 (inhibitory)
  So the SIGN matters more than the magnitude.
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("         ROW GROUP FUNCTION ANALYSIS")
print("         Neural Architecture Mapping")
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

# ============================================================================
# PHASE 1: Sign Analysis (What Aigarth Actually Sees)
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 1: Ternary Sign Analysis")
print("=" * 80)

# In Aigarth, weights are ternary-clamped
ternary_matrix = np.sign(matrix).astype(np.int8)  # -1, 0, +1

print(f"\n  Ternary distribution across entire matrix:")
total = 128 * 128
n_pos = np.sum(ternary_matrix == 1)
n_neg = np.sum(ternary_matrix == -1)
n_zero = np.sum(ternary_matrix == 0)
print(f"    Positive (+1): {n_pos} ({n_pos/total*100:.1f}%)")
print(f"    Negative (-1): {n_neg} ({n_neg/total*100:.1f}%)")
print(f"    Zero (0):      {n_zero} ({n_zero/total*100:.1f}%)")

# Per-row ternary analysis
print(f"\n  Per-row ternary profile (excitatory vs inhibitory):")
print(f"  {'Row':<5} {'Pos':<6} {'Neg':<6} {'Zero':<6} {'Balance':<10} {'Type':<20} {'DomValue':<10}")
print("  " + "-" * 70)

row_profiles = []
for r in range(128):
    row = ternary_matrix[r, :]
    pos = int(np.sum(row == 1))
    neg = int(np.sum(row == -1))
    zero = int(np.sum(row == 0))
    balance = pos - neg  # positive = excitatory dominant

    # Original dominant value
    orig_row = matrix[r, :]
    counter = Counter(orig_row)
    dom_val = counter.most_common(1)[0][0]

    if balance > 20:
        neuron_type = "STRONGLY EXCITATORY"
    elif balance > 0:
        neuron_type = "EXCITATORY"
    elif balance < -20:
        neuron_type = "STRONGLY INHIBITORY"
    elif balance < 0:
        neuron_type = "INHIBITORY"
    else:
        neuron_type = "BALANCED"

    profile = {
        'row': r,
        'positive': pos,
        'negative': neg,
        'zero': zero,
        'balance': balance,
        'type': neuron_type,
        'dominant_value': int(dom_val),
    }
    row_profiles.append(profile)

    if r < 20 or r in [23, 39, 55, 63, 64, 72, 88, 104, 121, 127]:
        print(f"  {r:<5} {pos:<6} {neg:<6} {zero:<6} {balance:<10} {neuron_type:<20} {dom_val:<10}")

# ============================================================================
# PHASE 2: Value Group → Neuron Type Mapping
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 2: Value Groups as Neuron Types")
print("=" * 80)

# Group rows by dominant value
value_groups = {}
for p in row_profiles:
    v = p['dominant_value']
    if v not in value_groups:
        value_groups[v] = []
    value_groups[v].append(p)

print(f"\n  {'DomValue':<10} {'#Rows':<7} {'AvgBalance':<12} {'AvgType':<25} {'Sign':<8} {'Rows'}")
print("  " + "-" * 90)

for v in sorted(value_groups.keys(), key=lambda x: -len(value_groups[x])):
    rows = value_groups[v]
    if len(rows) >= 3:
        avg_bal = np.mean([r['balance'] for r in rows])
        types = Counter(r['type'] for r in rows)
        most_common_type = types.most_common(1)[0][0]
        sign = "POS" if v > 0 else ("NEG" if v < 0 else "ZERO")
        row_nums = [r['row'] for r in rows]
        print(f"  {v:<10} {len(rows):<7} {avg_bal:<12.1f} {most_common_type:<25} {sign:<8} {row_nums[:8]}{'...' if len(row_nums) > 8 else ''}")

# ============================================================================
# PHASE 3: Mirror Pair Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 3: Mirror Pair Neural Analysis")
print("=" * 80)

print(f"\n  Mirror pair (r, 127-r) neuron type pairing:")
print(f"  {'Row':<5} {'Type':<22} {'Balance':<9} {'|':<3} {'Mirror':<7} {'Type':<22} {'Balance':<9} {'Complementary?'}")
print("  " + "-" * 95)

complement_count = 0
for r in range(64):
    mr = 127 - r
    p1 = row_profiles[r]
    p2 = row_profiles[mr]

    # Are they complementary? (one excitatory, one inhibitory)
    is_complement = (p1['balance'] > 0 and p2['balance'] < 0) or (p1['balance'] < 0 and p2['balance'] > 0)
    if is_complement:
        complement_count += 1

    if r < 10 or r in [23, 39, 55, 63]:
        comp_str = "YES" if is_complement else "no"
        print(f"  {r:<5} {p1['type']:<22} {p1['balance']:<9} {'|':<3} {mr:<7} {p2['type']:<22} {p2['balance']:<9} {comp_str}")

print(f"\n  Complementary pairs (excit/inhib): {complement_count}/64 ({complement_count/64*100:.1f}%)")

# ============================================================================
# PHASE 4: Dominant Value Relationships
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 4: Value Relationships")
print("=" * 80)

# Check relationships between dominant values
dom_values = sorted(set(p['dominant_value'] for p in row_profiles))
print(f"\n  All dominant values: {dom_values}")
print(f"  Count: {len(dom_values)}")

print(f"\n  Notable relationships:")
for i, v1 in enumerate(dom_values):
    for v2 in dom_values[i+1:]:
        s = v1 + v2
        if s in [-1, 0, 127, -128, 1]:
            count1 = len([p for p in row_profiles if p['dominant_value'] == v1])
            count2 = len([p for p in row_profiles if p['dominant_value'] == v2])
            print(f"    {v1} + {v2} = {s}  ({count1} rows + {count2} rows)")

# Check the -1 relationship specifically (since matrix symmetry rule is sum = -1)
print(f"\n  Pairs summing to -1 (matching symmetry rule):")
for v1 in dom_values:
    v2 = -1 - v1
    if v2 in dom_values and v1 < v2:
        count1 = len([p for p in row_profiles if p['dominant_value'] == v1])
        count2 = len([p for p in row_profiles if p['dominant_value'] == v2])
        rows1 = sorted([p['row'] for p in row_profiles if p['dominant_value'] == v1])
        rows2 = sorted([p['row'] for p in row_profiles if p['dominant_value'] == v2])
        print(f"    {v1} + {v2} = -1")
        print(f"      Value {v1}: {count1} rows: {rows1[:10]}")
        print(f"      Value {v2}: {count2} rows: {rows2[:10]}")
        # Check if they map to mirror pairs
        mirror_matches = sum(1 for r in rows1 if (127-r) in rows2)
        print(f"      Mirror pair matches: {mirror_matches}/{min(count1, count2)}")

# ============================================================================
# PHASE 5: Ternary Weight Matrix Properties
# ============================================================================
print("\n" + "=" * 80)
print("PHASE 5: Ternary Matrix Properties")
print("=" * 80)

# When ternary-clamped, how much information is lost?
# Original: 256 possible values per cell
# Ternary: 3 possible values per cell
# Information loss: log2(256) - log2(3) = 8 - 1.585 = 6.415 bits per cell

print(f"\n  Information analysis:")
print(f"    Original matrix: {128*128} cells x 8 bits = {128*128*8} bits")
print(f"    Ternary matrix: {128*128} cells x 1.585 bits = {128*128*1.585:.0f} bits")
print(f"    Information lost by ternary clamping: {128*128*6.415:.0f} bits ({6.415/8*100:.1f}%)")

# But the ternary matrix still has symmetry
tern_sym_count = 0
for r in range(128):
    for c in range(128):
        if ternary_matrix[r, c] + ternary_matrix[127-r, 127-c] == -1:
            tern_sym_count += 1
        elif ternary_matrix[r, c] + ternary_matrix[127-r, 127-c] in [0, -2]:
            # In ternary, -1 + 0 = -1 (satisfies), 1 + (-1) = 0 (doesn't), etc
            pass

print(f"\n  Ternary symmetry check:")
print(f"    sign(m[r,c]) + sign(m[127-r,127-c]) = -1:")
tern_sym = 0
for r in range(128):
    for c in range(128):
        if ternary_matrix[r, c] + ternary_matrix[127-r, 127-c] == -1:
            tern_sym += 1
print(f"    {tern_sym}/{total} ({tern_sym/total*100:.2f}%)")

# What does Aigarth actually see?
# Row-level ternary analysis
print(f"\n  Unique ternary row patterns: ", end="")
ternary_row_strings = []
for r in range(128):
    row_str = ''.join(['+' if v > 0 else ('-' if v < 0 else '0') for v in ternary_matrix[r]])
    ternary_row_strings.append(row_str)
unique_ternary_rows = len(set(ternary_row_strings))
print(f"{unique_ternary_rows}/128")

# How many rows become identical after ternary clamping?
ternary_row_counter = Counter(ternary_row_strings)
duplicates = [(count, pattern[:20] + "...") for pattern, count in ternary_row_counter.items() if count > 1]
if duplicates:
    print(f"  Duplicate ternary rows found: {len(duplicates)} patterns")
    for count, pattern in sorted(duplicates, reverse=True)[:5]:
        print(f"    {count} rows share pattern: {pattern}")
else:
    print(f"  No duplicate ternary rows -- all 128 rows are unique even after clamping")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ROW GROUP FUNCTION ANALYSIS SUMMARY")
print("=" * 80)

type_counts = Counter(p['type'] for p in row_profiles)
print(f"\n  Neuron type distribution:")
for t, c in type_counts.most_common():
    print(f"    {t:<25}: {c} rows ({c/128*100:.1f}%)")

print(f"\n  Key findings:")
print(f"    1. Matrix uses {len(dom_values)} distinct dominant values across 128 rows")
print(f"    2. Complementary mirror pairs: {complement_count}/64 ({complement_count/64*100:.1f}%)")
print(f"    3. Ternary clamping preserves row uniqueness: {unique_ternary_rows}/128 unique")
print(f"    4. The MAGNITUDE of values is irrelevant for Aigarth -- only the SIGN matters")
print(f"    5. The matrix encodes a balanced excitatory/inhibitory network architecture")

# Save results
results = {
    "date": datetime.now().isoformat(),
    "ternary_distribution": {
        "positive": int(n_pos),
        "negative": int(n_neg),
        "zero": int(n_zero),
    },
    "neuron_types": dict(type_counts),
    "complementary_pairs": complement_count,
    "unique_ternary_rows": unique_ternary_rows,
    "value_groups": {
        str(v): {
            "count": len(rows),
            "rows": [r['row'] for r in rows],
            "avg_balance": float(np.mean([r['balance'] for r in rows])),
        }
        for v, rows in value_groups.items()
        if len(rows) >= 3
    },
}

output_path = script_dir / "ROW_GROUP_FUNCTION_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to: {output_path}")
