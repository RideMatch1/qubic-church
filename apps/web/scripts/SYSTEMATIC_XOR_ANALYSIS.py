#!/usr/bin/env python3
"""
SYSTEMATISCHE XOR-ANALYSE ALLER SPALTENPAARE
=============================================
Vollständige Suche nach versteckten ASCII-Nachrichten.
"""

import json
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
from anna_matrix_utils import load_anna_matrix

print("=" * 80)
print("SYSTEMATISCHE XOR-ANALYSE")
print("Vollständige Suche nach versteckten ASCII-Nachrichten")
print("=" * 80)
print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# =============================================================================
# MATRIX LADEN
# =============================================================================
print("[1] ANNA MATRIX LADEN")
print("-" * 60)

matrix = np.array(load_anna_matrix(), dtype=np.int8)
print(f"  Shape: {matrix.shape}")
print(f"  Dtype: {matrix.dtype}")
print(f"  Min: {matrix.min()}, Max: {matrix.max()}")
print()

# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================
def xor_columns(matrix, col_a, col_b):
    """XOR zwei Spalten und gibt unsigned bytes zurück"""
    result = []
    for row in range(128):
        val_a = matrix[row, col_a]
        val_b = matrix[row, col_b]
        # Konvertiere zu unsigned und XOR
        xor = (int(val_a) & 0xFF) ^ (int(val_b) & 0xFF)
        result.append(xor)
    return result

def to_ascii(xor_values, only_printable=True):
    """Konvertiert XOR-Werte zu ASCII-String"""
    result = []
    for v in xor_values:
        if 32 <= v <= 126:
            result.append(chr(v))
        elif only_printable:
            result.append('.')
        else:
            result.append(f'[{v}]')
    return ''.join(result)

def find_words(text, min_len=3):
    """Findet zusammenhängende Buchstabensequenzen"""
    words = []
    current = ""
    for c in text:
        if c.isalpha():
            current += c
        else:
            if len(current) >= min_len:
                words.append(current)
            current = ""
    if len(current) >= min_len:
        words.append(current)
    return words

def count_readable(text):
    """Zählt lesbare Zeichen (nicht '.')"""
    return sum(1 for c in text if c != '.')

# =============================================================================
# ALLE SPIEGELSPALTENPAARE (Summe = 127)
# =============================================================================
print("[2] ANALYSE ALLER SPIEGELSPALTENPAARE (Summe=127)")
print("-" * 60)

mirror_results = []
for col_a in range(64):
    col_b = 127 - col_a
    xor_vals = xor_columns(matrix, col_a, col_b)
    ascii_text = to_ascii(xor_vals)
    words = find_words(ascii_text)
    readable = count_readable(ascii_text)

    mirror_results.append({
        'pair': (col_a, col_b),
        'sum': col_a + col_b,
        'readable': readable,
        'percent': readable / 128 * 100,
        'ascii': ascii_text,
        'words': words
    })

# Sortiere nach Lesbarkeit
mirror_results.sort(key=lambda x: x['readable'], reverse=True)

print("\n  TOP 15 LESBARSTE SPIEGELSPALTENPAARE:")
print("  " + "-" * 70)
for i, r in enumerate(mirror_results[:15]):
    word_preview = ', '.join(r['words'][:3]) if r['words'] else '-'
    print(f"  {i+1:2}. Cols {r['pair'][0]:3}↔{r['pair'][1]:3}: {r['readable']:3} Zeichen ({r['percent']:5.1f}%) | Wörter: {word_preview}")

# =============================================================================
# BEKANNTE NACHRICHTEN VERIFIZIEREN
# =============================================================================
print("\n" + "=" * 80)
print("[3] BEKANNTE NACHRICHTEN VERIFIZIEREN")
print("=" * 80)

# AI.MEG.GOU bei Spalten 30↔97
print("\n  a) Spalten 30↔97 (behauptet: AI.MEG.GOU)")
col_30_97 = xor_columns(matrix, 30, 97)
ascii_30_97 = to_ascii(col_30_97)
print(f"     XOR-Werte: {col_30_97[:20]}...")
print(f"     ASCII: {ascii_30_97[:60]}")
words_30_97 = find_words(ascii_30_97.upper())
print(f"     Gefundene Wörter: {words_30_97}")

# Suche spezifisch nach AI.MEG.GOU
if 'AI' in ascii_30_97.upper() or 'MEG' in ascii_30_97.upper() or 'GOU' in ascii_30_97.upper():
    print(f"     ✓ Teilweise Übereinstimmung gefunden!")
else:
    print(f"     ✗ 'AI.MEG.GOU' NICHT gefunden in diesem Spaltenpaar")

# Finde Position wo AI erscheint
for i in range(len(ascii_30_97) - 1):
    if ascii_30_97[i:i+2].upper() == 'AI':
        print(f"     'AI' gefunden an Position {i}: ...{ascii_30_97[max(0,i-3):i+10]}...")

