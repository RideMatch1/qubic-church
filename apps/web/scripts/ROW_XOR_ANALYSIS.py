#!/usr/bin/env python3
"""
===============================================================================
            ROW XOR ANALYSIS - RIGOROUS STATISTICAL APPROACH
===============================================================================
Analyze Row[r] ⊕ Row[127-r] for all 64 symmetric row pairs.
NO interpretation - only data extraction and statistical validation.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import random

script_dir = Path(__file__).parent

print("=" * 80)
print("           ROW XOR ANALYSIS")
print("           Rigorous statistical approach")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# ANALYZE ALL 64 ROW PAIRS
# ==============================================================================
print("\n" + "=" * 80)
print("ANALYZING ALL 64 SYMMETRIC ROW PAIRS")
print("=" * 80)

all_row_pairs = []

for r in range(64):
    partner = 127 - r

    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]

    # XOR
    xor_rp = [row_r[c] ^ row_p[c] for c in range(128)]
    xor_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_rp)

    # Find letter sequences
    words_3plus = re.findall(r'[a-zA-Z]{3,}', xor_string)
    words_4plus = re.findall(r'[a-zA-Z]{4,}', xor_string)
    words_5plus = re.findall(r'[a-zA-Z]{5,}', xor_string)

    # Count asymmetric columns
    asym_count = 0
    for c in range(128):
        if row_r[c] + row_p[127-c] != -1:
            asym_count += 1

    pair_data = {
        "row1": r,
        "row2": partner,
        "asymmetric_cols": asym_count,
        "words_3plus": words_3plus,
        "words_4plus": words_4plus,
        "words_5plus": words_5plus,
        "word_count_3plus": len(words_3plus),
        "word_count_4plus": len(words_4plus),
        "xor_string": xor_string,
    }

    all_row_pairs.append(pair_data)

# ==============================================================================
# STATISTICAL BASELINE
# ==============================================================================
print("\n" + "=" * 80)
print("MONTE CARLO BASELINE")
print("=" * 80)

random_word_counts = []
for _ in range(1000):
    r1 = random.randint(0, 127)
    r2 = random.randint(0, 127)

    row1 = [int(matrix[r1, c]) for c in range(128)]
    row2 = [int(matrix[r2, c]) for c in range(128)]
    xor = [row1[c] ^ row2[c] for c in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor)

    words = re.findall(r'[a-zA-Z]{4,}', xor_str)
    random_word_counts.append(len(words))

mean_random = np.mean(random_word_counts)
std_random = np.std(random_word_counts)
max_random = max(random_word_counts)

print(f"\n  Random row pairs (n=1000):")
print(f"    Mean 4+ letter words: {mean_random:.2f}")
print(f"    Std: {std_random:.2f}")
print(f"    Max: {max_random}")

# ==============================================================================
# RESULTS TABLE
# ==============================================================================
print("\n" + "=" * 80)
print("TOP 20 ROW PAIRS BY WORD COUNT")
print("=" * 80)

sorted_pairs = sorted(all_row_pairs, key=lambda x: x["word_count_4plus"], reverse=True)

print(f"\n  {'Pair':10} {'Asym':5} {'3+':4} {'4+':4} {'5+':4} {'Top Words'}")
print("  " + "-" * 70)

for pair in sorted_pairs[:20]:
    words_str = ",".join(pair["words_4plus"][:3]) if pair["words_4plus"] else "-"
    print(f"  {pair['row1']:3}↔{pair['row2']:3}   {pair['asymmetric_cols']:4}  {pair['word_count_3plus']:3}  "
          f"{pair['word_count_4plus']:3}  {len(pair['words_5plus']):3}  {words_str[:40]}")

# ==============================================================================
# STATISTICALLY SIGNIFICANT PAIRS
# ==============================================================================
print("\n" + "=" * 80)
print("STATISTICALLY SIGNIFICANT PAIRS")
print("=" * 80)

# Pairs exceeding 2 standard deviations above mean
threshold = mean_random + 2 * std_random
significant_pairs = [p for p in all_row_pairs if p["word_count_4plus"] > threshold]

print(f"\n  Threshold (mean + 2σ): {threshold:.2f}")
print(f"  Pairs above threshold: {len(significant_pairs)}")

for p in significant_pairs:
    z_score = (p["word_count_4plus"] - mean_random) / std_random if std_random > 0 else 0
    print(f"    Rows {p['row1']:3}↔{p['row2']:3}: {p['word_count_4plus']} words (z={z_score:.2f})")

# ==============================================================================
# LONGEST SEQUENCES
# ==============================================================================
print("\n" + "=" * 80)
print("LONGEST LETTER SEQUENCES (5+ chars)")
print("=" * 80)

all_long_words = []
for pair in all_row_pairs:
    for word in pair["words_5plus"]:
        all_long_words.append((word, pair["row1"], pair["row2"], len(word)))

all_long_words.sort(key=lambda x: x[3], reverse=True)

print(f"\n  Top 15 longest:")
for word, r1, r2, length in all_long_words[:15]:
    print(f"    '{word}' ({length} chars) in Rows {r1}↔{r2}")

# ==============================================================================
# COMPARE WITH COLUMN ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("COMPARISON: ROWS vs COLUMNS")
print("=" * 80)

total_row_words_4plus = sum(p["word_count_4plus"] for p in all_row_pairs)
total_row_words_3plus = sum(p["word_count_3plus"] for p in all_row_pairs)

print(f"\n  Row pairs:")
print(f"    Total 3+ letter words: {total_row_words_3plus}")
print(f"    Total 4+ letter words: {total_row_words_4plus}")
print(f"    Significant pairs (>2σ): {len(significant_pairs)}")

# ==============================================================================
# ASYMMETRY DISTRIBUTION
# ==============================================================================
print("\n" + "=" * 80)
print("ASYMMETRY DISTRIBUTION IN ROWS")
print("=" * 80)

asym_distribution = {}
for p in all_row_pairs:
    asym = p["asymmetric_cols"]
    if asym not in asym_distribution:
        asym_distribution[asym] = []
    asym_distribution[asym].append((p["row1"], p["row2"]))

print(f"\n  Asymmetric column counts:")
for asym in sorted(asym_distribution.keys()):
    pairs = asym_distribution[asym]
    print(f"    {asym} asymmetric cols: {len(pairs)} pairs")
    if asym > 0 and len(pairs) <= 5:
        for r1, r2 in pairs:
            print(f"      Rows {r1}↔{r2}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("ROW XOR ANALYSIS COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         ROW XOR SUMMARY                                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  BASELINE (random pairs):                                                     ║
║  • Mean 4+ letter words: {mean_random:.2f}                                           ║
║  • Std: {std_random:.2f}                                                             ║
║  • Max: {max_random}                                                               ║
║                                                                               ║
║  SYMMETRIC ROW PAIRS:                                                         ║
║  • Total 3+ letter words: {total_row_words_3plus:4}                                        ║
║  • Total 4+ letter words: {total_row_words_4plus:4}                                        ║
║  • Significant pairs (>2σ): {len(significant_pairs):2}                                       ║
║  • Longest sequence: {all_long_words[0][3] if all_long_words else 0} chars                                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "baseline": {
        "mean": mean_random,
        "std": std_random,
        "max": max_random,
    },
    "all_pairs": all_row_pairs,
    "significant_pairs": [p for p in significant_pairs],
    "longest_words": all_long_words[:30],
    "totals": {
        "words_3plus": total_row_words_3plus,
        "words_4plus": total_row_words_4plus,
    },
}

output_path = script_dir / "ROW_XOR_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved: {output_path}")
