#!/usr/bin/env python3
"""
PHASE C: SPIRAL-DEKODIERUNG
===========================
Lese die Matrix in Spiral-Mustern und suche nach versteckten Nachrichten.
"""

import json
import numpy as np
from datetime import datetime
from anna_matrix_utils import load_anna_matrix

print("=" * 80)
print("PHASE C: SPIRAL-DEKODIERUNG")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Matrix laden
matrix = np.array(load_anna_matrix(), dtype=np.int8)

# Bekannte Wörter
KNOWN_WORDS = [
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'yes', 'no',
    'sat', 'ai', 'meg', 'gou', 'cfb', 'fib', 'btc', 'key', 'god', 'truth',
    'satya', 'satoshi', 'bitcoin', 'qubic', 'iota', 'anna', 'code', 'hash',
    'void', 'time', 'lock', 'bridge', 'memory', 'entry', 'exit', 'core'
]

def spiral_clockwise_inward(n):
    """Generiert Positionen für Uhrzeigersinn-Spirale von außen nach innen."""
    positions = []
    top, bottom, left, right = 0, n - 1, 0, n - 1

    while top <= bottom and left <= right:
        # Oben: links nach rechts
        for col in range(left, right + 1):
            positions.append((top, col))
        top += 1

        # Rechts: oben nach unten
        for row in range(top, bottom + 1):
            positions.append((row, right))
        right -= 1

        # Unten: rechts nach links
        if top <= bottom:
            for col in range(right, left - 1, -1):
                positions.append((bottom, col))
            bottom -= 1

        # Links: unten nach oben
        if left <= right:
            for row in range(bottom, top - 1, -1):
                positions.append((row, left))
            left += 1

    return positions

def spiral_counterclockwise_inward(n):
    """Generiert Positionen für Gegenuhrzeigersinn-Spirale von außen nach innen."""
    positions = []
    top, bottom, left, right = 0, n - 1, 0, n - 1

    while top <= bottom and left <= right:
        # Oben: rechts nach links
        for col in range(right, left - 1, -1):
            positions.append((top, col))
        top += 1

        # Links: oben nach unten
        for row in range(top, bottom + 1):
            positions.append((row, left))
        left += 1

        # Unten: links nach rechts
        if top <= bottom:
            for col in range(left, right + 1):
                positions.append((bottom, col))
            bottom -= 1

        # Rechts: unten nach oben
        if left <= right:
            for row in range(bottom, top - 1, -1):
                positions.append((row, right))
            right -= 1

    return positions

def extract_values(matrix, positions):
    """Extrahiert Werte an den gegebenen Positionen."""
    return [int(matrix[r, c]) for r, c in positions]

def to_ascii(values):
    """Konvertiert zu ASCII mit unsigned bytes."""
    return ''.join([chr(v & 0xFF) if 32 <= (v & 0xFF) <= 126 else '.' for v in values])

def find_words(text, word_list):
    """Findet bekannte Wörter im Text."""
    upper = text.upper()
    found = []
    for word in word_list:
        if word.upper() in upper:
            pos = upper.find(word.upper())
            found.append({
                'word': word,
                'position': pos,
                'context': text[max(0, pos-5):pos+len(word)+5]
            })
    return found

# =============================================================================
# SPIRALE 1: UHRZEIGERSINN VON AUSSEN NACH INNEN
# =============================================================================
print("[1] SPIRALE UHRZEIGERSINN (AUSSEN → INNEN)")
print("-" * 60)

positions_cw = spiral_clockwise_inward(128)
values_cw = extract_values(matrix, positions_cw)
ascii_cw = to_ascii(values_cw)

readable_cw = sum(1 for c in ascii_cw if c != '.')
print(f"Positionen: {len(positions_cw)}")
print(f"Lesbare Zeichen: {readable_cw}/{len(ascii_cw)} ({readable_cw/len(ascii_cw)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_cw[:100]}")

words_cw = find_words(ascii_cw, KNOWN_WORDS)
if words_cw:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_cw]}")
    for w in words_cw[:10]:
        print(f"  '{w['word']}' an Position {w['position']}: {w['context']}")
print()

# =============================================================================
# SPIRALE 2: GEGENUHRZEIGERSINN VON AUSSEN NACH INNEN
# =============================================================================
print("[2] SPIRALE GEGENUHRZEIGERSINN (AUSSEN → INNEN)")
print("-" * 60)

positions_ccw = spiral_counterclockwise_inward(128)
values_ccw = extract_values(matrix, positions_ccw)
ascii_ccw = to_ascii(values_ccw)

readable_ccw = sum(1 for c in ascii_ccw if c != '.')
print(f"Positionen: {len(positions_ccw)}")
print(f"Lesbare Zeichen: {readable_ccw}/{len(ascii_ccw)} ({readable_ccw/len(ascii_ccw)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_ccw[:100]}")

words_ccw = find_words(ascii_ccw, KNOWN_WORDS)
if words_ccw:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_ccw]}")
    for w in words_ccw[:10]:
        print(f"  '{w['word']}' an Position {w['position']}: {w['context']}")
print()

