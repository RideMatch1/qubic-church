#!/usr/bin/env python3
"""
===============================================================================
                    G O D   M O D E   A C T I V A T E D
===============================================================================
ULTIMATIVE MATRIX-ANALYSE - KEINE GRENZEN - ALLES FINDEN

This script performs EXHAUSTIVE analysis of the Anna-Matrix:
1. ALL XOR combinations (not just symmetric pairs)
2. ALL possible message extractions
3. ALL coordinate-based patterns
4. ALL binary/hex interpretations
5. ALL frequency patterns
6. ALL statistical anomalies
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import hashlib
import re
import itertools

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗  ██████╗ ██████╗     ███╗   ███╗ ██████╗ ██████╗ ███████╗
  ██╔════╝ ██╔═══██╗██╔══██╗    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝
  ██║  ███╗██║   ██║██║  ██║    ██╔████╔██║██║   ██║██║  ██║█████╗
  ██║   ██║██║   ██║██║  ██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝
  ╚██████╔╝╚██████╔╝██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
   ╚═════╝  ╚═════╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
                     ULTIMATE MATRIX ANALYSIS
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Store ALL discoveries
discoveries = {
    "timestamp": datetime.now().isoformat(),
    "god_mode": True,
    "findings": []
}

def add_finding(category, description, data, significance="unknown"):
    discoveries["findings"].append({
        "category": category,
        "description": description,
        "data": data,
        "significance": significance
    })
    print(f"  [FOUND] {category}: {description}")

# ==============================================================================
# PHASE 1: COMPLETE XOR MATRIX
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 1: COMPLETE XOR ANALYSIS")
print("=" * 80)

# XOR every row with every other row
print("\n  Computing ALL row-row XORs...")
row_xor_words = {}

for r1 in range(128):
    for r2 in range(r1 + 1, 128):
        row1 = [int(matrix[r1, c]) for c in range(128)]
        row2 = [int(matrix[r2, c]) for c in range(128)]
        xor = [row1[c] ^ row2[c] for c in range(128)]

        # Extract all printable ASCII
        ascii_str = ''.join(chr(abs(x)) for x in xor if 32 <= abs(x) <= 126)

        # Find words (3+ letters)
        words = re.findall(r'[a-zA-Z]{3,}', ascii_str)

        if words:
            key = f"Row{r1}⊕Row{r2}"
            row_xor_words[key] = {
                "words": words,
                "full": ascii_str[:100],
                "pair_sum": r1 + r2
            }

print(f"  Row pairs with words: {len(row_xor_words)}")

# Find most interesting ones
sorted_pairs = sorted(row_xor_words.items(), key=lambda x: len(x[1]["words"]), reverse=True)
print("\n  Top 10 row XOR pairs with most words:")
for key, val in sorted_pairs[:10]:
    print(f"    {key}: {val['words'][:5]} (sum={val['pair_sum']})")
    add_finding("XOR_WORDS", f"{key} contains words", val, "medium")

# Column XOR
print("\n  Computing ALL column-column XORs...")
col_xor_words = {}

for c1 in range(128):
    for c2 in range(c1 + 1, 128):
        col1 = [int(matrix[r, c1]) for r in range(128)]
        col2 = [int(matrix[r, c2]) for r in range(128)]
        xor = [col1[r] ^ col2[r] for r in range(128)]

        ascii_str = ''.join(chr(abs(x)) for x in xor if 32 <= abs(x) <= 126)
        words = re.findall(r'[a-zA-Z]{3,}', ascii_str)

        if words:
            key = f"Col{c1}⊕Col{c2}"
            col_xor_words[key] = {
                "words": words,
                "full": ascii_str[:100],
                "pair_sum": c1 + c2
            }

print(f"  Column pairs with words: {len(col_xor_words)}")

sorted_cols = sorted(col_xor_words.items(), key=lambda x: len(x[1]["words"]), reverse=True)
print("\n  Top 10 column XOR pairs with most words:")
for key, val in sorted_cols[:10]:
    print(f"    {key}: {val['words'][:5]} (sum={val['pair_sum']})")
    add_finding("XOR_WORDS", f"{key} contains words", val, "medium")

# ==============================================================================
# PHASE 2: SPECIAL COORDINATES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 2: SPECIAL COORDINATE ANALYSIS")
print("=" * 80)

# Fibonacci positions
fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
fib_values = []
print("\n  Fibonacci coordinates:")
for i, f in enumerate(fibs):
    if f < 128:
        for j, g in enumerate(fibs):
            if g < 128:
                val = int(matrix[f, g])
                fib_values.append((f, g, val))
                if val != 0 and (97 <= abs(val) <= 122 or 65 <= abs(val) <= 90):
                    print(f"    ({f},{g}) = {val} = '{chr(abs(val))}'")

add_finding("FIBONACCI", "Fibonacci coordinate values", fib_values[:20], "exploratory")

# Prime positions
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]
prime_values = []
print("\n  Prime number coordinates:")
prime_chars = ""
for p in primes:
    if p < 128:
        val = int(matrix[p, p])  # Diagonal
        prime_values.append((p, val))
        if 32 <= abs(val) <= 126:
            prime_chars += chr(abs(val))

print(f"    Prime diagonal: {prime_chars}")
add_finding("PRIMES", "Prime diagonal values", {"chars": prime_chars, "values": prime_values}, "exploratory")

# Powers of 2
powers_of_2 = [1, 2, 4, 8, 16, 32, 64]
print("\n  Powers of 2 coordinates:")
pow2_chars = ""
for p in powers_of_2:
    val = int(matrix[p, p])
    if 32 <= abs(val) <= 126:
        pow2_chars += chr(abs(val))
print(f"    Powers of 2 diagonal: {pow2_chars}")
add_finding("POWERS_OF_2", "Power of 2 diagonal", pow2_chars, "exploratory")

# 42 - The Answer
print("\n  Position 42 (The Answer):")
row42 = ''.join(chr(abs(int(matrix[42, c]))) for c in range(128) if 32 <= abs(int(matrix[42, c])) <= 126)
col42 = ''.join(chr(abs(int(matrix[r, 42]))) for r in range(128) if 32 <= abs(int(matrix[r, 42])) <= 126)
print(f"    Row 42: {row42[:60]}...")
print(f"    Col 42: {col42[:60]}...")
add_finding("ANSWER_42", "Position 42 analysis", {"row": row42, "col": col42}, "thematic")

# ==============================================================================
# PHASE 3: BINARY PATTERNS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3: BINARY/HEX PATTERN ANALYSIS")
print("=" * 80)

# Convert matrix to binary
print("\n  Analyzing sign bits...")
sign_matrix = (matrix > 0).astype(int)

# Check for ASCII in sign bits (8 cols = 1 byte)
sign_bytes = []
for r in range(128):
    byte_val = 0
    for c in range(8):
        byte_val = (byte_val << 1) | sign_matrix[r, c]
    sign_bytes.append(byte_val)

sign_ascii = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in sign_bytes)
print(f"  Sign bits as bytes (first 64): {sign_ascii[:64]}")

# Look for magic numbers
print("\n  Searching for magic numbers...")
magic_numbers = {
    0x7F: "DEL/127",
    0x00: "NULL",
    0x89: "PNG",
    0x47: "GIF",
    0x25: "PDF",
    0x50: "PK/ZIP",
    0x42: "B (BTC?)",
    0x51: "Q (Qubic?)",
}

for r in range(128):
    for c in range(120):
        # Read 8 consecutive values as potential byte
        vals = [abs(int(matrix[r, c+i])) for i in range(8)]

        # Check if first byte matches magic
        if vals[0] in magic_numbers:
            context = ''.join(chr(v) if 32 <= v <= 126 else '.' for v in vals)
            if context.count('.') < 4:  # More than half printable
                add_finding("MAGIC_NUMBER", f"{magic_numbers[vals[0]]} at ({r},{c})", context, "low")

# ==============================================================================
# PHASE 4: HIDDEN MESSAGE EXTRACTION
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 4: HIDDEN MESSAGE EXTRACTION")
print("=" * 80)

# Method 1: Read diagonals as text
print("\n  Diagonal messages...")
main_diag = ''.join(chr(abs(int(matrix[i, i]))) for i in range(128) if 32 <= abs(int(matrix[i, i])) <= 126)
anti_diag = ''.join(chr(abs(int(matrix[i, 127-i]))) for i in range(128) if 32 <= abs(int(matrix[i, 127-i])) <= 126)

print(f"    Main diagonal: {main_diag[:60]}...")
print(f"    Anti diagonal: {anti_diag[:60]}...")
add_finding("DIAGONAL_MSG", "Diagonal text", {"main": main_diag, "anti": anti_diag}, "medium")

# Method 2: Spiral read
print("\n  Spiral read from center...")
def spiral_read(mat, n):
    result = []
    x, y = n // 2, n // 2
    result.append(int(mat[y, x]))

    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    d = 0
    steps = 1

    while len(result) < n * n:
        for _ in range(2):
            dx, dy = directions[d % 4]
            for _ in range(steps):
                x, y = x + dx, y + dy
                if 0 <= x < n and 0 <= y < n:
                    result.append(int(mat[y, x]))
            d += 1
        steps += 1

    return result[:256]

spiral = spiral_read(matrix, 128)
spiral_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in spiral)
print(f"    Spiral (first 64): {spiral_ascii[:64]}")
add_finding("SPIRAL_MSG", "Spiral read text", spiral_ascii[:128], "exploratory")

# Method 3: Modular reading
print("\n  Modular patterns (every Nth cell)...")
for n in [7, 11, 13, 17, 19, 23, 27, 37, 42, 55]:
    flat = matrix.flatten()
    mod_vals = flat[::n]
    mod_ascii = ''.join(chr(abs(int(v))) if 32 <= abs(int(v)) <= 126 else '' for v in mod_vals)
    if len(mod_ascii) > 10:
        words = re.findall(r'[a-zA-Z]{3,}', mod_ascii)
        if words:
            print(f"    Every {n}th: {words[:5]}")
            add_finding("MODULAR", f"Every {n}th cell", {"words": words, "text": mod_ascii[:50]}, "low")

# ==============================================================================
# PHASE 5: COMPLETE WORD SEARCH
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 5: COMPLETE WORD SEARCH")
print("=" * 80)

# Known significant words to search
search_words = [
    "SATOSHI", "NAKAMOTO", "BITCOIN", "QUBIC", "AIGARTH", "ANNA",
    "CFB", "SERGEY", "IOTA", "TERNARY", "GENESIS", "BLOCK",
    "SEED", "KEY", "HASH", "MERKLE", "NONCE", "MINER",
    "MEG", "GOU", "AIMEG", "IMAGE", "MIRROR", "BRIDGE",
    "SECRET", "HIDDEN", "FIND", "HERE", "LOOK", "ANSWER",
    "HELLO", "WORLD", "TEST", "CODE", "DATA", "INFO",
]

# Build full text representations
all_text = ""

# Rows
for r in range(128):
    row_text = ''.join(chr(abs(int(matrix[r, c]))) if 32 <= abs(int(matrix[r, c])) <= 126 else '' for c in range(128))
    all_text += row_text + "|"

# Columns
for c in range(128):
    col_text = ''.join(chr(abs(int(matrix[r, c]))) if 32 <= abs(int(matrix[r, c])) <= 126 else '' for r in range(128))
    all_text += col_text + "|"

# Search
found_words = {}
for word in search_words:
    # Case insensitive
    matches = re.findall(word, all_text, re.IGNORECASE)
    if matches:
        found_words[word] = len(matches)
        print(f"  '{word}' found {len(matches)} times")
        add_finding("WORD_SEARCH", f"'{word}' found", {"count": len(matches)}, "medium" if len(matches) > 1 else "low")

# ==============================================================================
# PHASE 6: XOR TRIPLE COMBINATIONS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 6: XOR TRIPLE COMBINATIONS")
print("=" * 80)

print("\n  Testing strategic row triples...")
# Key rows from previous analysis
key_rows = [15, 112, 7, 120, 6, 121, 12, 115, 42, 63, 64]

for r1, r2, r3 in itertools.combinations(key_rows, 3):
    row1 = np.array([int(matrix[r1, c]) for c in range(128)])
    row2 = np.array([int(matrix[r2, c]) for c in range(128)])
    row3 = np.array([int(matrix[r3, c]) for c in range(128)])

    triple_xor = row1 ^ row2 ^ row3

    ascii_str = ''.join(chr(abs(x)) for x in triple_xor if 32 <= abs(x) <= 126)
    words = re.findall(r'[a-zA-Z]{4,}', ascii_str)

    if words:
        key = f"Row{r1}⊕{r2}⊕{r3}"
        print(f"  {key}: {words[:3]}")
        add_finding("TRIPLE_XOR", key, {"words": words, "text": ascii_str[:50]}, "medium")

# ==============================================================================
# PHASE 7: STATISTICAL ANOMALIES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 7: STATISTICAL ANOMALY DETECTION")
print("=" * 80)

# Value distribution
print("\n  Value distribution analysis...")
flat = matrix.flatten()
value_counts = Counter(flat)

# Most common values
most_common = value_counts.most_common(10)
print(f"  Most common values: {most_common}")

# Least common values
least_common = value_counts.most_common()[-10:]
print(f"  Rarest values: {least_common}")

# Check for special values
special_values = [0, 1, -1, 42, 127, -128, 69, 73, 77]  # O, A, -1, *, DEL, min, E, I, M
for sv in special_values:
    count = value_counts.get(sv, 0)
    if count > 0:
        positions = [(r, c) for r in range(128) for c in range(128) if matrix[r, c] == sv]
        print(f"  Value {sv}: {count} occurrences")
        if count < 50:
            add_finding("SPECIAL_VALUE", f"Value {sv} positions", {"count": count, "positions": positions[:10]}, "low")

# Row entropy
print("\n  Row entropy analysis...")
row_entropies = []
for r in range(128):
    row = matrix[r, :]
    counts = Counter(row)
    entropy = -sum((c/128) * np.log2(c/128) for c in counts.values() if c > 0)
    row_entropies.append((r, entropy))

row_entropies.sort(key=lambda x: x[1])
print(f"  Lowest entropy rows: {row_entropies[:5]}")
print(f"  Highest entropy rows: {row_entropies[-5:]}")
add_finding("ENTROPY", "Row entropy extremes", {"lowest": row_entropies[:5], "highest": row_entropies[-5:]}, "medium")

# ==============================================================================
# PHASE 8: 55-CHAR SEED EXTRACTION (ALL METHODS)
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 8: EXHAUSTIVE 55-CHAR SEED EXTRACTION")
print("=" * 80)

all_seeds = []

# Method 1: Symmetric row XOR pairs
print("\n  Symmetric row XOR pairs...")
for r in range(64):
    partner = 127 - r
    row_r = np.array([int(matrix[r, c]) for c in range(128)])
    row_p = np.array([int(matrix[partner, c]) for c in range(128)])
    xor = row_r ^ row_p

    # Extract lowercase
    lowercase = ''.join(chr(abs(x)) for x in xor if 97 <= abs(x) <= 122)
    if len(lowercase) >= 55:
        all_seeds.append(("Row_XOR_" + str(r), lowercase[:55]))

# Method 2: Symmetric column XOR pairs
print("  Symmetric column XOR pairs...")
for c in range(64):
    partner = 127 - c
    col_c = np.array([int(matrix[r, c]) for r in range(128)])
    col_p = np.array([int(matrix[r, partner]) for r in range(128)])
    xor = col_c ^ col_p

    lowercase = ''.join(chr(abs(x)) for x in xor if 97 <= abs(x) <= 122)
    if len(lowercase) >= 55:
        all_seeds.append(("Col_XOR_" + str(c), lowercase[:55]))

# Method 3: Diagonal pairs
print("  Diagonal extractions...")
for offset in range(-73, 74):
    diag = []
    for i in range(128):
        c = i + offset
        if 0 <= c < 128:
            diag.append(int(matrix[i, c]))

    lowercase = ''.join(chr(abs(x)) for x in diag if 97 <= abs(x) <= 122)
    if len(lowercase) >= 55:
        all_seeds.append(("Diag_" + str(offset), lowercase[:55]))

# Method 4: Mod 26 conversions
print("  Mod 26 conversions...")
for r in range(128):
    row = [int(matrix[r, c]) for c in range(128)]
    seed = ''.join(chr((abs(v) % 26) + ord('a')) for v in row[:55])
    all_seeds.append(("Row_mod26_" + str(r), seed))

# Deduplicate
unique_seeds = {}
for name, seed in all_seeds:
    if seed not in unique_seeds:
        unique_seeds[seed] = name

print(f"\n  Total unique seeds extracted: {len(unique_seeds)}")

# Entropy analysis
def seed_entropy(s):
    freq = Counter(s)
    return -sum((c/len(s)) * np.log2(c/len(s)) for c in freq.values())

seed_entropies = [(name, seed, seed_entropy(seed)) for seed, name in unique_seeds.items()]
seed_entropies.sort(key=lambda x: x[2])

print("\n  LOWEST ENTROPY SEEDS (potentially encoded data):")
for name, seed, ent in seed_entropies[:10]:
    print(f"    {ent:.2f} bits: {seed[:40]}... ({name})")
    add_finding("LOW_ENTROPY_SEED", name, {"seed": seed, "entropy": ent}, "high")

# ==============================================================================
# PHASE 9: PALINDROME DEEP SCAN
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 9: COMPLETE PALINDROME SCAN")
print("=" * 80)

all_palindromes = []

# Check all row XOR pairs for palindromes
for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]

    # Get alphabetic characters
    alpha = ''.join(chr(abs(x)) for x in xor if chr(abs(x)).isalpha())

    # Find palindromic substrings
    for length in range(6, min(len(alpha), 50)):
        for start in range(len(alpha) - length + 1):
            sub = alpha[start:start+length]
            if sub.lower() == sub.lower()[::-1]:
                all_palindromes.append({
                    "source": f"Row{r}⊕{partner}",
                    "palindrome": sub,
                    "length": length
                })

# Deduplicate
unique_palindromes = {}
for p in all_palindromes:
    key = p["palindrome"].lower()
    if key not in unique_palindromes or len(p["palindrome"]) > len(unique_palindromes[key]["palindrome"]):
        unique_palindromes[key] = p

print(f"\n  Unique palindromes found: {len(unique_palindromes)}")

# Sort by length
sorted_palindromes = sorted(unique_palindromes.values(), key=lambda x: x["length"], reverse=True)
print("\n  Longest palindromes:")
for p in sorted_palindromes[:10]:
    print(f"    {p['length']} chars: '{p['palindrome']}' ({p['source']})")
    add_finding("PALINDROME", p["source"], p, "high")

# ==============================================================================
# PHASE 10: COORDINATE PATTERNS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 10: COORDINATE PATTERN ANALYSIS")
print("=" * 80)

# Check (r, c) where r + c = 127
print("\n  Sum=127 diagonal analysis...")
sum127_vals = [int(matrix[r, 127-r]) for r in range(128)]
sum127_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in sum127_vals)
print(f"    Text: {sum127_ascii[:60]}...")
add_finding("SUM_127", "r+c=127 diagonal", sum127_ascii, "medium")

# Check r = c (main diagonal)
print("\n  Main diagonal (r=c)...")
main_diag_vals = [int(matrix[r, r]) for r in range(128)]
main_diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in main_diag_vals)
print(f"    Text: {main_diag_ascii[:60]}...")

# Positions where value equals coordinate
print("\n  Cells where value = row or col index...")
coord_matches = []
for r in range(128):
    for c in range(128):
        val = int(matrix[r, c])
        if abs(val) == r or abs(val) == c or abs(val) == r + c or abs(val) == abs(r - c):
            coord_matches.append((r, c, val))

print(f"    Found {len(coord_matches)} coordinate-value matches")
add_finding("COORD_MATCH", "Value=coordinate cells", coord_matches[:20], "low")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("G O D   M O D E   C O M P L E T E")
print("=" * 80)

# Count findings by category
category_counts = Counter(f["category"] for f in discoveries["findings"])
high_sig = [f for f in discoveries["findings"] if f["significance"] == "high"]
medium_sig = [f for f in discoveries["findings"] if f["significance"] == "medium"]

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         G O D   M O D E   R E S U L T S                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  TOTAL FINDINGS: {len(discoveries["findings"]):5}                                                    ║
║                                                                               ║
║  BY SIGNIFICANCE:                                                             ║
║    HIGH:   {len(high_sig):4}                                                              ║
║    MEDIUM: {len(medium_sig):4}                                                              ║
║    OTHER:  {len(discoveries["findings"]) - len(high_sig) - len(medium_sig):4}                                                              ║
║                                                                               ║
║  BY CATEGORY:                                                                 ║""")

