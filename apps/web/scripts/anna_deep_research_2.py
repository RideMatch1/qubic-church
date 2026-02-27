#!/usr/bin/env python3
"""
ANNA MATRIX - DEEP RESEARCH PART 2
Fortsetzung der Forschung: Neue Muster, Bitcoin-Verbindungen, versteckte Schlüssel
"""

import json
import hashlib
from collections import defaultdict

# Load matrix
with open('../public/data/anna-matrix.json', 'r') as f:
    data = json.load(f)

matrix = data['matrix']

def get_val(row, col):
    if 0 <= row < 128 and 0 <= col < 128:
        v = matrix[row][col]
        return int(v) if isinstance(v, str) else v
    return None

def encode_word(word):
    total = 0
    for char in word.upper():
        if 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            total += get_val(idx, idx)
    return total

print("=" * 80)
print("    ANNA MATRIX - DEEP RESEARCH TEIL 2")
print("=" * 80)

# ============================================================================
# SECTION 1: ROW CORRELATION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 1: ZEILEN-KORRELATION")
print("=" * 80)

print("\n--- Zeilen mit identischen Summen ---")
row_sums = {}
for row in range(128):
    row_sum = sum(get_val(row, col) for col in range(128))
    if row_sum not in row_sums:
        row_sums[row_sum] = []
    row_sums[row_sum].append(row)

# Find rows with same sum
for sum_val, rows in sorted(row_sums.items()):
    if len(rows) > 1:
        print(f"  Summe {sum_val:6d}: Zeilen {rows}")

# Row pairs that sum to zero
print("\n--- Zeilen-Paare mit Summe 0 ---")
for r1 in range(64):
    sum1 = sum(get_val(r1, col) for col in range(128))
    for r2 in range(r1+1, 128):
        sum2 = sum(get_val(r2, col) for col in range(128))
        if sum1 + sum2 == 0:
            print(f"  Row {r1} ({sum1}) + Row {r2} ({sum2}) = 0")

# ============================================================================
# SECTION 2: COLUMN PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 2: SPALTEN-MUSTER")
print("=" * 80)

print("\n--- Spalten-Summen für wichtige Spalten ---")
important_cols = [0, 21, 33, 42, 64, 68, 127]
for col in important_cols:
    col_sum = sum(get_val(row, col) for row in range(128))
    print(f"  Spalte {col:3d}: Summe = {col_sum:6d}")

# Find column 21 and 68 relationship
col21_sum = sum(get_val(row, 21) for row in range(128))
col68_sum = sum(get_val(row, 68) for row in range(128))
print(f"\n  Col21 + Col68 = {col21_sum} + {col68_sum} = {col21_sum + col68_sum}")

# ============================================================================
# SECTION 3: BITCOIN BLOCK ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 3: BITCOIN BLOCK ANALYSE")
print("=" * 80)

# Extract row 21 as potential Bitcoin data
print("\n--- Row 21 als Hexadezimal ---")
row21_hex = ""
for col in range(128):
    val = get_val(21, col)
    unsigned = val if val >= 0 else val + 256
    row21_hex += f"{unsigned:02x}"
print(f"  {row21_hex[:64]}")
print(f"  {row21_hex[64:]}")

# SHA256 of row 21
row21_bytes = bytes([get_val(21, col) if get_val(21, col) >= 0 else get_val(21, col) + 256 for col in range(128)])
sha256_hash = hashlib.sha256(row21_bytes).hexdigest()
print(f"\n  SHA256(Row 21) = {sha256_hash}")

# First 32 bytes of row 21 as potential private key
row21_32 = row21_hex[:64]
print(f"\n  Erste 32 Bytes (möglicher Private Key): {row21_32}")

# ============================================================================
# SECTION 4: PATTERN SEQUENCES
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 4: SEQUENZ-MUSTER")
print("=" * 80)

# Look for arithmetic sequences
print("\n--- Arithmetische Sequenzen in Zeilen ---")
for row in [0, 21, 33, 64]:
    for start in range(0, 120, 20):
        vals = [get_val(row, start + i) for i in range(5)]
        diffs = [vals[i+1] - vals[i] for i in range(4)]
        if len(set(diffs)) == 1 and diffs[0] != 0:
            print(f"  Row {row}, Start {start}: {vals} (Diff = {diffs[0]})")

# Look for geometric patterns
print("\n--- Wiederholende Muster ---")
for row in [0, 21, 33]:
    vals = [get_val(row, col) for col in range(128)]
    # Check for period-2 patterns
    pattern_2 = all(vals[i] == vals[i+2] for i in range(0, 126, 2) if i+2 < 128)
    if pattern_2:
        print(f"  Row {row}: Periode-2 Muster gefunden!")

