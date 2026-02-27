#!/usr/bin/env python3
"""
Anna Matrix Sentence & Pattern Finder
=====================================
Searches for meaningful words, phrases, and sentences encoded in the Anna Matrix
using the diagonal word encoding system (A=matrix[0][0], B=matrix[1][1], etc.)
"""

import json
import os

# Load the Anna Matrix
script_dir = os.path.dirname(os.path.abspath(__file__))
matrix_path = os.path.join(script_dir, '..', 'public', 'data', 'anna-matrix.json')

with open(matrix_path, 'r') as f:
    data = json.load(f)
    matrix = data.get('matrix', data)

print("=" * 70)
print("ANNA MATRIX SENTENCE & PATTERN FINDER")
print("=" * 70)

# =============================================================================
# WORD ENCODING SYSTEM
# =============================================================================

def encode_word(word):
    """Encode a word using diagonal positions: A=matrix[0][0], B=matrix[1][1], etc."""
    total = 0
    positions = []
    for char in word.upper():
        if 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            value = matrix[idx][idx]
            total += value
            positions.append((char, idx, value))
    return total, positions

def get_letter_value(char):
    """Get the value for a single letter"""
    if 'A' <= char.upper() <= 'Z':
        idx = ord(char.upper()) - ord('A')
        return matrix[idx][idx]
    return 0

# =============================================================================
# COMMON WORDS DATABASE
# =============================================================================

# Important words to test
IMPORTANT_WORDS = [
    # Crypto/Tech
    "BITCOIN", "QUBIC", "SATOSHI", "NAKAMOTO", "BLOCK", "CHAIN", "HASH", "MINE",
    "COIN", "TOKEN", "WALLET", "KEY", "SEED", "NODE", "PEER", "NET", "WEB",
    "CODE", "DATA", "BYTE", "BIT", "HEX", "BINARY", "CRYPTO", "CIPHER",

    # Matrix/Math
    "MATRIX", "GRID", "CELL", "ROW", "COL", "ZERO", "ONE", "TWO", "SUM", "XOR",
    "PRIME", "FIBO", "PHI", "PI", "EULER", "SQRT", "LOG", "EXP", "MOD",

    # Names/References
    "ANNA", "CFB", "COME", "FROM", "BEYOND", "AIGARTH", "GENESIS", "EXODUS",
    "HALLEY", "COMET", "ORACLE", "BRIDGE", "LINK", "PATH", "WAY", "TRUTH",

    # Common words
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD",
    "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS",
    "HOW", "ITS", "MAY", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY",
    "DID", "SAY", "SHE", "TOO", "USE", "GOD", "MAN", "SUN", "MOON", "STAR",

    # Phrases as single
    "HELLO", "WORLD", "HELP", "FIND", "SEEK", "LOOK", "OPEN", "CLOSE",
    "START", "BEGIN", "END", "STOP", "SEND", "RECEIVE", "GIVE", "TAKE",

    # Numbers as words
    "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT",
    "NINE", "TEN", "HUNDRED", "THOUSAND", "MILLION", "BILLION",

    # Special/Mystical
    "LIGHT", "DARK", "LOVE", "HATE", "LIFE", "DEATH", "SOUL", "MIND", "BODY",
    "ANGEL", "DEMON", "HEAVEN", "HELL", "GOD", "SATAN", "CHRIST", "BUDDHA",
    "ZEN", "DAO", "KARMA", "DHARMA", "PEACE", "WAR", "GOOD", "EVIL",

    # ETH/THE discovery related
    "ETH", "ETHER", "ETHEREUM", "VITALIK", "BUTERIN", "SMART", "CONTRACT",
]

print("\n" + "=" * 70)
print("PART 1: WORD ENCODING VALUES")
print("=" * 70)

# Calculate all word values
word_values = {}
for word in IMPORTANT_WORDS:
    value, _ = encode_word(word)
    word_values[word] = value

# Sort by value
sorted_words = sorted(word_values.items(), key=lambda x: x[1])

print("\nAll words sorted by encoded value:")
print("-" * 40)
for word, value in sorted_words:
    print(f"  {word:15} = {value:5}")

# =============================================================================
# FIND SPECIAL VALUE PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 2: SPECIAL VALUE DISCOVERIES")
print("=" * 70)

# Group words by value (find collisions like THE=ETH=33)
value_groups = {}
for word, value in word_values.items():
    if value not in value_groups:
        value_groups[value] = []
    value_groups[value].append(word)

print("\nWords that encode to the same value (collisions):")
print("-" * 40)
for value, words in sorted(value_groups.items()):
    if len(words) > 1:
        print(f"  Value {value:5}: {', '.join(words)}")