for cat, count in category_counts.most_common(10):
    print(f"║    {cat:<20}: {count:4}                                            ║")

print(f"""║                                                                               ║
║  UNIQUE SEEDS EXTRACTED: {len(unique_seeds):4}                                               ║
║  PALINDROMES FOUND: {len(unique_palindromes):4}                                                    ║
║  ROW XOR PAIRS WITH WORDS: {len(row_xor_words):4}                                             ║
║  COL XOR PAIRS WITH WORDS: {len(col_xor_words):4}                                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
output_path = script_dir / "GOD_MODE_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(discoveries, f, indent=2, default=str)

print(f"✓ Full results saved to: {output_path.name}")

# Save seeds separately
seeds_path = script_dir / "GOD_MODE_ALL_SEEDS.json"
seed_data = {
    "timestamp": datetime.now().isoformat(),
    "total_seeds": len(unique_seeds),
    "seeds": [{"name": name, "seed": seed, "entropy": seed_entropy(seed)}
              for seed, name in unique_seeds.items()]
}
with open(seeds_path, "w") as f:
    json.dump(seed_data, f, indent=2)

print(f"✓ All seeds saved to: {seeds_path.name}")

# Print most significant findings
print("\n" + "=" * 80)
print("TOP HIGH-SIGNIFICANCE FINDINGS:")
print("=" * 80)
for f in high_sig[:15]:
    print(f"\n  [{f['category']}] {f['description']}")
    if isinstance(f['data'], dict):
        for k, v in list(f['data'].items())[:3]:
            print(f"    {k}: {str(v)[:60]}")
    else:
        print(f"    Data: {str(f['data'])[:80]}")

print("\n" + "=" * 80)
print("GOD MODE ANALYSIS COMPLETE")
print("=" * 80)
