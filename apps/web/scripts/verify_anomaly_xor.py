#!/usr/bin/env python3
"""
VERIFIZIERE XOR DER 68 ANOMALIE-ZELLEN
======================================
Die echten 34 Anomalien aus der Anna Matrix (68 Zellen total).
"""

import json

# Die echten Anomalien aus ANOMALY_68_ANALYSIS.json
anomalies = [
    {"pos": [19, 127], "value": 15, "mirror_value": -48},
    {"pos": [20, 22], "value": 92, "mirror_value": -18},
    {"pos": [21, 22], "value": 113, "mirror_value": -58},
    {"pos": [22, 22], "value": 100, "mirror_value": 100},  # Selbst-Spiegelung!
    {"pos": [23, 22], "value": -121, "mirror_value": -26},
    {"pos": [24, 22], "value": 42, "mirror_value": 74},
    {"pos": [25, 22], "value": 23, "mirror_value": 66},
    {"pos": [26, 22], "value": 106, "mirror_value": 100},
    {"pos": [27, 22], "value": 120, "mirror_value": 70},
    {"pos": [28, 22], "value": 40, "mirror_value": 110},
    {"pos": [29, 22], "value": -121, "mirror_value": -50},
    {"pos": [30, 22], "value": 44, "mirror_value": 110},
    {"pos": [31, 22], "value": 120, "mirror_value": 102},
    {"pos": [32, 22], "value": 101, "mirror_value": -108},
    {"pos": [48, 97], "value": 14, "mirror_value": -16},
    {"pos": [50, 97], "value": -114, "mirror_value": -15},
    {"pos": [51, 97], "value": 14, "mirror_value": 113},
    {"pos": [53, 97], "value": 30, "mirror_value": -15},
    {"pos": [54, 97], "value": 10, "mirror_value": -31},
    {"pos": [55, 97], "value": 26, "mirror_value": -11},
    {"pos": [56, 97], "value": -114, "mirror_value": -27},  # -27 erscheint!
    {"pos": [57, 97], "value": 30, "mirror_value": 113},
    {"pos": [58, 97], "value": -114, "mirror_value": -31},
    {"pos": [59, 97], "value": -98, "mirror_value": 113},
    {"pos": [60, 30], "value": 81, "mirror_value": 46},
    {"pos": [60, 97], "value": 22, "mirror_value": 97},
    {"pos": [61, 30], "value": -45, "mirror_value": -82},
    {"pos": [61, 97], "value": 30, "mirror_value": -23},
    {"pos": [62, 30], "value": -47, "mirror_value": 44},
    {"pos": [62, 41], "value": -101, "mirror_value": 109},
    {"pos": [62, 97], "value": -102, "mirror_value": -31},
    {"pos": [63, 30], "value": -27, "mirror_value": 46},  # -27 erscheint!
    {"pos": [63, 41], "value": -101, "mirror_value": 109},
    {"pos": [63, 97], "value": 26, "mirror_value": 101},
]

print("=" * 80)
print("VERIFIZIERE XOR DER 68 ANOMALIE-ZELLEN")
print("=" * 80)

# Alle Werte extrahieren
all_values = []
for a in anomalies:
    all_values.append(a['value'])
    if a['pos'] != [22, 22]:  # Selbst-Spiegelung nicht doppelt zählen
        all_values.append(a['mirror_value'])

print(f"\nAnzahl Anomalien: {len(anomalies)}")
print(f"Anzahl Zellen (mit Spiegeln): {len(all_values)}")
print()

# XOR METHODE 1: Alle Werte direkt (als signed int8 → unsigned)
def to_unsigned_byte(val):
    if val < 0:
        return (256 + val) % 256
    return val % 256

print("METHODE 1: XOR aller Werte (als unsigned bytes)")
xor1 = 0
for v in all_values:
    xor1 ^= to_unsigned_byte(v)
print(f"  XOR = {xor1}")
if 32 <= xor1 <= 126:
    print(f"  ASCII = '{chr(xor1)}'")
print()

# XOR METHODE 2: Nur Original-Werte (keine Spiegel)
print("METHODE 2: XOR nur Original-Werte (34 Werte)")
xor2 = 0
for a in anomalies:
    xor2 ^= to_unsigned_byte(a['value'])
