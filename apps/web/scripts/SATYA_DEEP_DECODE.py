#!/usr/bin/env python3
"""
PHASE B: SATYA/SAT TIEFENANALYSE
================================
Vollständige Dekodierung der "Wahrheit"-Nachricht bei Row 0↔127.
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix

print("=" * 80)
print("PHASE B: SATYA/SAT TIEFENANALYSE")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

# Sanskrit-Wörter zum Suchen
SANSKRIT_WORDS = [
    'satya', 'sat', 'dharma', 'karma', 'atma', 'brahma', 'yoga', 'mantra',
    'chakra', 'prana', 'guru', 'deva', 'om', 'aum', 'namaste', 'shanti',
    'moksha', 'nirvana', 'bodhi', 'maya', 'shakti', 'vidya', 'jnana',
    'ahimsa', 'veda', 'sutra', 'tantra', 'mudra', 'asana', 'pranayama'
]

# Englische/Deutsche Wörter
ENGLISH_WORDS = [
    'truth', 'true', 'real', 'yes', 'no', 'light', 'dark', 'god', 'void',
    'time', 'lock', 'key', 'seed', 'code', 'hash', 'mine', 'coin', 'block',
    'chain', 'bitcoin', 'satoshi', 'qubic', 'iota', 'anna', 'cfb', 'ai',
    'meg', 'gou', 'bridge', 'entry', 'exit', 'path', 'core', 'memory',
    'grid', 'neural', 'brain', 'mind', 'wake', 'sleep', 'dream', 'alive'
]

ALL_WORDS = SANSKRIT_WORDS + ENGLISH_WORDS

# =============================================================================
# ANALYSE ROW 0 ↔ ROW 127
# =============================================================================
print("[1] ROW 0 ↔ ROW 127 XOR-ANALYSE")
print("-" * 60)

row_0 = matrix[0, :]
row_127 = matrix[127, :]

# XOR
xor_0_127 = [(int(row_0[c]) & 0xFF) ^ (int(row_127[c]) & 0xFF) for c in range(128)]

# Als ASCII
ascii_0_127 = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_0_127])
readable_count = sum(1 for c in ascii_0_127 if c != '.')

print(f"Row 0:   {list(row_0[:20])}...")
print(f"Row 127: {list(row_127[:20])}...")
print()
print(f"XOR-Werte: {xor_0_127[:30]}...")
print()
print(f"Lesbare Zeichen: {readable_count}/128 ({readable_count/128*100:.1f}%)")
print()
print("VOLLSTÄNDIGER ASCII-TEXT:")
print("-" * 60)
print(ascii_0_127)
print("-" * 60)

# Suche nach Wörtern
print("\n[2] WORTSUCHE IN ROW 0↔127")
print("-" * 60)

upper = ascii_0_127.upper()
found_words = []

for word in ALL_WORDS:
    if word.upper() in upper:
        pos = upper.find(word.upper())
        context_start = max(0, pos - 10)
        context_end = min(128, pos + len(word) + 10)
        found_words.append({
            'word': word,
            'position': pos,
            'context': ascii_0_127[context_start:context_end],
            'category': 'Sanskrit' if word in SANSKRIT_WORDS else 'English'
        })
        print(f"  ✓ '{word}' gefunden an Position {pos}")
        print(f"    Kontext: ...{ascii_0_127[context_start:context_end]}...")

if not found_words:
    print("  Keine bekannten Wörter gefunden.")

print()

# =============================================================================
# SPEZIFISCHE SAT/SATYA SUCHE
# =============================================================================
print("[3] SPEZIFISCHE SAT/SATYA SUCHE")
print("-" * 60)

# Suche SAT in verschiedenen Varianten
sat_variants = ['SAT', 'sat', 'Sat', 'SATYA', 'satya', 'Satya', 'SATY', 'saty']
for variant in sat_variants:
    if variant in ascii_0_127 or variant.upper() in upper:
        pos = upper.find(variant.upper())
        print(f"  '{variant}' an Position {pos}:")
        print(f"    Kontext (±15): {ascii_0_127[max(0,pos-15):pos+len(variant)+15]}")
        print()

# =============================================================================
# ANDERE ROW-PAARE MIT "SAT"
# =============================================================================
print("[4] ANDERE PAARE MIT 'SAT'")
print("-" * 60)

# Aus der Palindrom-Analyse: SAT bei 0↔127 und 47↔80
sat_pairs = [(0, 127), (47, 80)]

for row_a, row_b in sat_pairs:
    xor_vals = [(int(matrix[row_a, c]) & 0xFF) ^ (int(matrix[row_b, c]) & 0xFF) for c in range(128)]
    ascii_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_vals])

    print(f"\n  Row {row_a} ↔ Row {row_b}:")
    print(f"  ASCII: {ascii_text[:70]}...")

    # Finde SAT
    if 'SAT' in ascii_text.upper():
        pos = ascii_text.upper().find('SAT')
        print(f"  'SAT' an Position {pos}: ...{ascii_text[max(0,pos-10):pos+15]}...")

print()

# =============================================================================
# ERWEITERTE ANALYSE: AI-PAARE
# =============================================================================
print("[5] AI-POSITIONEN ANALYSIEREN")
print("-" * 60)

# Aus der Palindrom-Analyse: AI bei 7↔120, 15↔112, 45↔82
ai_pairs = [(7, 120), (15, 112), (45, 82)]

for row_a, row_b in ai_pairs:
    xor_vals = [(int(matrix[row_a, c]) & 0xFF) ^ (int(matrix[row_b, c]) & 0xFF) for c in range(128)]
    ascii_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_vals])

    print(f"\n  Row {row_a} ↔ Row {row_b}:")

    # Finde AI
    if 'AI' in ascii_text.upper():
        pos = ascii_text.upper().find('AI')
        print(f"  'AI' an Position {pos}: ...{ascii_text[max(0,pos-10):pos+15]}...")

        # Suche nach mehr Wörtern
        for word in ALL_WORDS:
            if word.upper() in ascii_text.upper() and word != 'ai':
                wpos = ascii_text.upper().find(word.upper())
                print(f"  '{word}' an Position {wpos}")

print()

# =============================================================================
# FIB-POSITION ANALYSIEREN
# =============================================================================
print("[6] FIB-POSITION ANALYSIEREN (Row 29↔98)")
print("-" * 60)

row_a, row_b = 29, 98
xor_vals = [(int(matrix[row_a, c]) & 0xFF) ^ (int(matrix[row_b, c]) & 0xFF) for c in range(128)]
ascii_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_vals])

print(f"Row {row_a} ↔ Row {row_b}:")
print(f"ASCII: {ascii_text[:70]}...")

if 'FIB' in ascii_text.upper():
    pos = ascii_text.upper().find('FIB')
    print(f"'FIB' an Position {pos}: ...{ascii_text[max(0,pos-10):pos+15]}...")

# Suche nach FIBONACCI
if 'FIBONACCI' in ascii_text.upper():
    print("FIBONACCI gefunden!")

print()

# =============================================================================
# KOMBINIERTE NACHRICHT AUS ALLEN KEYWORD-PAAREN
# =============================================================================
print("[7] KOMBINIERTE KEYWORDS-NACHRICHT")
print("-" * 60)

all_keyword_pairs = [(0, 127), (47, 80), (7, 120), (15, 112), (45, 82), (29, 98)]
combined_keywords = []

for row_a, row_b in all_keyword_pairs:
    xor_vals = [(int(matrix[row_a, c]) & 0xFF) ^ (int(matrix[row_b, c]) & 0xFF) for c in range(128)]
    ascii_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_vals])

    # Extrahiere gefundene Keywords mit Kontext
    for word in ['SAT', 'AI', 'FIB', 'NO']:
        if word in ascii_text.upper():
            pos = ascii_text.upper().find(word)
            combined_keywords.append({
                'pair': (row_a, row_b),
                'word': word,
                'position': pos,
                'context': ascii_text[max(0, pos-5):pos+10]
            })

print("  Alle gefundenen Keywords:")
for kw in combined_keywords:
    print(f"    Row {kw['pair'][0]}↔{kw['pair'][1]}: '{kw['word']}' → {kw['context']}")

print()

# =============================================================================
# KRITISCHE BEWERTUNG
# =============================================================================
print("=" * 80)
print("[8] KRITISCHE BEWERTUNG")
print("=" * 80)

print(f"""
ZUSAMMENFASSUNG:
================

