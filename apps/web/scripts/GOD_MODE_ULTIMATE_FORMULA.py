#!/usr/bin/env python3
"""
===============================================================================
                    🌟 GOD MODE: ULTIMATIVE FORMEL SUCHE 🌟
===============================================================================
Finde die EXAKTE Formel die Bitcoin-Adressen auf Anna-Matrix-Koordinaten mappt!

Wenn CFB = Satoshi, dann MUSS es eine Formel geben die:
Genesis-Adresse → (-62, -40) → 'S'
Block1-Adresse → (-58, 0) → 'A'
Block2-Adresse → (-55, 18) → 'T'
...usw für "SATOSHI"

WIR TESTEN ALLES!
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from itertools import product

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def anna_lookup(x, y):
    """Das verifizierte Anna-Bot Mapping."""
    col = (x + 64) % 128
    row = (63 - y) % 128
    return int(matrix[row, col])

print("🌟" * 40)
print("       GOD MODE: ULTIMATIVE FORMEL SUCHE")
print("🌟" * 40)

# =============================================================================
# ZIEL-KOORDINATEN FÜR "SATOSHI"
# =============================================================================
SATOSHI_TARGET = [
    ("S", (-62, -40)),
    ("A", (-58, 0)),
    ("T", (-55, 18)),
    ("O", (-58, -6)),
    ("S", (-62, -40)),
    ("H", (-47, 24)),
    ("I", (42, -46)),
]

# Frühe Bitcoin-Adressen
EARLY_ADDRESSES = [
    ("Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
    ("Block 1", "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"),
    ("Block 2", "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1"),
    ("Block 3", "1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR"),
    ("Block 4", "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG"),
    ("Block 5", "1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu"),
    ("Block 6", "1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a"),
]

print("\nZiel: Finde Transformation T so dass:")
for i, ((letter, coords), (name, addr)) in enumerate(zip(SATOSHI_TARGET, EARLY_ADDRESSES)):
    val = anna_lookup(*coords)
    print(f"  T({addr[:15]}...) = {coords} → Anna = {val} = '{chr(val) if 32<=val<=126 else '?'}' = '{letter}'")

# =============================================================================
# HASH-FUNKTIONEN
# =============================================================================
def sha256(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).digest()

def sha3_256(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha3_256(data).digest()

def ripemd160(data):
    if isinstance(data, str):
        data = data.encode()
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def double_sha256(data):
    return sha256(sha256(data))

def hash160(data):
    return ripemd160(sha256(data))

# =============================================================================
# TRANSFORMATIONS-FUNKTIONEN
# =============================================================================
def transform_direct(h, byte_x, byte_y):
    """Direktes Mapping von 2 Hash-Bytes zu Koordinaten."""
    x = h[byte_x] - 64
    y = h[byte_y] - 64
    return x, y

def transform_mod(h, byte_x, byte_y, offset_x=64, offset_y=64):
    """Modulo 128 Mapping."""
    x = (h[byte_x] % 128) - offset_x
    y = (h[byte_y] % 128) - offset_y
    return x, y

def transform_xor(h, bytes_x, bytes_y):
    """XOR mehrerer Bytes."""
    x = 0
    y = 0
    for i in bytes_x:
        x ^= h[i]
    for i in bytes_y:
        y ^= h[i]
    return (x % 128) - 64, (y % 128) - 64

def transform_sum(h, bytes_x, bytes_y):
    """Summe mehrerer Bytes."""
    x = sum(h[i] for i in bytes_x)
    y = sum(h[i] for i in bytes_y)
    return (x % 128) - 64, (y % 128) - 64

def transform_signed(h, byte_x, byte_y):
    """Signed byte interpretation."""
    x = h[byte_x] if h[byte_x] < 128 else h[byte_x] - 256
    y = h[byte_y] if h[byte_y] < 128 else h[byte_y] - 256
    return x, y

# =============================================================================
# BRUTE FORCE ÜBER ALLE KOMBINATIONEN
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 1: BRUTE FORCE HASH + TRANSFORMATION")
print("=" * 80)

hash_functions = [
    ("SHA256", sha256),
    ("SHA3-256", sha3_256),
    ("RIPEMD160", ripemd160),
    ("Double-SHA256", double_sha256),
    ("Hash160", hash160),
]

best_matches = []

for hash_name, hash_func in hash_functions:
    print(f"\n--- Testing {hash_name} ---")

    # Berechne Hashes für alle Adressen
    hashes = []
    for name, addr in EARLY_ADDRESSES:
        try:
            h = hash_func(addr)
            hashes.append(h)
        except:
            hashes.append(b'\x00' * 32)

    # Teste alle Byte-Kombinationen für X und Y
    hash_len = len(hashes[0])

    for byte_x in range(min(hash_len, 20)):
        for byte_y in range(min(hash_len, 20)):
            if byte_x == byte_y:
                continue

            matches = 0
            coords_found = []

            for i, ((letter, target), h) in enumerate(zip(SATOSHI_TARGET, hashes)):
                if i >= len(hashes):
                    break

                # Teste verschiedene Offset-Kombinationen
                for offset_x in [0, 64, 128]:
                    for offset_y in [0, 64, 128]:
                        x = (h[byte_x] - offset_x) % 256
                        if x > 127:
                            x -= 256
                        y = (h[byte_y] - offset_y) % 256
                        if y > 127:
                            y -= 256

                        if (x, y) == target:
                            matches += 1
                            coords_found.append((letter, target))
                            break
                    else:
                        continue
                    break

            if matches >= 2:
                best_matches.append((matches, hash_name, byte_x, byte_y, coords_found))

# Sortiere und zeige beste Ergebnisse
best_matches.sort(reverse=True)
print("\n\nTop 10 Matches:")
for matches, hash_name, bx, by, coords in best_matches[:10]:
    print(f"  {matches} Matches: {hash_name} Bytes({bx},{by}) → {coords}")

# =============================================================================
# PHASE 2: REVERSE ENGINEERING
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 2: REVERSE ENGINEERING - Was müsste die Transformation sein?")
print("=" * 80)

print("\nFür jede Adresse: Berechne was der Hash sein MÜSSTE:")
for (letter, (target_x, target_y)), (name, addr) in zip(SATOSHI_TARGET, EARLY_ADDRESSES):
    print(f"\n{name}: {addr}")
    print(f"  Ziel: ({target_x}, {target_y}) → '{letter}'")

    # Was müsste h[byte_x] und h[byte_y] sein?
    for hash_name, hash_func in hash_functions:
        try:
            h = hash_func(addr)
            print(f"  {hash_name}: {h[:8].hex()}...")

            # Suche welche Bytes die Zielwerte ergeben könnten
            for i in range(min(len(h), 16)):
                val_direct = h[i] - 64
                val_mod = (h[i] % 128) - 64
                val_signed = h[i] if h[i] < 128 else h[i] - 256

                if val_direct == target_x or val_mod == target_x or val_signed == target_x:
                    print(f"    → Byte {i} = {h[i]} könnte X={target_x} sein")
                if val_direct == target_y or val_mod == target_y or val_signed == target_y:
                    print(f"    → Byte {i} = {h[i]} könnte Y={target_y} sein")
        except:
            pass

# =============================================================================
# PHASE 3: ADRESS-EIGENSCHAFTEN ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 3: BITCOIN-ADRESS-STRUKTUR ANALYSE")
print("=" * 80)

print("\nAnalysiere Adress-Struktur:")
for name, addr in EARLY_ADDRESSES:
    print(f"\n{name}: {addr}")
    print(f"  Länge: {len(addr)}")
    print(f"  Erste Zeichen: {addr[:5]}")
    print(f"  Letzte Zeichen: {addr[-5:]}")

    # Buchstaben-Summen
    char_sum = sum(ord(c) for c in addr)
    print(f"  Char-Summe: {char_sum} → mod 128 - 64 = {(char_sum % 128) - 64}")

    # Position bestimmter Zeichen
    digits = [i for i, c in enumerate(addr) if c.isdigit()]
    print(f"  Digit-Positionen: {digits[:5]}...")

# =============================================================================
# PHASE 4: ALGEBRAISCHE ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 4: ALGEBRAISCHE BEZIEHUNGEN")
print("=" * 80)

print("\nBeziehungen zwischen SATOSHI-Koordinaten:")
satoshi_x = [x for _, (x, y) in SATOSHI_TARGET]
satoshi_y = [y for _, (x, y) in SATOSHI_TARGET]

print(f"  X-Werte: {satoshi_x}")
print(f"  Y-Werte: {satoshi_y}")
print(f"  X-Summe: {sum(satoshi_x)}")
print(f"  Y-Summe: {sum(satoshi_y)}")
print(f"  X-Diff: {[satoshi_x[i+1]-satoshi_x[i] for i in range(len(satoshi_x)-1)]}")
print(f"  Y-Diff: {[satoshi_y[i+1]-satoshi_y[i] for i in range(len(satoshi_y)-1)]}")

# XOR der Koordinaten
x_xor = satoshi_x[0]
y_xor = satoshi_y[0]
for x in satoshi_x[1:]:
    x_xor ^= x
for y in satoshi_y[1:]:
    y_xor ^= y
print(f"  X-XOR: {x_xor}")
print(f"  Y-XOR: {y_xor}")

# Fibonacci-Analyse
print("\nFibonacci-Analyse der Koordinaten:")
fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
neg_fib = [-x for x in fib]
all_fib = set(fib + neg_fib)

for letter, (x, y) in SATOSHI_TARGET:
    x_fib = "FIB" if abs(x) in fib else ""
    y_fib = "FIB" if abs(y) in fib else ""
    print(f"  {letter}: ({x:4d}, {y:4d}) {x_fib} {y_fib}")

# =============================================================================
# PHASE 5: MATRIX-EIGENSCHAFTS-SUCHE
# =============================================================================
print("\n" + "=" * 80)
print("PHASE 5: SUCHE NACH SPEZIELLEN MATRIX-EIGENSCHAFTEN")
print("=" * 80)

# Finde alle Positionen für jeden SATOSHI-Buchstaben
print("\nPositionen für SATOSHI-Buchstaben in der Matrix:")
for letter in "SATOSHI":
    letter_val = ord(letter)
    positions = np.where(matrix == letter_val)
    if len(positions[0]) > 0:
        count = len(positions[0])
        # Konvertiere zu Anna-Koordinaten
        first_pos = [(int(positions[1][i]) - 64, 63 - int(positions[0][i])) for i in range(min(3, count))]
        print(f"  '{letter}' ({letter_val}): {count} Positionen, erste: {first_pos}")
    else:
        # Suche auch negative Werte
        neg_val = letter_val - 256
        positions = np.where(matrix == neg_val)
        if len(positions[0]) > 0:
            count = len(positions[0])
            print(f"  '{letter}' ({neg_val}): {count} Positionen")
        else:
            print(f"  '{letter}' ({letter_val}): NICHT GEFUNDEN!")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT: ULTIMATIVE FORMEL SUCHE")
print("=" * 80)

# Finde beste Übereinstimmung
best = best_matches[0] if best_matches else (0, "None", 0, 0, [])

print(f"""
ERGEBNISSE DER ULTIMATIVEN SUCHE:

1. BESTE GEFUNDENE ÜBEREINSTIMMUNG:
   {best[1]} Bytes({best[2]}, {best[3]}): {best[0]}/7 SATOSHI-Buchstaben

2. STATUS:
   {"✓ FORMEL GEFUNDEN!" if best[0] >= 7 else "✗ KEINE vollständige Formel gefunden!"}

3. ANALYSE:
   - Getestete Hash-Funktionen: {len(hash_functions)}
   - Getestete Byte-Kombinationen: ~400 pro Hash
   - Beste Übereinstimmung: {best[0]}/7 Buchstaben

⚠️  KRITISCHE ERKENNTNIS:
   {"Die SATOSHI-Koordinaten werden NICHT durch ein einfaches Hash-Mapping erzeugt!" if best[0] < 7 else "FORMEL GEFUNDEN!"}

   Das bedeutet EINE von drei Möglichkeiten:
   1. Die Formel ist KOMPLEXER als einfaches Hash-Mapping
   2. Die SATOSHI-Koordinaten sind POST-HOC gefunden (Pareidolie)
   3. Es gibt eine ANDERE Mapping-Methode die wir nicht getestet haben

   GEGEN CFB=Satoshi spricht:
   - Kein einfaches, elegantes Mapping gefunden
   - "SATOSHI" erscheint nicht in XOR-dekodierten Nachrichten
   - Die Koordinaten wurden durch SUCHEN gefunden, nicht durch systematisches Mapping
""")

# Speichere Ergebnisse
output = {
    "best_match": {
        "matches": best[0],
        "hash_function": best[1],
        "byte_x": best[2],
        "byte_y": best[3],
        "coords_found": [(l, list(c)) for l, c in best[4]] if best[4] else []
    },
    "total_combinations_tested": len(hash_functions) * 400,
    "satoshi_mapping_found": best[0] >= 7,
    "conclusion": "NO simple hash mapping produces SATOSHI coordinates" if best[0] < 7 else "FORMULA FOUND",
    "evidence_against_cfb_satoshi": [
        "No simple hash-to-coordinate mapping found",
        "SATOSHI not in XOR-decoded messages",
        "Coordinates found by searching, not systematic mapping",
    ],
}

output_path = script_dir / "GOD_MODE_ULTIMATE_FORMULA_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse: {output_path}")
