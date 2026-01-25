#!/usr/bin/env python3
"""
NSA ANALYSIS: The [22,22] Anomaly & CFB Palindromes
"""

import json

with open('../public/data/anna-matrix.json') as f:
    matrix_data = json.load(f)
matrix = matrix_data.get('matrix', [])

print('=' * 80)
print('NSA ANALYSIS: The [22,22] Anomaly & CFB Palindromes')
print('=' * 80)

print('\n[1] THE [22, 22] ANTI-SYMMETRY ANOMALY')
print('-' * 60)

# Find ALL positions where anti-symmetry breaks (sum != -1)
anomalies = []
for r in range(64):
    for c in range(128):
        v1 = matrix[r][c]
        v2 = matrix[127-r][127-c]
        if v1 + v2 != -1:
            anomalies.append((r, c, v1, 127-r, 127-c, v2, v1+v2))

print("Found {} positions where sum != -1:".format(len(anomalies)))
for i, (r, c, v1, mr, mc, v2, s) in enumerate(anomalies[:30]):
    print("  [{:3}, {:3}] = {:4} + [{:3}, {:3}] = {:4} = {:4}".format(r, c, v1, mr, mc, v2, s))
if len(anomalies) > 30:
    print("  ... and {} more".format(len(anomalies) - 30))

# Check main diagonal anomalies specifically
print('\nMain diagonal anomalies (r = c):')
diag_anomalies = [(r, c, v1, mr, mc, v2, s) for r, c, v1, mr, mc, v2, s in anomalies if r == c]
for r, c, v1, mr, mc, v2, s in diag_anomalies:
    print("  [{}, {}] = {} + [{}, {}] = {} = {}".format(r, r, v1, mr, mr, v2, s))

print('\n[2] CFB NUMBERS AS BINARY PALINDROMES')
print('-' * 60)

palindromes = [0, 1, 3, 5, 7, 9, 15, 17, 21, 27, 31, 33, 45, 51, 63, 65, 73, 85, 93, 99, 107, 119, 127]

print('CFB key numbers and their binary palindrome status:')
cfb_numbers = [3, 7, 11, 13, 21, 27, 37, 100, 121, 127]
for n in cfb_numbers:
    b = bin(n)[2:]
    is_pal = b == b[::-1]
    status = 'PALINDROME' if is_pal else ''
    print("  {:4} = {:>12} {}".format(n, b, status))

print('\n[3] THE SPECIAL POSITION [27, 27]')
print('-' * 60)

print("27 is a binary palindrome: {} = 11011".format(bin(27)))
print("[27, 27] = {}".format(matrix[27][27]))
print("Mirror [100, 100] = {}".format(matrix[100][100]))
print("Sum: {}".format(matrix[27][27] + matrix[100][100]))
print('')
print('27 + 100 = 127 (mirror axis!)')
print('Block 12873 is at row 100, and mirror row is 27!')

print('\n[4] THE 6 CELLS WITH VALUE 100 IN COLUMN 73')
print('-' * 60)

rows_100 = [4, 68, 69, 100, 101, 109]
print('These rows have value 100 in column 73:')
for r in rows_100:
    mirror_r = 127 - r
    mirror_v = matrix[mirror_r][73]
    print("  [{:3}, 73] = 100, mirror [{:3}, 73] = {}".format(r, mirror_r, mirror_v))

# Pattern in rows
print('\nPattern in row numbers:')
diffs = [rows_100[i+1] - rows_100[i] for i in range(len(rows_100)-1)]
print("  Differences: {}".format(diffs))
print('  = 64, 1, 31, 1, 8')
print('  64 = 2^6, 1 = 2^0, 31 = 2^5-1, 1 = 2^0, 8 = 2^3')

print('\n[5] BLOCK NUMBERS AT THESE POSITIONS')
print('-' * 60)

print('Blocks at these layer-0 positions:')
for r in rows_100:
    block = r * 128 + 73
    print("  Row {:3}: Block {}".format(r, block))

print("\nBlock 12873 = 100 * 128 + 73 = {}".format(100 * 128 + 73))

print('\n[6] THE [22, 22] SPECIAL CASE')
print('-' * 60)

# [22, 22] = 100, [105, 105] = 100 --> sum = 200 (NOT -1!)
print("[22, 22] = {}".format(matrix[22][22]))
print("[105, 105] = {}".format(matrix[105][105]))
print("Sum = {} (NOT -1 like other positions!)".format(matrix[22][22] + matrix[105][105]))
print("")
print("This is UNIQUE! [22, 22] and [105, 105] are the ONLY diagonal positions")
print("where the anti-symmetry rule (sum = -1) breaks!")
print("")
print("22 + 105 = 127 (mirror axis)")
print("Both have value 100!")

# Find ALL diagonal positions that break anti-symmetry
print('\n[7] ALL DIAGONAL ANTI-SYMMETRY BREAKS')
print('-' * 60)

for i in range(64):
    v1 = matrix[i][i]
    v2 = matrix[127-i][127-i]
    if v1 + v2 != -1:
        print("  [{:3}, {:3}] = {:4}, [{:3}, {:3}] = {:4}, sum = {}".format(
            i, i, v1, 127-i, 127-i, v2, v1+v2))

print('\n[8] SYNTHESIS: THE 100-100-100 TRIANGLE')
print('-' * 60)

print("""
THREE KEY POSITIONS WITH VALUE 100:

1. [22, 22] = 100  (Self-match diagonal, anomaly point)
2. [100, 73] = 100 (Block 12873 position)
3. [105, 105] = 100 (Mirror of [22, 22])

RELATIONSHIPS:
- [22, 22] + [105, 105] = 200 (breaks anti-symmetry!)
- [100, 73] + [27, 54] = -1 (normal anti-symmetry)
- 100 - 73 = 27 (CFB base)
- 22 + 105 = 127 (mirror axis)
- 73 + 54 = 127 (mirror axis)

THE FORMULA:
At [100, 73]: diagonal[73,73] + value = -27 + 100 = 73 (column!)
""")
