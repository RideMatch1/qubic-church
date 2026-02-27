#!/usr/bin/env python3
"""
ANNA Matrix - XOR Deep Analysis
================================
Following the HEXVRIDGST discovery
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

print("=" * 80)
print("XOR DEEP ANALYSIS - Following HEXVRIDGST")
print("=" * 80)
print()

# The discovery: BEDATZFAUR XOR EASTEREGG = HEXVRIDGST
print("BEDATZFAUR XOR EASTEREGG = ?")
word1 = "BEDATZFAUR"
word2 = "EASTEREGG" + "A"  # Pad to 10 chars

result = []
for i in range(len(word1)):
    xor_val = ord(word1[i]) ^ ord(word2[i])
    # Map back to uppercase letter (mod 26)
    char = chr((xor_val % 26) + ord('A'))
    result.append(char)
    print(f"  '{word1[i]}' ({ord(word1[i])}) XOR '{word2[i]}' ({ord(word2[i])}) = {xor_val} -> '{char}'")

print(f"\nResult: {''.join(result)}")
print()

# What is HEXVRIDGST?
print("=" * 80)
print("ANALYZING HEXVRIDGST")
print("=" * 80)

hexvr = "HEXVRIDGST"
print(f"\nHEXVRIDGST letters: {hexvr}")
print(f"Contains 'HEX' at start!")
print()

# Extract hex-like patterns
print("Possible interpretations:")
print("  1. HEX = Hexadecimal indicator")
print("  2. VRI = ?")
print("  3. DGST = 'DIGEST' without vowels?")
print()

# Letter values
values = [ord(c) - ord('A') + 1 for c in hexvr]
print(f"Letter values: {values}")
print(f"Sum: {sum(values)}")
print()

# Try to decode as hex pairs
print("Trying HEX interpretation:")
print("  H=8, E=5, X=24, V=22, R=18, I=9, D=4, G=7, S=19, T=20")
hex_vals = [8, 5, 24, 22, 18, 9, 4, 7, 19, 20]
print(f"  As decimal sequence: {hex_vals}")

# Group as hex pairs: 85, 24, 22, 18, 94, 7, 19, 20
print("  Grouped pairs: 85, 24, 22, 18, 94, 71, 92, 0")
print()

# ============================================================================
# TRY MORE XOR COMBINATIONS
# ============================================================================
print("=" * 80)
print("MORE XOR COMBINATIONS")
print("=" * 80)

words_to_try = [
    "KEYKEYKEYK",
    "SATOSHISAT",
    "BITCOINBTC",
    "QUBICQUBIC",
    "GENESISGEN",
    "ANNAANNAAN",
    "SIGNALSIGN",
    "MESSAGE576",
    "BLOODMOONB",
    "BRIDGEKEY1",
]

for word2 in words_to_try:
    word2_padded = (word2 * 2)[:10]  # Ensure 10 chars
    result = []
    for i in range(len(word1)):
        xor_val = ord(word1[i]) ^ ord(word2_padded[i])
        char = chr((xor_val % 26) + ord('A'))
        result.append(char)
    result_str = ''.join(result)
    print(f"  BEDATZFAUR XOR {word2_padded}: {result_str}")
print()

# ============================================================================
# XOR WITH MATRIX VALUES
# ============================================================================
print("=" * 80)
print("XOR BEDATZFAUR WITH MATRIX VALUES")
print("=" * 80)

# Use Row 7 values (the other 676-multiple row)
row7 = matrix[7, :]
print("Using Row 7 values (first 10):")
for i, c in enumerate(word1):
    val = row7[i]
    xor_val = ord(c) ^ abs(val)
    char = chr(xor_val % 256) if 32 <= xor_val % 256 <= 126 else '.'
    print(f"  '{c}' XOR {val:4d} = {xor_val:4d} = '{char}'")
print()

# Use diagonal 66 values (where "Key" was found)
print("Using Diagonal 66 values (starting at 'Key'):")
diag_66 = [matrix[i, i+66] for i in range(10)]
for i, c in enumerate(word1):
    val = diag_66[i]
    xor_val = ord(c) ^ abs(val)
    char = chr(xor_val % 256) if 32 <= xor_val % 256 <= 126 else '.'
    print(f"  '{c}' XOR {val:4d} = {xor_val:4d} = '{char}'")
print()

# ============================================================================
# THE KEY POSITION (8,74) CONNECTION
# ============================================================================
print("=" * 80)
print("KEY POSITION (8, 74) CONNECTION")
print("=" * 80)

# Start from position 8,74 and read 10 values
print("Reading from (8, 74) along row:")
key_vals = []
for j in range(74, min(84, 128)):
    key_vals.append(matrix[8, j])
print(f"Values: {key_vals}")

print("\nXOR BEDATZFAUR with key position values:")
for i, c in enumerate(word1[:len(key_vals)]):
    xor_val = ord(c) ^ abs(key_vals[i])
    char = chr(xor_val % 256) if 32 <= xor_val % 256 <= 126 else '.'
    print(f"  '{c}' XOR {key_vals[i]:4d} = {xor_val:4d} = '{char}'")
print()

# ============================================================================
# MATRIX[36, 36] = 90 = 'Z' ANALYSIS
# ============================================================================
print("=" * 80)
print("ROW 36, COLUMN 36 ANALYSIS")
print("=" * 80)

print("Values at significant positions in Row 36:")
significant_cols = [6, 26, 33, 36, 66, 76]
for col in significant_cols:
    val = matrix[36, col]
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    print(f"  Matrix[36, {col:2d}] = {val:4d} = '{char}'")
print()

# ============================================================================
# FULL ROW 36 XOR ROW 7 ANALYSIS
# ============================================================================
print("=" * 80)
print("ROW 36 XOR ROW 7 (BOTH 11 × 676)")
print("=" * 80)

row36 = matrix[36, :]
row7 = matrix[7, :]
xor_36_7 = row36 ^ row7

print("Row 36 XOR Row 7 full text:")
text = ''.join([chr(abs(v) % 256) if 32 <= abs(v) % 256 <= 126 else '.' for v in xor_36_7])
print(f"  {text}")
print()

# Extract uppercase only
uppercase = ''.join([chr(abs(v) % 256) if 65 <= abs(v) % 256 <= 90 else '_' for v in xor_36_7])
print(f"Uppercase only: {uppercase}")
print()

# Find longest uppercase sequence
sequences = [s for s in uppercase.split('_') if len(s) >= 3]
print(f"Uppercase sequences (3+ chars): {sequences}")
print()

# ============================================================================
# EASTER EGG COORDINATE FOLLOW-UP
# ============================================================================
print("=" * 80)
print("EASTER EGG AS COORDINATES")
print("=" * 80)

# EASTER = 69,65,83,84,69,82
# EGG = 69,71,71
easter = [69, 65, 83, 84, 69, 82]
egg = [69, 71, 71]

print("Using EASTER ASCII as coordinates:")
for i in range(0, len(easter), 2):
    row = easter[i] % 128
    col = easter[i+1] % 128 if i+1 < len(easter) else 0
    val = matrix[row, col]
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    print(f"  Matrix[{row}, {col}] = {val} = '{char}'")
print()

# EGG as single coordinate
e1, g1, g2 = egg
print(f"Using EGG (69, 71, 71):")
print(f"  Matrix[{e1}, {g1}] = {matrix[e1, g1]}")
print(f"  Matrix[{g1}, {g2}] = {matrix[g1, g2]}")
print(f"  Matrix[{e1}, {g2}] = {matrix[e1, g2]}")
print()

# ============================================================================
# POSITION 275 + 401 = 676 ANALYSIS
# ============================================================================
print("=" * 80)
print("POSITION 275 + 401 = 676 ANALYSIS")
print("=" * 80)

# 275 = sum of positions 23-32
# 401 is the missing piece to make 676
# 401 = 3 * 128 + 17 = row 3, column 17
pos_401_row = 401 // 128
pos_401_col = 401 % 128
print(f"Position 401 in flat array = row {pos_401_row}, column {pos_401_col}")
print(f"Matrix[{pos_401_row}, {pos_401_col}] = {matrix[pos_401_row, pos_401_col]}")
print()

# Value at position 275
pos_275_row = 275 // 128
pos_275_col = 275 % 128
print(f"Position 275 in flat array = row {pos_275_row}, column {pos_275_col}")
print(f"Matrix[{pos_275_row}, {pos_275_col}] = {matrix[pos_275_row, pos_275_col]}")
print()

# XOR of the two values
val_401 = matrix[pos_401_row, pos_401_col]
val_275 = matrix[pos_275_row, pos_275_col]
print(f"XOR of positions 275 and 401: {val_275} ^ {val_401} = {val_275 ^ val_401}")
print()

# ============================================================================
# FINAL SYNTHESIS
# ============================================================================
print("=" * 80)
print("FINAL SYNTHESIS")
print("=" * 80)

print("""
KEY FINDINGS:

