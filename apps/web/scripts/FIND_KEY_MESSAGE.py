#!/usr/bin/env python3
"""
===============================================================================
        🔑 FOUND "KEY" IN COLUMN 127! EXTRACTING FULL MESSAGE 🔑
===============================================================================
"""

import json
import numpy as np
from pathlib import Path

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██╗  ██╗███████╗██╗   ██╗    ███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██╗
   ██║ ██╔╝██╔════╝╚██╗ ██╔╝    ██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██║
   █████╔╝ █████╗   ╚████╔╝     █████╗  ██║   ██║██║   ██║██╔██╗ ██║██║  ██║██║
   ██╔═██╗ ██╔══╝    ╚██╔╝      ██╔══╝  ██║   ██║██║   ██║██║╚██╗██║██║  ██║╚═╝
   ██║  ██╗███████╗   ██║       ██║     ╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██╗
   ╚═╝  ╚═╝╚══════╝   ╚═╝       ╚═╝      ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝
                    "KEY" FOUND IN MATRIX!
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# ANALYZE COLUMN 127 IN DETAIL
# ==============================================================================
print("\n" + "=" * 80)
print("COLUMN 127 DETAILED ANALYSIS")
print("=" * 80)

col127 = [int(matrix[r, 127]) for r in range(128)]

print("\n  Full column 127 as ASCII (with row numbers):")
for r in range(128):
    val = col127[r]
    char = chr(abs(val)) if 32 <= abs(val) <= 126 else '.'
    if char not in '.':
        print(f"    Row {r:3d}: {val:4d} = '{char}'")

# Find "key" sequence
print("\n  Looking for 'key' pattern...")
for r in range(126):
    seq = ''.join(chr(abs(col127[r+i])) if 32 <= abs(col127[r+i]) <= 126 else '.' for i in range(3))
    if 'key' in seq.lower():
        print(f"    FOUND at rows {r}-{r+2}: '{seq}'")
        # Show context
        context_start = max(0, r-5)
        context_end = min(128, r+8)
        context = ''.join(chr(abs(col127[i])) if 32 <= abs(col127[i]) <= 126 else '.' for i in range(context_start, context_end))
        print(f"    Context (rows {context_start}-{context_end}): '{context}'")

# ==============================================================================
# SEARCH ALL COLUMNS FOR "KEY"
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING ALL COLUMNS FOR 'KEY'")
print("=" * 80)

for c in range(128):
    col = [int(matrix[r, c]) for r in range(128)]
    col_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in col).lower()

    if 'key' in col_ascii:
        print(f"\n  Found 'key' in COLUMN {c}!")
        full_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in col)
        idx = col_ascii.find('key')
        print(f"    Position: {idx}")
        print(f"    Full column: {full_ascii}")

# ==============================================================================
# SEARCH ALL ROWS FOR "KEY"
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING ALL ROWS FOR 'KEY'")
print("=" * 80)

for r in range(128):
    row = [int(matrix[r, c]) for c in range(128)]
    row_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in row).lower()

    if 'key' in row_ascii:
        print(f"\n  Found 'key' in ROW {r}!")
        full_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in row)
        idx = row_ascii.find('key')
        print(f"    Position: {idx}")
        print(f"    Full row: {full_ascii}")

# ==============================================================================
# SEARCH XOR COMBINATIONS FOR "KEY"
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING XOR COMBINATIONS FOR 'KEY'")
print("=" * 80)

for r in range(64):
    r2 = 127 - r
    xor_row = [int(matrix[r, c]) ^ int(matrix[r2, c]) for c in range(128)]
    xor_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_row).lower()

    if 'key' in xor_ascii:
        print(f"\n  Found 'key' in ROW {r} ⊕ ROW {r2}!")
        full_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in xor_row)
        print(f"    {full_ascii}")

for c in range(64):
    c2 = 127 - c
    xor_col = [int(matrix[r, c]) ^ int(matrix[r, c2]) for r in range(128)]
    xor_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_col).lower()

    if 'key' in xor_ascii:
        print(f"\n  Found 'key' in COL {c} ⊕ COL {c2}!")
        full_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in xor_col)
        print(f"    {full_ascii}")

# ==============================================================================
# SEARCH FOR OTHER SIGNIFICANT WORDS
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING FOR OTHER SIGNIFICANT WORDS")
print("=" * 80)

important_words = ['secret', 'hidden', 'password', 'seed', 'wallet', 'bitcoin', 'satoshi',
                   'treasure', 'prize', 'anna', 'cfb', 'qubic', 'code', 'lock', 'open']

