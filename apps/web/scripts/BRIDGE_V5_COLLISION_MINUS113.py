#!/usr/bin/env python3
"""
===============================================================================
        BRIDGE V5: VALUE -113 COLLISION ANALYSIS
===============================================================================
PRE-REGISTERED HYPOTHESIS:
  H5.3: Value -113 appears in the matrix with frequency X.
        The "all 3 methods produce -113" claim is or is not surprising
        given this frequency.

METHODOLOGY:
  - Count -113 occurrences in anna-matrix.json
  - Calculate P(3 random positions all = -113)
  - Compare against any value with higher frequency
  - Monte Carlo: pick 3 random cells, how often do they all match?

SIGNIFICANCE: p < 0.001
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

script_dir = Path(__file__).parent
np.random.seed(42)

print("=" * 80)
print("         BRIDGE V5: VALUE -113 COLLISION ANALYSIS")
print("=" * 80)
print(f"\nDate: {datetime.now().isoformat()}")

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int16)
total_cells = 128 * 128

results = {}

# ============================================================================
# VALUE -113 FREQUENCY
# ============================================================================
print("\n" + "=" * 80)
print("VALUE -113 IN THE MATRIX")
print("=" * 80)

all_vals = matrix.flatten()
val_counts = Counter(all_vals)

count_minus113 = val_counts.get(-113, 0)
freq_minus113 = count_minus113 / total_cells

print(f"\n  Value -113:")
print(f"    Count: {count_minus113}/{total_cells}")
print(f"    Frequency: {freq_minus113:.4f} ({freq_minus113*100:.2f}%)")
print(f"    Rank: {sorted(val_counts.values(), reverse=True).index(count_minus113) + 1} most common")

# Top 10 most common values
print(f"\n  Top 10 most common values:")
print(f"    {'Value':<8} {'Count':<8} {'Freq':<10} {'P(3 match)':<15}")
print("    " + "-" * 45)

for val, count in val_counts.most_common(10):
    freq = count / total_cells
    p3 = freq ** 3
    print(f"    {val:<8} {count:<8} {freq:<10.4f} {p3:<15.8f}")

# ============================================================================
# P(3 RANDOM CELLS ALL = -113)
# ============================================================================
print("\n" + "=" * 80)
print("PROBABILITY: 3 CELLS ALL = -113")
print("=" * 80)

p_minus113 = freq_minus113
p_3_minus113 = p_minus113 ** 3

print(f"\n  Analytical:")
print(f"    P(one cell = -113) = {p_minus113:.6f}")
print(f"    P(3 cells all = -113) = {p_3_minus113:.10f}")
print(f"    = 1 in {1/p_3_minus113:.0f}")

# But this is the probability for a SPECIFIC value
# What about P(3 cells all match ANY value)?
# This is much higher
p_3_any_match = sum((count / total_cells) ** 3 for count in val_counts.values())
print(f"\n  P(3 random cells all have the SAME value, any value):")
print(f"    = {p_3_any_match:.8f}")
print(f"    = 1 in {1/p_3_any_match:.0f}")

# How many values would produce a "1 in 1M+" claim?
impressive_count = 0
for val, count in val_counts.items():
    freq = count / total_cells
    if freq ** 3 < 1e-6:
        impressive_count += 1

print(f"\n  Values where P(3 match) < 1 in 1,000,000: {impressive_count}/{len(val_counts)}")
print(f"  This means: most values produce 'impressive' coincidences")

# ============================================================================
# MONTE CARLO: 3-CELL COLLISION FREQUENCY
# ============================================================================
print("\n" + "=" * 80)
print("MONTE CARLO: 3-Cell Collision Test")
print("=" * 80)

SIMULATIONS = 100000

collision_count = 0
minus113_collision = 0
collision_values = Counter()

for _ in range(SIMULATIONS):
    # Pick 3 random cells
    idx = np.random.randint(0, total_cells, size=3)
    vals = all_vals[idx]

    if vals[0] == vals[1] == vals[2]:
        collision_count += 1
        collision_values[int(vals[0])] += 1
        if vals[0] == -113:
            minus113_collision += 1

p_collision_mc = collision_count / SIMULATIONS
p_minus113_mc = minus113_collision / SIMULATIONS

print(f"\n  Simulations: {SIMULATIONS:,}")
print(f"  Any 3-cell collision: {collision_count} ({p_collision_mc*100:.3f}%)")
print(f"  Specific -113 collision: {minus113_collision} ({p_minus113_mc*100:.5f}%)")
print(f"")
print(f"  Most common collision values:")
for val, count in collision_values.most_common(10):
    print(f"    Value {val:>5}: {count} times")

# ============================================================================
# COLLISION ANALYSIS CONTEXT
# ============================================================================
print("\n" + "=" * 80)
print("CONTEXT: What Does the '3 Methods Produce -113' Claim Mean?")
print("=" * 80)

print(f"""
  The claim: "All 3 derivation methods (SHA256, K12, Qubic) produce
  collision value -113 when applied to the same seed."

  What this actually means:
  1. Take a Qubic seed (55 lowercase letters)
  2. Apply 3 different hash functions
  3. Map each hash to a matrix position
  4. Look up matrix value at each position
  5. All 3 happen to land on cells containing -113

  Key considerations:
  - -113 appears in {count_minus113}/16384 cells ({freq_minus113*100:.2f}% of the matrix)
  - P(3 independent positions all hit -113) = {p_3_minus113:.10f}
  - P(3 positions hit ANY same value) = {p_3_any_match:.8f} = 1 in {1/p_3_any_match:.0f}
  - There are {impressive_count} values that would produce "impressive" 3-way collisions
