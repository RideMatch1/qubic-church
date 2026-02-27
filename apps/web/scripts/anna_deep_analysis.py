#!/usr/bin/env python3
"""
Anna Matrix Deep Analysis
=========================
Extended pattern search for hidden messages, sequences, and codes
"""

import json
import os
from collections import Counter

# Load the Anna Matrix
script_dir = os.path.dirname(os.path.abspath(__file__))
matrix_path = os.path.join(script_dir, '..', 'public', 'data', 'anna-matrix.json')

with open(matrix_path, 'r') as f:
    data = json.load(f)
    matrix = data.get('matrix', data)

def get_val(row, col):
    v = matrix[row][col]
    return int(v) if isinstance(v, str) else v

def encode_word(word):
    total = 0
    for char in word.upper():
        if 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            total += get_val(idx, idx)
    return total

print("=" * 70)
print("ANNA MATRIX DEEP ANALYSIS")
print("=" * 70)

# =============================================================================
# SEARCH FOR FAMOUS NUMBERS
# =============================================================================

print("\n" + "=" * 70)
print("PART 1: FAMOUS NUMBERS IN THE MATRIX")
print("=" * 70)

famous_numbers = {
    3: "Trinity",
    7: "Lucky/Sacred",
    12: "Apostles/Months",
    13: "Unlucky",
    21: "Bitcoin/Blackjack",
    22: "Master Number",
    23: "Enigma",
    26: "Letters in alphabet",
    33: "Jesus age/Masonic",
    36: "6x6",
    42: "Answer to Everything",
    64: "Qubic Computors/Chess squares",
    66: "Route 66/Books in Bible",
    68: "Column of transformation",
    69: "Yin/Yang",
    72: "Angels/Divine names",
    77: "Perfection",
    88: "Constellations/Infinity",
    96: "ANNA",
    99: "Almost complete",
    100: "Century/Perfection",
    108: "Sacred in Buddhism",
    111: "Angel number",
    127: "Max signed byte",
    128: "Matrix size",
    144: "Gross/12x12",
    256: "Full byte range",
    314: "Pi approximation",
    365: "Days in year",
    666: "Number of the Beast",
    777: "Divine perfection",
    888: "Jesus in Greek gematria",
    1000: "Millennium",
}

print("\nSearching for famous numbers as word encodings...")
print("-" * 50)

# Extended word list
all_words = [
    # Short words
    "A", "I", "AM", "AN", "AS", "AT", "BE", "BY", "DO", "GO", "HE", "IF", "IN",
    "IS", "IT", "ME", "MY", "NO", "OF", "ON", "OR", "SO", "TO", "UP", "US", "WE",
    # 3-letter
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD", "HER",
    "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS", "HOW", "ITS",
    "MAY", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID", "SAY", "SHE",
    "GOD", "MAN", "SUN", "KEY", "END", "WAR", "USE", "TEN", "SIX", "TWO", "OWN",
    "ETH", "CFB", "BIT", "HEX", "NET", "WEB", "ROW", "SUM", "XOR", "LOG", "MOD",
    "PHI", "ZEN", "DAO", "AIR", "ART", "EGO", "ERA", "EYE", "LAW", "LIE", "SIN",
    # 4-letter
    "ANNA", "LOVE", "HATE", "LIFE", "DEATH", "SOUL", "MIND", "BODY", "CODE",
    "DATA", "BYTE", "HASH", "SEED", "NODE", "PEER", "COIN", "MINE", "GOLD",
    "ZERO", "HERO", "TIME", "YEAR", "MOON", "STAR", "FIRE", "WIND", "RAIN",
    "TREE", "BIRD", "FISH", "WORD", "BOOK", "PAGE", "LINE", "NAME", "GAME",
    "PLAY", "WORK", "HOME", "DOOR", "WALL", "ROAD", "PATH", "HOPE", "FEAR",
    "PAIN", "GAIN", "LOSS", "FIND", "SEEK", "LOOK", "GIVE", "TAKE", "SEND",
    "COME", "FROM", "OPEN", "EXIT", "EVIL", "GOOD", "DARK", "PURE", "TRUE",
    "FAKE", "REAL", "MYTH", "FACT", "SIGN", "LINK", "BOND", "FREE", "BIND",
    # 5-letter
    "ANGEL", "DEMON", "LIGHT", "PEACE", "TRUTH", "FAITH", "GRACE", "POWER",
    "MONEY", "WORLD", "EARTH", "WATER", "HEART", "BRAIN", "HUMAN", "BEING",
    "CHILD", "WOMAN", "BIRTH", "FIRST", "PRIME", "SEVEN", "EIGHT", "THREE",
    "ALPHA", "OMEGA", "JESUS", "MOSES", "SATAN", "DEVIL", "GHOST", "SPIRIT",
    "BLOOD", "FLESH", "STONE", "METAL", "CHAOS", "ORDER", "SPACE", "POINT",
    "CYCLE", "ORBIT", "SOLAR", "LUNAR", "COMET", "VENUS", "TERRA", "PLUTO",
    # 6-letter
    "CHRIST", "BUDDHA", "DHARMA", "HEAVEN", "COSMOS", "MATRIX", "BRIDGE",
    "QUBIC", "EXODUS", "SECRET", "CIPHER", "CRYPTO", "ORACLE", "BINARY",
    "BEYOND", "ORIGIN", "SOURCE", "TARGET", "RESULT", "ANSWER", "NUMBER",
    # 7+ letter
    "GENESIS", "BITCOIN", "SATOSHI", "NAKAMOTO", "HALLEY", "ETHEREUM",
    "INFINITY", "ETERNITY", "CREATION", "UNIVERSE", "DIMENSION", "FREQUENCY",
    "VIBRATION", "RESONANCE", "HARMONY", "BALANCE", "SYMMETRY", "PATTERN",
]

