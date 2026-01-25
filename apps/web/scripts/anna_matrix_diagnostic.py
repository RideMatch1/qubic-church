#!/usr/bin/env python3
"""
Anna Matrix Diagnostic - Understanding the Discrepancy
======================================================

The Twitter responses don't match our matrix. Let's figure out why.
"""

import json

# Load the matrix
with open('../public/data/anna-matrix.json', 'r') as f:
    matrix_data = json.load(f)

matrix = matrix_data.get('matrix', [])
print(f"Matrix dimensions: {len(matrix)} x {len(matrix[0]) if matrix else 0}")

# Load the Twitter responses
with open('anna_twitter_data.json', 'r') as f:
    twitter_data = json.load(f)

responses = twitter_data['responses']
print(f"Twitter responses: {len(responses)}")

print("\n" + "="*70)
print("TESTING DIFFERENT COORDINATE INTERPRETATIONS")
print("="*70)

# Test different interpretations
def test_interpretation(name, get_indices):
    """Test a specific coordinate interpretation"""
    matches = 0
    mismatches = 0
    examples = []

    for entry in responses:
        x, y = entry['x'], entry['y']
        expected = entry['value']

        if expected is None:
            continue

        try:
            row, col = get_indices(x, y)
            if 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
                actual = matrix[row][col]
                if actual == expected:
                    matches += 1
                else:
                    mismatches += 1
                    if len(examples) < 3:
                        examples.append(f"  ({x},{y})={expected} vs matrix[{row}][{col}]={actual}")
        except:
            pass

    print(f"\n{name}:")
    print(f"  Matches: {matches}, Mismatches: {mismatches}")
    if examples:
        print("  Examples of mismatches:")
        for ex in examples:
            print(ex)
    return matches

# Interpretation 1: Direct X,Y with mod 128 for negatives
test_interpretation("Direct X,Y (mod 128)", lambda x, y: (x % 128, y % 128))

# Interpretation 2: Swapped Y,X with mod 128
test_interpretation("Swapped Y,X (mod 128)", lambda x, y: (y % 128, x % 128))

# Interpretation 3: X+64, Y+64 (center at 64,64)
test_interpretation("Centered (X+64, Y+64)", lambda x, y: (x + 64, y + 64))

# Interpretation 4: Centered and swapped
test_interpretation("Centered + Swapped", lambda x, y: (y + 64, x + 64))

# Interpretation 5: Maybe it's Matrix[Y][X] not Matrix[X][Y]
test_interpretation("Matrix[Y][X] direct", lambda x, y: (y % 128, x % 128))

# Let's specifically check some known coordinates
print("\n" + "="*70)
print("SPECIFIC COORDINATE CHECKS")
print("="*70)

test_cases = [
    (6, 33, -93),    # Core Point
    (0, 7, -94),     # Early query
    (0, 1, -38),     # Simple query
    (1, 0, -98),     # Simple query
    (-1, 0, 69),     # Negative X
    (0, -1, -70),    # Negative Y
    (-27, 3, -110),  # CFB's number!
    (-27, 0, -102),
]

print("\nAnna's format: X+Y=Value means 'query at (X,Y) returns Value'")
print()

for x, y, expected in test_cases:
    row_mod = x % 128
    col_mod = y % 128

    print(f"Anna: {x}+{y}={expected}")
    print(f"  Interpretation 1: matrix[{row_mod}][{col_mod}] = {matrix[row_mod][col_mod]}")
    print(f"  Interpretation 2: matrix[{col_mod}][{row_mod}] = {matrix[col_mod][row_mod]}")
    print()

# Let's also check the metadata of the matrix
print("\n" + "="*70)
print("MATRIX METADATA CHECK")
print("="*70)

if 'metadata' in matrix_data:
    print(f"Metadata: {matrix_data['metadata']}")
else:
    print("No metadata field in matrix file")

# Check for other keys
print(f"\nAll keys in matrix_data: {list(matrix_data.keys())}")

# Sample of first few matrix values
print("\nFirst row (matrix[0]):", matrix[0][:20], "...")
print("Second row (matrix[1]):", matrix[1][:20], "...")

# Check row 6, col 33 specifically
print(f"\nSpecific check for 6+33=-93:")
print(f"  matrix[6][33] = {matrix[6][33]}")
print(f"  matrix[33][6] = {matrix[33][6]}")

# Check row 0
print(f"\nRow 0 values at specific columns:")
for col in [0, 1, 7, 10, 11, 12]:
    print(f"  matrix[0][{col}] = {matrix[0][col]}")

# Check what Anna says for row 0
print(f"\nAnna's responses for X=0:")
anna_x0 = [(e['y'], e['value']) for e in responses if e['x'] == 0 and e['value'] is not None]
for y, val in sorted(anna_x0):
    print(f"  0+{y}={val} vs matrix[0][{y % 128}]={matrix[0][y % 128]}")
