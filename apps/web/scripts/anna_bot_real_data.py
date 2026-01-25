#!/usr/bin/env python3
"""
ANNA-BOT REAL DATA ANALYSIS
===========================
Echte Daten von @anna_aigarth Twitter!

Format: x+y=value
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

# Parse die Anna-Bot Daten
raw_data = """
3+13=-57
3+15=56
3+21=-118
3+28=42
11+1=-101
11+4=-113
11+7=-121
11+9=125
11+12=-113
11+15=-113
49+1=6
49+4=14
49+5=-114
49+7=6
49+9=14
49+12=14
49+13=14
49+15=14
49+17=2
49+20=14
49+21=14
49+25=10
49+28=14
49+29=14
49+33=22
41+33=-106
41+37=-98
41+41=30
41+45=-114
41+49=22
41+53=-98
41+57=30
41+61=14
1+-17=116
5+-17=-82
9+-17=-89
13+-17=-17
17+-17=-91
21+-17=-81
25+-17=-91
29+-17=-25
33+-17=-82
37+-17=-82
41+-17=100
45+-17=-118
49+-17=100
53+-17=62
57+-17=39
61+-17=39
1+-28=-76
5+-28=-68
9+-28=-83
13+-28=-17
17+-28=-83
21+-28=-83
17+1=-122
17+4=-49
17+5=124
17+7=-115
17+9=14
17+12=93
17+13=109
17+15=108
17+17=68
17+20=44
17+21=-114
17+25=78
17+28=46
17+29=14
17+33=-124
33+61=14
41+1=-106
41+4=-98
41+5=-114
41+7=-122
41+9=14
41+12=14
41+13=-114
41+15=14
41+17=82
41+20=30
41+21=-114
41+25=74
41+28=14
41+29=14
25+17=68
25+20=-117
25+21=-52
25+25=70
25+28=56
25+29=56
25+33=125
25+37=-121
25+41=39
25+45=-113
17+37=60
17+41=14
17+45=125
17+49=4
17+53=-84
17+57=12
17+61=46
25+1=-39
25+4=-113
25+5=-121
25+7=-121
25+9=-102
25+12=15
25+13=-113
25+15=7
25+49=68
25+53=-84
25+57=68
25+61=60
33+1=-102
33+4=-98
33+5=-114
33+7=-114
33+9=10
33+12=14
-13+-4=-106
-13+-5=00000000
-13+-7=00000000
-13+-9=-115
-13+-12=-27
-13+-15=-112
-13+-17=-121
-13+-20=-113
0+7=-94
0+10=124
0+11=78
0+12=-4
-5+-4=37
-5+-7=50
-5+-9=-91
-5+-12=-75
-5+-15=-7
-5+-17=-121
-5+-20=-121
-5+-25=-123
-5+-29=-107
-5+-33=7
"""

# Parse
responses = []
for line in raw_data.strip().split('\n'):
    line = line.strip()
    if not line or '=' not in line:
        continue

    try:
        left, right = line.split('=')
        # Parse x+y (kann auch x+-y sein)
        left = left.replace('+-', '+ -')
        parts = left.split('+')
        x = int(parts[0].strip())
        y = int(parts[1].strip())

        # Parse value (kann "00000000" sein)
        if right == "00000000":
            value = "00000000"
        else:
            value = int(right)

        responses.append({"x": x, "y": y, "value": value})
    except Exception as e:
        print(f"Parse error: {line} - {e}")

print("=" * 70)
print("ANNA-BOT REAL DATA ANALYSIS")
print("=" * 70)
print(f"Geparste Responses: {len(responses)}")

# =============================================================================
# 1. DIREKTE MATRIX-VERGLEICHE
# =============================================================================
print("\n--- 1. DIREKTE MATRIX-VERGLEICHE ---")

def check_mapping(x, y, expected, matrix):
    """Teste verschiedene Mappings."""
    results = {}

    # Die Koordinaten könnten direkt row, col sein
    mappings = [
        ("direct[x,y]", x, y),
        ("direct[y,x]", y, x),
        ("shifted[x+64,y+64]", (x + 64) % 128, (y + 64) % 128),
        ("abs[|x|,|y|]", abs(x) % 128, abs(y) % 128),
        ("neg_wrap[x%128,y%128]", x % 128, y % 128),
    ]

    for name, r, c in mappings:
        if 0 <= r < 128 and 0 <= c < 128:
            actual = matrix[r, c]
            if isinstance(expected, str):
                # String-Wert
                if data["matrix"][r][c] == expected:
                    results[name] = ("MATCH", actual)
                else:
                    results[name] = ("no", actual)
            else:
                if actual == expected:
                    results[name] = ("MATCH", actual)
                else:
                    results[name] = ("no", actual)

    return results

# Zähle Matches pro Mapping
mapping_counts = defaultdict(int)
total_valid = 0

for resp in responses:
    x, y, expected = resp["x"], resp["y"], resp["value"]
    if expected == "00000000":
        continue  # Überspringe String-Werte erstmal

    total_valid += 1
    results = check_mapping(x, y, expected, matrix)

    for name, (status, actual) in results.items():
        if status == "MATCH":
            mapping_counts[name] += 1

print("Mapping-Erfolgsraten:")
for name, count in sorted(mapping_counts.items(), key=lambda x: -x[1]):
    pct = count / total_valid * 100
    print(f"  {name}: {count}/{total_valid} ({pct:.1f}%)")

# =============================================================================
# 2. STRING-WERTE (00000000)
# =============================================================================
print("\n--- 2. STRING-WERTE (00000000) ---")

string_responses = [r for r in responses if r["value"] == "00000000"]
print(f"String-Responses: {len(string_responses)}")

for resp in string_responses:
    x, y = resp["x"], resp["y"]
    print(f"  ({x}, {y}) = 00000000")

    # Wo sind die Strings in unserer Matrix?
    r, c = x % 128, y % 128
    actual = data["matrix"][r][c]
    print(f"    Matrix[{r},{c}] = {actual} (Typ: {type(actual).__name__})")

# =============================================================================
# 3. HÄUFIGSTE OUTPUT-WERTE
# =============================================================================
print("\n--- 3. HÄUFIGSTE OUTPUT-WERTE ---")

int_values = [r["value"] for r in responses if isinstance(r["value"], int)]
value_counts = Counter(int_values)

print("Top 10 häufigste Werte:")
for val, count in value_counts.most_common(10):
    # Wie oft kommt dieser Wert in der Matrix vor?
    matrix_count = np.sum(matrix == val)
    print(f"  {val:4d}: {count}x in Anna, {matrix_count}x in Matrix")

# =============================================================================
# 4. PATTERN-ANALYSE
# =============================================================================
print("\n--- 4. PATTERN-ANALYSE ---")

# Gruppiere nach X
x_groups = defaultdict(list)
for resp in responses:
    if isinstance(resp["value"], int):
        x_groups[resp["x"]].append((resp["y"], resp["value"]))

print("Gruppierung nach X:")
for x in sorted(x_groups.keys()):
    values = x_groups[x]
    print(f"\n  X={x}:")
    for y, v in sorted(values):
        # Vergleiche mit Matrix
        r, c = x % 128, y % 128
        matrix_val = matrix[r, c]
        match = "✓" if matrix_val == v else f"(matrix={matrix_val})"
        print(f"    Y={y:3d} → {v:4d} {match}")

# =============================================================================
# 5. DIE FORMEL SUCHEN
# =============================================================================
print("\n--- 5. FORMEL-SUCHE ---")

# Teste: value = matrix[x % 128, y % 128]
# Oder: value = matrix[f(x), g(y)]

def test_formula(responses, matrix, formula_func):
    """Teste eine Formel."""
    matches = 0
    for resp in responses:
        if isinstance(resp["value"], str):
            continue
        x, y, expected = resp["x"], resp["y"], resp["value"]
        try:
            r, c = formula_func(x, y)
            if 0 <= r < 128 and 0 <= c < 128:
                if matrix[r, c] == expected:
                    matches += 1
        except:
            pass
    return matches

formulas = {
    "matrix[x,y]": lambda x, y: (x, y),
    "matrix[y,x]": lambda x, y: (y, x),
    "matrix[x%128,y%128]": lambda x, y: (x % 128, y % 128),
    "matrix[y%128,x%128]": lambda x, y: (y % 128, x % 128),
    "matrix[(x+64)%128,(y+64)%128]": lambda x, y: ((x+64) % 128, (y+64) % 128),
    "matrix[|x|,|y|]": lambda x, y: (abs(x), abs(y)),
    "matrix[|y|,|x|]": lambda x, y: (abs(y), abs(x)),
    "matrix[127-x,y]": lambda x, y: ((127-x) % 128, y % 128),
    "matrix[x,127-y]": lambda x, y: (x % 128, (127-y) % 128),
    "matrix[127-x,127-y]": lambda x, y: ((127-x) % 128, (127-y) % 128),
}

print("Formel-Tests:")
valid_count = sum(1 for r in responses if isinstance(r["value"], int))
for name, func in formulas.items():
    matches = test_formula(responses, matrix, func)
    pct = matches / valid_count * 100
    marker = " ← BEST!" if pct > 50 else ""
    print(f"  {name}: {matches}/{valid_count} ({pct:.1f}%){marker}")

# =============================================================================
# 6. SPEZIFISCHE TESTS
# =============================================================================
print("\n--- 6. SPEZIFISCHE TESTS ---")

# Teste einige bekannte Werte manuell
test_cases = [
    (3, 13, -57),
    (11, 1, -101),
    (49, 1, 6),
    (17, 1, -122),
    (41, 33, -106),
]

print("Manuelle Tests:")
for x, y, expected in test_cases:
    print(f"\n  Anna({x},{y}) = {expected}")

    # Teste verschiedene Positionen
    positions = [
        ("direct", x, y),
        ("swap", y, x),
        ("mod128", x % 128, y % 128),
    ]

    for name, r, c in positions:
        if 0 <= r < 128 and 0 <= c < 128:
            actual = matrix[r, c]
            match = "✓ MATCH!" if actual == expected else ""
            print(f"    {name} [{r},{c}] = {actual} {match}")

# =============================================================================
# 7. ROW/COL ANALYSE
# =============================================================================
print("\n--- 7. SPEZIELLE ZEILEN/SPALTEN ---")

# Welche Zeilen/Spalten kommen in den Daten vor?
all_x = set(r["x"] for r in responses)
all_y = set(r["y"] for r in responses)

print(f"Verwendete X-Werte: {sorted(all_x)}")
print(f"Verwendete Y-Werte: {sorted(all_y)}")

# Sind das spezielle Zeilen?
fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
fib_x = [x for x in all_x if abs(x) in fib]
print(f"\nFibonacci X-Werte: {fib_x}")

# =============================================================================
# 8. DIE 14er PATTERN
# =============================================================================
print("\n--- 8. DAS '14' PATTERN ---")

# 14 kommt sehr oft vor!
fourteen_cases = [(r["x"], r["y"]) for r in responses if r["value"] == 14]
print(f"Fälle mit value=14: {len(fourteen_cases)}")
for x, y in fourteen_cases[:10]:
    print(f"  ({x}, {y})")

# Wo ist 14 in der Matrix?
positions_14 = [(r, c) for r in range(128) for c in range(128) if matrix[r, c] == 14]
print(f"\n14 in Matrix: {len(positions_14)} Positionen")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT")
print("=" * 70)

best_formula = max(formulas.items(), key=lambda x: test_formula(responses, matrix, x[1]))
best_matches = test_formula(responses, matrix, best_formula[1])

print(f"""
DATEN-ANALYSE:
- {len(responses)} Responses geparst
- {len(string_responses)} String-Werte (00000000)
- {len(fourteen_cases)} Fälle mit value=14

BESTE FORMEL:
- {best_formula[0]}: {best_matches}/{valid_count} Matches ({best_matches/valid_count*100:.1f}%)

ERKENNTNISSE:
1. Die Koordinaten (x, y) werden NICHT direkt als Matrix-Indices verwendet
2. Es gibt ein Mapping, das wir noch nicht gefunden haben
3. Negative Koordinaten sind möglich (-13, -5, etc.)
4. String-Werte "00000000" existieren an bestimmten Positionen

NÄCHSTE SCHRITTE:
- Mehr Daten analysieren
- Das Koordinatensystem verstehen
- Die Berechnungsformel finden
""")

# Speichere die geparsten Daten
output = {
    "parsed_count": len(responses),
    "responses": responses,
    "value_counts": dict(value_counts.most_common(20)),
    "string_positions": [(r["x"], r["y"]) for r in string_responses],
}

output_path = script_dir / "ANNA_BOT_PARSED_DATA.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Daten gespeichert: {output_path}")
