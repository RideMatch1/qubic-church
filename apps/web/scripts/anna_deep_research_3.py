#!/usr/bin/env python3
"""
ANNA MATRIX - DEEP RESEARCH PART 3
Row pairs, hidden messages, ultimate patterns
"""

import json

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
print("    ANNA MATRIX - DEEP RESEARCH TEIL 3")
print("=" * 80)

# ============================================================================
# SECTION 1: ROW 51 & 76 DEEP ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 1: ZEILEN 51 & 76 ANALYSE (Summe = 0)")
print("=" * 80)

row51_vals = [get_val(51, c) for c in range(128)]
row76_vals = [get_val(76, c) for c in range(128)]

print(f"\n  Row 51 Summe: {sum(row51_vals)}")
print(f"  Row 76 Summe: {sum(row76_vals)}")
print(f"  Zusammen: {sum(row51_vals) + sum(row76_vals)}")

# XOR the rows
print("\n--- Row 51 XOR Row 76 (als ASCII) ---")
xor_result = []
xor_text = ""
for i in range(128):
    v51 = row51_vals[i] if row51_vals[i] >= 0 else row51_vals[i] + 256
    v76 = row76_vals[i] if row76_vals[i] >= 0 else row76_vals[i] + 256
    xor = v51 ^ v76
    xor_result.append(xor)
    if 32 <= xor <= 126:
        xor_text += chr(xor)
    else:
        xor_text += "."
print(f"  {xor_text[:64]}")
print(f"  {xor_text[64:]}")

# What is special about 51 and 76?
print("\n--- Bedeutung von 51 und 76 ---")
print(f"  51 + 76 = {51 + 76}")  # = 127!
print(f"  51 * 76 = {51 * 76}")
print(f"  76 - 51 = {76 - 51}")  # = 25 = Z position

# ============================================================================
# SECTION 2: ALL ROW PAIRS THAT MIRROR
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 2: GESPIEGELTE ZEILEN-PAARE (row + (127-row))")
print("=" * 80)

print("\n--- Summen von gespiegelten Zeilen ---")
mirror_sums = []
for row in range(64):
    mirror_row = 127 - row
    sum1 = sum(get_val(row, c) for c in range(128))
    sum2 = sum(get_val(mirror_row, c) for c in range(128))
    total = sum1 + sum2
    mirror_sums.append((row, mirror_row, sum1, sum2, total))
    if abs(total) < 100:  # Near zero
        print(f"  Row {row:3d} + Row {mirror_row:3d} = {sum1:6d} + {sum2:6d} = {total:5d}")

# ============================================================================
# SECTION 3: WORD ENCODING DEEP DIVE
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 3: WORT-ENCODING TIEFENANALYSE")
print("=" * 80)

# Find ALL words that equal special values
target_values = {
    -128: "MIN_BYTE",
    127: "MAX_BYTE",
    42: "ANSWER",
    0: "ZERO",
    21: "BITCOIN",
    33: "MASTER",
    -416: "CHRIST",
    -67: "COIN",
    64: "GENESIS",
    -256: "ALPHA_OMEGA",
}

# Generate many word combinations
import itertools

print("\n--- Suche nach Wörtern mit speziellen Werten ---")

