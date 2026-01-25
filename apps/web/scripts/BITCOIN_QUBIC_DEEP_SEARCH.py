#!/usr/bin/env python3
"""
BITCOIN & QUBIC DEEP SEARCH
============================
Sucht nach versteckten kryptographischen Daten in der Anna Matrix.

Fokus:
- Bitcoin Private Keys (32 bytes / 64 hex chars)
- Qubic Seeds (55 lowercase letters)
- Wallet-Adressen (Base58 / Bech32)
"""

import json
import hashlib
import struct

# Matrix laden
with open('../public/data/anna-matrix.json', 'r') as f:
    matrix_data = json.load(f)
    matrix = matrix_data['matrix']

print("=" * 70)
print("BITCOIN & QUBIC DEEP SEARCH - Anna Matrix")
print("=" * 70)

# ============================================================
# 1. AI.MEG.GOU REGION ALS PRIVATE KEY
# ============================================================
print("\n" + "=" * 70)
print("1. AI.MEG.GOU REGION ALS BITCOIN PRIVATE KEY")
print("=" * 70)

# Die AI.MEG.GOU Region: Spalten 30 und 97, Zeilen 55-68
ai_meg_gou_rows = list(range(55, 71))  # 16 rows for 32 bytes
ai_meg_gou_cols = [30, 97]

# Method 1: Direct bytes
key_bytes_1 = []
for r in ai_meg_gou_rows:
    for c in ai_meg_gou_cols:
        val = matrix[r][c]
        if isinstance(val, str):
            key_bytes_1.append(0)
        else:
            key_bytes_1.append(val & 0xFF)

key_hex_1 = bytes(key_bytes_1).hex()
print(f"\nMethod 1 - Direct bytes (rows 55-70, cols 30+97):")
print(f"  Hex: {key_hex_1}")
print(f"  Length: {len(key_hex_1)} chars ({len(key_bytes_1)} bytes)")

# Method 2: XOR values
key_bytes_2 = []
for r in ai_meg_gou_rows[:32]:  # 32 rows = 32 bytes
    v1 = matrix[r][30]
    v2 = matrix[r][97]
    if isinstance(v1, str): v1 = 0
    if isinstance(v2, str): v2 = 0
    xor_val = (v1 ^ v2) & 0xFF
    key_bytes_2.append(xor_val)

key_hex_2 = bytes(key_bytes_2).hex()
print(f"\nMethod 2 - XOR(col30, col97) for rows 55-86:")
print(f"  Hex: {key_hex_2}")
print(f"  Length: {len(key_hex_2)} chars")

# Method 3: Absolute values mod 256
key_bytes_3 = []
for r in range(55, 55+16):
    for c in [30, 97]:
        val = matrix[r][c]
        if isinstance(val, str):
            key_bytes_3.append(0)
        else:
            key_bytes_3.append(abs(val) % 256)

key_hex_3 = bytes(key_bytes_3).hex()
print(f"\nMethod 3 - Absolute values mod 256:")
print(f"  Hex: {key_hex_3}")

# ============================================================
# 2. DIAGONALE ALS PRIVATE KEY
# ============================================================
print("\n" + "=" * 70)
print("2. DIAGONALE ALS BITCOIN PRIVATE KEY")
print("=" * 70)

# Main diagonal
diag_bytes = []
for i in range(32):
    val = matrix[i][i]
    if isinstance(val, str):
        diag_bytes.append(0)
    else:
        diag_bytes.append(val & 0xFF)

diag_hex = bytes(diag_bytes).hex()
print(f"\nMain diagonal (0-31):")
print(f"  Hex: {diag_hex}")

# Anti-diagonal
anti_diag_bytes = []
for i in range(32):
    val = matrix[i][127-i]
    if isinstance(val, str):
        anti_diag_bytes.append(0)
    else:
        anti_diag_bytes.append(val & 0xFF)

anti_diag_hex = bytes(anti_diag_bytes).hex()
print(f"\nAnti-diagonal (0-31):")
print(f"  Hex: {anti_diag_hex}")

# Center diagonal
center_diag_bytes = []
for i in range(32):
    val = matrix[48+i][48+i]
    if isinstance(val, str):
        center_diag_bytes.append(0)
    else:
        center_diag_bytes.append(val & 0xFF)

