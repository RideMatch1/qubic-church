#!/usr/bin/env python3
"""
PHASE D: PRIMZAHL-POSITIONEN DEKODIERUNG
=========================================
Extrahiere Werte an allen Primzahl-Positionen.
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix

print("=" * 80)
print("PHASE D: PRIMZAHL-POSITIONEN DEKODIERUNG")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

# Primzahlen bis 127 generieren
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

PRIMES = [p for p in range(128) if is_prime(p)]
print(f"Primzahlen 0-127: {PRIMES}")
print(f"Anzahl: {len(PRIMES)}")
print()

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
            found.append({'word': word, 'position': pos, 'context': text[max(0,pos-5):pos+len(word)+5]})
    return found

# =============================================================================
# METHODE 1: Row[prime] - Erste Spalte jeder Primzahl-Zeile
# =============================================================================
print("[1] ROW[PRIME] - ERSTE SPALTE")
print("-" * 60)

row_prime_col0 = [int(matrix[p, 0]) for p in PRIMES]
ascii_rp0 = to_ascii(row_prime_col0)
print(f"Werte: {row_prime_col0}")
print(f"ASCII: {ascii_rp0}")
words_rp0 = find_words(ascii_rp0, KNOWN_WORDS)
if words_rp0:
    print(f"WÖRTER: {[w['word'] for w in words_rp0]}")
print()

# =============================================================================
# METHODE 2: Col[prime] - Erste Zeile jeder Primzahl-Spalte
# =============================================================================
print("[2] COL[PRIME] - ERSTE ZEILE")
print("-" * 60)

col_prime_row0 = [int(matrix[0, p]) for p in PRIMES]
ascii_cp0 = to_ascii(col_prime_row0)
print(f"Werte: {col_prime_row0}")
print(f"ASCII: {ascii_cp0}")
words_cp0 = find_words(ascii_cp0, KNOWN_WORDS)
if words_cp0:
    print(f"WÖRTER: {[w['word'] for w in words_cp0]}")
print()

# =============================================================================
# METHODE 3: Diagonal[prime] - matrix[prime, prime]
# =============================================================================
print("[3] DIAGONAL[PRIME] - matrix[p, p]")
print("-" * 60)

diag_prime = [int(matrix[p, p]) for p in PRIMES]
ascii_dp = to_ascii(diag_prime)
print(f"Werte: {diag_prime}")
print(f"ASCII: {ascii_dp}")
words_dp = find_words(ascii_dp, KNOWN_WORDS)
if words_dp:
    print(f"WÖRTER: {[w['word'] for w in words_dp]}")
print()

# =============================================================================
# METHODE 4: Anti-Diagonal[prime] - matrix[prime, 127-prime]
# =============================================================================
print("[4] ANTI-DIAGONAL[PRIME] - matrix[p, 127-p]")
print("-" * 60)

anti_diag_prime = [int(matrix[p, 127-p]) for p in PRIMES if p <= 127]
ascii_adp = to_ascii(anti_diag_prime)
print(f"Werte: {anti_diag_prime}")
print(f"ASCII: {ascii_adp}")
words_adp = find_words(ascii_adp, KNOWN_WORDS)
if words_adp:
    print(f"WÖRTER: {[w['word'] for w in words_adp]}")
print()

# =============================================================================
# METHODE 5: Vollständige Zeilen an Primzahl-Positionen
# =============================================================================
print("[5] VOLLSTÄNDIGE PRIME-ZEILEN (erste 10 Primes)")
print("-" * 60)

for p in PRIMES[:10]:
    row_vals = [int(matrix[p, c]) for c in range(128)]
    ascii_row = to_ascii(row_vals)
    readable = sum(1 for c in ascii_row if c != '.')
    words = find_words(ascii_row, KNOWN_WORDS)
    print(f"  Row {p:3}: {readable:3} lesbar | Wörter: {[w['word'] for w in words] if words else '-'}")
    if words:
        print(f"           {ascii_row[:50]}...")

print()

# =============================================================================
# METHODE 6: XOR von Primzahl-Zeilen-Paaren
# =============================================================================
print("[6] XOR VON PRIME-ZEILEN-PAAREN")
print("-" * 60)

# Paare von aufeinanderfolgenden Primzahlen
prime_pairs = [(PRIMES[i], PRIMES[i+1]) for i in range(len(PRIMES)-1)]
best_xor_pairs = []

for p1, p2 in prime_pairs[:15]:
    xor_vals = [(int(matrix[p1, c]) & 0xFF) ^ (int(matrix[p2, c]) & 0xFF) for c in range(128)]
    ascii_xor = to_ascii([v if v >= 0 else v + 256 for v in xor_vals])
    readable = sum(1 for c in ascii_xor if c != '.')
    words = find_words(ascii_xor, KNOWN_WORDS)

    if words:
        print(f"  Row {p1} XOR Row {p2}: {readable} lesbar | Wörter: {[w['word'] for w in words]}")
        best_xor_pairs.append({'pair': (p1, p2), 'words': [w['word'] for w in words], 'readable': readable})

print()

# =============================================================================
# METHODE 7: Summe aller Werte an Primzahl-Positionen
# =============================================================================
print("[7] MATHEMATISCHE ANALYSE")
print("-" * 60)

all_prime_values = []
for p in PRIMES:
    all_prime_values.extend([int(matrix[p, c]) for c in range(128)])

total_sum = sum(all_prime_values)
xor_all = 0
for v in all_prime_values:
    xor_all ^= (v & 0xFF)

print(f"Summe aller Werte an Prime-Zeilen: {total_sum}")
print(f"  mod 127 = {total_sum % 127}")
print(f"  mod 137 = {total_sum % 137}")
print(f"  mod 11 = {total_sum % 11}")
print()
print(f"XOR aller Werte: {xor_all}")
if 32 <= xor_all <= 126:
    print(f"  = ASCII '{chr(xor_all)}'")
print()

# =============================================================================
# METHODE 8: Spezielle Primzahl-Kombinationen
# =============================================================================
print("[8] SPEZIELLE PRIMZAHL-KOMBINATIONEN")
print("-" * 60)

# CFB-Primzahlen: 11, 13, 19, 31, 37, 41, 43, 47, 127
cfb_primes = [11, 13, 19, 31, 37, 41, 43, 47, 127]
print(f"CFB-Primzahlen: {cfb_primes}")

cfb_values = [int(matrix[p, p]) for p in cfb_primes if p < 128]
print(f"Diagonal-Werte: {cfb_values}")
print(f"  Summe: {sum(cfb_values)}")

# Als ASCII
cfb_ascii = to_ascii(cfb_values)
print(f"  ASCII: {cfb_ascii}")
print()

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("=" * 80)
print("[9] ZUSAMMENFASSUNG")
print("=" * 80)

all_words = set()
for w in words_rp0 + words_cp0 + words_dp + words_adp:
    all_words.add(w['word'])
for pair in best_xor_pairs:
    for w in pair['words']:
        all_words.add(w)

print(f"""
ERGEBNISSE:
===========

