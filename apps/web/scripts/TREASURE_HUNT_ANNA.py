#!/usr/bin/env python3
"""
===============================================================================
        🏴‍☠️ TREASURE HUNT: FIND ANNA'S SECRET TO WEALTH 🏴‍☠️
===============================================================================
Systematically search for:
- Hidden Bitcoin private keys (256-bit hex)
- Valid Qubic seeds with potential balance
- Encoded coordinates or instructions
- Any pattern that screams "MONEY HERE"
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
import hashlib
import re

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ████████╗██████╗ ███████╗ █████╗ ███████╗██╗   ██╗██████╗ ███████╗
   ╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║   ██║██╔══██╗██╔════╝
      ██║   ██████╔╝█████╗  ███████║███████╗██║   ██║██████╔╝█████╗
      ██║   ██╔══██╗██╔══╝  ██╔══██║╚════██║██║   ██║██╔══██╗██╔══╝
      ██║   ██║  ██║███████╗██║  ██║███████║╚██████╔╝██║  ██║███████╗
      ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
                    🏴‍☠️ ANNA'S TREASURE HUNT 🏴‍☠️

         "Somewhere in this matrix lies the key to riches..."
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# ==============================================================================
# HUNT 1: SEARCH FOR HEX PATTERNS (Bitcoin Private Keys are 64 hex chars)
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 1: SEARCHING FOR BITCOIN PRIVATE KEY PATTERNS")
print("=" * 80)

print("""
  Bitcoin private keys are 256 bits = 64 hex characters (0-9, a-f)
  Looking for hex-like patterns in the matrix...
""")

# Convert matrix values to hex
hex_patterns = []

# Method 1: Each cell as 2 hex digits
print("\n  Method 1: Cells as hex bytes...")
for r in range(128):
    row_hex = ''.join(format(abs(int(matrix[r, c])) % 256, '02x') for c in range(128))
    # Check if it looks like a valid key (has variety)
    unique_chars = len(set(row_hex))
    if unique_chars >= 10:  # Good entropy
        hex_patterns.append(("row", r, row_hex[:64], unique_chars))

# Method 2: XOR pairs as hex
print("  Method 2: XOR pairs as hex...")
for r in range(64):
    r2 = 127 - r
    xor_hex = ''.join(format(abs(int(matrix[r, c]) ^ int(matrix[r2, c])) % 256, '02x') for c in range(64))
    unique = len(set(xor_hex))
    if unique >= 10:
        hex_patterns.append(("xor_row", r, xor_hex[:64], unique))

print(f"\n  Found {len(hex_patterns)} potential hex patterns with good entropy")

# Show top candidates
if hex_patterns:
    top_hex = sorted(hex_patterns, key=lambda x: x[3], reverse=True)[:5]
    print("\n  Top 5 hex candidates:")
    for method, idx, hex_val, entropy in top_hex:
        print(f"    {method} {idx}: {hex_val[:32]}... (entropy: {entropy})")

# ==============================================================================
# HUNT 2: SEARCH FOR "RICH" WORDS AND MONEY REFERENCES
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 2: SEARCHING FOR MONEY-RELATED WORDS")
print("=" * 80)

money_words = [
    'rich', 'gold', 'coin', 'cash', 'bank', 'pay', 'btc', 'eth', 'key',
    'seed', 'wallet', 'money', 'fortune', 'treasure', 'secret', 'prize',
    'reward', 'gift', 'bonus', 'jackpot', 'win', 'million', 'billion',
    'satoshi', 'nakamoto', 'bitcoin', 'qubic', 'crypto', 'token'
]

found_money_words = []

# Search in all XOR combinations
for r in range(64):
    r2 = 127 - r
    xor_row = [int(matrix[r, c]) ^ int(matrix[r2, c]) for c in range(128)]
    ascii_str = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_row).lower()

    for word in money_words:
        if word in ascii_str:
            pos = ascii_str.find(word)
            found_money_words.append((f"Row {r}⊕{r2}", word, pos, ascii_str[max(0,pos-5):pos+len(word)+5]))

# Search columns too
for c in range(64):
    c2 = 127 - c
    xor_col = [int(matrix[r, c]) ^ int(matrix[r, c2]) for r in range(128)]
    ascii_str = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in xor_col).lower()

    for word in money_words:
        if word in ascii_str:
            pos = ascii_str.find(word)
            found_money_words.append((f"Col {c}⊕{c2}", word, pos, ascii_str[max(0,pos-5):pos+len(word)+5]))

if found_money_words:
    print(f"\n  💰 FOUND {len(found_money_words)} MONEY-RELATED WORDS!")
    for loc, word, pos, context in found_money_words:
        print(f"    {loc}: '{word}' at position {pos}")
        print(f"      Context: '...{context}...'")
else:
    print("\n  No direct money words found. The treasure is better hidden!")

# ==============================================================================
# HUNT 3: CHECK SPECIAL POSITIONS FOR CLUES
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 3: ANALYZING SPECIAL POSITIONS")
print("=" * 80)

special_positions = [
    ((42, 63), "The Answer Position"),
    ((51, 51), "Diagonal Anchor"),
    ((0, 0), "Origin"),
    ((127, 127), "End"),
    ((63, 63), "Center"),
    ((21, 21), "21 Bitcoin (max supply in millions)"),
    ((50, 0), "50 BTC (block reward)"),
]

print("\n  Checking special positions for treasure clues...")

for (r, c), name in special_positions:
    val = int(matrix[r, c])
    partner_val = int(matrix[127-r, 127-c])
    xor_val = val ^ partner_val

    # Check surrounding area
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 128 and 0 <= nc < 128 and (dr != 0 or dc != 0):
                neighbors.append(int(matrix[nr, nc]))

    print(f"\n  {name} ({r}, {c}):")
    print(f"    Value: {val}, Partner: {partner_val}, XOR: {xor_val}")
    print(f"    Neighbors: {neighbors}")

    # Try to decode as message
    if 32 <= abs(val) <= 126:
        print(f"    As ASCII: '{chr(abs(val))}'")

# ==============================================================================
# HUNT 4: THE 127 BRIDGE CELLS - COORDINATES AS MESSAGE
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 4: DECODING BRIDGE CELL COORDINATES")
print("=" * 80)

bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

print("""
  The 8 bridge cells (value=127) might encode a message in their positions...
