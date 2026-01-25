#!/usr/bin/env python3
"""
PHASE E: BLOCK-BASIERTE DEKODIERUNG
===================================
Analysiere die Matrix in 8×8 und 16×16 Blöcken.
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix

print("=" * 80)
print("PHASE E: BLOCK-BASIERTE DEKODIERUNG")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

KNOWN_WORDS = [
    'the', 'and', 'for', 'yes', 'no', 'sat', 'ai', 'meg', 'gou', 'cfb',
    'fib', 'btc', 'key', 'god', 'truth', 'satya', 'satoshi', 'bitcoin',
    'qubic', 'iota', 'anna', 'code', 'void', 'time', 'lock', 'bridge'
]

def to_ascii(values):
    return ''.join([chr(v & 0xFF) if 32 <= (v & 0xFF) <= 126 else '.' for v in values])

def find_words(text, word_list):
    upper = text.upper()
    found = []
    for word in word_list:
        if word.upper() in upper:
            pos = upper.find(word.upper())
            found.append({'word': word, 'position': pos})
    return found

# =============================================================================
# METHODE 1: 8×8 BLÖCKE (256 Blöcke)
# =============================================================================
print("[1] 8×8 BLÖCKE - BLOCK-SUMMEN")
print("-" * 60)

block_8_sums = []
block_8_xors = []
block_8_means = []

for block_row in range(16):
    for block_col in range(16):
        r_start, r_end = block_row * 8, (block_row + 1) * 8
        c_start, c_end = block_col * 8, (block_col + 1) * 8

        block = matrix[r_start:r_end, c_start:c_end]
        block_sum = int(np.sum(block))
        block_mean = float(np.mean(block))

        # XOR aller Werte im Block
        block_xor = 0
        for val in block.flatten():
            block_xor ^= (int(val) & 0xFF)

        block_8_sums.append(block_sum)
        block_8_xors.append(block_xor)
        block_8_means.append(block_mean)

# Block-Summen als ASCII
ascii_8_sums = to_ascii([s & 0xFF for s in block_8_sums])
ascii_8_xors = to_ascii(block_8_xors)

print(f"256 Block-Summen (mod 256): {block_8_sums[:20]}...")
print(f"ASCII Summen: {ascii_8_sums[:64]}...")
print(f"ASCII XORs: {ascii_8_xors[:64]}...")

words_8_sums = find_words(ascii_8_sums, KNOWN_WORDS)
words_8_xors = find_words(ascii_8_xors, KNOWN_WORDS)

if words_8_sums:
    print(f"WÖRTER in Summen: {[w['word'] for w in words_8_sums]}")
if words_8_xors:
    print(f"WÖRTER in XORs: {[w['word'] for w in words_8_xors]}")
print()

# =============================================================================
# METHODE 2: 16×16 BLÖCKE (64 Blöcke)
# =============================================================================
print("[2] 16×16 BLÖCKE - BLOCK-SUMMEN")
print("-" * 60)

block_16_sums = []
block_16_xors = []

for block_row in range(8):
    for block_col in range(8):
        r_start, r_end = block_row * 16, (block_row + 1) * 16
        c_start, c_end = block_col * 16, (block_col + 1) * 16

        block = matrix[r_start:r_end, c_start:c_end]
        block_sum = int(np.sum(block))

        block_xor = 0
        for val in block.flatten():
            block_xor ^= (int(val) & 0xFF)

        block_16_sums.append(block_sum)
        block_16_xors.append(block_xor)

ascii_16_sums = to_ascii([s & 0xFF for s in block_16_sums])
ascii_16_xors = to_ascii(block_16_xors)

print(f"64 Block-Summen (mod 256): {block_16_sums}")
print(f"ASCII Summen: {ascii_16_sums}")
print(f"ASCII XORs: {ascii_16_xors}")

words_16_sums = find_words(ascii_16_sums, KNOWN_WORDS)
words_16_xors = find_words(ascii_16_xors, KNOWN_WORDS)

if words_16_sums:
    print(f"WÖRTER in Summen: {[w['word'] for w in words_16_sums]}")
if words_16_xors:
    print(f"WÖRTER in XORs: {[w['word'] for w in words_16_xors]}")
print()

# =============================================================================
# METHODE 3: BLOCK-DIAGONAL WERTE
# =============================================================================
print("[3] BLOCK-DIAGONAL (Hauptdiagonale jedes 8×8 Blocks)")
print("-" * 60)

block_diagonals = []
for block_row in range(16):
    for block_col in range(16):
        r_start = block_row * 8
        c_start = block_col * 8

        # Diagonal des Blocks
        diag_sum = 0
        for i in range(8):
            diag_sum += int(matrix[r_start + i, c_start + i])
        block_diagonals.append(diag_sum)

ascii_diag = to_ascii([d & 0xFF for d in block_diagonals])
print(f"Block-Diagonal-Summen: {block_diagonals[:20]}...")
print(f"ASCII: {ascii_diag[:64]}...")

words_diag = find_words(ascii_diag, KNOWN_WORDS)
if words_diag:
    print(f"WÖRTER: {[w['word'] for w in words_diag]}")
print()

# =============================================================================
# METHODE 4: QUADRANTEN-ANALYSE
# =============================================================================
print("[4] QUADRANTEN-ANALYSE (4 Quadranten à 64×64)")
print("-" * 60)

quadrants = [
    ("TL (0-63, 0-63)", matrix[0:64, 0:64]),
    ("TR (0-63, 64-127)", matrix[0:64, 64:128]),
    ("BL (64-127, 0-63)", matrix[64:128, 0:64]),
    ("BR (64-127, 64-127)", matrix[64:128, 64:128])
]

for name, quad in quadrants:
    q_sum = int(np.sum(quad))
    q_xor = 0
    for val in quad.flatten():
        q_xor ^= (int(val) & 0xFF)
    print(f"  {name}: Summe={q_sum:7}, XOR={q_xor:3} ('{chr(q_xor) if 32 <= q_xor <= 126 else '.'}')")

# XOR der Quadranten-Paare
tl = matrix[0:64, 0:64]
br = matrix[64:128, 64:128]
tr = matrix[0:64, 64:128]
bl = matrix[64:128, 0:64]

# TL XOR BR (diagonal gegenüber)
tl_br_xor = []
for r in range(64):
    for c in range(64):
        tl_br_xor.append((int(tl[r, c]) & 0xFF) ^ (int(br[r, c]) & 0xFF))

ascii_tl_br = to_ascii(tl_br_xor)
print(f"\n  TL XOR BR: {ascii_tl_br[:80]}...")
words_tl_br = find_words(ascii_tl_br, KNOWN_WORDS)
if words_tl_br:
    print(f"  WÖRTER TL XOR BR: {[w['word'] for w in words_tl_br]}")

# TR XOR BL (anti-diagonal gegenüber)
tr_bl_xor = []
for r in range(64):
    for c in range(64):
        tr_bl_xor.append((int(tr[r, c]) & 0xFF) ^ (int(bl[r, c]) & 0xFF))

ascii_tr_bl = to_ascii(tr_bl_xor)
print(f"  TR XOR BL: {ascii_tr_bl[:80]}...")
words_tr_bl = find_words(ascii_tr_bl, KNOWN_WORDS)
if words_tr_bl:
    print(f"  WÖRTER TR XOR BL: {[w['word'] for w in words_tr_bl]}")

print()

# =============================================================================
# METHODE 5: RING-ANALYSE (konzentrische Ringe)
# =============================================================================
print("[5] RING-ANALYSE (konzentrische Ringe um das Zentrum)")
print("-" * 60)

ring_xors = []
for ring in range(64):  # 64 Ringe von außen nach innen
    ring_values = []

    # Obere Kante
    for c in range(ring, 128 - ring):
        ring_values.append(int(matrix[ring, c]) & 0xFF)

    # Rechte Kante (ohne Ecken)
    for r in range(ring + 1, 127 - ring):
        ring_values.append(int(matrix[r, 127 - ring]) & 0xFF)

    # Untere Kante (rückwärts)
    for c in range(127 - ring, ring - 1, -1):
        ring_values.append(int(matrix[127 - ring, c]) & 0xFF)

    # Linke Kante (ohne Ecken, rückwärts)
    for r in range(126 - ring, ring, -1):
        ring_values.append(int(matrix[r, ring]) & 0xFF)

    # XOR aller Werte im Ring
    ring_xor = 0
    for v in ring_values:
        ring_xor ^= v
    ring_xors.append(ring_xor)

ascii_rings = to_ascii(ring_xors)
print(f"64 Ring-XORs: {ring_xors}")
print(f"ASCII: {ascii_rings}")

words_rings = find_words(ascii_rings, KNOWN_WORDS)
if words_rings:
    print(f"WÖRTER: {[w['word'] for w in words_rings]}")
print()

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("=" * 80)
print("[6] ZUSAMMENFASSUNG")
print("=" * 80)

all_words = set()
for w in words_8_sums + words_8_xors + words_16_sums + words_16_xors + words_diag + words_tl_br + words_tr_bl + words_rings:
    all_words.add(w['word'])

print(f"""
ERGEBNISSE:
===========