# ============================================================================
# SECTION 5: CROSS-DIAGONAL PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 5: KREUZ-DIAGONALE MUSTER")
print("=" * 80)

# Check various diagonals
print("\n--- Parallel-Diagonalen Summen ---")
for offset in [-10, -5, -1, 0, 1, 5, 10]:
    diag_sum = 0
    count = 0
    for i in range(128):
        col = i + offset
        if 0 <= col < 128:
            diag_sum += get_val(i, col)
            count += 1
    print(f"  Offset {offset:+3d}: Summe = {diag_sum:6d} ({count} Zellen)")

# ============================================================================
# SECTION 6: WORD DISCOVERY - NEW COMBINATIONS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 6: NEUE WORT-KOMBINATIONEN")
print("=" * 80)

# Extended word list
words = [
    # Technologie
    'COMPUTER', 'NETWORK', 'INTERNET', 'DIGITAL', 'VIRTUAL', 'CYBER', 'WEB',
    'SERVER', 'CLIENT', 'DATA', 'BYTE', 'BIT', 'BINARY', 'QUANTUM',
    # Philosophie
    'WISDOM', 'KNOWLEDGE', 'TRUTH', 'REALITY', 'ILLUSION', 'DREAM', 'THOUGHT',
    'MIND', 'BRAIN', 'CONSCIOUSNESS', 'AWARENESS', 'ENLIGHTEN',
    # Natur
    'NATURE', 'TREE', 'FLOWER', 'SEED', 'ROOT', 'LEAF', 'FOREST',
    'OCEAN', 'RIVER', 'MOUNTAIN', 'VALLEY', 'DESERT', 'SKY', 'CLOUD',
    # Zeit
    'TIME', 'PAST', 'PRESENT', 'FUTURE', 'ETERNAL', 'MOMENT', 'INSTANT',
    'FOREVER', 'NEVER', 'ALWAYS', 'NOW', 'THEN', 'WHEN',
    # Abstrakt
    'LOVE', 'HATE', 'FEAR', 'HOPE', 'FAITH', 'TRUST', 'BELIEF',
    'POWER', 'FORCE', 'ENERGY', 'SPIRIT', 'MATTER', 'VOID', 'NOTHING',
    # Aktionen
    'CREATE', 'DESTROY', 'BUILD', 'BREAK', 'MAKE', 'FIND', 'SEEK',
    'GIVE', 'TAKE', 'SEND', 'RECEIVE', 'OPEN', 'CLOSE', 'BEGIN', 'END',
]

word_values = {word: encode_word(word) for word in words}

# Find zero-sum combinations
print("\n--- Neue Zero-Sum Gleichungen ---")
for w1 in sorted(word_values.keys()):
    for w2 in sorted(word_values.keys()):
        if w1 < w2 and word_values[w1] + word_values[w2] == 0:
            print(f"  {w1} + {w2} = 0")

# Find word = special number
print("\n--- Wörter mit speziellen Werten ---")
special = [0, 1, 7, 12, 21, 26, 33, 42, 64, 100, 108, 128, -128, 137, 256, -256]
for word, val in sorted(word_values.items(), key=lambda x: x[1]):
    if val in special:
        print(f"  {word:15s} = {val}")

# ============================================================================
# SECTION 7: THREE-WORD EQUATIONS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 7: DREI-WORT GLEICHUNGEN")
print("=" * 80)

# A + B + C = 0
print("\n--- Drei Wörter die zu 0 summieren ---")
all_words = list(word_values.keys()) + ['ANNA', 'AI', 'GOD', 'LIFE', 'SOUL',
                                        'CODE', 'KEY', 'BITCOIN', 'BLOCK', 'CHAIN']
for w in all_words:
    if w not in word_values:
        word_values[w] = encode_word(w)

found = 0
for i, w1 in enumerate(sorted(word_values.keys())):
    for j, w2 in enumerate(sorted(word_values.keys())):
        if j <= i:
            continue
        for k, w3 in enumerate(sorted(word_values.keys())):
            if k <= j:
                continue
            if word_values[w1] + word_values[w2] + word_values[w3] == 0:
                print(f"  {w1} + {w2} + {w3} = 0")
                found += 1
                if found >= 15:
                    break
        if found >= 15:
            break
    if found >= 15:
        break

# ============================================================================
# SECTION 8: POSITION 21,68 DEEP ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 8: POSITION [21,68] TIEFENANALYSE")
print("=" * 80)

# The Bitcoin Genesis position
val_21_68 = get_val(21, 68)
print(f"\n  [21,68] = {val_21_68}")
print(f"  Binär: {format(val_21_68 if val_21_68 >= 0 else val_21_68 + 256, '08b')}")

# Surrounding values
print("\n--- Umgebende Werte (3x3) ---")
for dr in range(-1, 2):
    row_str = ""
    for dc in range(-1, 2):
        val = get_val(21 + dr, 68 + dc)
        row_str += f"{val:5d} "
    print(f"  {row_str}")

