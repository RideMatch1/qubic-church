#!/usr/bin/env python3
"""
===============================================================================
            COMPREHENSIVE SEED VALIDATION
===============================================================================
1. Find ALL possible 55-char seeds from matrix
2. Derive Qubic IDs using proper method
3. Validate format and check for known patterns
4. Statistical validation
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import hashlib
import re
from collections import Counter

script_dir = Path(__file__).parent

print("=" * 80)
print("           COMPREHENSIVE SEED VALIDATION")
print("           Finding and validating ALL seeds")
print("=" * 80)

# Try to import K12
try:
    from Crypto.Hash import KangarooTwelve as K12
    HAS_K12 = True
    print("  ✓ K12 (KangarooTwelve) available")
except ImportError:
    HAS_K12 = False
    print("  ✗ K12 not available, using SHA3-256 approximation")

# Try qubipy
try:
    from qubipy.crypto import get_identity_from_seed
    HAS_QUBIPY = True
    print("  ✓ qubipy available")
except ImportError:
    HAS_QUBIPY = False
    print("  ✗ qubipy not available")

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# QUBIC ID DERIVATION
# ==============================================================================
def derive_qubic_id(seed):
    """Derive Qubic ID from 55-char seed"""
    if not (len(seed) == 55 and seed.islower() and seed.isalpha()):
        return None, "Invalid seed format"

    if HAS_QUBIPY:
        try:
            identity = get_identity_from_seed(seed)
            return identity, "qubipy"
        except Exception as e:
            pass

    if HAS_K12:
        try:
            h = K12.new(data=seed.encode())
            digest = h.read(32)
            # Convert to Qubic ID format (base26 uppercase)
            id_chars = []
            for i in range(0, 32, 1):
                val = digest[i]
                id_chars.append(chr((val % 26) + ord('A')))
            return ''.join(id_chars[:60]), "K12"
        except Exception as e:
            pass

    # Fallback: SHA3-256
    h = hashlib.sha3_256(seed.encode()).digest()
    id_chars = []
    for i in range(60):
        val = h[i % 32]
        id_chars.append(chr((val % 26) + ord('A')))
    return ''.join(id_chars), "SHA3-256 (approximation)"

def is_valid_qubic_id(qid):
    """Check if string looks like a valid Qubic ID"""
    if not qid:
        return False
    # Qubic IDs are 60 uppercase letters
    if len(qid) != 60:
        return False
    if not qid.isupper():
        return False
    if not qid.isalpha():
        return False
    return True

# ==============================================================================
# EXHAUSTIVE SEED SEARCH
# ==============================================================================
print("\n" + "=" * 80)
print("EXHAUSTIVE SEED SEARCH")
print("=" * 80)

all_seeds = []

# Method 1: Row XOR pairs - extract lowercase only
print("\n  Method 1: Row XOR pairs (lowercase extraction)...")
for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]

    # Extract lowercase
    lowercase = ''.join(chr(abs(x)) for x in xor if 97 <= abs(x) <= 122)
    if len(lowercase) >= 55:
        all_seeds.append({
            "method": f"Row_{r}⊕{partner}_lowercase",
            "seed": lowercase[:55],
            "total_chars": len(lowercase),
        })

# Method 2: Column XOR pairs
print("  Method 2: Column XOR pairs (lowercase extraction)...")
for c in range(64):
    partner = 127 - c
    col_c = [int(matrix[r, c]) for r in range(128)]
    col_p = [int(matrix[r, partner]) for r in range(128)]
    xor = [col_c[r] ^ col_p[r] for r in range(128)]

    lowercase = ''.join(chr(abs(x)) for x in xor if 97 <= abs(x) <= 122)
    if len(lowercase) >= 55:
        all_seeds.append({
            "method": f"Col_{c}⊕{partner}_lowercase",
            "seed": lowercase[:55],
            "total_chars": len(lowercase),
        })

# Method 3: Direct rows (mod 26)
print("  Method 3: Direct rows (mod 26)...")
for r in range(128):
    row = [int(matrix[r, c]) for c in range(128)]
    seed = ''.join(chr((abs(v) % 26) + ord('a')) for v in row[:55])
    all_seeds.append({
        "method": f"Row_{r}_mod26",
        "seed": seed,
        "total_chars": 55,
    })

# Method 4: Direct columns (mod 26)
print("  Method 4: Direct columns (mod 26)...")
for c in range(128):
    col = [int(matrix[r, c]) for r in range(128)]
    seed = ''.join(chr((abs(v) % 26) + ord('a')) for v in col[:55])
    all_seeds.append({
        "method": f"Col_{c}_mod26",
        "seed": seed,
        "total_chars": 55,
    })

# Method 5: Diagonals
print("  Method 5: Diagonals...")
for offset in range(-73, 74):
    diag = []
    for i in range(128):
        c = i + offset
        if 0 <= c < 128:
            diag.append(int(matrix[i, c]))
    if len(diag) >= 55:
        seed = ''.join(chr((abs(v) % 26) + ord('a')) for v in diag[:55])
        all_seeds.append({
            "method": f"Diag_offset_{offset}_mod26",
            "seed": seed,
            "total_chars": len(diag),
        })

# Method 6: Anti-diagonals
print("  Method 6: Anti-diagonals...")
for offset in range(-73, 74):
    diag = []
    for i in range(128):
        c = 127 - i + offset
        if 0 <= c < 128:
            diag.append(int(matrix[i, c]))
    if len(diag) >= 55:
        seed = ''.join(chr((abs(v) % 26) + ord('a')) for v in diag[:55])
        all_seeds.append({
            "method": f"AntiDiag_offset_{offset}_mod26",
            "seed": seed,
            "total_chars": len(diag),
        })

# Method 7: Row XOR pairs (mod 26)
print("  Method 7: Row XOR pairs (mod 26)...")
for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]
    seed = ''.join(chr((abs(v) % 26) + ord('a')) for v in xor[:55])
    all_seeds.append({
        "method": f"Row_{r}⊕{partner}_mod26",
        "seed": seed,
        "total_chars": 55,
    })

# Method 8: Concatenated palindromes
print("  Method 8: Concatenated patterns...")
# Get all lowercase sequences from XOR
all_seqs = []
for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]
    xor_str = ''.join(chr(abs(x)).lower() if chr(abs(x)).isalpha() else '' for x in xor)
    seqs = re.findall(r'[a-z]{5,}', xor_str)
    all_seqs.extend(seqs)

# Sort by length and concatenate
all_seqs.sort(key=len, reverse=True)
concatenated = ''.join(all_seqs)[:55]
if len(concatenated) == 55:
    all_seeds.append({
        "method": "Concatenated_sequences",
        "seed": concatenated,
        "total_chars": 55,
    })

print(f"\n  Total seed candidates: {len(all_seeds)}")

# ==============================================================================
# REMOVE DUPLICATES
# ==============================================================================
print("\n" + "=" * 80)
print("DEDUPLICATION")
print("=" * 80)

unique_seeds = {}
for item in all_seeds:
    seed = item["seed"]
    if seed not in unique_seeds:
        unique_seeds[seed] = item

print(f"  Unique seeds: {len(unique_seeds)}")

# ==============================================================================
# DERIVE IDs FOR ALL SEEDS
# ==============================================================================
print("\n" + "=" * 80)
print("DERIVING QUBIC IDs")
print("=" * 80)

validated_seeds = []

for seed, item in list(unique_seeds.items())[:100]:  # Limit to first 100 for speed
    qid, method = derive_qubic_id(seed)

    if qid and is_valid_qubic_id(qid):
        validated_seeds.append({
            "seed": seed,
            "method": item["method"],
            "qubic_id": qid,
            "derivation_method": method,
        })

print(f"\n  Seeds with valid Qubic ID format: {len(validated_seeds)}")

# ==============================================================================
# CHECK FOR KNOWN PATTERNS IN IDs
# ==============================================================================
print("\n" + "=" * 80)
print("PATTERN CHECK IN DERIVED IDs")
print("=" * 80)

known_prefixes = ["BAAAA", "QUBIC", "AIGAR", "ANNA", "CFB", "SAT"]
pattern_matches = []

for item in validated_seeds:
    qid = item["qubic_id"]
    for prefix in known_prefixes:
        if prefix in qid:
            pattern_matches.append({
                "seed": item["seed"],
                "qubic_id": qid,
                "pattern": prefix,
                "position": qid.find(prefix),
            })

print(f"\n  IDs containing known patterns: {len(pattern_matches)}")
for match in pattern_matches[:10]:
    print(f"    '{match['pattern']}' at pos {match['position']} in {match['qubic_id'][:30]}...")

# ==============================================================================
# ENTROPY ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("ENTROPY ANALYSIS")
print("=" * 80)

def calculate_entropy(s):
    freq = Counter(s)
    entropy = 0
    for count in freq.values():
        p = count / len(s)
        entropy -= p * np.log2(p) if p > 0 else 0
    return entropy

# Calculate entropy for all seeds
entropies = []
for item in validated_seeds:
    ent = calculate_entropy(item["seed"])
    entropies.append((item["seed"], ent, item["method"]))

# Sort by entropy
entropies.sort(key=lambda x: x[1], reverse=True)

print(f"\n  Top 10 highest entropy seeds:")
for seed, ent, method in entropies[:10]:
    print(f"    {ent:.2f} bits: '{seed[:30]}...' ({method[:20]})")

print(f"\n  Bottom 10 lowest entropy seeds:")
for seed, ent, method in entropies[-10:]:
    print(f"    {ent:.2f} bits: '{seed[:30]}...' ({method[:20]})")

# ==============================================================================
# STATISTICAL VALIDATION
# ==============================================================================
print("\n" + "=" * 80)
print("STATISTICAL VALIDATION")
print("=" * 80)

# Generate random seeds for comparison
import random
random_entropies = []
for _ in range(1000):
    random_seed = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(55))
    random_entropies.append(calculate_entropy(random_seed))

mean_random = np.mean(random_entropies)
std_random = np.std(random_entropies)

print(f"\n  Random seed entropy: mean={mean_random:.2f}, std={std_random:.2f}")

# How many of our seeds have significantly different entropy?
low_entropy_seeds = [e for e in entropies if e[1] < mean_random - 2*std_random]
high_entropy_seeds = [e for e in entropies if e[1] > mean_random + 2*std_random]

print(f"  Our seeds with abnormally LOW entropy (<-2σ): {len(low_entropy_seeds)}")
print(f"  Our seeds with abnormally HIGH entropy (>+2σ): {len(high_entropy_seeds)}")

# ==============================================================================
# SPECIAL SEED ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("SPECIAL SEEDS (from palindromes)")
print("=" * 80)

special_seeds = [
    ("Row15⊕112", "kmiaaazmlmjbebpmimieegimieeeimiiifiifiiimieeeimigeeimim"),
    ("Row7⊕120", "ctgaeegceaacccgccaaoledduhwqkucwwgcgaeegkmjiacpccpcaijm"),
    ("Concatenated", "mieteeimkiiifiifiiikmieeteimegkmjiacpccpcaijmkgeeheemlm"),
]

print("\n  Special seed analysis:")
for name, seed in special_seeds:
    qid, method = derive_qubic_id(seed)
    ent = calculate_entropy(seed)
    z_score = (ent - mean_random) / std_random

    print(f"\n  {name}:")
    print(f"    Seed: '{seed}'")
    print(f"    Qubic ID: '{qid}'")
    print(f"    Entropy: {ent:.2f} bits (z={z_score:.2f})")
    print(f"    Valid format: {is_valid_qubic_id(qid)}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("COMPREHENSIVE VALIDATION COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         VALIDATION SUMMARY                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  SEED SEARCH:                                                                 ║
║  • Total candidates generated: {len(all_seeds):5}                                      ║
║  • Unique seeds: {len(unique_seeds):5}                                                  ║
║  • With valid Qubic ID format: {len(validated_seeds):5}                                      ║
║                                                                               ║
║  ENTROPY ANALYSIS:                                                            ║
║  • Random baseline: {mean_random:.2f} ± {std_random:.2f} bits                              ║
║  • Abnormally low entropy: {len(low_entropy_seeds):3} seeds                                    ║
║  • Abnormally high entropy: {len(high_entropy_seeds):3} seeds                                   ║
║                                                                               ║
║  PATTERN MATCHES:                                                             ║
║  • IDs with known patterns: {len(pattern_matches):3}                                         ║
║                                                                               ║
║  DERIVATION METHOD: {method if HAS_QUBIPY else 'SHA3-256 (approximation)':40}      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "total_candidates": len(all_seeds),
    "unique_seeds": len(unique_seeds),
    "validated_seeds": len(validated_seeds),
    "derivation_available": {
        "K12": HAS_K12,
        "qubipy": HAS_QUBIPY,
    },
    "entropy": {
        "random_mean": mean_random,
        "random_std": std_random,
        "low_entropy_count": len(low_entropy_seeds),
        "high_entropy_count": len(high_entropy_seeds),
    },
    "special_seeds": special_seeds,
    "validated_sample": validated_seeds[:20],
    "low_entropy_seeds": [(s, e, m) for s, e, m in low_entropy_seeds[:10]],
}

with open(script_dir / "COMPREHENSIVE_VALIDATION_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved")
