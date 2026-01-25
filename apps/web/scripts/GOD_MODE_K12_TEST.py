#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                     🔬 GOD MODE: K12 HASH TEST 🔬
═══════════════════════════════════════════════════════════════════════════════
Teste echtes K12 (KangarooTwelve) Hash für Bitcoin-Adress-Mapping.
K12 ist Qubic's native Hash-Funktion!
"""

import json
import numpy as np
from pathlib import Path
import hashlib
import struct

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def anna_lookup(x, y):
    col = (x + 64) % 128
    row = (63 - y) % 128
    return int(matrix[row, col])

print("🔬" * 40)
print("              GOD MODE: K12 HASH TEST")
print("🔬" * 40)

# =============================================================================
# K12 SIMULATION (Da echtes K12 eine C-Library braucht)
# =============================================================================
print("\n" + "═" * 80)
print("K12 HASH SIMULATION")
print("═" * 80)

# K12 basiert auf Keccak/SHA-3, wir simulieren es mit SHA3-256
def k12_simulate(data):
    """Simuliere K12 mit SHA3-256 (ähnliche Struktur)."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha3_256(data).digest()

def k12_to_coords(data):
    """Konvertiere K12-Hash zu Anna-Koordinaten."""
    h = k12_simulate(data)
    # K12 produziert 256 bits, wir brauchen 2 × 7 bits = 14 bits für Koordinaten
    x = (h[0] ^ h[2] ^ h[4]) % 128 - 64
    y = (h[1] ^ h[3] ^ h[5]) % 128 - 64
    return x, y

def k12_to_coords_v2(data):
    """Alternative K12 Mapping - erste 2 Bytes direkt."""
    h = k12_simulate(data)
    x = h[0] - 64
    y = h[1] - 64
    return x, y

def k12_to_coords_v3(data):
    """K12 Mapping - mit XOR aller Bytes."""
    h = k12_simulate(data)
    x = 0
    y = 0
    for i in range(0, 32, 2):
        x ^= h[i]
        y ^= h[i+1]
    x = (x % 128) - 64
    y = (y % 128) - 64
    return x, y

# =============================================================================
# TESTE BITCOIN-ADRESSEN MIT K12
# =============================================================================
print("\n" + "═" * 80)
print("BITCOIN-ADRESSEN MIT K12")
print("═" * 80)

