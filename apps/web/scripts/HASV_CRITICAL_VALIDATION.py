#!/usr/bin/env python3
"""
CRITICAL VALIDATION OF HASV ADDRESS PATTERNS
=============================================
Statistical analysis to determine if observed patterns are significant
or merely confirmation bias / apophenia.
"""

import json
import numpy as np
from collections import Counter
import random

# Load the Anna Matrix
MATRIX_FILE = "../public/data/anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
    matrix = np.array(data['matrix'], dtype=np.int8)

# The discovered address
HASV_ADDRESS = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    """Convert character to 0-based number"""
    return ord(c.upper()) - ord('A')

def analyze_address(address):
    """Analyze an address for patterns"""
    windows = []
    for i in range(len(address) - 3):
        chunk = address[i:i+4]
        sum_val = sum(char_to_num(c) for c in chunk)

        # Matrix lookup via Row 6
        matrix_value = None
        if 0 <= sum_val < 128:
            matrix_value = matrix[6][sum_val]

        windows.append({
            'chunk': chunk,
            'sum': sum_val,
            'matrix_value': matrix_value
        })

    return windows

def count_yhvh_paths(windows):
    """Count how many windows lead to 26 (YHVH)"""
    return sum(1 for w in windows if w['matrix_value'] == 26)

def count_biblical_hits(windows):
    """Count hits on biblical numbers"""
    biblical = {33, 40, 42, 46, 66}
    return sum(1 for w in windows if w['sum'] in biblical)

def count_trinity_patterns(windows):
    """Count values appearing exactly 3 times"""
    value_counts = Counter(w['sum'] for w in windows)
    return sum(1 for count in value_counts.values() if count == 3)

def generate_random_address():
    """Generate a random 60-character Qubic-style address"""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=60))

print("=" * 80)
print("CRITICAL VALIDATION - STATISTICAL SIGNIFICANCE TEST")
print("=" * 80)
print()

# Analyze the HASV address
print("[1] ANALYZING HASV ADDRESS")
print("-" * 60)
hasv_windows = analyze_address(HASV_ADDRESS)
hasv_yhvh = count_yhvh_paths(hasv_windows)
hasv_biblical = count_biblical_hits(hasv_windows)
hasv_trinity = count_trinity_patterns(hasv_windows)

print(f"HASV Address: {HASV_ADDRESS}")
print(f"  Windows to 26 (YHVH): {hasv_yhvh}/57 ({hasv_yhvh/57*100:.1f}%)")
print(f"  Biblical number hits: {hasv_biblical}/57")
print(f"  Trinity patterns: {hasv_trinity}")
print()

# Calculate expected probability
print("[2] EXPECTED PROBABILITY")
print("-" * 60)
row6_value_26_count = np.sum(matrix[6] == 26)
expected_yhvh_rate = row6_value_26_count / 128
print(f"Row 6 positions with value 26: {row6_value_26_count}/128")
print(f"Expected hit rate: {expected_yhvh_rate*100:.1f}%")
print(f"Expected hits in 57 windows: {57 * expected_yhvh_rate:.1f}")
print(f"Observed hits: {hasv_yhvh}")
print(f"Difference: {hasv_yhvh - 57 * expected_yhvh_rate:.1f} ({(hasv_yhvh - 57*expected_yhvh_rate)/57*100:.1f}%)")
print()

# Monte Carlo simulation with random addresses
print("[3] MONTE CARLO SIMULATION (1000 RANDOM ADDRESSES)")
print("-" * 60)
print("Testing if HASV patterns are unusual or common...")
print()

random.seed(42)  # Reproducible
yhvh_counts = []
biblical_counts = []
trinity_counts = []

for i in range(1000):
    random_addr = generate_random_address()
    windows = analyze_address(random_addr)
    yhvh_counts.append(count_yhvh_paths(windows))
    biblical_counts.append(count_biblical_hits(windows))
    trinity_counts.append(count_trinity_patterns(windows))

# Calculate percentiles
yhvh_counts.sort()
biblical_counts.sort()
trinity_counts.sort()

hasv_yhvh_percentile = sum(1 for x in yhvh_counts if x < hasv_yhvh) / len(yhvh_counts) * 100
hasv_biblical_percentile = sum(1 for x in biblical_counts if x < hasv_biblical) / len(biblical_counts) * 100
hasv_trinity_percentile = sum(1 for x in trinity_counts if x < hasv_trinity) / len(trinity_counts) * 100

