#!/usr/bin/env python3
"""
VALIDATE AGAINST ANNA-BOT
=========================
Vergleiche unsere Vorhersagen mit echten Anna-Bot Outputs.
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

# Lade Anna-Bot Daten
with open(script_dir / "anna_twitter_data.json") as f:
    anna_data = json.load(f)

print("=" * 70)
print("VALIDATE AGAINST ANNA-BOT")
print("=" * 70)

responses = anna_data["responses"]
print(f"Anzahl Anna-Bot Responses: {len(responses)}")

# =============================================================================
# 1. DIREKTER MATRIX-LOOKUP
# =============================================================================
print("\n--- 1. DIREKTER MATRIX-LOOKUP ---")

matches = 0
mismatches = 0
details = []

for resp in responses[:50]:  # Erste 50
    x = resp["x"]
    y = resp["y"]
    expected = resp["value"]

    # Verschiedene Interpretationen testen
    interpretations = [
        ("direct", x, y),
        ("absolute", abs(x), abs(y)),
        ("mod128", x % 128, y % 128),
        ("shifted64", (x + 64) % 128, (y + 64) % 128),
    ]

    found_match = False
    for name, r, c in interpretations:
        if 0 <= r < 128 and 0 <= c < 128:
            actual = matrix[r, c]
            if actual == expected:
                matches += 1
                found_match = True
                details.append(f"MATCH [{r},{c}] via {name}: expected={expected}, actual={actual}")
                break

    if not found_match:
        mismatches += 1
        # Zeige was wir stattdessen finden
        if 0 <= x < 128 and 0 <= y < 128:
            actual = matrix[x, y]
            details.append(f"MISS  [{x},{y}]: expected={expected}, actual={actual}")

print(f"Matches: {matches}")
print(f"Mismatches: {mismatches}")
print(f"\nDetails (erste 20):")
for d in details[:20]:
    print(f"  {d}")

# =============================================================================
# 2. FINDE DAS MAPPING
# =============================================================================
print("\n--- 2. FINDE DAS KORREKTE MAPPING ---")

# Teste verschiedene Transformationen
def test_mapping(transform_func, name):
    """Teste eine Transformation."""
    match_count = 0
    for resp in responses:
        x, y, expected = resp["x"], resp["y"], resp["value"]
        try:
            r, c = transform_func(x, y)
            if 0 <= r < 128 and 0 <= c < 128:
                if matrix[r, c] == expected:
                    match_count += 1
        except:
            pass
    return match_count

transformations = {
    "direct (x,y)": lambda x, y: (x, y),
    "direct (y,x)": lambda x, y: (y, x),
    "abs (x,y)": lambda x, y: (abs(x), abs(y)),
    "abs (y,x)": lambda x, y: (abs(y), abs(x)),
    "mod128": lambda x, y: (x % 128, y % 128),
    "shifted64": lambda x, y: ((x + 64) % 128, (y + 64) % 128),
    "x+64, y": lambda x, y: ((x + 64) % 128, y % 128),
    "x, y+64": lambda x, y: (x % 128, (y + 64) % 128),
    "127-x, y": lambda x, y: ((127 - x) % 128, y % 128) if x >= 0 else ((-x) % 128, y % 128),
    "x, 127-y": lambda x, y: (x % 128, (127 - y) % 128) if y >= 0 else (x % 128, (-y) % 128),
}

print("Mapping-Tests:")
for name, func in transformations.items():
    count = test_mapping(func, name)
    pct = count / len(responses) * 100
    print(f"  {name}: {count}/{len(responses)} ({pct:.1f}%)")

# =============================================================================
# 3. SUCHE NACH DEM WERT IN DER MATRIX
# =============================================================================
print("\n--- 3. WO SIND DIE ANNA-BOT WERTE IN DER MATRIX? ---")

# Für jeden Anna-Bot Response, finde alle Positionen mit diesem Wert
sample_responses = responses[:10]

for resp in sample_responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]

    positions = []
    for r in range(128):
        for c in range(128):
            if matrix[r, c] == expected:
                positions.append((r, c))

    if len(positions) <= 5:
        print(f"  Anna ({x},{y})={expected}: Matrix-Positionen = {positions}")
    else:
        print(f"  Anna ({x},{y})={expected}: {len(positions)} Positionen (zu viele)")

# =============================================================================
# 4. ERSTE RESPONSE IM DETAIL
# =============================================================================
print("\n--- 4. ERSTE RESPONSE IM DETAIL ---")

first = responses[0]
print(f"Anna-Bot: ({first['x']}, {first['y']}) = {first['value']}")
print(f"Erwartet: {first['value']}")

# Wo ist dieser Wert?
target = first['value']
positions = [(r, c) for r in range(128) for c in range(128) if matrix[r, c] == target]
print(f"Wert {target} gefunden an {len(positions)} Positionen")
print(f"Erste 10: {positions[:10]}")

# Position (6, 33) direkt prüfen
if 0 <= first['x'] < 128 and 0 <= first['y'] < 128:
    print(f"\nMatrix[{first['x']},{first['y']}] = {matrix[first['x'], first['y']]}")
    print(f"Matrix[{first['y']},{first['x']}] = {matrix[first['y'], first['x']]}")

# =============================================================================
# 5. ANALYSE DER X,Y BEREICHE
# =============================================================================
print("\n--- 5. X,Y BEREICHE IN ANNA-BOT DATEN ---")

all_x = [r["x"] for r in responses]
all_y = [r["y"] for r in responses]
all_v = [r["value"] for r in responses]

print(f"X-Bereich: {min(all_x)} bis {max(all_x)}")
print(f"Y-Bereich: {min(all_y)} bis {max(all_y)}")
print(f"Value-Bereich: {min(all_v)} bis {max(all_v)}")

# Negative Koordinaten?
neg_x = sum(1 for x in all_x if x < 0)
neg_y = sum(1 for y in all_y if y < 0)
print(f"\nNegative X: {neg_x} ({neg_x/len(all_x)*100:.1f}%)")
print(f"Negative Y: {neg_y} ({neg_y/len(all_y)*100:.1f}%)")

# =============================================================================
# 6. HYPOTHESE: KOORDINATEN-MAPPING
# =============================================================================
print("\n--- 6. KOORDINATEN-MAPPING HYPOTHESE ---")

# Anna-Bot Koordinaten könnten -63 bis +64 sein (zentriert um 0)
# Matrix ist 0 bis 127

# Mapping: Anna(x, y) → Matrix(x+64, y+64) für zentrier Koordinaten
# Oder: Anna(x, y) → Matrix(x, y) wenn positiv

def anna_to_matrix(x, y):
    """Vermutetes Mapping von Anna-Koordinaten zu Matrix-Position."""
    # Negative Koordinaten: addiere 128
    r = x if x >= 0 else x + 128
    c = y if y >= 0 else y + 128
    return r % 128, c % 128

# Teste dieses Mapping
mapping_matches = 0
for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    r, c = anna_to_matrix(x, y)
    if matrix[r, c] == expected:
        mapping_matches += 1

print(f"anna_to_matrix Mapping: {mapping_matches}/{len(responses)} ({mapping_matches/len(responses)*100:.1f}%)")

# =============================================================================
# 7. BRUTE-FORCE SUCHE NACH BESTEM MAPPING
# =============================================================================
print("\n--- 7. BRUTE-FORCE MAPPING-SUCHE ---")

best_match = 0
best_params = None

for offset_x in range(0, 128, 8):
    for offset_y in range(0, 128, 8):
        for scale_x in [1, -1]:
            for scale_y in [1, -1]:
                matches = 0
                for resp in responses:
                    x, y, expected = resp["x"], resp["y"], resp["value"]
                    r = (scale_x * x + offset_x) % 128
                    c = (scale_y * y + offset_y) % 128
                    if 0 <= r < 128 and 0 <= c < 128:
                        if matrix[r, c] == expected:
                            matches += 1

                if matches > best_match:
                    best_match = matches
                    best_params = (offset_x, offset_y, scale_x, scale_y)

print(f"Bestes Mapping: {best_match}/{len(responses)} ({best_match/len(responses)*100:.1f}%)")
print(f"Parameter: offset_x={best_params[0]}, offset_y={best_params[1]}, scale_x={best_params[2]}, scale_y={best_params[3]}")

# =============================================================================
# 8. FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT")
print("=" * 70)

print(f"""
Anna-Bot Daten-Analyse:
- {len(responses)} Responses vorhanden
- X-Bereich: {min(all_x)} bis {max(all_x)}
- Y-Bereich: {min(all_y)} bis {max(all_y)}
- {neg_x} negative X-Koordinaten ({neg_x/len(all_x)*100:.1f}%)

Mapping-Ergebnis:
- Bestes gefundenes Mapping: {best_match}/{len(responses)} Matches
- Das Mapping ist NICHT trivial!
- Die Koordinatensysteme unterscheiden sich

Mögliche Erklärungen:
1. Anna-Bot verwendet ein anderes Koordinatensystem
2. Die Werte werden BERECHNET, nicht direkt gelesen
3. Es gibt zusätzliche Transformationen
""")