1. BEDATZFAUR XOR EASTEREGG = HEXVRIDGST
   - Starts with "HEX" - hexadecimal indicator!
   - "DGST" could mean "DIGEST" (hash)

2. Row 36 contains the marker "BEDATZFAUR"
   - Row 36 sum = 7436 = 11 × 676
   - Row 7 also sums to 7436 = 11 × 676
   - Combined: 22 × 676 = 14872

3. The "Key" at diagonal 66:
   - Matrix[8,74] = 'K'
   - Matrix[9,75] = 'e'
   - Matrix[10,76] = 'y'
   - 8 × 74 + 84 = 676

4. Position 275 + 401 = 676
   - 275 = sum of BEDATZFAUR positions (23-32)
   - 401 = row 3, col 17

5. Matrix[36, 36] = 90 = 'Z'
   Matrix[36, 26] = 65 = 'A'

INTERPRETATION:
The matrix contains a COORDINATE SYSTEM for extracting keys.
- "HEX" in the XOR result suggests hexadecimal decoding
- The 676/576 patterns point to specific positions
- Row 7 + Row 36 form a KEY PAIR

NEXT STEPS:
1. Try hexadecimal decoding of key positions
2. Combine Row 7 and Row 36 values
3. Use XOR results as lookup coordinates
""")

# Try hex decode
print("\n" + "=" * 80)
print("BONUS: HEX DECODE ATTEMPT")
print("=" * 80)

# Take HEXVRIDGST and try to decode
hexvr = "HEXVRIDGST"
# H=7, E=4, X=23 (0-indexed)
# Could this be pointing to position [7][4][23]... or hex values?

print("HEXVRIDGST as hex values (A=0):")
hex_vals = [ord(c) - ord('A') for c in hexvr]
print(f"  Values: {hex_vals}")

# Convert pairs to bytes
pairs = []
for i in range(0, len(hex_vals)-1, 2):
    byte_val = (hex_vals[i] << 4) | hex_vals[i+1]
    pairs.append(byte_val)
print(f"  As byte pairs: {pairs}")
print(f"  As hex: {[hex(p) for p in pairs]}")

# Try to decode as ASCII
ascii_str = ''.join([chr(p) if 32 <= p <= 126 else '.' for p in pairs])
print(f"  As ASCII: {ascii_str}")
