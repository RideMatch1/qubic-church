#!/usr/bin/env python3
"""
CFB Puzzle - Finale Interpretation

CFB x CFB = CFB^9 bedeutet:
- Das kartesische Produkt von {C, F, B} x {C, F, B} = 9 Paare
- CFB = Come-From-Beyond's Signatur

Neue Interpretation: Die 40 Zahlen sind 20 Koordinatenpaare (x,y)
die auf eine 100x100 Matrix zeigen (wie die Anna-Matrix!)
"""

import json
import hashlib

numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

base58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

print("=" * 70)
print("CFB PUZZLE - FINALE INTERPRETATION")
print("=" * 70)

# Die 40 Zahlen als 20 Koordinatenpaare
coords = [(numbers[i], numbers[i+1]) for i in range(0, 40, 2)]
print("\n1. DIE 20 KOORDINATENPAARE:")
for i, (x, y) in enumerate(coords):
    print(f"   Paar {i+1}: ({x}, {y}) -> Summe: {x+y}")

# Spezielle Paare:
print("\n2. SPEZIELLE PAARE (Summe = 137 oder 121):")
for i, (x, y) in enumerate(coords):
    s = x + y
    if s == 137:
        print(f"   ⭐ Paar {i+1}: ({x}, {y}) = 137 (Feinstrukturkonstante)")
    elif s == 121:
        print(f"   ⭐ Paar {i+1}: ({x}, {y}) = 121 (11² = CFB²)")

# Die erste und letzte Paare
print("\n3. RAHMEN-PAARE:")
print(f"   Erstes Paar: ({coords[0][0]}, {coords[0][1]}) = {sum(coords[0])}")
print(f"   Letztes Paar: ({coords[-1][0]}, {coords[-1][1]}) = {sum(coords[-1])}")

# Lade die Anna-Matrix und schaue nach
print("\n4. ANNA-MATRIX LOOKUP:")
try:
    with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json', 'r') as f:
        anna = json.load(f)

    # Die Matrix ist wahrscheinlich als nested dict oder array strukturiert
    if "matrix" in anna:
        matrix = anna["matrix"]
        print(f"   Matrix gefunden mit {len(matrix)} Einträgen")

        # Versuche die Koordinaten nachzuschlagen
        values = []
        for layer in range(10):  # Probiere verschiedene Layer
            found_any = False
            for x, y in coords:
                key = f"{layer},{x},{y}"
                if key in matrix:
                    val = matrix[key]
                    print(f"   Layer {layer}, ({x},{y}): {val}")
                    values.append(val)
                    found_any = True
            if found_any:
                break

    else:
        print("   Matrix-Struktur nicht erkannt")
        print(f"   Top-Level Keys: {list(anna.keys())[:10]}")

except Exception as e:
    print(f"   Fehler: {e}")

# Alternative Interpretation: Die Koordinaten zeigen auf einen String
print("\n5. KOORDINATEN ALS BUCHSTABEN-INDIZES:")
# Erstelle einen String aus A-Z wiederholt
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4  # 104 Zeichen

# Nimm x als Index, dann y als Index
result_x = ''.join([alphabet[x % 26] for x, y in coords])
result_y = ''.join([alphabet[y % 26] for x, y in coords])
result_xy = ''.join([alphabet[(x+y) % 26] for x, y in coords])
result_xor = ''.join([alphabet[(x ^ y) % 26] for x, y in coords])

print(f"   X-Koordinaten: {result_x}")
print(f"   Y-Koordinaten: {result_y}")
print(f"   X+Y mod 26: {result_xy}")
print(f"   X XOR Y mod 26: {result_xor}")

# Die Koordinaten als Pfad auf einem Schachbrett
print("\n6. ALS PFAD (Bewegung von Punkt zu Punkt):")
moves = []
for i in range(len(coords) - 1):
    dx = coords[i+1][0] - coords[i][0]
    dy = coords[i+1][1] - coords[i][1]
    moves.append((dx, dy))
print(f"   Bewegungen: {moves[:10]}...")

# Die Summe aller Koordinaten
print("\n7. SUMMEN-ANALYSE:")
sum_x = sum(x for x, y in coords)
sum_y = sum(y for x, y in coords)
print(f"   Summe aller X: {sum_x}")
print(f"   Summe aller Y: {sum_y}")
print(f"   Gesamtsumme: {sum_x + sum_y} (= {sum(numbers)})")

