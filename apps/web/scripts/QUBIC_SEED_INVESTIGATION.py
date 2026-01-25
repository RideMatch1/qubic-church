#!/usr/bin/env python3
"""
===============================================================================
            QUBIC SEED INVESTIGATION
===============================================================================
Hypothesis: The palindromes/patterns might be Qubic seed fragments.
Qubic seed format: 55 lowercase letters (a-z only)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import re

script_dir = Path(__file__).parent

print("=" * 80)
print("           QUBIC SEED INVESTIGATION")
print("           Looking for 55-char lowercase sequences")
print("=" * 80)

matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# KNOWN PATTERNS - CHECK FOR LOWERCASE
# ==============================================================================
print("\n" + "=" * 80)
print("CHECKING KNOWN PATTERNS FOR SEED COMPATIBILITY")
print("=" * 80)

known_patterns = [
    ("Row 15↔112", "mieTeeimKiiifiifiiiKmieeTeim", 28),
    ("Row 7↔120", "egkmjiacpccpcaijmkge", 20),
    ("Row 6↔121", "iYkkkkkkYi", 10),
    ("Row 12↔115", "meeneeneem", 10),
    ("Row 19↔108", "xJhhJx", 6),
    ("Row 46↔81", "uQuuQu", 6),
    ("Row 48↔79", "HrllrH", 6),
]

print(f"\n  Pattern analysis:")
for name, pattern, length in known_patterns:
    lowercase_only = pattern.lower()
    is_valid_seed_chars = all(c in 'abcdefghijklmnopqrstuvwxyz' for c in lowercase_only)
    has_uppercase = any(c.isupper() for c in pattern)

    print(f"\n  {name}: '{pattern}'")
    print(f"    Length: {length}")
    print(f"    Lowercase version: '{lowercase_only}'")
    print(f"    Contains uppercase: {has_uppercase}")
    print(f"    Valid seed chars (a-z): {is_valid_seed_chars}")

# ==============================================================================
# SEARCH FOR PURE LOWERCASE SEQUENCES
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING FOR PURE LOWERCASE SEQUENCES (a-z only)")
print("=" * 80)

lowercase_sequences = []

# Search row XOR pairs
for r in range(64):
    partner = 127 - r
    row_r = [int(matrix[r, c]) for c in range(128)]
    row_p = [int(matrix[partner, c]) for c in range(128)]
    xor = [row_r[c] ^ row_p[c] for c in range(128)]

    # Convert to lowercase chars only
    xor_str = ''
    for x in xor:
        ch = chr(abs(x)) if 32 <= abs(x) <= 126 else '.'
        xor_str += ch.lower() if ch.isalpha() else '.'

    # Find lowercase sequences
    for match in re.finditer(r'[a-z]{5,}', xor_str):
        lowercase_sequences.append({
            "type": "row",
            "pair": f"{r}↔{partner}",
            "sequence": match.group(),
            "length": len(match.group()),
            "position": match.start(),
        })

# Search column XOR pairs
for c in range(64):
    partner = 127 - c
    col_c = [int(matrix[r, c]) for r in range(128)]
    col_p = [int(matrix[r, partner]) for r in range(128)]
    xor = [col_c[r] ^ col_p[r] for r in range(128)]

    xor_str = ''
    for x in xor:
        ch = chr(abs(x)) if 32 <= abs(x) <= 126 else '.'
        xor_str += ch.lower() if ch.isalpha() else '.'

    for match in re.finditer(r'[a-z]{5,}', xor_str):
        lowercase_sequences.append({
            "type": "col",
            "pair": f"{c}↔{partner}",
            "sequence": match.group(),
            "length": len(match.group()),
            "position": match.start(),
        })

# Sort by length
lowercase_sequences.sort(key=lambda x: x["length"], reverse=True)

print(f"\n  Found {len(lowercase_sequences)} lowercase sequences (5+ chars):")
for seq in lowercase_sequences[:20]:
    print(f"    {seq['type']:4} {seq['pair']:10}: '{seq['sequence']}' ({seq['length']} chars)")

# ==============================================================================
# TOTAL LOWERCASE CHARS EXTRACTED
# ==============================================================================
print("\n" + "=" * 80)
print("TOTAL LOWERCASE CHARACTERS")
print("=" * 80)

total_chars = sum(seq["length"] for seq in lowercase_sequences)
unique_sequences = list(set(seq["sequence"] for seq in lowercase_sequences))

print(f"\n  Total lowercase chars: {total_chars}")
print(f"  Unique sequences: {len(unique_sequences)}")

# Concatenate longest sequences
concatenated = ''.join(seq["sequence"] for seq in lowercase_sequences[:10])
print(f"\n  Top 10 sequences concatenated ({len(concatenated)} chars):")
print(f"    '{concatenated[:55]}'...")
print(f"    (Need 55 for a seed, have {len(concatenated)})")

# ==============================================================================
# SEARCH FOR 55-CHAR SEQUENCES DIRECTLY
# ==============================================================================
print("\n" + "=" * 80)
print("SEARCHING FOR 55-CHAR SEQUENCES")
print("=" * 80)

long_sequences = [seq for seq in lowercase_sequences if seq["length"] >= 20]
print(f"\n  Sequences with 20+ chars: {len(long_sequences)}")

# Try combining nearby sequences
print(f"\n  Longest individual sequences:")
for seq in lowercase_sequences[:5]:
    print(f"    {seq['sequence']} ({seq['length']} chars)")

# ==============================================================================
# EXTRACT RAW LOWERCASE FROM ENTIRE MATRIX
# ==============================================================================
print("\n" + "=" * 80)
print("RAW MATRIX LOWERCASE EXTRACTION")
print("=" * 80)

# Direct extraction from matrix values
lowercase_from_matrix = []
for r in range(128):
    for c in range(128):
        val = int(matrix[r, c])
        # Lowercase a-z is ASCII 97-122
        if 97 <= abs(val) <= 122:
            ch = chr(abs(val))
            lowercase_from_matrix.append({
                "pos": (r, c),
                "value": val,
                "char": ch,
            })

print(f"\n  Matrix cells with lowercase values (97-122): {len(lowercase_from_matrix)}")

# Group by character
char_counts = {}
for item in lowercase_from_matrix:
    ch = item["char"]
    char_counts[ch] = char_counts.get(ch, 0) + 1

print(f"\n  Character distribution:")
for ch in sorted(char_counts.keys()):
    print(f"    '{ch}': {char_counts[ch]} times")

# ==============================================================================
# TRY SPECIFIC EXTRACTION METHODS
# ==============================================================================
print("\n" + "=" * 80)
print("SEED EXTRACTION ATTEMPTS")
print("=" * 80)

# Method 1: Main diagonal
main_diag = [int(matrix[i, i]) for i in range(128)]
diag_seed = ''.join(chr(abs(v)).lower() if 97 <= abs(v) <= 122 else '' for v in main_diag)
print(f"\n  Method 1 - Main diagonal lowercase: '{diag_seed[:55]}'")
print(f"    Length: {len(diag_seed)}")

# Method 2: Anti-diagonal
anti_diag = [int(matrix[i, 127-i]) for i in range(128)]
anti_seed = ''.join(chr(abs(v)).lower() if 97 <= abs(v) <= 122 else '' for v in anti_diag)
print(f"\n  Method 2 - Anti-diagonal lowercase: '{anti_seed[:55]}'")
print(f"    Length: {len(anti_seed)}")

# Method 3: Row 15 (contains 28-char palindrome)
row15 = [int(matrix[15, c]) for c in range(128)]
row15_seed = ''.join(chr(abs(v)).lower() if 97 <= abs(v) <= 122 else '' for v in row15)
print(f"\n  Method 3 - Row 15 lowercase: '{row15_seed[:55]}'")
print(f"    Length: {len(row15_seed)}")

# Method 4: Column 30 (AI.MEG column)
col30 = [int(matrix[r, 30]) for r in range(128)]
col30_seed = ''.join(chr(abs(v)).lower() if 97 <= abs(v) <= 122 else '' for v in col30)
print(f"\n  Method 4 - Column 30 lowercase: '{col30_seed[:55]}'")
print(f"    Length: {len(col30_seed)}")

# Method 5: Combine palindrome centers
palindrome_chars = "mieteeimiifiifiiimieeteim"  # lowercase version without K
print(f"\n  Method 5 - Palindrome core: '{palindrome_chars}'")
print(f"    Length: {len(palindrome_chars)}")

# ==============================================================================
# VALIDATE AS QUBIC SEEDS
# ==============================================================================
print("\n" + "=" * 80)
print("SEED VALIDATION")
print("=" * 80)

def is_valid_qubic_seed(s):
    """Check if string could be a valid Qubic seed"""
    if len(s) != 55:
        return False, f"Wrong length: {len(s)}"
    if not s.islower():
        return False, "Contains uppercase"
    if not s.isalpha():
        return False, "Contains non-letters"
    return True, "Valid format"

candidates = [
    ("Concatenated top 10", concatenated[:55]),
    ("Main diagonal", diag_seed[:55] if len(diag_seed) >= 55 else diag_seed),
    ("Row 15", row15_seed[:55] if len(row15_seed) >= 55 else row15_seed),
]

print(f"\n  Candidate validation:")
for name, candidate in candidates:
    valid, reason = is_valid_qubic_seed(candidate)
    print(f"    {name}: {reason}")
    if len(candidate) >= 55:
        print(f"      '{candidate[:55]}'")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("QUBIC SEED INVESTIGATION COMPLETE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         SEED INVESTIGATION SUMMARY                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  LOWERCASE SEQUENCES FOUND:                                                   ║
║  • Total sequences (5+ chars): {len(lowercase_sequences):4}                                    ║
║  • Total lowercase chars: {total_chars:4}                                         ║
║  • Longest sequence: {lowercase_sequences[0]['length'] if lowercase_sequences else 0:2} chars                                        ║
║                                                                               ║
║  MATRIX LOWERCASE CELLS:                                                      ║
║  • Cells with values 97-122: {len(lowercase_from_matrix):4}                                    ║
║  • Unique letters: {len(char_counts):2}                                                  ║
║                                                                               ║
║  55-CHAR SEED CANDIDATES:                                                     ║
║  • From concatenation: {len(concatenated) >= 55}                                          ║
║  • From diagonal: {len(diag_seed) >= 55}                                              ║
║  • From row 15: {len(row15_seed) >= 55}                                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "lowercase_sequences": lowercase_sequences[:50],
    "total_sequences": len(lowercase_sequences),
    "total_chars": total_chars,
    "matrix_lowercase_count": len(lowercase_from_matrix),
    "candidates": {
        "concatenated": concatenated[:60],
        "diagonal": diag_seed[:60],
        "row15": row15_seed[:60],
        "col30": col30_seed[:60],
    }
}

with open(script_dir / "QUBIC_SEED_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved")