# =============================================================================
# SPIRALE 3: UHRZEIGERSINN VON INNEN NACH AUSSEN
# =============================================================================
print("[3] SPIRALE UHRZEIGERSINN (INNEN → AUSSEN)")
print("-" * 60)

positions_cw_out = list(reversed(positions_cw))
values_cw_out = extract_values(matrix, positions_cw_out)
ascii_cw_out = to_ascii(values_cw_out)

readable_cw_out = sum(1 for c in ascii_cw_out if c != '.')
print(f"Lesbare Zeichen: {readable_cw_out}/{len(ascii_cw_out)} ({readable_cw_out/len(ascii_cw_out)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_cw_out[:100]}")

words_cw_out = find_words(ascii_cw_out, KNOWN_WORDS)
if words_cw_out:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_cw_out]}")
print()

# =============================================================================
# SPIRALE 4: GEGENUHRZEIGERSINN VON INNEN NACH AUSSEN
# =============================================================================
print("[4] SPIRALE GEGENUHRZEIGERSINN (INNEN → AUSSEN)")
print("-" * 60)

positions_ccw_out = list(reversed(positions_ccw))
values_ccw_out = extract_values(matrix, positions_ccw_out)
ascii_ccw_out = to_ascii(values_ccw_out)

readable_ccw_out = sum(1 for c in ascii_ccw_out if c != '.')
print(f"Lesbare Zeichen: {readable_ccw_out}/{len(ascii_ccw_out)} ({readable_ccw_out/len(ascii_ccw_out)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_ccw_out[:100]}")

words_ccw_out = find_words(ascii_ccw_out, KNOWN_WORDS)
if words_ccw_out:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_ccw_out]}")
print()

# =============================================================================
# SPIRAL-XOR: Uhrzeigersinn XOR Gegenuhrzeigersinn
# =============================================================================
print("[5] SPIRAL-XOR (CW XOR CCW)")
print("-" * 60)

xor_spiral = [(values_cw[i] & 0xFF) ^ (values_ccw[i] & 0xFF) for i in range(len(values_cw))]
ascii_xor = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_spiral])

readable_xor = sum(1 for c in ascii_xor if c != '.')
print(f"Lesbare Zeichen: {readable_xor}/{len(ascii_xor)} ({readable_xor/len(ascii_xor)*100:.1f}%)")
print(f"Erste 100 Zeichen: {ascii_xor[:100]}")

words_xor = find_words(ascii_xor, KNOWN_WORDS)
if words_xor:
    print(f"GEFUNDENE WÖRTER: {[w['word'] for w in words_xor]}")
print()

# =============================================================================
# BESTE ERGEBNISSE
# =============================================================================
print("=" * 80)
print("[6] ZUSAMMENFASSUNG")
print("=" * 80)

all_results = [
    ('CW Inward', readable_cw, words_cw),
    ('CCW Inward', readable_ccw, words_ccw),
    ('CW Outward', readable_cw_out, words_cw_out),
    ('CCW Outward', readable_ccw_out, words_ccw_out),
    ('CW XOR CCW', readable_xor, words_xor)
]

print("\nÜBERSICHT:")
print(f"{'Spirale':<15} {'Lesbar':<10} {'Wörter'}")
print("-" * 50)
for name, readable, words in all_results:
    word_list = [w['word'] for w in words] if words else []
    print(f"{name:<15} {readable:<10} {word_list}")

# Beste Methode
best = max(all_results, key=lambda x: len(x[2]))
print(f"\nBESTE METHODE: {best[0]} mit {len(best[2])} Wörtern")

# Alle einzigartigen Wörter
all_words = set()
for _, _, words in all_results:
    for w in words:
        all_words.add(w['word'])
print(f"\nALLE GEFUNDENEN WÖRTER: {sorted(all_words)}")

print(f"""

KRITISCHE BEWERTUNG:
====================
- Spiral-Dekodierung {'zeigt Ergebnisse' if all_words else 'zeigt keine neuen Ergebnisse'}
- Gefundene Wörter: {len(all_words)}
- Signifikanz: {'MITTEL' if len(all_words) > 5 else 'NIEDRIG'} - kurze Wörter erwartbar bei 16384 Zeichen
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'methods': {
        'clockwise_inward': {
            'readable': readable_cw,
            'words': [w['word'] for w in words_cw],
            'sample': ascii_cw[:200]
        },
        'counterclockwise_inward': {
            'readable': readable_ccw,
            'words': [w['word'] for w in words_ccw],
            'sample': ascii_ccw[:200]
        },
        'clockwise_outward': {
            'readable': readable_cw_out,
            'words': [w['word'] for w in words_cw_out],
            'sample': ascii_cw_out[:200]
        },
        'counterclockwise_outward': {
            'readable': readable_ccw_out,
            'words': [w['word'] for w in words_ccw_out],
            'sample': ascii_ccw_out[:200]
        },
        'xor_cw_ccw': {
            'readable': readable_xor,
            'words': [w['word'] for w in words_xor],
            'sample': ascii_xor[:200]
        }
    },
    'all_unique_words': sorted(all_words),
    'best_method': best[0]
}

with open('SPIRAL_DECODE.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nErgebnisse gespeichert: SPIRAL_DECODE.json")
print("=" * 80)
