#!/usr/bin/env python3
"""
===============================================================================
   SUCHE NACH WIRKLICH SIGNIFIKANTEN MUSTERN
===============================================================================
Die Patoshi-Verbindung war ein Fehlalarm (p=0.79).
Jetzt suchen wir nach Mustern die WIRKLICH statistisch signifikant sind!

BEKANNTE CLAIMS ZU VALIDIEREN:
1. 99.58% Punkt-Symmetrie
2. "AI.MEG.GOU" in XOR-Spalten
3. "key" in Column 127
4. Bridge-Zellen (Wert 127)
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
import random
from collections import Counter

random.seed(42)
np.random.seed(42)

script_dir = Path(__file__).parent

print("=" * 80)
print("   SUCHE NACH STATISTISCH SIGNIFIKANTEN MUSTERN")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# TEST 1: PUNKT-SYMMETRIE VALIDIERUNG
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 1: PUNKT-SYMMETRIE VALIDIERUNG")
print("=" * 80)

# Check point symmetry: matrix[i,j] == -matrix[127-i, 127-j]
symmetric_count = 0
total_count = 0
asymmetric_cells = []

for i in range(128):
    for j in range(128):
        val = matrix[i, j]
        sym_val = matrix[127-i, 127-j]

        total_count += 1
        if val == -sym_val:
            symmetric_count += 1
        else:
            asymmetric_cells.append((i, j, val, sym_val))

symmetry_rate = symmetric_count / total_count
print(f"\n   Symmetrische Zellen: {symmetric_count}/{total_count}")
print(f"   Symmetrie-Rate: {symmetry_rate*100:.2f}%")
print(f"   Asymmetrische Zellen: {len(asymmetric_cells)}")

# Monte Carlo: How likely is this by chance?
print("\n   Monte-Carlo Test (1000 Durchläufe):")
random_symmetry_rates = []
for _ in range(1000):
    # Random 128x128 matrix with same value distribution
    values = matrix.flatten()
    np.random.shuffle(values)
    random_matrix = values.reshape(128, 128)

    sym_count = 0
    for i in range(128):
        for j in range(128):
            if random_matrix[i,j] == -random_matrix[127-i, 127-j]:
                sym_count += 1
    random_symmetry_rates.append(sym_count / total_count)

avg_random = np.mean(random_symmetry_rates)
std_random = np.std(random_symmetry_rates)
max_random = max(random_symmetry_rates)

print(f"   Zufällige Symmetrie: {avg_random*100:.2f}% ± {std_random*100:.2f}%")
print(f"   Maximum bei Zufall: {max_random*100:.2f}%")
print(f"   Tatsächlich: {symmetry_rate*100:.2f}%")

# Z-score
z_score = (symmetry_rate - avg_random) / std_random
print(f"   Z-Score: {z_score:.2f}")

if symmetry_rate > max_random:
    print(f"   ✅ HOCHSIGNIFIKANT! Höher als alle 1000 Zufallsmatrizen!")
    p_symmetry = 0.001  # p < 0.001
else:
    p_symmetry = sum(1 for r in random_symmetry_rates if r >= symmetry_rate) / len(random_symmetry_rates)
    print(f"   p-Wert: {p_symmetry}")

# ==============================================================================
# TEST 2: "KEY" IN COLUMN 127
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 2: 'KEY' IN COLUMN 127")
print("=" * 80)

# Check for "key" = 0x6b 0x65 0x79 = 107, 101, 121
col127 = [matrix[r, 127] for r in range(128)]

# Find "key" pattern
key_found = False
key_position = None
for r in range(126):
    v1, v2, v3 = col127[r], col127[r+1], col127[r+2]
    # Check if values spell "key" (considering sign)
    if (abs(v1) == 107 or v1 == 107) and (abs(v2) == 101 or v2 == -101) and (abs(v3) == 121 or v3 == -121):
        key_found = True
        key_position = r
        print(f"\n   Gefunden bei Rows {r}-{r+2}: [{v1}, {v2}, {v3}]")
        print(f"   Hex: {abs(v1):02x} {abs(v2):02x} {abs(v3):02x}")
        # Verify ASCII
        text = chr(abs(v1)) + chr(abs(v2)) + chr(abs(v3))
        print(f"   ASCII: '{text}'")

if not key_found:
    print("   ❌ 'key' nicht gefunden!")

# Monte Carlo: Probability of finding "key" in random column
print("\n   Monte-Carlo: Wahrscheinlichkeit 'key' in zufälliger Spalte")
key_in_random = 0
for _ in range(10000):
    random_col = [random.choice(range(-128, 128)) for _ in range(128)]
    for r in range(126):
        v1, v2, v3 = abs(random_col[r]), abs(random_col[r+1]), abs(random_col[r+2])
        if v1 == 107 and v2 == 101 and v3 == 121:
            key_in_random += 1
            break

p_key = key_in_random / 10000
print(f"   Zufällig 'key' finden: {p_key*100:.3f}%")
print(f"   p-Wert: {p_key:.6f}")

if p_key < 0.001:
    print(f"   ✅ HOCHSIGNIFIKANT!")

# ==============================================================================
# TEST 3: WERT 127 (BRIDGE CELLS)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 3: WERT 127 (BRIDGE CELLS)")
print("=" * 80)

# Count occurrences of 127
value_127_positions = []
for i in range(128):
    for j in range(128):
        if matrix[i, j] == 127:
            value_127_positions.append((i, j))

print(f"\n   Anzahl Zellen mit Wert 127: {len(value_127_positions)}")
print(f"   Positionen: {value_127_positions}")

# Value distribution
all_values = matrix.flatten()
value_counts = Counter(all_values)
count_127 = value_counts.get(127, 0)
total_cells = 128 * 128

print(f"\n   127 kommt {count_127}x vor von {total_cells} Zellen")
print(f"   Rate: {count_127/total_cells*100:.4f}%")

# Is 127 special compared to other values?
print("\n   Vergleich mit ähnlichen Werten:")
for v in [125, 126, 127, -127, -126, -125]:
    cnt = value_counts.get(v, 0)
    print(f"   Wert {v:4d}: {cnt:3d}x")

# ==============================================================================
# TEST 4: AI.MEG.GOU VALIDIERUNG
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 4: AI.MEG.GOU IN XOR-SPALTEN")
print("=" * 80)

# Check Col30 XOR Col97
col30 = matrix[:, 30]
col97 = matrix[:, 97]
xor_30_97 = col30 ^ col97

# Convert to characters
def to_char(v):
    v = abs(v) % 128
    if 32 <= v < 127:
        return chr(v)
    return '.'

xor_text = ''.join(to_char(v) for v in xor_30_97)
print(f"\n   Col30 XOR Col97:")
print(f"   {xor_text[:64]}")
print(f"   {xor_text[64:]}")

# Search for words
import re
words_found = re.findall(r'[A-Za-z]{3,}', xor_text)
print(f"\n   Gefundene Wörter (3+ Buchstaben): {words_found}")

# Check if AI.MEG.GOU is there
if 'AI' in xor_text and 'MEG' in xor_text:
    print(f"   ✅ AI und MEG gefunden!")

    # Monte Carlo
    print("\n   Monte-Carlo: Wahrscheinlichkeit 'AI' UND 'MEG' zufällig")
    ai_meg_random = 0
    for _ in range(10000):
        rand_col1 = np.random.randint(-128, 128, 128)
        rand_col2 = np.random.randint(-128, 128, 128)
        rand_xor = rand_col1 ^ rand_col2
        rand_text = ''.join(to_char(v) for v in rand_xor)
        if 'AI' in rand_text and 'MEG' in rand_text:
            ai_meg_random += 1

    p_aimeg = ai_meg_random / 10000
    print(f"   Zufällig: {p_aimeg*100:.2f}%")
    print(f"   p-Wert: {p_aimeg:.6f}")
else:
    print(f"   ❌ AI.MEG.GOU nicht eindeutig gefunden")

# ==============================================================================
# ZUSAMMENFASSUNG
# ==============================================================================
print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG: WIRKLICH SIGNIFIKANTE MUSTER")
print("=" * 80)

print(f"""
   ╔══════════════════════════════════════════════════════════════════════════╗
   ║  VALIDIERTE MUSTER                                                       ║
   ╠══════════════════════════════════════════════════════════════════════════╣
   ║                                                                          ║
   ║  1. PUNKT-SYMMETRIE: {symmetry_rate*100:.2f}%                                           ║
   ║     Z-Score: {z_score:.1f} → {"✅ HOCHSIGNIFIKANT" if z_score > 5 else "⚠️ Prüfen":<30}             ║
   ║                                                                          ║
   ║  2. "KEY" IN COL 127: {"✅ GEFUNDEN" if key_found else "❌ NICHT GEFUNDEN":<20}                          ║
   ║     p-Wert: {p_key:.6f}                                                   ║
   ║                                                                          ║
   ║  3. WERT 127: {count_127} Vorkommen                                            ║
   ║     (Keine klare statistische Signifikanz)                               ║
   ║                                                                          ║
   ║  4. PATOSHI-VERBINDUNG: ❌ NICHT SIGNIFIKANT (p=0.79)                    ║
   ║                                                                          ║
   ╚══════════════════════════════════════════════════════════════════════════╝
""")

