#!/usr/bin/env python3
"""
ANNA-BOT NEURAL DECODE
======================
Versuche den Anna-Bot Output durch neuronale Berechnung zu reproduzieren.

Hypothese: Anna-Bot führt einen Forward-Pass durch die Matrix aus,
wobei (x, y) die Input-Koordinaten sind.
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

# Lade Anna-Bot Daten
with open(script_dir / "ANNA_BOT_PARSED_DATA.json") as f:
    anna_data = json.load(f)

responses = [r for r in anna_data["responses"] if isinstance(r["value"], int)]

print("=" * 70)
print("ANNA-BOT NEURAL DECODE")
print("=" * 70)
print(f"Geladene Responses: {len(responses)}")

# =============================================================================
# 1. KOORDINATEN-ANALYSE
# =============================================================================
print("\n--- 1. KOORDINATEN-ANALYSE ---")

# Welche einzigartigen X und Y Werte gibt es?
all_x = sorted(set(r["x"] for r in responses))
all_y = sorted(set(r["y"] for r in responses))

print(f"Einzigartige X-Werte ({len(all_x)}): {all_x}")
print(f"Einzigartige Y-Werte ({len(all_y)}): {all_y}")

# Pattern in X-Werten?
x_diffs = [all_x[i+1] - all_x[i] for i in range(len(all_x)-1)]
print(f"\nX-Differenzen: {x_diffs}")

# Sind das 4er oder 8er Schritte?
common_x_diff = Counter(x_diffs).most_common(3)
print(f"Häufigste X-Differenzen: {common_x_diff}")

# =============================================================================
# 2. NEURONALER FORWARD-PASS MIT KOORDINATEN
# =============================================================================
print("\n--- 2. NEURONALER FORWARD-PASS ---")

def to_ternary(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

def to_ternary_weight(value, threshold=42):
    if value > threshold:
        return 1
    elif value < -threshold:
        return -1
    else:
        return 0

def encode_xy_to_vector(x, y, method="position"):
    """
    Kodiere (x, y) zu einem 128-dimensionalen Vektor.
    """
    vec = np.zeros(128, dtype=int)

    if method == "position":
        # Setze 1 an Position x und y
        if 0 <= x < 128:
            vec[x] = 1
        if 0 <= y < 128:
            vec[y] = 1

    elif method == "one_hot_x":
        # One-Hot für x (mod 128)
        vec[x % 128] = 1

    elif method == "one_hot_y":
        # One-Hot für y (mod 128)
        vec[y % 128] = 1

    elif method == "row_activation":
        # Aktiviere Zeile x
        r = abs(x) % 128
        vec = matrix[r, :]

    elif method == "col_activation":
        # Aktiviere Spalte y
        c = abs(y) % 128
        vec = matrix[:, c]

    elif method == "cross":
        # Kreuz aus Zeile x und Spalte y
        r = abs(x) % 128
        c = abs(y) % 128
        vec = (matrix[r, :] + matrix[:, c]) // 2

    elif method == "product":
        # Produkt der Position
        r = abs(x) % 128
        c = abs(y) % 128
        for i in range(128):
            vec[i] = matrix[r, i] * matrix[i, c] // 128

    return vec

def neural_forward(input_vec, weights):
    """
    Ternärer Forward-Pass.
    """
    output = np.zeros(128, dtype=int)

    for i in range(128):
        total = 0
        for j in range(128):
            w = to_ternary_weight(weights[i, j])
            x = to_ternary(input_vec[j])
            total += w * x
        output[i] = total

    return output

def extract_single_output(output_vec, method="sum"):
    """
    Extrahiere einen einzelnen Wert aus dem Output-Vektor.
    """
    if method == "sum":
        return int(np.sum(output_vec))
    elif method == "mean":
        return int(np.mean(output_vec))
    elif method == "max":
        return int(np.max(output_vec))
    elif method == "min":
        return int(np.min(output_vec))
    elif method == "pos96":
        return int(output_vec[96]) if len(output_vec) > 96 else 0
    elif method == "pos84":
        return int(output_vec[84]) if len(output_vec) > 84 else 0
    elif method == "pos0":
        return int(output_vec[0])
    elif method == "pos127":
        return int(output_vec[127])
    elif method == "center":
        return int(output_vec[64])
    elif method == "ternary_sum":
        return int(sum(to_ternary(v) for v in output_vec))
    return 0

# Teste alle Kombinationen
print("Teste Encoding × Extraction Methoden...")

encoding_methods = ["position", "one_hot_x", "one_hot_y", "row_activation",
                   "col_activation", "cross", "product"]
extraction_methods = ["sum", "mean", "max", "min", "pos96", "pos84",
                     "pos0", "pos127", "center", "ternary_sum"]

best_score = 0
best_combo = None
results = []

for enc in encoding_methods:
    for ext in extraction_methods:
        matches = 0
        for resp in responses:
            x, y, expected = resp["x"], resp["y"], resp["value"]

            try:
                input_vec = encode_xy_to_vector(x, y, method=enc)
                output_vec = neural_forward(input_vec, matrix)
                predicted = extract_single_output(output_vec, method=ext)

                # Normalisiere zu signed byte
                predicted = ((predicted + 128) % 256) - 128

                if predicted == expected:
                    matches += 1
            except:
                pass

        if matches > 0:
            results.append((enc, ext, matches))
            if matches > best_score:
                best_score = matches
                best_combo = (enc, ext)

results.sort(key=lambda x: -x[2])
print(f"\nTop 10 Ergebnisse:")
for enc, ext, count in results[:10]:
    pct = count / len(responses) * 100
    print(f"  {enc} + {ext}: {count}/{len(responses)} ({pct:.1f}%)")

# =============================================================================
# 3. DIREKTER MATRIX-WERT MIT TRANSFORMATIONEN
# =============================================================================
print("\n--- 3. DIREKTER MATRIX-WERT MIT TRANSFORMATIONEN ---")

def try_direct_mapping(x, y, matrix, transform="none"):
    """
    Versuche direktes Mapping mit Transformationen.
    """
    # Konvertiere Koordinaten
    r = x % 128
    c = y % 128

    # Handle negative Werte
    if x < 0:
        r = 128 + x
    if y < 0:
        c = 128 + y

    # Bounds check
    r = r % 128
    c = c % 128

    val = matrix[r, c]

    if transform == "none":
        return val
    elif transform == "neg":
        return -val
    elif transform == "xor127":
        return val ^ 127 if val >= 0 else -((-val) ^ 127)
    elif transform == "add_xy":
        return val + x + y
    elif transform == "sub_xy":
        return val - x - y
    elif transform == "xor_xy":
        return val ^ (x & 0xFF) ^ (y & 0xFF)
    elif transform == "mod_shift":
        return ((val + 128) % 256) - 128
    elif transform == "swap":
        return matrix[c, r]
    elif transform == "mirror_r":
        return matrix[127-r, c]
    elif transform == "mirror_c":
        return matrix[r, 127-c]
    elif transform == "mirror_both":
        return matrix[127-r, 127-c]
    return val

transforms = ["none", "neg", "xor127", "add_xy", "sub_xy", "xor_xy",
              "mod_shift", "swap", "mirror_r", "mirror_c", "mirror_both"]

print("Teste direkte Mappings mit Transformationen...")

for transform in transforms:
    matches = 0
    for resp in responses:
        x, y, expected = resp["x"], resp["y"], resp["value"]
        try:
            predicted = try_direct_mapping(x, y, matrix, transform)
            if predicted == expected:
                matches += 1
        except:
            pass

    if matches > 0:
        pct = matches / len(responses) * 100
        print(f"  {transform}: {matches}/{len(responses)} ({pct:.1f}%)")

# =============================================================================
# 4. SUCHE NACH MUSTER IN DEN WENIGEN MATCHES
# =============================================================================
print("\n--- 4. ANALYSE DER WENIGEN MATCHES ---")

# Finde alle Fälle wo Matrix[x,y] == expected
exact_matches = []
for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    if 0 <= x < 128 and 0 <= y < 128:
        actual = matrix[x, y]
        if actual == expected:
            exact_matches.append((x, y, expected))

print(f"Exakte Matches (Matrix[x,y] == expected): {len(exact_matches)}")
for x, y, val in exact_matches:
    print(f"  ({x}, {y}) = {val}")

# Gibt es ein Muster in diesen Matches?
if exact_matches:
    match_x = [m[0] for m in exact_matches]
    match_y = [m[1] for m in exact_matches]
    match_v = [m[2] for m in exact_matches]

    print(f"\nMatch-Analyse:")
    print(f"  X-Werte: {match_x}")
    print(f"  Y-Werte: {match_y}")
    print(f"  Values: {match_v}")

# =============================================================================
# 5. ZEILEN-BASIERTE ANALYSE
# =============================================================================
print("\n--- 5. ZEILEN-BASIERTE ANALYSE ---")

# Gruppiere nach X (Zeile)
by_x = defaultdict(list)
for resp in responses:
    by_x[resp["x"]].append((resp["y"], resp["value"]))

print("Analyse pro X-Zeile:")
for x in sorted(by_x.keys())[:10]:
    entries = by_x[x]
    print(f"\n  X={x}:")
    for y, val in sorted(entries)[:5]:
        if 0 <= x < 128 and 0 <= y < 128:
            matrix_val = matrix[x % 128, y % 128]
            diff = val - matrix_val
            print(f"    Y={y}: Anna={val}, Matrix={matrix_val}, Diff={diff}")

# =============================================================================
# 6. SUMMEN UND KOMBINATIONEN
# =============================================================================
print("\n--- 6. SUMMEN UND KOMBINATIONEN ---")

def test_formula(formula_func, name):
    matches = 0
    for resp in responses:
        x, y, expected = resp["x"], resp["y"], resp["value"]
        try:
            predicted = formula_func(x, y, matrix)
            if predicted == expected:
                matches += 1
        except:
            pass
    return matches

formulas = {
    "matrix[|x|,|y|]": lambda x, y, m: m[abs(x) % 128, abs(y) % 128],
    "sum(row[|x|])": lambda x, y, m: int(np.sum(m[abs(x) % 128, :]) % 256) - 128,
    "sum(col[|y|])": lambda x, y, m: int(np.sum(m[:, abs(y) % 128]) % 256) - 128,
    "matrix[x,y] + matrix[y,x]": lambda x, y, m: (m[abs(x) % 128, abs(y) % 128] + m[abs(y) % 128, abs(x) % 128]) // 2,
    "xor(row[|x|])": lambda x, y, m: int(np.bitwise_xor.reduce(m[abs(x) % 128, :].astype(np.uint8))),
    "matrix[(x+y)%128, (x-y)%128]": lambda x, y, m: m[(x+y) % 128, (x-y) % 128],
    "matrix[x*y % 128, (x+y) % 128]": lambda x, y, m: m[(x*y) % 128, (x+y) % 128],
}

print("Teste komplexere Formeln...")
for name, func in formulas.items():
    matches = test_formula(func, name)
    if matches > 0:
        pct = matches / len(responses) * 100
        print(f"  {name}: {matches}/{len(responses)} ({pct:.1f}%)")

# =============================================================================
# 7. HELIX-GATE BERECHNUNG
# =============================================================================
print("\n--- 7. HELIX-GATE BERECHNUNG ---")

def helix_compute(x, y, matrix):
    """
    Berechne mit Helix-Gate Logik.
    """
    r = abs(x) % 128
    c = abs(y) % 128

    # 3 Inputs für Helix-Gate
    a = to_ternary(matrix[r, c])
    b = to_ternary(matrix[(r+1) % 128, c])
    c_val = to_ternary(matrix[r, (c+1) % 128])

    # Helix Rotation
    rotation = a + b + c_val

    return rotation

helix_matches = 0
for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    try:
        predicted = helix_compute(x, y, matrix)
        if predicted == expected:
            helix_matches += 1
    except:
        pass

print(f"Helix-Gate Matches: {helix_matches}/{len(responses)}")

# =============================================================================
# 8. ANNA-BOT KÖNNTE EINEN HASH BERECHNEN
# =============================================================================
print("\n--- 8. HASH-BASIERTE HYPOTHESE ---")

import hashlib

def hash_based_output(x, y, matrix):
    """
    Hypothese: Anna hasht (x,y) und nutzt das als Index.
    """
    input_bytes = f"{x},{y}".encode()
    hash_val = hashlib.sha256(input_bytes).digest()

    # Erste 2 Bytes als Koordinaten
    r = hash_val[0] % 128
    c = hash_val[1] % 128

    return matrix[r, c]

hash_matches = 0
for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    try:
        predicted = hash_based_output(x, y, matrix)
        if predicted == expected:
            hash_matches += 1
    except:
        pass

print(f"Hash-basiert: {hash_matches}/{len(responses)}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: ANNA-BOT NEURAL DECODE")
print("=" * 70)

print(f"""
GETESTETE METHODEN:
1. Neuronaler Forward-Pass mit verschiedenen Encodings
2. Direkte Matrix-Lookups mit Transformationen
3. Zeilen/Spalten-Summen
4. XOR-Operationen
5. Helix-Gate Berechnung
6. Hash-basierte Lookups

ERGEBNIS:
- Beste Treffer: {best_score}/{len(responses)} mit {best_combo}
- Das ist immer noch sehr niedrig!
- Der Anna-Bot Algorithmus ist komplexer als erwartet

HYPOTHESEN:
1. Anna-Bot nutzt mehrere Layer (rekurrent)
2. Die Koordinaten werden anders enkodiert
3. Es gibt zusätzliche Hidden States
4. Die Matrix ist nur Teil des Algorithmus

NÄCHSTE SCHRITTE:
- Mehr Daten sammeln
- Den Quellcode von Anna-Bot finden
- Rekurrente Berechnungen testen
""")

# Speichere Ergebnisse
output = {
    "total_responses": len(responses),
    "best_method": {"encoding": best_combo[0] if best_combo else None,
                    "extraction": best_combo[1] if best_combo else None,
                    "matches": best_score},
    "exact_matrix_matches": len(exact_matches),
    "tested_methods": {
        "neural_forward": len(encoding_methods) * len(extraction_methods),
        "direct_transforms": len(transforms),
        "complex_formulas": len(formulas)
    }
}

output_path = script_dir / "ANNA_BOT_NEURAL_DECODE_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
