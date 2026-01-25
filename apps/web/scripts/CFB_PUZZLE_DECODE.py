#!/usr/bin/env python3
"""
CFB Puzzle Decoder - Analysiert die Zahlenfolge und den CFB x CFB Hinweis

Die Zahlenfolge: 45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39

Beobachtungen:
- 45 + 92 = 137 (Feinstrukturkonstante!)
- 82 + 39 = 121 (11² - Ende)
- CFB x CFB = 9 Elemente (kartesisches Produkt)
"""

import json
import hashlib

# Die Zahlenfolge
numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

results = {
    "basic_analysis": {},
    "decode_attempts": [],
    "cfb_connection": {},
    "matrix_interpretations": []
}

# Basis-Analyse
print("=" * 60)
print("CFB PUZZLE DECODER")
print("=" * 60)

print(f"\n1. GRUNDLEGENDE ANALYSE:")
print(f"   Anzahl Zahlen: {len(numbers)}")
print(f"   Summe aller Zahlen: {sum(numbers)}")
print(f"   Min: {min(numbers)}, Max: {max(numbers)}")

results["basic_analysis"] = {
    "count": len(numbers),
    "sum": sum(numbers),
    "min": min(numbers),
    "max": max(numbers),
    "numbers": numbers
}

# Beobachtungen des Users verifizieren
print(f"\n2. USER-BEOBACHTUNGEN VERIFIZIEREN:")
print(f"   Erste zwei: {numbers[0]} + {numbers[1]} = {numbers[0] + numbers[1]} (erwartet: 137)")
print(f"   Letzte zwei: {numbers[-2]} + {numbers[-1]} = {numbers[-2] + numbers[-1]} (erwartet: 121 = 11²)")
print(f"   Dritte Zahl: {numbers[2]} (nach dem 'prefix')")
print(f"   38. Zahl: {numbers[37]} (27 vor dem 'suffix')")

# Prüfe aufeinanderfolgende Paare die 137 oder 121 ergeben
print(f"\n3. PAARE MIT SUMME 137 oder 121:")
for i in range(len(numbers) - 1):
    s = numbers[i] + numbers[i+1]
    if s == 137:
        print(f"   Position {i},{i+1}: {numbers[i]} + {numbers[i+1]} = 137")
    if s == 121:
        print(f"   Position {i},{i+1}: {numbers[i]} + {numbers[i+1]} = 121")

# CFB x CFB = 9 - Interpretation
print(f"\n4. CFB x CFB INTERPRETATION:")
print(f"   CFB hat 3 Buchstaben: C, F, B")
print(f"   Kartesisches Produkt: 3 x 3 = 9 Elemente")
print(f"   CFB^9 = CFB in der 9. Potenz?")

# CFB als Zahlen
cfb_ascii = [ord('C'), ord('F'), ord('B')]  # 67, 70, 66
cfb_alpha = [3, 6, 2]  # Position im Alphabet
cfb_hex = 0xCFB  # 3323 dezimal

print(f"   CFB ASCII: {cfb_ascii}")
print(f"   CFB Alphabet-Position: {cfb_alpha}")
print(f"   CFB als Hex (0xCFB): {cfb_hex}")

results["cfb_connection"] = {
    "cfb_ascii": cfb_ascii,
    "cfb_alphabet": cfb_alpha,
    "cfb_hex": cfb_hex,
    "cartesian_product_size": 9
}

# Methode 1: Zahlen als Matrix 8x5 (40 Zahlen)
print(f"\n5. MATRIX-INTERPRETATION (8x5):")
matrix_8x5 = [numbers[i:i+5] for i in range(0, 40, 5)]
for i, row in enumerate(matrix_8x5):
    print(f"   Zeile {i}: {row}")

# Methode 2: Zahlen als Matrix 5x8
print(f"\n6. MATRIX-INTERPRETATION (5x8):")
matrix_5x8 = [numbers[i:i+8] for i in range(0, 40, 8)]
for i, row in enumerate(matrix_5x8):
    print(f"   Zeile {i}: {row}")

# Methode 3: Zahlen als Koordinaten in Anna-Matrix (100x100)
print(f"\n7. ALS KOORDINATEN (Paare):")
coordinates = [(numbers[i], numbers[i+1]) for i in range(0, len(numbers)-1, 2)]
print(f"   {len(coordinates)} Koordinatenpaare:")
for i, (x, y) in enumerate(coordinates):
    print(f"   Paar {i+1}: ({x}, {y})")

# Methode 4: Zahlen als ASCII-Zeichen
print(f"\n8. ALS ASCII-ZEICHEN:")
ascii_chars = ""
for n in numbers:
    if 32 <= n <= 126:
        ascii_chars += chr(n)
    else:
        ascii_chars += "?"
print(f"   Direkt: {ascii_chars}")

