#!/usr/bin/env python3
"""
DEEP CONNECTIONS: The Two "100" Positions
=========================================
[22, 22] = 100 (self-match position)
[100, 73] = 100 (Block 12873 position)

Why do both have the same value?
"""

import json

# Load matrix
with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json') as f:
    matrix_data = json.load(f)
matrix = matrix_data.get('matrix', [])

print("=" * 80)
print("DEEP CONNECTIONS: The Two '100' Positions")
print("=" * 80)

# Position 1: [22, 22]
pos1_row, pos1_col = 22, 22
pos1_val = matrix[pos1_row][pos1_col]
pos1_mirror_row, pos1_mirror_col = 127 - pos1_row, 127 - pos1_col  # [105, 105]
pos1_mirror_val = matrix[pos1_mirror_row][pos1_mirror_col]

# Position 2: [100, 73]
pos2_row, pos2_col = 100, 73
pos2_val = matrix[pos2_row][pos2_col]
pos2_mirror_row, pos2_mirror_col = 127 - pos2_row, 127 - pos2_col  # [27, 54]
pos2_mirror_val = matrix[pos2_mirror_row][pos2_mirror_col]

print("\n" + "-" * 80)
print("BASIC COMPARISON")
print("-" * 80)

print(f"\nPosition 1: [{pos1_row}, {pos1_col}]")
print(f"  Value: {pos1_val}")
print(f"  Mirror [{pos1_mirror_row}, {pos1_mirror_col}]: {pos1_mirror_val}")
print(f"  Sum with mirror: {pos1_val + pos1_mirror_val}")
print(f"  Diff with mirror: {pos1_val - pos1_mirror_val}")

print(f"\nPosition 2: [{pos2_row}, {pos2_col}]")
print(f"  Value: {pos2_val}")
print(f"  Mirror [{pos2_mirror_row}, {pos2_mirror_col}]: {pos2_mirror_val}")
print(f"  Sum with mirror: {pos2_val + pos2_mirror_val}")
print(f"  Diff with mirror: {pos2_val - pos2_mirror_val}")

print("\n" + "-" * 80)
print("COORDINATE RELATIONSHIPS")
print("-" * 80)

print(f"\nPosition 1: [{pos1_row}, {pos1_col}]")
print(f"  Row = Col (on diagonal)")
print(f"  22 × 2 = 44")
print(f"  22 + 22 = 44")
print(f"  22 = 2 × 11")

print(f"\nPosition 2: [{pos2_row}, {pos2_col}]")
print(f"  Row - Col = {pos2_row - pos2_col} = 27 (CFB base!)")
print(f"  Row + Col = {pos2_row + pos2_col} = 173")
print(f"  100 = 10²")
print(f"  73 = prime")

print("\n" + "-" * 80)
print("MIRROR RELATIONSHIPS")
print("-" * 80)

print(f"\nMirror of Position 1: [{pos1_mirror_row}, {pos1_mirror_col}] = [105, 105]")
print(f"  105 = 3 × 5 × 7")
print(f"  105 - 22 = 83 (prime)")
print(f"  105 = 127 - 22")

print(f"\nMirror of Position 2: [{pos2_mirror_row}, {pos2_mirror_col}] = [27, 54]")
print(f"  27 = 3³ = CFB base!")
print(f"  54 = 2 × 27 = 2 × 3³")
print(f"  27 + 54 = 81 = 3⁴")

print("\n" + "-" * 80)
print("CROSS-RELATIONSHIPS")
print("-" * 80)

# What happens at [22, 73] and [100, 22]?
cross1_val = matrix[22][73]
cross2_val = matrix[100][22]
print(f"\nCross positions:")
print(f"  [{pos1_row}, {pos2_col}] = [22, 73] = {cross1_val}")
print(f"  [{pos2_row}, {pos1_col}] = [100, 22] = {cross2_val}")

# Check all cells with value 100
print("\n" + "-" * 80)
print("ALL CELLS WITH VALUE 100")
print("-" * 80)

value_100_cells = []
for row in range(128):
    for col in range(128):
        if matrix[row][col] == 100:
            value_100_cells.append((row, col))

print(f"\nFound {len(value_100_cells)} cells with value 100:")
for r, c in value_100_cells:
    mirror_r, mirror_c = 127 - r, 127 - c
    mirror_v = matrix[mirror_r][mirror_c]
    print(f"  [{r:3}, {c:3}] = 100, mirror [{mirror_r:3}, {mirror_c:3}] = {mirror_v}")

# Check all cells with value -101 (mirror of 100 in Block 12873 context)
print("\n" + "-" * 80)
print("ALL CELLS WITH VALUE -101")
print("-" * 80)

value_m101_cells = []
for row in range(128):
    for col in range(128):
        if matrix[row][col] == -101:
            value_m101_cells.append((row, col))

print(f"\nFound {len(value_m101_cells)} cells with value -101:")
for r, c in value_m101_cells:
    mirror_r, mirror_c = 127 - r, 127 - c
    mirror_v = matrix[mirror_r][mirror_c]
    print(f"  [{r:3}, {c:3}] = -101, mirror [{mirror_r:3}, {mirror_c:3}] = {mirror_v}")

# Pattern analysis: What's special about value 100?
print("\n" + "-" * 80)
print("NUMERICAL PROPERTIES OF 100")
print("-" * 80)

