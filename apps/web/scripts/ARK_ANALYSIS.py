#!/usr/bin/env python3
"""
ARK Token Address Analysis
Analyzing ARKMGCWFYEHJFAVSGKEXVWBGGXZAVLZNBDNBZEXTQBKLKRPEYPEIEKFHUPNG
for mathematical patterns similar to POCC/HASV research
"""

import json
import sys
from pathlib import Path

# ARK address
ARK = "ARKMGCWFYEHJFAVSGKEXVWBGGXZAVLZNBDNBZEXTQBKLKRPEYPEIEKFHUPNG"

# Reference addresses
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
        return data['matrix']

def analyze_address(address, name="Address"):
    """Perform comprehensive analysis on an address"""
    print(f"\n{'='*80}")
    print(f"ANALYSIS: {name}")
    print(f"{'='*80}")
    print(f"Address: {address}")
    print(f"Length: {len(address)} characters\n")

    # Character values
    chars = [char_to_num(c) for c in address if c.isalpha()]

    # 1. Character Sum (A=0...Z=25)
    char_sum = sum(chars)
    print(f"1. CHARACTER SUM (A=0...Z=25)")
    print(f"   Sum: {char_sum}")

    # 2. One-based sum (A=1...Z=26)
    one_based_sum = sum(c + 1 for c in chars)
    print(f"\n2. ONE-BASED SUM (A=1...Z=26)")
    print(f"   Sum: {one_based_sum}")
    print(f"   Distance from 676: {abs(676 - one_based_sum)} ({abs(676 - one_based_sum)/676*100:.2f}% error)")

    # 3. Load matrix and calculate diagonal sum
    try:
        matrix = load_anna_matrix()
        diagonal_sum = sum(matrix[c][c] for c in chars if c < 128)
        print(f"\n3. DIAGONAL MATRIX SUM")
        print(f"   Diagonal sum: {diagonal_sum}")
    except Exception as e:
        print(f"\n3. DIAGONAL MATRIX SUM")
        print(f"   Error loading matrix: {e}")
        diagonal_sum = None

    # 4. Modular properties
    print(f"\n4. MODULAR PROPERTIES")
    print(f"   char_sum mod 6:   {char_sum % 6}")
    print(f"   char_sum mod 23:  {char_sum % 23}")
    print(f"   char_sum mod 26:  {char_sum % 26}")
    print(f"   char_sum mod 46:  {char_sum % 46}")
    print(f"   char_sum mod 121: {char_sum % 121}")
    print(f"   char_sum mod 138: {char_sum % 138}")
    print(f"   char_sum mod 676: {char_sum % 676}")

    if diagonal_sum is not None:
        print(f"\n   diagonal mod 26:  {diagonal_sum % 26}")
        print(f"   diagonal mod 121: {diagonal_sum % 121}")
        print(f"   diagonal mod 676: {diagonal_sum % 676}")

    # 5. Prefix analysis (first 4 letters)
    prefix = address[:4]
    prefix_sum = sum(char_to_num(c) for c in prefix)
    print(f"\n5. PREFIX ANALYSIS")
    print(f"   Prefix: {prefix}")
    print(f"   Prefix sum: {prefix_sum}")

    if matrix:
        try:
            row6_value = matrix[6][prefix_sum]
            print(f"   matrix[6,{prefix_sum}] = {row6_value}")
        except:
            print(f"   matrix[6,{prefix_sum}] = OUT OF RANGE")

    # 6. Sum of cubes
    cubes_sum = sum(c**3 for c in chars)
    print(f"\n6. SUM OF CUBES")
    print(f"   Sum: {cubes_sum}")

    # 7. Factorization of key numbers
    print(f"\n7. FACTORIZATION")
    print(f"   {char_sum} = ", end="")
    factorize(char_sum)

    return {
        'address': address,
        'char_sum': char_sum,
        'one_based_sum': one_based_sum,
        'diagonal_sum': diagonal_sum,
        'prefix_sum': prefix_sum,
        'cubes_sum': cubes_sum,
        'chars': chars
    }

