#!/usr/bin/env python3
"""
CFB Puzzle - Bitcoin Adress-Analyse

Die 36 Inhaltszahlen als Base58 ergeben: 4LF1WQ7aDqeP4ATesHGVUif85LHXWkh63GFU (36 Zeichen)
Bitcoin-Adressen haben 34 Zeichen - also 2 zu viel!

Was wenn wir 34 Zahlen nehmen? Der User sagte "34 Zahlen"!
"""

import hashlib
import json

numbers = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def to_base58(nums):
    result = ""
    for n in nums:
        if 0 <= n < 58:
            result += base58_alphabet[n]
        else:
            result += "?"
    return result

print("=" * 70)
print("CFB PUZZLE - BITCOIN ADRESS-ANALYSE")
print("=" * 70)

# Die User-Beobachtung: "34 Zahlen (a BTC wallet usually has 34 characters)"
# Aber wir haben 40 Zahlen!

print("\n1. VERSCHIEDENE 34-ZEICHEN EXTRAKTIONEN:")

# a) Ohne die ersten 6 (prefix + post-prefix)
subset_a = numbers[6:]  # 34 Zahlen
print(f"\n   a) Ab Position 6 (34 Zahlen): {len(subset_a)}")
addr_a = to_base58(subset_a)
print(f"      Als Base58: {addr_a}")
print(f"      Mit '1' prefix: 1{addr_a[:33]}")

# b) Nur die mittleren 34 (ohne erste 3 und letzte 3)
subset_b = numbers[3:-3]  # 34 Zahlen
print(f"\n   b) Position 3-36 (34 Zahlen): {len(subset_b)}")
addr_b = to_base58(subset_b)
print(f"      Als Base58: {addr_b}")

# c) Die "Inhaltszahlen" ohne erste und letzte
content = numbers[2:-2]  # 36 Zahlen
content_34 = content[1:-1]  # 34 Zahlen
print(f"\n   c) Inhalt ohne erste/letzte (34 Zahlen): {len(content_34)}")
addr_c = to_base58(content_34)
print(f"      Als Base58: {addr_c}")

# d) Erste 34 Zahlen
subset_d = numbers[:34]
print(f"\n   d) Erste 34 Zahlen: {len(subset_d)}")
addr_d = to_base58(subset_d)
print(f"      Als Base58: {addr_d}")

# e) Letzte 34 Zahlen
subset_e = numbers[6:]  # = subset_a
print(f"\n   e) Letzte 34 Zahlen: {len(subset_e)}")
addr_e = to_base58(subset_e)
print(f"      Als Base58: {addr_e}")

# Die wichtige Frage: Was ist "3 after the prefix"?
print("\n2. INTERPRETATION VON '3 AFTER THE PREFIX':")
print(f"   Die 3. Zahl (Index 2) ist: {numbers[2]}")
print(f"   Das bedeutet vielleicht: Die ersten 3 Zahlen sind der Prefix?")
print(f"   45, 92, 3 → 45+92=137, dann 3")

# Was wenn 3 bedeutet "nimm ab Position 3"?
subset_from_3 = numbers[3:]  # 37 Zahlen
print(f"\n   Ab Position 3: {len(subset_from_3)} Zahlen")
print(f"   Die ersten 34 davon: {to_base58(subset_from_3[:34])}")

# User sagte auch "27 before the suffix"
print("\n3. INTERPRETATION VON '27 BEFORE THE SUFFIX':")
print(f"   Position 37: {numbers[37]} = 27")
print(f"   Suffix = Position 38,39 = {numbers[38]}, {numbers[39]} = 82+39=121")
print(f"   Also: Zahlen 0-37 (38 Zahlen) vor dem Suffix")

# 38 Zahlen ohne die ersten 4 = 34
subset_core = numbers[4:38]  # 34 Zahlen!
print(f"\n   Position 4-37 (34 Zahlen): {len(subset_core)}")
addr_core = to_base58(subset_core)
print(f"   Als Base58: {addr_core}")

# Das könnte es sein!
print("\n4. ⭐ DIE 34 KERN-ZAHLEN (Position 4-37):")
print(f"   {subset_core}")
print(f"   Als Base58: {addr_core}")

# Prüfe ob das eine gültige Bitcoin-Adresse sein könnte
print("\n5. BITCOIN-ADRESS-VALIDIERUNG:")

# Mit verschiedenen Prefixes
potential_addresses = [
    f"1{addr_core[:33]}",  # Legacy P2PKH
    f"3{addr_core[:33]}",  # P2SH
    addr_core[:34],        # Direkt
]

for addr in potential_addresses:
    print(f"   Kandidat: {addr}")

# Die komplette 36-Zeichen Dekodierung von Inhalt
print("\n6. DIE 36 INHALTSZAHLEN ALS HEX:")
content = numbers[2:-2]
hex_content = ''.join([f'{n:02x}' for n in content])
print(f"   Als Hex (72 Zeichen): {hex_content}")

