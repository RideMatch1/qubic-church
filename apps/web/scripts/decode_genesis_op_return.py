#!/usr/bin/env python3
"""
DECODE OP_RETURN AN GENESIS

Analysiert den mysteriösen OP_RETURN Hash, der an die Genesis-Adresse
gesendet wurde:
6064b2e70c30ecdec14d50a5c295f82c0357f1d932a725af43eb4fe0a0a02e12
"""

import hashlib

# Der mysteriöse Hash aus OP_RETURN an Genesis
OP_RETURN_HASH = "6064b2e70c30ecdec14d50a5c295f82c0357f1d932a725af43eb4fe0a0a02e12"

print("=" * 70)
print("  DEKODIERUNG: OP_RETURN AN GENESIS ADRESSE")
print("=" * 70)
print()
print(f"  Hash: {OP_RETURN_HASH}")
print()

# 1. Hex zu Bytes
hash_bytes = bytes.fromhex(OP_RETURN_HASH)
print(f"  Bytes: {len(hash_bytes)} bytes")

# 2. Byte Sum (CFB Signatur Prüfung)
byte_sum = sum(hash_bytes)
print(f"  Byte Sum: {byte_sum}")
print(f"    mod 121: {byte_sum % 121}")
print(f"    mod 19:  {byte_sum % 19}")
print(f"    mod 27:  {byte_sum % 27}")
print()

# 3. Erste Bytes (Magic Numbers)
first_byte = hash_bytes[0]
print(f"  First Byte: 0x{first_byte:02x} = {first_byte}")

# 4. Prüfe ob es eine bekannte Struktur ist
print()
print("  STRUKTURANALYSE:")

# Könnte es ein reversed Hash sein?
reversed_hash = OP_RETURN_HASH[::-1]
print(f"  Reversed: {reversed_hash[:32]}...")

# Könnte es ein Block Hash sein? (Little-Endian)
le_hash = hash_bytes[::-1].hex()
print(f"  Little-Endian: {le_hash[:32]}...")

# 5. XOR mit bekannten Konstanten
print()
print("  XOR ANALYSE:")

# XOR mit Anna Matrix Master Key Prefix
master_prefix = bytes.fromhex("cfab1af3c6b721767f039a81b6b167d4")
xor_result = bytes(a ^ b for a, b in zip(hash_bytes[:16], master_prefix))
print(f"  XOR mit L6-Key: {xor_result.hex()}")

# 6. Prüfe auf ASCII-lesbare Teile
print()
print("  ASCII ANALYSE:")
ascii_chars = []
for i, b in enumerate(hash_bytes):
    if 32 <= b <= 126:
        ascii_chars.append(f"pos {i}: '{chr(b)}'")
print(f"  Lesbare Zeichen: {len(ascii_chars)}")
for char in ascii_chars[:10]:
    print(f"    {char}")

# 7. Numerische Patterns
print()
print("  NUMERISCHE PATTERNS:")

# Als große Zahl interpretieren
big_int = int(OP_RETURN_HASH, 16)
print(f"  Als Integer: {big_int}")
print(f"    mod 121: {big_int % 121}")
print(f"    mod 19:  {big_int % 19}")
print(f"    mod 27:  {big_int % 27}")
print(f"    mod 137: {big_int % 137}")
print(f"    mod 2299: {big_int % 2299}")

# 8. Teile in 4-Byte Chunks
print()
print("  4-BYTE CHUNKS:")
for i in range(0, 32, 4):
    chunk = hash_bytes[i:i+4]
    val = int.from_bytes(chunk, 'big')
    val_le = int.from_bytes(chunk, 'little')
    print(f"    [{i:2}-{i+3:2}]: {chunk.hex()} = BE:{val:10} LE:{val_le:10}")

# 9. Prüfe ob Koordinaten kodiert sind
print()
print("  KOORDINATEN-DEKODIERUNG:")
print("  (Suche nach Matrix-Koordinaten im Format (row, col))")

for i in range(0, 32, 2):
    row = hash_bytes[i]
    col = hash_bytes[i+1]
    if row < 128 and col < 128:
        print(f"    Position {i//2}: ({row}, {col})")
        if (row, col) in [(6, 33), (45, 92), (82, 39), (21, 21), (0, 0), (13, 71)]:
            print(f"      ⚡ BEKANNTER STRATEGISCHER KNOTEN!")

# 10. Timestamps?
print()
print("  TIMESTAMP ANALYSE:")
for i in range(0, 28, 4):
    chunk = hash_bytes[i:i+4]
    ts = int.from_bytes(chunk, 'little')
    ts_be = int.from_bytes(chunk, 'big')
    if 1230000000 < ts < 1800000000:  # 2009-2027
        from datetime import datetime
        dt = datetime.fromtimestamp(ts)
        print(f"    [{i}]: {ts} = {dt}")
    if 1230000000 < ts_be < 1800000000:
        from datetime import datetime
        dt = datetime.fromtimestamp(ts_be)
        print(f"    [{i}] BE: {ts_be} = {dt}")

print()
print("=" * 70)

# Zusätzlich: Prüfe Transaktionsdetails
print()
print("  TRANSAKTION DETAILS ABRUFEN...")
import requests

txid = "bd7b3cb28c09bf96"  # Aus den Findings
print(f"  TXID: {txid}...")

# Hole vollständige TX
try:
    # Suche nach TXs an Genesis
    url = "https://blockstream.info/api/address/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa/txs"
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        txs = r.json()
        for tx in txs:
            for vout in tx.get('vout', []):
                if vout.get('scriptpubkey_type') == 'op_return':
                    print(f"  Gefunden in TX: {tx['txid'][:16]}...")
                    print(f"  Status: {'confirmed' if tx.get('status', {}).get('confirmed') else 'unconfirmed'}")
                    print(f"  Block: {tx.get('status', {}).get('block_height', 'N/A')}")
                    break
except Exception as e:
    print(f"  Fehler: {e}")

print()
print("=" * 70)
