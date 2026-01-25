#!/usr/bin/env python3
"""
VALIDATE CFB FINDINGS
=====================
The ultra mining found CFB in row_11_xor127 and mod_26.
Let's validate these with rigorous Monte-Carlo.
"""

import json
import numpy as np
from pathlib import Path
import random

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("=" * 70)
print("CFB VALIDATION - Deep Analysis")
print("=" * 70)

# =============================================================================
# FINDING 1: CFB in row_11 XOR 127
# =============================================================================
print("\n--- Finding 1: Row 11 XOR 127 ---")

row_11 = matrix[11]
xor127 = [(v ^ 127) & 0x7F for v in row_11]
text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor127])

print(f"Row 11 XOR 127: {text}")

# Find CFB
pos = text.lower().find('cfb')
if pos >= 0:
    print(f"'cfb' found at position {pos}")
    print(f"Context: ...{text[max(0,pos-10):pos+13]}...")

    # Monte-Carlo validation for this specific encoding
    print("\nMonte-Carlo validation (10000 iterations)...")

    hits = 0
    for _ in range(10000):
        # Generate random row with same value distribution
        rand_row = np.random.choice(row_11, size=128, replace=True)
        rand_xor = [(v ^ 127) & 0x7F for v in rand_row]
        rand_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in rand_xor])
        if 'cfb' in rand_text.lower():
            hits += 1

    p_value = hits / 10000
    print(f"  Random hits: {hits}/10000")
    print(f"  p-value: {p_value}")
    print(f"  Significant (p < 0.05): {p_value < 0.05}")
else:
    print("'cfb' NOT found in row 11 XOR 127")

# =============================================================================
# FINDING 2: CFB in mod_26
# =============================================================================
print("\n--- Finding 2: Mod 26 Encoding ---")

mod26 = []
for v in matrix.flatten():
    m = abs(v) % 26
    mod26.append(chr(ord('a') + m))

mod26_text = ''.join(mod26)

pos = mod26_text.find('cfb')
if pos >= 0:
    print(f"'cfb' found at position {pos}")
    print(f"Context: ...{mod26_text[max(0,pos-10):pos+13]}...")

    # Monte-Carlo for mod26
    print("\nMonte-Carlo validation (10000 iterations)...")

    flat = matrix.flatten()
    hits = 0
    for _ in range(10000):
        rand_flat = np.random.choice(flat, size=len(flat), replace=True)
        rand_mod26 = ''.join([chr(ord('a') + abs(v) % 26) for v in rand_flat])
        if 'cfb' in rand_mod26:
            hits += 1

    p_value = hits / 10000
    print(f"  Random hits: {hits}/10000")
    print(f"  p-value: {p_value}")
    print(f"  Significant (p < 0.05): {p_value < 0.05}")
else:
    print("'cfb' NOT found in mod 26")

# =============================================================================
# FINDING 3: CFB in XOR const 127
# =============================================================================
print("\n--- Finding 3: Full Matrix XOR 127 ---")

xor_full = (matrix ^ 127) & 0x7F
text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_full.flatten()])

pos = text.lower().find('cfb')
if pos >= 0:
    print(f"'cfb' found at position {pos}")
    print(f"Context: ...{text[max(0,pos-10):pos+13]}...")

    # Convert position to row,col
    row = pos // 128
    col = pos % 128
    print(f"Position in matrix: row {row}, col {col}")

    # Monte-Carlo
    print("\nMonte-Carlo validation (5000 iterations, sampled)...")

    hits = 0
    for _ in range(5000):
        rand_matrix = np.random.choice(matrix.flatten(), size=(128, 128), replace=True)
        rand_xor = (rand_matrix ^ 127) & 0x7F
        rand_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in rand_xor.flatten()[:5000]])
        if 'cfb' in rand_text.lower():
            hits += 1

    p_value = hits / 5000
    print(f"  Random hits: {hits}/5000")
    print(f"  p-value: {p_value}")
    print(f"  Significant (p < 0.05): {p_value < 0.05}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("CFB VALIDATION SUMMARY")
print("=" * 70)

print("""
The "CFB" findings need careful interpretation:

1. Row 11 XOR 127: If found, this is a specific encoding at a specific row
2. Mod 26: This converts ALL values to letters, so finding 3-letter words
   is more likely (26^3 = 17,576 combinations)
3. Full Matrix XOR 127: Longer text = higher probability of 3-letter patterns

Short 3-letter patterns like "CFB" have HIGH random probability.
Only MULTIPLE independent findings of CFB would be significant.
""")