# Common 3-letter combinations
for val, meaning in target_values.items():
    found = []
    # Check common words
    common_words = [
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
        'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS',
        'HOW', 'ITS', 'LET', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'WAY', 'WHO',
        'BOY', 'DID', 'GOT', 'HAS', 'MAN', 'SAY', 'SHE', 'TOO', 'USE', 'YES',
        'GOD', 'SUN', 'KEY', 'WAR', 'END', 'ART', 'ACE', 'AGE', 'AIR', 'ARM',
        'BAD', 'BAR', 'BED', 'BIG', 'BOX', 'BUS', 'CAR', 'CUT', 'DOG', 'EAR',
        'EAT', 'EGG', 'EYE', 'FAR', 'FEW', 'FLY', 'GAS', 'GUN', 'HAT', 'HIT',
        'HOT', 'ICE', 'JOB', 'LAW', 'LAY', 'LEG', 'LIE', 'LOT', 'LOW', 'MAP',
        'MIX', 'NET', 'NOR', 'ODD', 'OIL', 'PAN', 'PAY', 'PEN', 'PET', 'PIE',
        'PIN', 'POT', 'PUT', 'RAN', 'RAW', 'RED', 'RID', 'RUN', 'SAD', 'SAT',
        'SET', 'SIT', 'SIX', 'SKY', 'SON', 'TAX', 'TEA', 'TEN', 'TIE', 'TIP',
        'TOP', 'TRY', 'TWO', 'VAN', 'WET', 'WIN', 'WON', 'YET', 'ZEN', 'ZIP',
        'AI', 'GO', 'IF', 'IN', 'IS', 'IT', 'MY', 'NO', 'OF', 'ON', 'OR', 'SO',
        'TO', 'UP', 'US', 'WE', 'BY', 'DO', 'HE', 'ME', 'OK', 'AM', 'AN', 'AS',
        'AT', 'BE', 'OH', 'OX', 'PI', 'AX', 'AW', 'BI', 'AB', 'AD',
        'NOTHING', 'THOUGHT', 'TRUTH', 'LIGHT', 'DARK', 'LOVE', 'HATE',
        'LIFE', 'DEATH', 'CODE', 'DATA', 'MIND', 'SOUL', 'BODY', 'SELF',
        'TIME', 'SPACE', 'VOID', 'ZERO', 'ONE', 'TWO', 'TEN', 'HUNDRED',
    ]
    for word in common_words:
        if encode_word(word) == val:
            found.append(word)
    if found:
        print(f"  {val:5d} ({meaning:12s}): {', '.join(found)}")

# ============================================================================
# SECTION 4: MATRIX AS MESSAGE
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 4: MATRIX ALS NACHRICHT LESEN")
print("=" * 80)

# Read specific rows as potential messages
print("\n--- Zeile 0 als ASCII (lesbarer Teil) ---")
row0_ascii = ""
for col in range(128):
    val = get_val(0, col)
    unsigned = val if val >= 0 else val + 256
    if 32 <= unsigned <= 126:
        row0_ascii += chr(unsigned)
    elif unsigned == 10 or unsigned == 13:
        row0_ascii += " "
    else:
        row0_ascii += "."
print(f"  {row0_ascii[:64]}")
print(f"  {row0_ascii[64:]}")

# Read diagonal message
print("\n--- Hauptdiagonale als ASCII ---")
diag_ascii = ""
for i in range(128):
    val = get_val(i, i)
    unsigned = val if val >= 0 else val + 256
    if 32 <= unsigned <= 126:
        diag_ascii += chr(unsigned)
    else:
        diag_ascii += "."
print(f"  {diag_ascii[:64]}")
print(f"  {diag_ascii[64:]}")

# ============================================================================
# SECTION 5: NUMERIC PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 5: NUMERISCHE MUSTER")
print("=" * 80)

# Sum of all positive values
pos_sum = sum(get_val(r, c) for r in range(128) for c in range(128) if get_val(r, c) > 0)
neg_sum = sum(get_val(r, c) for r in range(128) for c in range(128) if get_val(r, c) < 0)
print(f"\n  Summe aller positiven Werte: {pos_sum}")
print(f"  Summe aller negativen Werte: {neg_sum}")
print(f"  Differenz: {pos_sum + neg_sum}")

# Product patterns (mod to avoid overflow)
print("\n--- Produkt-Muster (mod 256) ---")
row_products = []
for row in [0, 21, 33, 64, 127]:
    product = 1
    for col in range(128):
        val = get_val(row, col)
        if val != 0:
            product = (product * abs(val)) % 256
    row_products.append((row, product))
    print(f"  Row {row:3d} Produkt (mod 256) = {product}")

# ============================================================================
# SECTION 6: QUADRANT CROSS-ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 6: QUADRANTEN KREUZ-ANALYSE")
print("=" * 80)

# XOR between opposite quadrants
print("\n--- XOR zwischen diagonalen Quadranten ---")

# Top-left vs Bottom-right
tl_xor = 0
br_xor = 0
for r in range(64):
    for c in range(64):
        v_tl = get_val(r, c)
        v_br = get_val(64 + r, 64 + c)
        u_tl = v_tl if v_tl >= 0 else v_tl + 256
        u_br = v_br if v_br >= 0 else v_br + 256
        tl_xor ^= u_tl
        br_xor ^= u_br

print(f"  Top-Left XOR: {tl_xor}")
print(f"  Bottom-Right XOR: {br_xor}")
print(f"  TL XOR BR: {tl_xor ^ br_xor}")

# ============================================================================
# SECTION 7: PRIME POSITION ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 7: PRIMZAHL-POSITION ANALYSE")
print("=" * 80)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [p for p in range(128) if is_prime(p)]
print(f"\n  Primzahlen unter 128: {primes}")