# Mit Offset 32
ascii_offset32 = ""
for n in numbers:
    c = n + 32
    if 32 <= c <= 126:
        ascii_offset32 += chr(c)
    else:
        ascii_offset32 += "?"
print(f"   +32 Offset: {ascii_offset32}")

# Mit Offset 64 (A=65)
ascii_offset64 = ""
for n in numbers:
    c = n + 64
    if 32 <= c <= 126:
        ascii_offset64 += chr(c)
    elif c > 126:
        ascii_offset64 += chr((c - 65) % 26 + 65)  # Wrap around
    else:
        ascii_offset64 += "?"
print(f"   +64 Offset: {ascii_offset64}")

# Methode 5: Modulo-Operationen (26 für Alphabet, 10 für Ziffern)
print(f"\n9. MODULO-OPERATIONEN:")
mod26 = [n % 26 for n in numbers]
mod10 = [n % 10 for n in numbers]
mod_alphabet = ''.join([chr(n % 26 + 65) for n in numbers])
print(f"   Mod 26: {mod26}")
print(f"   Als Buchstaben (A=0): {mod_alphabet}")
print(f"   Mod 10: {mod10}")
print(f"   Als Zahl: {''.join(map(str, mod10))}")

# Methode 6: CFB^9 = 9x9 Matrix? (aber wir haben 40 Zahlen)
# Vielleicht sind nur bestimmte Zahlen relevant
print(f"\n10. CFB^9 - MÖGLICHE INTERPRETATIONEN:")

# 9 Elemente aus den 40 extrahieren?
# Jede 4. Zahl (40/9 ≈ 4.4)
every_4th = numbers[::4][:9]
print(f"    Jede 4. Zahl (erste 9): {every_4th}")

# Summe aller Zahlen mod 9
sum_mod9 = sum(numbers) % 9
print(f"    Summe mod 9: {sum_mod9}")

# Die Zahlen die durch 9 teilbar sind
div_by_9 = [n for n in numbers if n % 9 == 0]
print(f"    Durch 9 teilbar: {div_by_9}")

# Methode 7: Base58 Dekodierung (Bitcoin-Adressformat)
print(f"\n11. BASE58 INTERPRETATION:")
base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
# Zahlen als Index in Base58
base58_chars = ""
for n in numbers:
    if 0 <= n < 58:
        base58_chars += base58_alphabet[n]
    else:
        base58_chars += "?"  # Außerhalb des Bereichs
print(f"    Als Base58: {base58_chars}")

# Methode 8: Die Zahlen sortieren und als Index nutzen
print(f"\n12. SORTIERTE REIHENFOLGE:")
sorted_with_index = sorted(enumerate(numbers), key=lambda x: x[1])
sorted_indices = [i for i, _ in sorted_with_index]
print(f"    Sortierte Indizes: {sorted_indices[:20]}...")

# Vielleicht ist die Position in der sortierten Reihenfolge der Schlüssel
# Index der Zahl in sortierter Reihenfolge
position_in_sorted = [0] * 40
for rank, (orig_idx, _) in enumerate(sorted_with_index):
    position_in_sorted[orig_idx] = rank
print(f"    Position jeder Zahl nach Sortierung: {position_in_sorted[:20]}...")

# Methode 9: Differenzen zwischen aufeinanderfolgenden Zahlen
print(f"\n13. DIFFERENZEN (erste 20):")
diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
print(f"    {diffs[:20]}...")
print(f"    Als positive Werte: {[abs(d) for d in diffs[:20]]}...")

# Methode 10: XOR-Operationen
print(f"\n14. XOR-OPERATIONEN:")
xor_consecutive = [numbers[i] ^ numbers[i+1] for i in range(len(numbers)-1)]
print(f"    XOR aufeinanderfolgende (erste 10): {xor_consecutive[:10]}")

# XOR aller Zahlen
xor_all = numbers[0]
for n in numbers[1:]:
    xor_all ^= n
print(f"    XOR aller Zahlen: {xor_all}")

# Methode 11: Die 137 und 121 Grenzen - extrahiere den "Inhalt"
print(f"\n15. INHALT ZWISCHEN PREFIX UND SUFFIX:")
# Prefix: 45, 92 (=137), Suffix: 82, 39 (=121)
# Die 36 Zahlen dazwischen (3 bis 72+27)
content = numbers[2:-2]  # Zahlen 3 bis 27 (ohne 82, 39)
print(f"    Anzahl Inhaltszahlen: {len(content)}")
print(f"    Inhalt: {content}")

# Als Base58
content_base58 = ""
for n in content:
    if 0 <= n < 58:
        content_base58 += base58_alphabet[n]
    else:
        content_base58 += "?"
print(f"    Inhalt als Base58: {content_base58}")

# Methode 12: Anna-Matrix Koordinaten
print(f"\n16. ANNA-MATRIX KOORDINATEN LOOKUP:")
print("    Lade Anna-Matrix...")

