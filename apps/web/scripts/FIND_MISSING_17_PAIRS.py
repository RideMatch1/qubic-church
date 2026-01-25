#!/usr/bin/env python3
"""
PHASE A: DIE 17 FEHLENDEN ZEILENPAARE
=====================================
Identifiziere und analysiere die Paare, die KEINE Palindrome bilden.
Hypothese: Diese könnten die Hauptnachricht enthalten!
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix
import re

print("=" * 80)
print("PHASE A: DIE 17 FEHLENDEN ZEILENPAARE")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

# Lade die gefundenen Palindrom-Paare
with open('PALINDROME_DEEP_ANALYSIS.json', 'r') as f:
    palindrome_data = json.load(f)

found_pairs = set()
for pair in palindrome_data['row_pairs']:
    found_pairs.add(tuple(sorted(pair)))

print(f"[1] GEFUNDENE PALINDROM-PAARE: {len(found_pairs)}")
print("-" * 60)

# Alle 64 möglichen Paare (0↔127, 1↔126, ... 63↔64)
all_possible_pairs = set()
for i in range(64):
    all_possible_pairs.add((i, 127 - i))

print(f"Alle möglichen Paare (Summe=127): {len(all_possible_pairs)}")
print()

# Fehlende Paare identifizieren
missing_pairs = all_possible_pairs - found_pairs
print(f"[2] FEHLENDE PAARE: {len(missing_pairs)}")
print("-" * 60)

missing_sorted = sorted(missing_pairs, key=lambda x: x[0])
for pair in missing_sorted:
    print(f"  Row {pair[0]:3} ↔ Row {pair[1]:3}")

print()

# =============================================================================
# ANALYSE DER FEHLENDEN PAARE
# =============================================================================
print("[3] DETAILANALYSE DER FEHLENDEN PAARE")
print("-" * 60)

KNOWN_WORDS = [
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
    'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
    'how', 'its', 'let', 'may', 'new', 'now', 'old', 'see', 'two', 'way',
    'who', 'boy', 'did', 'man', 'say', 'she', 'too', 'use', 'god', 'dog',
    'cat', 'sun', 'web', 'net', 'bit', 'key', 'yes', 'no', 'ai', 'sat',
    'cfb', 'meg', 'gou', 'anna', 'iota', 'seed', 'code', 'hash', 'mine',
    'coin', 'truth', 'satya', 'satoshi', 'bitcoin', 'qubic', 'void', 'time',
    'lock', 'bridge', 'memory', 'grid', 'core', 'entry', 'exit', 'path'
]

missing_analysis = []

for row_a, row_b in missing_sorted:
    # XOR der beiden Zeilen
    xor_vals = [(int(matrix[row_a, c]) & 0xFF) ^ (int(matrix[row_b, c]) & 0xFF) for c in range(128)]

    # Als ASCII
    ascii_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_vals])
    readable_count = sum(1 for c in ascii_text if c != '.')

    # Suche nach Wörtern
    found_words = []
    upper = ascii_text.upper()
    for word in KNOWN_WORDS:
        if word.upper() in upper:
            pos = upper.find(word.upper())
            found_words.append({
                'word': word,
                'position': pos,
                'context': ascii_text[max(0, pos-5):pos+len(word)+5]
            })

    # Prüfe ob es ein Palindrom ist
    is_palindrome = ascii_text == ascii_text[::-1]

    # Speichere Analyse
    analysis = {
        'pair': (row_a, row_b),
        'sum': row_a + row_b,
        'xor_values': xor_vals,
        'ascii': ascii_text,
        'readable_count': readable_count,
        'is_palindrome': is_palindrome,
        'found_words': found_words
    }
    missing_analysis.append(analysis)

    # Ausgabe
    print(f"\n  ROW {row_a} ↔ ROW {row_b} (Summe={row_a + row_b})")
    print(f"  Lesbar: {readable_count}/128 ({readable_count/128*100:.1f}%)")
    print(f"  Palindrom: {'JA' if is_palindrome else 'NEIN'}")
    print(f"  ASCII: {ascii_text[:60]}...")
    if found_words:
        print(f"  GEFUNDENE WÖRTER: {[w['word'] for w in found_words]}")

print()

# =============================================================================
# WARUM FEHLEN DIESE PAARE?
# =============================================================================
print("[4] ANALYSE: WARUM FEHLEN DIESE PAARE?")
print("-" * 60)

# Prüfe Lesbarkeit
readable_counts = [a['readable_count'] for a in missing_analysis]
avg_readable = sum(readable_counts) / len(readable_counts) if readable_counts else 0

print(f"  Durchschnittliche Lesbarkeit: {avg_readable:.1f} Zeichen")
print(f"  Min: {min(readable_counts)}, Max: {max(readable_counts)}")
print()

# Prüfe auf gemeinsame Muster
all_words_found = []
for a in missing_analysis:
    for w in a['found_words']:
        all_words_found.append(w['word'])

from collections import Counter
word_freq = Counter(all_words_found)
print(f"  Gefundene Wörter insgesamt: {len(all_words_found)}")
if word_freq:
    print(f"  Häufigste: {word_freq.most_common(10)}")
print()

# =============================================================================
# KOMBINIERTE NACHRICHT AUS ALLEN FEHLENDEN PAAREN
# =============================================================================
print("[5] KOMBINIERTE NACHRICHT")
print("-" * 60)

# Extrahiere nur lesbare Zeichen aus jedem Paar
combined_readable = ""
for a in missing_analysis:
    # Nur Buchstaben extrahieren
    letters_only = ''.join([c for c in a['ascii'] if c.isalpha()])
    combined_readable += letters_only

print(f"  Kombinierte Buchstaben: {len(combined_readable)}")
print(f"  Text (erste 200): {combined_readable[:200]}")

# Suche nach Wörtern in kombinierter Nachricht
print("\n  Wörter in kombinierter Nachricht:")
combined_upper = combined_readable.upper()
for word in sorted(KNOWN_WORDS, key=len, reverse=True):
    if word.upper() in combined_upper:
        count = combined_upper.count(word.upper())
        print(f"    '{word}': {count}×")

print()

# =============================================================================
# XOR ALLER FEHLENDEN PAARE
# =============================================================================
print("[6] XOR ALLER FEHLENDEN PAARE")
print("-" * 60)

# XOR alle XOR-Werte zusammen
total_xor = [0] * 128
for a in missing_analysis:
    for i, v in enumerate(a['xor_values']):
        total_xor[i] ^= v

total_ascii = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in total_xor])
print(f"  XOR aller {len(missing_analysis)} fehlenden Paare:")
print(f"  ASCII: {total_ascii}")

# Suche nach Wörtern
total_upper = total_ascii.upper()
found_in_total = []
for word in KNOWN_WORDS:
    if word.upper() in total_upper:
        found_in_total.append(word)
if found_in_total:
    print(f"  GEFUNDENE WÖRTER: {found_in_total}")

print()

# =============================================================================
# SPEZIELLE ANALYSE: DIE VIELVERSPRECHENDSTEN PAARE
# =============================================================================
print("[7] DIE VIELVERSPRECHENDSTEN PAARE")
print("-" * 60)

# Sortiere nach Anzahl gefundener Wörter
missing_analysis.sort(key=lambda x: len(x['found_words']), reverse=True)

print("  TOP 5 PAARE MIT WÖRTERN:")
for a in missing_analysis[:5]:
    if a['found_words']:
        print(f"\n  Row {a['pair'][0]} ↔ Row {a['pair'][1]}:")
        print(f"    ASCII: {a['ascii'][:70]}...")
        for w in a['found_words']:
            print(f"    '{w['word']}' an Position {w['position']}: {w['context']}")

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

1. FEHLENDE PAARE: {len(missing_pairs)}
   - Diese Paare bilden KEINE perfekten Palindrome
   - Aber sie haben trotzdem Summe = 127

2. LESBARKEIT:
   - Durchschnitt: {avg_readable:.1f} Zeichen pro Paar
   - Vergleich: AI.MEG.GOU hat 82 lesbare Zeichen

3. GEFUNDENE WÖRTER:
   - In fehlenden Paaren: {len(all_words_found)} Wörter
   - Häufigste: {word_freq.most_common(5) if word_freq else 'keine'}

4. HYPOTHESE-TEST:
   - "17 fehlende Paare = Hauptnachricht"
   - Ergebnis: {'TEILWEISE BESTÄTIGT' if all_words_found else 'NICHT BESTÄTIGT'}

5. SIGNIFIKANZ:
   - Die fehlenden Paare enthalten {'einige' if all_words_found else 'keine'} lesbare Wörter
   - Weitere Analyse empfohlen für Paare mit hoher Lesbarkeit
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'total_possible_pairs': 64,
    'found_palindrome_pairs': len(found_pairs),
    'missing_pairs_count': len(missing_pairs),
    'missing_pairs': missing_sorted,
    'analysis': [
        {
            'pair': a['pair'],
            'sum': a['sum'],
            'readable_count': a['readable_count'],
            'is_palindrome': a['is_palindrome'],
            'ascii': a['ascii'],
            'found_words': [w['word'] for w in a['found_words']]
        }
        for a in missing_analysis
    ],
    'combined_readable_length': len(combined_readable),
    'words_in_missing_pairs': list(word_freq.keys()) if word_freq else [],
    'xor_all_missing': total_ascii,
    'hypothesis_result': 'PARTIALLY_CONFIRMED' if all_words_found else 'NOT_CONFIRMED'
}

with open('MISSING_17_PAIRS_ANALYSIS.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: MISSING_17_PAIRS_ANALYSIS.json")
print("=" * 80)
