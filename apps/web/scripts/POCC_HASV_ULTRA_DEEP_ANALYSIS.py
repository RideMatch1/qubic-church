#!/usr/bin/env python3
"""
POCC ↔ HASV ULTRA-DEEP MATRIX ANALYSIS
=======================================
Findet ALLE versteckten mathematischen Verbindungen in der Anna Matrix
"""

import json
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations

# Load Anna Matrix
MATRIX_FILE = "../public/data/anna-matrix.json"
with open(MATRIX_FILE, 'r') as f:
    data = json.load(f)
    matrix = np.array(data['matrix'], dtype=np.int8)

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    return ord(c.upper()) - ord('A')

print("=" * 80)
print("POCC ↔ HASV ULTRA-DEEP MATRIX ANALYSIS")
print("=" * 80)
print()

# =============================================================================
# LEVEL 1: ALL ROW INTERACTIONS
# =============================================================================
print("[LEVEL 1] ALL ROW INTERACTIONS")
print("-" * 60)

pocc_chars = [char_to_num(c) for c in POCC]
hasv_chars = [char_to_num(c) for c in HASV]

# Test EVERY row for interesting patterns
interesting_rows = {}

for row in range(128):
    pocc_row_sum = sum(matrix[row][c] for c in pocc_chars)
    hasv_row_sum = sum(matrix[row][c] for c in hasv_chars)
    diff = hasv_row_sum - pocc_row_sum

    # Check if difference is significant
    if abs(diff) in [26, 33, 46, 138, 676]:
        interesting_rows[row] = {
            'pocc_sum': pocc_row_sum,
            'hasv_sum': hasv_row_sum,
            'diff': diff
        }

print(f"Rows with significant differences (26, 33, 46, 138, 676):")
for row, data in sorted(interesting_rows.items()):
    print(f"  Row {row:3d}: POCC={data['pocc_sum']:6d}, HASV={data['hasv_sum']:6d}, diff={data['diff']:6d}")

print()

# =============================================================================
# LEVEL 2: CROSS-MATRIX LOOKUPS
# =============================================================================
print("[LEVEL 2] CROSS-MATRIX LOOKUPS (POCC chars × HASV chars)")
print("-" * 60)

# For each pair of chars at same position, check matrix[pocc_char][hasv_char]
cross_lookups = []
for i in range(60):
    p = pocc_chars[i]
    h = hasv_chars[i]
    if 0 <= p < 128 and 0 <= h < 128:
        val = matrix[p][h]
        cross_lookups.append((i, POCC[i], HASV[i], p, h, val))

# Find patterns in cross-lookups
cross_values = [x[5] for x in cross_lookups]
print(f"Cross-lookup stats:")
print(f"  Sum: {sum(cross_values)}")
print(f"  Mean: {np.mean(cross_values):.2f}")
print(f"  Most common: {Counter(cross_values).most_common(5)}")
print()

# Check for 26, 676, 138
special_cross = [x for x in cross_lookups if abs(x[5]) in [26, 33, 46, 138, 676]]
if special_cross:
    print(f"Special cross-lookups (26, 33, 46, 138, 676):")
    for i, pc, hc, pv, hv, val in special_cross[:10]:
        print(f"  [{i:2d}] {pc}×{hc} → matrix[{pv},{hv}] = {val}")
print()

# =============================================================================
# LEVEL 3: WINDOW-BASED MATRIX PATTERNS
# =============================================================================
print("[LEVEL 3] WINDOW-BASED MATRIX ENCODING")
print("-" * 60)

# For 4-char windows, create matrix coordinate pairs
def window_to_coords(window):
    """Convert 4-char window to matrix coordinates"""
    coords = []
    s = sum(char_to_num(c) for c in window)
    if 0 <= s < 128:
        # Try different coordinate schemes
        coords.append(('sum', s, s))  # [s, s]
        coords.append(('row6', 6, s))  # [6, s]
        coords.append(('sum_row', s, 6))  # [s, 6]

        # Pair-based
        if len(window) >= 2:
            c1 = char_to_num(window[0])
            c2 = char_to_num(window[1])
            if 0 <= c1 < 128 and 0 <= c2 < 128:
                coords.append(('pair', c1, c2))
    return coords

pocc_windows = [POCC[i:i+4] for i in range(57)]
hasv_windows = [HASV[i:i+4] for i in range(57)]

# Compare window encodings
print("Comparing window matrix encodings...")
matches = defaultdict(list)