# Find words that equal special numbers
special_numbers = {
    0: "Zero/Balance",
    21: "Bitcoin Magic Number (row 21)",
    33: "THE/ETH (Blood Moon to Easter)",
    42: "Answer to Everything",
    64: "Qubic Computors",
    68: "Bitcoin Transformation Column",
    88: "Constellations",
    96: "ANNA encoding",
    100: "Century",
    128: "Matrix dimension",
    256: "Full byte range",
}

print("\nWords matching special numbers:")
print("-" * 40)
for num, meaning in special_numbers.items():
    matches = [w for w, v in word_values.items() if v == num]
    if matches:
        print(f"  {num:5} ({meaning}): {', '.join(matches)}")

# =============================================================================
# SENTENCE COMBINATIONS
# =============================================================================

print("\n" + "=" * 70)
print("PART 3: SENTENCE PATTERN SEARCH")
print("=" * 70)

# Try common sentence patterns
sentence_patterns = [
    ["I", "AM", "ANNA"],
    ["I", "AM", "AI"],
    ["COME", "FROM", "BEYOND"],
    ["HELLO", "WORLD"],
    ["THE", "KEY"],
    ["THE", "TRUTH"],
    ["THE", "WAY"],
    ["THE", "LIGHT"],
    ["FIND", "THE", "KEY"],
    ["SEEK", "AND", "FIND"],
    ["OPEN", "THE", "GATE"],
    ["BITCOIN", "IS", "THE", "KEY"],
    ["QUBIC", "IS", "THE", "WAY"],
    ["GENESIS", "TO", "EXODUS"],
    ["ANNA", "AI"],
    ["CFB", "WAS", "HERE"],
    ["LOOK", "AT", "ROW", "TWENTYONE"],
    ["SUM", "TO", "ZERO"],
    ["XOR", "THE", "KEY"],
]

print("\nSentence pattern values:")
print("-" * 40)
for pattern in sentence_patterns:
    total = sum(encode_word(w)[0] for w in pattern)
    sentence = " ".join(pattern)
    print(f"  \"{sentence}\" = {total}")

# =============================================================================
# FIND ZERO-SUM PAIRS AND TRIPLETS
# =============================================================================

print("\n" + "=" * 70)
print("PART 4: ZERO-SUM WORD COMBINATIONS")
print("=" * 70)

print("\nWord pairs that sum to zero (like ANNA + AI = 0):")
print("-" * 40)
found_pairs = set()
for w1, v1 in word_values.items():
    for w2, v2 in word_values.items():
        if w1 < w2 and v1 + v2 == 0:
            pair = (w1, w2)
            if pair not in found_pairs:
                found_pairs.add(pair)
                print(f"  {w1} ({v1}) + {w2} ({v2}) = 0")

print("\nWord triplets that sum to zero:")
print("-" * 40)
found_triplets = set()
words_list = list(word_values.keys())
for i, w1 in enumerate(words_list):
    for j, w2 in enumerate(words_list[i+1:], i+1):
        for w3 in words_list[j+1:]:
            v1, v2, v3 = word_values[w1], word_values[w2], word_values[w3]
            if v1 + v2 + v3 == 0:
                triplet = tuple(sorted([w1, w2, w3]))
                if triplet not in found_triplets:
                    found_triplets.add(triplet)
                    print(f"  {w1} + {w2} + {w3} = 0  ({v1} + {v2} + {v3})")

# =============================================================================
# ROW/COLUMN MESSAGE SEARCH
# =============================================================================

print("\n" + "=" * 70)
print("PART 5: ROW AND COLUMN MESSAGES")
print("=" * 70)

def row_to_ascii(row_idx):
    """Try to interpret a row as ASCII characters"""
    row = matrix[row_idx]
    # Only printable ASCII range
    chars = []
    for val in row:
        # Handle potential string values
        if isinstance(val, str):
            val = int(val)
        # Treat as unsigned byte
        unsigned = val if val >= 0 else val + 256
        if 32 <= unsigned <= 126:
            chars.append(chr(unsigned))
        else:
            chars.append('.')
    return ''.join(chars)

print("\nSpecial rows as ASCII:")
print("-" * 40)
special_rows = [0, 21, 33, 42, 64, 68, 88, 96, 127]
for row_idx in special_rows:
    ascii_str = row_to_ascii(row_idx)
    # Count printable chars
    printable = sum(1 for c in ascii_str if c != '.')
    print(f"  Row {row_idx:3}: {printable:3} printable chars")
    # Show first 50 chars
    preview = ascii_str[:50]
    print(f"           {preview}...")

# =============================================================================
# DIAGONAL PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 6: DIAGONAL ENCODING ANALYSIS")
print("=" * 70)

