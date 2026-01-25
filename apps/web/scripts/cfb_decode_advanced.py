#!/usr/bin/env python3
"""
CFB Puzzle - Advanced Decoding
==============================

Building on initial analysis:
1. 40 unique numbers
2. 27 appears at position 37
3. IOTA trytes: RKCWNDB9FFPUNVGICJWPSADNOGHSTCFPQEFOR9AL
"""

import hashlib

PUZZLE = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

def decode_as_permutation():
    """Maybe it's indices into something?"""
    print("=" * 70)
    print("METHOD: Permutation/Index Mapping")
    print("=" * 70)

    # If these are indices 1-100 selecting 40 items...
    # Maybe they point to positions in a reference text?

    # Classic reference: "The quick brown fox..."
    reference = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    print(f"\nReference text: {reference}")

    # Use mod length
    result = ''.join(reference[n % len(reference)] for n in PUZZLE)
    print(f"Mapped to reference: {result}")

    # Numbers as positions, sorted order reveals message?
    sorted_with_idx = sorted(enumerate(PUZZLE), key=lambda x: x[1])
    positions = [x[0] for x in sorted_with_idx]
    print(f"\nSorted indices: {positions}")

    # The position of each number reveals order
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if max(positions) < 40:
        order_message = ''.join(alphabet[p % 26] for p in positions)
        print(f"Positions as letters: {order_message}")


def decode_as_grid():
    """Maybe it's coordinates in a 10x10 grid?"""
    print("\n" + "=" * 70)
    print("METHOD: 10x10 Grid Coordinates")
    print("=" * 70)

    # Numbers 1-100 can map to 10x10 grid
    # row = (n-1) // 10, col = (n-1) % 10
    coords = []
    for n in PUZZLE:
        row = (n - 1) // 10
        col = (n - 1) % 10
        coords.append((row, col))
        print(f"{n:3d} -> ({row}, {col})")

    print(f"\nCoordinates: {coords}")


def decode_as_binary_positions():
    """Maybe the numbers represent bit positions?"""
    print("\n" + "=" * 70)
    print("METHOD: Binary/Bit Positions")
    print("=" * 70)

    # Create a 100-bit number with 1s at puzzle positions
    bitmap = 0
    for n in PUZZLE:
        bitmap |= (1 << n)

    print(f"As binary (last 100 bits):")
    binary_str = bin(bitmap)[2:].zfill(100)
    print(binary_str)

    # Convert to hex
    hex_str = hex(bitmap)[2:]
    print(f"\nAs hex: {hex_str}")

    # Check if it's a valid private key length (64 chars = 256 bits)
    print(f"Hex length: {len(hex_str)}")


def decode_sorted_values():
    """Sort and decode"""
    print("\n" + "=" * 70)
    print("METHOD: Sorted Order Decoding")
    print("=" * 70)

    # Sort numbers but keep track of original positions
    indexed = list(enumerate(PUZZLE))
    sorted_by_value = sorted(indexed, key=lambda x: x[1])

    # Original positions in sorted order
    positions_in_sorted_order = [x[0] for x in sorted_by_value]
    print(f"Original positions when sorted by value:")
    print(positions_in_sorted_order)

    # As mod 26
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text = ''.join(alphabet[p % 26] for p in positions_in_sorted_order)
    print(f"As letters: {text}")


def decode_differences():
    """Decode using differences between numbers"""
    print("\n" + "=" * 70)
    print("METHOD: Difference Decoding")
    print("=" * 70)

    diffs = [PUZZLE[i+1] - PUZZLE[i] for i in range(len(PUZZLE)-1)]
    print(f"Differences: {diffs}")

    # Absolute differences
    abs_diffs = [abs(d) for d in diffs]
    print(f"Absolute: {abs_diffs}")

    # mod 26
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text_diff = ''.join(alphabet[d % 26] for d in abs_diffs)
    print(f"As letters (mod 26): {text_diff}")

    # mod 27
    tryte_alpha = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text_27 = ''.join(tryte_alpha[d % 27] for d in abs_diffs)
    print(f"As trytes (mod 27): {text_27}")


def decode_pairs_as_chars():
    """Pair up numbers to form ASCII codes?"""
    print("\n" + "=" * 70)
    print("METHOD: Paired Numbers as ASCII")
    print("=" * 70)

    # Pairs as two-digit numbers
    for i in range(0, len(PUZZLE)-1, 2):
        a, b = PUZZLE[i], PUZZLE[i+1]
        # Different combinations
        n1 = a * 10 + b  # Not useful if > 127
        n2 = a + b  # Sum
        n3 = abs(a - b)  # Difference
        # print(f"({a}, {b}) -> sum={n2}, diff={n3}")

    # Sum of pairs as ASCII
    sums = [PUZZLE[i] + PUZZLE[i+1] for i in range(0, len(PUZZLE)-1, 2)]
    print(f"Sums of pairs: {sums}")
    ascii_from_sums = ''.join(chr(s) if 32 <= s <= 126 else '?' for s in sums)
    print(f"Sums as ASCII: {ascii_from_sums}")


