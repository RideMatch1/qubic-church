#!/usr/bin/env python3
"""
SYSTEMATISCHE ANALYSE ALLER 64 SPALTENPAARE
============================================
Was haben wir übersehen? Prüfe ALLE Paare, nicht nur 30↔97.
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix
from collections import Counter

print("=" * 80)
print("SYSTEMATISCHE ANALYSE ALLER 64 SPALTENPAARE")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

# Erweiterte Wortliste - ALLES was relevant sein könnte
KNOWN_WORDS = [
    # Qubic/CFB spezifisch
    'ai', 'meg', 'gou', 'cfb', 'nxt', 'iota', 'qubic', 'anna', 'jinn',
    'aigarth', 'ternary', 'trits', 'trytes', 'tangle', 'dag',

    # Bitcoin/Krypto
    'btc', 'sat', 'satoshi', 'bitcoin', 'block', 'chain', 'hash', 'mine',
    'coin', 'key', 'seed', 'wallet', 'genesis', 'nakamoto',

    # Technisch
    'code', 'data', 'grid', 'node', 'net', 'web', 'api', 'cpu', 'gpu',
    'ram', 'rom', 'io', 'bus', 'bit', 'byte', 'hex', 'bin',

    # Mystisch/Philosophisch
    'god', 'truth', 'satya', 'void', 'time', 'lock', 'bridge', 'gate',
    'path', 'way', 'door', 'portal', 'light', 'dark', 'yin', 'yang',

    # Kurze relevante
    'yes', 'no', 'ok', 'go', 'run', 'end', 'start', 'stop', 'init',
    'hello', 'world', 'test', 'true', 'false', 'null', 'nil',

    # Namen
    'sergey', 'come', 'from', 'beyond', 'anna', 'meg', 'maria',
]

def to_ascii(values):
    """Konvertiert zu ASCII."""
    return ''.join([chr(v & 0xFF) if 32 <= (v & 0xFF) <= 126 else '.' for v in values])

def find_words(text, word_list):
    """Findet Wörter case-insensitive."""
    upper = text.upper()
    found = []
    for word in word_list:
        if len(word) >= 2 and word.upper() in upper:
            pos = upper.find(word.upper())
            found.append({
                'word': word,
                'position': pos,
                'context': text[max(0, pos-3):pos+len(word)+3]
            })
    return found

def count_printable_sequences(text, min_len=3):
    """Zählt zusammenhängende lesbare Sequenzen."""
    sequences = []
    current = ""
    start = 0

    for i, c in enumerate(text):
        if c != '.':
            if not current:
                start = i
            current += c
        else:
            if len(current) >= min_len:
                sequences.append({'start': start, 'text': current, 'length': len(current)})
            current = ""

    if len(current) >= min_len:
        sequences.append({'start': start, 'text': current, 'length': len(current)})

    return sequences

# =============================================================================
# ALLE 64 SPALTENPAARE ANALYSIEREN
# =============================================================================
print("[1] ANALYSE ALLER 64 SPALTENPAARE (Summe=127)")
print("-" * 60)

all_pairs_results = []

for col_a in range(64):
    col_b = 127 - col_a

    # XOR der beiden Spalten
    xor_vals = [(int(matrix[r, col_a]) & 0xFF) ^ (int(matrix[r, col_b]) & 0xFF) for r in range(128)]
    ascii_text = to_ascii(xor_vals)

    # Analyse
    readable_count = sum(1 for c in ascii_text if c != '.')
    found_words = find_words(ascii_text, KNOWN_WORDS)
    sequences = count_printable_sequences(ascii_text)

    result = {
        'pair': (col_a, col_b),
        'readable_count': readable_count,
        'readable_percent': readable_count / 128 * 100,
        'found_words': found_words,
        'sequences': sequences,
        'longest_sequence': max([s['length'] for s in sequences]) if sequences else 0,
        'ascii': ascii_text
    }
    all_pairs_results.append(result)

    # Ausgabe nur wenn interessant
    if found_words or (sequences and max([s['length'] for s in sequences]) >= 4):
        print(f"\n  Col {col_a:3} ↔ {col_b:3}: {readable_count:3} lesbar ({readable_count/128*100:.0f}%)")
        if found_words:
            print(f"    WÖRTER: {[w['word'] for w in found_words]}")
        if sequences:
            long_seqs = [s for s in sequences if s['length'] >= 3]
            if long_seqs:
                print(f"    SEQUENZEN (≥3): {[s['text'] for s in long_seqs[:5]]}")

print()

# =============================================================================
# TOP 10 NACH LESBARKEIT
# =============================================================================
print("[2] TOP 10 SPALTENPAARE NACH LESBARKEIT")
print("-" * 60)

sorted_by_readable = sorted(all_pairs_results, key=lambda x: x['readable_count'], reverse=True)

for i, result in enumerate(sorted_by_readable[:10]):
    col_a, col_b = result['pair']
    print(f"  {i+1}. Col {col_a:3} ↔ {col_b:3}: {result['readable_count']:3} lesbar ({result['readable_percent']:.1f}%)")
    print(f"     Wörter: {[w['word'] for w in result['found_words']] if result['found_words'] else '-'}")
    print(f"     Längste Sequenz: {result['longest_sequence']} Zeichen")
    if result['sequences']:
        best_seq = max(result['sequences'], key=lambda s: s['length'])
        print(f"     Beste: '{best_seq['text']}'")
    print()

# =============================================================================
# TOP 10 NACH WORTFUNDEN
# =============================================================================
print("[3] TOP 10 SPALTENPAARE NACH WORTFUNDEN")
print("-" * 60)

sorted_by_words = sorted(all_pairs_results, key=lambda x: len(x['found_words']), reverse=True)

for i, result in enumerate(sorted_by_words[:10]):
    if not result['found_words']:
        break
    col_a, col_b = result['pair']
    print(f"  {i+1}. Col {col_a:3} ↔ {col_b:3}: {len(result['found_words'])} Wörter")
    print(f"     → {[w['word'] for w in result['found_words']]}")
    print(f"     ASCII: {result['ascii'][:60]}...")
    print()

# =============================================================================
# ALLE GEFUNDENEN WÖRTER ZUSAMMENFASSEN
# =============================================================================
print("[4] ALLE GEFUNDENEN WÖRTER (GLOBAL)")
print("-" * 60)

all_words_found = []
word_locations = {}

for result in all_pairs_results:
    for w in result['found_words']:
        all_words_found.append(w['word'])
        if w['word'] not in word_locations:
            word_locations[w['word']] = []
        word_locations[w['word']].append(result['pair'])

word_freq = Counter(all_words_found)
print(f"  Einzigartige Wörter: {len(word_freq)}")
print(f"  Häufigste:")
for word, count in word_freq.most_common(20):
    print(f"    '{word}': {count}× an Paaren {word_locations[word]}")

print()

# =============================================================================
# VERGLEICH: COL 30↔97 VS ANDERE
# =============================================================================
print("[5] VERGLEICH: COL 30↔97 (AI.MEG.GOU) VS ANDERE")
print("-" * 60)

# Finde Col 30↔97
col_30_97 = next(r for r in all_pairs_results if r['pair'] == (30, 97))

print(f"  Col 30↔97:")
print(f"    Lesbar: {col_30_97['readable_count']} ({col_30_97['readable_percent']:.1f}%)")
print(f"    Wörter: {[w['word'] for w in col_30_97['found_words']]}")
print(f"    Längste Sequenz: {col_30_97['longest_sequence']}")
print()

# Gibt es bessere?
better_readable = [r for r in all_pairs_results if r['readable_count'] > col_30_97['readable_count']]
better_words = [r for r in all_pairs_results if len(r['found_words']) > len(col_30_97['found_words'])]
better_seq = [r for r in all_pairs_results if r['longest_sequence'] > col_30_97['longest_sequence']]

print(f"  Paare mit MEHR lesbaren Zeichen: {len(better_readable)}")
for r in better_readable[:5]:
    print(f"    → Col {r['pair'][0]}↔{r['pair'][1]}: {r['readable_count']} lesbar")

print(f"\n  Paare mit MEHR Wörtern: {len(better_words)}")
for r in better_words[:5]:
    print(f"    → Col {r['pair'][0]}↔{r['pair'][1]}: {len(r['found_words'])} Wörter")

print(f"\n  Paare mit LÄNGEREN Sequenzen: {len(better_seq)}")
for r in better_seq[:5]:
    print(f"    → Col {r['pair'][0]}↔{r['pair'][1]}: {r['longest_sequence']} Zeichen")

print()

# =============================================================================
# SPEZIAL: PAARE MIT "KEY", "SEED", "CODE"
# =============================================================================
print("[6] SPEZIAL: PAARE MIT KRYPTO-KEYWORDS")
print("-" * 60)

crypto_keywords = ['key', 'seed', 'code', 'hash', 'btc', 'coin', 'mine', 'block']

for keyword in crypto_keywords:
    pairs_with_kw = [r for r in all_pairs_results if any(w['word'] == keyword for w in r['found_words'])]
    if pairs_with_kw:
        print(f"  '{keyword}' gefunden in:")
        for r in pairs_with_kw:
            match = next(w for w in r['found_words'] if w['word'] == keyword)
            print(f"    Col {r['pair'][0]}↔{r['pair'][1]} an Position {match['position']}: '{match['context']}'")
        print()

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("=" * 80)
print("[7] ZUSAMMENFASSUNG: WAS HABEN WIR ÜBERSEHEN?")
print("=" * 80)

# Statistik
total_words = len(all_words_found)
unique_words = len(word_freq)
pairs_with_words = len([r for r in all_pairs_results if r['found_words']])

print(f"""
STATISTIK:
==========
- 64 Spaltenpaare analysiert
- {pairs_with_words} Paare enthalten bekannte Wörter
- {total_words} Wortfunde insgesamt ({unique_words} einzigartige)

