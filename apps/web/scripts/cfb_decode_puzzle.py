#!/usr/bin/env python3
"""
CFB Discord Puzzle Decoder
==========================

CFB posted: "Ask Grok to decode
45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39"

Testing various decoding methods including:
- mod 27 (CFB's favorite number, IOTA ternary: 3^3=27)
- mod 26 (alphabet)
- ASCII conversion
- Ternary systems
- Position mapping
"""

import hashlib
from typing import List

# The puzzle numbers from CFB
PUZZLE = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

def analyze_basics():
    """Basic statistical analysis"""
    print("=" * 70)
    print("CFB PUZZLE ANALYSIS")
    print("=" * 70)
    print(f"\nNumbers: {PUZZLE}")
    print(f"Count: {len(PUZZLE)}")
    print(f"Min: {min(PUZZLE)}, Max: {max(PUZZLE)}")
    print(f"Sum: {sum(PUZZLE)}")
    print(f"Sum mod 27: {sum(PUZZLE) % 27}")
    print(f"Sum mod 26: {sum(PUZZLE) % 26}")

    # Check for duplicates
    if len(PUZZLE) == len(set(PUZZLE)):
        print("All numbers are unique!")
    else:
        print(f"Duplicates found: {len(PUZZLE) - len(set(PUZZLE))}")

    # Differences
    diffs = [PUZZLE[i+1] - PUZZLE[i] for i in range(len(PUZZLE)-1)]
    print(f"\nDifferences between consecutive numbers:")
    print(diffs[:20], "...")


def decode_mod_27():
    """Decode using mod 27 (IOTA ternary base)"""
    print("\n" + "=" * 70)
    print("METHOD: mod 27 (IOTA/Ternary)")
    print("=" * 70)

    # Method 1: Direct mod 27
    mod27 = [n % 27 for n in PUZZLE]
    print(f"\nmod 27: {mod27}")

    # Map to alphabet (A=0, B=1, ... Z=25, space=26)
    alphabet_27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    try:
        text1 = ''.join(alphabet_27[m] for m in mod27)
        print(f"As alphabet (A=0): {text1}")
    except IndexError:
        print("Index error in alphabet mapping")

    # Map to alphabet (A=1, B=2, ... Z=26, 0=space)
    alphabet_27b = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    try:
        text2 = ''.join(alphabet_27b[m] for m in mod27)
        print(f"As alphabet (A=1): {text2}")
    except IndexError:
        print("Index error in alphabet mapping")

    # Ternary interpretation
    print("\nTernary (base 3) of mod 27 values:")
    for i, m in enumerate(mod27[:10]):
        tern = ""
        val = m
        for _ in range(3):
            tern = str(val % 3) + tern
            val //= 3
        print(f"  {PUZZLE[i]} -> {m} -> {tern}")


def decode_mod_26():
    """Decode using mod 26 (standard alphabet)"""
    print("\n" + "=" * 70)
    print("METHOD: mod 26 (Standard Alphabet)")
    print("=" * 70)

    mod26 = [n % 26 for n in PUZZLE]
    print(f"\nmod 26: {mod26}")

    # A=0
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text1 = ''.join(alphabet[m] for m in mod26)
    print(f"As alphabet (A=0): {text1}")

    # A=1 (shift by 1)
    text2 = ''.join(alphabet[(m-1) % 26] for m in mod26)
    print(f"As alphabet (A=1): {text2}")


def decode_ascii():
    """Try ASCII interpretation"""
    print("\n" + "=" * 70)
    print("METHOD: ASCII")
    print("=" * 70)

    # Direct ASCII (won't work for low numbers)
    print("\nDirect ASCII (most will be control chars):")
    ascii_chars = []
    for n in PUZZLE:
        if 32 <= n <= 126:
            ascii_chars.append(chr(n))
        else:
            ascii_chars.append('?')
    print(''.join(ascii_chars))

    # Shifted ASCII (+32, +48, +65)
    for offset in [32, 48, 65]:
        shifted = []
        for n in PUZZLE:
            char_code = n + offset
            if 32 <= char_code <= 126:
                shifted.append(chr(char_code))
            else:
                shifted.append('?')
        print(f"ASCII + {offset}: {''.join(shifted)}")


def decode_position_cipher():
    """Position-based cipher decoding"""
    print("\n" + "=" * 70)
    print("METHOD: Position Cipher")
    print("=" * 70)

    # Maybe the numbers represent positions in some text?
    # Or indices into alphabet based on position

    # XOR with position
    xor_pos = [(n ^ i) % 26 for i, n in enumerate(PUZZLE)]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text_xor = ''.join(alphabet[x] for x in xor_pos)
    print(f"XOR with position mod 26: {text_xor}")

    # Subtract position
    sub_pos = [(n - i) % 26 for i, n in enumerate(PUZZLE)]
    text_sub = ''.join(alphabet[s] for s in sub_pos)
    print(f"(n - position) mod 26: {text_sub}")

    # Add position
    add_pos = [(n + i) % 26 for i, n in enumerate(PUZZLE)]
    text_add = ''.join(alphabet[a] for a in add_pos)
    print(f"(n + position) mod 26: {text_add}")


