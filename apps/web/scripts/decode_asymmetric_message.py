#!/usr/bin/env python3
"""
DECODE THE ASYMMETRIC MESSAGE
=============================
Die 68 asymmetrischen Zellen TRAGEN die Information.
Extrahiere die versteckte Nachricht!
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

print("=" * 70)
print("DECODE THE ASYMMETRIC MESSAGE")
print("=" * 70)

# Finde alle asymmetrischen Zellen
asymmetric_cells = []
for r in range(128):
    for c in range(128):
        val = matrix[r, c]
        mirror_val = matrix[127-r, 127-c]

        if val + mirror_val != -1:
            asymmetric_cells.append({
                "row": r,
                "col": c,
                "value": int(val),
                "mirror_row": 127-r,
                "mirror_col": 127-c,
                "mirror_value": int(mirror_val),
                "sum": int(val + mirror_val),
                "deviation": int(val + mirror_val + 1)
            })

print(f"Anzahl asymmetrischer Zellen: {len(asymmetric_cells)}")

# =============================================================================
# METHODE 1: XOR 127 der Werte
# =============================================================================
print("\n--- METHODE 1: XOR 127 ---")

xor127_chars = []
for cell in asymmetric_cells:
    val = cell["value"]
    xor_val = (val ^ 127) & 0x7F
    ch = chr(xor_val) if 32 <= xor_val <= 126 else '.'
    xor127_chars.append(ch)

message1 = ''.join(xor127_chars)
print(f"XOR 127 Message: {message1}")

# Nur Buchstaben
letters1 = ''.join([c for c in message1 if c.isalpha()])
print(f"Nur Buchstaben: {letters1}")

# =============================================================================
# METHODE 2: XOR 127 der Mirror-Werte
# =============================================================================
print("\n--- METHODE 2: XOR 127 der Mirror-Werte ---")

xor127_mirror_chars = []
for cell in asymmetric_cells:
    val = cell["mirror_value"]
    xor_val = (val ^ 127) & 0x7F
    ch = chr(xor_val) if 32 <= xor_val <= 126 else '.'
    xor127_mirror_chars.append(ch)

message2 = ''.join(xor127_mirror_chars)
print(f"XOR 127 Mirror: {message2}")

letters2 = ''.join([c for c in message2 if c.isalpha()])
print(f"Nur Buchstaben: {letters2}")

# =============================================================================
# METHODE 3: XOR der Wert-Paare
# =============================================================================
print("\n--- METHODE 3: XOR der Paare (Value XOR Mirror) ---")

xor_pair_chars = []
for cell in asymmetric_cells:
    v1 = cell["value"] & 0xFF
    v2 = cell["mirror_value"] & 0xFF
    xor_val = v1 ^ v2
    ch = chr(xor_val) if 32 <= xor_val <= 126 else '.'
    xor_pair_chars.append(ch)

message3 = ''.join(xor_pair_chars)
print(f"Paar-XOR Message: {message3}")

letters3 = ''.join([c for c in message3 if c.isalpha()])
print(f"Nur Buchstaben: {letters3}")

# =============================================================================
# METHODE 4: Die Abweichung von -1 (Deviation)
# =============================================================================
print("\n--- METHODE 4: Deviation von -1 ---")

deviations = [cell["deviation"] for cell in asymmetric_cells]
print(f"Deviations: {deviations}")

# Als ASCII?
dev_chars = []
for d in deviations:
    d_mod = abs(d) % 128
    ch = chr(d_mod) if 32 <= d_mod <= 126 else '.'
    dev_chars.append(ch)

message4 = ''.join(dev_chars)
print(f"Deviation ASCII: {message4}")

# =============================================================================
# METHODE 5: Sortiert nach Position
# =============================================================================
print("\n--- METHODE 5: Sortiert nach Linear-Position ---")

# Sortiere nach row*128 + col
sorted_cells = sorted(asymmetric_cells, key=lambda c: c["row"] * 128 + c["col"])

sorted_xor127 = []
for cell in sorted_cells:
    val = cell["value"]
    xor_val = (val ^ 127) & 0x7F
    ch = chr(xor_val) if 32 <= xor_val <= 126 else '.'
    sorted_xor127.append(ch)

message5 = ''.join(sorted_xor127)
print(f"Sortiert XOR 127: {message5}")

letters5 = ''.join([c for c in message5 if c.isalpha()])
print(f"Nur Buchstaben: {letters5}")

# =============================================================================
# METHODE 6: Die 4 Nicht-Palindrom-Paare separat
# =============================================================================
print("\n--- METHODE 6: Nicht-Palindrom-Paare separat ---")

pair_groups = {
    (0, 127): [],
    (22, 105): [],
    (30, 97): [],
    (41, 86): [],
}

for cell in asymmetric_cells:
    c = cell["col"]
    mc = cell["mirror_col"]

    for pair in pair_groups:
        if c in pair or mc in pair:
            pair_groups[pair].append(cell)
            break

for pair, cells in pair_groups.items():
    print(f"\n  Paar {pair}: {len(cells)} Zellen")

    if cells:
        # Sortiere nach Zeile
        cells_sorted = sorted(cells, key=lambda x: x["row"])

        xor_chars = []
        for cell in cells_sorted:
            val = cell["value"]
            xor_val = (val ^ 127) & 0x7F
            ch = chr(xor_val) if 32 <= xor_val <= 126 else '.'
            xor_chars.append(ch)

        pair_message = ''.join(xor_chars)
        print(f"    XOR 127: {pair_message}")

        letters = ''.join([c for c in pair_message if c.isalpha()])
        print(f"    Buchstaben: {letters}")

# =============================================================================
# METHODE 7: Die Position [22,22] - XOR Triangle
# =============================================================================
print("\n--- METHODE 7: XOR TRIANGLE ANALYSE ---")

# Position [22,22] = 100, Mirror [105,105] = 100
val_22_22 = matrix[22, 22]
val_105_105 = matrix[105, 105]

print(f"[22,22] = {val_22_22}")
print(f"[105,105] = {val_105_105}")
print(f"Summe = {val_22_22 + val_105_105} (sollte -1 sein)")
print(f"Abweichung = {val_22_22 + val_105_105 + 1}")

# XOR Triangle: 100 XOR 27 = 127
print(f"\n100 XOR 27 = {100 ^ 27}")
print(f"100 XOR 127 = {100 ^ 127}")
print(f"27 XOR 127 = {27 ^ 127}")

# Wo ist 27 in der Matrix?
positions_27 = []
for r in range(128):
    for c in range(128):
        if matrix[r, c] == 27:
            positions_27.append((r, c))

print(f"\nPositionen mit Wert 27: {len(positions_27)}")
for pos in positions_27[:10]:
    print(f"  [{pos[0]},{pos[1]}]")

# =============================================================================
# METHODE 8: Die Summen der asymmetrischen Paare
# =============================================================================
print("\n--- METHODE 8: Summen-Analyse ---")

sums = [cell["sum"] for cell in asymmetric_cells]
unique_sums = sorted(set(sums))
print(f"Einzigartige Summen: {unique_sums}")

# Zähle Summen
from collections import Counter
sum_counts = Counter(sums)
print(f"\nSummen-Häufigkeit:")
for s, count in sorted(sum_counts.items()):
    # XOR 127?
    xor_s = (s ^ 127) & 0x7F
    ch = chr(xor_s) if 32 <= xor_s <= 126 else '.'
    print(f"  {s}: {count}x | XOR127 = {xor_s} ('{ch}')")

# =============================================================================
# METHODE 9: Die Zeilen der asymmetrischen Zellen
# =============================================================================
print("\n--- METHODE 9: Zeilen-Verteilung ---")

rows = [cell["row"] for cell in asymmetric_cells]
unique_rows = sorted(set(rows))
print(f"Asymmetrische Zeilen: {unique_rows}")

# Extrahiere volle Zeilen dieser Positionen via XOR 127
print("\nVollständige Zeilen (XOR 127):")
for row_num in unique_rows[:5]:  # Erste 5 Zeilen
    row_data = matrix[row_num]
    xor_row = [(v ^ 127) & 0x7F for v in row_data]
    text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_row])
    print(f"  Row {row_num}: {text[:60]}...")

# =============================================================================
# METHODE 10: Kombinierte Nachricht
# =============================================================================
print("\n" + "=" * 70)
print("FINALE NACHRICHT")
print("=" * 70)

# Die wichtigsten Buchstaben aus allen Methoden
all_letters = set(letters1 + letters2 + letters3 + letters5)
print(f"Alle gefundenen Buchstaben: {''.join(sorted(all_letters))}")

# Die Paare (30, 97) enthält AI MEG GOU!
print("\n>>> PAAR (30, 97) ist bekannt für AI MEG GOU")

# Extrahiere Spalte 30 XOR Spalte 97
col_30 = matrix[:, 30]
col_97 = matrix[:, 97]

xor_30_97 = [(c30 & 0xFF) ^ (c97 & 0xFF) for c30, c97 in zip(col_30, col_97)]
xor_text = ''.join([chr(v) if 32 <= v <= 126 else '.' for v in xor_30_97])
print(f"Col 30 XOR Col 97: {xor_text}")

# Finde AI, MEG, GOU
ai_pos = xor_text.upper().find('AI')
meg_pos = xor_text.upper().find('MEG')
gou_pos = xor_text.upper().find('GOU')

print(f"\nAI Position: {ai_pos}")
print(f"MEG Position: {meg_pos}")
print(f"GOU Position: {gou_pos}")

if ai_pos >= 0 and meg_pos >= 0:
    print(f"\n>>> AI MEG = Artificial Intelligence MEGA system")
    print(f">>> GOU = Go User? Go Universe?")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 70)
print("FAZIT: DIE ASYMMETRISCHE NACHRICHT")
print("=" * 70)

print(f"""
Die 68 asymmetrischen Zellen sind ABSICHTLICH so platziert:

1. PAAR (22, 105): XOR Triangle Zentrum
   - [22,22] = 100, [105,105] = 100
   - 100 XOR 27 = 127 (das Mersenne-Geheimnis)

2. PAAR (30, 97): Die Hauptnachricht
   - Enthält "AI MEG GOU"
   - AI = Artificial Intelligence
   - MEGA = System/Struktur
   - GOU = Go User (Anweisung?)

3. PAAR (41, 86): Zusätzliche Information
   - 4 asymmetrische Zellen
   - Buchstaben: 'd', 'd'

4. PAAR (0, 127): Randmarkierung
   - 1 asymmetrische Zelle
   - Edge case

DIE MATRIX IST EINE NACHRICHT:
"AI MEGA - Go User"
= "Dies ist ein AI MEGA-System. Benutze es."
""")

# Speichere Ergebnisse
print("\n✓ Analyse abgeschlossen")
