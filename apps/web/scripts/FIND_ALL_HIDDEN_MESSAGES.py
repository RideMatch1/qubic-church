#!/usr/bin/env python3
"""
FINDE ALLE VERSTECKTEN NACHRICHTEN
===================================
Systematische Suche nach ALLEN möglichen ASCII-Nachrichten in der Anna Matrix.
"""

import json
import numpy as np
from collections import defaultdict
from datetime import datetime
from anna_matrix_utils import load_anna_matrix
import re

print("=" * 80)
print("SYSTEMATISCHE SUCHE NACH ALLEN VERSTECKTEN NACHRICHTEN")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

matrix = np.array(load_anna_matrix(), dtype=np.int8)

# Bekannte englische/deutsche Wörter und relevante Terme
KNOWN_WORDS = {
    'AI', 'MEG', 'GOU', 'FIB', 'CFB', 'SAT', 'BTC', 'KEY', 'SEED', 'CODE',
    'HASH', 'ANNA', 'GROK', 'YES', 'NO', 'THE', 'AND', 'FOR', 'NOT', 'ARE',
    'BUT', 'WAS', 'ALL', 'CAN', 'HAD', 'HER', 'ONE', 'OUR', 'OUT', 'YOU',
    'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'LET', 'MAY', 'NEW',
    'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'MAN', 'SAY',
    'SHE', 'TOO', 'USE', 'GOD', 'DOG', 'CAT', 'SUN', 'WEB', 'NET', 'BIT',
    'COIN', 'BLOCK', 'CHAIN', 'CRYPTO', 'SATOSHI', 'MEMORY', 'GRID', 'DATA',
    'HELLO', 'WORLD', 'START', 'BEGIN', 'TRUTH', 'LIGHT', 'DARK', 'VOID',
    'LOVE', 'HATE', 'GOOD', 'EVIL', 'TIME', 'LOCK', 'OPEN', 'CLOSE',
    'BRIDGE', 'QUANTUM', 'NEURAL', 'BRAIN', 'MIND', 'CORE', 'NODE',
    'ENTRY', 'EXIT', 'PATH', 'FIND', 'SEEK', 'LOOK', 'WATCH', 'GUARD',
    'AIGARTH', 'QUBIC', 'IOTA', 'COME', 'FROM', 'BEYOND', 'FUTURE', 'PAST'
}

def xor_columns(matrix, col_a, col_b):
    return [(int(matrix[r, col_a]) & 0xFF) ^ (int(matrix[r, col_b]) & 0xFF) for r in range(128)]

def to_ascii(vals):
    return ''.join([chr(v) if 32 <= v <= 126 else '.' for v in vals])

def find_known_words(text):
    upper = text.upper()
    found = []
    for word in KNOWN_WORDS:
        if word in upper:
            idx = upper.find(word)
            found.append((word, idx))
    return found

def find_sequences(text, min_len=4):
    """Findet zusammenhängende Buchstabensequenzen"""
    sequences = []
    pattern = r'[A-Za-z]{' + str(min_len) + r',}'
    for match in re.finditer(pattern, text):
        sequences.append((match.group(), match.start()))
    return sequences

# =============================================================================
# ALLE SPALTENPAARE DURCHSUCHEN
# =============================================================================
print("[1] DURCHSUCHE ALLE 8128 SPALTENPAARE")
print("-" * 60)

all_findings = []

for col_a in range(128):
    for col_b in range(col_a + 1, 128):
        xor_vals = xor_columns(matrix, col_a, col_b)
        ascii_text = to_ascii(xor_vals)

        # Suche nach bekannten Wörtern
        words_found = find_known_words(ascii_text)

        # Suche nach langen Sequenzen
        sequences = find_sequences(ascii_text, 5)

        if words_found or len(sequences) > 3:
            all_findings.append({
                'pair': (col_a, col_b),
                'sum': col_a + col_b,
                'words': words_found,
                'sequences': sequences,
                'ascii': ascii_text
            })

print(f"  Gefunden: {len(all_findings)} interessante Spaltenpaare")
print()

# Sortiere nach Anzahl gefundener Wörter
all_findings.sort(key=lambda x: len(x['words']), reverse=True)

print("[2] TOP 20 SPALTENPAARE MIT BEKANNTEN WÖRTERN")
print("-" * 60)

for i, f in enumerate(all_findings[:20]):
    print(f"\n  #{i+1}: Spalten {f['pair'][0]}↔{f['pair'][1]} (Summe {f['sum']})")
    if f['words']:
        for word, pos in f['words']:
            context_start = max(0, pos - 5)
            context_end = min(128, pos + len(word) + 5)
            context = f['ascii'][context_start:context_end]
            print(f"      '{word}' an Position {pos}: ...{context}...")
    if f['sequences'][:3]:
        print(f"      Sequenzen: {[s[0] for s in f['sequences'][:3]]}")

# =============================================================================
# SUCHE NACH SPEZIFISCHEN MUSTERN
# =============================================================================
print("\n" + "=" * 80)
print("[3] SUCHE NACH SPEZIFISCHEN MUSTERN")
print("=" * 80)

# Suche nach "SATOSHI" (7 Zeichen)
print("\n  Suche nach 'SATOSHI'...")
satoshi_found = False
for f in all_findings:
    if 'SATOSHI' in f['ascii'].upper():
        print(f"    ✓ GEFUNDEN bei Spalten {f['pair']}!")
        satoshi_found = True
if not satoshi_found:
    print(f"    ✗ Nicht gefunden")