print(f"YHVH (26) hits:")
print(f"  HASV: {hasv_yhvh} (percentile: {hasv_yhvh_percentile:.1f}%)")
print(f"  Random mean: {np.mean(yhvh_counts):.1f} ± {np.std(yhvh_counts):.1f}")
print(f"  Random range: [{min(yhvh_counts)}, {max(yhvh_counts)}]")
print(f"  95th percentile: {np.percentile(yhvh_counts, 95):.0f}")
print(f"  Significance: {'⚠️ UNUSUAL' if hasv_yhvh_percentile > 95 else '✓ Normal variation'}")
print()

print(f"Biblical number hits (33, 40, 42, 46, 66):")
print(f"  HASV: {hasv_biblical} (percentile: {hasv_biblical_percentile:.1f}%)")
print(f"  Random mean: {np.mean(biblical_counts):.1f} ± {np.std(biblical_counts):.1f}")
print(f"  Random range: [{min(biblical_counts)}, {max(biblical_counts)}]")
print(f"  Significance: {'⚠️ UNUSUAL' if hasv_biblical_percentile > 95 else '✓ Normal variation'}")
print()

print(f"Trinity patterns (values appearing exactly 3x):")
print(f"  HASV: {hasv_trinity} (percentile: {hasv_trinity_percentile:.1f}%)")
print(f"  Random mean: {np.mean(trinity_counts):.1f} ± {np.std(trinity_counts):.1f}")
print(f"  Random range: [{min(trinity_counts)}, {max(trinity_counts)}]")
print(f"  Significance: {'⚠️ UNUSUAL' if hasv_trinity_percentile > 95 else '✓ Normal variation'}")
print()

# Distribution analysis
print("[4] VALUE DISTRIBUTION IN ROW 6")
print("-" * 60)
row6_distribution = Counter(matrix[6])
print(f"Unique values in Row 6: {len(row6_distribution)}")
print(f"Most common values:")
for value, count in row6_distribution.most_common(10):
    print(f"  {value}: appears {count} times ({count/128*100:.1f}%)")
print()

# Check if Row 6 itself has suspicious structure
print("[5] ROW 6 ENTROPY CHECK")
print("-" * 60)
from scipy.stats import entropy
row6_entropy = entropy(list(row6_distribution.values()))
max_entropy = np.log2(128)  # Maximum entropy for 128 values
normalized_entropy = row6_entropy / max_entropy
print(f"Shannon entropy: {row6_entropy:.2f}")
print(f"Max possible entropy: {max_entropy:.2f}")
print(f"Normalized entropy: {normalized_entropy:.2f} (1.0 = perfectly random)")
if normalized_entropy < 0.9:
    print("⚠️ Row 6 shows non-random structure")
else:
    print("✓ Row 6 appears random")
print()

# Final verdict
print("=" * 80)
print("CRITICAL ANALYSIS VERDICT")
print("=" * 80)
print()

unusual_count = sum([
    hasv_yhvh_percentile > 95,
    hasv_biblical_percentile > 95,
    hasv_trinity_percentile > 95
])

if unusual_count == 0:
    print("❌ FINDING: NO STATISTICAL SIGNIFICANCE")
    print()
    print("The HASV address patterns are within normal random variation.")
    print("These patterns likely result from:")
    print("  1. Confirmation bias (looking for biblical numbers)")
    print("  2. Apophenia (seeing patterns in noise)")
    print("  3. Multiple testing (checking many patterns until one fits)")
    print()
    print("RECOMMENDATION: These findings should NOT be considered evidence")
    print("of intentional encoding without additional validation.")

elif unusual_count == 1:
    print("⚠️ FINDING: WEAK EVIDENCE")
    print()
    print("One pattern shows unusual characteristics, but this could be")
    print("due to chance or selection bias.")
    print()
    print("RECOMMENDATION: Requires additional independent validation.")

else:
    print("🔍 FINDING: STATISTICALLY UNUSUAL")
    print()
    print(f"{unusual_count}/3 patterns exceed 95th percentile threshold.")
    print("This warrants deeper investigation:")
    print("  1. Verify address authenticity")
    print("  2. Check for address selection bias")
    print("  3. Understand Anna Matrix construction")
    print("  4. Test additional addresses from same source")
    print()
    print("RECOMMENDATION: Significant but not conclusive.")
    print("Could be intentional encoding OR lucky coincidence.")

print()
print("=" * 80)