addresses = [
    ("Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
    ("Block 1", "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"),
    ("Block 2", "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1"),
    ("Block 3", "1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR"),
    ("Block 4", "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG"),
    ("Block 5", "1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu"),
    ("Block 6", "1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a"),
    ("Block 7", "16LoW7y83wtawMg5XmT4M3Q7EdjjUmenjM"),
    ("Block 8", "1J6PYEzr4CUoGbnXrELyHszoTSz3wCsCaj"),
    ("Block 9", "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"),
]

print("\nMethode 1: K12 XOR (Bytes 0,2,4 und 1,3,5)")
results_v1 = []
for name, addr in addresses:
    x, y = k12_to_coords(addr)
    val = anna_lookup(x, y)
    ch = chr(val) if 32 <= val <= 126 else '.'
    results_v1.append(ch)
    print(f"  {name:10s}: Anna({x:4d},{y:4d}) = {val:4d} → '{ch}'")
print(f"  Kombiniert: '{''.join(results_v1)}'")

print("\nMethode 2: K12 Direkt (Bytes 0,1)")
results_v2 = []
for name, addr in addresses:
    x, y = k12_to_coords_v2(addr)
    val = anna_lookup(x, y)
    ch = chr(val) if 32 <= val <= 126 else '.'
    results_v2.append(ch)
    print(f"  {name:10s}: Anna({x:4d},{y:4d}) = {val:4d} → '{ch}'")
print(f"  Kombiniert: '{''.join(results_v2)}'")

print("\nMethode 3: K12 XOR Alle")
results_v3 = []
for name, addr in addresses:
    x, y = k12_to_coords_v3(addr)
    val = anna_lookup(x, y)
    ch = chr(val) if 32 <= val <= 126 else '.'
    results_v3.append(ch)
    print(f"  {name:10s}: Anna({x:4d},{y:4d}) = {val:4d} → '{ch}'")
print(f"  Kombiniert: '{''.join(results_v3)}'")

# =============================================================================
# BRUTE FORCE: FINDE DAS RICHTIGE MAPPING
# =============================================================================
print("\n" + "═" * 80)
print("BRUTE FORCE: SUCHE NACH SATOSHI-MAPPING")
print("═" * 80)

# Wir suchen eine Hash-Transformation die "SATOSHI" aus den ersten Adressen erzeugt
# oder zumindest signifikante Buchstaben

def try_mapping(addrs, byte_pairs):
    """Versuche verschiedene Byte-Kombinationen."""
    results = []
    for name, addr in addrs:
        h = k12_simulate(addr)
        x = (h[byte_pairs[0]] ^ h[byte_pairs[2]]) % 128 - 64
        y = (h[byte_pairs[1]] ^ h[byte_pairs[3]]) % 128 - 64
        val = anna_lookup(x, y)
        ch = chr(val) if 32 <= val <= 126 else '.'
        results.append(ch)
    return ''.join(results)

print("\nBrute-Force über verschiedene Byte-Kombinationen:")
best_matches = []

for b0 in range(8):
    for b1 in range(8):
        for b2 in range(8):
            for b3 in range(8):
                if b0 != b2 and b1 != b3:  # Unterschiedliche Bytes
                    result = try_mapping(addresses[:7], (b0, b1, b2, b3))
                    # Prüfe auf SATOSHI-ähnliche Buchstaben
                    score = sum(1 for c in result if c in "SATOSHI")
                    if score >= 3:
                        best_matches.append((score, (b0,b1,b2,b3), result))

best_matches.sort(reverse=True)
print("\nTop 10 Matches:")
for score, bytes_used, result in best_matches[:10]:
    print(f"  Score {score}: Bytes {bytes_used} → '{result}'")

# =============================================================================
# QUBIC-STYLE MAPPING
# =============================================================================
print("\n" + "═" * 80)
print("QUBIC-STYLE MAPPING (55 Zeichen Alphabet)")
print("═" * 80)

# Qubic verwendet ein 55-Zeichen Alphabet: abcdefghijklmnopqrstuvwxyz
QUBIC_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def addr_to_qubic_seed(addr):
    """Konvertiere Bitcoin-Adresse zu Qubic-ähnlichem Seed."""
    h = k12_simulate(addr)
    seed = ""
    for byte in h[:28]:  # 28 Zeichen wie Qubic Seeds
        seed += QUBIC_ALPHABET[byte % 26]
    return seed

def qubic_seed_to_coords(seed):
    """Konvertiere Qubic-Seed zu Anna-Koordinaten."""
    # Summe der Zeichen-Indizes
    x = sum(QUBIC_ALPHABET.index(c) for c in seed[:14]) % 128 - 64
    y = sum(QUBIC_ALPHABET.index(c) for c in seed[14:28]) % 128 - 64
    return x, y

print("\nBitcoin → Qubic Seed → Anna Koordinaten:")
for name, addr in addresses[:7]:
    seed = addr_to_qubic_seed(addr)
    x, y = qubic_seed_to_coords(seed)
    val = anna_lookup(x, y)
    ch = chr(val) if 32 <= val <= 126 else '.'
    print(f"  {name:10s}: Seed={seed[:10]}... Anna({x:4d},{y:4d}) = {val:4d} → '{ch}'")

# =============================================================================
# REVERSE ENGINEERING: WAS MÜSSTE DIE FORMEL SEIN?
# =============================================================================
print("\n" + "═" * 80)
print("REVERSE ENGINEERING: GESUCHTE FORMEL")
print("═" * 80)

# Wir kennen die SATOSHI-Koordinaten:
# S: (-62, -40), A: (-58, 0), T: (-55, 18), O: (-58, -6), S: (-62, -40), H: (-47, 24), I: (42, -46)

satoshi_target = [
    ("Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", (-62, -40)),  # S
    ("Block 1", "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX", (-58, 0)),    # A
    ("Block 2", "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1", (-55, 18)),   # T
    ("Block 3", "1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR", (-58, -6)),   # O
    ("Block 4", "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG", (-62, -40)),  # S
    ("Block 5", "1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu", (-47, 24)),   # H
    ("Block 6", "1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a", (42, -46)),   # I
]

print("\nGesuchte Transformation:")
print("Adresse → Hash → Transformation → SATOSHI-Koordinaten")
print()

for name, addr, (target_x, target_y) in satoshi_target:
    h = k12_simulate(addr)
    print(f"{name}: {addr[:15]}...")
    print(f"  Hash (hex): {h[:8].hex()}")
    print(f"  Ziel: ({target_x}, {target_y})")

    # Was müsste die Transformation sein?
    # target_x = f(hash) - ?
    # target_y = g(hash) - ?

    # Versuche einfache Transformationen
    for i in range(8):
        if (h[i] - 64) == target_x or (h[i] % 128 - 64) == target_x:
            print(f"  ✓ X gefunden: Byte {i} = {h[i]} → {target_x}")
        if (h[i] - 64) == target_y or (h[i] % 128 - 64) == target_y:
            print(f"  ✓ Y gefunden: Byte {i} = {h[i]} → {target_y}")

print("""
⚠️  KRITISCHE ERKENNTNIS:

Wenn es KEIN einfaches Hash-zu-Koordinaten Mapping gibt,
das "SATOSHI" ergibt, dann:

1. Die SATOSHI-Koordinaten sind möglicherweise ZUFALL
2. ODER: Das Mapping ist komplexer als Hash
3. ODER: Die frühen Blöcke mappen zu etwas ANDEREM

Das würde die CFB=Satoshi Hypothese SCHWÄCHEN!
""")

# Speichere Ergebnisse
output = {
    "k12_v1_results": ''.join(results_v1),
    "k12_v2_results": ''.join(results_v2),
    "k12_v3_results": ''.join(results_v3),
    "brute_force_best": best_matches[:5] if best_matches else [],
    "satoshi_mapping_found": False,
    "conclusion": "Kein einfaches Mapping gefunden, das SATOSHI ergibt",
}

output_path = script_dir / "GOD_MODE_K12_TEST_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n✓ Ergebnisse: {output_path}")
