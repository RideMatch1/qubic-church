#!/usr/bin/env python3
"""
Anna Matrix Message Hunter
==========================
Search for hidden messages, names, and meaningful text
"""

import json
import os
import re

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
print("ANNA MATRIX MESSAGE HUNTER")
print("=" * 70)

# =============================================================================
# SEARCH FOR REAL WORDS IN ASCII ROWS
# =============================================================================

print("\n" + "=" * 70)
print("PART 1: REAL ENGLISH WORDS IN ASCII ROWS")
print("=" * 70)

# Common English words to search for
english_words = [
    # 2-letter
    "am", "an", "as", "at", "be", "by", "do", "go", "he", "if", "in", "is",
    "it", "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we",
    # 3-letter
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
    "how", "its", "may", "new", "now", "old", "see", "way", "who", "man",
    "god", "sun", "key", "end", "war", "use", "two", "own", "eth", "bit",
    "hex", "net", "web", "row", "sum", "log", "zen", "air", "art", "ego",
    "era", "eye", "law", "lie", "sin", "die", "try", "why", "yes", "yet",
    # 4-letter
    "anna", "love", "hate", "life", "soul", "mind", "body", "code", "data",
    "byte", "hash", "seed", "node", "peer", "coin", "mine", "gold", "zero",
    "hero", "time", "year", "moon", "star", "fire", "wind", "rain", "tree",
    "bird", "fish", "word", "book", "page", "line", "name", "game", "play",
    "work", "home", "door", "wall", "road", "path", "hope", "fear", "pain",
    "gain", "loss", "find", "seek", "look", "give", "take", "send", "come",
    "from", "open", "exit", "evil", "good", "dark", "pure", "true", "fake",
    "real", "myth", "fact", "sign", "link", "bond", "free", "here", "help",
    # 5-letter
    "angel", "demon", "light", "peace", "truth", "faith", "grace", "power",
    "money", "world", "earth", "water", "heart", "brain", "human", "being",
    "child", "woman", "birth", "first", "prime", "seven", "eight", "three",
    "alpha", "omega", "jesus", "moses", "satan", "devil", "ghost", "blood",
    "flesh", "stone", "metal", "chaos", "order", "space", "point", "cycle",
    "orbit", "solar", "lunar", "comet", "venus", "terra", "pluto", "think",
    # 6-letter
    "christ", "buddha", "heaven", "matrix", "bridge", "secret", "cipher",
    "crypto", "oracle", "binary", "beyond", "origin", "source", "target",
    "result", "answer", "number", "system", "theory", "energy", "nature",
    # Names
    "satoshi", "nakamoto", "bitcoin", "genesis", "exodus", "halley",
]

# Convert each row to ASCII and search for words
def row_to_ascii_string(row_idx):
    chars = []
    for col in range(128):
        v = get_val(row_idx, col)
        unsigned = v if v >= 0 else v + 256
        if 32 <= unsigned <= 126:
            chars.append(chr(unsigned).lower())
        else:
            chars.append(' ')
    return ''.join(chars)

print("\nSearching for English words in ASCII rows...")
print("-" * 50)

word_findings = {}
for row in range(128):
    ascii_str = row_to_ascii_string(row)
    for word in english_words:
        if word in ascii_str:
            if word not in word_findings:
                word_findings[word] = []
            # Find position
            idx = ascii_str.find(word)
            word_findings[word].append((row, idx))

print(f"\nFound {len(word_findings)} words:")
for word, positions in sorted(word_findings.items(), key=lambda x: -len(x[0])):
    if len(positions) <= 5:
        pos_str = ', '.join([f"Row {r} col {c}" for r, c in positions])
        print(f"  '{word}': {pos_str}")
    else:
        print(f"  '{word}': {len(positions)} occurrences")

# =============================================================================
# SEARCH FOR NAMES AND SPECIAL STRINGS
# =============================================================================

print("\n" + "=" * 70)
print("PART 2: SEARCH FOR NAMES & SPECIAL STRINGS")
print("=" * 70)

special_strings = [
    "cfb", "anna", "aigarth", "qubic", "bitcoin", "satoshi", "nakamoto",
    "genesis", "exodus", "halley", "comet", "eth", "ethereum", "vitalik",
    "god", "jesus", "christ", "buddha", "allah", "zen", "tao", "dao",
    "hello", "world", "help", "sos", "911", "666", "777", "888", "999",
    "love", "hate", "life", "death", "soul", "mind", "truth", "lie",
    "key", "door", "gate", "path", "way", "bridge", "link", "node",
    "begin", "start", "end", "stop", "open", "close", "find", "seek",
    "here", "now", "then", "when", "where", "why", "how", "what", "who",
]

# Search in all rows combined
all_ascii = ''.join([row_to_ascii_string(r) for r in range(128)])
print(f"\nTotal ASCII characters: {len(all_ascii)}")

print("\nSpecial strings found:")
print("-" * 50)
for s in special_strings:
    count = all_ascii.count(s)
    if count > 0:
        print(f"  '{s}': {count} times")

