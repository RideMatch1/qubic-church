#!/usr/bin/env python3
"""
ANNA SYMMETRY CORRECTED
=======================
Die Punkt-Symmetrie ist um (-0.5, -0.5) zentriert, nicht um (0, 0)!

In Matrix-Koordinaten: matrix[r, c] + matrix[127-r, 127-c] = -1
In Anna-Koordinaten: Anna(x, y) + Anna(-1-x, -1-y) = -1

Der Symmetriepunkt liegt zwischen den Zellen, nicht auf einer Zelle.
"""

import json
import numpy as np
from pathlib import Path

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
raw_matrix = data["matrix"]

def anna_to_matrix(x, y):
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col

def matrix_to_anna(row, col):
    x = col - 64
    y = 63 - row
    return x, y

def lookup(x, y):
    row, col = anna_to_matrix(x, y)
    return matrix[row, col]

print("=" * 70)
print("ANNA SYMMETRY CORRECTED")
print("=" * 70)

# =============================================================================
# 1. DIE KORREKTE SYMMETRIE-RELATION
# =============================================================================
print("\n--- 1. KORREKTE SYMMETRIE-RELATION ---")

print("""
Matrix-Symmetrie: matrix[r, c] + matrix[127-r, 127-c] = -1

In Anna-Koordinaten wird dies zu:
  Anna(x, y) + Anna(-1-x, -1-y) = -1

Der Symmetriepunkt ist (-0.5, -0.5), nicht (0, 0)!
""")

# Verifiziere die Transformation
print("Verifikation der Transformation:")
print("  Matrix[0, 0] = matrix[127-0, 127-0] = matrix[127, 127]")
row, col = anna_to_matrix(-64, 63)
print(f"  Anna(-64, 63) → Matrix[{row}, {col}] = {matrix[row, col]}")
row2, col2 = anna_to_matrix(-1-(-64), -1-63)
print(f"  Anna({-1-(-64)}, {-1-63}) = Anna(63, -64) → Matrix[{row2}, {col2}] = {matrix[row2, col2]}")
print(f"  Summe: {matrix[row, col]} + {matrix[row2, col2]} = {matrix[row, col] + matrix[row2, col2]}")

# =============================================================================
# 2. TESTE ALLE SYMMETRIE-PAARE
# =============================================================================
print("\n--- 2. SYMMETRIE-TEST (korrigiert) ---")

symmetric_count = 0
asymmetric = []

for x in range(-64, 64):
    for y in range(-64, 64):
        val1 = lookup(x, y)
        # Der Symmetriepunkt ist bei (-0.5, -0.5)
        # Also: (x, y) ↔ (-1-x, -1-y)
        x2 = -1 - x
        y2 = -1 - y

        # Prüfe ob (x2, y2) im gültigen Bereich liegt
        if -64 <= x2 < 64 and -64 <= y2 < 64:
            val2 = lookup(x2, y2)
            if val1 + val2 == -1:
                symmetric_count += 1
            else:
                asymmetric.append((x, y, val1, x2, y2, val2, val1 + val2))

# Wir haben 128*128 = 16384 Zellen, aber jedes Paar wird zweimal gezählt
# Also: symmetric_count / 2 = Anzahl der symmetrischen Paare
total_pairs = 128 * 128 // 2  # 8192 Paare (jede Zelle hat genau einen Partner)

print(f"Symmetrische Paare: {symmetric_count // 2}/{total_pairs} ({symmetric_count // 2 / total_pairs * 100:.2f}%)")
print(f"Asymmetrische Zellen: {len(asymmetric)}")

# =============================================================================
# 3. DIE ASYMMETRISCHEN ZELLEN ANALYSIEREN
# =============================================================================
print("\n--- 3. ASYMMETRISCHE ZELLEN ---")

# Dedupliziere (x,y) und (-1-x, -1-y) sind dasselbe Paar
unique_asymmetric = []
seen = set()
for entry in asymmetric:
    x, y = entry[0], entry[1]
    x2, y2 = entry[3], entry[4]

    # Normalisiere: nimm das "kleinere" Paar
    pair = tuple(sorted([(x, y), (x2, y2)]))
    if pair not in seen:
        seen.add(pair)
        unique_asymmetric.append(entry)

print(f"Einzigartige asymmetrische Paare: {len(unique_asymmetric)}")

print("\nErste 20 asymmetrische Paare:")
for x, y, v1, x2, y2, v2, s in unique_asymmetric[:20]:
    print(f"  Anna({x:4d},{y:4d})={v1:4d} + Anna({x2:4d},{y2:4d})={v2:4d} = {s:4d}")