1. 8×8 Blöcke (256 Stück):
   - Summen-ASCII: {'Wörter gefunden' if words_8_sums else 'keine Wörter'}
   - XOR-ASCII: {'Wörter gefunden' if words_8_xors else 'keine Wörter'}

2. 16×16 Blöcke (64 Stück):
   - Summen-ASCII: {'Wörter gefunden' if words_16_sums else 'keine Wörter'}
   - XOR-ASCII: {'Wörter gefunden' if words_16_xors else 'keine Wörter'}

3. Quadranten XOR:
   - TL XOR BR: {'Wörter gefunden' if words_tl_br else 'keine Wörter'}
   - TR XOR BL: {'Wörter gefunden' if words_tr_bl else 'keine Wörter'}

4. Ring-XOR: {'Wörter gefunden' if words_rings else 'keine Wörter'}

ALLE GEFUNDENEN WÖRTER: {sorted(all_words) if all_words else 'keine'}

KRITISCHE BEWERTUNG:
- Block-basierte Dekodierung {'zeigt Ergebnisse' if all_words else 'zeigt keine neuen Nachrichten'}
- Signifikanz: {'MITTEL' if len(all_words) > 3 else 'NIEDRIG'}
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'block_8x8': {
        'count': 256,
        'sums_ascii': ascii_8_sums,
        'xors_ascii': ascii_8_xors,
        'words_in_sums': [w['word'] for w in words_8_sums],
        'words_in_xors': [w['word'] for w in words_8_xors]
    },
    'block_16x16': {
        'count': 64,
        'sums': block_16_sums,
        'sums_ascii': ascii_16_sums,
        'xors_ascii': ascii_16_xors,
        'words_in_sums': [w['word'] for w in words_16_sums],
        'words_in_xors': [w['word'] for w in words_16_xors]
    },
    'quadrant_xor': {
        'tl_br_words': [w['word'] for w in words_tl_br],
        'tr_bl_words': [w['word'] for w in words_tr_bl]
    },
    'ring_analysis': {
        'ring_xors': ring_xors,
        'ascii': ascii_rings,
        'words': [w['word'] for w in words_rings]
    },
    'all_unique_words': sorted(all_words)
}

with open('BLOCK_DECODE.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: BLOCK_DECODE.json")
print("=" * 80)
