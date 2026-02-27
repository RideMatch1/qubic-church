#!/usr/bin/env python3
"""
ANNA Matrix - Final Extraction
==============================
Using all discovered patterns to extract the final key
"""

import json
import numpy as np
import hashlib

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
print("ANNA MATRIX - FINAL KEY EXTRACTION")
print("=" * 80)
print()

# ============================================================================
# METHOD 1: HEXVRIDGST as coordinates
# ============================================================================
print("=" * 80)
print("METHOD 1: Using HEXVRIDGST as coordinates")
print("=" * 80)

hexvr = "HEXVRIDGST"
# As letter values (A=0)
coords = [ord(c) - ord('A') for c in hexvr]
print(f"HEXVRIDGST as indices: {coords}")
print("  H=7, E=4, X=23, V=21, R=17, I=8, D=3, G=6, S=18, T=19")
print()

# Use as (row, col) pairs
print("Reading as coordinate pairs:")
extracted = []
for i in range(0, len(coords)-1, 2):
    row, col = coords[i], coords[i+1]
    val = matrix[row, col]
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    extracted.append(val)
    print(f"  Matrix[{row:2d}, {col:2d}] = {val:5d} = '{char}'")

print(f"\nExtracted values: {extracted}")
print(f"Sum: {sum(extracted)}")
print()

# Use coords directly as row indices
print("Using HEXVRIDGST indices to read from row 36:")
row36 = matrix[36, :]
values_36 = [row36[c] for c in coords]
text = ''.join([chr(abs(v) % 256) if 32 <= abs(v) % 256 <= 126 else '.' for v in values_36])
print(f"  Values: {values_36}")
print(f"  As text: {text}")
print()

# ============================================================================
# METHOD 2: Row 7 XOR Row 36 as key
# ============================================================================
print("=" * 80)
print("METHOD 2: Row 7 XOR Row 36 as decryption key")
print("=" * 80)

row7 = matrix[7, :]
row36 = matrix[36, :]
key = row7 ^ row36

print("First 20 values of the key (Row 7 XOR Row 36):")
print(f"  {list(key[:20])}")
print()

# Use this key to decrypt something
print("Key applied to diagonal 66 (where 'Key' was found):")
diag_66 = [matrix[i, i+66] for i in range(62)]
decrypted = [diag_66[i] ^ key[i] for i in range(min(len(diag_66), len(key)))]
text = ''.join([chr(abs(v) % 256) if 32 <= abs(v) % 256 <= 126 else '.' for v in decrypted[:40]])
print(f"  Decrypted: {text}")
print()

# ============================================================================
# METHOD 3: 676 positions combined
# ============================================================================
print("=" * 80)
print("METHOD 3: Combining all 676-related positions")
print("=" * 80)

# All positions where i*j = 676 or close
positions_676 = []
for i in range(1, 128):
    for j in range(1, 128):
        if i * j == 676:
            positions_676.append((i, j, matrix[i, j]))

print("Positions where i × j = 676:")
for i, j, val in positions_676:
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    print(f"  {i:3d} × {j:3d} = 676 -> Matrix[{i},{j}] = {val:5d} = '{char}'")
print()

# Build potential key from 676 positions
key_676 = [v for _, _, v in positions_676]
print(f"676 position values: {key_676}")
print(f"Sum: {sum(key_676)}")
print()

# ============================================================================
# METHOD 4: Position (8,74) expansion
# ============================================================================
print("=" * 80)
print("METHOD 4: Expanding from (8, 74) 'Key' position")
print("=" * 80)

# Read in a spiral pattern from (8, 74)
center_r, center_c = 8, 74
print(f"Reading in expanding square from ({center_r}, {center_c}):")

# Read 60 values (Qubic address length)
values = []
r, c = center_r, center_c
for _ in range(60):
    if 0 <= r < 128 and 0 <= c < 128:
        values.append(matrix[r, c])
    # Move in a pattern
    c += 1
    if c >= 128:
        c = 0
        r += 1
    if r >= 128:
        r = 0

print(f"First 30 values: {values[:30]}")

# Convert to uppercase letters (mod 26 + A)
address = ''.join([chr(abs(v) % 26 + ord('A')) for v in values])
print(f"As Qubic-like address: {address}")
print()

# ============================================================================
# METHOD 5: Hash-based extraction
# ============================================================================
print("=" * 80)
print("METHOD 5: Hash-based extraction")
print("=" * 80)

# Hash Row 7 and Row 36
row7_bytes = row7.tobytes()
row36_bytes = row36.tobytes()
combined = row7_bytes + row36_bytes

sha256 = hashlib.sha256(combined).hexdigest()
print(f"SHA256 of (Row7 + Row36): {sha256}")

# Use hash as seed for address generation
print("\nHash-derived address attempt:")
# Take first 60 hex characters and convert to letters
hex_chars = sha256[:60] + sha256[:60]  # Extend if needed
address_from_hash = ''.join([chr(int(hex_chars[i:i+2], 16) % 26 + ord('A')) for i in range(0, 120, 2)])
print(f"  {address_from_hash}")
print()

# ============================================================================
# METHOD 6: The BEDATZFAUR cipher
# ============================================================================
print("=" * 80)
print("METHOD 6: BEDATZFAUR as cipher key")
print("=" * 80)