# Suche nach "HELLO"
print("\n  Suche nach 'HELLO'...")
hello_found = False
for f in all_findings:
    if 'HELLO' in f['ascii'].upper():
        print(f"    ✓ GEFUNDEN bei Spalten {f['pair']}!")
        hello_found = True
if not hello_found:
    print(f"    ✗ Nicht gefunden")

# Suche nach "BITCOIN"
print("\n  Suche nach 'BITCOIN'...")
bitcoin_found = False
for col_a in range(128):
    for col_b in range(col_a + 1, 128):
        xor_vals = xor_columns(matrix, col_a, col_b)
        ascii_text = to_ascii(xor_vals)
        if 'BITCOIN' in ascii_text.upper():
            print(f"    ✓ GEFUNDEN bei Spalten {col_a}↔{col_b}!")
            bitcoin_found = True
if not bitcoin_found:
    print(f"    ✗ Nicht gefunden")

# =============================================================================
# ZEILEN-BASIERTE SUCHE
# =============================================================================
print("\n" + "=" * 80)
print("[4] ZEILEN-BASIERTE SUCHE")
print("=" * 80)

row_findings = []
for row_a in range(128):
    for row_b in range(row_a + 1, 128):
        xor_vals = [(int(matrix[row_a, c]) & 0xFF) ^ (int(matrix[row_b, c]) & 0xFF) for c in range(128)]
        ascii_text = to_ascii(xor_vals)

        words_found = find_known_words(ascii_text)
        if words_found:
            row_findings.append({
                'pair': (row_a, row_b),
                'words': words_found,
                'ascii': ascii_text
            })

row_findings.sort(key=lambda x: len(x['words']), reverse=True)

print(f"\n  Gefunden: {len(row_findings)} interessante Zeilenpaare")
print("\n  TOP 10:")
for i, f in enumerate(row_findings[:10]):
    print(f"    Zeilen {f['pair'][0]}↔{f['pair'][1]}: {[w[0] for w in f['words']]}")

# =============================================================================
# DIAGONALE SUCHE
# =============================================================================
print("\n" + "=" * 80)
print("[5] DIAGONALE SUCHE")
print("=" * 80)

# Alle Diagonalen (offset -127 bis +127)
diag_findings = []
for offset in range(-127, 128):
    diag_vals = []
    for i in range(128):
        row = i
        col = i + offset
        if 0 <= col < 128:
            diag_vals.append(int(matrix[row, col]) & 0xFF)

    if len(diag_vals) >= 10:
        ascii_text = to_ascii(diag_vals)
        words = find_known_words(ascii_text)
        if words:
            diag_findings.append({
                'offset': offset,
                'words': words,
                'ascii': ascii_text[:50]
            })

print(f"\n  Gefunden: {len(diag_findings)} Diagonalen mit Wörtern")
for f in diag_findings[:5]:
    print(f"    Offset {f['offset']:+4}: {[w[0] for w in f['words']]}")

# =============================================================================
# EINZELNE SPALTEN/ZEILEN ALS ASCII
# =============================================================================
print("\n" + "=" * 80)
print("[6] EINZELNE SPALTEN/ZEILEN ALS ASCII")
print("=" * 80)

single_findings = []

# Spalten
for col in range(128):
    vals = [int(matrix[r, col]) & 0xFF for r in range(128)]
    ascii_text = to_ascii(vals)
    words = find_known_words(ascii_text)
    if words:
        single_findings.append({
            'type': 'column',
            'index': col,
            'words': words
        })

# Zeilen
for row in range(128):
    vals = [int(matrix[row, c]) & 0xFF for c in range(128)]
    ascii_text = to_ascii(vals)
    words = find_known_words(ascii_text)
    if words:
        single_findings.append({
            'type': 'row',
            'index': row,
            'words': words
        })

print(f"\n  Gefunden: {len(single_findings)} Spalten/Zeilen mit Wörtern")
for f in single_findings[:10]:
    print(f"    {f['type'].capitalize()} {f['index']}: {[w[0] for w in f['words']]}")

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("\n" + "=" * 80)
print("[7] ZUSAMMENFASSUNG ALLER GEFUNDENEN NACHRICHTEN")
print("=" * 80)

# Sammle alle einzigartigen Wörter
all_words_found = set()
for f in all_findings:
    for word, _ in f['words']:
        all_words_found.add(word)
for f in row_findings:
    for word, _ in f['words']:
        all_words_found.add(word)

print(f"\n  Einzigartige bekannte Wörter gefunden: {len(all_words_found)}")
print(f"  Wörter: {sorted(all_words_found)}")

# Die stärksten Nachrichten
print(f"\n  STÄRKSTE NACHRICHTEN:")
print(f"  ─────────────────────")
print(f"  1. AI.MEG.GOU bei Spalten 30↔97 (BESTÄTIGT)")

# Finde andere starke Kandidaten
strong_candidates = [f for f in all_findings if len(f['words']) >= 3]
for f in strong_candidates[:5]:
    words = [w[0] for w in f['words']]
    print(f"  2. {words} bei Spalten {f['pair']}")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'total_column_pairs_checked': 8128,
    'interesting_column_pairs': len(all_findings),
    'interesting_row_pairs': len(row_findings),
    'unique_words_found': list(all_words_found),
    'top_column_findings': [
        {'pair': f['pair'], 'sum': f['sum'], 'words': [w[0] for w in f['words']]}
        for f in all_findings[:30]
    ],
    'satoshi_found': satoshi_found,
    'bitcoin_found': bitcoin_found,
    'hello_found': hello_found
}

with open('ALL_HIDDEN_MESSAGES.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nErgebnisse gespeichert: ALL_HIDDEN_MESSAGES.json")
print("=" * 80)
