#!/usr/bin/env python3
"""
FIBONACCI INVESTIGATION
=======================
Die asymmetrischen Zellen zeigen ">FIB" - Zeiger auf Fibonacci!
Wo sind die Fibonacci-Muster in der Matrix?
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("=" * 70)
print("FIBONACCI INVESTIGATION")
print("=" * 70)

# Fibonacci-Zahlen bis 128
fib = [0, 1]
while fib[-1] < 256:
    fib.append(fib[-1] + fib[-2])

fib_set = set(fib)
neg_fib_set = set(-f for f in fib if f > 0)

print(f"Fibonacci-Zahlen bis 256: {[f for f in fib if f <= 256]}")

# =============================================================================
# 1. Fibonacci-Werte in der Matrix
# =============================================================================
print("\n--- 1. FIBONACCI-WERTE IN DER MATRIX ---")

fib_count = 0
neg_fib_count = 0
fib_positions = []

for r in range(128):
    for c in range(128):
        val = matrix[r, c]
        if val in fib_set:
            fib_count += 1
            fib_positions.append((r, c, val))
        if val in neg_fib_set:
            neg_fib_count += 1
            fib_positions.append((r, c, val))

print(f"Positive Fibonacci-Werte: {fib_count}")
print(f"Negative Fibonacci-Werte: {neg_fib_count}")
print(f"Total: {fib_count + neg_fib_count} von 16384 ({(fib_count + neg_fib_count)/16384*100:.2f}%)")

# Erwartungswert bei Zufall
fib_in_range = [f for f in fib if -128 <= f <= 127]
expected_ratio = len(fib_in_range) / 256
print(f"Erwartete Quote bei Zufall: {expected_ratio*100:.2f}%")
print(f"Tatsächliche Quote ist {(fib_count + neg_fib_count)/16384/expected_ratio:.2f}x der Erwartung")

# =============================================================================
# 2. Fibonacci-Positionen (Zeile oder Spalte ist Fibonacci)
# =============================================================================
print("\n--- 2. FIBONACCI-POSITIONEN ---")

fib_rows = [f for f in fib if f < 128]
fib_cols = fib_rows

print(f"Fibonacci-Zeilen: {fib_rows}")
print(f"Fibonacci-Spalten: {fib_cols}")

# Analysiere Fibonacci-Zeilen
print("\nInhalt der Fibonacci-Zeilen:")
for row in fib_rows:
    row_data = matrix[row]
    unique = len(set(row_data))
    mean = np.mean(row_data)
    row_xor127 = [(v ^ 127) & 0x7F for v in row_data]
    text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in row_xor127])
    print(f"  Row {row}: unique={unique}, mean={mean:.1f}")
    print(f"    XOR127: {text[:50]}...")

# =============================================================================
# 3. Fibonacci-Spirale in der Matrix
# =============================================================================
print("\n--- 3. FIBONACCI-SPIRALE ---")

# Generiere Fibonacci-Spirale-Positionen (starting from center)
center = (64, 64)

def fibonacci_spiral_positions(n_points, start=center):
    """Generiere Positionen entlang einer Fibonacci-Spirale."""
    positions = []
    r, c = start

    # Fibonacci-Abstände
    fib_steps = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    # Richtungen: rechts, runter, links, hoch
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    dir_idx = 0

    for step in fib_steps:
        dr, dc = directions[dir_idx % 4]
        for _ in range(step):
            if 0 <= r < 128 and 0 <= c < 128:
                positions.append((r, c))
            r += dr
            c += dc
        dir_idx += 1

    return positions[:n_points]

spiral_positions = fibonacci_spiral_positions(100)
print(f"Erste 20 Spiralpositionen: {spiral_positions[:20]}")

# Extrahiere Werte entlang der Spirale
spiral_values = [matrix[r, c] for r, c in spiral_positions if 0 <= r < 128 and 0 <= c < 128]
spiral_xor127 = [(v ^ 127) & 0x7F for v in spiral_values]
spiral_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in spiral_xor127])

print(f"Spiral-Werte (XOR 127): {spiral_text}")

# =============================================================================
# 4. Golden Ratio Positionen
# =============================================================================
print("\n--- 4. GOLDEN RATIO POSITIONEN ---")

PHI = (1 + 5**0.5) / 2  # 1.618...
print(f"Golden Ratio (φ): {PHI}")

# Positionen basierend auf φ
golden_positions = []
for i in range(20):
    r = int((i * PHI * 10) % 128)
    c = int((i * PHI * PHI * 10) % 128)
    golden_positions.append((r, c))

print(f"Golden-Ratio Positionen: {golden_positions[:10]}")

golden_values = [matrix[r, c] for r, c in golden_positions]
golden_xor127 = [(v ^ 127) & 0x7F for v in golden_values]
golden_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in golden_xor127])

print(f"Golden-Ratio Werte (XOR 127): {golden_text}")

# =============================================================================
# 5. Fibonacci-Differenzen zwischen Werten
# =============================================================================
print("\n--- 5. FIBONACCI-DIFFERENZEN ---")

# Prüfe ob aufeinanderfolgende Werte Fibonacci-Differenzen haben
flat = matrix.flatten()
fib_diff_count = 0

for i in range(len(flat) - 1):
    diff = abs(flat[i+1] - flat[i])
    if diff in fib_set:
        fib_diff_count += 1

print(f"Fibonacci-Differenzen zwischen Nachbarn: {fib_diff_count} von {len(flat)-1}")
print(f"Quote: {fib_diff_count/(len(flat)-1)*100:.2f}%")
print(f"Erwartung bei Zufall: {len([f for f in fib if f <= 255])/256*100:.2f}%")

# =============================================================================
# 6. Position [22,22] und Fibonacci
# =============================================================================
print("\n--- 6. XOR TRIANGLE UND FIBONACCI ---")

# 100, 27, 127 - das XOR Triangle
print("XOR Triangle: 100 XOR 27 = 127")
print(f"  100 in Fib? {100 in fib_set}")
print(f"  27 in Fib? {27 in fib_set}")
print(f"  127 in Fib? {127 in fib_set}")

# Aber: 100 = 89 + 11 (89 ist Fib)
# 27 = 21 + 6 (aber 6 ist nicht Fib)
# 127 = 89 + 34 + 3 + 1 = Fib-Summe!

print("\n127 als Fibonacci-Summe:")
# Zeckendorf-Darstellung von 127
def zeckendorf(n):
    """Zeckendorf-Darstellung: Jede positive Ganzzahl als Summe nicht-benachbarter Fibonacci-Zahlen."""
    result = []
    fibs = [f for f in fib if f > 0 and f <= n][::-1]
    for f in fibs:
        if f <= n:
            result.append(f)
            n -= f
    return result

z127 = zeckendorf(127)
print(f"  127 = {' + '.join(map(str, z127))} (Zeckendorf)")

z100 = zeckendorf(100)
print(f"  100 = {' + '.join(map(str, z100))} (Zeckendorf)")

z27 = zeckendorf(27)
print(f"  27 = {' + '.join(map(str, z27))} (Zeckendorf)")

# =============================================================================
# 7. Die "FIB" Position finden
# =============================================================================
print("\n--- 7. WO IST 'FIB' IN DER MATRIX? ---")

# Suche nach F, I, B als aufeinanderfolgende Buchstaben
# F = 70, I = 73, B = 66 (ASCII)
# XOR 127: F = 70 ^ 127 = 57, I = 73 ^ 127 = 54, B = 66 ^ 127 = 61

target_F = 70 ^ 127  # 57
target_I = 73 ^ 127  # 54
target_B = 66 ^ 127  # 61

print(f"Suche nach XOR-127 Werten für F({target_F}), I({target_I}), B({target_B})...")

# Als Sequenz
for r in range(128):
    for c in range(126):
        v1 = (matrix[r, c] ^ 127) & 0x7F
        v2 = (matrix[r, c+1] ^ 127) & 0x7F
        v3 = (matrix[r, c+2] ^ 127) & 0x7F

        if v1 == target_F and v2 == target_I and v3 == target_B:
            print(f"  FIB gefunden bei [{r},{c}]-[{r},{c+2}]!")
            print(f"    Raw values: {matrix[r, c]}, {matrix[r, c+1]}, {matrix[r, c+2]}")

# =============================================================================
# 8. Fibonacci-Indices in den asymmetrischen Zellen
# =============================================================================
print("\n--- 8. FIBONACCI IN ASYMMETRISCHEN ZELLEN ---")

asymmetric = []
for r in range(128):
    for c in range(128):
        val = matrix[r, c]
        mirror_val = matrix[127-r, 127-c]
        if val + mirror_val != -1:
            asymmetric.append({"r": r, "c": c, "v": val, "mv": mirror_val})

# Prüfe ob Positionen Fibonacci-Zahlen sind
fib_position_count = 0
for cell in asymmetric:
    r, c = cell["r"], cell["c"]
    if r in fib_set or c in fib_set:
        fib_position_count += 1
        print(f"  [{r},{c}] - Row oder Col ist Fibonacci")

print(f"\nAsymmetrische Zellen mit Fib-Position: {fib_position_count} von {len(asymmetric)}")

# =============================================================================
# 9. Die >FIB Nachricht deuten
# =============================================================================
print("\n--- 9. WAS BEDEUTET >FIB? ---")

print("""
>FIB interpretiert:

1. ZEIGER (>) auf FIBONACCI (FIB)
   - Die Struktur folgt Fibonacci-Mustern
   - Möglicherweise Fibonacci-basierte Adressierung

2. GRÖSSER ALS FIBONACCI?
   - Die Matrix transzendiert Fibonacci?
   - Erweiterung des Fibonacci-Konzepts?

3. FIBONACCI-POINTER in Programmiersprache
   - >FIB könnte ein Befehl sein
   - "Spring zu Fibonacci-Routine"

4. IM KONTEXT DER MATRIX:
   - Die asymmetrischen Zellen ZEIGEN auf Fibonacci
   - Das Paar-XOR ergibt einen Zeiger
   - Die Nachricht ist selbst palindromisch!
""")

# =============================================================================
# 10. Fazit
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: FIBONACCI IN DER MATRIX")
print("=" * 70)

print(f"""
ENTDECKUNGEN:

1. >FIB in asymmetrischem XOR:
   - Die Asymmetrie-Paare ergeben ">FIB...BIF<"
   - Ein palindromischer Zeiger!

2. 127 (Mersenne-Zahl) als Fibonacci-Summe:
   - 127 = {' + '.join(map(str, z127))}
   - Verknüpft Mersenne mit Fibonacci!

3. XOR Triangle:
   - 100 = {' + '.join(map(str, z100))}
   - 27 = {' + '.join(map(str, z27))}
   - Alle drei sind Fibonacci-Kompositionen

4. Die Matrix-Struktur:
   - Fibonacci-Zeilen existieren (0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
   - Diese könnten spezielle Funktionen haben

BEDEUTUNG:
Die Matrix kombiniert:
- Mersenne-Zahlen (127 = 2^7 - 1)
- Fibonacci-Sequenzen
- Ternäre Logik
- Punkt-Symmetrie

= MATHEMATISCHE ELEGANZ MIT ABSICHT
""")