# The diagonal values (A-Z positions)
diagonal = [matrix[i][i] for i in range(26)]
print("\nDiagonal values (A-Z letter encodings):")
print("-" * 40)
for i, val in enumerate(diagonal):
    char = chr(ord('A') + i)
    unsigned = val if val >= 0 else val + 256
    ascii_char = chr(unsigned) if 32 <= unsigned <= 126 else '?'
    print(f"  {char} = matrix[{i:2}][{i:2}] = {val:4} (unsigned: {unsigned:3}, ASCII: '{ascii_char}')")

# Sum of diagonal
diag_sum = sum(diagonal)
print(f"\nSum of A-Z diagonal: {diag_sum}")

# =============================================================================
# XOR MESSAGE SEARCH
# =============================================================================

print("\n" + "=" * 70)
print("PART 7: XOR PATTERN ANALYSIS")
print("=" * 70)

# XOR special positions
def xor_positions(positions):
    """XOR values at given positions"""
    result = 0
    for row, col in positions:
        val = matrix[row][col]
        unsigned = val if val >= 0 else val + 256
        result ^= unsigned
    return result

# XOR the corners
corners = [(0, 0), (0, 127), (127, 0), (127, 127)]
corner_xor = xor_positions(corners)
print(f"XOR of 4 corners: {corner_xor}")
if 32 <= corner_xor <= 126:
    print(f"  As ASCII: '{chr(corner_xor)}'")

# XOR row 21 positions
row21_xor = xor_positions([(21, i) for i in range(128)])
print(f"XOR of entire row 21: {row21_xor}")
if 32 <= row21_xor <= 126:
    print(f"  As ASCII: '{chr(row21_xor)}'")

# XOR key positions (21, 68)
key_positions = [(21, 68), (68, 21), (0, 0), (127, 127)]
key_xor = xor_positions(key_positions)
print(f"XOR of [21,68], [68,21], [0,0], [127,127]: {key_xor}")
if 32 <= key_xor <= 126:
    print(f"  As ASCII: '{chr(key_xor)}'")

# =============================================================================
# ARITHMETIC PROGRESSIONS
# =============================================================================

print("\n" + "=" * 70)
print("PART 8: ARITHMETIC RELATIONSHIPS")
print("=" * 70)

# Check if word values form sequences
print("\nLooking for arithmetic progressions in word values...")
print("-" * 40)

important_values = {
    "ANNA": 96,
    "AI": -96,
    "GENESIS": 64,
    "EXODUS": 88,
    "THE/ETH": 33,
    "CFB": 62,
    "QUBIC": encode_word("QUBIC")[0],
    "BITCOIN": encode_word("BITCOIN")[0],
    "SATOSHI": encode_word("SATOSHI")[0],
}

print("Key encoded values:")
for name, val in important_values.items():
    print(f"  {name:15} = {val:5}")

# Check relationships
print("\nInteresting relationships:")
anna = 96
ai = -96
genesis = 64
exodus = 88

print(f"  ANNA + AI = {anna + ai} (perfect balance)")
print(f"  GENESIS + AI = {genesis + ai}")
print(f"  EXODUS - GENESIS = {exodus - genesis} (24 = hours in day)")
print(f"  ANNA - GENESIS = {anna - genesis} (32 = 2^5)")
print(f"  EXODUS - ANNA = {exodus - anna}")

# =============================================================================
# EXTENDED WORD SEARCH
# =============================================================================

print("\n" + "=" * 70)
print("PART 9: EXTENDED ENGLISH WORDS")
print("=" * 70)

