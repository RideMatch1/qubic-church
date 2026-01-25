#!/usr/bin/env python3
"""
ULTRA MINING BLITZ - NO TOMORROW MODE
======================================
EVERY possible encoding method. EVERY combination.
All findings immediately validated with Monte-Carlo.

KEINE HALLUZINATIONEN - NUR VALIDIERTE FAKTEN!
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
import random
import itertools
import datetime

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

print("=" * 70)
print("ULTRA MINING BLITZ - NO TOMORROW MODE")
print("=" * 70)
print(f"Start: {datetime.datetime.now()}")

# Extended word list - includes crypto terms, names, commands
target_words = set([
    # Core crypto/tech
    'bitcoin', 'satoshi', 'nakamoto', 'genesis', 'block', 'hash', 'nonce', 'merkle',
    'qubic', 'iota', 'tangle', 'ternary', 'trinary', 'jinn', 'aigarth', 'oracle',
    'bridge', 'wallet', 'seed', 'node', 'chain', 'coin', 'mine', 'proof',
    # Names/identifiers
    'anna', 'cfb', 'mega', 'come', 'from', 'beyond', 'sergey', 'ivancheglo',
    # Commands/actions
    'init', 'boot', 'wake', 'rise', 'start', 'begin', 'open', 'unlock', 'decode',
    'read', 'find', 'seek', 'look', 'call', 'send', 'activate', 'execute',
    # Messages
    'hello', 'world', 'truth', 'proof', 'secret', 'hidden', 'code', 'cipher',
    'key', 'door', 'gate', 'path', 'way', 'here', 'now', 'time', 'wait',
    # Numbers as words
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'zero', 'null', 'void', 'none',
    # Special
    'god', 'all', 'end', 'fib', 'meg', 'gou', 'you', 'are', 'the', 'and',
    # Longer significant words (5+ letters)
    'entropy', 'random', 'signal', 'pattern', 'matrix', 'vector', 'tensor',
    'neural', 'network', 'brain', 'mind', 'think', 'learn', 'compute',
    'future', 'past', 'present', 'eternal', 'infinite', 'finite',
    'creator', 'author', 'builder', 'maker', 'master', 'system',
])

discoveries = []
validated = []

def monte_carlo_validate(text, word, iterations=1000):
    """Quick Monte-Carlo validation for a word in text."""
    if word not in text.lower():
        return None

    # Count in actual text
    actual_count = text.lower().count(word)

    # Generate random texts with same character distribution
    char_freq = Counter(text.lower())
    chars = list(char_freq.keys())
    weights = [char_freq[c] for c in chars]

    random_hits = 0
    for _ in range(iterations):
        rand_text = ''.join(random.choices(chars, weights=weights, k=len(text)))
        if word in rand_text:
            random_hits += 1

    p_value = random_hits / iterations

    return {
        "word": word,
        "count": actual_count,
        "p_value": p_value,
        "significant": p_value < 0.05
    }

def extract_and_validate(text, method_name, min_len=3):
    """Extract words and immediately validate."""
    results = []
    text_lower = text.lower()

    for word in target_words:
        if len(word) >= min_len and word in text_lower:
            pos = text_lower.find(word)
            context = text_lower[max(0, pos-15):pos+len(word)+15]

            # Validate longer words (4+) immediately
            validation = None
            if len(word) >= 4:
                validation = monte_carlo_validate(text, word, 500)

            result = {
                "method": method_name,
                "word": word,
                "position": pos,
                "context": context,
                "validation": validation
            }
            results.append(result)

            sig = ""
            if validation:
                sig = f" [p={validation['p_value']:.3f}{'*' if validation['significant'] else ''}]"
            print(f"  [{method_name}] '{word}' at {pos}{sig}")

    return results

# =============================================================================
# BLITZ 1: ALL 64 XOR PAIRS - Multiple Encodings
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 1: ALL 64 XOR PAIRS × MULTIPLE ENCODINGS")
print("=" * 70)

for col1 in range(64):
    col2 = 127 - col1

    # Method A: Standard XOR
    xor_vals = [(matrix[r][col1] & 0xFF) ^ (matrix[r][col2] & 0xFF) for r in range(128)]
    text_a = ''.join([chr(v) if 32 <= v <= 126 else '' for v in xor_vals])
    discoveries.extend(extract_and_validate(text_a, f"xor_{col1}_{col2}"))

    # Method B: XOR with 7-bit masking
    text_b = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in xor_vals])
    discoveries.extend(extract_and_validate(text_b, f"xor7_{col1}_{col2}"))

    # Method C: Difference encoding
    diff_vals = [abs(matrix[r][col1] - matrix[r][col2]) for r in range(128)]
    text_c = ''.join([chr(v) if 32 <= v <= 126 else '' for v in diff_vals])
    discoveries.extend(extract_and_validate(text_c, f"diff_{col1}_{col2}"))

# =============================================================================
# BLITZ 2: ALL ROWS × MULTIPLE ENCODINGS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 2: ALL 128 ROWS × MULTIPLE ENCODINGS")
print("=" * 70)

for r in range(128):
    row = matrix[r]

    # Direct 7-bit ASCII
    text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in row])
    discoveries.extend(extract_and_validate(text, f"row_{r}_ascii7"))

    # XOR with row index
    text = ''.join([chr((v ^ r) & 0x7F) if 32 <= ((v ^ r) & 0x7F) <= 126 else '' for v in row])
    discoveries.extend(extract_and_validate(text, f"row_{r}_xor_idx"))

    # Absolute values
    text = ''.join([chr(abs(v)) if 32 <= abs(v) <= 126 else '' for v in row])
    discoveries.extend(extract_and_validate(text, f"row_{r}_abs"))

    # XOR with 127
    text = ''.join([chr((v ^ 127) & 0x7F) if 32 <= ((v ^ 127) & 0x7F) <= 126 else '' for v in row])
    discoveries.extend(extract_and_validate(text, f"row_{r}_xor127"))

# =============================================================================
# BLITZ 3: ALL COLUMNS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 3: ALL 128 COLUMNS")
print("=" * 70)

for c in range(128):
    col = matrix[:, c]

    text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in col])
    discoveries.extend(extract_and_validate(text, f"col_{c}"))

# =============================================================================
# BLITZ 4: ALL DIAGONALS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 4: ALL DIAGONALS (255 total)")
print("=" * 70)

for offset in range(-127, 128):
    diag = []
    for i in range(128):
        c = i + offset
        if 0 <= c < 128:
            diag.append(matrix[i][c])

    if len(diag) >= 10:
        text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in diag])
        discoveries.extend(extract_and_validate(text, f"diag_{offset}"))

# Anti-diagonals
for offset in range(-127, 128):
    diag = []
    for i in range(128):
        c = 127 - i + offset
        if 0 <= c < 128:
            diag.append(matrix[i][c])

    if len(diag) >= 10:
        text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in diag])
        discoveries.extend(extract_and_validate(text, f"antidiag_{offset}"))

# =============================================================================
# BLITZ 5: MODULAR ARITHMETIC (All useful moduli)
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 5: MODULAR ARITHMETIC")
print("=" * 70)

for mod in [26, 27, 32, 64, 95, 128]:
    chars = []
    for v in matrix.flatten():
        m = abs(v) % mod
        if mod == 26:
            chars.append(chr(ord('a') + m))
        elif mod == 27:
            chars.append(' ' if m == 0 else chr(ord('a') + m - 1))
        elif mod == 95:
            chars.append(chr(32 + m))  # Printable ASCII range
        else:
            if 32 <= m <= 126:
                chars.append(chr(m))

    text = ''.join(chars)
    discoveries.extend(extract_and_validate(text[:10000], f"mod_{mod}"))

# =============================================================================
# BLITZ 6: BIT PLANES (All 8 bits)
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 6: BIT PLANE EXTRACTION")
print("=" * 70)

for bit in range(8):
    bit_plane = (matrix >> bit) & 1
    flat = bit_plane.flatten()

    # Convert groups of 7 bits to ASCII
    chars = []
    for i in range(0, len(flat) - 6, 7):
        byte = 0
        for b in range(7):
            byte |= flat[i + b] << (6 - b)
        if 32 <= byte <= 126:
            chars.append(chr(byte))

    text = ''.join(chars)
    discoveries.extend(extract_and_validate(text, f"bitplane_{bit}"))

# =============================================================================
# BLITZ 7: INTERLEAVING PATTERNS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 7: INTERLEAVING PATTERNS")
print("=" * 70)

# Interleave rows
for step in [2, 3, 4, 5, 7, 11]:
    chars = []
    for r in range(0, 128, step):
        for c in range(128):
            v = matrix[r][c]
            if 32 <= (v & 0x7F) <= 126:
                chars.append(chr(v & 0x7F))
    text = ''.join(chars)
    discoveries.extend(extract_and_validate(text, f"row_step_{step}"))

# Interleave columns
for step in [2, 3, 4, 5, 7, 11]:
    chars = []
    for c in range(0, 128, step):
        for r in range(128):
            v = matrix[r][c]
            if 32 <= (v & 0x7F) <= 126:
                chars.append(chr(v & 0x7F))
    text = ''.join(chars)
    discoveries.extend(extract_and_validate(text, f"col_step_{step}"))

# =============================================================================
# BLITZ 8: SPECIAL TRAVERSAL PATTERNS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 8: SPECIAL TRAVERSALS")
print("=" * 70)

# Spiral (outward)
def spiral_outward(m):
    result = []
    top, bottom, left, right = 0, 127, 0, 127
    while top <= bottom and left <= right:
        for i in range(left, right + 1):
            result.append(m[top][i])
        top += 1
        for i in range(top, bottom + 1):
            result.append(m[i][right])
        right -= 1
        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(m[bottom][i])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(m[i][left])
            left += 1
    return result

spiral = spiral_outward(matrix)
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in spiral])
discoveries.extend(extract_and_validate(text, "spiral_out"))

# Zigzag
def zigzag(m):
    result = []
    for r in range(128):
        if r % 2 == 0:
            for c in range(128):
                result.append(m[r][c])
        else:
            for c in range(127, -1, -1):
                result.append(m[r][c])
    return result

zz = zigzag(matrix)
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in zz])
discoveries.extend(extract_and_validate(text, "zigzag"))

# Hilbert curve approximation (simplified)
def hilbert_order():
    """Generate approximate Hilbert curve coordinates for 128x128."""
    coords = []
    for i in range(128):
        for j in range(128):
            # Simple approximation
            coords.append((i ^ (i >> 1), j ^ (j >> 1)))
    return coords

hilbert = hilbert_order()
hilbert_vals = [matrix[c[0] % 128][c[1] % 128] for c in hilbert]
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in hilbert_vals])
discoveries.extend(extract_and_validate(text, "hilbert"))

# =============================================================================
# BLITZ 9: VALUE-BASED FILTERING
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 9: VALUE-BASED FILTERING")
print("=" * 70)

# Only positive values
pos_vals = [v for v in matrix.flatten() if v > 0]
text = ''.join([chr(v) if 32 <= v <= 126 else '' for v in pos_vals])
discoveries.extend(extract_and_validate(text, "positive_only"))

# Only negative values (abs)
neg_vals = [abs(v) for v in matrix.flatten() if v < 0]
text = ''.join([chr(v) if 32 <= v <= 126 else '' for v in neg_vals])
discoveries.extend(extract_and_validate(text, "negative_abs"))

# Prime positions only
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

prime_vals = [matrix[r][c] for r in range(128) for c in range(128) if is_prime(r * 128 + c)]
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in prime_vals])
discoveries.extend(extract_and_validate(text, "prime_positions"))

# Fibonacci positions
fibs = set([0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
fib_vals = [matrix[r][c] for r in range(128) for c in range(128) if r in fibs or c in fibs]
text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in fib_vals])
discoveries.extend(extract_and_validate(text, "fibonacci_pos"))

# =============================================================================
# BLITZ 10: XOR COMBINATIONS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 10: XOR COMBINATIONS")
print("=" * 70)

# XOR all rows with row 64 (middle)
row64 = matrix[64]
for r in range(128):
    if r != 64:
        xor_row = matrix[r] ^ row64
        text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in xor_row])
        discoveries.extend(extract_and_validate(text, f"xor_row64_{r}"))

# XOR with constants
for const in [27, 42, 100, 121, 127]:
    xored = matrix ^ const
    text = ''.join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else '' for v in xored.flatten()])
    discoveries.extend(extract_and_validate(text[:5000], f"xor_const_{const}"))

# =============================================================================
# BLITZ 11: DIFFERENCE ENCODING
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 11: DIFFERENCE ENCODING")
print("=" * 70)

# Horizontal differences
h_diff = []
for r in range(128):
    for c in range(127):
        h_diff.append(abs(matrix[r][c+1] - matrix[r][c]))
text = ''.join([chr(v) if 32 <= v <= 126 else '' for v in h_diff])
discoveries.extend(extract_and_validate(text, "h_diff"))

# Vertical differences
v_diff = []
for c in range(128):
    for r in range(127):
        v_diff.append(abs(matrix[r+1][c] - matrix[r][c]))
text = ''.join([chr(v) if 32 <= v <= 126 else '' for v in v_diff])
discoveries.extend(extract_and_validate(text, "v_diff"))

# =============================================================================
# BLITZ 12: ASYMMETRIC CELLS DEEP ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("BLITZ 12: ASYMMETRIC CELLS (68 total)")
print("=" * 70)

asym_cells = []
for r in range(128):
    for c in range(128):
        if matrix[r][c] + matrix[127-r][127-c] != -1:
            asym_cells.append({
                "pos": (r, c),
                "val": matrix[r][c],
                "mirror_val": matrix[127-r][127-c]
            })

# Direct values
text = ''.join([chr(a["val"] & 0x7F) if 32 <= (a["val"] & 0x7F) <= 126 else '' for a in asym_cells])
discoveries.extend(extract_and_validate(text, "asym_direct"))

# XOR values
text = ''.join([chr((a["val"] ^ a["mirror_val"]) & 0x7F) if 32 <= ((a["val"] ^ a["mirror_val"]) & 0x7F) <= 126 else '' for a in asym_cells])
discoveries.extend(extract_and_validate(text, "asym_xor"))

# Sum values mod 256
text = ''.join([chr((a["val"] + a["mirror_val"]) & 0x7F) if 32 <= ((a["val"] + a["mirror_val"]) & 0x7F) <= 126 else '' for a in asym_cells])
discoveries.extend(extract_and_validate(text, "asym_sum"))

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("ULTRA MINING BLITZ COMPLETE")
print("=" * 70)
print(f"End: {datetime.datetime.now()}")

# Deduplicate
seen = set()
unique = []
for d in discoveries:
    key = (d["word"], d.get("validation", {}).get("significant", False) if d.get("validation") else False)
    if key not in seen:
        seen.add(key)
        unique.append(d)

# Separate validated from unvalidated
validated_significant = [d for d in unique if d.get("validation") and d["validation"]["significant"]]
validated_not_sig = [d for d in unique if d.get("validation") and not d["validation"]["significant"]]
unvalidated = [d for d in unique if not d.get("validation")]

print(f"\nTotal unique words found: {len(unique)}")
print(f"  Validated SIGNIFICANT (p < 0.05): {len(validated_significant)}")
print(f"  Validated not significant: {len(validated_not_sig)}")
print(f"  Short words (< 4 chars, not validated): {len(unvalidated)}")

if validated_significant:
    print("\n*** SIGNIFICANT FINDINGS (p < 0.05) ***")
    for d in sorted(validated_significant, key=lambda x: x["validation"]["p_value"]):
        print(f"  '{d['word']}' via [{d['method']}] p={d['validation']['p_value']:.4f}")
        print(f"    Context: ...{d['context']}...")

# Save results
output = {
    "timestamp": datetime.datetime.now().isoformat(),
    "total_unique": len(unique),
    "validated_significant": validated_significant,
    "validated_not_significant": validated_not_sig,
    "unvalidated_short": unvalidated,
    "methods_tested": 12
}

output_path = script_dir / "ULTRA_MINING_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n✓ Results saved to {output_path}")