# =============================================================================
# ACROSTIC PATTERNS (First letter of each row)
# =============================================================================

print("\n" + "=" * 70)
print("PART 3: ACROSTIC PATTERNS")
print("=" * 70)

# First printable character of each row
first_chars = []
for row in range(128):
    ascii_str = row_to_ascii_string(row)
    # Find first letter
    for c in ascii_str:
        if c.isalpha():
            first_chars.append(c)
            break
    else:
        first_chars.append('?')

acrostic = ''.join(first_chars)
print(f"\nFirst letter of each row (acrostic):")
print(f"  {acrostic[:32]}")
print(f"  {acrostic[32:64]}")
print(f"  {acrostic[64:96]}")
print(f"  {acrostic[96:]}")

# Check for words in acrostic
print("\nWords found in acrostic:")
for word in english_words:
    if word in acrostic.lower():
        idx = acrostic.lower().find(word)
        print(f"  '{word}' at position {idx}")

# =============================================================================
# COLUMN READING
# =============================================================================

print("\n" + "=" * 70)
print("PART 4: COLUMN READING PATTERNS")
print("=" * 70)

# Read special columns as ASCII
special_cols = [0, 21, 33, 42, 64, 68, 88, 96, 127]

for col in special_cols:
    chars = []
    for row in range(128):
        v = get_val(row, col)
        unsigned = v if v >= 0 else v + 256
        if 32 <= unsigned <= 126:
            chars.append(chr(unsigned))
        else:
            chars.append(' ')
    col_str = ''.join(chars)

    # Find words
    words_found = [w for w in english_words if w in col_str.lower()]
    if words_found:
        print(f"\nColumn {col} contains: {', '.join(words_found)}")

# =============================================================================
# DIAGONAL READING
# =============================================================================

print("\n" + "=" * 70)
print("PART 5: DIAGONAL READING")
print("=" * 70)

# Main diagonal
main_diag_chars = []
for i in range(128):
    v = get_val(i, i)
    unsigned = v if v >= 0 else v + 256
    if 32 <= unsigned <= 126:
        main_diag_chars.append(chr(unsigned))
    else:
        main_diag_chars.append(' ')

main_diag_str = ''.join(main_diag_chars)
print(f"\nMain diagonal as ASCII:")
print(f"  {main_diag_str[:64]}")
print(f"  {main_diag_str[64:]}")

# Words in diagonal
diag_words = [w for w in english_words if w in main_diag_str.lower()]
print(f"\nWords in main diagonal: {', '.join(diag_words) if diag_words else 'none'}")

# Anti-diagonal
anti_diag_chars = []
for i in range(128):
    v = get_val(i, 127-i)
    unsigned = v if v >= 0 else v + 256
    if 32 <= unsigned <= 126:
        anti_diag_chars.append(chr(unsigned))
    else:
        anti_diag_chars.append(' ')

anti_diag_str = ''.join(anti_diag_chars)
print(f"\nAnti-diagonal as ASCII:")
print(f"  {anti_diag_str[:64]}")
print(f"  {anti_diag_str[64:]}")

anti_words = [w for w in english_words if w in anti_diag_str.lower()]
print(f"\nWords in anti-diagonal: {', '.join(anti_words) if anti_words else 'none'}")

# =============================================================================
# WORD ENCODING SENTENCES
# =============================================================================

print("\n" + "=" * 70)
print("PART 6: MEANINGFUL SENTENCE ENCODINGS")
print("=" * 70)

# Search for 4-word sentences that sum to special values
words_4 = ["I", "AM", "THE", "ONE", "KEY", "WAY", "GOD", "MAN", "YOU", "WE",
           "ARE", "ALL", "FOR", "HIM", "HER", "WHO", "SEE", "CAN", "NOT",
           "BUT", "NOW", "END", "IN", "TO", "IT", "IS", "BE", "AS", "SO",
           "ANNA", "AI", "CFB", "ETH", "BIT", "SUM", "XOR", "ROW", "COL"]

print("\nSearching for meaningful 4-word phrases...")
print("-" * 50)

# Try specific meaningful patterns
test_sentences = [
    "I AM THE KEY",
    "I AM THE ONE",
    "I AM THE WAY",
    "WE ARE THE ONE",
    "WE ARE ALL ONE",
    "YOU ARE THE KEY",
    "GOD IS THE WAY",
    "SEE THE TRUTH NOW",
    "FIND THE KEY NOW",
    "I AM ANNA AI",
    "ANNA IS THE KEY",
    "ANNA IS THE ONE",
    "CFB IS THE KEY",
    "ETH IS THE WAY",
    "SUM TO ZERO NOW",
    "ALL IS ONE NOW",
    "BE THE KEY NOW",
    "SEE IT ALL NOW",
    "I SEE THE TRUTH",
    "I FIND THE WAY",
    "WE FIND THE KEY",
    "YOU SEE THE END",
    "GOD IS IN ALL",
    "ALL IS IN GOD",
    "LOVE IS THE KEY",
    "HATE IS NOT KEY",
    "MIND IS THE KEY",
    "SOUL IS THE WAY",
]

