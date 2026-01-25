#!/usr/bin/env python3
"""
===============================================================================
            VALIDATE 28-CHAR SEQUENCE
===============================================================================
Statistically validate: "mieTeeimKiiifiifiiiKmieeTeim" in Rows 15↔112
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import random

script_dir = Path(__file__).parent

print("=" * 80)
print("           VALIDATE 28-CHAR SEQUENCE")
print("           'mieTeeimKiiifiifiiiKmieeTeim'")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# EXTRACT AND VERIFY THE SEQUENCE
# ==============================================================================
print("\n" + "=" * 80)
print("EXTRACTING SEQUENCE FROM ROWS 15↔112")
print("=" * 80)

row_15 = [int(matrix[15, c]) for c in range(128)]
row_112 = [int(matrix[112, c]) for c in range(128)]

xor_15_112 = [row_15[c] ^ row_112[c] for c in range(128)]
xor_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_15_112)

print(f"\n  Full XOR string (128 chars):")
for i in range(0, 128, 64):
    print(f"    [{i:3d}-{i+63:3d}]: {xor_string[i:i+64]}")

# Find the 28-char sequence
target = "mieTeeimKiiifiifiiiKmieeTeim"
pos = xor_string.find(target)

print(f"\n  Target: '{target}'")
print(f"  Length: {len(target)} characters")
print(f"  Position: {pos}")
print(f"  Found: {'YES' if pos >= 0 else 'NO'}")

# Find all long sequences
all_sequences = re.findall(r'[a-zA-Z]{10,}', xor_string)
print(f"\n  All 10+ char sequences in this row pair:")
for seq in all_sequences:
    print(f"    '{seq}' ({len(seq)} chars)")

# ==============================================================================
# MONTE CARLO: LONGEST SEQUENCE IN RANDOM ROW XOR
# ==============================================================================
print("\n" + "=" * 80)
print("MONTE CARLO: LONGEST SEQUENCE IN RANDOM ROW XOR")
print("=" * 80)

n_simulations = 10000
longest_random = []

for _ in range(n_simulations):
    r1 = random.randint(0, 127)
    r2 = random.randint(0, 127)

    row1 = [int(matrix[r1, c]) for c in range(128)]
    row2 = [int(matrix[r2, c]) for c in range(128)]
    xor = [row1[c] ^ row2[c] for c in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor)

    sequences = re.findall(r'[a-zA-Z]+', xor_str)
    max_len = max(len(s) for s in sequences) if sequences else 0
    longest_random.append(max_len)

mean_longest = np.mean(longest_random)
std_longest = np.std(longest_random)
max_longest = max(longest_random)

# Count how many random pairs have 28+ char sequence
count_28plus = sum(1 for x in longest_random if x >= 28)

print(f"\n  Random row pairs (n={n_simulations}):")
print(f"    Mean longest sequence: {mean_longest:.2f} chars")
print(f"    Std: {std_longest:.2f}")
print(f"    Max: {max_longest} chars")
print(f"    Count with 28+ chars: {count_28plus}")
print(f"    p-value (28+ chars): {count_28plus/n_simulations:.6f}")

# Z-score for 28 chars
z_score = (28 - mean_longest) / std_longest
print(f"\n  Z-score for 28 chars: {z_score:.2f}")

# ==============================================================================
# MONTE CARLO: SYMMETRIC ROW PAIRS ONLY
# ==============================================================================
print("\n" + "=" * 80)
print("MONTE CARLO: SYMMETRIC ROW PAIRS (r ↔ 127-r)")
print("=" * 80)

# Check all 64 symmetric pairs
symmetric_longest = []

for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor)

    sequences = re.findall(r'[a-zA-Z]+', xor_str)
    max_len = max(len(s) for s in sequences) if sequences else 0
    symmetric_longest.append((r, partner, max_len))

# Sort by length
symmetric_longest.sort(key=lambda x: x[2], reverse=True)

print(f"\n  Top 10 symmetric row pairs by longest sequence:")
for r, p, length in symmetric_longest[:10]:
    print(f"    Rows {r:3}↔{p:3}: {length} chars")

# How many have 20+ chars?
count_20plus_sym = sum(1 for _, _, l in symmetric_longest if l >= 20)
count_25plus_sym = sum(1 for _, _, l in symmetric_longest if l >= 25)
count_28plus_sym = sum(1 for _, _, l in symmetric_longest if l >= 28)

print(f"\n  Distribution in symmetric pairs:")
print(f"    20+ chars: {count_20plus_sym}/64 pairs")
print(f"    25+ chars: {count_25plus_sym}/64 pairs")
print(f"    28+ chars: {count_28plus_sym}/64 pairs")

# ==============================================================================
# ANALYZE THE SEQUENCE STRUCTURE
# ==============================================================================
print("\n" + "=" * 80)
print("SEQUENCE STRUCTURE ANALYSIS")
print("=" * 80)

# Check for palindrome
is_palindrome = target == target[::-1]
is_palindrome_case_insensitive = target.lower() == target.lower()[::-1]

print(f"\n  Palindrome check:")
print(f"    Exact: {is_palindrome}")
print(f"    Case-insensitive: {is_palindrome_case_insensitive}")

# Check for repetition patterns
print(f"\n  Letter frequency:")
from collections import Counter
freq = Counter(target.lower())
for letter, count in freq.most_common():
    print(f"    '{letter}': {count} times ({count/len(target)*100:.1f}%)")

# Check for sub-patterns
print(f"\n  Sub-pattern search:")
for pattern_len in [3, 4, 5]:
    patterns = {}
    for i in range(len(target) - pattern_len + 1):
        p = target[i:i+pattern_len]
        patterns[p] = patterns.get(p, 0) + 1

    repeats = {k: v for k, v in patterns.items() if v > 1}
    if repeats:
        print(f"    {pattern_len}-char patterns repeated: {repeats}")

# ==============================================================================
# RAW VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("RAW XOR VALUES")
print("=" * 80)

if pos >= 0:
    print(f"\n  Values at sequence position {pos}-{pos+27}:")
    for i in range(28):
        c = pos + i
        val = xor_15_112[c]
        ch = chr(abs(val)) if 32 <= abs(val) <= 126 else '.'
        r15_val = row_15[c]
        r112_val = row_112[c]
        print(f"    Col {c:3d}: Row15={r15_val:4d}, Row112={r112_val:4d}, XOR={val:4d} = '{ch}'")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)

is_significant = count_28plus == 0

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         28-CHAR SEQUENCE VALIDATION                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  SEQUENCE: "mieTeeimKiiifiifiiiKmieeTeim"                                    ║
║  LOCATION: Rows 15↔112, position {pos:3d}                                        ║
║                                                                               ║
║  MONTE CARLO (n={n_simulations}):                                                  ║
║  • Mean longest in random: {mean_longest:.2f} chars                                 ║
║  • Max in random: {max_longest} chars                                              ║
║  • Random pairs with 28+ chars: {count_28plus}/{n_simulations}                            ║
║  • p-value: {count_28plus/n_simulations:.6f}                                                      ║
║  • Z-score: {z_score:.2f}                                                          ║
║                                                                               ║
║  SYMMETRIC PAIRS (64 total):                                                  ║
║  • Pairs with 28+ chars: {count_28plus_sym}/64                                        ║
║                                                                               ║
║  CONCLUSION:                                                                  ║
║  • Statistically significant (p<0.01): {'YES ✓' if is_significant else 'NO  ✗'}                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "sequence": target,
    "length": len(target),
    "location": {"rows": [15, 112], "position": pos},
    "monte_carlo": {
        "n_simulations": n_simulations,
        "mean_longest": mean_longest,
        "std_longest": std_longest,
        "max_longest": max_longest,
        "count_28plus": count_28plus,
        "p_value": count_28plus / n_simulations,
        "z_score": z_score,
    },
    "symmetric_pairs": {
        "count_28plus": count_28plus_sym,
        "top_10": symmetric_longest[:10],
    },
    "is_significant": is_significant,
}

output_path = script_dir / "VALIDATE_28CHAR_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved: {output_path}")
