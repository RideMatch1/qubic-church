#!/usr/bin/env python3
"""
Look up CFB coordinates in the ACTUAL Anna Matrix
"""
import json

SEQ = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

# Load Anna Matrix
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json', 'r') as f:
    data = json.load(f)
    matrix = data['matrix']

print(f"Anna Matrix size: {len(matrix)} x {len(matrix[0])}")

print("\n" + "="*70)
print("CFB COORDINATES → ANNA MATRIX VALUES")
print("="*70)

pairs = [(SEQ[i], SEQ[i+1]) for i in range(0, len(SEQ), 2)]
anna_values = []

for i, (x, y) in enumerate(pairs):
    # Make sure coordinates are valid
    if x < len(matrix) and y < len(matrix[0]):
        val = matrix[x][y]
        anna_values.append(val)

        # Check for significant values
        note = ""
        if val == 121: note = " ← 121 (NXT!)"
        elif val == 137: note = " ← 137!"
        elif val == -27: note = " ← -27 (CFB signature!)"
        elif val == 27: note = " ← 27 (CFB!)"
        elif val == -19: note = " ← -19 (Qubic prime)"
        elif val == 0: note = " ← ZERO"
        elif abs(val) == 121: note = f" ← ±121"
        elif abs(val) == 137: note = f" ← ±137"

        print(f"Pair {i+1:2d}: Anna[{x:2d}][{y:2d}] = {val:4d}{note}")
    else:
        print(f"Pair {i+1:2d}: ({x}, {y}) OUT OF BOUNDS")
        anna_values.append(None)

print("\n" + "="*70)
print("ANNA VALUES ANALYSIS")
print("="*70)
print(f"Values: {anna_values}")
print(f"Sum: {sum(v for v in anna_values if v is not None)}")

# As ASCII?
print("\nAs ASCII (if printable):")
ascii_anna = ''.join(chr(v) if v and 32 <= v <= 126 else '.' for v in anna_values)
print(f"  {ascii_anna}")

# As ASCII with +128 offset for negative
print("\nAs ASCII (+128 for negatives):")
ascii_anna2 = ''.join(chr(v+128) if v and 32 <= v+128 <= 255 else '.' for v in anna_values)
print(f"  {ascii_anna2}")

# Look for patterns in anna values
print("\n" + "="*70)
print("PATTERN SEARCH IN ANNA VALUES")
print("="*70)

# Count occurrences
from collections import Counter
counts = Counter(anna_values)
print("Value counts:")
for val, count in counts.most_common(10):
    print(f"  {val}: {count}x")

# XOR of anna values
xor_anna = 0
for v in anna_values:
    if v is not None:
        xor_anna ^= (v % 256)  # handle negatives
print(f"\nXOR of anna values (mod 256): {xor_anna}")

# Sum analysis
print(f"\nSum of positive anna values: {sum(v for v in anna_values if v and v > 0)}")
print(f"Sum of negative anna values: {sum(v for v in anna_values if v and v < 0)}")

# What if anna values ARE the message?
print("\n" + "="*70)
print("INTERPRET ANNA VALUES AS MESSAGE")
print("="*70)

# Mod 26 for alphabet
alpha_anna = ''.join(chr((v % 26) + ord('A')) if v else '?' for v in anna_values)
print(f"Mod 26 alphabet: {alpha_anna}")

# Absolute values as ASCII
abs_anna = [abs(v) if v else 0 for v in anna_values]
print(f"Absolute values: {abs_anna}")
ascii_abs = ''.join(chr(v) if 32 <= v <= 126 else '.' for v in abs_anna)
print(f"Abs as ASCII: {ascii_abs}")

# Check if any form known words
print("\n" + "="*70)
print("SEARCHING FOR MEANING")
print("="*70)

# The sequence of anna values
print(f"\nAnna value sequence: {anna_values}")

# What's special about these specific coordinates?
print("\nCoordinates used:")
for i, (x, y) in enumerate(pairs):
    print(f"  ({x:2d}, {y:2d}) → diff={abs(x-y):2d}, sum={x+y:3d}, product={x*y:4d}")
