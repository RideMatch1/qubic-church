#!/usr/bin/env python3
"""
===============================================================================
            ↘️ DIAGONAL ANALYSIS ↘️
===============================================================================
Analyze the main diagonal, anti-diagonal, and all parallel diagonals.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re

script_dir = Path(__file__).parent

print("=" * 80)
print("           ↘️ DIAGONAL ANALYSIS ↘️")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# MAIN DIAGONAL (r = c)
# ==============================================================================
print("\n" + "=" * 80)
print("MAIN DIAGONAL (r = c)")
print("=" * 80)

main_diag = [int(matrix[i, i]) for i in range(128)]
main_diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in main_diag)

print(f"\n  Main diagonal as ASCII:")
for i in range(0, 128, 32):
    print(f"    [{i:3d}-{i+31:3d}]: {main_diag_ascii[i:i+32]}")

# Find words
main_diag_words = re.findall(r'[a-zA-Z]{3,}', main_diag_ascii)
print(f"\n  Words found: {main_diag_words}")

# Check symmetry on diagonal
diag_symmetric = 0
for i in range(64):
    if main_diag[i] + main_diag[127-i] == -1:
        diag_symmetric += 1

print(f"\n  Diagonal symmetry: {diag_symmetric}/64 pairs ({diag_symmetric/64*100:.1f}%)")

# Special positions on diagonal
print(f"\n  Special diagonal positions:")
for i in [0, 22, 42, 63, 64, 127]:
    v = main_diag[i]
    ch = chr(abs(v)) if 32 <= abs(v) <= 126 else '.'
    print(f"    [{i},{i}] = {v:4d} = '{ch}'")

# ==============================================================================
# ANTI-DIAGONAL (r + c = 127)
# ==============================================================================
print("\n" + "=" * 80)
print("ANTI-DIAGONAL (r + c = 127)")
print("=" * 80)

anti_diag = [int(matrix[i, 127-i]) for i in range(128)]
anti_diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in anti_diag)

print(f"\n  Anti-diagonal as ASCII:")
for i in range(0, 128, 32):
    print(f"    [{i:3d}-{i+31:3d}]: {anti_diag_ascii[i:i+32]}")

anti_diag_words = re.findall(r'[a-zA-Z]{3,}', anti_diag_ascii)
print(f"\n  Words found: {anti_diag_words}")

# ==============================================================================
# XOR OF DIAGONALS
# ==============================================================================
print("\n" + "=" * 80)
print("DIAGONAL XOR")
print("=" * 80)

diag_xor = [main_diag[i] ^ anti_diag[i] for i in range(128)]
diag_xor_ascii = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in diag_xor)

print(f"\n  Main ⊕ Anti diagonal:")
for i in range(0, 128, 32):
    print(f"    [{i:3d}-{i+31:3d}]: {diag_xor_ascii[i:i+32]}")

diag_xor_words = re.findall(r'[a-zA-Z]{3,}', diag_xor_ascii)
print(f"\n  Words found: {diag_xor_words}")

# ==============================================================================
# PARALLEL DIAGONALS
# ==============================================================================
print("\n" + "=" * 80)
print("PARALLEL DIAGONALS (offset from main)")
print("=" * 80)

# Diagonals with offset from main
interesting_offsets = []

for offset in range(-63, 64):
    if offset == 0:
        continue

    diag = []
    for i in range(128):
        c = i + offset
        if 0 <= c < 128:
            diag.append(int(matrix[i, c]))

    if len(diag) < 10:
        continue

    diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in diag)
    words = re.findall(r'[a-zA-Z]{4,}', diag_ascii)

    if words:
        interesting_offsets.append({
            "offset": offset,
            "length": len(diag),
            "words": words,
            "ascii": diag_ascii[:50],
        })

print(f"\n  Diagonals with 4+ letter words:")
for d in interesting_offsets[:15]:
    print(f"    Offset {d['offset']:+3d} (len={d['length']:3d}): {d['words'][:5]}")

# ==============================================================================
# CENTER OF DIAGONALS
# ==============================================================================
print("\n" + "=" * 80)
print("DIAGONAL CENTER ANALYSIS")
print("=" * 80)

# The center of the main diagonal is [63,63] and [64,64]
center_region = []
for i in range(60, 68):
    v = main_diag[i]
    ch = chr(abs(v)) if 32 <= abs(v) <= 126 else '.'
    partner_v = main_diag[127-i]
    partner_ch = chr(abs(partner_v)) if 32 <= abs(partner_v) <= 126 else '.'
    is_sym = "✓" if v + partner_v == -1 else "✗"

    center_region.append({
        "pos": i,
        "value": v,
        "char": ch,
        "partner_value": partner_v,
        "partner_char": partner_ch,
        "symmetric": v + partner_v == -1,
    })

    print(f"  [{i},{i}] = {v:4d} '{ch}' ↔ [{127-i},{127-i}] = {partner_v:4d} '{partner_ch}' {is_sym}")

# ==============================================================================
# FIBONACCI POSITIONS ON DIAGONAL
# ==============================================================================
print("\n" + "=" * 80)
print("FIBONACCI POSITIONS ON DIAGONAL")
print("=" * 80)

fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
print("\n  Values at Fibonacci positions:")

fib_values = []
for f in fib:
    if f < 128:
        v = main_diag[f]
        ch = chr(abs(v)) if 32 <= abs(v) <= 126 else '.'
        fib_values.append((f, v, ch))
        print(f"    [{f},{f}] = {v:4d} = '{ch}'")

# Check if fib values form a pattern
fib_chars = ''.join(fv[2] for fv in fib_values)
print(f"\n  Fibonacci positions spell: '{fib_chars}'")

# ==============================================================================
# ROW XOR ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("ROW XOR ANALYSIS (Row[r] ⊕ Row[127-r])")
print("=" * 80)

# XOR symmetric row pairs
row_xors = []
for r in range(64):
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_partner = [int(matrix[127-r, c]) for c in range(128)]

    xor_row = [row_r[c] ^ row_partner[c] for c in range(128)]
    xor_ascii = ''.join(chr(abs(x)) if 32 <= abs(x) <= 126 else '.' for x in xor_row)

    words = re.findall(r'[a-zA-Z]{4,}', xor_ascii)

    if words:
        row_xors.append({
            "row": r,
            "partner": 127 - r,
            "words": words,
        })

print(f"\n  Row pairs with 4+ letter words: {len(row_xors)}")
for rx in row_xors[:10]:
    print(f"    Rows {rx['row']:3}↔{rx['partner']:3}: {rx['words'][:5]}")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("↘️ DIAGONAL ANALYSIS COMPLETE ↘️")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         DIAGONAL FINDINGS                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  MAIN DIAGONAL:                                                               ║
║  • Words found: {len(main_diag_words)} words                                            ║
║  • Notable: {str(main_diag_words[:5])[:45]:45}     ║
║  • Symmetry: {diag_symmetric}/64 pairs                                           ║
║                                                                               ║
║  ANTI-DIAGONAL:                                                               ║
║  • Words found: {len(anti_diag_words)} words                                            ║
║  • Notable: {str(anti_diag_words[:5])[:45]:45}     ║
║                                                                               ║
║  DIAGONAL XOR:                                                                ║
║  • Words found: {len(diag_xor_words)} words                                             ║
║                                                                               ║
║  PARALLEL DIAGONALS:                                                          ║
║  • {len(interesting_offsets)} diagonals have 4+ letter words                              ║
║                                                                               ║
║  ROW XOR (Row[r] ⊕ Row[127-r]):                                              ║
║  • {len(row_xors)} row pairs have 4+ letter words                                    ║
║                                                                               ║
║  FIBONACCI POSITIONS:                                                         ║
║  • Spell: '{fib_chars}'                                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "main_diagonal": {
        "ascii": main_diag_ascii,
        "words": main_diag_words,
        "symmetry_pairs": diag_symmetric,
    },
    "anti_diagonal": {
        "ascii": anti_diag_ascii,
        "words": anti_diag_words,
    },
    "diagonal_xor": {
        "ascii": diag_xor_ascii,
        "words": diag_xor_words,
    },
    "parallel_diagonals": interesting_offsets,
    "row_xors": row_xors,
    "fibonacci_pattern": fib_chars,
    "center_region": center_region,
}

output_path = script_dir / "DIAGONAL_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
