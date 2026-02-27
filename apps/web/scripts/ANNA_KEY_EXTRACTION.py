#!/usr/bin/env python3
"""
ANNA Matrix - KEY EXTRACTION Analysis
=====================================
Focused on the discovered patterns that contain keys/passwords
"""

import json
import numpy as np

# Load matrix
with open('../public/data/anna-matrix.json', 'r') as f:
    data = json.load(f)

def safe_int(v):
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    return 0

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.int64)

def to_ascii(arr):
    """Convert array to ASCII string"""
    return ''.join([chr(abs(v) % 256) if 32 <= abs(v) % 256 <= 126 else '.' for v in arr])

print("=" * 80)
print("ANNA MATRIX - KEY EXTRACTION ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# KEY FINDING 1: Row XOR pairs with "key"
# ============================================================================
print("=" * 80)
print("KEY FINDING 1: XOR PAIRS CONTAINING 'KEY'")
print("=" * 80)

key_pairs = [(29, 114), (36, 49)]
for r1, r2 in key_pairs:
    xor_result = matrix[r1, :] ^ matrix[r2, :]
    text = to_ascii(xor_result)
    print(f"\nRow {r1} XOR Row {r2}:")
    print(f"  Full text: {text}")

    # Find position of 'key' in text
    text_lower = text.lower()
    pos = text_lower.find('key')
    if pos >= 0:
        print(f"  'key' found at position {pos}")
        print(f"  Context: ...{text[max(0,pos-10):pos+20]}...")
        print(f"  Values at key position: {xor_result[pos:pos+3]}")

print()

# ============================================================================
# KEY FINDING 2: Row XOR pairs with "egg"
# ============================================================================
print("=" * 80)
print("KEY FINDING 2: XOR PAIRS CONTAINING 'EGG'")
print("=" * 80)

egg_pairs = [(4, 115), (39, 104)]
for r1, r2 in egg_pairs:
    xor_result = matrix[r1, :] ^ matrix[r2, :]
    text = to_ascii(xor_result)
    print(f"\nRow {r1} XOR Row {r2}:")
    print(f"  Full text: {text}")

    text_lower = text.lower()
    pos = text_lower.find('egg')
    if pos >= 0:
        print(f"  'egg' found at position {pos}")
        print(f"  Context: ...{text[max(0,pos-10):pos+20]}...")

print()

# ============================================================================
# KEY FINDING 3: Row XOR pairs with "676" and "576"
# ============================================================================
print("=" * 80)
print("KEY FINDING 3: XOR PAIRS CONTAINING '676' AND '576'")
print("=" * 80)

signal_pairs = [(16, 72, "676"), (16, 81, "576")]
for r1, r2, keyword in signal_pairs:
    xor_result = matrix[r1, :] ^ matrix[r2, :]
    text = to_ascii(xor_result)
    print(f"\nRow {r1} XOR Row {r2} (searching for '{keyword}'):")
    print(f"  Full text: {text}")

    pos = text.find(keyword)
    if pos >= 0:
        print(f"  '{keyword}' found at position {pos}")
        print(f"  Context: ...{text[max(0,pos-10):pos+20]}...")

print()

# ============================================================================
# KEY FINDING 4: "moon" in XOR pair
# ============================================================================
print("=" * 80)
print("KEY FINDING 4: XOR PAIR WITH 'MOON'")
print("=" * 80)

xor_result = matrix[12, :] ^ matrix[105, :]
text = to_ascii(xor_result)
print(f"\nRow 12 XOR Row 105:")
print(f"  Full text: {text}")

text_lower = text.lower()
pos = text_lower.find('moon')
if pos >= 0:
    print(f"  'moon' found at position {pos}")
    print(f"  Context: ...{text[max(0,pos-10):pos+20]}...")

print()

# ============================================================================
# KEY FINDING 5: Diagonal offset 66 "Key" location
# ============================================================================
print("=" * 80)
print("KEY FINDING 5: DIAGONAL OFFSET 66 - THE 'KEY' POSITION")
print("=" * 80)

print("\nFull diagonal offset 66:")
diag_vals = []
diag_text = []
for i in range(128):
    j = i + 66
    if 0 <= j < 128:
        val = matrix[i, j]
        diag_vals.append(val)
        char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
        diag_text.append(char)

print(f"  Text: {''.join(diag_text)}")
print(f"  Length: {len(diag_text)} characters")

# Key is at positions 8, 9, 10
print("\nDetailed 'Key' extraction:")
for i in range(6, 14):
    j = i + 66
    if 0 <= j < 128:
        val = matrix[i, j]
        char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
        signed_char = chr(val % 256) if 0 <= val % 256 <= 127 else '.'
        print(f"  Matrix[{i:2d},{j:3d}] = {val:5d} | abs mod 256 = {abs(val) % 256:3d} = '{char}' | signed mod 256 = {val % 256:3d}")

print()

# ============================================================================
# KEY FINDING 6: Row 7 and Row 36 Analysis (both sum to 11 × 676)
# ============================================================================
print("=" * 80)
print("KEY FINDING 6: ROWS 7 AND 36 (BOTH SUM TO 11 × 676 = 7436)")
print("=" * 80)

row7 = matrix[7, :]
row36 = matrix[36, :]

print(f"\nRow 7:")
print(f"  Sum: {row7.sum()} = {row7.sum() // 676} × 676")
print(f"  As ASCII: {to_ascii(row7)}")

print(f"\nRow 36:")
print(f"  Sum: {row36.sum()} = {row36.sum() // 676} × 676")
print(f"  As ASCII: {to_ascii(row36)}")

print(f"\nRow 7 XOR Row 36:")
xor_7_36 = row7 ^ row36
print(f"  XOR text: {to_ascii(xor_7_36)}")

print(f"\nRow 7 + Row 36 (element-wise):")
add_7_36 = row7 + row36
print(f"  Sum text: {to_ascii(add_7_36)}")

print()

# ============================================================================
# KEY FINDING 7: Position 576 patterns
# ============================================================================
print("=" * 80)
print("KEY FINDING 7: POSITION 576 PATTERNS (i × j = 576)")
print("=" * 80)

patterns_576 = []
for i in range(1, 128):
    for j in range(1, 128):
        if i * j == 576:
            val = matrix[i, j]
            char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
            patterns_576.append((i, j, val, char))
            print(f"  {i:3d} × {j:3d} = 576 -> Matrix[{i},{j}] = {val:5d} = '{char}'")

print("\nKey insight: Matrix[24,24] = -75, which is the same value as Matrix[8,74] (the 'K' in 'Key')")
print("  24 × 24 = 576 = Message 576!")
print("  8 × 74 + 84 = 676 = Computors!")
print()

# ============================================================================
# KEY FINDING 8: The Easter Egg coordinates
# ============================================================================
print("=" * 80)
print("KEY FINDING 8: EASTER EGG COORDINATE ANALYSIS")
print("=" * 80)

# EASTER = 69+65+83+84+69+82 = 452
# EGG = 69+71+71 = 211
# EASTER EGG = 663
# 663 + 13 = 676

print("EASTER ASCII values: E=69, A=65, S=83, T=84, E=69, R=82")
print("EASTER sum = 69+65+83+84+69+82 = 452")
print("EGG sum = 69+71+71 = 211")
print("EASTER EGG sum = 663")
print("663 + 13 = 676 (Computors!)")
print()

# Use EASTER EGG as coordinates
print("Using 'EASTER' letters as row indices:")
easter_rows = [ord(c) - ord('A') for c in "EASTER"]
print(f"  Row indices: {easter_rows}")  # [4, 0, 18, 19, 4, 17]

# Read those rows as columns
combined = []
for i, row_idx in enumerate(easter_rows):
    combined.append(matrix[row_idx, :])

print(f"\nConcatenating rows {easter_rows}:")
concat = np.concatenate(combined)
print(f"  First 100 chars as ASCII: {to_ascii(concat[:100])}")

print()

# ============================================================================
# KEY FINDING 9: The "33" positions (33 days between Blood Moon and Easter)
# ============================================================================
print("=" * 80)
print("KEY FINDING 9: POSITION 33 PATTERNS")
print("=" * 80)

print(f"Matrix[33,33] = {matrix[33,33]} (26 = letters in alphabet)")
print()

# Row 33 and Column 33
print(f"Row 33 as ASCII: {to_ascii(matrix[33, :])}")
print(f"Column 33 as ASCII: {to_ascii(matrix[:, 33])}")
print()

# Matrix values where i=33 or j=33
print("Diagonal crossing at row 33:")
for j in range(30, 40):
    print(f"  Matrix[33,{j}] = {matrix[33,j]}")
print()

# ============================================================================
# KEY FINDING 10: Extract potential password/key
# ============================================================================
print("=" * 80)
print("KEY FINDING 10: POTENTIAL KEY/PASSWORD EXTRACTION")
print("=" * 80)

# Combine all significant positions
key_positions = [
    (8, 74),   # K
    (9, 75),   # e
    (10, 76),  # y
    (24, 24),  # 576 position
    (33, 33),  # Blood Moon - Easter (26)
    (6, 96),   # 576 position with value 26
]

print("Values at key positions:")
key_values = []
for i, j in key_positions:
    val = matrix[i, j]
    key_values.append(val)
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    print(f"  Matrix[{i},{j}] = {val} = '{char}'")

print(f"\nKey values: {key_values}")
print(f"Sum of key values: {sum(key_values)}")
print()

# XOR all key values
xor_result = 0
for v in key_values:
    xor_result ^= v
print(f"XOR of all key values: {xor_result}")
print()

# ============================================================================
# KEY FINDING 11: Search for hidden Qubic addresses
# ============================================================================
print("=" * 80)
print("KEY FINDING 11: SEARCHING FOR QUBIC ADDRESS PATTERNS")
print("=" * 80)

# Qubic addresses are 60 uppercase letters A-Z
# Look for sequences of values in range 65-90 (A-Z)

print("Searching for sequences of 10+ uppercase letter values...")
for i in range(128):
    row = matrix[i, :]
    sequence = []
    start_pos = 0
    for j, val in enumerate(row):
        abs_val = abs(val) % 256
        if 65 <= abs_val <= 90:
            if len(sequence) == 0:
                start_pos = j
            sequence.append(chr(abs_val))
        else:
            if len(sequence) >= 10:
                print(f"  Row {i}, pos {start_pos}-{j-1}: {''.join(sequence)}")
            sequence = []
    if len(sequence) >= 10:
        print(f"  Row {i}, pos {start_pos}-127: {''.join(sequence)}")

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("FINAL SUMMARY - KEY EXTRACTION RESULTS")
print("=" * 80)

print("""
DISCOVERED KEYS:

1. "Key" at diagonal offset 66, position (8,74):
   Matrix[8,74] = -75 = 'K'
   Matrix[9,75] = 101 = 'e'
   Matrix[10,76] = -121 = 'y'

2. Signal 576 Connection:
   Matrix[24,24] = -75 (same as 'K'!)
   24 × 24 = 576 = Message 576

3. Blood Moon - Easter Connection:
   Matrix[33,33] = 26
   33 = days between 03.03.2026 and Easter

4. XOR Row Pairs with Keywords:
   - Row 29 XOR Row 114 = "key"
   - Row 36 XOR Row 49 = "key"
   - Row 4 XOR Row 115 = "egg"
   - Row 12 XOR Row 105 = "moon"
   - Row 16 XOR Row 72 = "676"
   - Row 16 XOR Row 81 = "576"

5. Mathematical Signature:
   8 × 74 + 84 = 676 = Computors
   6 × 96 = 576, Matrix[6,96] = 26

INTERPRETATION:
The "Key" in the matrix appears to be a COORDINATE KEY.
- Position (8,74) for "Key"
- Position (24,24) for "576"
- Position (33,33) for "Blood Moon - Easter"

These coordinates might be:
- Wallet derivation indices
- Message decryption keys
- Claim verification codes
""")