for i in range(57):
    p_coords = window_to_coords(pocc_windows[i])
    h_coords = window_to_coords(hasv_windows[i])

    for p_type, p_r, p_c in p_coords:
        for h_type, h_r, h_c in h_coords:
            if matrix[p_r][p_c] == matrix[h_r][h_c]:
                matches[f"{p_type}={h_type}"].append({
                    'pos': i,
                    'pocc_window': pocc_windows[i],
                    'hasv_window': hasv_windows[i],
                    'value': matrix[p_r][p_c]
                })

for key, match_list in matches.items():
    if len(match_list) >= 3:  # At least 3 matches
        print(f"\n{key}: {len(match_list)} matches")
        for m in match_list[:5]:
            print(f"  [{m['pos']:2d}] {m['pocc_window']} ≡ {m['hasv_window']} → {m['value']}")

print()

# =============================================================================
# LEVEL 4: PALINDROME AND SYMMETRY PATTERNS
# =============================================================================
print("[LEVEL 4] PALINDROME & SYMMETRY ANALYSIS")
print("-" * 60)

# Check if addresses have palindromic properties
def check_palindrome_sections(addr, section_size=4):
    """Check for palindromic sections"""
    palindromes = []
    for i in range(len(addr) - section_size + 1):
        section = addr[i:i+section_size]
        if section == section[::-1]:
            palindromes.append((i, section))
    return palindromes

pocc_palindromes = check_palindrome_sections(POCC)
hasv_palindromes = check_palindrome_sections(HASV)

print(f"POCC palindromes: {pocc_palindromes}")
print(f"HASV palindromes: {hasv_palindromes}")
print()

# Reverse and mirror encodings
pocc_reversed = POCC[::-1]
hasv_reversed = HASV[::-1]

pocc_rev_sum = sum(char_to_num(c) for c in pocc_reversed)
hasv_rev_sum = sum(char_to_num(c) for c in hasv_reversed)

print(f"Reversed sums:")
print(f"  POCC reversed: {pocc_rev_sum}")
print(f"  HASV reversed: {hasv_rev_sum}")
print(f"  Difference: {hasv_rev_sum - pocc_rev_sum}")
print()

# =============================================================================
# LEVEL 5: FIBONACCI & GOLDEN RATIO POSITIONS
# =============================================================================
print("[LEVEL 5] FIBONACCI POSITION ENCODING")
print("-" * 60)

# Fibonacci positions in the address
fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
fib_positions = [f for f in fib if f < 60]

print(f"Checking Fibonacci positions: {fib_positions}")

pocc_fib_chars = [POCC[i] for i in fib_positions]
hasv_fib_chars = [HASV[i] for i in fib_positions]

pocc_fib_sum = sum(char_to_num(c) for c in pocc_fib_chars)
hasv_fib_sum = sum(char_to_num(c) for c in hasv_fib_chars)

print(f"Fibonacci position sums:")
print(f"  POCC: {pocc_fib_sum}")
print(f"  HASV: {hasv_fib_sum}")
print(f"  Difference: {hasv_fib_sum - pocc_fib_sum}")
print()

# =============================================================================
# LEVEL 6: PRIME NUMBER POSITIONS
# =============================================================================
print("[LEVEL 6] PRIME POSITION ENCODING")
print("-" * 60)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

prime_positions = [i for i in range(60) if is_prime(i)]
print(f"Prime positions: {prime_positions}")

pocc_prime_chars = [POCC[i] for i in prime_positions]
hasv_prime_chars = [HASV[i] for i in prime_positions]

pocc_prime_sum = sum(char_to_num(c) for c in pocc_prime_chars)
hasv_prime_sum = sum(char_to_num(c) for c in hasv_prime_chars)

print(f"Prime position sums:")
print(f"  POCC: {pocc_prime_sum}")
print(f"  HASV: {hasv_prime_sum}")
print(f"  Difference: {hasv_prime_sum - pocc_prime_sum}")
print()

# =============================================================================
# LEVEL 7: MATRIX EIGENVALUE CONNECTION
# =============================================================================
print("[LEVEL 7] MATRIX ALGEBRAIC PROPERTIES")
print("-" * 60)

try:
    # Compute eigenvalues (may take a moment)
    eigenvalues = np.linalg.eigvals(matrix.astype(np.float64))
    top_eigenvalues = sorted(eigenvalues.real, reverse=True)[:10]

    print(f"Top 10 eigenvalues:")
    for i, ev in enumerate(top_eigenvalues):
        print(f"  λ{i+1} = {ev:.2f}")

    # Check if any are close to our key numbers
    key_numbers = [26, 33, 46, 138, 676]
    for num in key_numbers:
        closest = min(top_eigenvalues, key=lambda x: abs(x - num))
        if abs(closest - num) < 5:
            print(f"  ⚠️  Eigenvalue {closest:.2f} ≈ {num}")

