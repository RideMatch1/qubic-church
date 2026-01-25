#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                          GOD MODE: GENESIS ADDRESS MAPPING
═══════════════════════════════════════════════════════════════════════════════
Mappe die ersten Bitcoin-Adressen (Genesis, Block 1-10) auf die Anna-Matrix.
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from collections import Counter

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
    return int(matrix[row, col])

print("═" * 80)
print("                    GOD MODE: GENESIS ADDRESS MAPPING")
print("═" * 80)

# =============================================================================
# GENESIS UND FRÜHE ADRESSEN
# =============================================================================

# Block 0 (Genesis) - Satoshi
genesis_addresses = [
    ("Block 0 - Genesis", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
]

# Blocks 1-9 (erste Mining-Blöcke)
early_blocks = [
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

# Satoshi's letzte bekannte Adresse
satoshi_last = [
    ("Satoshi Last Known", "1HQ3Go3ggs8pFnXuHVHRytPCq5fGG8Hbhx"),
]

# CFB-Pattern Adressen (1CFB...)
cfb_addresses = [
    ("1CFB Pattern 1", "1CFBdvaiCFc4FpZv1gXKS6R3gUhVMRBknj"),
    ("1CFB Pattern 2", "1CFB1CFB1CFB1CFB1CFB1CFB1CFB1CFB12"),  # Hypothetisch
]

all_addresses = genesis_addresses + early_blocks + satoshi_last

# =============================================================================
# ADRESSE ZU KOORDINATEN MAPPING
# =============================================================================
print("\n" + "─" * 80)
print("1. ADRESS-HASH ZU KOORDINATEN")
print("─" * 80)

def address_to_coords_sha256(address):
    """Methode 1: SHA256 der Adresse → erste 2 Bytes als Koordinaten."""
    h = hashlib.sha256(address.encode()).digest()
    x = (h[0] - 64)  # Zentriert: -64 bis +63
    y = (h[1] - 64)
    return x, y

def address_to_coords_k12(address):
    """Methode 2: K12-ähnlich (simuliert mit SHA256 + Twist)."""
    h = hashlib.sha256(address.encode()).digest()
    # Simuliere K12 mit XOR-Twist
    x = ((h[0] ^ h[2]) - 64)
    y = ((h[1] ^ h[3]) - 64)
    return x, y

def address_to_coords_base58(address):
    """Methode 3: Direkt aus Base58 Zeichen."""
    base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    if len(address) < 4:
        return 0, 0
    x = (base58_chars.index(address[1]) - 29) if address[1] in base58_chars else 0
    y = (base58_chars.index(address[2]) - 29) if address[2] in base58_chars else 0
    return x, y

def address_to_coords_qubic(address):
    """Methode 4: Qubic-Style (XOR der Hash-Bytes)."""
    h = hashlib.sha256(address.encode()).digest()
    x = 0
    y = 0
    for i in range(0, 32, 2):
        x ^= h[i]
        y ^= h[i+1]
    x = (x % 128) - 64
    y = (y % 128) - 64
    return x, y

print("\nMapping-Methoden für Genesis-Adressen:")
print("-" * 80)

results = []

for name, addr in all_addresses:
    sha_x, sha_y = address_to_coords_sha256(addr)
    k12_x, k12_y = address_to_coords_k12(addr)
    b58_x, b58_y = address_to_coords_base58(addr)
    qub_x, qub_y = address_to_coords_qubic(addr)

    sha_val = lookup(sha_x, sha_y)
    k12_val = lookup(k12_x, k12_y)
    b58_val = lookup(b58_x, b58_y)
    qub_val = lookup(qub_x, qub_y)

    result = {
        "name": name,
        "address": addr,
        "sha256": {"x": sha_x, "y": sha_y, "value": sha_val},
        "k12": {"x": k12_x, "y": k12_y, "value": k12_val},
        "base58": {"x": b58_x, "y": b58_y, "value": b58_val},
        "qubic": {"x": qub_x, "y": qub_y, "value": qub_val},
    }
    results.append(result)

    print(f"\n{name}:")
    print(f"  Adresse: {addr[:20]}...")
    print(f"  SHA256:  Anna({sha_x:4d},{sha_y:4d}) = {sha_val:4d}")
    print(f"  K12:     Anna({k12_x:4d},{k12_y:4d}) = {k12_val:4d}")
    print(f"  Base58:  Anna({b58_x:4d},{b58_y:4d}) = {b58_val:4d}")
    print(f"  Qubic:   Anna({qub_x:4d},{qub_y:4d}) = {qub_val:4d}")

# =============================================================================
# 2. PATTERN-ANALYSE
# =============================================================================
print("\n" + "─" * 80)
print("2. PATTERN-ANALYSE DER GENESIS-WERTE")
print("─" * 80)

# Sammle alle Werte pro Methode
sha_values = [r["sha256"]["value"] for r in results]
k12_values = [r["k12"]["value"] for r in results]
qub_values = [r["qubic"]["value"] for r in results]

print("\nWert-Verteilung pro Methode:")
print(f"  SHA256: {Counter(sha_values).most_common(5)}")
print(f"  K12:    {Counter(k12_values).most_common(5)}")
print(f"  Qubic:  {Counter(qub_values).most_common(5)}")

# Gibt es Wiederholungen?
print("\nWiederholte Werte (Kollisionen):")
for method, values in [("SHA256", sha_values), ("K12", k12_values), ("Qubic", qub_values)]:
    counts = Counter(values)
    repeated = [(v, c) for v, c in counts.items() if c > 1]
    if repeated:
        print(f"  {method}: {repeated}")
    else:
        print(f"  {method}: Keine Kollisionen")

# =============================================================================
# 3. SIGNIFIKANTE WERTE SUCHEN
# =============================================================================
print("\n" + "─" * 80)
print("3. SUCHE NACH SIGNIFIKANTEN WERTEN")
print("─" * 80)

significant = [-114, -113, 14, 100, 27, 127]
print(f"\nSignifikante Werte: {significant}")

for r in results:
    for method in ["sha256", "k12", "qubic"]:
        val = r[method]["value"]
        if val in significant:
            print(f"  {r['name']} ({method}): {val} ← SIGNIFIKANT!")

# =============================================================================
# 4. GENESIS ADRESSE SPEZIAL-ANALYSE
# =============================================================================
print("\n" + "─" * 80)
print("4. GENESIS ADRESSE TIEFEN-ANALYSE")
print("─" * 80)

genesis = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
print(f"\nGenesis: {genesis}")

# Alle möglichen Koordinaten-Methoden
methods = {
    "SHA256 Byte 0,1": address_to_coords_sha256(genesis),
    "K12 Simulation": address_to_coords_k12(genesis),
    "Base58 Chars": address_to_coords_base58(genesis),
    "Qubic XOR": address_to_coords_qubic(genesis),
}

# Zusätzliche Methoden
h = hashlib.sha256(genesis.encode()).digest()
methods["SHA256 Byte 2,3"] = ((h[2] - 64), (h[3] - 64))
methods["SHA256 Byte 4,5"] = ((h[4] - 64), (h[5] - 64))
methods["SHA256 Sum mod 128"] = ((sum(h[:16]) % 128 - 64), (sum(h[16:]) % 128 - 64))

print("\nAlle Mapping-Methoden:")
for method, (x, y) in methods.items():
    val = lookup(x, y)
    row, col = anna_to_matrix(x, y)
    print(f"  {method:20s}: Anna({x:4d},{y:4d}) → Matrix[{row:3d},{col:3d}] = {val:4d}")

# =============================================================================
# 5. CLUSTER-ANALYSE
# =============================================================================
print("\n" + "─" * 80)
print("5. CLUSTER-ANALYSE DER POSITIONEN")
print("─" * 80)

# Sind die Positionen geclustert?
sha_coords = [(r["sha256"]["x"], r["sha256"]["y"]) for r in results]
qub_coords = [(r["qubic"]["x"], r["qubic"]["y"]) for r in results]

def calculate_spread(coords):
    """Berechne die Streuung der Koordinaten."""
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    x_range = max(xs) - min(xs)
    y_range = max(ys) - min(ys)
    return x_range, y_range, np.std(xs), np.std(ys)

sha_spread = calculate_spread(sha_coords)
qub_spread = calculate_spread(qub_coords)

print("\nStreuung der Koordinaten:")
print(f"  SHA256: X-Range={sha_spread[0]}, Y-Range={sha_spread[1]}, StdX={sha_spread[2]:.1f}, StdY={sha_spread[3]:.1f}")
print(f"  Qubic:  X-Range={qub_spread[0]}, Y-Range={qub_spread[1]}, StdX={qub_spread[2]:.1f}, StdY={qub_spread[3]:.1f}")

# =============================================================================
# 6. ROW/COL ANALYSE
# =============================================================================
print("\n" + "─" * 80)
print("6. ROW/COL ANALYSE")
print("─" * 80)

sha_rows = [anna_to_matrix(r["sha256"]["x"], r["sha256"]["y"])[0] for r in results]
sha_cols = [anna_to_matrix(r["sha256"]["x"], r["sha256"]["y"])[1] for r in results]

print("\nSHA256 Matrix-Positionen:")
print(f"  Rows: {sha_rows}")
print(f"  Cols: {sha_cols}")

# Row%8 Analyse
row_mod8 = [r % 8 for r in sha_rows]
print(f"  Row%8: {row_mod8}")
print(f"  Row%8 Verteilung: {Counter(row_mod8)}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "═" * 80)
print("                         GENESIS MAPPING FAZIT")
print("═" * 80)

print(f"""
ERGEBNISSE:

1. GENESIS-ADRESSE:
   - Verschiedene Hash-Methoden → verschiedene Positionen
   - Kein einzelner "korrekter" Hash gefunden
   - Weitere Untersuchung nötig

2. PATTERN:
   - SHA256 Werte: {Counter(sha_values).most_common(3)}
   - Keine offensichtlichen Kollisionen

3. CLUSTER:
   - SHA256 verteilt Adressen pseudo-zufällig
   - Qubic XOR-Methode zeigt ähnliche Streuung

4. SIGNIFIKANTE WERTE:
   - Suche nach -114, -113, 14, 100, 27, 127
   - Ergebnisse oben dokumentiert

NÄCHSTE SCHRITTE:
- Mehr Adressen testen (Patoshi-Set)
- Andere Hash-Methoden probieren (echtes K12)
- Korrelation mit bekannten Anna-Bot Koordinaten suchen
""")

# Speichere
output = {
    "addresses_mapped": len(results),
    "results": results,
    "sha256_values": sha_values,
    "patterns_found": dict(Counter(sha_values)),
}

output_path = script_dir / "GOD_MODE_GENESIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse: {output_path}")