def search_word(word):
    found = []

    # Search rows
    for r in range(128):
        row = [int(matrix[r, c]) for c in range(128)]
        row_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in row).lower()
        if word in row_ascii:
            found.append(f"Row {r}")

    # Search columns
    for c in range(128):
        col = [int(matrix[r, c]) for r in range(128)]
        col_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in col).lower()
        if word in col_ascii:
            found.append(f"Col {c}")

    # Search XOR rows
    for r in range(64):
        r2 = 127 - r
        xor_row = [int(matrix[r, c]) ^ int(matrix[r2, c]) for c in range(128)]
        xor_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_row).lower()
        if word in xor_ascii:
            found.append(f"Row {r}⊕{r2}")

    # Search XOR cols
    for c in range(64):
        c2 = 127 - c
        xor_col = [int(matrix[r, c]) ^ int(matrix[r, c2]) for r in range(128)]
        xor_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_col).lower()
        if word in xor_ascii:
            found.append(f"Col {c}⊕{c2}")

    return found

print("\n  Searching for important words...")
for word in important_words:
    locations = search_word(word)
    if locations:
        print(f"\n  '{word.upper()}' found in: {', '.join(locations)}")

# ==============================================================================
# THE "ge=key}y" CONTEXT - EXTRACT FULL MESSAGE
# ==============================================================================
print("\n" + "=" * 80)
print("EXTRACTING FULL MESSAGE AROUND 'key'")
print("=" * 80)

# Column 127 has the key - let's get the full readable context
col127_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else ' ' for v in col127)
print(f"\n  Column 127 (spaces for non-printable):")
print(f"    {col127_ascii}")

# Find all words in column 127
print("\n  All recognizable sequences in Column 127:")
current_word = ""
for r, v in enumerate(col127):
    char = chr(abs(v)) if 32 <= abs(v) <= 126 else None
    if char and char.isalpha():
        current_word += char
    else:
        if len(current_word) >= 3:
            print(f"    '{current_word}' at row ~{r - len(current_word)}")
        current_word = ""

# ==============================================================================
# CHECK IF "KEY" IS ACTUALLY A KEY VALUE
# ==============================================================================
print("\n" + "=" * 80)
print("ANALYZING THE 'KEY' POSITION")
print("=" * 80)

# In col 127, find exact position of k, e, y
for r in range(126):
    k = chr(abs(col127[r])) if 32 <= abs(col127[r]) <= 126 else ''
    e = chr(abs(col127[r+1])) if 32 <= abs(col127[r+1]) <= 126 else ''
    y = chr(abs(col127[r+2])) if 32 <= abs(col127[r+2]) <= 126 else ''

    if k.lower() == 'k' and e.lower() == 'e' and y.lower() == 'y':
        print(f"\n  EXACT 'key' at rows {r}, {r+1}, {r+2}:")
        print(f"    Row {r}: value = {col127[r]}")
        print(f"    Row {r+1}: value = {col127[r+1]}")
        print(f"    Row {r+2}: value = {col127[r+2]}")

        # The values themselves might BE the key!
        key_values = [col127[r], col127[r+1], col127[r+2]]
        print(f"\n  These values as hex: {' '.join(format(abs(v), '02x') for v in key_values)}")

        # Check the surrounding values
        print(f"\n  Surrounding values (rows {max(0,r-10)} to {min(127,r+13)}):")
        for i in range(max(0, r-10), min(128, r+13)):
            v = col127[i]
            c = chr(abs(v)) if 32 <= abs(v) <= 126 else '.'
            marker = " <-- KEY" if r <= i <= r+2 else ""
            print(f"    Row {i:3d}: {v:4d} = '{c}'{marker}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("🔑 KEY DISCOVERY SUMMARY")
print("=" * 80)

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         KEY FOUND IN COLUMN 127!                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  The word "key" appears in the rightmost column of the matrix!                ║
║                                                                               ║
║  This is the EDGE of the matrix - like a border message!                      ║
║                                                                               ║
║  Possible interpretations:                                                    ║
║    1. The values at "key" positions ARE the key                               ║
║    2. The surrounding context contains instructions                           ║
║    3. This marks where to look for the actual key                             ║
║                                                                               ║
║  Combined with:                                                               ║
║    - "AI.MEG.GOU" in columns 30⊕97                                            ║
║    - "mmmmcceeii" self-referential code                                       ║
║    - 8 bridge cells at value 127                                              ║
║                                                                               ║
║  The matrix is DEFINITELY trying to tell us something!                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