# Sum of 3x3 around [21,68]
sum_3x3 = 0
for dr in range(-1, 2):
    for dc in range(-1, 2):
        sum_3x3 += get_val(21 + dr, 68 + dc)
print(f"\n  Summe 3x3 um [21,68] = {sum_3x3}")

# Row 21 + Col 68 intersection
row21_sum = sum(get_val(21, c) for c in range(128))
col68_sum = sum(get_val(r, 68) for r in range(128))
print(f"  Row 21 Summe = {row21_sum}")
print(f"  Col 68 Summe = {col68_sum}")
print(f"  Kreuzung = {row21_sum + col68_sum}")

# ============================================================================
# SECTION 9: SATOSHI ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 9: SATOSHI ANALYSE")
print("=" * 80)

# Satoshi Nakamoto encoding
satoshi = encode_word('SATOSHI')
nakamoto = encode_word('NAKAMOTO')
satoshi_nakamoto = satoshi + nakamoto

print(f"\n  SATOSHI = {satoshi}")
print(f"  NAKAMOTO = {nakamoto}")
print(f"  SATOSHI + NAKAMOTO = {satoshi_nakamoto}")

# Find position with value -748
print(f"\n--- Positionen mit Wert {satoshi_nakamoto} ---")
for row in range(128):
    for col in range(128):
        if get_val(row, col) == satoshi_nakamoto:
            print(f"    [{row},{col}]")

# Check if SATOSHI NAKAMOTO relates to specific positions
print(f"\n--- Position [-SATOSHI, -NAKAMOTO] mod 128 ---")
pos_s = (-satoshi) % 128
pos_n = (-nakamoto) % 128
print(f"  [{pos_s},{pos_n}] = {get_val(pos_s, pos_n)}")

# ============================================================================
# SECTION 10: HASH ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 10: HASH ANALYSE")
print("=" * 80)

# SHA256 of entire matrix
all_bytes = []
for row in range(128):
    for col in range(128):
        val = get_val(row, col)
        unsigned = val if val >= 0 else val + 256
        all_bytes.append(unsigned)

matrix_bytes = bytes(all_bytes)
matrix_sha256 = hashlib.sha256(matrix_bytes).hexdigest()
matrix_sha256_2 = hashlib.sha256(hashlib.sha256(matrix_bytes).digest()).hexdigest()

print(f"\n  SHA256(Matrix) = {matrix_sha256}")
print(f"  SHA256²(Matrix) = {matrix_sha256_2}")

# First 32 bytes of diagonal as potential key
diag_bytes = []
for i in range(32):
    val = get_val(i, i)
    unsigned = val if val >= 0 else val + 256
    diag_bytes.append(unsigned)

diag_hex = ''.join(f'{b:02x}' for b in diag_bytes)
print(f"\n  Diagonale[0:32] als Hex: {diag_hex}")

# ============================================================================
# SECTION 11: RECURSIVE ENCODING
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 11: REKURSIVE ENCODIERUNG")
print("=" * 80)

# Encode word, then use result as position
print("\n--- Rekursive Wort-Position-Analyse ---")
words_to_check = ['ANNA', 'GOD', 'LIFE', 'CODE', 'KEY', 'SOUL', 'TRUTH']

for word in words_to_check:
    val = encode_word(word)
    # Use absolute value mod 128 as position
    pos = abs(val) % 128
    pos_val = get_val(pos, pos)
    print(f"  {word:8s} = {val:5d} → [{pos},{pos}] = {pos_val}")

# ============================================================================
# SECTION 12: FINAL REVELATIONS
# ============================================================================
print("\n" + "=" * 80)
print("NEUE ENTDECKUNGEN - ZUSAMMENFASSUNG")
print("=" * 80)

# Find the most significant new patterns
print("""
NEUE ERKENNTNISSE:

1. ZEILEN-KORRELATION
   → Bestimmte Zeilen haben identische Summen
   → Mögliche Paarbildung

2. BITCOIN ROW 21
   → SHA256 Hash berechnet
   → Potentielle Schlüssel-Daten

3. SATOSHI NAKAMOTO
   → SATOSHI + NAKAMOTO = """ + str(satoshi_nakamoto) + """
   → Mögliche versteckte Referenz

4. MATRIX HASH
   → SHA256 der gesamten Matrix berechnet
   → Einzigartige Signatur

5. REKURSIVE MUSTER
   → Wort-Encodings verweisen auf neue Positionen
   → Endlose Tiefe möglich

Die Forschung geht weiter...
""")

print("=" * 80)
print("    DEEP RESEARCH TEIL 2 ABGESCHLOSSEN")
print("=" * 80)