# CFB^9 - 9 spezielle Koordinaten aus dem kartesischen Produkt
print("\n8. CFB^9 - DIE 9 SPEZIELLEN KOORDINATEN:")
# CFB = {C, F, B} = {3, 6, 2} oder {67, 70, 66} (ASCII)
# Das kartesische Produkt gibt uns 9 Paare

# Mit Alphabet-Positionen (C=3, F=6, B=2)
cfb_alpha = [3, 6, 2]
cfb9_coords = [(a, b) for a in cfb_alpha for b in cfb_alpha]
print(f"   CFB = {{3, 6, 2}} (Alphabet-Positionen)")
print(f"   CFB x CFB = {cfb9_coords}")

# Finde welche unserer 20 Koordinaten zu diesen 9 passen könnten
print("\n   Matching unserer Koordinaten mit CFB^9:")
for x, y in coords:
    # Prüfe ob (x mod 10, y mod 10) in cfb9_coords ist
    mod_pair = (x % 10, y % 10)
    if mod_pair in cfb9_coords:
        print(f"   ({x}, {y}) mod 10 = {mod_pair} ✓")

# Oder die 9 Paare aus unseren 20 extrahieren die am besten zu CFB passen
print("\n9. ALTERNATIVE: DIE ERSTEN 9 PAARE:")
first_9 = coords[:9]
for i, (x, y) in enumerate(first_9):
    print(f"   Paar {i+1}: ({x}, {y})")

# Die Werte dieser 9 Paare als Summen
first_9_sums = [x+y for x, y in first_9]
print(f"   Summen: {first_9_sums}")
print(f"   Gesamtsumme: {sum(first_9_sums)}")

# Interessant: Diese 9 Summen als Base58
first_9_b58 = ''.join([base58[s % 58] for s in first_9_sums])
print(f"   Als Base58: {first_9_b58}")

# Die letzte Interpretation: Vielleicht ist das ein Qubic Seed?
print("\n10. QUBIC SEED INTERPRETATION:")
# Qubic Seeds sind 55 Zeichen aus A-Z (Großbuchstaben)
# Wir haben 20 Koordinatenpaare = 40 Zahlen

# X+Y mod 26 + A für Großbuchstaben
qubic_seed = ''.join([chr((x+y) % 26 + 65) for x, y in coords])
print(f"   X+Y als Buchstaben: {qubic_seed} ({len(qubic_seed)} Zeichen)")

# Erweitere auf 55 durch Wiederholung
if len(qubic_seed) < 55:
    extended = (qubic_seed * 3)[:55]
    print(f"   Erweitert auf 55: {extended}")

# Alle Zahlen einzeln als Buchstaben
all_letters = ''.join([chr(n % 26 + 65) for n in numbers])
print(f"   Alle 40 als Buchstaben: {all_letters}")

# Finale Zusammenfassung
print("\n" + "=" * 70)
print("FINALE ZUSAMMENFASSUNG")
print("=" * 70)
print("""
Die Struktur des CFB-Rätsels:
============================
- 40 Zahlen = 20 Koordinatenpaare
- Paar 1: (45, 92) = 137 (Feinstrukturkonstante) - ANFANG
- Paar 20: (82, 39) = 121 (11² = CFB²) - ENDE

CFB x CFB = 9 erklärt:
=====================
- CFB = {C, F, B} = {3, 6, 2} (Alphabet-Positionen)
- C + F + B = 11, daher CFB² = 121
- Das kartesische Produkt hat 9 Elemente
- 36 "Inhaltszahlen" = 3 * 6 * 2 = CFB-Produkt

Die 137/121 Rahmenstruktur:
==========================
- 137 = Feinstrukturkonstante (fundamentale Physikkonstante)
- 121 = 11² = perfektes Quadrat
- Diese rahmen den Inhalt ein

Wichtigste dekodierte Strings:
=============================
""")

# Zeige die wichtigsten Ergebnisse
results = {
    "coordinates": coords,
    "x_letters": result_x,
    "y_letters": result_y,
    "xy_letters": result_xy,
    "xor_letters": result_xor,
    "qubic_seed_attempt": all_letters,
    "first_9_sums": first_9_sums,
    "structure": {
        "prefix": coords[0],
        "prefix_sum": 137,
        "suffix": coords[-1],
        "suffix_sum": 121
    }
}

print(f"   X-Koordinaten als Buchstaben: {result_x}")
print(f"   Y-Koordinaten als Buchstaben: {result_y}")
print(f"   X+Y mod 26: {result_xy}")
print(f"   X XOR Y mod 26: {result_xor}")
print(f"   Alle 40 als Buchstaben: {all_letters}")

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_PUZZLE_FINAL_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\n\nErgebnisse gespeichert!")
