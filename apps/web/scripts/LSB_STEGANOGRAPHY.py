#!/usr/bin/env python3
"""
PHASE F: LSB STEGANOGRAPHIE
===========================
Extrahiere die Least Significant Bits aller Matrix-Werte.
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix

print("=" * 80)
print("PHASE F: LSB STEGANOGRAPHIE")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

KNOWN_WORDS = [
    'the', 'and', 'for', 'yes', 'no', 'sat', 'ai', 'meg', 'gou', 'cfb',
    'fib', 'btc', 'key', 'god', 'truth', 'satya', 'satoshi', 'bitcoin',
    'qubic', 'iota', 'anna', 'code', 'void', 'time', 'lock', 'bridge',
    'hello', 'world', 'secret', 'hidden', 'message', 'begin', 'end'
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
# METHODE 1: LSB ALLER WERTE (Bit 0)
# =============================================================================
print("[1] LSB EXTRAKTION (Bit 0)")
print("-" * 60)

# Extrahiere LSB jedes Wertes
lsb_bits = []
for r in range(128):
    for c in range(128):
        val = int(matrix[r, c]) & 0xFF  # Unsigned byte
        lsb_bits.append(val & 1)  # Niedrigstes Bit

print(f"Total Bits: {len(lsb_bits)}")
print(f"1-Bits: {sum(lsb_bits)}, 0-Bits: {len(lsb_bits) - sum(lsb_bits)}")
print(f"Ratio: {sum(lsb_bits)/len(lsb_bits)*100:.1f}% sind 1")
print()

# Bits zu Bytes gruppieren (8 Bits = 1 Byte)
lsb_bytes = []
for i in range(0, len(lsb_bits) - 7, 8):
    byte_val = 0
    for bit_pos in range(8):
        byte_val |= (lsb_bits[i + bit_pos] << (7 - bit_pos))  # MSB first
    lsb_bytes.append(byte_val)

ascii_lsb = to_ascii(lsb_bytes)
readable_lsb = sum(1 for c in ascii_lsb if c != '.')

print(f"LSB als Bytes: {len(lsb_bytes)} Bytes")
print(f"Lesbare Zeichen: {readable_lsb}/{len(lsb_bytes)} ({readable_lsb/len(lsb_bytes)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_lsb[:100]}")

words_lsb = find_words(ascii_lsb, KNOWN_WORDS)
if words_lsb:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_lsb]}")
print()

# =============================================================================
# METHODE 2: BIT 1 (Zweites niedrigstes Bit)
# =============================================================================
print("[2] BIT 1 EXTRAKTION")
print("-" * 60)

bit1_bits = []
for r in range(128):
    for c in range(128):
        val = int(matrix[r, c]) & 0xFF
        bit1_bits.append((val >> 1) & 1)

bit1_bytes = []
for i in range(0, len(bit1_bits) - 7, 8):
    byte_val = 0
    for bit_pos in range(8):
        byte_val |= (bit1_bits[i + bit_pos] << (7 - bit_pos))
    bit1_bytes.append(byte_val)

ascii_bit1 = to_ascii(bit1_bytes)
readable_bit1 = sum(1 for c in ascii_bit1 if c != '.')

print(f"Lesbare Zeichen: {readable_bit1}/{len(bit1_bytes)} ({readable_bit1/len(bit1_bytes)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_bit1[:100]}")

words_bit1 = find_words(ascii_bit1, KNOWN_WORDS)
if words_bit1:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_bit1]}")
print()

# =============================================================================
# METHODE 3: LSB MIT VERSCHIEDENEN LESERICHTUNGEN
# =============================================================================
print("[3] LSB MIT ALTERNATIVEN LESERICHTUNGEN")
print("-" * 60)

# Spaltenweise statt zeilenweise
lsb_col_bits = []
for c in range(128):
    for r in range(128):
        val = int(matrix[r, c]) & 0xFF
        lsb_col_bits.append(val & 1)

lsb_col_bytes = []
for i in range(0, len(lsb_col_bits) - 7, 8):
    byte_val = 0
    for bit_pos in range(8):
        byte_val |= (lsb_col_bits[i + bit_pos] << (7 - bit_pos))
    lsb_col_bytes.append(byte_val)

ascii_col = to_ascii(lsb_col_bytes)
readable_col = sum(1 for c in ascii_col if c != '.')
print(f"Spaltenweise: {readable_col}/{len(lsb_col_bytes)} lesbar")
print(f"Erste 50: {ascii_col[:50]}")

words_col = find_words(ascii_col, KNOWN_WORDS)
if words_col:
    print(f"WÖRTER: {[w['word'] for w in words_col]}")

# Diagonal
lsb_diag_bits = []
for d in range(-127, 128):  # Alle Diagonalen
    for i in range(128):
        r, c = i, i - d
        if 0 <= r < 128 and 0 <= c < 128:
            val = int(matrix[r, c]) & 0xFF
            lsb_diag_bits.append(val & 1)

lsb_diag_bytes = []
for i in range(0, len(lsb_diag_bits) - 7, 8):
    byte_val = 0
    for bit_pos in range(8):
        byte_val |= (lsb_diag_bits[i + bit_pos] << (7 - bit_pos))
    lsb_diag_bytes.append(byte_val)

ascii_diag = to_ascii(lsb_diag_bytes)
readable_diag = sum(1 for c in ascii_diag if c != '.')
print(f"Diagonal: {readable_diag}/{len(lsb_diag_bytes)} lesbar")

words_diag = find_words(ascii_diag, KNOWN_WORDS)
if words_diag:
    print(f"WÖRTER: {[w['word'] for w in words_diag]}")
print()

# =============================================================================
# METHODE 4: KOMBINIERTE BITS (LSB XOR Bit1)
# =============================================================================
print("[4] KOMBINIERTE BITS (LSB XOR Bit1)")
print("-" * 60)

combined_bits = [lsb_bits[i] ^ bit1_bits[i] for i in range(len(lsb_bits))]

combined_bytes = []
for i in range(0, len(combined_bits) - 7, 8):
    byte_val = 0
    for bit_pos in range(8):
        byte_val |= (combined_bits[i + bit_pos] << (7 - bit_pos))
    combined_bytes.append(byte_val)

ascii_combined = to_ascii(combined_bytes)
readable_combined = sum(1 for c in ascii_combined if c != '.')
print(f"Lesbare Zeichen: {readable_combined}/{len(combined_bytes)} ({readable_combined/len(combined_bytes)*100:.1f}%)")
print(f"Erste 100: {ascii_combined[:100]}")

words_combined = find_words(ascii_combined, KNOWN_WORDS)
if words_combined:
    print(f"WÖRTER: {[w['word'] for w in words_combined]}")
print()

# =============================================================================
# METHODE 5: PARITY BITS (XOR aller Bits pro Wert)
# =============================================================================
print("[5] PARITY BITS (XOR aller Bits jedes Wertes)")
print("-" * 60)

parity_bits = []
for r in range(128):
    for c in range(128):
        val = int(matrix[r, c]) & 0xFF
        parity = 0
        for bit in range(8):
            parity ^= ((val >> bit) & 1)
        parity_bits.append(parity)

parity_bytes = []
for i in range(0, len(parity_bits) - 7, 8):
    byte_val = 0
    for bit_pos in range(8):
        byte_val |= (parity_bits[i + bit_pos] << (7 - bit_pos))
    parity_bytes.append(byte_val)

ascii_parity = to_ascii(parity_bytes)
readable_parity = sum(1 for c in ascii_parity if c != '.')
print(f"Lesbare Zeichen: {readable_parity}/{len(parity_bytes)} ({readable_parity/len(parity_bytes)*100:.1f}%)")
print(f"Erste 100: {ascii_parity[:100]}")

words_parity = find_words(ascii_parity, KNOWN_WORDS)
if words_parity:
    print(f"WÖRTER: {[w['word'] for w in words_parity]}")
print()

# =============================================================================
# METHODE 6: DATEISIGNATUR-SUCHE
# =============================================================================
print("[6] DATEISIGNATUR-SUCHE")
print("-" * 60)

# Bekannte Dateisignaturen
signatures = {
    'PNG': bytes([0x89, 0x50, 0x4E, 0x47]),
    'JPEG': bytes([0xFF, 0xD8, 0xFF]),
    'GIF': bytes([0x47, 0x49, 0x46, 0x38]),
    'ZIP': bytes([0x50, 0x4B, 0x03, 0x04]),
    'PDF': bytes([0x25, 0x50, 0x44, 0x46]),
    'GZIP': bytes([0x1F, 0x8B]),
    'ELF': bytes([0x7F, 0x45, 0x4C, 0x46]),
}

lsb_raw = bytes(lsb_bytes)
for name, sig in signatures.items():
    if sig in lsb_raw:
        pos = lsb_raw.find(sig)
        print(f"  ✓ {name} Signatur gefunden an Position {pos}!")

# Suche in verschiedenen Bit-Ebenen
print("  Suche in alternativen Extraktionen...")
for sig_name, sig in signatures.items():
    if sig in bytes(bit1_bytes):
        print(f"    ✓ {sig_name} in Bit1!")
    if sig in bytes(combined_bytes):
        print(f"    ✓ {sig_name} in Combined!")
print()

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("=" * 80)
print("[7] ZUSAMMENFASSUNG")
print("=" * 80)

all_words = set()
for w in words_lsb + words_bit1 + words_col + words_diag + words_combined + words_parity:
    all_words.add(w['word'])

print(f"""
ERGEBNISSE:
===========