center_diag_hex = bytes(center_diag_bytes).hex()
print(f"\nCenter diagonal (48-79):")
print(f"  Hex: {center_diag_hex}")

# ============================================================
# 3. UNKNOWN POSITIONEN ALS SCHLÜSSEL
# ============================================================
print("\n" + "=" * 70)
print("3. UNKNOWN POSITIONEN")
print("=" * 70)

unknowns = []
for r in range(128):
    for c in range(128):
        if isinstance(matrix[r][c], str):
            unknowns.append((r, c))

print(f"\n26 UNKNOWN Positionen:")
for i, (r, c) in enumerate(unknowns):
    mirror_r, mirror_c = 127-r, 127-c
    mirror_val = matrix[mirror_r][mirror_c]
    print(f"  {i+1:2d}. [{r:3d},{c:3d}] -> Mirror [{mirror_r:3d},{mirror_c:3d}] = {mirror_val}")

# Encode UNKNOWN positions as bytes
unknown_pos_bytes = []
for r, c in unknowns:
    unknown_pos_bytes.append(r)
    unknown_pos_bytes.append(c)

unknown_pos_hex = bytes(unknown_pos_bytes).hex()
print(f"\nUNKNOWN positions as bytes (r,c pairs):")
print(f"  Hex: {unknown_pos_hex}")
print(f"  Length: {len(unknown_pos_hex)} chars ({len(unknown_pos_bytes)} bytes)")

# UNKNOWN columns only
unknown_cols = [c for r, c in unknowns]
unknown_cols_unique = sorted(set(unknown_cols))
print(f"\nUnique UNKNOWN columns: {unknown_cols_unique}")
print(f"  Sum: {sum(unknown_cols_unique)}")

# Check for 137 combinations
print(f"\n137 combinations from UNKNOWN columns:")
for i, c1 in enumerate(unknown_cols_unique):
    for c2 in unknown_cols_unique[i+1:]:
        if c1 + c2 == 137:
            print(f"  {c1} + {c2} = 137")
    for c2 in unknown_cols_unique[i+1:]:
        for c3 in unknown_cols_unique:
            if c1 + c2 + c3 == 137 and c3 > c2:
                print(f"  {c1} + {c2} + {c3} = 137")

# ============================================================
# 4. ZEILEN MIT SPEZIELLEN SUMMEN
# ============================================================
print("\n" + "=" * 70)
print("4. ZEILEN MIT SPEZIELLEN EIGENSCHAFTEN")
print("=" * 70)

row_sums = []
for r in range(128):
    row_sum = 0
    for c in range(128):
        val = matrix[r][c]
        if not isinstance(val, str):
            row_sum += val
    row_sums.append(row_sum)