print(f"\n100 in different systems:")
print(f"  Decimal: 100")
print(f"  Binary: {bin(100)}")
print(f"  Hex: {hex(100)} = 0x64")
print(f"  ASCII 0x64 = 'd'")
print(f"  100 = 10² = 4 × 25 = 2² × 5²")

print(f"\nXOR relationships:")
print(f"  100 XOR 127 = {100 ^ 127} = 27 (CFB base!)")
print(f"  100 XOR 73 = {100 ^ 73}")
print(f"  100 XOR 22 = {100 ^ 22}")
print(f"  100 XOR 105 = {100 ^ 105}")

print(f"\nMod relationships:")
print(f"  100 mod 27 = {100 % 27}")
print(f"  100 mod 121 = {100 % 121}")
print(f"  100 mod 11 = {100 % 11} = 1")

# Deep dive: The path from [22,22] to [100,73]
print("\n" + "-" * 80)
print("PATH FROM [22,22] TO [100,73]")
print("-" * 80)

print(f"\nCoordinate differences:")
print(f"  Row diff: 100 - 22 = 78")
print(f"  Col diff: 73 - 22 = 51")
print(f"  78 + 51 = 129")
print(f"  78 - 51 = 27 (CFB!)")
print(f"  78 = 2 × 3 × 13")
print(f"  51 = 3 × 17")
print(f"  GCD(78, 51) = {__import__('math').gcd(78, 51)} = 3")

print(f"\nVector from [22,22] to [100,73]:")
print(f"  Direction: (+78, +51)")
print(f"  Simplified: (+26, +17) × 3")
print(f"  26 = 2 × 13")
print(f"  17 = prime")

# Check intermediate positions along the path
print("\n" + "-" * 80)
print("INTERMEDIATE POSITIONS ON PATH")
print("-" * 80)

print("\nChecking positions along the line from [22,22] to [100,73]:")
for t in [0, 0.25, 0.5, 0.75, 1.0]:
    r = int(22 + t * 78)
    c = int(22 + t * 51)
    if 0 <= r < 128 and 0 <= c < 128:
        v = matrix[r][c]
        print(f"  t={t:.2f}: [{r:3}, {c:3}] = {v:4}")

# The diagonal through [100, 73]
print("\n" + "-" * 80)
print("DIAGONAL ANALYSIS (Row - Col = 27)")
print("-" * 80)

print("\nAll positions where Row - Col = 27:")
diag_27_values = []
for row in range(27, 128):
    col = row - 27
    if 0 <= col < 128:
        v = matrix[row][col]
        diag_27_values.append((row, col, v))
        if row <= 35 or row >= 95 or (row >= 98 and row <= 102):
            print(f"  [{row:3}, {col:3}] = {v:4}")

print(f"\nStatistics for diagonal Row - Col = 27:")
values = [v for _, _, v in diag_27_values]
print(f"  Count: {len(values)}")
print(f"  Sum: {sum(values)}")
print(f"  Mean: {sum(values)/len(values):.2f}")
print(f"  Min: {min(values)}")
print(f"  Max: {max(values)}")

# Check if any cell on this diagonal has value 100
val_100_on_diag = [(r, c, v) for r, c, v in diag_27_values if v == 100]
print(f"\n  Cells with value 100 on this diagonal: {len(val_100_on_diag)}")
for r, c, v in val_100_on_diag:
    print(f"    [{r}, {c}] = {v}")

# Final synthesis
print("\n" + "=" * 80)
print("SYNTHESIS: The 100-100 Connection")
print("=" * 80)

print("""
1. TWO POSITIONS SHARE VALUE 100:
   - [22, 22] on main diagonal (self-match)
   - [100, 73] on Row-Col=27 diagonal (Block 12873)

2. BOTH CONNECT TO 27:
   - [22, 22]: 100 XOR 127 = 27
   - [100, 73]: 100 - 73 = 27

3. THE PATH BETWEEN THEM:
   - Vector: (+78, +51) = 3 × (26, 17)
   - Factor 3 = CFB ternary base
   - Difference: 78 - 51 = 27 (CFB!)

4. MIRROR RELATIONSHIPS:
   - [22, 22] mirror is [105, 105] with same value 100
   - [100, 73] mirror is [27, 54] (both CFB numbers)
   - [27, 54] value = -101 → diff = 201 = 12873 mod 576

5. HYPOTHESIS:
   The two "100" positions mark:
   - [22, 22] = Origin point (fixed reference)
   - [100, 73] = Destination point (Block 12873 marker)

   The relationship between them encodes CFB's signature.
""")

# Save results
results = {
    'position_22_22': {
        'coords': [22, 22],
        'value': pos1_val,
        'mirror': [105, 105],
        'mirror_value': pos1_mirror_val
    },
    'position_100_73': {
        'coords': [100, 73],
        'value': pos2_val,
        'mirror': [27, 54],
        'mirror_value': pos2_mirror_val
    },
    'all_cells_with_100': value_100_cells,
    'all_cells_with_minus_101': value_m101_cells,
    'diagonal_row_minus_col_27': [(r, c, v) for r, c, v in diag_27_values]
}

with open('DEEP_CONNECTIONS_100_100_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to DEEP_CONNECTIONS_100_100_RESULTS.json")