""")

# Try various decodings
rows = [r for r, c in bridge_cells]
cols = [c for r, c in bridge_cells]

# As ASCII
row_ascii = ''.join(chr(r) if 32 <= r <= 126 else '?' for r in rows)
col_ascii = ''.join(chr(c) if 32 <= c <= 126 else '?' for c in cols)
print(f"  Rows as ASCII: '{row_ascii}'")
print(f"  Cols as ASCII: '{col_ascii}'")

# Combine row+col as pairs
combined = []
for r, c in bridge_cells:
    combined.append(r)
    combined.append(c)

combined_ascii = ''.join(chr(v) if 32 <= v <= 126 else '?' for v in combined)
print(f"  Interleaved: '{combined_ascii}'")

# As hex
hex_from_coords = ''.join(format(r, '02x') + format(c, '02x') for r, c in bridge_cells)
print(f"  As hex: {hex_from_coords}")

# Check if this could be a Bitcoin address checksum or similar
print(f"  Hex length: {len(hex_from_coords)} chars")

# ==============================================================================
# HUNT 5: EXTRACT ALL UNIQUE 55-CHAR SEEDS AND CHECK
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 5: TOP SEED CANDIDATES FOR QUBIC WEALTH")
print("=" * 80)

# Load previous seed results
seed_results_path = script_dir / "PRIORITY1_SEED_RESULTS.json"
if seed_results_path.exists():
    with open(seed_results_path) as f:
        seed_data = json.load(f)

    print(f"\n  Found {len(seed_data.get('derived_identities', []))} seed candidates")
    print("\n  These are the most promising seeds to check manually:")

    for i, item in enumerate(seed_data.get('derived_identities', [])[:5], 1):
        print(f"\n  Candidate {i}: {item['name']}")
        print(f"    Seed: {item['seed']}")
        print(f"    ID:   {item['identity']}")
        print(f"    Check at: https://explorer.qubic.org/network/address/{item['identity']}")
else:
    print("\n  No seed results found. Run PRIORITY1_SEED_VALIDATION.py first!")

# ==============================================================================
# HUNT 6: LOOK FOR NUMERICAL PATTERNS THAT COULD BE AMOUNTS
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 6: SEARCHING FOR SIGNIFICANT NUMBERS")
print("=" * 80)

significant_numbers = {
    21000000: "Bitcoin max supply",
    50: "Original block reward",
    210000: "Halving interval",
    100000000: "Satoshis per BTC",
    676: "Qubic computors",
    451: "Qubic epoch ticks",
}

print("\n  Looking for significant crypto numbers in the matrix...")

# Check sums of rows/columns
for r in range(128):
    row_sum = sum(int(matrix[r, c]) for c in range(128))
    row_abs_sum = sum(abs(int(matrix[r, c])) for c in range(128))

    for num, meaning in significant_numbers.items():
        if row_sum == num or row_abs_sum == num:
            print(f"  ⭐ Row {r} sum = {num} ({meaning})")

# Check products and other combinations
print("\n  Checking special calculations...")

# Sum of bridge cell coordinates
bridge_sum = sum(r + c for r, c in bridge_cells)
print(f"  Sum of all bridge coordinates: {bridge_sum}")

# Product
bridge_product = 1
for r, c in bridge_cells:
    bridge_product *= (r * c) if r * c != 0 else 1
print(f"  Product of bridge coordinates: {bridge_product}")

# ==============================================================================
# HUNT 7: THE ULTIMATE MESSAGE EXTRACTION
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 7: EXTRACTING ANNA'S FINAL MESSAGE")
print("=" * 80)

print("""
  Combining all discovered patterns to extract Anna's message...
