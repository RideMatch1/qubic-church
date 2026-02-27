#!/usr/bin/env python3
"""
ANNA Matrix - Address/Seed Hunt
================================
Looking for hidden Qubic addresses, seeds, or Bitcoin private keys
"""

import json
import numpy as np
import hashlib
import itertools

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
print("ANNA MATRIX - ADDRESS/SEED HUNT")
print("=" * 80)
print()

# ============================================================================
# SEARCH 1: Look for "BEDATZFAUR" and similar patterns
# ============================================================================
print("=" * 80)
print("SEARCH 1: UPPERCASE LETTER SEQUENCES (POTENTIAL ADDRESSES)")
print("=" * 80)

# Find all sequences of uppercase letters
all_uppercase_sequences = []

for i in range(128):
    row = matrix[i, :]
    sequence = []
    start_pos = 0
    for j, val in enumerate(row):
        abs_val = abs(val) % 256
        if 65 <= abs_val <= 90:  # A-Z
            if len(sequence) == 0:
                start_pos = j
            sequence.append(chr(abs_val))
        else:
            if len(sequence) >= 5:
                all_uppercase_sequences.append((i, start_pos, ''.join(sequence)))
            sequence = []
    if len(sequence) >= 5:
        all_uppercase_sequences.append((i, start_pos, ''.join(sequence)))

print(f"Found {len(all_uppercase_sequences)} uppercase sequences (5+ chars):")
for row, pos, seq in sorted(all_uppercase_sequences, key=lambda x: len(x[2]), reverse=True)[:20]:
    print(f"  Row {row:3d}, pos {pos:3d}: {seq} ({len(seq)} chars)")
print()

# ============================================================================
# SEARCH 2: Try to construct addresses from key positions
# ============================================================================
print("=" * 80)
print("SEARCH 2: CONSTRUCTING ADDRESSES FROM KEY POSITIONS")
print("=" * 80)

# Key positions we discovered
key_positions = [
    (8, 74), (9, 75), (10, 76),  # "Key"
    (24, 24),  # 576 position with 'K'
    (33, 33),  # Blood Moon - Easter
    (6, 96),   # 576 position with 26
    (7, 36), (36, 7),  # Row pairs that sum to 676 multiples
]

# Read row 36 completely (it contains "BEDATZFAUR")
row36 = matrix[36, :]
row36_upper = ''.join([chr(abs(v) % 256) if 65 <= abs(v) % 256 <= 90 else '_' for v in row36])
print(f"Row 36 uppercase only: {row36_upper}")
print()

# Extract the BEDATZFAUR and see if we can extend it
for i in range(128):
    for j in range(128):
        if matrix[i, j] == ord('B'):
            # Try to read 60 characters starting here (Qubic address length)
            addr = []
            for k in range(min(60, 128-j)):
                val = abs(matrix[i, j+k]) % 256
                if 65 <= val <= 90:
                    addr.append(chr(val))
                else:
                    break
            if len(addr) >= 10:
                print(f"  Starting at ({i},{j}): {''.join(addr)}")
print()

# ============================================================================
# SEARCH 3: XOR-based address extraction
# ============================================================================
print("=" * 80)
print("SEARCH 3: XOR-BASED ADDRESS EXTRACTION")
print("=" * 80)

# Try XOR of specific rows to get addresses
key_xor_pairs = [(7, 36), (29, 114), (36, 49), (4, 115)]

for r1, r2 in key_xor_pairs:
    xor_result = matrix[r1, :] ^ matrix[r2, :]
    # Extract uppercase letters
    uppercase = ''.join([chr(abs(v) % 256) if 65 <= abs(v) % 256 <= 90 else '_' for v in xor_result])
    print(f"Row {r1} XOR Row {r2} uppercase: {uppercase}")

    # Find longest uppercase sequence
    max_seq = ""
    current_seq = ""
    for c in uppercase:
        if c != '_':
            current_seq += c
        else:
            if len(current_seq) > len(max_seq):
                max_seq = current_seq
            current_seq = ""
    if len(current_seq) > len(max_seq):
        max_seq = current_seq
    if len(max_seq) >= 5:
        print(f"  Longest sequence: {max_seq}")
print()

# ============================================================================
# SEARCH 4: Diagonal-based address extraction
# ============================================================================
print("=" * 80)
print("SEARCH 4: DIAGONAL-BASED ADDRESS EXTRACTION")
print("=" * 80)

for offset in [66, 33, 0, -33, -66]:
    diag = []
    for i in range(128):
        j = i + offset
        if 0 <= j < 128:
            val = abs(matrix[i, j]) % 256
            if 65 <= val <= 90:
                diag.append(chr(val))
            else:
                diag.append('_')
    diag_str = ''.join(diag)
    # Find sequences
    sequences = [s for s in diag_str.split('_') if len(s) >= 5]
    if sequences:
        print(f"Diagonal offset {offset}: {sequences}")