# Find special rows
print("\nZeilen mit selbst-referenzieller Summe (sum = k*row):")
for r, s in enumerate(row_sums):
    if s != 0 and s % (r+1) == 0 and abs(s // (r+1)) <= 128:
        print(f"  Row {r}: sum={s}, factor={s//(r+1) if r > 0 else 'N/A'}")

print("\nZeilen 51 und 76 (die Spiegel-Zeilen):")
print(f"  Row 51: sum = {row_sums[51]} = {row_sums[51]//51 if row_sums[51] % 51 == 0 else '?'} × 51")
print(f"  Row 76: sum = {row_sums[76]} = {row_sums[76]//51 if row_sums[76] % 51 == 0 else '?'} × 51")
print(f"  51 + 76 = {51 + 76}")

# ============================================================
# 5. QUBIC SEEDS AUS DER MATRIX
# ============================================================
print("\n" + "=" * 70)
print("5. QUBIC SEEDS GENERIERUNG")
print("=" * 70)

def matrix_to_qubic_seed(method='diagonal'):
    """Generate a 55-character lowercase seed"""
    seed_chars = []

    if method == 'diagonal':
        for i in range(55):
            val = matrix[i][i]
            if isinstance(val, str):
                seed_chars.append('a')
            else:
                char_idx = abs(val) % 26
                seed_chars.append(chr(ord('a') + char_idx))

    elif method == 'ai_meg_gou_xor':
        for r in range(55):
            v1 = matrix[r][30] if not isinstance(matrix[r][30], str) else 0
            v2 = matrix[r][97] if not isinstance(matrix[r][97], str) else 0
            xor_val = v1 ^ v2
            char_idx = abs(xor_val) % 26
            seed_chars.append(chr(ord('a') + char_idx))

    elif method == 'row_51':
        for c in range(55):
            val = matrix[51][c]
            if isinstance(val, str):
                seed_chars.append('a')
            else:
                char_idx = abs(val) % 26
                seed_chars.append(chr(ord('a') + char_idx))

    elif method == 'center':
        idx = 0
        for r in range(64-4, 64+4):
            for c in range(64-4, 64+4):
                if idx >= 55:
                    break
                val = matrix[r][c]
                if isinstance(val, str):
                    seed_chars.append('a')
                else:
                    char_idx = abs(val) % 26
                    seed_chars.append(chr(ord('a') + char_idx))
                idx += 1

    elif method == 'fibonacci':
        fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i in range(55):
            r = fib[i % len(fib)] % 128
            c = fib[(i + 1) % len(fib)] % 128
            val = matrix[r][c]
            if isinstance(val, str):
                seed_chars.append('a')
            else:
                char_idx = abs(val) % 26
                seed_chars.append(chr(ord('a') + char_idx))

    return ''.join(seed_chars)

seeds = {
    'diagonal': matrix_to_qubic_seed('diagonal'),
    'ai_meg_gou_xor': matrix_to_qubic_seed('ai_meg_gou_xor'),
    'row_51': matrix_to_qubic_seed('row_51'),
    'center': matrix_to_qubic_seed('center'),
    'fibonacci': matrix_to_qubic_seed('fibonacci'),
}

print("\nGenerierte Qubic Seeds (55 lowercase chars):")
for name, seed in seeds.items():
    print(f"\n  {name}:")
    print(f"    {seed}")
    # SHA256 des Seeds
    seed_hash = hashlib.sha256(seed.encode()).hexdigest()
    print(f"    SHA256: {seed_hash[:32]}...")

# ============================================================
# 6. HASH-BASIERTE SCHLÜSSEL
# ============================================================
print("\n" + "=" * 70)
print("6. HASH-BASIERTE SCHLÜSSEL")
print("=" * 70)

# Hash der gesamten Matrix
matrix_bytes = []
for r in range(128):
    for c in range(128):
        val = matrix[r][c]
        if isinstance(val, str):
            matrix_bytes.append(0)
        else:
            matrix_bytes.append(val & 0xFF)

matrix_full_hash = hashlib.sha256(bytes(matrix_bytes)).hexdigest()
print(f"\nSHA256 der gesamten Matrix:")
print(f"  {matrix_full_hash}")

# Hash bekannter Strings
strings_to_hash = [
    "AI.MEG.GOU",
    "AIGARTH",
    "ANNA",
    "CFB",
    "Sergey Ivancheglo",
    "Come-from-Beyond",
    "qubic",
    "bitcoin",
    "satoshi",
]

print("\nSHA256 bekannter Strings:")
for s in strings_to_hash:
    h = hashlib.sha256(s.encode()).hexdigest()
    print(f"  {s}: {h[:32]}...")

# ============================================================
# 7. SPEZIELLE MUSTER SUCHEN
# ============================================================
print("\n" + "=" * 70)
print("7. SPEZIELLE MUSTER IN DER MATRIX")
print("=" * 70)

# Suche nach Sequenzen die Bitcoin-Adress-Präfixe sein könnten
print("\nSuche nach Bitcoin-ähnlichen Mustern:")

# 1 für P2PKH (Legacy)
# 3 für P2SH
# bc1 für Bech32

# Suche nach '1' als ASCII (49) gefolgt von gültigen Base58 chars
count_legacy = 0
count_segwit = 0

for r in range(128):
    for c in range(125):  # Raum für 3 chars
        v1 = matrix[r][c]
        v2 = matrix[r][c+1]
        v3 = matrix[r][c+2]

        if isinstance(v1, str) or isinstance(v2, str) or isinstance(v3, str):
            continue

        # Check for '1' (49)
        if v1 == 49:
            count_legacy += 1

        # Check for 'bc1' sequence
        if v1 == 98 and v2 == 99 and v3 == 49:  # 'b', 'c', '1'
            print(f"  Found 'bc1' at [{r}, {c}]!")
            count_segwit += 1

print(f"  Positionen mit '1' (ASCII 49): {count_legacy}")
print(f"  'bc1' Sequenzen gefunden: {count_segwit}")

# ============================================================
# 8. 137 UND 1337 MUSTER
# ============================================================
print("\n" + "=" * 70)
print("8. 137 UND 1337 MUSTER")
print("=" * 70)

# Find all positions where consecutive values form 137 or 1337
print("\nPositionen wo Werte 1-3-7 oder 1-3-3-7 bilden:")

for r in range(128):
    for c in range(125):
        vals = []
        for i in range(4):
            if c + i < 128:
                v = matrix[r][c+i]
                if isinstance(v, str):
                    break
                vals.append(v)

        if len(vals) >= 3:
            # Check for 1, 3, 7 sequence
            if vals[0] == 1 and vals[1] == 3 and vals[2] == 7:
                print(f"  1-3-7 at row {r}, col {c}")

            if len(vals) >= 4:
                if vals[0] == 1 and vals[1] == 3 and vals[2] == 3 and vals[3] == 7:
                    print(f"  1-3-3-7 at row {r}, col {c}")

# Check row/column sums for 137
print("\nZeilen/Spalten mit Summe 137:")
for r in range(128):
    row_sum = sum(v for v in [matrix[r][c] for c in range(128)] if not isinstance(v, str))
    if abs(row_sum) == 137:
        print(f"  Row {r}: sum = {row_sum}")

for c in range(128):
    col_sum = sum(v for v in [matrix[r][c] for r in range(128)] if not isinstance(v, str))
    if abs(col_sum) == 137:
        print(f"  Col {c}: sum = {col_sum}")

# ============================================================
# 9. XOR ALLER ZEILEN/SPALTEN
# ============================================================
print("\n" + "=" * 70)
print("9. XOR PATTERNS")
print("=" * 70)

print("\nZeilen mit XOR = 127 (Matrix-Konstante):")
for r in range(128):
    xor_val = 0
    valid = True
    for c in range(128):
        v = matrix[r][c]
        if isinstance(v, str):
            valid = False
            break
        xor_val ^= v
    if valid and xor_val == 127:
        print(f"  Row {r}: XOR = 127")

print("\nZeilen mit XOR = 137 (Feinstruktur):")
for r in range(128):
    xor_val = 0
    valid = True
    for c in range(128):
        v = matrix[r][c]
        if isinstance(v, str):
            valid = False
            break
        xor_val ^= v
    if valid and abs(xor_val) == 137:
        print(f"  Row {r}: XOR = {xor_val}")

# ============================================================
# 10. FINALE ZUSAMMENFASSUNG
# ============================================================
print("\n" + "=" * 70)
print("10. ZUSAMMENFASSUNG DER POTENTIELLEN SCHLÜSSEL")
print("=" * 70)

print("\n--- Bitcoin Private Key Kandidaten (64 hex chars) ---")
print(f"1. AI.MEG.GOU Direct:  {key_hex_1}")
print(f"2. AI.MEG.GOU XOR:     {key_hex_2}")
print(f"3. Diagonal:           {diag_hex}")
print(f"4. Anti-Diagonal:      {anti_diag_hex}")
print(f"5. Center Diagonal:    {center_diag_hex}")
print(f"6. Matrix Hash:        {matrix_full_hash}")

print("\n--- Qubic Seed Kandidaten (55 lowercase chars) ---")
for name, seed in seeds.items():
    print(f"{name:20s}: {seed}")

# Speichern der Ergebnisse
results = {
    "bitcoin_key_candidates": {
        "ai_meg_gou_direct": key_hex_1,
        "ai_meg_gou_xor": key_hex_2,
        "diagonal": diag_hex,
        "anti_diagonal": anti_diag_hex,
        "center_diagonal": center_diag_hex,
        "matrix_hash": matrix_full_hash,
    },
    "qubic_seed_candidates": seeds,
    "unknown_positions": [(r, c) for r, c in unknowns],
    "unknown_positions_hex": unknown_pos_hex,
    "key_numbers": {
        "26": "UNKNOWN count, -1 count",
        "27": "Ternary base (3^3)",
        "127": "Matrix constant (2^7-1)",
        "137": "Fine structure constant",
        "476": "Count of 26 and -27",
    }
}

with open('BITCOIN_QUBIC_KEYS_ANALYSIS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Ergebnisse gespeichert in: BITCOIN_QUBIC_KEYS_ANALYSIS.json")
print("=" * 70)
