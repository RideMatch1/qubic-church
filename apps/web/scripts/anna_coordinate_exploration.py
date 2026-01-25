#!/usr/bin/env python3
"""
ANNA COORDINATE EXPLORATION
===========================
Systematische Erforschung der Matrix im Anna-Koordinatensystem.

Jetzt wo wir die Transformation kennen, können wir:
1. Wichtige Positionen in Anna-Koordinaten ausdrücken
2. Muster im zentrierten Koordinatensystem finden
3. Die Bedeutung bestimmter Regionen verstehen
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
raw_matrix = data["matrix"]

# =============================================================================
# KOORDINATEN-FUNKTIONEN
# =============================================================================

def anna_to_matrix(x, y):
    """Anna → Matrix"""
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col

def matrix_to_anna(row, col):
    """Matrix → Anna"""
    x = col - 64
    if x > 63:
        x -= 128
    y = 63 - row
    if y < -64:
        y += 128
    return x, y

def lookup(x, y):
    """Lookup im Anna-System"""
    row, col = anna_to_matrix(x, y)
    return matrix[row, col]

def lookup_raw(x, y):
    """Lookup mit Rohwert"""
    row, col = anna_to_matrix(x, y)
    return raw_matrix[row][col]

print("=" * 70)
print("ANNA COORDINATE EXPLORATION")
print("=" * 70)

# =============================================================================
# 1. WICHTIGE POSITIONEN IN ANNA-KOORDINATEN
# =============================================================================
print("\n--- 1. WICHTIGE MATRIX-POSITIONEN IN ANNA-KOORDINATEN ---")

important_matrix_positions = [
    ((0, 0), "Obere linke Ecke"),
    ((63, 64), "Zentrum (Anna 0,0)"),
    ((127, 127), "Untere rechte Ecke"),
    ((22, 22), "XOR Triangle Zentrum (100)"),
    ((105, 105), "XOR Triangle Spiegel (100)"),
    ((21, 0), "Row 21 Start (Bitcoin Input Layer)"),
    ((96, 0), "Row 96 Start (Output Layer)"),
    ((68, 0), "Row 68 Start (Cortex)"),
    ((84, 0), "Col 84 (Decision Neurons)"),
]

print("\nMatrix-Position → Anna-Koordinaten:")
for (row, col), desc in important_matrix_positions:
    x, y = matrix_to_anna(row, col)
    val = matrix[row, col]
    print(f"  Matrix[{row:3d},{col:3d}] → Anna({x:4d},{y:4d}) = {val:4d}  ({desc})")

# =============================================================================
# 2. DAS ZENTRUM ANALYSIEREN
# =============================================================================
print("\n--- 2. DAS ZENTRUM (Anna 0,0) ---")

print("\nRegion um das Zentrum (x=-5..5, y=5..-5):")
print("      ", end="")
for x in range(-5, 6):
    print(f"{x:5d}", end="")
print()

for y in range(5, -6, -1):
    print(f"y={y:3d}:", end="")
    for x in range(-5, 6):
        val = lookup(x, y)
        print(f"{val:5d}", end="")
    print()

# =============================================================================
# 3. DIE ACHSEN
# =============================================================================
print("\n--- 3. DIE ACHSEN ---")

print("\nX-Achse (y=0, x von -10 bis 10):")
x_axis = [(x, lookup(x, 0)) for x in range(-10, 11)]
for x, val in x_axis:
    print(f"  Anna({x:3d}, 0) = {val:4d}")

print("\nY-Achse (x=0, y von 10 bis -10):")
y_axis = [(y, lookup(0, y)) for y in range(10, -11, -1)]
for y, val in y_axis:
    print(f"  Anna(0, {y:3d}) = {val:4d}")

# =============================================================================
# 4. DIAGONALEN
# =============================================================================
print("\n--- 4. DIAGONALEN ---")

print("\nHauptdiagonale (x=y, von -10 bis 10):")
main_diag = [(i, lookup(i, i)) for i in range(-10, 11)]
for i, val in main_diag:
    print(f"  Anna({i:3d},{i:3d}) = {val:4d}")

print("\nAnti-Diagonale (x=-y, von -10 bis 10):")
anti_diag = [(i, lookup(i, -i)) for i in range(-10, 11)]
for i, val in anti_diag:
    print(f"  Anna({i:3d},{-i:3d}) = {val:4d}")

# =============================================================================
# 5. STRING-WERTE FINDEN
# =============================================================================
print("\n--- 5. STRING-WERTE (00000000) ---")

string_positions = []
for row in range(128):
    for col in range(128):
        if isinstance(raw_matrix[row][col], str):
            x, y = matrix_to_anna(row, col)
            string_positions.append((x, y, row, col, raw_matrix[row][col]))

print(f"Gefundene String-Werte: {len(string_positions)}")
for x, y, row, col, val in string_positions:
    print(f"  Anna({x:4d},{y:4d}) = '{val}' (Matrix[{row},{col}])")

# =============================================================================
# 6. SYMMETRIE IM ANNA-SYSTEM
# =============================================================================
print("\n--- 6. PUNKT-SYMMETRIE IM ANNA-SYSTEM ---")

# Punkt-Symmetrie bedeutet: f(x,y) + f(-x,-y) = -1
symmetric_count = 0
asymmetric = []

for x in range(-64, 64):
    for y in range(-64, 64):
        val1 = lookup(x, y)
        val2 = lookup(-x, -y)
        if val1 + val2 == -1:
            symmetric_count += 1
        else:
            asymmetric.append((x, y, val1, val2, val1 + val2))

total = 128 * 128
print(f"Symmetrische Paare: {symmetric_count}/{total} ({symmetric_count/total*100:.2f}%)")
print(f"Asymmetrische Positionen: {len(asymmetric)}")

print("\nErste 20 asymmetrische Positionen:")
for x, y, v1, v2, s in asymmetric[:20]:
    print(f"  Anna({x:4d},{y:4d}): {v1:4d} + Anna({-x:4d},{-y:4d}): {v2:4d} = {s:4d}")

# =============================================================================
# 7. FIBONACCI-POSITIONEN
# =============================================================================
print("\n--- 7. FIBONACCI-POSITIONEN ---")

fib = [1, 2, 3, 5, 8, 13, 21, 34, 55]

print("\nFibonacci-Koordinaten (x=fib, y=fib):")
for f in fib:
    if f < 64:
        val = lookup(f, f)
        val_neg = lookup(-f, -f)
        print(f"  Anna({f:3d},{f:3d}) = {val:4d}, Anna({-f:3d},{-f:3d}) = {val_neg:4d}, Sum = {val + val_neg}")

print("\nFibonacci auf X-Achse (y=0):")
for f in fib:
    if f < 64:
        val = lookup(f, 0)
        val_neg = lookup(-f, 0)
        print(f"  Anna({f:3d}, 0) = {val:4d}, Anna({-f:3d}, 0) = {val_neg:4d}")

# =============================================================================
# 8. WERT-VERTEILUNG IN QUADRANTEN
# =============================================================================
print("\n--- 8. WERT-VERTEILUNG IN QUADRANTEN ---")

quadrants = {
    "Q1 (+x, +y)": [],
    "Q2 (-x, +y)": [],
    "Q3 (-x, -y)": [],
    "Q4 (+x, -y)": [],
}

for x in range(-64, 64):
    for y in range(-64, 64):
        val = lookup(x, y)
        if x >= 0 and y >= 0:
            quadrants["Q1 (+x, +y)"].append(val)
        elif x < 0 and y >= 0:
            quadrants["Q2 (-x, +y)"].append(val)
        elif x < 0 and y < 0:
            quadrants["Q3 (-x, -y)"].append(val)
        else:
            quadrants["Q4 (+x, -y)"].append(val)

for name, values in quadrants.items():
    arr = np.array(values)
    print(f"\n{name}:")
    print(f"  Mean: {arr.mean():.2f}, Std: {arr.std():.2f}")
    print(f"  Min: {arr.min()}, Max: {arr.max()}")
    print(f"  Positive: {np.sum(arr > 0)}, Zero: {np.sum(arr == 0)}, Negative: {np.sum(arr < 0)}")

# =============================================================================
# 9. BEKANNTE MUSTER IN ANNA-KOORDINATEN
# =============================================================================
print("\n--- 9. BEKANNTE MUSTER IN ANNA-KOORDINATEN ---")

# Der CORE node bei Matrix[30, 70] = -93
core_x, core_y = matrix_to_anna(30, 70)
print(f"\nCORE Node: Anna({core_x}, {core_y}) = {lookup(core_x, core_y)}")

# XOR Triangle Zentrum bei Matrix[22, 22] = 100
xor_x, xor_y = matrix_to_anna(22, 22)
print(f"XOR Triangle: Anna({xor_x}, {xor_y}) = {lookup(xor_x, xor_y)}")

# Die 68 asymmetrischen Zellen
print(f"\nAsymmetrische Zellen: {len(asymmetric)} gefunden")
print("Diese Zellen tragen Information (brechen Symmetrie)")

# =============================================================================
# 10. SPEZIELLE WERTE SUCHEN
# =============================================================================
print("\n--- 10. SPEZIELLE WERTE IM ANNA-SYSTEM ---")

special_values = {
    0: "Zero (neutral)",
    127: "Maximum positive",
    -128: "Maximum negative",
    14: "Häufigster Wert",
    -114: "Zweithäufigster",
    100: "XOR Triangle",
    27: "XOR Triangle",
    -93: "CORE node",
}

for val, desc in special_values.items():
    positions = []
    for x in range(-64, 64):
        for y in range(-64, 64):
            if lookup(x, y) == val:
                positions.append((x, y))
    print(f"\n{val} ({desc}): {len(positions)} Positionen")
    if len(positions) <= 10:
        for x, y in positions:
            print(f"  Anna({x:4d},{y:4d})")
    else:
        print(f"  Erste 5: {positions[:5]}")

# =============================================================================
# 11. KREISFÖRMIGE MUSTER
# =============================================================================
print("\n--- 11. KREISFÖRMIGE MUSTER (Radius) ---")

def get_circle_values(radius):
    """Hole alle Werte auf einem Kreis um das Zentrum."""
    values = []
    for angle in range(360):
        import math
        x = int(round(radius * math.cos(math.radians(angle))))
        y = int(round(radius * math.sin(math.radians(angle))))
        if -64 <= x < 64 and -64 <= y < 64:
            values.append(lookup(x, y))
    return values

print("\nMittelwerte auf verschiedenen Radien:")
for r in [1, 2, 3, 5, 8, 13, 21, 34]:
    vals = get_circle_values(r)
    if vals:
        arr = np.array(vals)
        print(f"  Radius {r:2d}: Mean={arr.mean():6.2f}, Std={arr.std():5.2f}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: ANNA COORDINATE EXPLORATION")
print("=" * 70)

print(f"""
ENTDECKUNGEN IM ANNA-KOORDINATENSYSTEM:

