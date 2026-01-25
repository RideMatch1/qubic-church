#!/usr/bin/env python3
"""
===============================================================================
            VALIDATE 20-CHAR SEQUENCE
===============================================================================
"egkmjiacpccpcaijmkge" in Rows 7↔120 - is it significant?
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import random

script_dir = Path(__file__).parent

print("=" * 80)
print("           VALIDATE 20-CHAR SEQUENCE")
print("           'egkmjiacpccpcaijmkge'")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Extract
row_7 = [int(matrix[7, c]) for c in range(128)]
row_120 = [int(matrix[120, c]) for c in range(128)]
xor_7_120 = [row_7[c] ^ row_120[c] for c in range(128)]
xor_string = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_7_120)

target = "egkmjiacpccpcaijmkge"
pos = xor_string.find(target)

print(f"\n  Target: '{target}'")
print(f"  Length: {len(target)}")
print(f"  Position: {pos}")
print(f"  Found: {'YES' if pos >= 0 else 'NO'}")

# Palindrome check
is_palindrome = target == target[::-1]
print(f"  Is palindrome: {is_palindrome}")

# Monte Carlo
n_sim = 10000
count_20plus = 0
for _ in range(n_sim):
    r1, r2 = random.randint(0,127), random.randint(0,127)
    row1 = [int(matrix[r1,c]) for c in range(128)]
    row2 = [int(matrix[r2,c]) for c in range(128)]
    xor = [row1[c]^row2[c] for c in range(128)]
    xor_str = ''.join(chr(abs(x)) if 32<=abs(x)<=126 else '.' for x in xor)
    seqs = re.findall(r'[a-zA-Z]+', xor_str)
    max_len = max(len(s) for s in seqs) if seqs else 0
    if max_len >= 20:
        count_20plus += 1

p_value = count_20plus / n_sim
print(f"\n  Monte Carlo (n={n_sim}):")
print(f"    Random pairs with 20+ chars: {count_20plus}")
print(f"    p-value: {p_value:.6f}")
print(f"    Significant (p<0.01): {'YES' if p_value < 0.01 else 'NO'}")

# Save
results = {
    "sequence": target,
    "length": len(target),
    "position": pos,
    "is_palindrome": is_palindrome,
    "p_value": p_value,
    "significant": p_value < 0.01
}
with open(script_dir / "VALIDATE_20CHAR_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n✓ Saved results")
