#!/usr/bin/env python3
"""
ARK ISSUER ADDRESS - COMPLETE MATHEMATICAL ANALYSIS
Analyzing like POCC/HASV to find hidden patterns
"""

import json
import sys
from pathlib import Path
import numpy as np

# ARK Issuer Address
ARK = "ARKMGCWFYEHJFAVSGKEXVWBGGXZAVLZNBDNBZEXTQBKLKRPEYPEIEKFHUPNG"

# Reference addresses for comparison
POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

def char_to_num(c):
    """Convert character to number (A=0, B=1, ..., Z=25)"""
    if c.isalpha():
        return ord(c.upper()) - ord('A')
    return 0

def load_anna_matrix():
    """Load Anna Matrix from JSON file"""
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
        return np.array(data['matrix'], dtype=np.float64)

def analyze_complete(address, name="Address"):
    """Complete POCC/HASV-style analysis"""
    print(f"\n{'='*80}")
    print(f"COMPLETE ANALYSIS: {name}")
    print(f"{'='*80}")
    print(f"Address: {address}")
    print(f"Length: {len(address)} characters\n")

    # Character values
    chars = [char_to_num(c) for c in address if c.isalpha()]

    # Load matrix
    matrix = load_anna_matrix()

    # ==================== SECTION 1: CHARACTER SUMS ====================
    print(f"{'='*80}")
    print("SECTION 1: CHARACTER SUMS")
    print(f"{'='*80}")

    # 1.1 Zero-based sum (A=0...Z=25)
    char_sum = sum(chars)
    print(f"\n1.1 ZERO-BASED SUM (A=0...Z=25)")
    print(f"    Sum: {char_sum}")

    # 1.2 One-based sum (A=1...Z=26)
    one_based_sum = sum(c + 1 for c in chars)
    print(f"\n1.2 ONE-BASED SUM (A=1...Z=26)")
    print(f"    Sum: {one_based_sum}")
    print(f"    Distance from 676: {abs(676 - one_based_sum)} ({abs(676 - one_based_sum)/676*100:.2f}% error)")
    if abs(676 - one_based_sum) < 10:
        print(f"    ⭐ VERY CLOSE TO 676!")

    # 1.3 Cubes sum
    cubes_sum = sum(c**3 for c in chars)
    print(f"\n1.3 SUM OF CUBES")
    print(f"    Sum: {cubes_sum}")
    print(f"    Divisible by 676? {cubes_sum % 676 == 0}")
    if cubes_sum % 676 == 0:
        print(f"    ⭐ CUBES SUM = {cubes_sum // 676} × 676")

    # ==================== SECTION 2: DIAGONAL MATRIX SUM ====================
    print(f"\n{'='*80}")
    print("SECTION 2: DIAGONAL MATRIX SUM")
    print(f"{'='*80}")

    diagonal_sum = sum(matrix[c][c] for c in chars if c < 128)
    print(f"\n2.1 DIAGONAL SUM")
    print(f"    Sum: {diagonal_sum:.0f}")
    print(f"    Comparison to POCC: {diagonal_sum - (-1231):.0f}")
    print(f"    Comparison to HASV: {diagonal_sum - (-555):.0f}")

    diff_pocc = abs(diagonal_sum - (-1231))
    diff_hasv = abs(diagonal_sum - (-555))

    if diff_pocc % 676 == 0:
        print(f"    ⭐ DIFF FROM POCC = {int(diff_pocc // 676)} × 676!")
    if diff_hasv % 676 == 0:
        print(f"    ⭐ DIFF FROM HASV = {int(diff_hasv // 676)} × 676!")

    # ==================== SECTION 3: MODULAR PROPERTIES ====================
    print(f"\n{'='*80}")
    print("SECTION 3: MODULAR PROPERTIES")
    print(f"{'='*80}")

    print(f"\n3.1 CHARACTER SUM MODULOS")
    for mod in [6, 23, 26, 46, 121, 138, 676]:
        result = char_sum % mod
        print(f"    char_sum mod {mod:3d} = {result:3d}", end="")

        # Compare to POCC/HASV
        pocc_chars = [char_to_num(c) for c in POCC if c.isalpha()]
        hasv_chars = [char_to_num(c) for c in HASV if c.isalpha()]
        pocc_mod = sum(pocc_chars) % mod
        hasv_mod = sum(hasv_chars) % mod

        if result == pocc_mod == hasv_mod:
            print(f" ⭐ MATCHES BOTH POCC & HASV!")
        elif result == pocc_mod:
            print(f" ← MATCHES POCC")
        elif result == hasv_mod:
            print(f" ← MATCHES HASV")
        else:
            print()

    print(f"\n3.2 DIAGONAL SUM MODULOS")
    for mod in [26, 121, 676]:
        result = int(diagonal_sum) % mod
        print(f"    diagonal mod {mod:3d} = {result:3d}", end="")

        if mod == 676 and result == 121:
            print(f" ⭐ = 11² (LIKE POCC/HASV!)")
        elif mod == 26 and result == 17:
            print(f" ⭐ MATCHES POCC/HASV!")
        else:
            print()

    # ==================== SECTION 4: ROW 6 ORACLE ====================
    print(f"\n{'='*80}")
    print("SECTION 4: ROW 6 ORACLE")
    print(f"{'='*80}")

    # Prefix (first 4 letters)
    prefix = address[:4]
    prefix_sum = sum(char_to_num(c) for c in prefix)
    print(f"\n4.1 PREFIX ANALYSIS")
    print(f"    Prefix: {prefix}")
    print(f"    Prefix sum: {prefix_sum}")
    print(f"    matrix[6,{prefix_sum}] = {matrix[6][prefix_sum]:.0f}", end="")
    if matrix[6][prefix_sum] == 26:
        print(f" ⭐⭐⭐ EQUALS 26 (LIKE POCC!)")
    elif matrix[6][prefix_sum] == 90:
        print(f" ⭐⭐⭐ EQUALS 90 (LIKE HASV!)")
    else:
        print()

    # All 4-letter windows
    print(f"\n4.2 SLIDING WINDOW ANALYSIS (all 4-letter windows)")
    special_windows = []
    for i in range(len(address) - 3):
        window = address[i:i+4]
        window_sum = sum(char_to_num(c) for c in window)
        if window_sum < 128:
            row6_value = matrix[6][window_sum]
            if row6_value in [26, 90, 121, 138, 676 % 128]:
                special_windows.append((i, window, window_sum, row6_value))

    print(f"    Found {len(special_windows)} windows with special Row 6 values:")
    for i, window, wsum, value in special_windows[:10]:  # Show first 10
        print(f"    Position {i:2d}: '{window}' (sum={wsum:3d}) → matrix[6,{wsum}] = {value:.0f}")
    if len(special_windows) > 10:
        print(f"    ... and {len(special_windows) - 10} more")

    # ==================== SECTION 5: POSITION PATTERNS ====================
    print(f"\n{'='*80}")
    print("SECTION 5: POSITION PATTERNS")
    print(f"{'='*80}")

    # Compare positions with POCC and HASV
    print(f"\n5.1 IDENTICAL POSITIONS WITH POCC")
    pocc_matches = []
    for i in range(min(len(address), len(POCC))):
        if address[i] == POCC[i] and address[i].isalpha():
            pocc_matches.append((i, address[i]))

    if pocc_matches:
        print(f"    Found {len(pocc_matches)} matching positions:")
        for pos, char in pocc_matches[:10]:
            print(f"    Position {pos}: {char}")

        positions_sum = sum(pos for pos, _ in pocc_matches)
        chars_sum = sum(char_to_num(char) for _, char in pocc_matches)
        print(f"\n    Sum of positions: {positions_sum}")
        print(f"    Sum of char values: {chars_sum}")
        print(f"    Positions mod 26: {positions_sum % 26}")
        print(f"    Chars mod 26: {chars_sum % 26}")
    else:
        print(f"    No matching positions with POCC")

    print(f"\n5.2 IDENTICAL POSITIONS WITH HASV")
    hasv_matches = []
    for i in range(min(len(address), len(HASV))):
        if address[i] == HASV[i] and address[i].isalpha():
            hasv_matches.append((i, address[i]))

    if hasv_matches:
        print(f"    Found {len(hasv_matches)} matching positions:")
        for pos, char in hasv_matches[:10]:
            print(f"    Position {pos}: {char}")

        positions_sum = sum(pos for pos, _ in hasv_matches)
        chars_sum = sum(char_to_num(char) for _, char in hasv_matches)
        print(f"\n    Sum of positions: {positions_sum}")
        print(f"    Sum of char values: {chars_sum}")
        print(f"    Positions mod 26: {positions_sum % 26}")
        print(f"    Chars mod 26: {chars_sum % 26}")
    else:
        print(f"    No matching positions with HASV")

    # ==================== SECTION 6: ROW 79 ANALYSIS ====================
    print(f"\n{'='*80}")
    print("SECTION 6: ROW 79 SPECIAL")
    print(f"{'='*80}")

    row79_sum = sum(matrix[79][c] for c in chars if c < 128)
    print(f"\n6.1 ROW 79 SUM")
    print(f"    Sum: {row79_sum:.0f}")

    pocc_row79 = sum(matrix[79][char_to_num(c)] for c in POCC if c.isalpha() and char_to_num(c) < 128)
    hasv_row79 = sum(matrix[79][char_to_num(c)] for c in HASV if c.isalpha() and char_to_num(c) < 128)

    print(f"    Difference from POCC row79: {row79_sum - pocc_row79:.0f}")
    print(f"    Difference from HASV row79: {row79_sum - hasv_row79:.0f}")

    if abs(row79_sum - pocc_row79) == 26:
        print(f"    ⭐ DIFF FROM POCC = 26 (√676)!")
    if abs(row79_sum - hasv_row79) == 26:
        print(f"    ⭐ DIFF FROM HASV = 26 (√676)!")

    # ==================== SECTION 7: SPECIAL CHAR VALUES ====================
    print(f"\n{'='*80}")
    print("SECTION 7: SPECIAL CHARACTER VALUES")
    print(f"{'='*80}")

    # Count occurrences of special values
    print(f"\n7.1 CHARACTER VALUE DISTRIBUTION")
    special_values = [0, 6, 7, 11, 17, 25]  # Special in previous research
    for val in special_values:
        count = chars.count(val)
        if count > 0:
            letter = chr(ord('A') + val)
            print(f"    Value {val:2d} ({letter}): appears {count} times")

    # Count diagonal value 26
    diagonal_26_count = sum(1 for c in chars if c < 128 and matrix[c][c] == 26)
    print(f"\n7.2 DIAGONAL VALUE 26 COUNT")
    print(f"    Characters with diagonal value 26: {diagonal_26_count}")
    print(f"    (POCC has 2, HASV has 7)")

    # ==================== SECTION 8: SUMMARY ====================
    print(f"\n{'='*80}")
    print("SECTION 8: SUMMARY OF KEY NUMBERS")
    print(f"{'='*80}")

    print(f"\n📊 KEY METRICS:")
    print(f"    Character sum (0-based):   {char_sum}")
    print(f"    Character sum (1-based):   {one_based_sum}")
    print(f"    Diagonal sum:              {diagonal_sum:.0f}")
    print(f"    Cubes sum:                 {cubes_sum}")
    print(f"    Row 79 sum:                {row79_sum:.0f}")
    print(f"    Prefix sum (Row 6 lookup): {prefix_sum} → {matrix[6][prefix_sum]:.0f}")
    print(f"    Special Row 6 windows:     {len(special_windows)}")
    print(f"    Positions matching POCC:   {len(pocc_matches)}")
    print(f"    Positions matching HASV:   {len(hasv_matches)}")

    return {
        'char_sum': char_sum,
        'one_based_sum': one_based_sum,
        'diagonal_sum': diagonal_sum,
        'cubes_sum': cubes_sum,
        'row79_sum': row79_sum,
        'prefix_sum': prefix_sum,
        'special_windows': len(special_windows),
        'pocc_matches': len(pocc_matches),
        'hasv_matches': len(hasv_matches)
    }