def decode_iota_trytes():
    """IOTA uses trytes (base 27 with special alphabet)"""
    print("\n" + "=" * 70)
    print("METHOD: IOTA Trytes (Base 27)")
    print("=" * 70)

    # IOTA tryte alphabet: 9ABCDEFGHIJKLMNOPQRSTUVWXYZ
    TRYTE_ALPHABET = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    mod27 = [n % 27 for n in PUZZLE]
    trytes = ''.join(TRYTE_ALPHABET[m] for m in mod27)
    print(f"As IOTA trytes: {trytes}")

    # Try to decode as IOTA address or seed
    print(f"Length: {len(trytes)} (IOTA seeds are 81 trytes)")

    # Double the sequence to get to 80 trytes?
    if len(trytes) == 40:
        doubled = trytes * 2
        print(f"Doubled (80 chars): {doubled}")
        print(f"With checksum char: {doubled}9")


def decode_qubic_seed():
    """Try as Qubic seed format"""
    print("\n" + "=" * 70)
    print("METHOD: Qubic Seed")
    print("=" * 70)

    # Qubic uses 55-char seeds with uppercase letters
    QUBIC_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    mod26 = [n % 26 for n in PUZZLE]
    seed_attempt = ''.join(QUBIC_ALPHABET[m] for m in mod26)
    print(f"As Qubic seed chars: {seed_attempt}")
    print(f"Length: {len(seed_attempt)} (Qubic seeds are 55 chars)")

    # Extend to 55 chars?
    if len(seed_attempt) == 40:
        # Repeat first 15 chars
        extended = seed_attempt + seed_attempt[:15]
        print(f"Extended to 55: {extended}")


def decode_special_patterns():
    """Look for special patterns CFB might use"""
    print("\n" + "=" * 70)
    print("METHOD: Special CFB Patterns")
    print("=" * 70)

    # 27 is in the sequence! Position?
    if 27 in PUZZLE:
        pos_27 = PUZZLE.index(27)
        print(f"27 appears at position: {pos_27}")

    # Multiples of 27
    mult_27 = [n for n in PUZZLE if n % 27 == 0]
    print(f"Multiples of 27: {mult_27}")

    # Numbers that are 27 mod something
    for mod in [3, 9, 19, 27]:
        matches = [n for n in PUZZLE if n % mod == 0]
        print(f"Divisible by {mod}: {len(matches)} numbers")

    # Prime numbers in sequence
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    primes = [n for n in PUZZLE if is_prime(n)]
    print(f"Prime numbers: {primes}")
    print(f"Count of primes: {len(primes)}")


def decode_as_coordinates():
    """Maybe pairs of numbers are coordinates?"""
    print("\n" + "=" * 70)
    print("METHOD: Coordinate Pairs")
    print("=" * 70)

    # Pair up numbers
    pairs = [(PUZZLE[i], PUZZLE[i+1]) for i in range(0, len(PUZZLE)-1, 2)]
    print(f"As (x,y) pairs: {pairs[:10]}...")

    # If these are coordinates in a 10x10 grid...
    grid_10 = [(x % 10, y % 10) for x, y in pairs]
    print(f"mod 10 grid: {grid_10[:10]}...")


def decode_reverse_engineer():
    """Try to reverse engineer what Grok might find"""
    print("\n" + "=" * 70)
    print("METHOD: Reverse Engineering")
    print("=" * 70)

    # The fact that CFB asks to use "Grok" suggests LLM pattern recognition
    # Maybe it's a simple cipher that an LLM would recognize

    # Caesar cipher variants
    for shift in range(1, 27):
        mod27 = [(n - shift) % 27 for n in PUZZLE]
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        text = ''.join(alphabet[m] if m < 27 else '?' for m in mod27)
        if text.count(' ') >= 2 and text.count(' ') <= 10:  # Looks like words
            print(f"Caesar shift -{shift}: {text}")

    # Look for common words
    print("\nLooking for readable patterns with mod 26...")
    mod26 = [n % 26 for n in PUZZLE]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base_text = ''.join(alphabet[m] for m in mod26)
    print(f"Base mod 26: {base_text}")

    # With different starting points
    for start in range(26):
        shifted = ''.join(alphabet[(m + start) % 26] for m in mod26)
        # Check if it contains common letter patterns
        if any(word in shifted.lower() for word in ['the', 'and', 'for', 'are', 'but', 'not']):
            print(f"Shift +{start}: {shifted}")


def main():
    analyze_basics()
    decode_mod_27()
    decode_mod_26()
    decode_ascii()
    decode_position_cipher()
    decode_iota_trytes()
    decode_qubic_seed()
    decode_special_patterns()
    decode_as_coordinates()
    decode_reverse_engineer()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Key observations:
1. 40 numbers (not 27, 55, or 81 - common crypto lengths)
2. All numbers are unique
3. Range 3-98 (fits in mod 99, or 3 trits in base 3)
4. The number 27 itself appears in the sequence!
5. CFB specifically asked to use "Grok" - pattern recognition hint?

Most promising leads:
- mod 27 -> IOTA trytes
- mod 26 -> Standard alphabet
- The number 27 at position 37 might be significant
""")


if __name__ == "__main__":
    main()