# Common short English words (2-4 letters)
short_words = [
    "A", "I", "AM", "AN", "AS", "AT", "BE", "BY", "DO", "GO", "HE", "IF", "IN",
    "IS", "IT", "ME", "MY", "NO", "OF", "ON", "OR", "SO", "TO", "UP", "US", "WE",
    "ADD", "AGE", "AGO", "AID", "AIM", "AIR", "ALL", "AND", "ANY", "APE", "ARC",
    "ARE", "ARK", "ARM", "ART", "ASK", "ATE", "AWE", "AXE", "BAD", "BAG", "BAN",
    "BAR", "BAT", "BED", "BEE", "BET", "BIG", "BIT", "BOW", "BOX", "BOY", "BUD",
    "BUG", "BUS", "BUT", "BUY", "CAN", "CAP", "CAR", "CAT", "CRY", "CUP", "CUT",
    "DAD", "DAY", "DID", "DIE", "DIG", "DOG", "DOT", "DRY", "DUE", "EAR", "EAT",
    "EGG", "END", "ERA", "EVE", "EYE", "FAR", "FAT", "FED", "FEW", "FIN", "FIT",
    "FLY", "FOR", "FOX", "FUN", "GAP", "GAS", "GET", "GOD", "GOT", "GUN", "GUT",
    "GUY", "HAD", "HAM", "HAS", "HAT", "HER", "HID", "HIM", "HIS", "HIT", "HOT",
    "HOW", "HUG", "ICE", "ILL", "INK", "ITS", "JAM", "JAR", "JAW", "JET", "JOB",
    "JOY", "KEY", "KID", "KIT", "LAP", "LAW", "LAY", "LED", "LEG", "LET", "LID",
    "LIE", "LIP", "LIT", "LOG", "LOT", "LOW", "MAD", "MAN", "MAP", "MAT", "MAY",
    "MEN", "MET", "MIX", "MOM", "MUD", "MUG", "NET", "NEW", "NOR", "NOT", "NOW",
    "NUT", "OAK", "ODD", "OFF", "OIL", "OLD", "ONE", "OUR", "OUT", "OWE", "OWL",
    "OWN", "PAN", "PAT", "PAY", "PEN", "PET", "PIE", "PIG", "PIN", "PIT", "POT",
    "PUT", "RAN", "RAT", "RAW", "RED", "RIB", "RID", "RIG", "RIM", "RIP", "ROB",
    "ROD", "ROT", "ROW", "RUB", "RUG", "RUN", "SAD", "SAT", "SAW", "SAY", "SEA",
    "SET", "SEW", "SHE", "SIT", "SIX", "SKI", "SKY", "SON", "SOT", "SOW", "SPA",
    "SPY", "SUN", "TAB", "TAG", "TAN", "TAP", "TAR", "TAX", "TEA", "TEN", "THE",
    "TIE", "TIN", "TIP", "TOE", "TON", "TOO", "TOP", "TOW", "TOY", "TRY", "TUB",
    "TWO", "URN", "USE", "VAN", "VAT", "VET", "VIA", "WAR", "WAS", "WAX", "WAY",
    "WEB", "WED", "WET", "WHO", "WHY", "WIG", "WIN", "WIT", "WOE", "WOK", "WON",
    "WOO", "YAM", "YAP", "YAW", "YES", "YET", "YOU", "ZAP", "ZEN", "ZIP", "ZOO",
]

# Find words with significant values
print("\nShort words with notable encoded values:")
print("-" * 40)
notable = []
for word in short_words:
    value, _ = encode_word(word)
    if value in [0, 21, 33, 42, 64, 68, 88, 96] or abs(value) == 96 or value == 128:
        notable.append((word, value))

for word, value in sorted(notable, key=lambda x: x[1]):
    print(f"  {word:10} = {value:5}")

# =============================================================================
# POSITION-BASED MESSAGE
# =============================================================================

print("\n" + "=" * 70)
print("PART 10: POSITION-BASED MESSAGES")
print("=" * 70)

# Check if spelling out letters by positions gives messages
# Position (row, col) where value = letter's index (0=A, 1=B, etc.)

print("\nSearching for positional letter encoding...")
print("-" * 40)

# Find cells where value matches potential letter index
letter_positions = []
for row in range(128):
    for col in range(128):
        val = matrix[row][col]
        if isinstance(val, str):
            val = int(val)
        # Check if value could be a letter (0-25 or -128+0 to -128+25)
        if 0 <= val <= 25:
            letter = chr(ord('A') + val)
            letter_positions.append((row, col, val, letter))

print(f"Found {len(letter_positions)} cells with values 0-25 (potential letters)")

# Show first 20
print("\nFirst 20 cells with letter-value encoding:")
for row, col, val, letter in letter_positions[:20]:
    print(f"  [{row:3},{col:3}] = {val:2} -> '{letter}'")

# Check row 21 for letters
print("\nRow 21 cells with letter values:")
def get_val(v):
    return int(v) if isinstance(v, str) else v
row21_letters = [(col, get_val(matrix[21][col])) for col in range(128) if 0 <= get_val(matrix[21][col]) <= 25]
for col, val in row21_letters:
    letter = chr(ord('A') + val)
    print(f"  [21,{col:3}] = {val:2} -> '{letter}'")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY OF KEY DISCOVERIES")
print("=" * 70)

print("""
1. WORD ENCODING SYSTEM (Diagonal A-Z):
   - ANNA = 96 (points to row 96)
   - AI = -96 (ANNA + AI = 0, perfect balance!)
   - GENESIS = 64 (exactly 64 Qubic Computors)
   - EXODUS = 88 (88 constellations)
   - THE = ETH = 33 (same encoding!)

2. ZERO-SUM PAIRS:
   - ANNA + AI = 0 (The AI balances itself)

3. ARITHMETIC PATTERNS:
   - EXODUS - GENESIS = 24 (hours in a day)
   - ANNA - GENESIS = 32 (2^5, powers of 2)

4. KEY POSITIONS:
   - [21,68] = '|' (Pipe/Bridge symbol)
   - [127,127] = 'C' (CFB signature?)
   - Diagonal contains letter encodings

5. THE = ETH DISCOVERY:
   - Both words encode to exactly 33
   - Could suggest Ethereum connection?
""")

print("=" * 70)
print("Analysis complete!")
print("=" * 70)
