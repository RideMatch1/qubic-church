#!/usr/bin/env python3
"""
CFB Puzzle - Permutation und Modulo Analyse

Die Zahlen 58+ sind außerhalb des Base58-Bereichs.
Neue Ideen:
1. Die Zahlen als Permutation (Reihenfolge zum Lesen)
2. Modulo-Operationen
3. Die Zahlen als Zeiger in einen bekannten Text
"""

import json
import hashlib

numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

print("=" * 70)
print("CFB PUZZLE - PERMUTATION & MODULO ANALYSE")
print("=" * 70)

# 1. Modulo 58 für Base58
print("\n1. MODULO 58 FÜR BASE58:")
mod58 = [n % 58 for n in numbers]
base58_mod = ''.join([base58_alphabet[m] for m in mod58])
print(f"   Mod 58 Werte: {mod58}")
print(f"   Als Base58: {base58_mod}")

# Die 36 Inhaltszahlen mit Mod 58
content = numbers[2:-2]
content_mod58 = [n % 58 for n in content]
content_b58 = ''.join([base58_alphabet[m] for m in content_mod58])
print(f"\n   Inhalt (36) mod 58: {content_mod58}")
print(f"   Als Base58: {content_b58}")

# 2. Die Zahlen könnten Positionen sein - sortiert
print("\n2. PERMUTATION - SORTIERUNG:")
# Jede Zahl könnte sagen: "Nimm das Zeichen an dieser Position"
# Sortieren wir die Zahlen und schauen, welche Indizes sie in der sortierten Reihenfolge haben

# Rang jeder Zahl in der sortierten Reihenfolge
sorted_with_orig_idx = sorted(enumerate(numbers), key=lambda x: x[1])
rank_of_number = [0] * 40
for rank, (orig_idx, _) in enumerate(sorted_with_orig_idx):
    rank_of_number[orig_idx] = rank

print(f"   Rang jeder Position: {rank_of_number}")

# Diese Ränge als Base58 (0-39, alle < 58)
rank_b58 = ''.join([base58_alphabet[r] for r in rank_of_number])
print(f"   Ränge als Base58: {rank_b58}")

# 3. Die Zahlen als Zeiger auf eine 99-Buchstaben Quelle
print("\n3. ALS ZEIGER IN ALPHABETE:")

# Erweitertes Alphabet: a-z, A-Z, 0-9, Sonderzeichen
extended_alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:',.<>?/~`"
print(f"   Erweitertes Alphabet ({len(extended_alpha)} Zeichen)")

result_extended = ''.join([extended_alpha[n % len(extended_alpha)] for n in numbers])
print(f"   Ergebnis: {result_extended}")

# Nur Kleinbuchstaben wiederholt
lower_repeat = "abcdefghijklmnopqrstuvwxyz" * 4  # 104 Zeichen
result_lower = ''.join([lower_repeat[n] for n in numbers])
print(f"   Als Kleinbuchstaben (a-z repeat): {result_lower}")

# 4. XOR mit einem Schlüssel
print("\n4. XOR MIT VERSCHIEDENEN SCHLÜSSELN:")

# XOR mit 137 (prefix sum)
xor_137 = [(n ^ 137) % 58 for n in numbers]
xor_137_b58 = ''.join([base58_alphabet[x] for x in xor_137])
print(f"   XOR 137, mod 58: {xor_137_b58}")

# XOR mit 121 (suffix sum)
xor_121 = [(n ^ 121) % 58 for n in numbers]
xor_121_b58 = ''.join([base58_alphabet[x] for x in xor_121])
print(f"   XOR 121, mod 58: {xor_121_b58}")

# XOR mit 11 (CFB sum)
xor_11 = [(n ^ 11) % 58 for n in numbers]
xor_11_b58 = ''.join([base58_alphabet[x] for x in xor_11])
print(f"   XOR 11, mod 58: {xor_11_b58}")

# 5. Die Zahlen als Byte-Offsets
print("\n5. ALS ASCII MIT OFFSET:")
# Offset 48 (Zahlen beginnen bei '0')
offset_48 = ''.join([chr(n + 48) if 32 <= n + 48 <= 126 else '?' for n in numbers])
print(f"   +48 (ab '0'): {offset_48}")

# Offset 55 (Großbuchstaben ab 10)
offset_55 = ''.join([chr(n + 55) if 32 <= n + 55 <= 126 else '?' for n in numbers])
print(f"   +55: {offset_55}")

# 6. Die fehlenden Zahlen könnten der Schlüssel sein
print("\n6. DIE FEHLENDEN ZAHLEN ALS SCHLÜSSEL:")
all_nums = set(range(1, 100))
present = set(numbers)
missing = sorted(all_nums - present)

# Die Summe der fehlenden = 2977, der vorhandenen = 1973
# 2977 + 1973 = 4950 = 1+2+...+99
print(f"   Fehlend: {missing}")
print(f"   Anzahl fehlend: {len(missing)}")

# Erste 40 fehlende als Schlüssel?
missing_key = missing[:40] if len(missing) >= 40 else missing
print(f"   Fehlende als potentieller Schlüssel: {missing_key[:20]}...")

# XOR mit den fehlenden (wenn gleiche Länge)
if len(missing) >= 40:
    xor_missing = [numbers[i] ^ missing[i] for i in range(40)]
    print(f"   XOR mit fehlenden: {xor_missing}")

