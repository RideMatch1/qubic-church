#!/usr/bin/env python3
"""
===============================================================================
        GOD MODE PHASE 3: EVEN DEEPER
===============================================================================
Push the boundaries. Find what we missed.

1. Decode the 106-char palindrome
2. Find hidden messages in the 'm' patterns
3. Analyze the "center" of each palindrome
4. XOR palindromes together
5. Binary interpretation of palindromes
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
import hashlib

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗  ██████╗ ██████╗     ███╗   ███╗ ██████╗ ██████╗ ███████╗
  ██╔════╝ ██╔═══██╗██╔══██╗    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝
  ██║  ███╗██║   ██║██║  ██║    ██╔████╔██║██║   ██║██║  ██║█████╗
  ██║   ██║██║   ██║██║  ██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝
  ╚██████╔╝╚██████╔╝██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
   ╚═════╝  ╚═════╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
                       PHASE 3: DEEPER
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# The key palindromes
palindromes = [
    ("13↔114", "EHEEMMMMMjMEEYEMMMEEIEMNbMNfEmonMMMmEEeMXMmEuEeMmmMmmmmMmmMeEuEmMXMeEEmMMMnomEfNMbNMEIEEMMMEYEEMjMMMMMEEHE"),
    ("5↔122", "EhEEMlMMMMpMEEtEOMMEEEMPMNlcfUpmUcUgMhMmEEeMmmMmmmmMmmMeEEmMhMgUcUmpUfclNMPMEEEMMOEtEEMpMMMMlMEEhE"),
    ("7↔120", "ctgaeegceaacccgccaaoledduhwqkucwwgcgaeegkmjiacpccpcaijmkgeeagcgwwcukqwhuddeloaaccgcccaaecgeeagtc"),
    ("12↔115", "pVvgeeeeaempzEeffuqhukuaueuugeeeeeemmmeeneeneemmmeeeeeeguueuaukuhquffeEzpmeaeeeegvVp"),
    ("15↔112", "DkmFiaaazmlmjbebpmimieegimieTeeimKiiifiifiiiKmieeTeimigeeimimpbebjmlmzaaaiFmkD"),
]

# ==============================================================================
# PHASE 3.1: DECODE THE CENTER
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.1: PALINDROME CENTERS")
print("=" * 80)

print("\n  Every palindrome has a CENTER character(s):")

for name, pal in palindromes:
    length = len(pal)
    if length % 2 == 1:
        center = pal[length // 2]
        print(f"\n  {name} ({length} chars):")
        print(f"    Center char: '{center}' (ASCII {ord(center)})")
    else:
        c1 = pal[length // 2 - 1]
        c2 = pal[length // 2]
        print(f"\n  {name} ({length} chars):")
        print(f"    Center chars: '{c1}{c2}' (ASCII {ord(c1)}, {ord(c2)})")

# Extract all center characters
centers = []
for name, pal in palindromes:
    length = len(pal)
    if length % 2 == 1:
        centers.append(pal[length // 2])
    else:
        centers.append(pal[length // 2 - 1])
        centers.append(pal[length // 2])

center_str = ''.join(centers)
print(f"\n  All centers combined: '{center_str}'")

# ==============================================================================
# PHASE 3.2: THE 'M' PATTERN
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.2: THE 'M' PATTERN DECODED")
print("=" * 80)

# The 106-char palindrome has 50 'm's
longest = palindromes[0][1]
m_positions = [i for i, c in enumerate(longest) if c.lower() == 'm']

print(f"\n  Longest palindrome: {len(longest)} chars")
print(f"  Number of 'm's: {len(m_positions)}")
print(f"  Positions of 'm': {m_positions[:20]}...")

# Binary encode: m=1, not-m=0
binary_m = ''.join('1' if c.lower() == 'm' else '0' for c in longest)
print(f"\n  Binary (m=1): {binary_m[:50]}...")

# Split into 8-bit chunks
bytes_m = [binary_m[i:i+8] for i in range(0, len(binary_m), 8) if len(binary_m[i:i+8]) == 8]
print(f"  As bytes: {bytes_m[:5]}...")

# Convert to ASCII
ascii_m = ''.join(chr(int(b, 2)) for b in bytes_m if int(b, 2) < 128)
print(f"  As ASCII: {repr(ascii_m)}")

# Try other encodings
# e=1, else=0
binary_e = ''.join('1' if c.lower() == 'e' else '0' for c in longest)
bytes_e = [binary_e[i:i+8] for i in range(0, len(binary_e), 8) if len(binary_e[i:i+8]) == 8]
ascii_e = ''.join(chr(int(b, 2)) for b in bytes_e if 0 < int(b, 2) < 128)
print(f"\n  Binary (e=1): {binary_e[:50]}...")
print(f"  As ASCII: {repr(ascii_e)}")

# ==============================================================================
# PHASE 3.3: XOR PALINDROMES TOGETHER
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.3: XOR PALINDROMES TOGETHER")
print("=" * 80)

# XOR first two palindromes
p1 = palindromes[0][1].lower()
p2 = palindromes[1][1].lower()

min_len = min(len(p1), len(p2))
xor_12 = ''.join(chr(ord(p1[i]) ^ ord(p2[i])) for i in range(min_len))

print(f"\n  P1 (106) XOR P2 (98):")
printable = ''.join(c if 32 <= ord(c) <= 126 else '.' for c in xor_12)
print(f"    Result: {printable[:60]}...")

# Count non-zero
nonzero = sum(1 for c in xor_12 if ord(c) != 0)
print(f"    Non-zero chars: {nonzero}/{min_len}")

# Check for patterns
if xor_12.count('\x00') > 10:
    print(f"    NULL bytes: {xor_12.count(chr(0))} (positions match!)")

# ==============================================================================
# PHASE 3.4: EXTRACT UNIQUE PARTS
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.4: UNIQUE PARTS OF PALINDROMES")
print("=" * 80)

print("\n  Since palindromes are symmetric, only first half is unique:")

for name, pal in palindromes[:5]:
    half = len(pal) // 2
    unique_part = pal[:half]
    print(f"\n  {name}:")
    print(f"    Unique half: '{unique_part}'")
    print(f"    Length: {len(unique_part)} chars")

    # Check if it's a valid seed length
    if len(unique_part) == 55:
        print(f"    ★ EXACTLY 55 CHARS - QUBIC SEED LENGTH!")
    elif 50 <= len(unique_part) <= 60:
        print(f"    Close to Qubic seed length (55)")

# ==============================================================================
# PHASE 3.5: HIDDEN WORDS IN PALINDROMES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.5: HIDDEN WORDS SEARCH")
print("=" * 80)

# Combine all palindromes
all_pals = ''.join(p[1].lower() for p in palindromes)

# Search for meaningful words
words_to_find = [
    "satoshi", "nakamoto", "bitcoin", "qubic", "aigarth", "anna",
    "genesis", "block", "hash", "key", "seed", "iota", "ternary",
    "hello", "world", "secret", "hidden", "find", "look", "here",
    "cfb", "sergey", "come", "back", "future", "time", "money",
    "god", "mode", "meg", "aim", "image", "mirror", "bridge",
    "mom", "dad", "mim", "mem", "mum", "eee", "mmm", "iii",
]

found = []
for word in words_to_find:
    if word in all_pals:
        count = all_pals.count(word)
        found.append((word, count))
        print(f"  '{word}' found {count} times")

# ==============================================================================
# PHASE 3.6: NUMERIC INTERPRETATION
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.6: NUMERIC SECRETS")
print("=" * 80)

longest = palindromes[0][1]

# Convert to numbers (a=0, b=1, ...)
nums = [ord(c.lower()) - ord('a') for c in longest if c.isalpha()]

print(f"\n  Longest palindrome as numbers (a=0):")
print(f"    First 20: {nums[:20]}")
print(f"    Sum: {sum(nums)}")
print(f"    Mean: {np.mean(nums):.2f}")
print(f"    XOR all: {np.bitwise_xor.reduce(nums)}")

# Look for special sums
running_sum = 0
special_positions = []
for i, n in enumerate(nums):
    running_sum += n
    if running_sum in [127, 255, 256, 512, 1024]:
        special_positions.append((i, running_sum))

if special_positions:
    print(f"\n  Special sum positions: {special_positions}")

# ==============================================================================
# PHASE 3.7: HASH THE PALINDROMES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.7: CRYPTOGRAPHIC HASHES")
print("=" * 80)

for name, pal in palindromes[:3]:
    sha256 = hashlib.sha256(pal.encode()).hexdigest()
    sha3 = hashlib.sha3_256(pal.encode()).hexdigest()

    print(f"\n  {name}:")
    print(f"    SHA256: {sha256[:32]}...")
    print(f"    SHA3:   {sha3[:32]}...")

    # Check for patterns in hash
    if '00000' in sha256:
        print(f"    ★ SHA256 contains '00000'!")
    if 'dead' in sha256.lower() or 'beef' in sha256.lower():
        print(f"    ★ SHA256 contains magic bytes!")

# ==============================================================================
# PHASE 3.8: EXTRACT ALL 55-CHAR SEQUENCES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.8: 55-CHAR SEQUENCES FROM PALINDROMES")
print("=" * 80)

seeds_55 = []

for name, pal in palindromes:
    pal_lower = pal.lower()

    # Sliding window of 55
    for i in range(len(pal_lower) - 54):
        window = pal_lower[i:i+55]
        if window.isalpha():
            seeds_55.append({
                "source": name,
                "position": i,
                "seed": window
            })

print(f"\n  Total 55-char sequences found: {len(seeds_55)}")

# Deduplicate
unique_55 = {}
for s in seeds_55:
    if s["seed"] not in unique_55:
        unique_55[s["seed"]] = s

print(f"  Unique 55-char seeds: {len(unique_55)}")

# Show first few
for seed, info in list(unique_55.items())[:5]:
    print(f"\n  From {info['source']} pos {info['position']}:")
    print(f"    '{seed}'")

# ==============================================================================
# PHASE 3.9: THE ROW 13 SECRET
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.9: ROW 13 DEEP ANALYSIS")
print("=" * 80)

# Row 13 produced the longest palindrome
row13 = [int(matrix[13, c]) for c in range(128)]
row114 = [int(matrix[114, c]) for c in range(128)]

print("\n  Row 13 raw values:")
print(f"    First 20: {row13[:20]}")
print(f"    Sum: {sum(row13)}")
print(f"    Mean: {np.mean(row13):.2f}")

print("\n  Row 114 raw values:")
print(f"    First 20: {row114[:20]}")
print(f"    Sum: {sum(row114)}")

print("\n  XOR of rows:")
xor = [row13[i] ^ row114[i] for i in range(128)]
print(f"    First 20: {xor[:20]}")
print(f"    Sum: {sum(xor)}")

# How many produce the 'm' character?
m_count = sum(1 for x in xor if chr(abs(x)).lower() == 'm')
print(f"    Values that decode to 'm': {m_count}")

# ==============================================================================
# PHASE 3.10: 127 EVERYWHERE
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.10: THE NUMBER 127")
print("=" * 80)

# Find all occurrences of 127 in the matrix
count_127 = np.sum(matrix == 127)
count_neg127 = np.sum(matrix == -127)

print(f"\n  Value 127 appears: {count_127} times")
print(f"  Value -127 appears: {count_neg127} times")

# Positions
pos_127 = [(r, c) for r in range(128) for c in range(128) if matrix[r, c] == 127]
print(f"\n  Positions of 127: {pos_127}")

# Check if they form a pattern
if pos_127:
    rows = [p[0] for p in pos_127]
    cols = [p[1] for p in pos_127]
    print(f"    Row sum: {sum(rows)}")
    print(f"    Col sum: {sum(cols)}")

# ==============================================================================
# PHASE 3.11: CONCATENATE UNIQUE HALVES
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3.11: CONCATENATED UNIQUE HALVES")
print("=" * 80)

# Get first half of each palindrome
halves = []
for name, pal in palindromes:
    half = pal[:len(pal)//2].lower()
    halves.append(half)

concatenated = ''.join(halves)
print(f"\n  Concatenated unique halves: {len(concatenated)} chars")
print(f"    First 80: '{concatenated[:80]}'")

# Extract 55-char seed from this
if len(concatenated) >= 55:
    seed_from_concat = concatenated[:55]
    print(f"\n  ★ POTENTIAL SEED (first 55 chars):")
    print(f"    '{seed_from_concat}'")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("PHASE 3 COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PHASE 3 DISCOVERIES                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  PALINDROME CENTERS:                                                          ║
║    Combined: '{center_str}'                                                   ║
║                                                                               ║
║  'M' PATTERN:                                                                 ║
║    50 'm's in longest palindrome                                              ║
║    Binary encoding attempted                                                  ║
║                                                                               ║
║  55-CHAR SEEDS FROM PALINDROMES:                                              ║
║    Total: {len(seeds_55)}                                                              ║
║    Unique: {len(unique_55)}                                                            ║
║                                                                               ║
║  VALUE 127 OCCURRENCES: {count_127}                                                     ║
║                                                                               ║
║  WORDS FOUND: {len(found)}                                                             ║
║    {', '.join(w[0] for w in found[:5])}...                                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "centers": center_str,
    "unique_55_seeds": list(unique_55.keys())[:20],
    "words_found": found,
    "value_127_positions": pos_127,
    "concatenated_seed": seed_from_concat if len(concatenated) >= 55 else None
}

with open(script_dir / "GOD_MODE_PHASE3_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("✓ Results saved to GOD_MODE_PHASE3_RESULTS.json")
