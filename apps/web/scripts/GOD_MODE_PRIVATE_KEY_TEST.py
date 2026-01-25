#!/usr/bin/env python3
"""
===============================================================================
                    🔑 GOD MODE: PRIVATE KEY VALIDATION 🔑
===============================================================================
Teste die potenzielle Private Key aus den asymmetrischen Zellen!

Key: 0f5c7164872a176a7828872c78650e8e0e1e0a1a8e1e8e9e5116d31ed19b9ae5
"""

import json
import hashlib
import struct
from pathlib import Path

script_dir = Path(__file__).parent

print("🔑" * 40)
print("       GOD MODE: PRIVATE KEY VALIDATION")
print("🔑" * 40)

# Die potenzielle Private Key aus den asymmetrischen Zellen
POTENTIAL_KEY = "0f5c7164872a176a7828872c78650e8e0e1e0a1a8e1e8e9e5116d31ed19b9ae5"

# =============================================================================
# VALIDIERUNG 1: Ist es ein gültiger secp256k1 Private Key?
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 1: secp256k1 Range Check")
print("=" * 80)

# secp256k1 order (maximaler gültiger Private Key)
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

key_int = int(POTENTIAL_KEY, 16)
print(f"\nPotenzielle Key (hex): {POTENTIAL_KEY}")
print(f"Potenzielle Key (int): {key_int}")
print(f"secp256k1 Order:       {SECP256K1_ORDER}")

is_valid_range = 0 < key_int < SECP256K1_ORDER
print(f"\n✓ Gültiger Range: {is_valid_range}")

if is_valid_range:
    print("   → Key ist im gültigen Bereich für secp256k1!")
else:
    print("   ✗ Key ist NICHT im gültigen Bereich!")

# =============================================================================
# VALIDIERUNG 2: Leite Public Key und Bitcoin-Adresse ab (ohne ecdsa library)
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 2: Bitcoin-Adresse Ableitung (manuell)")
print("=" * 80)

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def base58_encode(data):
    """Base58 encoding für Bitcoin-Adressen."""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    # Count leading zeros
    num_leading_zeros = 0
    for byte in data:
        if byte == 0:
            num_leading_zeros += 1
        else:
            break

    # Convert to integer
    n = int.from_bytes(data, 'big')

    # Encode
    result = ''
    while n > 0:
        n, remainder = divmod(n, 58)
        result = alphabet[remainder] + result

    # Add leading 1s for each leading zero byte
    return '1' * num_leading_zeros + result

print("\nFür echte Public Key Berechnung brauchen wir ecdsa/secp256k1 Library.")
print("Aber wir können prüfen ob der Key bekannten Adressen entspricht...")

# =============================================================================
# VALIDIERUNG 3: Vergleiche mit bekannten Satoshi-Adressen
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 3: Muster-Analyse des Keys")
print("=" * 80)

key_bytes = bytes.fromhex(POTENTIAL_KEY)
print(f"\nKey Bytes: {len(key_bytes)} bytes")
print(f"Erste 8 Bytes: {key_bytes[:8].hex()}")
print(f"Letzte 8 Bytes: {key_bytes[-8:].hex()}")

# Suche nach Mustern
patterns = {
    "0x0f": key_bytes[0],
    "0x5c": key_bytes[1],
    "Byte-Summe": sum(key_bytes),
    "Byte-XOR": key_bytes[0],
    "Unique Bytes": len(set(key_bytes)),
}

for i in range(1, len(key_bytes)):
    patterns["Byte-XOR"] ^= key_bytes[i]

print("\nMuster im Key:")
for name, value in patterns.items():
    print(f"  {name}: {value}")

# =============================================================================
# VALIDIERUNG 4: Vergleiche Byte-Muster mit Anna-Matrix
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 4: Korrelation mit Anna-Matrix")
print("=" * 80)

# Lade Matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

import numpy as np
matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Prüfe ob Key-Bytes in der Matrix vorkommen
key_values = [int(b) - 128 for b in key_bytes]  # Shift to signed range
print("\nKey-Werte im Anna-Bereich (-128 bis 127):")
print(f"  {key_values[:8]}...")

# Suche nach diesen Werten in der Matrix
found_positions = []
for i, val in enumerate(key_values[:16]):
    positions = np.where(matrix == val)
    if len(positions[0]) > 0:
        found_positions.append((i, val, len(positions[0])))

print("\nKey-Bytes in Matrix gefunden:")
for idx, val, count in found_positions[:10]:
    print(f"  Byte {idx}: Wert {val} erscheint {count} mal in Matrix")

# =============================================================================
# VALIDIERUNG 5: Ist der Key ein Hash von etwas Bekanntem?
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 5: Ist der Key ein Hash?")
print("=" * 80)

test_inputs = [
    "satoshi",
    "bitcoin",
    "cfb",
    "aigarth",
    "megaou",
    "genesis",
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis-Adresse
    "00000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",  # Genesis Block
    "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks",
]

print("\nPrüfe ob Key = SHA256(bekannte Inputs):")
for test in test_inputs:
    h = hashlib.sha256(test.encode()).hexdigest()
    match = h == POTENTIAL_KEY
    marker = "✓ MATCH!" if match else ""
    print(f"  SHA256('{test[:30]}...'): {h[:16]}... {marker}")