print()

# ============================================================================
# SEARCH 5: Seed-like patterns (55 lowercase letters for Qubic seed)
# ============================================================================
print("=" * 80)
print("SEARCH 5: SEED-LIKE PATTERNS (LOWERCASE)")
print("=" * 80)

# Qubic seeds are 55 lowercase letters
for i in range(128):
    row = matrix[i, :]
    lowercase = ''.join([chr(abs(v) % 256) if 97 <= abs(v) % 256 <= 122 else '_' for v in row])
    # Find longest lowercase sequence
    max_seq = ""
    current_seq = ""
    for c in lowercase:
        if c != '_':
            current_seq += c
        else:
            if len(current_seq) > len(max_seq):
                max_seq = current_seq
            current_seq = ""
    if len(current_seq) > len(max_seq):
        max_seq = current_seq
    if len(max_seq) >= 15:
        print(f"  Row {i}: {max_seq} ({len(max_seq)} chars)")
print()

# ============================================================================
# SEARCH 6: Specific known address fragments
# ============================================================================
print("=" * 80)
print("SEARCH 6: SEARCHING FOR KNOWN ADDRESS FRAGMENTS")
print("=" * 80)

known_fragments = [
    "POCC",  # GENESIS issuer
    "HASV",  # 676 intermediate
    "HIFU",  # ANNA issuer
    "AAAA",  # Burn address
    "BAAA",  # QX contract
    "EXOD",  # EXODUS
]

for frag in known_fragments:
    print(f"\nSearching for '{frag}':")
    for i in range(128):
        row_text = ''.join([chr(abs(v) % 256) if 65 <= abs(v) % 256 <= 90 else '.' for v in matrix[i, :]])
        if frag in row_text:
            pos = row_text.find(frag)
            print(f"  Found in row {i} at position {pos}: ...{row_text[max(0,pos-5):pos+15]}...")
print()

# ============================================================================
# SEARCH 7: Hash the matrix and look for patterns
# ============================================================================
print("=" * 80)
print("SEARCH 7: MATRIX HASH ANALYSIS")
print("=" * 80)

# Hash different matrix regions
regions = [
    ("Full matrix", matrix),
    ("Row 7", matrix[7:8, :]),
    ("Row 36", matrix[36:37, :]),
    ("Rows 7+36", matrix[[7, 36], :]),
    ("Key diagonal 66", np.array([matrix[i, i+66] for i in range(62)])),
    ("Center 26x26", matrix[51:77, 51:77]),
]

for name, region in regions:
    data_bytes = region.tobytes()
    md5 = hashlib.md5(data_bytes).hexdigest()
    sha256 = hashlib.sha256(data_bytes).hexdigest()
    print(f"\n{name}:")
    print(f"  MD5: {md5}")
    print(f"  SHA256: {sha256}")
print()

# ============================================================================
# SEARCH 8: Use key coordinates as indices
# ============================================================================
print("=" * 80)
print("SEARCH 8: USING KEY COORDINATES AS INDICES")
print("=" * 80)

# The positions where we found significant values
coords = [
    (8, 74),   # Key - K
    (9, 75),   # Key - e
    (10, 76),  # Key - y
    (24, 24),  # 576 - K
    (33, 33),  # 26 (alphabet)
    (6, 96),   # 576 - 26
]

print("Reading values at each coordinate and using them as next indices:")
current_row, current_col = 8, 74
visited = []
for _ in range(20):
    val = matrix[current_row, current_col]
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    visited.append((current_row, current_col, val, char))
    # Use abs(val) mod 128 as next indices
    next_row = abs(val) % 128
    next_col = (current_row + current_col) % 128
    current_row, current_col = next_row, next_col

print("Traversal starting from (8, 74):")
for r, c, v, ch in visited:
    print(f"  Matrix[{r:3d},{c:3d}] = {v:5d} = '{ch}'")
print()

# ============================================================================
# SEARCH 9: Binary-encoded addresses
# ============================================================================
print("=" * 80)
print("SEARCH 9: BINARY-ENCODED PATTERNS")
print("=" * 80)

# Check if row values could be binary-encoded letters
print("Checking for 7-bit binary encoding patterns...")

# Convert each 7 consecutive values to a character (if they're 0/1)
for i in range(128):
    row = matrix[i, :]
    # Check if any 7 consecutive values are 0 or 1
    for j in range(121):
        segment = row[j:j+7]
        if all(v in [0, 1] for v in segment):
            binary_str = ''.join(str(v) for v in segment)
            ascii_val = int(binary_str, 2)
            if 32 <= ascii_val <= 126:
                print(f"  Row {i}, pos {j}: {binary_str} = {ascii_val} = '{chr(ascii_val)}'")