# 7. Inverse Permutation
print("\n7. INVERSE PERMUTATION:")
# Wenn numbers[i] = j, dann inverse[j] = i (für Zahlen 1-99)
# Das ergibt eine sparse Zuordnung

inverse_map = {}
for i, n in enumerate(numbers):
    inverse_map[n] = i

# Lese die Positionen in sortierter Reihenfolge der Zahlen
reading_order = [inverse_map[n] for n in sorted(present)]
print(f"   Lese-Reihenfolge (sortiert nach Zahlenwert): {reading_order}")

# 8. Die Zahlen könnten Bits kodieren
print("\n8. BINÄR-KODIERUNG:")
# Jede Zahl modulo 2 = 0 oder 1
binary = ''.join([str(n % 2) for n in numbers])
print(f"   Mod 2 (Parität): {binary}")

# In Bytes umwandeln (8 Bits)
bytes_from_binary = []
for i in range(0, len(binary), 8):
    byte_str = binary[i:i+8]
    if len(byte_str) == 8:
        bytes_from_binary.append(int(byte_str, 2))
print(f"   Als Bytes: {bytes_from_binary}")
print(f"   Als ASCII: {''.join([chr(b) if 32 <= b <= 126 else '?' for b in bytes_from_binary])}")

# Gerade/Ungerade als Binär anders herum
binary_rev = ''.join([str(1 - n % 2) for n in numbers])
print(f"   Invertiert: {binary_rev}")

# 9. Die Struktur 137 | 36 | 121 genauer
print("\n9. DIE STRUKTUR 137 | 36 | 121:")
print(f"   137 = 45 + 92 (Position 0,1)")
print(f"   36 Zahlen (Position 2-37)")
print(f"   121 = 82 + 39 (Position 38,39)")
print(f"\n   Was passiert wenn wir 137 und 121 als Operationen verwenden?")

# Jede Inhaltszahl mod 137
content_mod137 = [n % 137 for n in content]
print(f"   Inhalt mod 137: {content_mod137}")

# Inhalt XOR 137
content_xor137 = [n ^ 137 for n in content]
print(f"   Inhalt XOR 137: {content_xor137[:10]}...")

# 10. CFB^9 - Die 9 Indizes aus CFB-Koordinaten in 6x6
print("\n10. CFB^9 IN 6x6 MATRIX (0-indexed):")
# C=2, F=5, B=1 (0-indexed: A=0, B=1, C=2, ...)
# Kartesisches Produkt:
cfb_coords = []
for i in [2, 5, 1]:  # C, F, B
    for j in [2, 5, 1]:  # C, F, B
        cfb_coords.append((i, j))
print(f"   CFB x CFB Koordinaten (0-idx): {cfb_coords}")

# Die 6x6 Matrix der Inhaltszahlen
matrix_6x6 = [content[i*6:(i+1)*6] for i in range(6)]
print("\n   6x6 Matrix:")
for row in matrix_6x6:
    print(f"   {row}")

# Werte an den CFB x CFB Koordinaten
cfb9_values = []
for r, c in cfb_coords:
    if r < 6 and c < 6:
        val = matrix_6x6[r][c]
        cfb9_values.append(val)
        print(f"   Matrix[{r}][{c}] = {val}")

print(f"\n   Die 9 CFB^9 Werte: {cfb9_values}")
print(f"   Summe: {sum(cfb9_values)}")

# Als Base58 mit mod
cfb9_b58 = ''.join([base58_alphabet[v % 58] for v in cfb9_values])
print(f"   Als Base58: {cfb9_b58}")

# Als ASCII
cfb9_ascii = ''.join([chr(v) if 32 <= v <= 126 else chr(v % 26 + 65) for v in cfb9_values])
print(f"   Als ASCII/Buchstaben: {cfb9_ascii}")

# 11. Finale Idee: Die Zahlen sind eine Lookup-Tabelle
print("\n11. LOOKUP-TABELLE INTERPRETATION:")
# Die Zahlen könnten sagen: "An Position X findest du Buchstabe Y"
# Oder umgekehrt: "Buchstabe X steht an Position Y"

# Konstruiere eine 100-Element Tabelle
lookup = ['_'] * 100
for i, n in enumerate(numbers):
    if n < 100:
        lookup[n] = chr(i + 65) if i < 26 else chr(i + 71)  # A-Z, dann a-n

print(f"   Lookup-Tabelle (erste 40): {lookup[:40]}")
print(f"   Besetzt: {[i for i, c in enumerate(lookup) if c != '_']}")

# Zusammenfassung
print("\n" + "=" * 70)
print("VIELVERSPRECHENDSTE ERGEBNISSE")
print("=" * 70)
print(f"""
1. Base58 mit Mod 58:
   Alle 40: {base58_mod}
   Inhalt 36: {content_b58}

2. Rang-Permutation als Base58:
   {rank_b58}

3. CFB^9 aus 6x6 Matrix:
   Werte: {cfb9_values}
   Als Base58: {cfb9_b58}

4. Die Struktur bleibt:
   PREFIX: 137 (Feinstrukturkonstante)
   CONTENT: 36 = 3*6*2 = CFB-Produkt
   SUFFIX: 121 = 11² = (C+F+B)²
""")

# Speichere
results = {
    "base58_mod58": base58_mod,
    "content_base58_mod58": content_b58,
    "rank_permutation": rank_b58,
    "cfb9_values": cfb9_values,
    "cfb9_base58": cfb9_b58,
    "binary_parity": binary,
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_PUZZLE_PERMUTATION_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nErgebnisse gespeichert!")