def decode_xor_chain():
    """XOR consecutive numbers"""
    print("\n" + "=" * 70)
    print("METHOD: XOR Chain")
    print("=" * 70)

    xor_chain = []
    result = PUZZLE[0]
    xor_chain.append(result)
    for i in range(1, len(PUZZLE)):
        result = result ^ PUZZLE[i]
        xor_chain.append(result)

    print(f"XOR chain: {xor_chain}")
    print(f"Final XOR: {result}")

    # mod 27
    tryte_alpha = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text = ''.join(tryte_alpha[x % 27] for x in xor_chain)
    print(f"As trytes: {text}")


def decode_position_37():
    """27 is at position 37 - maybe significant?"""
    print("\n" + "=" * 70)
    print("METHOD: Position 37 Analysis")
    print("=" * 70)

    print(f"27 is at position 37 (0-indexed)")
    print(f"37 is a prime number!")
    print(f"37 + 27 = 64 (perfect for crypto!)")
    print(f"37 - 27 = 10")
    print(f"37 * 27 = {37 * 27} = 999!")

    # Split at position 37
    before_27 = PUZZLE[:37]
    after_27 = PUZZLE[38:]  # Skip the 27
    print(f"\nNumbers before 27: {len(before_27)} items")
    print(f"Numbers after 27: {len(after_27)} items")

    # mod 27 of each part
    tryte_alpha = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    before_trytes = ''.join(tryte_alpha[n % 27] for n in before_27)
    after_trytes = ''.join(tryte_alpha[n % 27] for n in after_27)
    print(f"Before 27 as trytes: {before_trytes}")
    print(f"After 27 as trytes: {after_trytes}")


def test_as_bitcoin_key():
    """Test if decoded values could be a Bitcoin key"""
    print("\n" + "=" * 70)
    print("METHOD: Bitcoin Key Test")
    print("=" * 70)

    try:
        import ecdsa
        from ecdsa import SECP256k1
        import base58

        def private_to_address(priv_hex):
            priv_bytes = bytes.fromhex(priv_hex)
            sk = ecdsa.SigningKey.from_string(priv_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()
            pub = b'\x04' + vk.to_string()

            sha = hashlib.sha256(pub).digest()
            ripe = hashlib.new('ripemd160', sha).digest()
            versioned = b'\x00' + ripe
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            return base58.b58encode(versioned + checksum).decode()

        # Method 1: Numbers as hex bytes directly
        hex_key = ''.join(f'{n:02x}' for n in PUZZLE[:32])
        print(f"First 32 numbers as hex: {hex_key}")
        addr = private_to_address(hex_key)
        print(f"Bitcoin address: {addr}")

        # Method 2: mod 256 as bytes
        mod256 = bytes(n % 256 for n in PUZZLE[:32])
        hex_key2 = mod256.hex()
        addr2 = private_to_address(hex_key2)
        print(f"mod 256 as key: {addr2}")

        # Method 3: SHA256 of the full sequence
        seq_str = ','.join(str(n) for n in PUZZLE)
        hash_key = hashlib.sha256(seq_str.encode()).hexdigest()
        addr3 = private_to_address(hash_key)
        print(f"SHA256 of sequence: {addr3}")

    except ImportError:
        print("ecdsa/base58 not installed")


def main():
    decode_as_permutation()
    decode_as_grid()
    decode_as_binary_positions()
    decode_sorted_values()
    decode_differences()
    decode_pairs_as_chars()
    decode_xor_chain()
    decode_position_37()
    test_as_bitcoin_key()

    print("\n" + "=" * 70)
    print("MOST INTERESTING FINDINGS")
    print("=" * 70)
    print("""
1. 27 at position 37: 37 * 27 = 999 (!)
2. 37 + 27 = 64 (crypto significant)
3. IOTA Trytes: RKCWNDB9FFPUNVGICJWPSADNOGHSTCFPQEFOR9AL
4. The sequence seems deliberately constructed

Hypothesis: CFB is testing if Grok can recognize:
- IOTA/ternary encoding
- A specific cryptographic pattern
- Or something entirely different...
""")


if __name__ == "__main__":
    main()