print()

# ============================================================================
# SEARCH 10: The "576" and "676" specific search
# ============================================================================
print("=" * 80)
print("SEARCH 10: POSITIONS WITH 576 AND 676 PRODUCTS")
print("=" * 80)

# Positions where i*j = 576 or i*j = 676
print("Building address from 576 positions:")
addr_576 = []
for i in range(1, 128):
    for j in range(1, 128):
        if i * j == 576:
            val = matrix[i, j]
            if 65 <= abs(val) % 256 <= 90:
                addr_576.append(chr(abs(val) % 256))
            elif 97 <= abs(val) % 256 <= 122:
                addr_576.append(chr(abs(val) % 256))
print(f"  576 positions letters: {''.join(addr_576)}")

print("\nBuilding address from 676 positions:")
addr_676 = []
for i in range(1, 128):
    for j in range(1, 128):
        if i * j == 676:
            val = matrix[i, j]
            if 65 <= abs(val) % 256 <= 90:
                addr_676.append(chr(abs(val) % 256))
            elif 97 <= abs(val) % 256 <= 122:
                addr_676.append(chr(abs(val) % 256))
print(f"  676 positions letters: {''.join(addr_676)}")
print()

# ============================================================================
# SEARCH 11: Row 36 deep analysis (contains BEDATZFAUR)
# ============================================================================
print("=" * 80)
print("SEARCH 11: ROW 36 DEEP ANALYSIS")
print("=" * 80)

row36 = matrix[36, :]
print("Row 36 values around BEDATZFAUR (positions 23-32):")
for j in range(20, 40):
    val = row36[j]
    char = chr(abs(val) % 256) if 32 <= abs(val) % 256 <= 126 else '.'
    print(f"  Position {j:2d}: value = {val:5d} = '{char}'")
print()

# Try to extend BEDATZFAUR
print("Attempting to extend BEDATZFAUR...")
print("Checking if BEDATZFAUR appears in any known Qubic address format...")

# Known addresses from our analysis
known_addresses = [
    "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD",
    "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO",
    "HIFUSWQYNUZTSDRPXZOXXIWUPWTAOVJUTCVLFIHLHARCXSARRTGCJLGGAREO",
]

for addr in known_addresses:
    if "BEDATZFAUR" in addr:
        print(f"  Found in: {addr}")
    # Check if any substring of BEDATZFAUR appears
    for length in range(4, len("BEDATZFAUR")):
        for start in range(len("BEDATZFAUR") - length + 1):
            fragment = "BEDATZFAUR"[start:start+length]
            if fragment in addr:
                print(f"  Fragment '{fragment}' found in {addr[:20]}...")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("FINAL SUMMARY - ADDRESS HUNT RESULTS")
print("=" * 80)

print("""
DISCOVERED PATTERNS:

1. "BEDATZFAUR" at Row 36, positions 23-32
   - This is the longest uppercase sequence found
   - Does NOT match any known Qubic address
   - Could be: an anagram, encoded seed, or partial key

2. Multiple uppercase sequences found but none are complete addresses

3. The "Key" at diagonal 66 (positions 8-10) spells "Key"
   - Matrix[8,74] = 'K'
   - Matrix[9,75] = 'e'
   - Matrix[10,76] = 'y'

4. Position 24,24 = -75 = 'K' (same as Key position)
   - 24 × 24 = 576 = Message 576!

5. No complete Qubic addresses (60 uppercase letters) found
6. No complete Qubic seeds (55 lowercase letters) found

INTERPRETATION:
The matrix contains HINTS rather than complete keys:
- "Key" is literally spelled out at diagonal 66
- "BEDATZFAUR" might be an anagram or cipher
- The real key might require XOR/combination operations

ANAGRAM POSSIBILITIES FOR "BEDATZFAUR":
- "ZFAU" could be part of "FXIB" (burn address ending)
- "BEDAT" could be related to "BETA" or a date
- Could spell: "AZURE DEBT A F" with rearrangement?
""")

# Try anagram analysis
import itertools

letters = "BEDATZFAUR"
print("\nAnagram analysis for BEDATZFAUR:")
print(f"  Letters: {letters}")
print(f"  Sorted: {''.join(sorted(letters))}")
print(f"  Vowels: {''.join(c for c in letters if c in 'AEIOU')}")
print(f"  Consonants: {''.join(c for c in letters if c not in 'AEIOU')}")

# Check if it's a simple substitution
print("\n  As numbers (A=1, B=2...):")
nums = [ord(c) - ord('A') + 1 for c in letters]
print(f"  {nums}")
print(f"  Sum: {sum(nums)}")