1. Primzahlen 0-127: {len(PRIMES)} Stück
2. Diagonal[prime] = matrix[p,p]: {'Wörter gefunden' if words_dp else 'keine Wörter'}
3. Prime-Zeilen-XOR: {len(best_xor_pairs)} Paare mit Wörtern

ALLE GEFUNDENEN WÖRTER: {sorted(all_words) if all_words else 'keine'}

KRITISCHE BEWERTUNG:
- Primzahl-Positionen {'zeigen Muster' if all_words else 'zeigen keine neuen Nachrichten'}
- Signifikanz: {'MITTEL' if len(all_words) > 3 else 'NIEDRIG'}
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'primes': PRIMES,
    'methods': {
        'row_prime_col0': {'values': row_prime_col0, 'ascii': ascii_rp0, 'words': [w['word'] for w in words_rp0]},
        'col_prime_row0': {'values': col_prime_row0, 'ascii': ascii_cp0, 'words': [w['word'] for w in words_cp0]},
        'diagonal_prime': {'values': diag_prime, 'ascii': ascii_dp, 'words': [w['word'] for w in words_dp]},
        'anti_diagonal_prime': {'values': anti_diag_prime, 'ascii': ascii_adp, 'words': [w['word'] for w in words_adp]}
    },
    'prime_xor_pairs': best_xor_pairs,
    'math_analysis': {
        'sum': total_sum,
        'sum_mod_127': total_sum % 127,
        'sum_mod_137': total_sum % 137,
        'xor_all': xor_all,
        'xor_ascii': chr(xor_all) if 32 <= xor_all <= 126 else None
    },
    'all_unique_words': sorted(all_words)
}

with open('PRIME_POSITION_DECODE.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: PRIME_POSITION_DECODE.json")
print("=" * 80)
