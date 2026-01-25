#!/usr/bin/env python3
"""
CFB IOTA Decode - Testing the Trytes
====================================

The sequence decodes to IOTA trytes: RKCWNDB9FFPUNVGICJWPSADNOGHSTCFPQEFOR9AL
Let's test this as an IOTA seed and explore connections.
"""

import hashlib

PUZZLE = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

TRYTE_ALPHABET = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def get_trytes():
    """Convert to IOTA trytes"""
    mod27 = [n % 27 for n in PUZZLE]
    return ''.join(TRYTE_ALPHABET[m] for m in mod27)

def analyze_trytes():
    print("=" * 70)
    print("CFB IOTA TRYTE ANALYSIS")
    print("=" * 70)

    trytes = get_trytes()
    print(f"\nTrytes: {trytes}")
    print(f"Length: {len(trytes)}")

    # IOTA seeds are 81 trytes
    # 40 trytes = half + half = 80 + 1 checksum?

    # Method 1: Double it
    doubled = trytes * 2
    print(f"\nDoubled (80 chars): {doubled}")
    print(f"With '9' checksum: {doubled}9")

    # Method 2: The 9s in the trytes
    nine_positions = [i for i, c in enumerate(trytes) if c == '9']
    print(f"\n'9' appears at positions: {nine_positions}")
    print(f"(In IOTA, 9 represents 0 in ternary)")

    # Position 7 and 37 have '9'
    if 7 in nine_positions:
        print("Position 7: This maps to number 81 (3^4, ternary power!)")
    if 37 in nine_positions:
        print("Position 37: This maps to number 27 (3^3, ternary power!)")

    # Both 81 and 27 are powers of 3!
    print("\n⚠️  81 = 3^4 and 27 = 3^3 - both map to '9' (zero)!")
    print("This is likely intentional ternary significance!")


def analyze_999_connection():
    print("\n" + "=" * 70)
    print("THE 999 CONNECTION")
    print("=" * 70)

    print("""
Position of 27 in sequence: 37
37 * 27 = 999

999 in different bases:
- Decimal: 999
- Binary: 1111100111
- Ternary: 1101000 (NOT balanced)
- Hex: 3E7

999 = 27 * 37 = 3^3 * 37

In IOTA:
- 999...999 (81 nines) is the "null address"
- It represents zero value

Is CFB hinting at the null/zero concept?
""")


def analyze_grid_pattern():
    print("\n" + "=" * 70)
    print("GRID PATTERN ANALYSIS")
    print("=" * 70)

    # The numbers form a specific pattern in 10x10 grid
    grid = [[' ' for _ in range(10)] for _ in range(10)]

    for i, n in enumerate(PUZZLE):
        row = (n - 1) // 10
        col = (n - 1) % 10
        grid[row][col] = chr(65 + i) if i < 26 else chr(97 + i - 26)

    print("Grid visualization (letters show order in sequence):")
    print("   0 1 2 3 4 5 6 7 8 9")
    print("  " + "-" * 21)
    for i, row in enumerate(grid):
        print(f"{i} |{' '.join(row)}|")
    print("  " + "-" * 21)


def check_special_numbers():
    print("\n" + "=" * 70)
    print("SPECIAL NUMBER ANALYSIS")
    print("=" * 70)

    # Numbers that are powers of 3
    powers_of_3 = [3, 9, 27, 81]
    found_powers = [n for n in PUZZLE if n in powers_of_3]
    print(f"Powers of 3 in sequence: {found_powers}")

    # Their positions
    for p in found_powers:
        pos = PUZZLE.index(p)
        print(f"  {p} (3^{[0,1,2,3,4][powers_of_3.index(p)+1]}) at position {pos}")

    # Products of found powers
    if 3 in PUZZLE and 27 in PUZZLE:
        pos_3 = PUZZLE.index(3)
        pos_27 = PUZZLE.index(27)
        print(f"\n3 at position {pos_3}, 27 at position {pos_27}")
        print(f"Position difference: {abs(pos_27 - pos_3)}")
        print(f"Position product: {pos_3 * pos_27}")

    if 81 in PUZZLE:
        pos_81 = PUZZLE.index(81)
        print(f"81 at position {pos_81}")


def decode_message_attempt():
    print("\n" + "=" * 70)
    print("MESSAGE DECODING ATTEMPTS")
    print("=" * 70)

    trytes = get_trytes()

    # Read as words?
    # RKCWNDB9FFPUNVGICJWPSADNOGHSTCFPQEFOR9AL

    # Split at 9s (which represent spaces/zeros)
    parts = trytes.split('9')
    print(f"Split at '9': {parts}")

    # Common words in crypto:
    # KEY, SEED, IOTA, QUBIC, CFB, etc.

    # Check for embedded words
    keywords = ['KEY', 'SEED', 'IOTA', 'CFB', 'NXT', 'BTC', 'FOR', 'AND', 'THE']
    for word in keywords:
        if word in trytes:
            pos = trytes.index(word)
            print(f"Found '{word}' at position {pos}")

    # "FOR" is in there at position 34!
    # "AL" at the end (like a name? Algorithm?)

    print("\nPossible interpretation:")
    print("RKCWNDB | 9 | FFPUNVGICJWPSADNOGHSTCFPQE | FOR | 9 | AL")
    print("         ^                               ^^^       ^^")
    print("        (0)                             (for)    (AL?)")


def try_as_seed():
    print("\n" + "=" * 70)
    print("TESTING AS CRYPTO SEEDS")
    print("=" * 70)

    trytes = get_trytes()

    # As Qubic seed (55 chars)
    qubic_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mod26 = [n % 26 for n in PUZZLE]
    qubic_chars = ''.join(qubic_alphabet[m] for m in mod26)

    print(f"As Qubic format (40 chars): {qubic_chars}")

    # Need 55 chars for Qubic
    # 40 + 15 = 55
    extended = qubic_chars + qubic_chars[:15]
    print(f"Extended to 55: {extended}")

    # Calculate hash
    hash_of_trytes = hashlib.sha256(trytes.encode()).hexdigest()
    print(f"\nSHA256 of trytes: {hash_of_trytes}")

    # Could this hash be a private key?
    print(f"Length: {len(hash_of_trytes)} (64 = valid Bitcoin private key length)")


def main():
    analyze_trytes()
    analyze_999_connection()
    analyze_grid_pattern()
    check_special_numbers()
    decode_message_attempt()
    try_as_seed()

    print("\n" + "=" * 70)
    print("SUMMARY OF KEY FINDINGS")
    print("=" * 70)
    print("""
🔑 KEY DISCOVERIES:

1. TERNARY SIGNIFICANCE:
   - 81 (3^4) and 27 (3^3) both map to '9' (zero in ternary)
   - This is clearly intentional IOTA/ternary encoding

2. THE 999 PATTERN:
   - 37 * 27 = 999
   - 999 is the "null" in IOTA (like 0x00...00 in Bitcoin)

3. FOUND WORD "FOR":
   - "FOR" appears in the trytes at position 34
   - Sequence ends with "9AL" (For ALL? Algorithm?)

4. TRYTES: RKCWNDB9FFPUNVGICJWPSADNOGHSTCFPQEFOR9AL
   - 40 characters (half of 80, needs +1 for IOTA seed)
   - Two '9's at positions 7 and 37

HYPOTHESIS:
CFB is demonstrating ternary encoding and/or
testing if AI (Grok) can recognize IOTA patterns.

The message might be:
"[something] FOR ALL" or related to IOTA's null address concept.
""")


if __name__ == "__main__":
    main()
