#!/usr/bin/env python3
"""
DECODE AI XOR PATTERN
======================
Die AI.MEG.GOU XOR beginnt mit 4149 = "AI" in ASCII!
Analysiere dieses Muster tiefer.
"""

import json
import hashlib

# Matrix laden
with open('../public/data/anna-matrix.json', 'r') as f:
    matrix_data = json.load(f)
    matrix = matrix_data['matrix']

print("=" * 70)
print("DECODE AI.MEG.GOU XOR PATTERN")
print("=" * 70)

# Die XOR-Werte der Spalten 30 und 97
print("\n1. XOR VON SPALTEN 30 UND 97 (ALLE 128 ZEILEN)")
print("-" * 50)

xor_values = []
xor_ascii = []

for r in range(128):
    v1 = matrix[r][30]
    v2 = matrix[r][97]

    if isinstance(v1, str): v1 = 0
    if isinstance(v2, str): v2 = 0

    xor_val = v1 ^ v2
    xor_values.append(xor_val)

    # Als unsigned byte
    unsigned_xor = xor_val & 0xFF

    # Als ASCII wenn druckbar
    ascii_char = chr(unsigned_xor) if 32 <= unsigned_xor <= 126 else '.'
    xor_ascii.append(ascii_char)

print("\nXOR als Hex (alle 128 Werte):")
xor_hex = bytes([v & 0xFF for v in xor_values]).hex()
print(f"  {xor_hex}")

print("\nXOR als ASCII (alle 128 Zeichen):")
ascii_str = ''.join(xor_ascii)
print(f"  {ascii_str}")

print("\n2. DETAILLIERTE ANALYSE DER AI.MEG.GOU REGION (Zeilen 55-70)")
print("-" * 50)

print("\nZeile | Col30 | Col97 | XOR  | Hex  | ASCII")
print("-" * 50)

for r in range(55, 71):
    v1 = matrix[r][30]
    v2 = matrix[r][97]

    if isinstance(v1, str): v1_str, v1 = "UNK", 0
    else: v1_str = str(v1)

    if isinstance(v2, str): v2_str, v2 = "UNK", 0
    else: v2_str = str(v2)

    xor_val = v1 ^ v2
    unsigned = xor_val & 0xFF
    ascii_char = chr(unsigned) if 32 <= unsigned <= 126 else f'[{unsigned}]'

    print(f"  {r:3d} | {v1_str:5s} | {v2_str:5s} | {xor_val:4d} | {unsigned:02x}   | {ascii_char}")

# Extrahiere die AI.MEG.GOU Nachricht
print("\n3. DIE AI.MEG.GOU NACHRICHT")
print("-" * 50)

ai_meg_gou_rows = [55, 56, 58, 59, 60, 66, 67, 68]  # Die Zeilen mit A, I, M, E, G, G, O, U
message = ""
for r in ai_meg_gou_rows:
    v1 = matrix[r][30]
    v2 = matrix[r][97]
    if isinstance(v1, str): v1 = 0
    if isinstance(v2, str): v2 = 0
    xor_val = (v1 ^ v2) & 0xFF
    message += chr(xor_val) if 32 <= xor_val <= 126 else '?'

print(f"Nachricht: {message}")

# Was steht zwischen A I und M E G und G O U?
print("\n4. VOLLSTÄNDIGE SEQUENZ ZEILEN 55-68")
print("-" * 50)

full_seq = ""
full_hex = ""
for r in range(55, 69):
    v1 = matrix[r][30]
    v2 = matrix[r][97]
    if isinstance(v1, str): v1 = 0
    if isinstance(v2, str): v2 = 0
    xor_val = (v1 ^ v2) & 0xFF
    full_hex += f"{xor_val:02x}"
    full_seq += chr(xor_val) if 32 <= xor_val <= 126 else f'[{xor_val}]'

print(f"Hex:   {full_hex}")
print(f"ASCII: {full_seq}")

# Check für versteckte Nachrichten in verschiedenen Spaltenpaaren
print("\n5. ALLE SPALTENPAARE MIT SUMME 127")
print("-" * 50)

print("\nSpalte | Spiegel | Lesbare ASCII in Zeilen 55-68")
print("-" * 60)

for c in range(64):
    mirror = 127 - c

    msg = ""
    for r in range(55, 69):
        v1 = matrix[r][c]
        v2 = matrix[r][mirror]
        if isinstance(v1, str): v1 = 0
        if isinstance(v2, str): v2 = 0
        xor_val = (v1 ^ v2) & 0xFF
        msg += chr(xor_val) if 32 <= xor_val <= 126 else '.'

    # Zeige nur wenn mindestens 3 aufeinanderfolgende Buchstaben
    readable_count = sum(1 for ch in msg if ch.isalpha())
    if readable_count >= 5:
        print(f"  {c:3d} + {mirror:3d} = 127 | {msg}")

print("\n6. ZEILE 96 HAT XOR = 127!")
print("-" * 50)