# Als SHA256 Input?
sha256_hex = hashlib.sha256(bytes(content)).hexdigest()
print(f"   SHA256: {sha256_hex}")

# Als RIPEMD160 (für Bitcoin Adressen)
ripemd = hashlib.new('ripemd160', bytes(content)).hexdigest()
print(f"   RIPEMD160: {ripemd}")

# Die 40 Zahlen als Seed?
print("\n7. DIE 40 ZAHLEN ALS POTENTIELLER SEED:")
hex_all = ''.join([f'{n:02x}' for n in numbers])
print(f"   Alle 40 als Hex: {hex_all}")
print(f"   Länge: {len(hex_all)} Zeichen (80 hex = 40 bytes)")

# SHA256 davon
sha_all = hashlib.sha256(bytes(numbers)).hexdigest()
print(f"   SHA256: {sha_all}")

# Die Zahlen sortiert
print("\n8. SORTIERTE ZAHLEN:")
sorted_nums = sorted(numbers)
print(f"   Sortiert: {sorted_nums}")

# Welche Zahlen fehlen zwischen 1-99?
all_possible = set(range(1, 100))
present = set(numbers)
missing = sorted(all_possible - present)
print(f"   Fehlende Zahlen (1-99): {missing[:20]}...")
print(f"   Anzahl fehlend: {len(missing)}")

# Doppelte Zahlen?
from collections import Counter
counts = Counter(numbers)
duplicates = {k: v for k, v in counts.items() if v > 1}
print(f"   Doppelte Zahlen: {duplicates if duplicates else 'Keine'}")

# Die Zahlen 1-99 die NICHT in der Folge sind könnten auch wichtig sein
print("\n9. DIE FEHLENDEN ZAHLEN:")
print(f"   Anzahl: {len(missing)} (von 99 möglichen, 40 sind verwendet)")
print(f"   Fehlend: {missing}")

# Summe der fehlenden
print(f"   Summe fehlend: {sum(missing)}")
print(f"   Summe vorhanden: {sum(numbers)}")
print(f"   Zusammen: {sum(missing) + sum(numbers)}")

# CFB^9 nochmal anders interpretiert
print("\n10. CFB^9 - ALTERNATIVE INTERPRETATION:")
print(f"    Was wenn CFB^9 bedeutet: 9 spezielle Werte extrahieren?")

# Die 9 Positionen die 3 enthalten
positions_with_3 = [i for i, n in enumerate(numbers) if n % 3 == 0]
print(f"    Positionen mit durch 3 teilbaren Zahlen: {positions_with_3}")
div_by_3 = [numbers[i] for i in positions_with_3]
print(f"    Diese Zahlen: {div_by_3}")
print(f"    Erste 9: {div_by_3[:9]}")

# Die Zahlen an Position 0,4,8,12,16,20,24,28,32 (jede 4., 9 Stück)
every_4th = numbers[::4][:9]
print(f"    Jede 4. Zahl (9 Stück): {every_4th}")
print(f"    Als Base58: {to_base58(every_4th)}")

# Die Zahlen an Position 3,6,9,12,15,18,21,24,27 (vielfache von 3)
pos_multiples_3 = numbers[3::3][:9]
print(f"    Position 3,6,9,... (9 Stück): {pos_multiples_3}")
print(f"    Als Base58: {to_base58(pos_multiples_3)}")

# Finale Zusammenfassung
print("\n" + "=" * 70)
print("ZUSAMMENFASSUNG - WICHTIGSTE KANDIDATEN")
print("=" * 70)
print(f"""
Die Zahlenfolge ist strukturiert als:
  PREFIX:  45, 92, 3      (45+92=137, dann 3)
  CONTENT: Zahlen 3-37    (34 Zahlen für BTC-Adresse?)
  SUFFIX:  27, 82, 39     (27 vor 82+39=121)

Top Bitcoin-Adress-Kandidaten:
  1. {addr_core} (Position 4-37)
  2. 1{addr_core[:33]} (mit Legacy-Prefix)
  3. {addr_c} (Inhalt ohne Ränder)

CFB x CFB = 121 = 11² (C+F+B = 3+6+2 = 11)
CFB-Produkt = 36 (Anzahl Inhaltszahlen)

Summe aller Zahlen: 1973 (Primzahl!)
""")

# Speichere Ergebnisse
results = {
    "address_candidates": [
        {"method": "position_4_37", "address": addr_core},
        {"method": "with_1_prefix", "address": f"1{addr_core[:33]}"},
        {"method": "content_without_edges", "address": addr_c},
        {"method": "first_34", "address": addr_d},
    ],
    "structure": {
        "prefix": [45, 92, 3],
        "content_34": list(subset_core),
        "suffix": [27, 82, 39],
    },
    "missing_numbers": missing,
    "hex_all": hex_all,
    "sha256_content": sha256_hex,
}

with open('/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/CFB_PUZZLE_BITCOIN_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nErgebnisse gespeichert!")