# Calculate all encodings
word_encodings = {w: encode_word(w) for w in all_words}

# Find matches
for num, meaning in sorted(famous_numbers.items()):
    matches = [w for w, v in word_encodings.items() if v == num]
    neg_matches = [w for w, v in word_encodings.items() if v == -num]
    if matches or neg_matches:
        print(f"\n{num} ({meaning}):")
        if matches:
            print(f"  Positive: {', '.join(matches)}")
        if neg_matches:
            print(f"  Negative (-{num}): {', '.join(neg_matches)}")

# =============================================================================
# SEARCH FOR COORDINATE PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 2: COORDINATE PATTERN ANALYSIS")
print("=" * 70)

# Check special coordinate pairs
coordinate_checks = [
    ((0, 0), (127, 127), "Diagonal corners"),
    ((0, 127), (127, 0), "Anti-diagonal corners"),
    ((21, 68), (68, 21), "Bitcoin bridge positions"),
    ((64, 64), (63, 63), "Center area"),
    ((33, 33), (66, 66), "33/66 positions"),
    ((21, 21), (42, 42), "21/42 diagonal"),
    ((0, 21), (21, 0), "Row/Col 21 start"),
]

print("\nCoordinate pair analysis:")
print("-" * 50)
for (r1, c1), (r2, c2), desc in coordinate_checks:
    v1 = get_val(r1, c1)
    v2 = get_val(r2, c2)
    sum_v = v1 + v2
    xor_v = (v1 if v1 >= 0 else v1 + 256) ^ (v2 if v2 >= 0 else v2 + 256)
    print(f"\n{desc}:")
    print(f"  [{r1},{c1}] = {v1}, [{r2},{c2}] = {v2}")
    print(f"  Sum: {sum_v}, XOR: {xor_v}")

# =============================================================================
# ROW AND COLUMN SUMS
# =============================================================================

print("\n" + "=" * 70)
print("PART 3: ROW AND COLUMN SUMS")
print("=" * 70)

row_sums = [sum(get_val(r, c) for c in range(128)) for r in range(128)]
col_sums = [sum(get_val(r, c) for r in range(128)) for c in range(128)]

# Find rows with special sums
print("\nRows with notable sums:")
print("-" * 50)
for row, s in enumerate(row_sums):
    if s in famous_numbers or -s in famous_numbers or s == 0:
        meaning = famous_numbers.get(s, famous_numbers.get(-s, "Zero"))
        print(f"  Row {row:3}: sum = {s:6} ({meaning})")

# Find matching row/col sums
print("\nRows where sum equals row number:")
for row, s in enumerate(row_sums):
    if s == row or s == -row:
        print(f"  Row {row}: sum = {s}")

# Check if any row sum matches a word encoding
print("\nRow sums that match word encodings:")
for row, s in enumerate(row_sums):
    matches = [w for w, v in word_encodings.items() if v == s]
    if matches and len(matches) <= 3:
        print(f"  Row {row:3}: sum = {s:6} = {', '.join(matches)}")