WICHTIGSTE ENTDECKUNG:
=====================
Col 30↔97 (AI.MEG.GOU) ist {'NICHT das einzige' if pairs_with_words > 1 else 'das einzige'} Paar mit Wörtern!

ANDERE INTERESSANTE PAARE:
""")

# Top 3 andere Paare (nicht 30↔97)
other_interesting = [r for r in sorted_by_words if r['pair'] != (30, 97) and r['found_words']]
for r in other_interesting[:5]:
    print(f"  Col {r['pair'][0]}↔{r['pair'][1]}: {[w['word'] for w in r['found_words']]}")

print(f"""

KRITISCHE BEWERTUNG:
===================
- Die meisten "Wörter" sind kurz (2-3 Buchstaben) und könnten Zufall sein
- AI.MEG.GOU bleibt die signifikanteste Entdeckung (Kontext + Länge)
- Weitere Monte-Carlo-Tests empfohlen für neue Kandidaten
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'total_pairs': 64,
    'pairs_with_words': pairs_with_words,
    'total_word_finds': total_words,
    'unique_words': unique_words,
    'word_frequency': dict(word_freq.most_common()),
    'word_locations': {k: [list(p) for p in v] for k, v in word_locations.items()},
    'top_by_readable': [
        {'pair': list(r['pair']), 'readable': r['readable_count'], 'words': [w['word'] for w in r['found_words']]}
        for r in sorted_by_readable[:10]
    ],
    'top_by_words': [
        {'pair': list(r['pair']), 'word_count': len(r['found_words']), 'words': [w['word'] for w in r['found_words']]}
        for r in sorted_by_words[:10] if r['found_words']
    ],
    'col_30_97_comparison': {
        'readable': col_30_97['readable_count'],
        'words': [w['word'] for w in col_30_97['found_words']],
        'better_readable_count': len(better_readable),
        'better_words_count': len(better_words)
    }
}

with open('SYSTEMATIC_ALL_PAIRS_SCAN.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: SYSTEMATIC_ALL_PAIRS_SCAN.json")
print("=" * 80)