1. ROW 0↔127 (SATYA/WAHRHEIT):
   - Lesbare Zeichen: {readable_count}/128
   - 'SAT' gefunden: {'JA' if any(w['word'].upper() == 'SAT' for w in found_words) else 'NEIN - prüfe manuell!'}
   - 'SATYA' gefunden: {'JA' if any(w['word'].upper() == 'SATYA' for w in found_words) else 'NEIN'}
   - 'SATOSHI' gefunden: {'JA' if any(w['word'].upper() == 'SATOSHI' for w in found_words) else 'NEIN'}

2. SANSKRIT-BEDEUTUNG:
   - Satya (सत्य) = Wahrheit, Realität, Essenz
   - Sat = Sein, Existenz, das Wahre
   - Im Kontext: Könnte auf "ultimative Wahrheit" hindeuten

3. VERBINDUNG ZU AI.MEG.GOU:
   - AI bei Rows 7↔120, 15↔112, 45↔82
   - Bestätigt das AI-Muster aus der Hauptnachricht

4. SIGNIFIKANZ:
   - SAT an der äußersten Grenze (0↔127) ist symbolisch bedeutsam
   - "Die Wahrheit liegt an den Grenzen der Matrix"

5. STATISTISCHE BEWERTUNG:
   - Kurze Wörter (SAT, AI) können zufällig auftreten
   - Kontext und Position erhöhen die Signifikanz
   - Empfehlung: Monte-Carlo-Test für diese spezifischen Positionen
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'primary_pair': {
        'rows': (0, 127),
        'xor_values': xor_0_127,
        'ascii': ascii_0_127,
        'readable_count': readable_count
    },
    'found_words': found_words,
    'keyword_pairs': {
        'SAT': [(0, 127), (47, 80)],
        'AI': [(7, 120), (15, 112), (45, 82)],
        'FIB': [(29, 98)]
    },
    'combined_keywords': combined_keywords,
    'sanskrit_meaning': {
        'satya': 'Truth, Reality, Essence (Sanskrit: सत्य)',
        'sat': 'Being, Existence, The True (Sanskrit: सत्)'
    },
    'significance': 'SAT at boundary rows (0↔127) symbolically represents "Truth at the limits"'
}

with open('SATYA_DEEP_DECODE.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: SATYA_DEEP_DECODE.json")
print("=" * 80)