def factorize(n):
    """Simple factorization"""
    if n <= 1:
        print(n)
        return

    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)

    if factors:
        print(" × ".join(map(str, factors)))
    else:
        print(f"{n} (prime)")

def compare_addresses(ark_data, pocc_data, hasv_data):
    """Compare ARK with POCC and HASV"""
    print(f"\n{'='*80}")
    print(f"COMPARATIVE ANALYSIS")
    print(f"{'='*80}")

    # Character sum differences
    print(f"\nCHARACTER SUM COMPARISONS:")
    print(f"ARK:  {ark_data['char_sum']}")
    print(f"POCC: {pocc_data['char_sum']}")
    print(f"HASV: {hasv_data['char_sum']}")
    print(f"\nARK - POCC = {ark_data['char_sum'] - pocc_data['char_sum']}")
    print(f"ARK - HASV = {ark_data['char_sum'] - hasv_data['char_sum']}")
    print(f"POCC - HASV = {pocc_data['char_sum'] - hasv_data['char_sum']} (known: 138)")

    # Diagonal sum differences
    if all(d['diagonal_sum'] is not None for d in [ark_data, pocc_data, hasv_data]):
        print(f"\nDIAGONAL SUM COMPARISONS:")
        print(f"ARK:  {ark_data['diagonal_sum']}")
        print(f"POCC: {pocc_data['diagonal_sum']}")
        print(f"HASV: {hasv_data['diagonal_sum']}")
        print(f"\nARK - POCC = {ark_data['diagonal_sum'] - pocc_data['diagonal_sum']}")
        print(f"ARK - HASV = {ark_data['diagonal_sum'] - hasv_data['diagonal_sum']}")
        print(f"POCC - HASV = {pocc_data['diagonal_sum'] - hasv_data['diagonal_sum']} (known: 676)")

        # Check if differences are special numbers
        ark_pocc_diff = ark_data['diagonal_sum'] - pocc_data['diagonal_sum']
        ark_hasv_diff = ark_data['diagonal_sum'] - hasv_data['diagonal_sum']

        print(f"\nSPECIAL NUMBER CHECKS:")
        for diff, name in [(ark_pocc_diff, "ARK-POCC"), (ark_hasv_diff, "ARK-HASV")]:
            print(f"\n{name} difference = {diff}")
            if diff % 26 == 0:
                print(f"  → Divisible by 26! ({diff // 26} × 26)")
            if diff % 121 == 0:
                print(f"  → Divisible by 121! ({diff // 121} × 121)")
            if diff % 138 == 0:
                print(f"  → Divisible by 138! ({diff // 138} × 138)")
            if diff % 676 == 0:
                print(f"  → Divisible by 676! ({diff // 676} × 676)")

def analyze_supply_2028():
    """Analyze the supply number 2028"""
    print(f"\n{'='*80}")
    print(f"SUPPLY ANALYSIS: 2,028")
    print(f"{'='*80}")

    supply = 2028

    print(f"\n1. BASIC PROPERTIES")
    print(f"   2028 = ", end="")
    factorize(2028)

    print(f"\n2. DIGIT SUM")
    digit_sum = 2 + 0 + 2 + 8
    print(f"   2 + 0 + 2 + 8 = {digit_sum}")

    print(f"\n3. MODULAR TESTS")
    print(f"   2028 mod 26 = {2028 % 26}")
    print(f"   2028 mod 121 = {2028 % 121}")
    print(f"   2028 mod 138 = {2028 % 138}")
    print(f"   2028 mod 676 = {2028 % 676}")

    print(f"\n4. DIVISIBILITY")
    if 2028 % 26 == 0:
        print(f"   2028 / 26 = {2028 // 26}")
    if 2028 % 121 == 0:
        print(f"   2028 / 121 = {2028 // 121}")
    if 2028 % 138 == 0:
        print(f"   2028 / 138 = {2028 // 138}")
    if 2028 % 676 == 0:
        print(f"   2028 / 676 = {2028 // 676}")

    print(f"\n5. CONNECTION TO 6,268 DAYS")
    print(f"   Genesis to March 3, 2026 = 6,268 days")
    print(f"   6,268 - 2,028 = {6268 - 2028}")
    print(f"   6,268 / 2,028 = {6268 / 2028:.4f}")
    print(f"   2,028 / 676 = {2028 / 676:.4f}")