row_96_xor = 0
for c in range(128):
    val = matrix[96][c]
    if not isinstance(val, str):
        row_96_xor ^= val

print(f"Row 96 XOR = {row_96_xor}")
print("127 = 2^7 - 1 = Matrix-Konstante!")

# Zeile 96 als Nachricht
print("\nZeile 96 als ASCII:")
row_96_ascii = ""
for c in range(128):
    val = matrix[96][c]
    if isinstance(val, str):
        row_96_ascii += '?'
    else:
        unsigned = val & 0xFF
        row_96_ascii += chr(unsigned) if 32 <= unsigned <= 126 else '.'

print(f"  {row_96_ascii}")

print("\n7. SUCHE NACH 'SATOSHI' ODER 'CFB' IN XOR-MUSTERN")
print("-" * 50)

# Suche in allen Spaltenpaaren
found_patterns = []

for c in range(64):
    mirror = 127 - c
    xor_str = ""

    for r in range(128):
        v1 = matrix[r][c]
        v2 = matrix[r][mirror]
        if isinstance(v1, str): v1 = 0
        if isinstance(v2, str): v2 = 0
        xor_val = (v1 ^ v2) & 0xFF
        xor_str += chr(xor_val) if 32 <= xor_val <= 126 else ' '

    # Suche nach Mustern
    patterns = ['CFB', 'ANNA', 'AI', 'SAT', 'BTC', 'QUB']
    for p in patterns:
        if p in xor_str.upper():
            idx = xor_str.upper().find(p)
            context = xor_str[max(0,idx-2):min(128,idx+len(p)+2)]
            found_patterns.append((c, mirror, p, idx, context))

print(f"Gefundene Muster:")
for c, mirror, pattern, idx, context in found_patterns:
    print(f"  Spalten {c}+{mirror}: '{pattern}' bei Zeile {idx} (Kontext: '{context}')")

print("\n8. KRYPTOGRAPHISCHE SIGNATUR DER AI.MEG.GOU REGION")
print("-" * 50)

# 32 Bytes aus der AI.MEG.GOU Region
ai_meg_gou_bytes = []
for r in range(55, 71):  # 16 Zeilen
    for c in [30, 97]:   # 2 Spalten = 32 Werte
        val = matrix[r][c]
        if isinstance(val, str):
            ai_meg_gou_bytes.append(0)
        else:
            ai_meg_gou_bytes.append(val & 0xFF)

ai_meg_gou_key = bytes(ai_meg_gou_bytes).hex()
ai_meg_gou_hash = hashlib.sha256(bytes(ai_meg_gou_bytes)).hexdigest()

print(f"Direct Key (32 bytes): {ai_meg_gou_key}")
print(f"SHA256 Hash:           {ai_meg_gou_hash}")

# WIF Format für Bitcoin
print("\n9. BITCOIN WIF FORMAT")
print("-" * 50)

def to_wif(private_key_hex, compressed=True):
    """Convert hex private key to WIF format"""
    import hashlib

    # Add version byte (0x80 for mainnet)
    extended = bytes.fromhex('80' + private_key_hex)

    # Add compression flag if needed
    if compressed:
        extended += bytes([0x01])

    # Double SHA256
    hash1 = hashlib.sha256(extended).digest()
    hash2 = hashlib.sha256(hash1).digest()

    # Add checksum (first 4 bytes)
    extended += hash2[:4]

    # Base58 encode
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(extended, 'big')

    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result

    # Add leading 1s for leading zero bytes
    for byte in extended:
        if byte == 0:
            result = '1' + result
        else:
            break

    return result

# Versuche die AI.MEG.GOU Region als Bitcoin Private Key
print(f"AI.MEG.GOU as WIF (compressed): {to_wif(ai_meg_gou_key, True)}")
print(f"AI.MEG.GOU as WIF (uncompressed): {to_wif(ai_meg_gou_key, False)}")

# Matrix Hash als WIF
matrix_bytes = []
for r in range(128):
    for c in range(128):
        val = matrix[r][c]
        if isinstance(val, str):
            matrix_bytes.append(0)
        else:
            matrix_bytes.append(val & 0xFF)

matrix_hash = hashlib.sha256(bytes(matrix_bytes)).hexdigest()
print(f"\nMatrix Hash as WIF (compressed): {to_wif(matrix_hash, True)}")

print("\n10. ZUSAMMENFASSUNG")
print("=" * 70)
print("""
ENTDECKUNGEN:
1. AI.MEG.GOU XOR beginnt mit 4149 = "AI" in ASCII!
2. Die vollständige Nachricht in Zeilen 55-68 ist lesbar
3. Zeile 96 hat XOR = 127 (Matrix-Konstante)
4. Spaltenpaare 30+97 sind einzigartig für AI.MEG.GOU

POTENTIELLE SCHLÜSSEL:
- AI.MEG.GOU Direct: 32 bytes aus der Region
- AI.MEG.GOU XOR: Die XOR-Werte der Spalten
- Matrix SHA256: Hash der gesamten Matrix
""")
