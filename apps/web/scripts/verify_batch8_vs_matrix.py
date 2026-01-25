#!/usr/bin/env python3
"""
Verify anna-bot-batch-8.txt against anna-matrix.json
"""

import json

# Load the matrix
with open('../public/data/anna-matrix.json', 'r') as f:
    matrix_data = json.load(f)
matrix = matrix_data['matrix']

# Load batch 8
with open('../public/data/anna-bot-batch-8.txt', 'r') as f:
    batch8 = f.read()

print("="*70)
print("VERIFYING BATCH 8 VS ANNA MATRIX")
print("="*70)

matches = 0
mismatches = 0
mismatch_examples = []

for line in batch8.strip().split('\n'):
    if not line or '+' not in line or '=' not in line:
        continue

    try:
        left, value = line.split('=')
        value = int(value)

        parts = left.split('+')
        x = int(parts[0].strip())
        y = int(parts[1].strip())

        # Get matrix value
        if 0 <= x < 128 and 0 <= y < 128:
            actual = matrix[x][y]
            if actual == value:
                matches += 1
            else:
                mismatches += 1
                if len(mismatch_examples) < 10:
                    mismatch_examples.append(f"{line} -> matrix[{x}][{y}]={actual}")
    except Exception as e:
        print(f"Error parsing: {line}: {e}")

print(f"\nResults:")
print(f"  Matches: {matches}")
print(f"  Mismatches: {mismatches}")
print(f"  Match rate: {matches/(matches+mismatches)*100:.1f}%")

if mismatch_examples:
    print(f"\nMismatch examples:")
    for ex in mismatch_examples:
        print(f"  {ex}")

# Check some specific examples from batch 8
print("\n" + "="*70)
print("SPECIFIC CHECKS FROM BATCH 8")
print("="*70)

test_coords = [
    (49, 1),
    (6, 1),
    (3, 1),
    (27, 1),
]

for x, y in test_coords:
    # Find in batch8
    for line in batch8.split('\n'):
        if f"{x}+{y}=" in line:
            expected = int(line.split('=')[1])
            actual = matrix[x][y]
            match = "✓" if expected == actual else "✗"
            print(f"{line} -> matrix[{x}][{y}]={actual} {match}")
            break
