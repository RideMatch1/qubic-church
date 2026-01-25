#!/usr/bin/env python3
"""
Tiefere CFB Puzzle Analyse - CFB x CFB = CFB^9

Wichtige Erkenntnisse aus erster Analyse:
- 40 Zahlen total
- XOR aller Zahlen = 1
- 137 und 121 als Marker-Summen (mehrfach!)
- Zahlen durch 9 teilbar: 45, 81, 9, 72, 27
"""

import json

numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

print("=" * 70)
print("CFB x CFB = CFB^9 - TIEFE ANALYSE")
print("=" * 70)

# Lade Anna-Matrix mit korrektem Key-Format
print("\n1. ANNA-MATRIX MIT LAYER-KEYS:")
try:
    with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json', 'r') as f:
        anna_data = json.load(f)

    # Prüfe das Key-Format
    sample_keys = list(anna_data.keys())[:5]
    print(f"   Beispiel-Keys: {sample_keys}")

    # Versuche verschiedene Key-Formate
    for layer in range(10):
        for i in range(0, len(numbers)-1, 2):
            row, col = numbers[i], numbers[i+1]
            key = f"{layer},{row},{col}"
            if key in anna_data:
                cell = anna_data[key]
                print(f"   GEFUNDEN! Layer {layer}: ({row},{col}) = {cell}")
                break
        else:
            continue
        break

except Exception as e:
    print(f"   Fehler: {e}")

# CFB als Zahlen - verschiedene Interpretationen
print("\n2. CFB NUMERISCHE INTERPRETATIONEN:")
# C=67, F=70, B=66 (ASCII)
# C=3, F=6, B=2 (Alphabet Position)
# CFB könnte auch 362 sein (C=3, F=6, B=2 zusammen)

cfb_362 = 362
cfb_cfb = cfb_362 * cfb_362  # CFB x CFB als Multiplikation
print(f"   CFB als 362: {cfb_362}")
print(f"   CFB x CFB = 362² = {cfb_cfb}")
print(f"   CFB^9 = 362^9 = {362**9}")

# Was wenn CFB die Summe C+F+B ist?
cfb_sum = 3 + 6 + 2  # = 11
print(f"\n   CFB als Summe (3+6+2) = {cfb_sum}")
print(f"   CFB x CFB = 11 x 11 = 121")  # Das ist das Suffix-Pattern!
print(f"   ⭐ 121 = 82 + 39 (letzte zwei Zahlen)")

# C=3, F=6, B=2 → CFB^9 könnte 11^9 bedeuten?
print(f"   11^9 = {11**9}")  # Sehr große Zahl

# Oder CFB als Produkt: 3 * 6 * 2 = 36
cfb_prod = 3 * 6 * 2
print(f"\n   CFB als Produkt (3*6*2) = {cfb_prod}")
print(f"   Wir haben 36 Zahlen zwischen Prefix und Suffix!")

# DIE VERBINDUNG!
print("\n" + "=" * 70)
print("⭐ MÖGLICHE LÖSUNG GEFUNDEN!")
print("=" * 70)
print("""
   CFB = 3, 6, 2 (Alphabet-Positionen von C, F, B)
   CFB als Summe = 3 + 6 + 2 = 11
   CFB x CFB = 11 x 11 = 121 (= letzte zwei Zahlen: 82 + 39!)
   CFB als Produkt = 3 * 6 * 2 = 36 (= Anzahl Zahlen zwischen Prefix/Suffix!)

   Die Zahlenfolge ist strukturiert als:
   - PREFIX: 45, 92 (= 137, Feinstrukturkonstante)
   - INHALT: 36 Zahlen (= C * F * B = 3 * 6 * 2)
   - SUFFIX: 82, 39 (= 121 = CFB x CFB = 11 x 11)
""")

# Analysiere die 36 Inhaltszahlen genauer
content = numbers[2:-2]
print(f"\n3. DIE 36 INHALTSZAHLEN (3*6*2 = CFB-Produkt):")
print(f"   {content}")

# 36 = 6 x 6, könnte eine 6x6 Matrix sein
print("\n   Als 6x6 Matrix:")
for i in range(6):
    row = content[i*6:(i+1)*6]
    print(f"   {row}")

# Summen der Zeilen und Spalten
print("\n   Zeilensummen:")
for i in range(6):
    row = content[i*6:(i+1)*6]
    print(f"   Zeile {i}: {sum(row)}")