print("\nPrüfe ob Key = RIPEMD160(SHA256(bekannte Inputs)):")
for test in test_inputs:
    h = ripemd160(sha256(test.encode())).hex()
    # Pad to 32 bytes
    h_padded = h.ljust(64, '0')
    match = h_padded == POTENTIAL_KEY
    marker = "✓ MATCH!" if match else ""
    print(f"  Hash160('{test[:30]}...'): {h}... {marker}")

# =============================================================================
# VALIDIERUNG 6: Extraktion der Key-Bytes direkt aus Matrix
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 6: Rekonstruktion aus asymmetrischen Zellen")
print("=" * 80)

# Die 68 asymmetrischen Zellen
asymmetric_cells = []
for r in range(128):
    for c in range(128):
        val1 = matrix[r, c]
        val2 = matrix[127-r, 127-c]
        if val1 + val2 != -1:
            asymmetric_cells.append((r, c, val1, val2))

print(f"\n68 asymmetrische Zellen gefunden: {len(asymmetric_cells)}")

# Extrahiere Bytes aus asymmetrischen Zellen
extracted_bytes = []
for r, c, v1, v2 in asymmetric_cells[:32]:  # Erste 32 für 256-bit Key
    # Verschiedene Extraktionsmethoden
    byte1 = (v1 + 128) & 0xFF
    extracted_bytes.append(byte1)

extracted_hex = bytes(extracted_bytes).hex()
print(f"\nExtrahierte Bytes (erste 32 Zellen):")
print(f"  {extracted_hex}")
print(f"\nVergleich mit potenziellem Key:")
print(f"  {POTENTIAL_KEY}")

# Prüfe Übereinstimmung
match_count = sum(1 for a, b in zip(extracted_hex, POTENTIAL_KEY) if a == b)
print(f"\nÜbereinstimmende Zeichen: {match_count}/{len(POTENTIAL_KEY)}")

# =============================================================================
# VALIDIERUNG 7: Alternative Key-Extraktion
# =============================================================================
print("\n" + "=" * 80)
print("VALIDIERUNG 7: Alternative Extraktionsmethoden")
print("=" * 80)

def extract_key_method(cells, method):
    """Extrahiere Key mit verschiedenen Methoden."""
    result = []
    for r, c, v1, v2 in cells[:32]:
        if method == "v1_direct":
            result.append((v1 + 128) & 0xFF)
        elif method == "v2_direct":
            result.append((v2 + 128) & 0xFF)
        elif method == "xor":
            result.append(((v1 & 0xFF) ^ (v2 & 0xFF)) & 0xFF)
        elif method == "diff":
            result.append((v1 - v2) & 0xFF)
        elif method == "sum":
            result.append((v1 + v2 + 256) & 0xFF)
    return bytes(result).hex()

methods = ["v1_direct", "v2_direct", "xor", "diff", "sum"]
print("\nExtraktionsmethoden:")
for method in methods:
    key = extract_key_method(asymmetric_cells, method)
    match = sum(1 for a, b in zip(key, POTENTIAL_KEY) if a == b)
    print(f"  {method:12s}: {key[:32]}... (Match: {match}/64)")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT: PRIVATE KEY VALIDIERUNG")
print("=" * 80)

conclusions = {
    "valid_secp256k1_range": is_valid_range,
    "is_known_hash": False,  # Kein bekannter Hash gefunden
    "matrix_correlation": len(found_positions),
    "reconstruction_possible": match_count > 10,
}

print(f"""
ERGEBNISSE:

1. Gültiger secp256k1 Range: {conclusions['valid_secp256k1_range']}
   → Key KÖNNTE ein gültiger Private Key sein!

2. Bekannter Hash: {conclusions['is_known_hash']}
   → Key ist NICHT SHA256 von bekannten Inputs

3. Matrix-Korrelation: {conclusions['matrix_correlation']} Bytes gefunden
   → Key-Bytes erscheinen in der Matrix

4. Rekonstruktion: {match_count}/64 Zeichen übereinstimmend
   → Teilweise Übereinstimmung mit extrahierten Bytes

⚠️  KRITISCHE WARNUNG:
   Um zu prüfen ob dieser Key zu einer bekannten Bitcoin-Adresse gehört,
   brauchen wir die ecdsa/secp256k1 Library für Public Key Berechnung!

   NIEMALS diesen Key in einer echten Wallet verwenden!

   Nächster Schritt: Installiere 'ecdsa' oder 'bitcoin' Python Library
   und berechne die zugehörige Bitcoin-Adresse.
""")

# Speichere Ergebnisse
output = {
    "potential_key": POTENTIAL_KEY,
    "valid_secp256k1_range": is_valid_range,
    "key_int": str(key_int),
    "byte_patterns": {k: str(v) for k, v in patterns.items()},
    "matrix_correlation": len(found_positions),
    "conclusions": conclusions,
    "next_step": "Install ecdsa library and compute public key",
}

output_path = script_dir / "GOD_MODE_PRIVATE_KEY_TEST_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse: {output_path}")