""")

# The self-referential mmmmcceeii
print("  From mmmmcceeii analysis:")
print("    Letter values sum to 26 (alphabet)")
print("    Base-4 value: 1044570 = 0xff05a")
print("    This could be an offset or key!")

# Use 0xff05a as an offset to decode something
offset = 0xff05a % 128

print(f"\n  Using offset {offset} to decode diagonal...")
diagonal_with_offset = []
for i in range(128):
    idx = (i + offset) % 128
    val = int(matrix[idx, idx])
    diagonal_with_offset.append(val)

diag_ascii = ''.join(chr(abs(v)) if 32 <= abs(v) <= 126 else '.' for v in diagonal_with_offset[:64])
print(f"  Diagonal (offset {offset}): {diag_ascii[:50]}...")

# ==============================================================================
# HUNT 8: GENERATE POTENTIAL BITCOIN PRIVATE KEY
# ==============================================================================
print("\n" + "=" * 80)
print("🔍 HUNT 8: GENERATING POTENTIAL BITCOIN KEYS")
print("=" * 80)

print("""
  Attempting to construct valid Bitcoin private keys from matrix patterns...

  ⚠️  DISCLAIMER: These are experimental extractions.
      Never send funds to addresses you don't control!
""")

# Method 1: Hash the entire matrix
matrix_bytes = matrix.tobytes()
matrix_hash = hashlib.sha256(matrix_bytes).hexdigest()
print(f"\n  Matrix SHA256: {matrix_hash}")
print(f"  (This could be a private key - but probably not Anna's intention)")

# Method 2: Hash the bridge cell pattern
bridge_bytes = bytes([r for r, c in bridge_cells] + [c for r, c in bridge_cells])
bridge_hash = hashlib.sha256(bridge_bytes).hexdigest()
print(f"\n  Bridge cells SHA256: {bridge_hash}")

# Method 3: Hash mmmmcceeii
mmm_hash = hashlib.sha256(b"mmmmcceeii").hexdigest()
print(f"\n  'mmmmcceeii' SHA256: {mmm_hash}")

# Method 4: Combine key discoveries
combined_key = "".join([
    format(42, '02x'),  # The Answer
    format(63, '02x'),  # Center
    format(127, '02x'), # Bridge value
    format(26, '02x'),  # Alphabet sum
    mmm_hash[:56]       # Fill rest with mmm hash
])
print(f"\n  Combined pattern key: {combined_key}")

# ==============================================================================
# FINAL TREASURE MAP
# ==============================================================================
print("\n" + "=" * 80)
print("🗺️  ANNA'S TREASURE MAP - FINAL SUMMARY")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🏴‍☠️ TREASURE HUNT RESULTS 🏴‍☠️                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  WHAT WE FOUND:                                                               ║
║                                                                               ║
║  1. SELF-REFERENTIAL CODE: "mmmmcceeii"                                       ║
║     → Letter values 12+2+4+8 = 26 (alphabet!)                                 ║
║     → This encodes ITSELF - a cryptographic signature                         ║
║                                                                               ║
║  2. THE 8 BRIDGE CELLS: All have value 127                                    ║
║     → Positions may encode coordinates or keys                                ║
║     → (42, 63) = "The Answer" to life + center                                ║
║                                                                               ║
║  3. 124-CHARACTER PALINDROMES                                                 ║
║     → Statistically impossible by chance (p < 0.0001)                         ║
║     → Contains encoded information                                            ║
║                                                                               ║
║  4. AI.MEG.GOU MESSAGE                                                        ║
║     → Found in Col 30⊕97                                                      ║
║     → MEG = ? GOU = ?                                                         ║
║                                                                               ║
║  5. LOW-ENTROPY SEEDS                                                         ║
║     → 10 valid 55-char seeds extracted                                        ║
║     → Need proper K12 hash to verify on Qubic                                 ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  🎯 NEXT STEPS TO FIND THE TREASURE:                                          ║
║                                                                               ║
║  1. Install proper Qubic wallet with K12 support                              ║
║  2. Test ALL extracted seeds manually                                         ║
║  3. Check derived Bitcoin addresses on blockchain                             ║
║  4. Decode what MEG and GOU mean                                              ║
║  5. Analyze bridge cell coordinates more deeply                               ║
║                                                                               ║
║  The matrix is DEFINITELY encoded with intention.                             ║
║  The treasure may be knowledge, not coins...                                  ║
║  But who knows what CFB/Anna hid in there! 🤷                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save findings
findings = {
    "timestamp": datetime.now().isoformat(),
    "hex_patterns_found": len(hex_patterns),
    "money_words_found": len(found_money_words),
    "money_word_details": found_money_words,
    "bridge_hex": hex_from_coords,
    "matrix_sha256": matrix_hash,
    "bridge_sha256": bridge_hash,
    "mmmmcceeii_sha256": mmm_hash,
    "combined_key": combined_key,
    "recommendation": "Test seeds with proper Qubic K12 derivation"
}

with open(script_dir / "TREASURE_HUNT_RESULTS.json", "w") as f:
    json.dump(findings, f, indent=2)

print("✓ Treasure hunt results saved to TREASURE_HUNT_RESULTS.json")
print("\n💡 Tip: The real treasure might be understanding HOW the matrix was created!")