def analyze_timestamps():
    """Analyze the T+7 and T+21 timestamps"""
    print(f"\n{'='*80}")
    print(f"TIMESTAMP ANALYSIS")
    print(f"{'='*80}")

    from datetime import datetime, timedelta

    issue_date = datetime(2026, 2, 4)
    t_plus_7 = issue_date + timedelta(days=7)
    t_plus_21 = issue_date + timedelta(days=21)
    march_3 = datetime(2026, 3, 3)

    print(f"\nIssue Date:  {issue_date.strftime('%Y-%m-%d')}")
    print(f"T+7:         {t_plus_7.strftime('%Y-%m-%d')} (February 11, 2026)")
    print(f"T+21:        {t_plus_21.strftime('%Y-%m-%d')} (February 25, 2026)")
    print(f"March 3:     {march_3.strftime('%Y-%m-%d')}")

    print(f"\nDAYS UNTIL MARCH 3, 2026:")
    print(f"From issue date: {(march_3 - issue_date).days} days")
    print(f"From T+7:        {(march_3 - t_plus_7).days} days")
    print(f"From T+21:       {(march_3 - t_plus_21).days} days")

    print(f"\nPATTERN ANALYSIS:")
    print(f"T+7 to T+21:     {21 - 7} = 14 days (2 weeks)")
    print(f"T+21 to March 3: {(march_3 - t_plus_21).days} days")

    # Check if these numbers have special properties
    print(f"\nNUMBER PROPERTIES:")
    for num, name in [(7, "T+7"), (21, "T+21"), (14, "T+7 to T+21 span")]:
        print(f"\n{name} = {num}")
        print(f"  Factorization: ", end="")
        factorize(num)
        print(f"  mod 26 = {num % 26}")
        if num % 7 == 0:
            print(f"  Divisible by 7")

def main():
    """Main analysis"""
    print("\n" + "="*80)
    print("ARK TOKEN COMPREHENSIVE ANALYSIS")
    print("Issue Date: 2026-02-04")
    print("Supply: 2,028")
    print("="*80)

    # Analyze all three addresses
    ark_data = analyze_address(ARK, "ARK")
    pocc_data = analyze_address(POCC, "POCC (GENESIS)")
    hasv_data = analyze_address(HASV, "HASV (EXODUS)")

    # Compare them
    compare_addresses(ark_data, pocc_data, hasv_data)

    # Analyze supply
    analyze_supply_2028()

    # Analyze timestamps
    analyze_timestamps()

    # Final assessment
    print(f"\n{'='*80}")
    print(f"FINAL ASSESSMENT")
    print(f"{'='*80}")
    print(f"""
The ARK token shows several interesting properties:

1. MATHEMATICAL CONNECTIONS
   - Character sums, diagonal sums, and modular properties can be compared
     to POCC/HASV patterns
   - Check if differences are multiples of 26, 121, 138, or 676

2. SUPPLY: 2,028
   - Could reference year 2028
   - Digit sum = 12 (biblical completeness number)
   - Mathematical relationship to 676?

3. TIMESTAMPS
   - T+7:  February 11, 2026
   - T+21: February 25, 2026
   - Both BEFORE March 3, 2026 (the predicted date)

4. MESSAGE CONTENT
   - "Proof of Existence" - echoes our mathematical proof methodology
   - "Verification procedure" - matches our research approach
   - "easter egg" signature - confirms deliberate design
   - "Architect" - references the creator/designer

5. BIBLICAL REFERENCE
   - ARK = Noah's Ark (salvation vessel)
   - ARK = Ark of the Covenant (sacred container)
   - Connects to Genesis/Exodus theme

CONCLUSION:
This token appears to be deliberately created with:
- Mathematical encoding (to be verified above)
- Biblical symbolism (ARK, Genesis/Exodus connection)
- Temporal coordination (T+7, T+21 before March 3)
- Meta-commentary on verification and proof

Recommend: Check if issuer address has POCC/HASV-like patterns.
""")

if __name__ == "__main__":
    main()