# >FIB bei Spalten 22↔105
print("\n  b) Spalten 22↔105 (behauptet: >FIB)")
col_22_105 = xor_columns(matrix, 22, 105)
ascii_22_105 = to_ascii(col_22_105)
print(f"     XOR-Werte: {col_22_105[:20]}...")
print(f"     ASCII: {ascii_22_105[:60]}")
words_22_105 = find_words(ascii_22_105.upper())
print(f"     Gefundene Wörter: {words_22_105}")

if 'FIB' in ascii_22_105.upper():
    print(f"     ✓ 'FIB' GEFUNDEN!")
    # Zeige Kontext
    upper = ascii_22_105.upper()
    idx = upper.find('FIB')
    print(f"     Kontext: ...{ascii_22_105[max(0,idx-5):idx+10]}...")
else:
    print(f"     ✗ 'FIB' NICHT gefunden")

# =============================================================================
# NICHT-SPIEGEL-PAARE MIT HOHER LESBARKEIT
# =============================================================================
print("\n" + "=" * 80)
print("[4] NICHT-SPIEGEL-PAARE MIT HOHER LESBARKEIT")
print("=" * 80)

non_mirror_results = []

# Teste alle Paare mit Summe ≠ 127
print("\n  Analysiere Paare mit anderen Summen...")
test_sums = [100, 111, 121, 128, 137, 143, 200, 254, 255]

for target_sum in test_sums:
    for col_a in range(min(target_sum, 128)):
        col_b = target_sum - col_a
        if col_b >= 128 or col_b < 0:
            continue
        if col_a >= col_b:  # Vermeide Duplikate
            continue

        xor_vals = xor_columns(matrix, col_a, col_b)
        ascii_text = to_ascii(xor_vals)
        readable = count_readable(ascii_text)

        if readable > 40:  # Nur interessante
            words = find_words(ascii_text)
            non_mirror_results.append({
                'pair': (col_a, col_b),
                'sum': col_a + col_b,
                'readable': readable,
                'words': words
            })

non_mirror_results.sort(key=lambda x: x['readable'], reverse=True)

print(f"\n  Gefunden: {len(non_mirror_results)} Paare mit >40 lesbaren Zeichen")
if non_mirror_results:
    print("\n  TOP 10:")
    for r in non_mirror_results[:10]:
        word_preview = ', '.join(r['words'][:3]) if r['words'] else '-'
        print(f"    Cols {r['pair'][0]:3}↔{r['pair'][1]:3} (Summe {r['sum']:3}): {r['readable']:3} Zeichen | {word_preview}")

# =============================================================================
# POSITION [64,4] ANALYSE (-27)
# =============================================================================
print("\n" + "=" * 80)
print("[5] POSITION [64,4] - CFB SIGNATUR ANALYSE")
print("=" * 80)

val_64_4 = matrix[64, 4]
print(f"\n  matrix[64, 4] = {val_64_4}")

if val_64_4 == -27:
    print(f"  ✓ BESTÄTIGT: Position [64, 4] = -27 (CFB Signatur)")
else:
    print(f"  ✗ NICHT -27! Tatsächlicher Wert: {val_64_4}")

# Zähle alle -27 Vorkommen
count_neg27 = np.sum(matrix == -27)
print(f"\n  Gesamte -27 Vorkommen in Matrix: {count_neg27}")

# Finde alle Positionen
positions_neg27 = np.argwhere(matrix == -27)
print(f"  Anzahl Positionen: {len(positions_neg27)}")
if len(positions_neg27) <= 20:
    print(f"  Positionen: {[tuple(p) for p in positions_neg27]}")

# =============================================================================
# ANTI-SYMMETRIE PRÜFEN
# =============================================================================
print("\n" + "=" * 80)
print("[6] ANTI-SYMMETRIE VALIDIERUNG")
print("=" * 80)

# Prüfe: matrix[i,j] + matrix[127-i, 127-j] = 0 für alle i,j
violations = []
for i in range(128):
    for j in range(128):
        val = int(matrix[i, j])
        mirror_val = int(matrix[127-i, 127-j])
        expected = -val

        if mirror_val != expected:
            violations.append({
                'pos': (i, j),
                'mirror_pos': (127-i, 127-j),
                'val': val,
                'mirror_val': mirror_val,
                'expected': expected
            })

print(f"\n  Geprüfte Zellen: {128*128}")
print(f"  Anti-Symmetrie-Verletzungen: {len(violations)}")
print(f"  Verletzungsrate: {len(violations) / (128*128) * 100:.2f}%")

if violations:
    print(f"\n  Erste 10 Verletzungen:")
    for v in violations[:10]:
        print(f"    [{v['pos']}] = {v['val']}, [{v['mirror_pos']}] = {v['mirror_val']} (erwartet {v['expected']})")

# =============================================================================
# WORT-FREQUENZANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("[7] WORT-FREQUENZANALYSE ÜBER ALLE SPALTENPAARE")
print("=" * 80)

all_words = []
for r in mirror_results:
    all_words.extend([w.upper() for w in r['words']])