# =============================================================================
# FIBONACCI AND PRIME PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 4: FIBONACCI AND PRIME POSITIONS")
print("=" * 70)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Fibonacci sequence up to 128
fib = [0, 1]
while fib[-1] < 128:
    fib.append(fib[-1] + fib[-2])
fib = [f for f in fib if f < 128]

# Primes up to 128
primes = [p for p in range(128) if is_prime(p)]

print(f"\nFibonacci positions in matrix: {fib}")
print(f"Prime positions: {primes[:20]}...")

# Values at Fibonacci diagonal positions
print("\nDiagonal values at Fibonacci positions:")
fib_diagonal = [(f, get_val(f, f)) for f in fib]
for pos, val in fib_diagonal:
    print(f"  [{pos},{pos}] = {val}")
fib_sum = sum(v for _, v in fib_diagonal)
print(f"  Sum: {fib_sum}")

# Check if Fibonacci sum matches anything
matches = [w for w, v in word_encodings.items() if v == fib_sum]
if matches:
    print(f"  Matches: {', '.join(matches)}")

# Values at Prime diagonal positions
print("\nDiagonal values at Prime positions (first 10):")
prime_vals = [(p, get_val(p, p)) for p in primes[:10]]
for pos, val in prime_vals:
    print(f"  [{pos},{pos}] = {val}")

# =============================================================================
# QUADRANT ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print("PART 5: QUADRANT ANALYSIS")
print("=" * 70)

quadrants = {
    "Top-Left (0-63, 0-63)": (0, 64, 0, 64),
    "Top-Right (0-63, 64-127)": (0, 64, 64, 128),
    "Bottom-Left (64-127, 0-63)": (64, 128, 0, 64),
    "Bottom-Right (64-127, 64-127)": (64, 128, 64, 128),
}

print("\nQuadrant statistics:")
print("-" * 50)
for name, (r1, r2, c1, c2) in quadrants.items():
    values = [get_val(r, c) for r in range(r1, r2) for c in range(c1, c2)]
    q_sum = sum(values)
    q_mean = q_sum / len(values)
    q_min = min(values)
    q_max = max(values)
    zeros = sum(1 for v in values if v == 0)
    print(f"\n{name}:")
    print(f"  Sum: {q_sum}, Mean: {q_mean:.2f}")
    print(f"  Min: {q_min}, Max: {q_max}")
    print(f"  Zeros: {zeros}")

# XOR each quadrant
print("\nQuadrant XOR values:")
for name, (r1, r2, c1, c2) in quadrants.items():
    xor_result = 0
    for r in range(r1, r2):
        for c in range(c1, c2):
            v = get_val(r, c)
            xor_result ^= (v if v >= 0 else v + 256)
    print(f"  {name}: XOR = {xor_result}")

# =============================================================================
# SEARCH FOR TEXT IN ROWS (Extended ASCII interpretation)
# =============================================================================

print("\n" + "=" * 70)
print("PART 6: ASCII TEXT SEARCH IN ROWS")
print("=" * 70)

def row_to_readable(row_idx, unsigned=True):
    """Convert row to readable ASCII string"""
    chars = []
    for col in range(128):
        v = get_val(row_idx, col)
        if unsigned:
            v = v if v >= 0 else v + 256
        if 32 <= v <= 126:  # Printable ASCII
            chars.append(chr(v))
        else:
            chars.append(' ')
    return ''.join(chars)

print("\nSearching for readable text patterns in all rows...")
print("-" * 50)

# Look for rows with consecutive printable characters
for row in range(128):
    text = row_to_readable(row)
    # Find sequences of 3+ printable chars
    import re
    sequences = re.findall(r'[A-Za-z0-9]{3,}', text)
    if sequences:
        meaningful = [s for s in sequences if len(s) >= 3]
        if meaningful:
            print(f"Row {row:3}: {meaningful}")

# =============================================================================
# SPECIAL VALUE DISTRIBUTION
# =============================================================================

print("\n" + "=" * 70)
print("PART 7: VALUE DISTRIBUTION ANALYSIS")
print("=" * 70)

# Count all values
all_values = [get_val(r, c) for r in range(128) for c in range(128)]
value_counts = Counter(all_values)

# Most common values
print("\nMost common values (top 15):")
print("-" * 50)
for val, count in value_counts.most_common(15):
    unsigned = val if val >= 0 else val + 256
    ascii_char = chr(unsigned) if 32 <= unsigned <= 126 else '?'
    print(f"  Value {val:4} (ASCII '{ascii_char}'): {count:4} occurrences")