except Exception as e:
    print(f"Eigenvalue computation failed: {e}")

print()

# =============================================================================
# LEVEL 8: MODULAR ARITHMETIC PATTERNS
# =============================================================================
print("[LEVEL 8] MODULAR ARITHMETIC DEEP DIVE")
print("-" * 60)

moduli = [7, 13, 23, 26, 128, 676]
pocc_sum = sum(pocc_chars)
hasv_sum = sum(hasv_chars)

print(f"Modular patterns:")
for mod in moduli:
    p_mod = pocc_sum % mod
    h_mod = hasv_sum % mod
    diff_mod = (hasv_sum - pocc_sum) % mod
    print(f"  mod {mod:3d}: POCC={p_mod:3d}, HASV={h_mod:3d}, diff={diff_mod:3d}")

print()

# Check if diagonal sums have special modular properties
pocc_diag = sum(matrix[c][c] for c in pocc_chars)
hasv_diag = sum(matrix[c][c] for c in hasv_chars)

print(f"Diagonal modular patterns:")
for mod in moduli:
    p_mod = pocc_diag % mod
    h_mod = hasv_diag % mod
    diff_mod = (hasv_diag - pocc_diag) % mod
    print(f"  mod {mod:3d}: POCC={p_mod:3d}, HASV={h_mod:3d}, diff={diff_mod:3d}")

print()

# =============================================================================
# LEVEL 9: HAMMING DISTANCE & BIT PATTERNS
# =============================================================================
print("[LEVEL 9] HAMMING DISTANCE & BIT ANALYSIS")
print("-" * 60)

# Hamming distance
hamming_distance = sum(1 for i in range(60) if POCC[i] != HASV[i])
print(f"Hamming distance: {hamming_distance}/60")
print(f"Similarity: {(60-hamming_distance)/60*100:.1f}%")
print()

# Bit-level XOR pattern
xor_values = [pocc_chars[i] ^ hasv_chars[i] for i in range(60)]
print(f"XOR pattern stats:")
print(f"  Sum: {sum(xor_values)}")
print(f"  Mean: {np.mean(xor_values):.2f}")
print(f"  Distribution: {Counter(xor_values).most_common(10)}")
print()

# =============================================================================
# LEVEL 10: SEARCH FOR 676 ENCODING EVERYWHERE
# =============================================================================
print("[LEVEL 10] 676 SIGNATURE SEARCH")
print("-" * 60)

# Find ALL ways these addresses encode 676
encodings_676 = []

# 1. Diagonal difference (already known)
encodings_676.append(("Diagonal difference", hasv_diag - pocc_diag))

# 2. Specific row sums
for row in range(128):
    p_row = sum(matrix[row][c] for c in pocc_chars)
    h_row = sum(matrix[row][c] for c in hasv_chars)
    if abs(h_row - p_row) == 676:
        encodings_676.append((f"Row {row} difference", h_row - p_row))

# 3. Column sums
for col in range(128):
    p_col = sum(matrix[c][col] for c in pocc_chars if c < 128)
    h_col = sum(matrix[c][col] for c in hasv_chars if c < 128)
    if abs(h_col - p_col) == 676:
        encodings_676.append((f"Column {col} difference", h_col - p_col))

# 4. Product/XOR combinations
if (pocc_sum * hasv_sum) % 676 == 0:
    encodings_676.append(("Product mod 676", 0))

# 5. Window-based
for window_size in [2, 3, 4, 5, 6]:
    for i in range(60 - window_size + 1):
        p_window_sum = sum(char_to_num(POCC[j]) for j in range(i, i+window_size))
        h_window_sum = sum(char_to_num(HASV[j]) for j in range(i, i+window_size))
        if abs(h_window_sum - p_window_sum) == 26:  # 26² = 676
            encodings_676.append((f"Window size {window_size} at pos {i} (26)", h_window_sum - p_window_sum))

print(f"Found {len(encodings_676)} ways to encode 676:")
for name, value in encodings_676[:15]:
    print(f"  {name}: {value}")

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 80)
print("ULTRA-DEEP ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Key discoveries:")
print(f"  1. {len(interesting_rows)} rows with significant differences")
print(f"  2. Cross-lookup sum: {sum(cross_values)}")
print(f"  3. Hamming distance: {hamming_distance}/60")
print(f"  4. Fibonacci position diff: {hasv_fib_sum - pocc_fib_sum}")
print(f"  5. Prime position diff: {hasv_prime_sum - pocc_prime_sum}")
print(f"  6. Total 676 encodings found: {len(encodings_676)}")
print()