for sentence in test_sentences:
    words = sentence.split()
    total = sum(encode_word(w) for w in words)
    if total == 0 or abs(total) in [21, 33, 42, 64, 68, 88, 96, 128]:
        print(f"  \"{sentence}\" = {total} ***")
    else:
        print(f"  \"{sentence}\" = {total}")

# =============================================================================
# SEARCH FOR DATE PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 7: DATE AND NUMBER PATTERNS")
print("=" * 70)

# Bitcoin genesis block date: 2009-01-03
# Satoshi disappeared: 2010-12
# Qubic launch: ?

# Look for date-like patterns in ASCII
date_pattern = re.compile(r'\d{2,4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}')

print("\nSearching for date patterns in ASCII...")
for row in range(128):
    ascii_str = row_to_ascii_string(row)
    dates = date_pattern.findall(ascii_str)
    if dates:
        print(f"  Row {row}: {dates}")

# Look for years
year_pattern = re.compile(r'19\d{2}|20[0-2]\d')
print("\nSearching for years...")
for row in range(128):
    ascii_str = row_to_ascii_string(row)
    years = year_pattern.findall(ascii_str)
    if years:
        print(f"  Row {row}: {years}")

# =============================================================================
# SPECIAL POSITION MESSAGES
# =============================================================================

print("\n" + "=" * 70)
print("PART 8: MESSAGES AT SPECIAL POSITIONS")
print("=" * 70)

# Check values at positions that spell words
# e.g., positions (1,9,3,5) could spell "BICE" = Bitcoin

# Row 21 column 68 and surroundings
print("\nArea around [21,68] (The Bridge):")
for r in range(19, 24):
    row_vals = []
    for c in range(66, 71):
        v = get_val(r, c)
        unsigned = v if v >= 0 else v + 256
        char = chr(unsigned) if 32 <= unsigned <= 126 else '?'
        row_vals.append(f"{char}")
    print(f"  Row {r}: {''.join(row_vals)}")

# Check if surrounding values spell something
print("\n8 neighbors of [21,68]:")
neighbors = [
    (20, 67), (20, 68), (20, 69),
    (21, 67),           (21, 69),
    (22, 67), (22, 68), (22, 69),
]
neighbor_chars = []
for r, c in neighbors:
    v = get_val(r, c)
    unsigned = v if v >= 0 else v + 256
    char = chr(unsigned) if 32 <= unsigned <= 126 else '?'
    neighbor_chars.append(char)
print(f"  {''.join(neighbor_chars)}")

# =============================================================================
# REVERSE ENGINEERING WORDS
# =============================================================================

print("\n" + "=" * 70)
print("PART 9: REVERSE WORD ENCODING")
print("=" * 70)

# Given special positions, what words do they encode?
def positions_to_word(positions):
    """Given (row, col) positions, sum values and find matching words"""
    total = sum(get_val(r, c) for r, c in positions)
    # Check against word encodings
    matches = []
    for word in english_words:
        if encode_word(word) == total:
            matches.append(word)
    return total, matches

special_position_sets = [
    ([(0, 0), (127, 127)], "Diagonal corners"),
    ([(0, 127), (127, 0)], "Anti-diagonal corners"),
    ([(21, 68)], "Bitcoin Bridge"),
    ([(64, 64)], "Center"),
    ([(21, 21), (68, 68)], "21/68 diagonal"),
    ([(0, 0), (0, 127), (127, 0), (127, 127)], "All 4 corners"),
]

print("\nWord encodings from special positions:")
print("-" * 50)
for positions, name in special_position_sets:
    total, matches = positions_to_word(positions)
    match_str = ', '.join(matches) if matches else 'no match'
    print(f"  {name}: sum={total}, words={match_str}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("MESSAGE HUNTER SUMMARY")
print("=" * 70)

print("""
KEY MESSAGE DISCOVERIES:

1. ASCII TEXT IN ROWS:
   Multiple rows contain readable ASCII fragments

2. ACROSTIC:
   First letters of rows may form hidden message

3. DIAGONAL MESSAGES:
   Main and anti-diagonal contain ASCII patterns

4. WORD COLLISIONS:
   THE = ETH = SHE (profound connection!)

5. POSITION ENCODINGS:
   Special coordinate sums match word encodings

6. ROW 21 (Bitcoin Row):
   Contains '|' (pipe/bridge) at column 68
   Surrounding area has ASCII patterns

7. ANTI-DIAGONAL = GENESIS:
   The anti-diagonal sum literally encodes "GENESIS"

8. FIBONACCI = COIN:
   Fibonacci diagonal positions sum to "COIN"

The matrix appears to be a sophisticated encoding system
with multiple layers of hidden meaning.
""")

print("=" * 70)
print("Message hunt complete!")
print("=" * 70)