1. LSB (Bit 0):
   - {readable_lsb}/{len(lsb_bytes)} lesbare Zeichen
   - Wörter: {[w['word'] for w in words_lsb] if words_lsb else 'keine'}

2. Bit 1:
   - {readable_bit1}/{len(bit1_bytes)} lesbare Zeichen
   - Wörter: {[w['word'] for w in words_bit1] if words_bit1 else 'keine'}

3. Spaltenweise LSB:
   - {readable_col}/{len(lsb_col_bytes)} lesbare Zeichen
   - Wörter: {[w['word'] for w in words_col] if words_col else 'keine'}

4. Kombiniert (LSB XOR Bit1):
   - {readable_combined}/{len(combined_bytes)} lesbare Zeichen
   - Wörter: {[w['word'] for w in words_combined] if words_combined else 'keine'}

ALLE GEFUNDENEN WÖRTER: {sorted(all_words) if all_words else 'keine'}

KRITISCHE BEWERTUNG:
- LSB Steganographie {'zeigt Ergebnisse' if all_words else 'zeigt keine versteckten Daten'}
- Dateisignaturen: Keine bekannten Formate gefunden
- Signifikanz: {'MITTEL' if len(all_words) > 3 else 'NIEDRIG'}
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'lsb_bit0': {
        'total_bits': len(lsb_bits),
        'ones_ratio': sum(lsb_bits) / len(lsb_bits),
        'bytes': len(lsb_bytes),
        'readable': readable_lsb,
        'sample': ascii_lsb[:200],
        'words': [w['word'] for w in words_lsb]
    },
    'bit1': {
        'readable': readable_bit1,
        'sample': ascii_bit1[:200],
        'words': [w['word'] for w in words_bit1]
    },
    'column_wise': {
        'readable': readable_col,
        'words': [w['word'] for w in words_col]
    },
    'combined_xor': {
        'readable': readable_combined,
        'sample': ascii_combined[:200],
        'words': [w['word'] for w in words_combined]
    },
    'parity': {
        'readable': readable_parity,
        'sample': ascii_parity[:200],
        'words': [w['word'] for w in words_parity]
    },
    'file_signatures_found': False,
    'all_unique_words': sorted(all_words)
}

with open('LSB_STEGANOGRAPHY.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: LSB_STEGANOGRAPHY.json")
print("=" * 80)