bedatzfaur = "BEDATZFAUR"
# Use BEDATZFAUR values to select matrix positions
print("Using BEDATZFAUR letter values as column indices:")
for i, c in enumerate(bedatzfaur):
    col = ord(c) - ord('A')
    # Read from multiple significant rows
    for row in [7, 36, 33, 8]:
        val = matrix[row, col]
        char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
        print(f"  '{c}' (col {col:2d}) -> Row {row:2d}: {val:5d} = '{char}'")
print()

# ============================================================================
# METHOD 7: The complete 676 key
# ============================================================================
print("=" * 80)
print("METHOD 7: Complete 676 Key Construction")
print("=" * 80)

print("Building key from all 676-related discoveries:")
print()

# Component 1: The "Key" word
print("1. Key location: (8, 74), (9, 75), (10, 76)")
print("   K = -75, e = 101, y = -121")
key_word = [-75, 101, -121]

# Component 2: Position 576 'K'
print("2. 576 position: (24, 24)")
print("   K = -75 (same value!)")
key_576 = [-75]

# Component 3: Row 7 + Row 36 signature
print("3. Row 7 and 36 both sum to 7436 = 11 × 676")
row_signature = [7436, 7436]

# Component 4: Matrix[33,33] = 26
print("4. Matrix[33,33] = 26 (alphabet signature)")
alphabet_sig = [26]

# Component 5: HEXVRIDGST
print("5. HEXVRIDGST letter sum = 136")
hexvr_sig = [136]

# Combine
all_components = key_word + key_576 + row_signature + alphabet_sig + hexvr_sig
print(f"\nCombined components: {all_components}")
print(f"Total sum: {sum(all_components)}")
print()

# ============================================================================
# METHOD 8: Final address attempt
# ============================================================================
print("=" * 80)
print("METHOD 8: Final Address Attempt")
print("=" * 80)

# Combine Row 7 and Row 36, extract uppercase
combined_rows = []
for i in range(128):
    combined_rows.append(row7[i] ^ row36[i])

# Find all uppercase characters
uppercase_chars = []
for val in combined_rows:
    abs_val = abs(val) % 256
    if 65 <= abs_val <= 90:
        uppercase_chars.append(chr(abs_val))

print(f"Uppercase from Row7 XOR Row36: {''.join(uppercase_chars[:60])}")
print()

# Try mod 26 to get letters
letters_26 = ''.join([chr(abs(v) % 26 + ord('A')) for v in combined_rows])
print(f"All values mod 26 as letters: {letters_26}")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("FINAL EXTRACTION SUMMARY")
print("=" * 80)

print("""
EXTRACTED KEYS AND PATTERNS:

1. THE "KEY" WORD:
   - Location: Diagonal 66, positions (8,74) to (10,76)
   - Values: K=-75, e=101, y=-121
   - Formula: 8 × 74 + 84 = 676

2. THE 576 CONNECTION:
   - Matrix[24,24] = -75 = 'K'
   - 24 × 24 = 576 = Message 576

3. ROW SIGNATURE:
   - Row 7 sum = Row 36 sum = 7436 = 11 × 676
   - Only 2 rows with this property

4. BEDATZFAUR:
   - Row 36, positions 23-32
   - Letter sum = 104 = 4 × 26
   - XOR with EASTEREGG = HEXVRIDGST

5. HEXVRIDGST MEANING:
   - HEX = Hexadecimal encoding
   - DGST = Digest (hash)
   - Suggests: Look for hex-encoded hash data

6. KEY COORDINATES:
   - (8, 74): K
   - (24, 24): K (576)
   - (33, 33): 26 (alphabet)
   - (36, 23-32): BEDATZFAUR

INTERPRETATION:
The ANNA Matrix is a COORDINATE MAP that encodes:
- Key positions (8, 74) and (24, 24)
- Timing information (33, 36)
- Verification signatures (676, 576, 26)
- An encryption hint (HEXVRIDGST = "Hex Digest")

PROBABLE USE:
The matrix provides coordinates for:
1. Wallet derivation paths
2. Claim verification
3. Bridge authorization

The actual key likely requires:
- The ANNA token burns (EASTER EGG)
- The GENESIS top-676 list
- Matrix coordinates combined
""")

# One more attempt: use the discovered values as a seed
print("\n" + "=" * 80)
print("BONUS: Seed-like output from key positions")
print("=" * 80)

# Collect all key values
key_values = [
    matrix[8, 74],    # K
    matrix[9, 75],    # e
    matrix[10, 76],   # y
    matrix[24, 24],   # 576 K
    matrix[33, 33],   # 26
    matrix[36, 23],   # B
    matrix[36, 24],   # E
    matrix[36, 25],   # D
    matrix[36, 26],   # A
    matrix[36, 27],   # T
]

print(f"Key position values: {key_values}")

# Convert to lowercase letters (Qubic seed format)
seed_chars = [chr(abs(v) % 26 + ord('a')) for v in key_values]
print(f"As lowercase: {''.join(seed_chars)}")

# Extend to 55 characters (Qubic seed length)
extended_seed = (seed_chars * 6)[:55]
print(f"Extended to 55: {''.join(extended_seed)}")
