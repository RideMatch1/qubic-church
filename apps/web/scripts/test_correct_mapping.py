#!/usr/bin/env python3
"""
TEST CORRECT MAPPING
====================
Teste das korrekte Anna-zu-Matrix Koordinaten-Mapping.

Die verifizierte Transformation:
  col = (x + 64) % 128
  row = (63 - y) % 128
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

# Lade Anna-Bot Daten
with open(script_dir / "ANNA_BOT_PARSED_DATA.json") as f:
    anna_data = json.load(f)

responses = [r for r in anna_data["responses"] if isinstance(r["value"], int)]

print("=" * 70)
print("TEST CORRECT MAPPING")
print("=" * 70)

# =============================================================================
# 1. DIE VERIFIZIERTE TRANSFORMATION
# =============================================================================
print("\n--- 1. VERIFIZIERTE TRANSFORMATION ---")

def anna_to_matrix(x, y):
    """
    Konvertiere Anna-Koordinaten zu Matrix-Indices.

    Verifizierte Formel:
      col = (x + 64) % 128
      row = (63 - y) % 128
    """
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col

# Teste mit bekanntem Beispiel: Anna(6, 33) → Matrix[30, 70] = -93
test_x, test_y = 6, 33
row, col = anna_to_matrix(test_x, test_y)
print(f"Anna({test_x}, {test_y}) → Matrix[{row}, {col}] = {matrix[row, col]}")
print(f"Erwartet: Matrix[30, 70] = -93")

# =============================================================================
# 2. TESTE ALLE ANNA-BOT RESPONSES
# =============================================================================
print("\n--- 2. TESTE ALLE RESPONSES ---")

matches = 0
mismatches = 0
details = []

for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]

    row, col = anna_to_matrix(x, y)

    if 0 <= row < 128 and 0 <= col < 128:
        actual = matrix[row, col]

        if actual == expected:
            matches += 1
            details.append(f"MATCH: Anna({x:4d},{y:4d}) → Matrix[{row:3d},{col:3d}] = {actual}")
        else:
            mismatches += 1
            details.append(f"MISS:  Anna({x:4d},{y:4d}) → Matrix[{row:3d},{col:3d}] = {actual}, expected {expected}")
    else:
        mismatches += 1
        details.append(f"OUT:   Anna({x:4d},{y:4d}) → [{row},{col}] out of bounds")

print(f"Matches: {matches}/{len(responses)} ({matches/len(responses)*100:.1f}%)")
print(f"Mismatches: {mismatches}")

print("\nErste 20 Details:")
for d in details[:20]:
    print(f"  {d}")

# =============================================================================
# 3. ANALYSE DER MISMATCHES
# =============================================================================
print("\n--- 3. ANALYSE DER MISMATCHES ---")

# Sammle Differenzen
diffs = []
for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    row, col = anna_to_matrix(x, y)

    if 0 <= row < 128 and 0 <= col < 128:
        actual = matrix[row, col]
        diffs.append(expected - actual)

diff_counts = Counter(diffs)
print("Häufigste Differenzen (expected - actual):")
for diff, count in diff_counts.most_common(10):
    print(f"  Diff={diff:5d}: {count}x")

# =============================================================================
# 4. ALTERNATIVE TRANSFORMATIONEN TESTEN
# =============================================================================
print("\n--- 4. ALTERNATIVE TRANSFORMATIONEN ---")

def test_transform(transform_func, name):
    match_count = 0
    for resp in responses:
        x, y, expected = resp["x"], resp["y"], resp["value"]
        try:
            row, col = transform_func(x, y)
            if 0 <= row < 128 and 0 <= col < 128:
                if matrix[row, col] == expected:
                    match_count += 1
        except:
            pass
    return match_count

transforms = {
    "verified: row=(63-y)%128, col=(x+64)%128":
        lambda x, y: ((63 - y) % 128, (x + 64) % 128),

    "swap: row=(63-x)%128, col=(y+64)%128":
        lambda x, y: ((63 - x) % 128, (y + 64) % 128),

    "both_add: row=(y+64)%128, col=(x+64)%128":
        lambda x, y: ((y + 64) % 128, (x + 64) % 128),

    "both_sub: row=(63-y)%128, col=(63-x)%128":
        lambda x, y: ((63 - y) % 128, (63 - x) % 128),

    "neg_x: row=(63-y)%128, col=(-x+64)%128":
        lambda x, y: ((63 - y) % 128, (-x + 64) % 128),

    "neg_y: row=(-y+63)%128, col=(x+64)%128":
        lambda x, y: ((-y + 63) % 128, (x + 64) % 128),

    "offset_32: row=(31-y)%128, col=(x+32)%128":
        lambda x, y: ((31 - y) % 128, (x + 32) % 128),

    "direct: row=y%128, col=x%128":
        lambda x, y: (y % 128, x % 128),

    "abs: row=|y|, col=|x|":
        lambda x, y: (abs(y) % 128, abs(x) % 128),
}

print("Teste verschiedene Transformationen:")
results = []
for name, func in transforms.items():
    count = test_transform(func, name)
    pct = count / len(responses) * 100
    results.append((name, count, pct))

results.sort(key=lambda x: -x[1])
for name, count, pct in results:
    marker = " ← BEST" if count == max(r[1] for r in results) else ""
    print(f"  {name}: {count}/{len(responses)} ({pct:.1f}%){marker}")

# =============================================================================
# 5. VIELLEICHT IST DAS KOORDINATENSYSTEM ANDERS
# =============================================================================
print("\n--- 5. KOORDINATENSYSTEM-ANALYSE ---")

# Die Anna-Bot Daten haben X von -13 bis 61 und Y von -33 bis 61
# Das sind NICHT -64 bis 63 wie in der Dokumentation

# Vielleicht werden nur bestimmte Positionen abgefragt?
all_x = sorted(set(r["x"] for r in responses))
all_y = sorted(set(r["y"] for r in responses))

print(f"X-Bereich in Daten: {min(all_x)} bis {max(all_x)} ({len(all_x)} unique)")
print(f"Y-Bereich in Daten: {min(all_y)} bis {max(all_y)} ({len(all_y)} unique)")

# Welche Zeilen/Spalten werden abgefragt?
queried_rows = set()
queried_cols = set()
for resp in responses:
    row, col = anna_to_matrix(resp["x"], resp["y"])
    if 0 <= row < 128:
        queried_rows.add(row)
    if 0 <= col < 128:
        queried_cols.add(col)

print(f"\nAbgefragte Matrix-Zeilen: {len(queried_rows)} unique")
print(f"Abgefragte Matrix-Spalten: {len(queried_cols)} unique")

# =============================================================================
# 6. MAYBE THE VALUES ARE COMPUTED, NOT LOOKED UP
# =============================================================================
print("\n--- 6. BERECHNUNGS-HYPOTHESEN ---")

def test_computation(compute_func, name):
    match_count = 0
    for resp in responses:
        x, y, expected = resp["x"], resp["y"], resp["value"]
        try:
            result = compute_func(x, y, matrix)
            if result == expected:
                match_count += 1
        except:
            pass
    return match_count

# Die Matrix-Werte könnten kombiniert werden
computations = {
    "matrix[row,col] XOR x":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) ^ (x & 0xFF),

    "matrix[row,col] XOR y":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) ^ (y & 0xFF),

    "matrix[row,col] XOR (x+y)":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) ^ ((x+y) & 0xFF),

    "matrix[row,col] + x":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) + x,

    "matrix[row,col] + y":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) + y,

    "matrix[row,col] - x":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) - x,

    "matrix[row,col] - y":
        lambda x, y, m: int(m[(63-y)%128, (x+64)%128]) - y,

    "sum(matrix[row,:]) % 256 - 128":
        lambda x, y, m: int(np.sum(m[(63-y)%128, :])) % 256 - 128,

    "matrix[row,col] * -1":
        lambda x, y, m: int(-m[(63-y)%128, (x+64)%128]),
}

print("Teste Berechnungen auf Matrix-Werten:")
comp_results = []
for name, func in computations.items():
    count = test_computation(func, name)
    if count > 0:
        pct = count / len(responses) * 100
        comp_results.append((name, count, pct))

comp_results.sort(key=lambda x: -x[1])
for name, count, pct in comp_results[:10]:
    print(f"  {name}: {count}/{len(responses)} ({pct:.1f}%)")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: KOORDINATEN-MAPPING TEST")
print("=" * 70)

best_transform = max(results, key=lambda x: x[1])

print(f"""
VERIFIZIERTE TRANSFORMATION:
  row = (63 - y) % 128
  col = (x + 64) % 128

TESTERGEBNIS:
  Matches: {matches}/{len(responses)} ({matches/len(responses)*100:.1f}%)

BESTE ALTERNATIVE:
  {best_transform[0]}: {best_transform[1]} Matches ({best_transform[2]:.1f}%)

SCHLUSSFOLGERUNG:
  Die dokumentierte Transformation passt NICHT zu den Anna-Bot Daten!
  Anna-Bot macht NICHT einfach matrix[row, col] lookups.

  Die Werte müssen BERECHNET werden, nicht direkt ausgelesen.
  Der Algorithmus ist noch unbekannt.
""")

# Speichere Ergebnisse
output = {
    "verified_transform_matches": matches,
    "total_responses": len(responses),
    "match_rate": matches / len(responses),
    "best_transform": {
        "name": best_transform[0],
        "matches": best_transform[1],
        "rate": best_transform[2] / 100
    },
    "conclusion": "Direct matrix lookup does NOT match Anna-Bot outputs"
}

output_path = script_dir / "MAPPING_TEST_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
