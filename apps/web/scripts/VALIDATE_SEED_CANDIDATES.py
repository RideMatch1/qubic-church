#!/usr/bin/env python3
"""
===============================================================================
            VALIDATE SEED CANDIDATES
===============================================================================
Test the discovered 55-char sequences as potential Qubic seeds.
Derive Qubic IDs if possible.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import hashlib

script_dir = Path(__file__).parent

print("=" * 80)
print("           VALIDATE SEED CANDIDATES")
print("           Testing 55-char sequences as Qubic seeds")
print("=" * 80)

# The key candidates
candidates = {
    "Row15_XOR_112_direct": "kmiaaazmlmjbebpmimieegimieeeimiiifiifiiimieeeimigeeimim",
    "Concatenated_palindromes": "mieteeimkiiifiifiiikmieeteimegkmjiacpccpcaijmkgeeheemlm",
    "Row7_XOR_120_direct": "ctgaeegceaacccgccaaoledduhwqkucwwgcgaeegkmjiacpccpcaijm",
}

# ==============================================================================
# VALIDATE FORMAT
# ==============================================================================
print("\n" + "=" * 80)
print("FORMAT VALIDATION")
print("=" * 80)

for name, seed in candidates.items():
    print(f"\n  {name}:")
    print(f"    Seed: '{seed}'")
    print(f"    Length: {len(seed)}")
    print(f"    All lowercase: {seed.islower()}")
    print(f"    All alpha: {seed.isalpha()}")
    print(f"    Valid Qubic format: {len(seed) == 55 and seed.islower() and seed.isalpha()}")

# ==============================================================================
# ANALYZE SEED STRUCTURE
# ==============================================================================
print("\n" + "=" * 80)
print("SEED STRUCTURE ANALYSIS")
print("=" * 80)

for name, seed in candidates.items():
    print(f"\n  {name}:")

    # Character frequency
    freq = {}
    for c in seed:
        freq[c] = freq.get(c, 0) + 1

    # Entropy calculation
    entropy = 0
    for count in freq.values():
        p = count / len(seed)
        entropy -= p * np.log2(p) if p > 0 else 0

    print(f"    Unique chars: {len(freq)}")
    print(f"    Entropy: {entropy:.2f} bits")
    print(f"    Max possible entropy: {np.log2(26):.2f} bits")
    print(f"    Entropy ratio: {entropy / np.log2(26) * 100:.1f}%")

    # Most common chars
    top_chars = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"    Top 5 chars: {top_chars}")

    # Check for patterns
    # Repeated substrings
    for length in [3, 4, 5]:
        patterns = {}
        for i in range(len(seed) - length + 1):
            p = seed[i:i+length]
            patterns[p] = patterns.get(p, 0) + 1
        repeats = {k: v for k, v in patterns.items() if v > 1}
        if repeats:
            print(f"    Repeated {length}-grams: {len(repeats)}")

# ==============================================================================
# TRY TO DERIVE QUBIC ID
# ==============================================================================
print("\n" + "=" * 80)
print("QUBIC ID DERIVATION ATTEMPT")
print("=" * 80)

# Qubic uses K12 hash for ID derivation
# We'll compute various hashes as approximation

for name, seed in candidates.items():
    print(f"\n  {name}:")

    # SHA256 of seed
    sha256 = hashlib.sha256(seed.encode()).hexdigest()
    print(f"    SHA256: {sha256[:32]}...")

    # SHA3-256
    sha3 = hashlib.sha3_256(seed.encode()).hexdigest()
    print(f"    SHA3-256: {sha3[:32]}...")

    # BLAKE2b
    blake2 = hashlib.blake2b(seed.encode(), digest_size=32).hexdigest()
    print(f"    BLAKE2b: {blake2[:32]}...")

# ==============================================================================
# CHECK IF SEEDS ARE RELATED
# ==============================================================================
print("\n" + "=" * 80)
print("SEED RELATIONSHIP ANALYSIS")
print("=" * 80)

seed_list = list(candidates.values())

# Check for common substrings
def longest_common_substring(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    longest = 0
    end_pos = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > longest:
                    longest = dp[i][j]
                    end_pos = i
    return s1[end_pos - longest:end_pos]

print("\n  Longest common substrings:")
for i, (n1, s1) in enumerate(candidates.items()):
    for n2, s2 in list(candidates.items())[i+1:]:
        lcs = longest_common_substring(s1, s2)
        print(f"    {n1[:15]} ∩ {n2[:15]}: '{lcs}' ({len(lcs)} chars)")

# ==============================================================================
# EXTRACT MORE CANDIDATES FROM XOR
# ==============================================================================
print("\n" + "=" * 80)
print("ADDITIONAL XOR-BASED CANDIDATES")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Find all row pairs that produce 55+ lowercase chars via XOR
print("\n  Searching for 55-char XOR sequences...")

found_55 = []

for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]

    # Extract lowercase only
    lowercase = ''.join(chr(abs(x)) for x in xor if 97 <= abs(x) <= 122)

    if len(lowercase) >= 55:
        found_55.append({
            "pair": f"{r}↔{partner}",
            "sequence": lowercase[:55],
            "total_length": len(lowercase),
        })

print(f"\n  Row pairs with 55+ lowercase XOR chars: {len(found_55)}")
for item in found_55:
    print(f"    {item['pair']}: '{item['sequence'][:40]}...' ({item['total_length']} total)")

# Same for columns
col_55 = []
for c in range(64):
    partner = 127 - c
    col_c = [int(matrix[r, c]) for r in range(128)]
    col_p = [int(matrix[r, partner]) for r in range(128)]
    xor = [col_c[r] ^ col_p[r] for r in range(128)]

    lowercase = ''.join(chr(abs(x)) for x in xor if 97 <= abs(x) <= 122)

    if len(lowercase) >= 55:
        col_55.append({
            "pair": f"{c}↔{partner}",
            "sequence": lowercase[:55],
            "total_length": len(lowercase),
        })

print(f"\n  Column pairs with 55+ lowercase XOR chars: {len(col_55)}")
for item in col_55:
    print(f"    {item['pair']}: '{item['sequence'][:40]}...' ({item['total_length']} total)")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)

all_valid_seeds = []
for name, seed in candidates.items():
    if len(seed) == 55 and seed.islower() and seed.isalpha():
        all_valid_seeds.append((name, seed))

for item in found_55:
    all_valid_seeds.append((f"Row_{item['pair']}", item['sequence']))

for item in col_55:
    all_valid_seeds.append((f"Col_{item['pair']}", item['sequence']))

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         SEED VALIDATION SUMMARY                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  VALID 55-CHAR SEEDS FOUND:                                                   ║
║  • From key candidates: {len([s for n,s in candidates.items() if len(s)==55 and s.islower()])}                                               ║
║  • From row XOR: {len(found_55)}                                                       ║
║  • From column XOR: {len(col_55)}                                                     ║
║  • TOTAL: {len(all_valid_seeds)}                                                          ║
║                                                                               ║
║  PRIMARY CANDIDATE:                                                           ║
║  '{candidates.get("Row15_XOR_112_direct", "N/A")[:50]}...'  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "primary_candidates": candidates,
    "row_xor_55": found_55,
    "col_xor_55": col_55,
    "total_valid_seeds": len(all_valid_seeds),
    "all_seeds": all_valid_seeds[:20],
}

with open(script_dir / "SEED_VALIDATION_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved")
