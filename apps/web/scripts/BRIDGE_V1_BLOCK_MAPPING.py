#!/usr/bin/env python3
"""
===============================================================================
        BRIDGE V1: 27-DIVISIBLE BLOCK MAPPING VALIDATION
===============================================================================
PRE-REGISTERED HYPOTHESES:
  H1.7: Mapping algorithm row=(block//27)%128, col=block%128 produces
        documented coordinates for the 4 claimed blocks
  H1.8: Matrix values at those coordinates match documented [85, 60, 100, -68]
  H1.9: Sum = 177 = 0xB1

CRITICAL CONTROL TESTS:
  C1: Test 10 OTHER divisors (13,19,23,29,31,37,41,43,47,53).
      For each, pick 4 blocks divisible by that number, map to matrix,
      sum values. How often is the sum a "notable" hex byte?
  C2: Test 100 random sets of 4 blocks with divisor 27.
      How specific is sum=177?
  C3: Test if value-26 and value-27 dominance creates bias toward
      certain sums regardless of block selection.

SIGNIFICANCE: Bonferroni-corrected for 11 divisors × multiple comparisons
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
print("         BRIDGE V1: 27-DIVISIBLE BLOCK MAPPING VALIDATION")
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

results = {}

# ============================================================================
# H1.7: Mapping Algorithm Verification
# ============================================================================
print("\n" + "=" * 80)
print("H1.7/H1.8/H1.9: Documented Block Mapping")
print("=" * 80)

documented_blocks = {
    3996: {"row": 20, "col": 28, "value": 85},
    10611: {"row": 9, "col": 115, "value": 60},
    16065: {"row": 83, "col": 65, "value": 100},
    36153: {"row": 59, "col": 57, "value": -68},
}

print(f"\n  Mapping: row = (block // 27) % 128, col = block % 128")
print(f"\n  {'Block':<8} {'Row':<6} {'Col':<6} {'Value':<8} {'Expected':<10} {'Match'}")
print("  " + "-" * 50)

all_match = True
values = []
for block, expected in documented_blocks.items():
    assert block % 27 == 0, f"Block {block} not divisible by 27"
    row = (block // 27) % 128
    col = block % 128
    val = int(matrix[row, col])
    values.append(val)
    match = row == expected["row"] and col == expected["col"] and val == expected["value"]
    if not match:
        all_match = False
    print(f"  {block:<8} {row:<6} {col:<6} {val:<8} {expected['value']:<10} {'PASS' if match else 'FAIL'}")

total = sum(values)
hex_sum = hex(total & 0xFF)

print(f"\n  Sum: {total} (expected 177)")
print(f"  Hex: {hex_sum} (expected 0xb1)")
print(f"  H1.7 (coordinates): {'CONFIRMED' if all_match else 'FAILED'}")
print(f"  H1.8 (values): {'CONFIRMED' if all_match else 'FAILED'}")
print(f"  H1.9 (sum=177): {'CONFIRMED' if total == 177 else 'FAILED'}")

results["h1_7_8_9"] = {
    "all_match": all_match,
    "sum": total,
    "hex": hex_sum,
}

# ============================================================================
# CONTROL C1: Other Divisors
# ============================================================================
print("\n" + "=" * 80)
print("CONTROL C1: Testing 10 Other Divisors")
print("=" * 80)

# Define "notable" hex bytes
NOTABLE_HEX = {
    0x00: "NULL", 0x0A: "LF", 0x0D: "CR", 0x1B: "ESC/27",
    0x20: "SPACE", 0x2A: "asterisk", 0x42: "B", 0x43: "C",
    0x46: "F", 0x4F: "O", 0x7F: "DEL", 0xA0: "NBSP",
    0xB1: "±/177", 0xFE: "THORN", 0xFF: "y-uml",
}

# For a broader definition: any printable ASCII or well-known byte
def is_notable_hex(val):
    """Check if a byte value is 'notable' in some way."""
    b = val & 0xFF
    if b in NOTABLE_HEX:
        return NOTABLE_HEX[b]
    if 0x41 <= b <= 0x5A:  # A-Z
        return f"ASCII '{chr(b)}'"
    if 0x30 <= b <= 0x39:  # 0-9
        return f"ASCII '{chr(b)}'"
    return None

other_divisors = [13, 19, 23, 29, 31, 37, 41, 43, 47, 53]

print(f"\n  For each divisor D, picking first 4 blocks divisible by D")
print(f"  from the same pool as the documented blocks (range 1-50000)")
print(f"\n  {'Divisor':<10} {'Blocks':<30} {'Sum':<8} {'Hex':<8} {'Notable?'}")
print("  " + "-" * 70)

control_sums = {}
for d in other_divisors:
    # Pick 4 blocks divisible by d in similar range to documented blocks
    blocks = [b for b in range(d, 50000, d)]
    # Pick 4 at positions matching the documented block indices roughly
    # Use same selection as documented: blocks near 4000, 10600, 16000, 36000
    selected = []
    for target in [3996, 10611, 16065, 36153]:
        # Find closest block divisible by d to each target
        closest = min(blocks, key=lambda x: abs(x - target))
        selected.append(closest)

    vals = []
    for block in selected:
        row = (block // d) % 128
        col = block % 128
        vals.append(int(matrix[row, col]))

    s = sum(vals)
    h = hex(s & 0xFF)
    notable = is_notable_hex(s)
    control_sums[d] = {"blocks": selected, "values": vals, "sum": s, "hex": h, "notable": notable}

    notable_str = notable if notable else "-"
    print(f"  {d:<10} {str(selected):<30} {s:<8} {h:<8} {notable_str}")

# Add divisor 27 for comparison
print(f"  {'27':<10} {str(list(documented_blocks.keys())):<30} {total:<8} {hex_sum:<8} {is_notable_hex(total) or '-'}")

# Count how many divisors produce "notable" results
notable_count = sum(1 for v in control_sums.values() if v["notable"] is not None)
notable_count_with_27 = notable_count + (1 if is_notable_hex(total) else 0)

print(f"\n  Notable results: {notable_count_with_27} out of 11 divisors")
print(f"  This means {'27 is NOT special' if notable_count >= 2 else '27 may be special'}")

results["c1_other_divisors"] = {str(d): v for d, v in control_sums.items()}
results["c1_notable_count"] = notable_count_with_27

# ============================================================================
# CONTROL C2: Random Block Sets with Divisor 27
# ============================================================================
print("\n" + "=" * 80)
print("CONTROL C2: 10000 Random Block Sets with Divisor 27")
print("=" * 80)

SIMULATIONS = 10000
MAX_BLOCK = 100000

# All blocks divisible by 27 in range
blocks_27 = list(range(27, MAX_BLOCK, 27))

random_sums = []
sum_177_count = 0
notable_sum_count = 0

for sim in range(SIMULATIONS):
    # Pick 4 random blocks divisible by 27
    selected = np.random.choice(blocks_27, size=4, replace=False)
    vals = []
    for block in selected:
        row = (block // 27) % 128
        col = block % 128
        vals.append(int(matrix[row, col]))
    s = sum(vals)
    random_sums.append(s)

    if s == 177:
        sum_177_count += 1
    if is_notable_hex(s) is not None:
        notable_sum_count += 1

random_sums = np.array(random_sums)

print(f"\n  Simulations: {SIMULATIONS}")
print(f"  Sum = 177 occurred: {sum_177_count} times ({sum_177_count/SIMULATIONS*100:.2f}%)")
print(f"  Notable hex sums: {notable_sum_count} times ({notable_sum_count/SIMULATIONS*100:.1f}%)")
print(f"\n  Sum distribution:")
print(f"    Mean: {np.mean(random_sums):.1f}")
print(f"    Std: {np.std(random_sums):.1f}")
print(f"    Min: {np.min(random_sums)}")
print(f"    Max: {np.max(random_sums)}")
print(f"    Median: {np.median(random_sums):.1f}")

# p-value for sum = 177
p_exact_177 = sum_177_count / SIMULATIONS
p_at_least_177 = np.sum(random_sums >= 177) / SIMULATIONS

print(f"\n  P(sum = 177): {p_exact_177:.4f}")
print(f"  P(sum >= 177): {p_at_least_177:.4f}")
print(f"  P(|sum| >= 177): {np.sum(np.abs(random_sums) >= 177) / SIMULATIONS:.4f}")

results["c2_random_sums"] = {
    "simulations": SIMULATIONS,
    "sum_177_count": sum_177_count,
    "p_exact_177": p_exact_177,
    "p_at_least_177": float(p_at_least_177),
    "notable_sum_count": notable_sum_count,
    "mean": float(np.mean(random_sums)),
    "std": float(np.std(random_sums)),
}

# ============================================================================
# CONTROL C3: Matrix Value Bias Effect
# ============================================================================
print("\n" + "=" * 80)
print("CONTROL C3: Matrix Value Bias Analysis")
print("=" * 80)

# The matrix has dominant values (26, -27, 101, -102)
# This might bias sums regardless of block selection
# What's the expected sum from 4 random matrix cells?

print(f"\n  Matrix value statistics:")
all_vals = matrix.flatten()
print(f"    Mean: {np.mean(all_vals):.2f}")
print(f"    Expected sum of 4 random cells: {4 * np.mean(all_vals):.2f}")
print(f"    Std of 4-cell sum: {np.std(all_vals) * 2:.2f} (√4 × cell_std)")

# Test: 10000 random sets of 4 cells from ANY position
random_cell_sums = []
for _ in range(SIMULATIONS):
    rows = np.random.randint(0, 128, size=4)
    cols = np.random.randint(0, 128, size=4)
    s = sum(int(matrix[r, c]) for r, c in zip(rows, cols))
    random_cell_sums.append(s)

random_cell_sums = np.array(random_cell_sums)
p_177_any_cells = np.sum(random_cell_sums == 177) / SIMULATIONS

print(f"\n  Random 4-cell sum (any position):")
print(f"    Mean: {np.mean(random_cell_sums):.1f}")
print(f"    Std: {np.std(random_cell_sums):.1f}")
print(f"    P(sum = 177): {p_177_any_cells:.4f}")
print(f"    This is the BASE RATE regardless of block mapping")

results["c3_base_rate"] = {
    "mean_4cell_sum": float(np.mean(random_cell_sums)),
    "std_4cell_sum": float(np.std(random_cell_sums)),
    "p_177_any_cells": float(p_177_any_cells),
}

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("BLOCK MAPPING VALIDATION SUMMARY")
print("=" * 80)

print(f"\n  H1.7 (Mapping produces documented coordinates): {'CONFIRMED' if all_match else 'FAILED'}")
print(f"  H1.8 (Cell values match documentation): {'CONFIRMED' if all_match else 'FAILED'}")
print(f"  H1.9 (Sum = 177 = 0xB1): {'CONFIRMED' if total == 177 else 'FAILED'}")
print(f"")
print(f"  Control results:")
print(f"    C1: {notable_count_with_27}/11 divisors produce 'notable' hex sums")
print(f"    C2: P(sum=177 with random blocks ÷ 27) = {p_exact_177:.4f}")
print(f"    C3: P(sum=177 with 4 random cells) = {p_177_any_cells:.4f}")
print(f"")
if notable_count >= 3:
    print(f"  VERDICT: Sum = 177 is NOT unique to divisor 27. Multiple divisors")
    print(f"  produce 'notable' sums. The finding is LIKELY CHERRY-PICKED.")
elif p_exact_177 > 0.01:
    print(f"  VERDICT: Sum = 177 occurs {p_exact_177*100:.1f}% of the time with random")
    print(f"  blocks divisible by 27. This is NOT statistically significant.")
else:
    print(f"  VERDICT: Sum = 177 is rare (p = {p_exact_177:.4f}) but needs")
    print(f"  Bonferroni correction for {notable_count_with_27} tested divisors.")

# Save results
output_path = script_dir / "BRIDGE_V1_BLOCK_MAPPING_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Results saved to: {output_path}")