try:
    with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json', 'r') as f:
        anna_data = json.load(f)

    # Koordinatenpaare in Matrix nachschlagen
    anna_cells = []
    for i in range(0, len(numbers)-1, 2):
        row, col = numbers[i], numbers[i+1]
        if 0 <= row < 100 and 0 <= col < 100:
            key = f"{row},{col}"
            if key in anna_data:
                cell = anna_data[key]
                anna_cells.append({
                    "coords": (row, col),
                    "value": cell.get("value"),
                    "xor": cell.get("xor"),
                    "text": cell.get("text", "")[:50]
                })
                print(f"    ({row},{col}): value={cell.get('value')}, xor={cell.get('xor')}")
            else:
                print(f"    ({row},{col}): NICHT IN MATRIX")
        else:
            print(f"    ({row},{col}): AUSSERHALB (0-99)")

    results["matrix_interpretations"].append({
        "method": "anna_matrix_coordinates",
        "cells": anna_cells
    })

except Exception as e:
    print(f"    Fehler beim Laden: {e}")

# Methode 13: 9er-Gruppierung (CFB x CFB)
print(f"\n17. 9ER-GRUPPIERUNG (CFB x CFB):")
# Teile die 40 Zahlen in Gruppen
groups_of_9 = []
for i in range(0, 36, 9):
    group = numbers[i:i+9]
    groups_of_9.append(group)
    print(f"    Gruppe {i//9 + 1}: {group} (Summe: {sum(group)})")
print(f"    Rest: {numbers[36:]}")

# Methode 14: Produkt (CFB x CFB könnte Multiplikation bedeuten)
print(f"\n18. PAAR-PRODUKTE:")
products = []
for i in range(0, len(numbers)-1, 2):
    p = numbers[i] * numbers[i+1]
    products.append(p)
print(f"    Produkte: {products}")
print(f"    Summe der Produkte: {sum(products)}")

# Methode 15: Hex-Interpretation
print(f"\n19. HEX-INTERPRETATION:")
# Paare als Hex-Bytes
hex_pairs = []
for i in range(0, len(numbers)-1, 2):
    hex_byte = (numbers[i] << 8) | numbers[i+1]
    hex_pairs.append(hex_byte)
print(f"    Als 16-bit Werte: {[hex(h) for h in hex_pairs[:10]]}...")

# Einzelne Zahlen als Hex
single_hex = ''.join([f'{n:02x}' for n in numbers])
print(f"    Als Hex-String: {single_hex}")

# Methode 16: Bitcoin-Adress-Konstruktion
print(f"\n20. BITCOIN-ADRESS-VERSUCH:")
# 34 Zeichen für BTC-Adresse
# Die ersten 34 Zahlen als Base58
btc_attempt = ""
for n in numbers[:34]:
    if 0 <= n < 58:
        btc_attempt += base58_alphabet[n]
    else:
        btc_attempt += "?"
print(f"    Erste 34 als Base58: {btc_attempt}")

# Mit 1 am Anfang (Legacy BTC)
btc_with_1 = "1" + btc_attempt[:33]
print(f"    Mit '1' Prefix: {btc_with_1}")

# Methode 17: Die Zahlen könnten Positionen sein
print(f"\n21. POSITION-IN-ALPHABET/BASE58:")
# Was wenn die Zahlen uns sagen, welche Position in einer Sequenz zu nehmen ist?
# Beispiel: Position in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
pos_result = ""
for n in numbers:
    if 0 <= n < len(alphanumeric):
        pos_result += alphanumeric[n]
    else:
        pos_result += "?"
print(f"    Alphanumerisch: {pos_result}")

# Speichere Ergebnisse
results["decode_attempts"] = [
    {"method": "direct_ascii", "result": ascii_chars},
    {"method": "ascii_offset32", "result": ascii_offset32},
    {"method": "mod26_alphabet", "result": mod_alphabet},
    {"method": "base58", "result": base58_chars},
    {"method": "content_base58", "result": content_base58},
    {"method": "btc_attempt", "result": btc_attempt},
    {"method": "alphanumeric", "result": pos_result},
]

# Zusammenfassung
print(f"\n" + "=" * 60)
print("ZUSAMMENFASSUNG DER WICHTIGSTEN ERKENNTNISSE:")
print("=" * 60)
print(f"1. 45 + 92 = 137 (Feinstrukturkonstante) ✓")
print(f"2. 82 + 39 = 121 (11²) ✓")
print(f"3. 40 Zahlen total (nicht 34 wie für BTC-Adresse)")
print(f"4. Summe aller Zahlen: {sum(numbers)}")
print(f"5. CFB x CFB = 9 (kartesisches Produkt)")
print(f"6. Interessante Base58-Dekodierung: {base58_chars[:40]}")

# Speichere
output_path = '/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_PUZZLE_RESULTS.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nErgebnisse gespeichert: {output_path}")