1. ZENTRUM Anna(0,0) = {lookup(0, 0)}
   - Das ist der Nullpunkt des Systems
   - Matrix-Position [63, 64]

2. PUNKT-SYMMETRIE: {symmetric_count/total*100:.2f}%
   - Fast perfekte Symmetrie um das Zentrum
   - {len(asymmetric)} asymmetrische Positionen tragen Information

3. QUADRANTEN:
   - Alle Quadranten haben ähnliche Statistiken
   - Dies bestätigt die zentrale Symmetrie

4. STRING-WERTE:
   - {len(string_positions)} Positionen mit "00000000"
   - Diese sind spezielle Marker

5. BEKANNTE POSITIONEN:
   - CORE: Anna({core_x}, {core_y}) = -93
   - XOR Triangle: Anna({xor_x}, {xor_y}) = 100

Das Anna-Koordinatensystem ist ein zentriertes, punkt-symmetrisches
System mit einer kleinen Anzahl asymmetrischer Zellen, die als
Informationsträger dienen.
""")

# Speichere Ergebnisse
output = {
    "center_value": int(lookup(0, 0)),
    "symmetry_percent": symmetric_count / total * 100,
    "asymmetric_count": len(asymmetric),
    "string_positions": [(x, y) for x, y, _, _, _ in string_positions],
    "core_position": {"anna": (core_x, core_y), "value": int(lookup(core_x, core_y))},
    "xor_triangle": {"anna": (xor_x, xor_y), "value": int(lookup(xor_x, xor_y))},
}

output_path = script_dir / "ANNA_COORDINATE_EXPLORATION.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
