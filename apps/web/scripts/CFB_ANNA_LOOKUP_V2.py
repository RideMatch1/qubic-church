#!/usr/bin/env python3
"""
Look up CFB coordinates in Anna Matrix - try both orderings
"""
import json

SEQ = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json', 'r') as f:
    data = json.load(f)
    matrix = data['matrix']

pairs = [(SEQ[i], SEQ[i+1]) for i in range(0, len(SEQ), 2)]

print("="*70)
print("COMPARISON: Anna[x][y] vs Anna[y][x]")
print("="*70)

vals_xy = []
vals_yx = []

for i, (a, b) in enumerate(pairs):
    val_xy = matrix[a][b] if a < 128 and b < 128 else None
    val_yx = matrix[b][a] if a < 128 and b < 128 else None
    vals_xy.append(val_xy)
    vals_yx.append(val_yx)

    note_xy = ""
    note_yx = ""
    for val, note_ref in [(val_xy, "xy"), (val_yx, "yx")]:
        if val == 121:
            if note_ref == "xy": note_xy = "←121"
            else: note_yx = "←121"
        elif val == -27:
            if note_ref == "xy": note_xy = "←-27"
            else: note_yx = "←-27"
        elif val == 27:
            if note_ref == "xy": note_xy = "←27"
            else: note_yx = "←27"
        elif val == -19:
            if note_ref == "xy": note_xy = "←-19"
            else: note_yx = "←-19"

    print(f"Pair {i+1:2d} ({a:2d},{b:2d}): [{a}][{b}]={val_xy:4d} {note_xy:6s}  [{b}][{a}]={val_yx:4d} {note_yx}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Anna[x][y] values: {vals_xy}")
print(f"Anna[y][x] values: {vals_yx}")
print(f"\nSum [x][y]: {sum(vals_xy)}")
print(f"Sum [y][x]: {sum(vals_yx)}")

# Check for 121, -27, -19 in each
print("\n" + "="*70)
print("KEY VALUES FOUND")
print("="*70)
for name, vals in [("Anna[x][y]", vals_xy), ("Anna[y][x]", vals_yx)]:
    print(f"\n{name}:")
    if 121 in vals: print(f"  121 at position {vals.index(121)+1}")
    if -27 in vals: print(f"  -27 at position {vals.index(-27)+1}")
    if 27 in vals: print(f"  27 at position {vals.index(27)+1}")
    if -19 in vals: print(f"  -19 at position {vals.index(-19)+1}")
    if 137 in vals: print(f"  137 at position {vals.index(137)+1}")
    if -118 in vals: print(f"  -118 at position {vals.index(-118)+1}")

# What about looking at DIFFERENCES between the two?
print("\n" + "="*70)
print("DIFFERENCE: Anna[y][x] - Anna[x][y]")
print("="*70)
diffs = [vals_yx[i] - vals_xy[i] for i in range(len(vals_xy))]
print(f"Differences: {diffs}")
print(f"Sum of diffs: {sum(diffs)}")

# Is the matrix symmetric?
print("\n" + "="*70)
print("SYMMETRY CHECK")
print("="*70)
symmetric_count = sum(1 for i in range(len(vals_xy)) if vals_xy[i] == vals_yx[i])
print(f"Symmetric pairs (same value both ways): {symmetric_count}/{len(pairs)}")

# What if we USE both values?
print("\n" + "="*70)
print("COMBINING BOTH: (Anna[x][y] + Anna[y][x]) / 2")
print("="*70)
combined = [(vals_xy[i] + vals_yx[i]) // 2 for i in range(len(vals_xy))]
print(f"Combined: {combined}")
print(f"Sum: {sum(combined)}")

# XOR both?
print("\n" + "="*70)
print("XOR BOTH: Anna[x][y] XOR Anna[y][x]")
print("="*70)
xored = [vals_xy[i] ^ vals_yx[i] for i in range(len(vals_xy))]
print(f"XORed: {xored}")