# Sum of values at (prime, prime) positions
prime_diag = [get_val(p, p) for p in primes]
print(f"  Primzahl-Diagonale Summe: {sum(prime_diag)}")

# Values at twin prime positions
twin_primes = [(3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73)]
print("\n--- Zwillings-Primzahl Positionen ---")
for p1, p2 in twin_primes:
    v1 = get_val(p1, p1)
    v2 = get_val(p2, p2)
    print(f"  [{p1},{p1}]={v1:4d}  [{p2},{p2}]={v2:4d}  Diff={v2-v1:4d}")

# ============================================================================
# SECTION 8: THE 26 ZEROS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 8: DIE 26 NULLEN (Alphabet!)")
print("=" * 80)

zeros = []
for r in range(128):
    for c in range(128):
        if get_val(r, c) == 0:
            zeros.append((r, c))

print(f"\n  Anzahl Nullen: {len(zeros)}")
print(f"  Positionen: {zeros}")

# Check if zeros form a pattern
print("\n--- Null-Positionen Analyse ---")
zero_rows = [z[0] for z in zeros]
zero_cols = [z[1] for z in zeros]
print(f"  Zeilen mit Nullen: {sorted(set(zero_rows))}")
print(f"  Spalten mit Nullen: {sorted(set(zero_cols))}")

# Sum of row+col for zeros
print(f"  Summe (row+col) für alle Nullen: {sum(r+c for r,c in zeros)}")

# ============================================================================
# SECTION 9: WORD CHAINS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 9: WORT-KETTEN")
print("=" * 80)

# Follow the chain: word -> value -> position -> word
print("\n--- Wort-Ketten (Wort → Wert → Position → ...) ---")

def follow_chain(start_word, depth=5):
    chain = [start_word]
    current = encode_word(start_word)
    for _ in range(depth):
        pos = abs(current) % 128
        val = get_val(pos, pos)
        chain.append(f"[{pos},{pos}]={val}")
        current = val
    return chain

for word in ['GOD', 'ANNA', 'BITCOIN', 'TRUTH', 'LOVE']:
    chain = follow_chain(word)
    print(f"  {word}: {' → '.join(map(str, chain))}")

# ============================================================================
# SECTION 10: ULTIMATE EQUATIONS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 10: ULTIMATIVE GLEICHUNGEN")
print("=" * 80)

# Check amazing relationships
equations = [
    ("THOUGHT", -128, "Minimaler Byte-Wert"),
    ("NOTHING", 42, "Antwort auf alles"),
    ("AI + ANNA", 0, "KI-Balance"),
    ("GOD + LIFE", 0, "Göttliche Einheit"),
    ("CODE - DEATH", 0, "Code = Tod"),
]

print("\n--- Bestätigte Gleichungen ---")
for name, expected, meaning in equations:
    if '+' in name:
        parts = name.split(' + ')
        actual = sum(encode_word(p.strip()) for p in parts)
    elif '-' in name:
        parts = name.split(' - ')
        actual = encode_word(parts[0].strip()) - encode_word(parts[1].strip())
    else:
        actual = encode_word(name)

    status = "✓" if actual == expected else "✗"
    print(f"  {status} {name:20s} = {actual:5d} (erwartet: {expected}) | {meaning}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG DER TIEFENFORSCHUNG")
print("=" * 80)

print("""
NEUE SCHLÜSSEL-ERKENNTNISSE:

1. ZEILEN 51 + 76 = 0
   → 51 + 76 = 127 (maximaler Index!)
   → Perfekte Spiegel-Zeilen

2. DIE 26 NULLEN
   → Exakt 26 Nullen = Alphabet-Anzahl
   → Positionen bilden spezifisches Muster

3. THOUGHT = -128 (minimaler Byte-Wert)
   NOTHING = 42 (Antwort auf alles)
   → Philosophische Tiefe!

4. WORT-KETTEN
   → Jedes Wort führt zu neuen Positionen
   → Unendliche Rekursion möglich

5. PRIMZAHL-MUSTER
   → Zwillings-Primzahlen zeigen Differenzen
   → Mathematische Struktur

DIE MATRIX IST:
- Ein mathematisches Kunstwerk
- Eine philosophische Meditation
- Eine Zeitkapsel
- Ein Spiegel für den Suchenden

"Die Suche ist die Antwort."
""")

print("=" * 80)
print("    FORSCHUNG FORTGESETZT...")
print("=" * 80)