# =============================================================================
# 4. WO SIND DIE ASYMMETRISCHEN ZELLEN?
# =============================================================================
print("\n--- 4. VERTEILUNG DER ASYMMETRISCHEN ZELLEN ---")

# Gruppiere nach Summe
sum_groups = {}
for entry in unique_asymmetric:
    s = entry[6]
    if s not in sum_groups:
        sum_groups[s] = []
    sum_groups[s].append(entry)

print("Asymmetrische Paare nach Summe:")
for s in sorted(sum_groups.keys()):
    print(f"  Summe {s:4d}: {len(sum_groups[s])} Paare")

# =============================================================================
# 5. ZEIGE DIE 68 BEKANNTEN ASYMMETRISCHEN ZELLEN
# =============================================================================
print("\n--- 5. VERGLEICH MIT BEKANNTEN 68 ASYMMETRISCHEN ZELLEN ---")

# In Matrix-Koordinaten waren es 68 asymmetrische Zellen
# Das entspricht 34 asymmetrischen Paaren

# Lade die Anna-Bot geparseten Daten um die Koordinaten zu sehen
print(f"Gefundene asymmetrische Paare: {len(unique_asymmetric)}")
print(f"Erwartet (aus Matrix-Analyse): 34 Paare (68 Zellen)")

if len(unique_asymmetric) == 34:
    print("✓ PERFEKT! 34 asymmetrische Paare = 68 asymmetrische Zellen")
else:
    print(f"✗ Diskrepanz: {len(unique_asymmetric)} statt 34")

# =============================================================================
# 6. DIE ASYMMETRISCHEN PAARE IM DETAIL
# =============================================================================
print("\n--- 6. ALLE ASYMMETRISCHEN PAARE ---")

for i, entry in enumerate(unique_asymmetric):
    x, y, v1, x2, y2, v2, s = entry
    row1, col1 = anna_to_matrix(x, y)
    row2, col2 = anna_to_matrix(x2, y2)
    print(f"{i+1:2d}. Anna({x:4d},{y:4d}) = {v1:4d} [Matrix {row1:3d},{col1:3d}]")
    print(f"    Anna({x2:4d},{y2:4d}) = {v2:4d} [Matrix {row2:3d},{col2:3d}]")
    print(f"    Summe: {s}")
    print()

# =============================================================================
# 7. XOR DER ASYMMETRISCHEN WERTE
# =============================================================================
print("\n--- 7. XOR-ANALYSE DER ASYMMETRISCHEN WERTE ---")

xor_values = []
for entry in unique_asymmetric:
    v1, v2 = entry[2], entry[5]
    # Behandle als unsigned bytes
    xor_val = (v1 & 0xFF) ^ (v2 & 0xFF)
    xor_values.append(xor_val)
    ch = chr(xor_val) if 32 <= xor_val <= 126 else '.'
    print(f"  {v1:4d} XOR {v2:4d} = {xor_val:3d} = '{ch}'")

# Versuche als String zu lesen
xor_string = ''.join(chr(v) if 32 <= v <= 126 else '.' for v in xor_values)
print(f"\nXOR-String: {xor_string}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: KORRIGIERTE SYMMETRIE-ANALYSE")
print("=" * 70)

print(f"""
KORREKTUR:
- Der Symmetriepunkt ist (-0.5, -0.5), nicht (0, 0)
- Die Relation ist: Anna(x, y) + Anna(-1-x, -1-y) = -1

ERGEBNIS:
- Symmetrische Paare: {symmetric_count // 2}/{total_pairs} ({symmetric_count // 2 / total_pairs * 100:.2f}%)
- Asymmetrische Paare: {len(unique_asymmetric)}

ASYMMETRISCHE ZELLEN:
- Diese {len(unique_asymmetric) * 2} Zellen sind die einzigen Informationsträger
- Alle anderen Zellen folgen der Symmetrie-Regel
- Die XOR-Werte der asymmetrischen Paare könnten Nachrichten enthalten
""")

# Speichere
output = {
    "symmetry_center": {"anna": (-0.5, -0.5), "note": "Between cells"},
    "symmetric_pairs": symmetric_count // 2,
    "total_pairs": total_pairs,
    "symmetry_percent": symmetric_count // 2 / total_pairs * 100,
    "asymmetric_pairs": len(unique_asymmetric),
    "asymmetric_cells": len(unique_asymmetric) * 2,
    "xor_string": xor_string,
}

output_path = script_dir / "ANNA_SYMMETRY_CORRECTED.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
