#!/usr/bin/env python3
"""
===============================================================================
            FIND ALL PALINDROMES SYSTEMATICALLY
===============================================================================
Search ALL row pairs AND column pairs for palindromes of 5+ characters.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import random

script_dir = Path(__file__).parent

print("=" * 80)
print("           FIND ALL PALINDROMES")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

all_palindromes = []

# ==============================================================================
# SEARCH ROW PAIRS
# ==============================================================================
print("\n  Searching row pairs...")

for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor)

    # Find all letter sequences 5+
    for match in re.finditer(r'[a-zA-Z]{5,}', xor_str):
        seq = match.group()
        if seq == seq[::-1]:  # Exact palindrome
            all_palindromes.append({
                "type": "row",
                "pair": f"{r}↔{partner}",
                "idx1": r,
                "idx2": partner,
                "palindrome": seq,
                "length": len(seq),
                "position": match.start(),
            })

# ==============================================================================
# SEARCH COLUMN PAIRS
# ==============================================================================
print("  Searching column pairs...")

for c in range(64):
    partner = 127 - c
    col_c = [int(matrix[r, c]) for r in range(128)]
    col_p = [int(matrix[r, partner]) for r in range(128)]
    xor = [col_c[r] ^ col_p[r] for r in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor)

    for match in re.finditer(r'[a-zA-Z]{5,}', xor_str):
        seq = match.group()
        if seq == seq[::-1]:
            all_palindromes.append({
                "type": "col",
                "pair": f"{c}↔{partner}",
                "idx1": c,
                "idx2": partner,
                "palindrome": seq,
                "length": len(seq),
                "position": match.start(),
            })

# ==============================================================================
# SEARCH DIAGONALS
# ==============================================================================
print("  Searching diagonals...")

# Main diagonal XOR with anti-diagonal
main_diag = [int(matrix[i, i]) for i in range(128)]
anti_diag = [int(matrix[i, 127-i]) for i in range(128)]
xor_diag = [main_diag[i] ^ anti_diag[i] for i in range(128)]
xor_str = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_diag)

for match in re.finditer(r'[a-zA-Z]{5,}', xor_str):
    seq = match.group()
    if seq == seq[::-1]:
        all_palindromes.append({
            "type": "diagonal",
            "pair": "main↔anti",
            "idx1": 0,
            "idx2": 0,
            "palindrome": seq,
            "length": len(seq),
            "position": match.start(),
        })

# ==============================================================================
# RESULTS
# ==============================================================================
print("\n" + "=" * 80)
print("PALINDROMES FOUND")
print("=" * 80)

# Sort by length
all_palindromes.sort(key=lambda x: x["length"], reverse=True)

print(f"\n  Total palindromes (5+ chars): {len(all_palindromes)}")
print(f"\n  All palindromes:")
for p in all_palindromes:
    print(f"    {p['type']:8} {p['pair']:10}: '{p['palindrome']}' ({p['length']} chars)")

# ==============================================================================
# VALIDATE LONGEST ONES
# ==============================================================================
print("\n" + "=" * 80)
print("MONTE CARLO VALIDATION")
print("=" * 80)

# Test: how often do we find palindromes of each length in random XOR?
n_sim = 5000
random_palindrome_lengths = []

for _ in range(n_sim):
    # Random row or column pair
    if random.random() < 0.5:
        r1, r2 = random.randint(0,127), random.randint(0,127)
        v1 = [int(matrix[r1,c]) for c in range(128)]
        v2 = [int(matrix[r2,c]) for c in range(128)]
    else:
        c1, c2 = random.randint(0,127), random.randint(0,127)
        v1 = [int(matrix[r,c1]) for r in range(128)]
        v2 = [int(matrix[r,c2]) for r in range(128)]

    xor = [v1[i]^v2[i] for i in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32<=abs(x)<=126 else '.' for x in xor)

    # Find palindromes
    max_pal_len = 0
    for match in re.finditer(r'[a-zA-Z]{5,}', xor_str):
        seq = match.group()
        if seq == seq[::-1] and len(seq) > max_pal_len:
            max_pal_len = len(seq)

    random_palindrome_lengths.append(max_pal_len)

# Statistics
for length in [5, 10, 15, 20, 25, 28]:
    count = sum(1 for x in random_palindrome_lengths if x >= length)
    p = count / n_sim
    print(f"  Random pairs with palindrome {length}+ chars: {count}/{n_sim} (p={p:.4f})")

# Check our findings
print(f"\n  Our palindromes vs random:")
for p in all_palindromes[:5]:
    count = sum(1 for x in random_palindrome_lengths if x >= p["length"])
    pval = count / n_sim
    sig = "✓ SIGNIFICANT" if pval < 0.01 else "✗ not significant"
    print(f"    '{p['palindrome'][:20]}...' ({p['length']} chars): p={pval:.4f} {sig}")

# Save
results = {
    "timestamp": datetime.now().isoformat(),
    "total_palindromes": len(all_palindromes),
    "palindromes": all_palindromes,
    "monte_carlo": {
        "n_simulations": n_sim,
        "distribution": {str(k): sum(1 for x in random_palindrome_lengths if x >= k) for k in [5,10,15,20,25,28]}
    }
}

with open(script_dir / "ALL_PALINDROMES_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved")