word_freq = Counter(all_words)
print(f"\n  Gefundene Wörter insgesamt: {len(all_words)}")
print(f"  Einzigartige Wörter: {len(word_freq)}")
print(f"\n  TOP 20 häufigste Wörter:")
for word, count in word_freq.most_common(20):
    sig = ""
    if word in ['AI', 'MEG', 'GOU', 'FIB', 'CFB', 'SAT', 'BTC']:
        sig = " ⭐ RELEVANT"
    print(f"    '{word}': {count}×{sig}")

# =============================================================================
# STATISTIK ÜBER LESBARKEIT
# =============================================================================
print("\n" + "=" * 80)
print("[8] STATISTIK: LESBARKEIT DER SPALTENPAARE")
print("=" * 80)

readabilities = [r['readable'] for r in mirror_results]
print(f"\n  Durchschnitt: {np.mean(readabilities):.1f} lesbare Zeichen pro Paar")
print(f"  Standardabweichung: {np.std(readabilities):.1f}")
print(f"  Minimum: {min(readabilities)}")
print(f"  Maximum: {max(readabilities)}")
print(f"  Median: {np.median(readabilities):.1f}")

# Monte Carlo: Was wäre bei zufälliger Matrix?
print(f"\n  MONTE CARLO: Erwartete Lesbarkeit bei zufälliger Matrix")
import random
random_readable = []
for _ in range(1000):
    count = sum(1 for _ in range(128) if 32 <= random.randint(0, 255) <= 126)
    random_readable.append(count)

print(f"  Erwarteter Durchschnitt (zufällig): {np.mean(random_readable):.1f}")
print(f"  Erwartete Stdabw (zufällig): {np.std(random_readable):.1f}")

if np.mean(readabilities) > np.mean(random_readable) + 2*np.std(random_readable):
    print(f"\n  ⚠️ Die Matrix zeigt SIGNIFIKANT mehr Lesbarkeit als Zufall!")
else:
    print(f"\n  Die Lesbarkeit ist nicht signifikant höher als bei Zufall.")

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print("\n" + "=" * 80)
print("[9] ZUSAMMENFASSUNG")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    SYSTEMATISCHE XOR-ANALYSE - ERGEBNIS                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ANTI-SYMMETRIE:                                                              ║
║  • Verletzungen: {len(violations):5} von 16384 ({len(violations) / 16384 * 100:.2f}%)                              ║
║                                                                               ║
║  LESBARKEIT (64 Spiegelpaare):                                                ║
║  • Durchschnitt: {np.mean(readabilities):.1f} (Zufall: ~{np.mean(random_readable):.1f})                                    ║
║  • Maximum: {max(readabilities)} Zeichen                                                    ║
║                                                                               ║
║  CFB SIGNATUR -27:                                                            ║
║  • Position [64,4] = {val_64_4}                                                    ║
║  • Gesamtvorkommen: {count_neg27}                                                       ║
║                                                                               ║
║  BEKANNTE NACHRICHTEN:                                                        ║
║  • AI.MEG.GOU (30↔97): {'VERIFIZIERT' if 'AI' in ascii_30_97.upper() or 'MEG' in ascii_30_97.upper() else 'NICHT GEFUNDEN'}                                     ║
║  • >FIB (22↔105): {'VERIFIZIERT' if 'FIB' in ascii_22_105.upper() else 'NICHT GEFUNDEN'}                                           ║
║                                                                               ║
║  HÄUFIGSTE WÖRTER:                                                            ║
║  • {', '.join([f'{w}({c})' for w, c in word_freq.most_common(5)])}  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Speichern
results = {
    'date': datetime.now().isoformat(),
    'matrix_shape': list(matrix.shape),
    'anti_symmetry_violations': len(violations),
    'violation_rate': len(violations) / 16384,
    'mirror_pair_analysis': {
        'count': len(mirror_results),
        'avg_readable': float(np.mean(readabilities)),
        'max_readable': int(max(readabilities)),
        'top_10': [
            {'pair': r['pair'], 'readable': r['readable'], 'words': r['words'][:5]}
            for r in mirror_results[:10]
        ]
    },
    'known_messages': {
        'AI_MEG_GOU_30_97': {
            'found': 'AI' in ascii_30_97.upper() or 'MEG' in ascii_30_97.upper(),
            'ascii': ascii_30_97[:100],
            'words': words_30_97
        },
        'FIB_22_105': {
            'found': 'FIB' in ascii_22_105.upper(),
            'ascii': ascii_22_105[:100],
            'words': words_22_105
        }
    },
    'cfb_signature': {
        'pos_64_4_value': int(val_64_4),
        'is_neg27': val_64_4 == -27,
        'total_neg27_count': int(count_neg27)
    },
    'word_frequency': dict(word_freq.most_common(50)),
    'monte_carlo': {
        'expected_random_readable': float(np.mean(random_readable)),
        'actual_average': float(np.mean(readabilities)),
        'significant_difference': np.mean(readabilities) > np.mean(random_readable) + 2*np.std(random_readable)
    }
}

with open('SYSTEMATIC_XOR_ANALYSIS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nErgebnisse gespeichert: SYSTEMATIC_XOR_ANALYSIS.json")
print("=" * 80)