# Transponierte Matrix für Spaltensummen
print("\n   Spaltensummen:")
for j in range(6):
    col = [content[i*6+j] for i in range(6)]
    print(f"   Spalte {j}: {sum(col)}")

# Diagonalen
print("\n   Diagonalen:")
diag1 = [content[i*6+i] for i in range(6)]
diag2 = [content[i*6+(5-i)] for i in range(6)]
print(f"   Hauptdiagonale: {diag1} = {sum(diag1)}")
print(f"   Nebendiagonale: {diag2} = {sum(diag2)}")

# CFB^9 - könnte 9 spezielle Positionen markieren
print("\n4. CFB^9 = 9 SPEZIELLE POSITIONEN:")
# Im kartesischen Produkt {C,F,B} x {C,F,B} gibt es 9 Paare:
# (C,C), (C,F), (C,B), (F,C), (F,F), (F,B), (B,C), (B,F), (B,B)
# Mit C=3, F=6, B=2:
pairs = [
    (3,3), (3,6), (3,2),
    (6,3), (6,6), (6,2),
    (2,3), (2,6), (2,2)
]
print(f"   CFB x CFB Paare (mit C=3,F=6,B=2): {pairs}")

# Diese Koordinaten in der 6x6 Matrix (0-indexed)
print("\n   Werte an diesen Positionen in der 6x6 Matrix:")
for row_idx, col_idx in pairs:
    if row_idx < 6 and col_idx < 6:
        idx = row_idx * 6 + col_idx
        if idx < 36:
            val = content[idx]
            print(f"   ({row_idx},{col_idx}): {val}")
        else:
            print(f"   ({row_idx},{col_idx}): Index {idx} außerhalb")
    else:
        print(f"   ({row_idx},{col_idx}): Außerhalb der 6x6 Matrix")

# Sammle die 9 Werte
valid_values = []
for row_idx, col_idx in pairs:
    if row_idx < 6 and col_idx < 6:
        idx = row_idx * 6 + col_idx
        if idx < 36:
            valid_values.append(content[idx])
print(f"\n   Die 9 CFB^9 Werte: {valid_values}")
print(f"   Summe: {sum(valid_values)}")

# Als ASCII
print(f"   Als ASCII: {''.join([chr(v) if 32<=v<=126 else '?' for v in valid_values])}")

# Weitere Interpretationen
print("\n5. WEITERE PATTERN-ANALYSE:")

# Die Zahlen 137 und 121 als Schlüssel
print(f"\n   137 = Feinstrukturkonstante (1/α ≈ 137.036)")
print(f"   121 = 11² = CFB x CFB (wenn CFB = 3+6+2 = 11)")
print(f"   137 - 121 = 16 = 4²")
print(f"   137 + 121 = 258 = 2 * 129")

# Finde alle Zahlen-Kombinationen die 137 oder 121 ergeben
print("\n   Nicht-aufeinanderfolgende Paare mit Summe 137:")
for i in range(len(numbers)):
    for j in range(i+2, len(numbers)):  # Nicht aufeinanderfolgend
        if numbers[i] + numbers[j] == 137:
            print(f"   ({i},{j}): {numbers[i]} + {numbers[j]} = 137")

print("\n   Nicht-aufeinanderfolgende Paare mit Summe 121:")
for i in range(len(numbers)):
    for j in range(i+2, len(numbers)):
        if numbers[i] + numbers[j] == 121:
            print(f"   ({i},{j}): {numbers[i]} + {numbers[j]} = 121")

# Die durch 9 teilbaren Zahlen: 45, 81, 9, 72, 27
print("\n6. ZAHLEN TEILBAR DURCH 9:")
div9 = [(i, n) for i, n in enumerate(numbers) if n % 9 == 0]
print(f"   {div9}")
div9_values = [n for _, n in div9]
print(f"   Summe: {sum(div9_values)}")
print(f"   Produkt/9: {45*81*9*72*27 // 9}")

# Die Zahl 27 ist besonders interessant (3^3)
print(f"\n   27 = 3³ (Kubikzahl)")
print(f"   81 = 3⁴ (Potenz von 3)")
print(f"   9 = 3² (Potenz von 3)")
print(f"   45 = 9 * 5 = 3² * 5")
print(f"   72 = 8 * 9 = 2³ * 3²")

