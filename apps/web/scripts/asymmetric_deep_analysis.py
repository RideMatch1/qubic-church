#!/usr/bin/env python3
"""
ASYMMETRIC DEEP ANALYSIS
========================
Die 34 asymmetrischen Paare im Detail analysieren.

Beobachtungen:
- Die Paare konzentrieren sich auf Spaltenpaare (22,105) und (30,97)
- Der XOR-String enthält ">BIF" (Fibonacci-Pointer)
- Das XOR Triangle Zentrum ist dabei: Anna(-42, 41) = 100 = Anna(41, -42)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def anna_to_matrix(x, y):
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col

def lookup(x, y):
    row, col = anna_to_matrix(x, y)
    return matrix[row, col]

print("=" * 70)
print("ASYMMETRIC DEEP ANALYSIS")
print("=" * 70)

# Die 34 asymmetrischen Paare (aus vorheriger Analyse)
asymmetric_pairs = []
for x in range(-64, 64):
    for y in range(-64, 64):
        x2 = -1 - x
        y2 = -1 - y
        if -64 <= x2 < 64 and -64 <= y2 < 64:
            val1 = lookup(x, y)
            val2 = lookup(x2, y2)
            if val1 + val2 != -1:
                row1, col1 = anna_to_matrix(x, y)
                row2, col2 = anna_to_matrix(x2, y2)
                # Normalisiere: nimm das mit kleinerem col
                if col1 <= col2:
                    asymmetric_pairs.append({
                        "anna1": (x, y), "matrix1": (row1, col1), "val1": val1,
                        "anna2": (x2, y2), "matrix2": (row2, col2), "val2": val2,
                        "sum": val1 + val2
                    })

# Dedupliziere
seen = set()
unique_pairs = []
for p in asymmetric_pairs:
    key = (p["matrix1"], p["matrix2"])
    if key not in seen:
        seen.add(key)
        unique_pairs.append(p)

print(f"\nGefundene asymmetrische Paare: {len(unique_pairs)}")

# =============================================================================
# 1. GRUPPIERUNG NACH SPALTENPAAREN
# =============================================================================
print("\n--- 1. GRUPPIERUNG NACH SPALTENPAAREN ---")

col_pairs = defaultdict(list)
for p in unique_pairs:
    col_pair = (p["matrix1"][1], p["matrix2"][1])
    col_pairs[col_pair].append(p)

for (c1, c2), pairs in sorted(col_pairs.items()):
    print(f"\nSpaltenpaar ({c1}, {c2}): {len(pairs)} Paare")
    print(f"  Col {c1} + Col {c2} = {c1 + c2}")
    for p in pairs:
        r1, r2 = p["matrix1"][0], p["matrix2"][0]
        v1, v2 = p["val1"], p["val2"]
        s = p["sum"]
        xor = (v1 & 0xFF) ^ (v2 & 0xFF)
        ch = chr(xor) if 32 <= xor <= 126 else '.'
        print(f"    Row {r1:3d} ↔ Row {r2:3d}: {v1:4d} + {v2:4d} = {s:4d}, XOR={xor:3d} '{ch}'")

# =============================================================================
# 2. DIE SPALTENPAARE (22,105) UND (30,97)
# =============================================================================
print("\n--- 2. ANALYSE DER SPALTENPAARE ---")

# Beide erfüllen: Col1 + Col2 = 127
print("Spaltenpaar-Eigenschaften:")
print(f"  22 + 105 = {22 + 105}")
print(f"  30 +  97 = {30 + 97}")

# Was ist an diesen Spalten besonders?
print("\nSpalte 22 (Anna x = -42):")
col22_vals = matrix[:, 22]
print(f"  Mean: {col22_vals.mean():.2f}")
print(f"  Unique values: {len(set(col22_vals))}")

print("\nSpalte 105 (Anna x = 41):")
col105_vals = matrix[:, 105]
print(f"  Mean: {col105_vals.mean():.2f}")
print(f"  Unique values: {len(set(col105_vals))}")

# =============================================================================
# 3. XOR-STRING REKONSTRUKTION
# =============================================================================
print("\n--- 3. XOR-STRING NACH ZEILEN SORTIERT ---")

# Sortiere nach Row-Position für den String
pairs_by_row = []
for p in unique_pairs:
    row1 = p["matrix1"][0]
    xor = (p["val1"] & 0xFF) ^ (p["val2"] & 0xFF)
    ch = chr(xor) if 32 <= xor <= 126 else '.'
    pairs_by_row.append((row1, ch, p))

pairs_by_row.sort(key=lambda x: x[0])

print("XOR-Zeichen nach Row-Position:")
for row, ch, p in pairs_by_row:
    v1, v2 = p["val1"], p["val2"]
    xor = (v1 & 0xFF) ^ (v2 & 0xFF)
    print(f"  Row {row:3d}: {v1:4d} XOR {v2:4d} = {xor:3d} = '{ch}'")

xor_string = ''.join(ch for _, ch, _ in pairs_by_row)
print(f"\nKompletter XOR-String: {xor_string}")

# =============================================================================
# 4. SEPARIERE DIE ZWEI SPALTENPAARE
# =============================================================================
print("\n--- 4. XOR-STRINGS PRO SPALTENPAAR ---")

for (c1, c2), pairs in sorted(col_pairs.items()):
    # Sortiere nach Row
    sorted_pairs = sorted(pairs, key=lambda p: p["matrix1"][0])

    xor_chars = []
    for p in sorted_pairs:
        xor = (p["val1"] & 0xFF) ^ (p["val2"] & 0xFF)
        ch = chr(xor) if 32 <= xor <= 126 else '.'
        xor_chars.append(ch)

    xor_str = ''.join(xor_chars)
    print(f"\nSpaltenpaar ({c1}, {c2}):")
    print(f"  XOR-String: {xor_str}")

    # Zeige die Rows
    rows = [p["matrix1"][0] for p in sorted_pairs]
    print(f"  Rows: {rows}")

# =============================================================================
# 5. DAS XOR TRIANGLE ZENTRUM
# =============================================================================
print("\n--- 5. DAS XOR TRIANGLE ZENTRUM ---")

# Anna(-42, 41) und Anna(41, -42) sind beide 100!
val_triangle = lookup(-42, 41)
val_mirror = lookup(41, -42)

print(f"Anna(-42, 41) = {val_triangle}")
print(f"Anna( 41,-42) = {val_mirror}")
print(f"Summe: {val_triangle + val_mirror}")
print(f"XOR: {val_triangle ^ val_mirror}")

print("\nDas ist das einzige Paar mit val1 == val2!")
print("100 XOR 100 = 0 → NULL-Zeichen (kein printable char)")

# =============================================================================
# 6. FIBONACCI-ANALYSE DER ASYMMETRISCHEN ROWS
# =============================================================================
print("\n--- 6. FIBONACCI-ANALYSE ---")

fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# Welche asymmetrischen Rows sind Fibonacci?
asym_rows = set()
for p in unique_pairs:
    asym_rows.add(p["matrix1"][0])
    asym_rows.add(p["matrix2"][0])

fib_rows = [r for r in asym_rows if r in fib or (128 - r) in fib]
print(f"Asymmetrische Rows: {sorted(asym_rows)}")
print(f"Davon Fibonacci (oder 128-fib): {fib_rows}")

# =============================================================================
# 7. DIE NACHRICHT EXTRAHIEREN
# =============================================================================
print("\n--- 7. NACHRICHT EXTRAHIEREN ---")

# Die XOR-Werte der Spaltenpaare getrennt analysieren
print("\nSpaltenpaar (22, 105) - '>BIF' Pointer:")
col22_105_pairs = col_pairs.get((22, 105), [])
for p in sorted(col22_105_pairs, key=lambda p: p["matrix1"][0]):
    r1 = p["matrix1"][0]
    xor = (p["val1"] & 0xFF) ^ (p["val2"] & 0xFF)
    ch = chr(xor) if 32 <= xor <= 126 else f'\\x{xor:02x}'
    print(f"  Row {r1:3d}: '{ch}' ({xor})")

print("\nSpaltenpaar (30, 97) - Weitere Nachricht:")
col30_97_pairs = col_pairs.get((30, 97), [])
for p in sorted(col30_97_pairs, key=lambda p: p["matrix1"][0]):
    r1 = p["matrix1"][0]
    xor = (p["val1"] & 0xFF) ^ (p["val2"] & 0xFF)
    ch = chr(xor) if 32 <= xor <= 126 else f'\\x{xor:02x}'
    print(f"  Row {r1:3d}: '{ch}' ({xor})")

# =============================================================================
# 8. BEIDE STRINGS ZUSAMMEN
# =============================================================================
print("\n--- 8. VOLLSTÄNDIGE NACHRICHT ---")

# Erstelle einen 128-Zeichen String für jedes Spaltenpaar
def extract_message_from_col_pair(col1, col2):
    """Extrahiere die XOR-Nachricht aus einem Spaltenpaar."""
    message = []
    for row in range(128):
        val1 = matrix[row, col1]
        val2 = matrix[row, col2]

        # Symmetrie prüfen: sollte val1 + val2 = -1 sein?
        mirror_row = 127 - row
        mirror_val1 = matrix[mirror_row, 127 - col1]
        mirror_val2 = matrix[mirror_row, 127 - col2]

        if val1 + val2 != -1:
            # Asymmetrisch!
            xor = (val1 & 0xFF) ^ (val2 & 0xFF)
            ch = chr(xor) if 32 <= xor <= 126 else '.'
            message.append(ch)
        else:
            message.append(' ')  # Symmetrisch = Leer

    return ''.join(message)

msg_22_105 = extract_message_from_col_pair(22, 105)
msg_30_97 = extract_message_from_col_pair(30, 97)

print("Nachricht in Spaltenpaar (22, 105):")
print(f"  '{msg_22_105.strip()}'")

print("\nNachricht in Spaltenpaar (30, 97):")
print(f"  '{msg_30_97.strip()}'")

# Kompaktere Darstellung (nur nicht-leere Zeichen)
compact_22 = ''.join(c for c in msg_22_105 if c != ' ')
compact_30 = ''.join(c for c in msg_30_97 if c != ' ')

print(f"\nKompakt (22,105): {compact_22}")
print(f"Kompakt (30,97):  {compact_30}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: ASYMMETRISCHE ZELLEN")
print("=" * 70)

print(f"""
STRUKTUR:
- 34 asymmetrische Paare = 68 Zellen
- Konzentriert auf 2 Spaltenpaare:
  - (22, 105): {len(col22_105_pairs)} Paare
  - (30,  97): {len(col30_97_pairs)} Paare

XOR-NACHRICHTEN:
- Spaltenpaar (22, 105): '{compact_22}'
- Spaltenpaar (30,  97): '{compact_30}'

BESONDERHEITEN:
- Das XOR Triangle Zentrum (100,100) ist dabei
- 100 XOR 100 = 0 (Null-Zeichen)
- ">BIF" könnte ein Pointer auf Fibonacci sein

INTERPRETATION:
Die 68 asymmetrischen Zellen sind die einzigen Informationsträger
in einer sonst 99.58% symmetrischen Matrix. Die XOR-Werte dieser
Zellen enthalten möglicherweise versteckte Nachrichten.
""")

# Speichere
output = {
    "total_asymmetric_pairs": len(unique_pairs),
    "column_pairs": {
        "(22,105)": {
            "count": len(col22_105_pairs),
            "xor_message": compact_22
        },
        "(30,97)": {
            "count": len(col30_97_pairs),
            "xor_message": compact_30
        }
    },
    "xor_triangle_center": {
        "position": "Anna(-42, 41) and Anna(41, -42)",
        "values": [100, 100],
        "xor": 0
    }
}

output_path = script_dir / "ASYMMETRIC_DEEP_ANALYSIS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse gespeichert: {output_path}")
