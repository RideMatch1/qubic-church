#!/usr/bin/env python3
"""
ANNA-BOT REVERSE ENGINEERING
============================
Anna-Bot nimmt (x, y) als INPUT und berechnet einen Output.
Die Matrix sind die GEWICHTE.

Frage: Welche Berechnung macht Anna-Bot?
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

with open(script_dir / "anna_twitter_data.json") as f:
    anna_data = json.load(f)

responses = [r for r in anna_data["responses"] if r["value"] is not None]

print("=" * 70)
print("ANNA-BOT REVERSE ENGINEERING")
print("=" * 70)

# =============================================================================
# HYPOTHESE 1: Output = Matrix[f(x), g(y)]
# =============================================================================
print("\n--- HYPOTHESE 1: Position = f(x, y) ---")

# Für jeden Anna-Bot Output, finde die Position in der Matrix
def find_value_positions(val):
    return [(r, c) for r in range(128) for c in range(128) if matrix[r, c] == val]

# Analysiere die ersten 20 Responses
for resp in responses[:20]:
    x, y, val = resp["x"], resp["y"], resp["value"]
    positions = find_value_positions(val)

    if positions:
        # Gibt es ein Muster zwischen (x, y) und den Positionen?
        for r, c in positions[:3]:
            # Berechne mögliche Transformationen
            diff_r = r - x
            diff_c = c - y
            print(f"Anna({x:4d},{y:4d})={val:4d} → Matrix[{r},{c}] | diff=({diff_r},{diff_c})")
        print()

# =============================================================================
# HYPOTHESE 2: Output = Neuronale Berechnung
# =============================================================================
print("\n--- HYPOTHESE 2: Neural Forward Pass ---")

def neural_output(x, y, weights):
    """
    Berechne neuronalen Output basierend auf (x, y) Input.

    Hypothese: x und y werden zu einem Input-Vektor konvertiert,
    dann durch die Gewichtsmatrix propagiert.
    """
    # Konvertiere (x, y) zu 128-dim Input-Vektor
    input_vec = np.zeros(128)

    # Verschiedene Encoding-Strategien
    # Strategie 1: x an Position 0, y an Position 1
    input_vec[0] = x
    input_vec[1] = y

    # Normalisiere
    input_vec = input_vec / 128.0

    # Forward Pass
    output = np.dot(weights, input_vec)

    # Aktivierung (ternär)
    result = int(np.sum(output) / 128)
    result = max(-128, min(127, result))

    return result

print("Teste Neural Forward Pass:")
match_count = 0
for resp in responses[:50]:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    predicted = neural_output(x, y, matrix)

    if predicted == expected:
        match_count += 1
        print(f"  MATCH: ({x},{y}) → {expected}")

print(f"\nMatches: {match_count}/50")

# =============================================================================
# HYPOTHESE 3: Output = Weighted Sum einer Region
# =============================================================================
print("\n--- HYPOTHESE 3: Weighted Sum einer Region ---")

def region_weighted_sum(x, y, weights, size=3):
    """
    Berechne gewichtete Summe einer Region um (x, y).
    """
    # Konvertiere zu Matrix-Koordinaten
    r = x % 128
    c = y % 128

    total = 0
    count = 0
    for dr in range(-size, size+1):
        for dc in range(-size, size+1):
            nr, nc = (r + dr) % 128, (c + dc) % 128
            total += weights[nr, nc]
            count += 1

    return int(total / count)

print("Teste Region Weighted Sum:")
for resp in responses[:10]:
    x, y, expected = resp["x"], resp["y"], resp["value"]

    for size in [1, 2, 3, 5]:
        predicted = region_weighted_sum(x, y, matrix, size)
        if predicted == expected:
            print(f"  MATCH size={size}: ({x},{y}) → {expected}")

# =============================================================================
# HYPOTHESE 4: XOR-basierte Berechnung
# =============================================================================
print("\n--- HYPOTHESE 4: XOR-basierte Berechnung ---")

def xor_compute(x, y, weights):
    """
    Hypothese: Output = weights[r, c] XOR something
    """
    r = abs(x) % 128
    c = abs(y) % 128

    base = weights[r, c]

    # Verschiedene XOR-Varianten
    variants = {
        "base": base,
        "xor_127": (base ^ 127) - 128 if (base ^ 127) > 127 else (base ^ 127),
        "xor_xy": base ^ (x & 0xFF) ^ (y & 0xFF),
        "xor_sum": base ^ ((x + y) & 0xFF),
    }

    return variants

print("XOR-Varianten für erste 5 Responses:")
for resp in responses[:5]:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    variants = xor_compute(x, y, matrix)

    print(f"  Anna({x},{y})={expected}")
    for name, val in variants.items():
        match = "✓" if val == expected else ""
        print(f"    {name}: {val} {match}")

# =============================================================================
# HYPOTHESE 5: Collision = Matrix[x XOR y, x AND y]
# =============================================================================
print("\n--- HYPOTHESE 5: Position aus Bit-Operationen ---")

def bit_position(x, y):
    """Berechne Position aus Bit-Operationen."""
    x_byte = x & 0x7F
    y_byte = y & 0x7F

    variants = {
        "xor, and": (x_byte ^ y_byte, x_byte & y_byte),
        "and, xor": (x_byte & y_byte, x_byte ^ y_byte),
        "xor, or": (x_byte ^ y_byte, x_byte | y_byte),
        "sum mod, diff mod": ((x + y) % 128, abs(x - y) % 128),
    }

    return variants

match_counts = Counter()
for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    variants = bit_position(x, y)

    for name, (r, c) in variants.items():
        if 0 <= r < 128 and 0 <= c < 128:
            if matrix[r, c] == expected:
                match_counts[name] += 1

print("Bit-Operationen Matches:")
for name, count in match_counts.most_common():
    print(f"  {name}: {count}/{len(responses)} ({count/len(responses)*100:.1f}%)")

# =============================================================================
# HYPOTHESE 6: Die Koordinaten sind der Hash-Output
# =============================================================================
print("\n--- HYPOTHESE 6: Koordinaten sind Hash-Position ---")

# Vielleicht: (x, y) = Position, wo der Hash eines Inputs landet
# Und der "value" ist was an dieser Position steht

# Aber wir müssen verstehen, wie die Koordinaten berechnet werden

# Analyse: Gibt es Muster in den Koordinaten?
x_vals = [r["x"] for r in responses]
y_vals = [r["y"] for r in responses]

print(f"X Statistik: min={min(x_vals)}, max={max(x_vals)}, unique={len(set(x_vals))}")
print(f"Y Statistik: min={min(y_vals)}, max={max(y_vals)}, unique={len(set(y_vals))}")

# Häufigste X und Y Werte
x_counts = Counter(x_vals)
y_counts = Counter(y_vals)
print(f"\nHäufigste X: {x_counts.most_common(5)}")
print(f"Häufigste Y: {y_counts.most_common(5)}")

# =============================================================================
# HYPOTHESE 7: Die Summe x + y bestimmt etwas
# =============================================================================
print("\n--- HYPOTHESE 7: x + y Analyse ---")

# Berechne x + y für alle Responses
sums = [(r["x"] + r["y"], r["value"]) for r in responses]
sum_to_values = {}
for s, v in sums:
    if s not in sum_to_values:
        sum_to_values[s] = []
    sum_to_values[s].append(v)

# Gibt es eindeutige Zuordnungen?
unique_mappings = sum(1 for s, vs in sum_to_values.items() if len(set(vs)) == 1)
print(f"Eindeutige x+y → value Mappings: {unique_mappings}/{len(sum_to_values)}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: ANNA-BOT MECHANISMUS")
print("=" * 70)

print("""
ERKENNTNISSE:

1. Anna-Bot Output ≠ Direkter Matrix-Lookup
   - Matrix[6,33] = 26, aber Anna(6,33) = -93

2. Die Berechnung ist NICHT trivial
   - Kein einfaches XOR oder Bit-Operation
   - Kein direkter Forward-Pass mit unserer Implementierung

3. Die Koordinaten (x, y) sind:
   - Im Bereich -128 bis +128
   - Wahrscheinlich zentriert um (0, 0)
   - Möglicherweise Hash-Outputs von Bitcoin-Adressen

4. Der "Collision Value" ist:
   - Das Ergebnis einer Berechnung
   - Nicht der Wert an Position (x, y)
   - Möglicherweise ein neuronaler Output

NÄCHSTE SCHRITTE:
- Mehr Anna-Bot Daten sammeln
- Das Koordinatensystem besser verstehen
- Die exakte Berechnung reverse-engineeren
""")