def compare_all_three():
    """Compare ARK, POCC, HASV side by side"""
    print(f"\n{'='*80}")
    print("COMPARATIVE ANALYSIS: ARK vs POCC vs HASV")
    print(f"{'='*80}")

    ark_chars = [char_to_num(c) for c in ARK if c.isalpha()]
    pocc_chars = [char_to_num(c) for c in POCC if c.isalpha()]
    hasv_chars = [char_to_num(c) for c in HASV if c.isalpha()]

    matrix = load_anna_matrix()

    print(f"\n{'Metric':<30} {'ARK':>10} {'POCC':>10} {'HASV':>10}")
    print(f"{'-'*60}")

    # Character sums
    ark_sum = sum(ark_chars)
    pocc_sum = sum(pocc_chars)
    hasv_sum = sum(hasv_chars)
    print(f"{'Character sum':<30} {ark_sum:>10} {pocc_sum:>10} {hasv_sum:>10}")

    # Diagonal sums
    ark_diag = sum(matrix[c][c] for c in ark_chars if c < 128)
    pocc_diag = sum(matrix[c][c] for c in pocc_chars if c < 128)
    hasv_diag = sum(matrix[c][c] for c in hasv_chars if c < 128)
    print(f"{'Diagonal sum':<30} {ark_diag:>10.0f} {pocc_diag:>10.0f} {hasv_diag:>10.0f}")

    # Differences
    print(f"\n{'Differences':<30} {'ARK-POCC':>10} {'ARK-HASV':>10} {'POCC-HASV':>10}")
    print(f"{'-'*60}")
    print(f"{'Character sum diff':<30} {ark_sum - pocc_sum:>10} {ark_sum - hasv_sum:>10} {pocc_sum - hasv_sum:>10}")
    print(f"{'Diagonal sum diff':<30} {ark_diag - pocc_diag:>10.0f} {ark_diag - hasv_diag:>10.0f} {pocc_diag - hasv_diag:>10.0f}")

    # Check if differences are special
    print(f"\n🔍 CHECKING FOR SPECIAL DIFFERENCE VALUES:")
    for val, name in [(676, "676"), (138, "138"), (26, "26"), (121, "121")]:
        if abs((ark_diag - pocc_diag) - val) < 1:
            print(f"   ⭐ ARK - POCC diagonal ≈ {name}!")
        if abs((ark_diag - hasv_diag) - val) < 1:
            print(f"   ⭐ ARK - HASV diagonal ≈ {name}!")

def main():
    """Execute complete analysis"""
    print("\n" + "="*80)
    print("ARK ISSUER ADDRESS - COMPLETE MATHEMATICAL ANALYSIS")
    print("Analyzing with same rigor as POCC/HASV research")
    print("="*80)

    # Full analysis of ARK
    ark_results = analyze_complete(ARK, "ARK ISSUER")

    # Comparative analysis
    compare_all_three()

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"""
🎯 NEXT STEPS:
   1. Review all ⭐ marked discoveries above
   2. Compare to POCC/HASV patterns
   3. Document any new connections found
   4. Monitor for temporal events at T+7, T+21, March 3
    """)

if __name__ == "__main__":
    main()