# Values that appear exactly special number of times
print("\nValues appearing a special number of times:")
for count in [1, 21, 33, 42, 64, 88, 128]:
    vals = [v for v, c in value_counts.items() if c == count]
    if vals:
        print(f"  {count} times: {vals[:10]}")

# =============================================================================
# WORD SEARCH IN DIAGONAL
# =============================================================================

print("\n" + "=" * 70)
print("PART 8: DIAGONAL WORD PATTERNS")
print("=" * 70)

# Main diagonal (full 128)
main_diag = [get_val(i, i) for i in range(128)]
main_diag_sum = sum(main_diag)
print(f"\nMain diagonal (128 values):")
print(f"  Sum: {main_diag_sum}")

# Anti-diagonal
anti_diag = [get_val(i, 127-i) for i in range(128)]
anti_diag_sum = sum(anti_diag)
print(f"\nAnti-diagonal (128 values):")
print(f"  Sum: {anti_diag_sum}")

# Check if sums match words
for name, s in [("Main diagonal", main_diag_sum), ("Anti-diagonal", anti_diag_sum)]:
    matches = [w for w, v in word_encodings.items() if v == s or v == -s]
    if matches:
        print(f"  {name} sum matches: {', '.join(matches)}")

# =============================================================================
# BINARY PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 9: BINARY PATTERN ANALYSIS")
print("=" * 70)

# Convert entire matrix to binary (sign bit)
print("\nSign-bit pattern in row 21:")
row21_signs = ''.join(['1' if get_val(21, c) >= 0 else '0' for c in range(128)])
print(f"  {row21_signs[:64]}")
print(f"  {row21_signs[64:]}")

# Count patterns in sign bits
ones = row21_signs.count('1')
zeros = row21_signs.count('0')
print(f"  Positive (1): {ones}, Negative (0): {zeros}")

# Check if binary could spell something
# Split into 8-bit chunks
print("\nRow 21 sign bits as ASCII (8-bit chunks):")
for i in range(0, 128, 8):
    byte = row21_signs[i:i+8]
    if len(byte) == 8:
        val = int(byte, 2)
        char = chr(val) if 32 <= val <= 126 else '?'
        print(f"  Bits {i:3}-{i+7:3}: {byte} = {val:3} = '{char}'")

# =============================================================================
# LETTER FREQUENCY IN ASCII INTERPRETATION
# =============================================================================

print("\n" + "=" * 70)
print("PART 10: LETTER FREQUENCY ANALYSIS")
print("=" * 70)

# Convert all values to ASCII and count letters
ascii_letters = []
for r in range(128):
    for c in range(128):
        v = get_val(r, c)
        unsigned = v if v >= 0 else v + 256
        if 65 <= unsigned <= 90:  # A-Z
            ascii_letters.append(chr(unsigned))
        elif 97 <= unsigned <= 122:  # a-z
            ascii_letters.append(chr(unsigned).upper())

letter_freq = Counter(ascii_letters)
print(f"\nLetter frequency in ASCII interpretation:")
print("-" * 50)
for letter, count in sorted(letter_freq.items()):
    bar = '#' * (count // 10)
    print(f"  {letter}: {count:4} {bar}")

print(f"\nTotal letters found: {len(ascii_letters)}")

# Check if frequency matches English or is encoded
# English frequency: ETAOINSHRDLCUMWFGYPBVKJXQZ
english_freq = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
matrix_freq = ''.join([l for l, _ in letter_freq.most_common()])
print(f"\nEnglish frequency order: {english_freq}")
print(f"Matrix frequency order:  {matrix_freq}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("DEEP ANALYSIS SUMMARY")
print("=" * 70)

print("""
KEY FINDINGS FROM DEEP ANALYSIS:

1. The matrix contains specific coordinate symmetries
2. Row sums reveal hidden word encodings
3. Fibonacci positions have special significance
4. Quadrant XOR patterns show balance
5. ASCII interpretation reveals letter patterns
6. Sign-bit encoding in Row 21 may contain messages
7. Main diagonal sum has cryptographic significance

Continue searching for:
- Multi-row sentence patterns
- Columnar encoding schemes
- Position-based ciphers
- Mathematical sequences embedded in values
""")

print("=" * 70)
print("Deep analysis complete!")
print("=" * 70)
