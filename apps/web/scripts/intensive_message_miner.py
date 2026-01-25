#!/usr/bin/env python3
"""
INTENSIVE MESSAGE MINER - Background Process
=============================================
Exhaustive search for hidden messages using ALL possible methods.

Runs ALL encoding combinations systematically.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import itertools
import datetime

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("=" * 70)
print("INTENSIVE MESSAGE MINER - Background Process")
print("=" * 70)

# English dictionary for validation
english_words = set([
    # 3-letter
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her',
    'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its',
    'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'end',
    'key', 'god', 'man', 'use', 'say', 'she', 'too', 'any', 'meg', 'gou', 'fib',
    # 4-letter
    'code', 'hash', 'seed', 'node', 'sign', 'time', 'find', 'look', 'come', 'here',
    'mega', 'anna', 'jinn', 'mine', 'coin', 'call', 'send', 'wake', 'rise', 'boot',
    'init', 'read', 'true', 'zero', 'ones', 'gate', 'open', 'shut', 'loop', 'next',
    # 5+ letter (more significant)
    'truth', 'proof', 'begin', 'start', 'ternary', 'binary', 'trinity', 'oracle',
    'bridge', 'qubic', 'aigarth', 'satoshi', 'bitcoin', 'genesis', 'merkle',
    'hidden', 'secret', 'cipher', 'decode', 'encode', 'unlock', 'reveal'
])

# Minimum word length to report (avoid noise)
MIN_WORD_LEN = 4

discoveries = []

def extract_words(text, method_name):
    """Extract all English words from text."""
    text_lower = text.lower()
    found = []
    for word in english_words:
        if len(word) >= MIN_WORD_LEN and word in text_lower:
            pos = text_lower.find(word)
            found.append({
                "method": method_name,
                "word": word,
                "position": pos,
                "context": text_lower[max(0, pos-10):pos+len(word)+10]
            })
    return found

# =============================================================================
# METHOD GROUP 1: ALL XOR PAIRS (64 pairs × multiple encodings)
# =============================================================================
print("\n--- XOR ALL 64 PAIRS ---")

for col1 in range(64):
    col2 = 127 - col1

    # Standard XOR
    xor_text = ''
    for r in range(128):
        xv = (matrix[r][col1] & 0xFF) ^ (matrix[r][col2] & 0xFF)
        xor_text += chr(xv) if 32 <= xv <= 126 else '.'

    found = extract_words(xor_text, f"xor_pair_{col1}_{col2}")
    if found:
        for f in found:
            print(f"  Pair {col1}↔{col2}: '{f['word']}' at {f['position']}")
            discoveries.append(f)

# =============================================================================
# METHOD GROUP 2: ROW OPERATIONS
# =============================================================================
print("\n--- ROW OPERATIONS ---")

for r in range(128):
    row = matrix[r]

    # Direct ASCII
    text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in row])
    found = extract_words(text, f"row_{r}_ascii")
    if found:
        for f in found:
            print(f"  Row {r} ASCII: '{f['word']}'")
            discoveries.append(f)

    # XOR with row number
    text = ''.join([chr((v ^ r) & 0x7F) if 32 <= ((v ^ r) & 0x7F) <= 126 else '.' for v in row])
    found = extract_words(text, f"row_{r}_xor_rownum")
    if found:
        for f in found:
            print(f"  Row {r} XOR {r}: '{f['word']}'")
            discoveries.append(f)

# =============================================================================
# METHOD GROUP 3: SPECIAL ROWS (High Density ASCII)
# =============================================================================
print("\n--- SPECIAL ROWS ---")

# Check rows 1, 5, 13, 64 (known high-density)
special_rows = [1, 5, 13, 64, 0, 127]

for r in special_rows:
    row = matrix[r]

    # Multiple encodings
    encodings = [
        ("ascii7", lambda v: chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.'),
        ("xor127", lambda v: chr((v ^ 127) & 0x7F) if 32 <= ((v ^ 127) & 0x7F) <= 126 else '.'),
        ("abs", lambda v: chr(abs(v)) if 32 <= abs(v) <= 126 else '.'),
        ("plus128", lambda v: chr((v + 128) % 256) if 32 <= ((v + 128) % 256) <= 126 else '.'),
    ]

    for name, func in encodings:
        text = ''.join([func(v) for v in row])
        found = extract_words(text, f"row_{r}_{name}")
        if found:
            for f in found:
                print(f"  Row {r} {name}: '{f['word']}'")
                discoveries.append(f)

# =============================================================================
# METHOD GROUP 4: DIAGONAL PATTERNS
# =============================================================================
print("\n--- DIAGONAL PATTERNS ---")

# Main diagonal
main_diag = [matrix[i][i] for i in range(128)]
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in main_diag])
found = extract_words(text, "main_diagonal")
for f in found:
    print(f"  Main diagonal: '{f['word']}'")
    discoveries.append(f)

# Anti-diagonal
anti_diag = [matrix[i][127-i] for i in range(128)]
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in anti_diag])
found = extract_words(text, "anti_diagonal")
for f in found:
    print(f"  Anti-diagonal: '{f['word']}'")
    discoveries.append(f)

# All diagonals
for offset in range(-127, 128):
    diag = []
    for i in range(128):
        c = i + offset
        if 0 <= c < 128:
            diag.append(matrix[i][c])
    if len(diag) >= 20:  # Only check substantial diagonals
        text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in diag])
        found = extract_words(text, f"diag_offset_{offset}")
        if found:
            for f in found:
                print(f"  Diagonal offset {offset}: '{f['word']}'")
                discoveries.append(f)

# =============================================================================
# METHOD GROUP 5: BIT PLANES
# =============================================================================
print("\n--- BIT PLANE ANALYSIS ---")

for bit in range(8):
    # Extract bit plane
    bit_plane = (matrix >> bit) & 1

    # Convert to text (groups of 8 bits)
    flat = bit_plane.flatten()
    text_chars = []
    for i in range(0, len(flat) - 7, 8):
        byte = 0
        for b in range(8):
            byte |= flat[i + b] << (7 - b)
        if 32 <= byte <= 126:
            text_chars.append(chr(byte))
        else:
            text_chars.append('.')

    text = ''.join(text_chars)
    found = extract_words(text, f"bit_plane_{bit}")
    if found:
        for f in found:
            print(f"  Bit plane {bit}: '{f['word']}'")
            discoveries.append(f)

# =============================================================================
# METHOD GROUP 6: MODULAR ARITHMETIC
# =============================================================================
print("\n--- MODULAR ARITHMETIC ---")

for mod in [26, 27, 32, 64, 128]:
    text = []
    for v in matrix.flatten():
        m = abs(v) % mod
        if mod == 26:
            text.append(chr(ord('a') + m))
        elif mod == 27:
            text.append(' ' if m == 0 else chr(ord('a') + m - 1))
        else:
            if 32 <= m <= 126:
                text.append(chr(m))
            else:
                text.append('.')

    text_str = ''.join(text)
    found = extract_words(text_str[:5000], f"mod_{mod}")  # Only check first 5000 chars
    if found:
        for f in found:
            print(f"  Mod {mod}: '{f['word']}'")
            discoveries.append(f)

# =============================================================================
# METHOD GROUP 7: COLUMN INTERLEAVING
# =============================================================================
print("\n--- COLUMN INTERLEAVING ---")

# Read columns in pairs and interleave
for col1 in range(0, 64, 2):
    col2 = col1 + 1
    interleaved = []
    for r in range(128):
        interleaved.append(matrix[r][col1])
        interleaved.append(matrix[r][col2])

    text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in interleaved])
    found = extract_words(text, f"interleave_{col1}_{col2}")
    if found:
        for f in found:
            print(f"  Interleave {col1},{col2}: '{f['word']}'")
            discoveries.append(f)

# =============================================================================
# METHOD GROUP 8: SPIRAL READING
# =============================================================================
print("\n--- SPIRAL READING ---")

def spiral_order(matrix):
    """Read matrix in spiral order."""
    result = []
    m, n = len(matrix), len(matrix[0])
    top, bottom, left, right = 0, m - 1, 0, n - 1

    while top <= bottom and left <= right:
        for i in range(left, right + 1):
            result.append(matrix[top][i])
        top += 1

        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1

        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(matrix[bottom][i])
            bottom -= 1

        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1

    return result

spiral = spiral_order(matrix.tolist())
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in spiral])
found = extract_words(text, "spiral")
if found:
    for f in found:
        print(f"  Spiral: '{f['word']}'")
        discoveries.append(f)

# =============================================================================
# METHOD GROUP 9: KNIGHT'S TOUR
# =============================================================================
print("\n--- KNIGHT'S TOUR PATTERN ---")

# Follow knight moves from center
moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
visited = set()
knight_values = []
r, c = 64, 64  # Start from center

for _ in range(128):
    if 0 <= r < 128 and 0 <= c < 128 and (r, c) not in visited:
        knight_values.append(matrix[r][c])
        visited.add((r, c))
    # Move
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 128 and 0 <= nc < 128 and (nr, nc) not in visited:
            r, c = nr, nc
            break

text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '.' for v in knight_values])
found = extract_words(text, "knight_tour")
if found:
    for f in found:
        print(f"  Knight's tour: '{f['word']}'")
        discoveries.append(f)

# =============================================================================
# METHOD GROUP 10: DIFFERENCE ENCODING
# =============================================================================
print("\n--- DIFFERENCE ENCODING ---")

# Row-wise differences
diff_text = []
for r in range(128):
    for c in range(127):
        diff = matrix[r][c+1] - matrix[r][c]
        diff = (diff + 128) % 256  # Normalize to 0-255
        if 32 <= diff <= 126:
            diff_text.append(chr(diff))
        else:
            diff_text.append('.')

text = ''.join(diff_text)
found = extract_words(text, "row_diff")
if found:
    for f in found:
        print(f"  Row differences: '{f['word']}'")
        discoveries.append(f)

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("INTENSIVE MINING COMPLETE")
print("=" * 70)

# Remove duplicates
unique_discoveries = []
seen = set()
for d in discoveries:
    key = (d["method"].split("_")[0], d["word"])
    if key not in seen:
        seen.add(key)
        unique_discoveries.append(d)

print(f"\nTotal unique discoveries: {len(unique_discoveries)}")
print("\nSignificant findings (4+ letters):")
for d in sorted(unique_discoveries, key=lambda x: (-len(x["word"]), x["word"])):
    if len(d["word"]) >= 4:
        print(f"  [{d['method']}] {d['word']}")

# Save results
output = {
    "timestamp": datetime.datetime.now().isoformat(),
    "total_discoveries": len(unique_discoveries),
    "discoveries": unique_discoveries,
    "methods_tested": 10
}

output_path = script_dir / "INTENSIVE_MINING_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Results saved to {output_path}")