""")

# ============================================================================
# WHAT ABOUT COLLISION ANALYSIS DATA?
# ============================================================================
print("=" * 80)
print("CROSS-CHECK: Anna Collision Analysis Data")
print("=" * 80)

collision_path = script_dir.parent / "public" / "data" / "anna-collision-analysis.json"
with open(collision_path) as f:
    collision_data = json.load(f)

top_collisions = collision_data.get("topCollisions", [])
print(f"\n  Collision analysis has {collision_data.get('totalResponses', 0)} total responses")
print(f"  Top collision values:")
for entry in top_collisions[:10]:
    val = entry.get("value", entry.get("collision_value", "?"))
    count = entry.get("count", 0)
    # Expected from matrix frequency
    matrix_freq = val_counts.get(val, 0) / total_cells if isinstance(val, int) else 0
    expected = collision_data.get('totalResponses', 897) * matrix_freq
    ratio = count / expected if expected > 0 else float('inf')
    print(f"    Value {val:>5}: {count} collisions (matrix freq: {matrix_freq:.4f}, expected: {expected:.1f}, ratio: {ratio:.1f}x)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("VALUE -113 ANALYSIS SUMMARY")
print("=" * 80)

print(f"\n  H5.3 Result:")
print(f"    -113 appears {count_minus113} times in matrix ({freq_minus113*100:.2f}%)")
print(f"    P(3 cells all = -113) = {p_3_minus113:.10f} = 1 in {1/p_3_minus113:.0f}")
print(f"    P(3 cells match ANY value) = {p_3_any_match:.8f} = 1 in {1/p_3_any_match:.0f}")
print(f"")
print(f"  VERDICT:")
print(f"    A 3-way -113 collision IS unlikely for that specific value.")
print(f"    But {impressive_count} other values would produce equally 'impressive' results.")
print(f"    This is another LOOK-ELSEWHERE EFFECT.")
print(f"    The probability of SOME value producing a 3-way collision")
print(f"    across methods is much higher than for -113 specifically.")

results["summary"] = {
    "minus113_count": count_minus113,
    "minus113_freq": float(freq_minus113),
    "p_3_minus113": float(p_3_minus113),
    "p_3_any_match": float(p_3_any_match),
    "impressive_values": impressive_count,
    "verdict": "Look-elsewhere effect",
}

# Save results
output_path = script_dir / "BRIDGE_V5_COLLISION_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Results saved to: {output_path}")