# Alle Potenzen von 3 in der Sequenz
powers_of_3 = [3, 9, 27, 81]
print(f"\n   Potenzen von 3 in der Sequenz:")
for p in powers_of_3:
    if p in numbers:
        idx = numbers.index(p)
        print(f"   3^{powers_of_3.index(p)+1} = {p} an Position {idx}")

# Die 3er-Potenz-Sequenz: 3, 9, 27, 81
# Positionen: 2, 15, 37, 7
positions_3pow = [numbers.index(p) for p in powers_of_3 if p in numbers]
print(f"   Positionen: {positions_3pow}")

# Bilden diese Positionen selbst ein Muster?
print(f"   Position-Differenzen: {[positions_3pow[i+1]-positions_3pow[i] for i in range(len(positions_3pow)-1)]}")

# Die Summe 1973
print("\n7. DIE SUMME 1973:")
print(f"   Summe aller Zahlen = 1973")
print(f"   1973 ist eine Primzahl: {all(1973 % i != 0 for i in range(2, int(1973**0.5)+1))}")
print(f"   1973 könnte ein Jahr sein...")
print(f"   1973 + 137 = 2110")
print(f"   1973 - 121 = 1852")
print(f"   1973 mod 137 = {1973 % 137}")
print(f"   1973 mod 121 = {1973 % 121}")

# CFB Geburtstag/Wichtiges Datum?
print(f"\n   Wichtige Daten 1973:")
print(f"   - Ethernet erfunden")
print(f"   - Unix Zeit begann 1970")
print(f"   - Qubic-Bezug?")

# Final: Versuche eine Bitcoin-Adresse zu konstruieren
print("\n8. FINALE BITCOIN-ADRESS-KONSTRUKTION:")
base58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Die 36 Inhaltszahlen als Indizes in Base58
content_b58 = ""
for n in content:
    if 0 <= n < 58:
        content_b58 += base58[n]
    elif n >= 58:
        # Modulo 58
        content_b58 += base58[n % 58]
print(f"   Inhalt (36 Zahlen) als Base58: {content_b58}")

# Mit der CFB^9 Extraktion (9 Werte)
cfb9_b58 = ""
for v in valid_values:
    if 0 <= v < 58:
        cfb9_b58 += base58[v]
    else:
        cfb9_b58 += base58[v % 58]
print(f"   CFB^9 (9 Werte) als Base58: {cfb9_b58}")

# Vielleicht sind die Zahlen Positionen in einem bekannten String?
print("\n9. QUBIC ID VERSUCH (55 Zeichen, A-Z):")
qubic_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# Die ersten 26 Zahlen für 26 Buchstaben, dann wiederholen
qubic_id = ""
for n in numbers[:55]:
    qubic_id += qubic_alphabet[n % 26]
print(f"   Als Qubic-ähnliche ID: {qubic_id}")

print("\n" + "=" * 70)
print("ZUSAMMENFASSUNG")
print("=" * 70)
print("""
Die Struktur des Rätsels:
========================
PREFIX:  45 + 92 = 137 (Feinstrukturkonstante)
INHALT:  36 Zahlen (= 3 * 6 * 2 = CFB-Produkt)
SUFFIX:  82 + 39 = 121 (= 11² = CFB x CFB)

CFB x CFB Interpretation:
========================
C = 3, F = 6, B = 2 (Alphabet-Positionen)
CFB-Summe = 11, daher CFB x CFB = 121
CFB-Produkt = 36 (Anzahl der Inhaltszahlen)

Die 9 Koordinaten aus dem kartesischen Produkt:
(3,3), (3,6), (3,2), (6,3), (6,6), (6,2), (2,3), (2,6), (2,2)

Extrahierte 9 Werte: """ + str(valid_values) + """

Potenzen von 3 in der Sequenz:
3¹=3, 3²=9, 3³=27, 3⁴=81 - alle vorhanden!
""")

# Speichere die Ergebnisse
results = {
    "prefix_sum": 137,
    "suffix_sum": 121,
    "content_count": 36,
    "cfb_product": 36,
    "cfb_sum_squared": 121,
    "cfb9_values": valid_values,
    "cfb9_positions": pairs,
    "powers_of_3": {"3": 2, "9": 15, "27": 37, "81": 7},
    "total_sum": 1973,
    "content_as_6x6": [content[i*6:(i+1)*6] for i in range(6)]
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_PUZZLE_DEEP_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nErgebnisse gespeichert!")