print(f"  XOR = {xor2}")
if 32 <= xor2 <= 126:
    print(f"  ASCII = '{chr(xor2)}'")
print()

# XOR METHODE 3: Nur Spiegel-Werte
print("METHODE 3: XOR nur Spiegel-Werte")
xor3 = 0
for a in anomalies:
    xor3 ^= to_unsigned_byte(a['mirror_value'])
print(f"  XOR = {xor3}")
if 32 <= xor3 <= 126:
    print(f"  ASCII = '{chr(xor3)}'")
print()

# XOR METHODE 4: Summen der Paare
print("METHODE 4: XOR der Summen (value + mirror_value)")
sums = [a['value'] + a['mirror_value'] for a in anomalies]
xor4 = 0
for s in sums:
    xor4 ^= to_unsigned_byte(s)
print(f"  Summen: {sums[:10]}...")
print(f"  XOR = {xor4}")
if 32 <= xor4 <= 126:
    print(f"  ASCII = '{chr(xor4)}'")
print()

# XOR METHODE 5: Positionen
print("METHODE 5: XOR aller Positionen")
xor_rows = 0
xor_cols = 0
for a in anomalies:
    xor_rows ^= a['pos'][0]
    xor_cols ^= a['pos'][1]
print(f"  XOR Rows = {xor_rows}")
print(f"  XOR Cols = {xor_cols}")
print(f"  XOR(Rows) ^ XOR(Cols) = {xor_rows ^ xor_cols}")
if 32 <= (xor_rows ^ xor_cols) <= 126:
    print(f"  ASCII = '{chr(xor_rows ^ xor_cols)}'")
print()

# Suche nach 61
print("SUCHE NACH 61 (= ASCII '='):")
print("-" * 60)

# Subsets
for i, a in enumerate(anomalies):
    test_xor = 0
    for j, b in enumerate(anomalies):
        if j != i:
            test_xor ^= to_unsigned_byte(b['value'])
    if test_xor == 61:
        print(f"  Ohne Anomalie {i} (Pos {a['pos']}, Val {a['value']}): XOR = 61!")

# Versuche verschiedene Kombinationen
print("\nAndere interessante XOR-Werte:")
interesting = [11, 27, 33, 61, 83, 89, 121, 127, 137]
for target in interesting:
    for i, a in enumerate(anomalies):
        test_xor = 0
        for j, b in enumerate(anomalies):
            if j <= i:
                test_xor ^= to_unsigned_byte(b['value'])
        if test_xor == target:
            print(f"  XOR der ersten {i+1} Werte = {target}" + (f" = '{chr(target)}'" if 32 <= target <= 126 else ""))
            break

print()
print("=" * 80)
print("ANALYSE DER CFB-SIGNATUREN IN ANOMALIEN")
print("=" * 80)

# Zähle CFB-Signaturen
cfb_vals = {-27: 0, -121: 0, 100: 0, 121: 0, 37: 0, 73: 0, 127: 0}
for v in all_values:
    if v in cfb_vals:
        cfb_vals[v] += 1

print("\nCFB-Signaturen in Anomalien:")
for val, count in cfb_vals.items():
    if count > 0:
        print(f"  {val:4}: {count}× {'⭐ CFB!' if val in [-27, 121, 100] else ''}")

# Einzigartige Werte
unique = sorted(set(all_values))
print(f"\nEinzigartige Werte ({len(unique)}): {unique}")

# Summen-Analyse
total_sum = sum(all_values)
print(f"\nSumme aller Werte: {total_sum}")
print(f"Summe mod 127: {total_sum % 127}")
print(f"Summe mod 137: {total_sum % 137}")
print(f"Summe mod 11: {total_sum % 11}")

# Speichern
results = {
    'anomaly_count': len(anomalies),
    'total_cells': len(all_values),
    'xor_all_unsigned': xor1,
    'xor_originals_only': xor2,
    'xor_mirrors_only': xor3,
    'xor_sums': xor4,
    'xor_rows': xor_rows,
    'xor_cols': xor_cols,
    'unique_values': unique,
    'total_sum': total_sum,
    'cfb_signatures_found': {k: v for k, v in cfb_vals.items() if v > 0}
}

with open('ANOMALY_XOR_VERIFIED.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nGespeichert: ANOMALY_XOR_VERIFIED.json")
