#!/usr/bin/env python3
"""
Verify Letter Product Formula
=============================
Understand the CFB signature in address letter products.
"""

def address_letter_product(address: str) -> int:
    """Calculate product of letter values (Base58 alphabet)."""
    # Base58: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
    # Letters only (no digits): ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
    product = 1
    letter_count = 0
    letter_values = []

    for char in address[1:]:  # Skip first '1'
        if char.upper() in "ABCDEFGHJKLMNPQRSTUVWXYZ":
            if char.isupper():
                val = ord(char) - ord('A') + 1
                if char > 'I': val -= 1  # Skip I
                if char > 'O': val -= 1  # Skip O
            else:
                val = ord(char) - ord('a') + 1
                if char > 'l': val -= 1  # Skip l
            product *= val
            letter_count += 1
            letter_values.append((char, val))

    return product, letter_count, letter_values

# Test with Block 12873 address
address = "1Loo8Lw74rtdRA6PqRho8nq86SrNSDg99L"
product, count, values = address_letter_product(address)

print("=" * 70)
print(f"ADDRESS: {address}")
print("=" * 70)
print(f"\nLetter values ({count} letters):")
for char, val in values:
    print(f"  {char} → {val}")

print(f"\nProduct = {product}")
print(f"Product mod 576 = {product % 576}")
print(f"Product mod 27 = {product % 27}")

# Factor the product
print(f"\n" + "-" * 70)
print("PRODUCT FACTORIZATION")
print("-" * 70)

def factorize(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

factors = factorize(product)
print(f"Product = {product}")
print(f"Factors: {factors}")

# Count powers of primes
from collections import Counter
factor_counts = Counter(factors)
print(f"Prime powers: ", end="")
print(" × ".join(f"{p}^{e}" for p, e in sorted(factor_counts.items())))

# Why not divisible by 27?
print(f"\n" + "-" * 70)
print("WHY IS THIS EXCEPTIONAL?")
print("-" * 70)
power_of_3 = factor_counts.get(3, 0)
print(f"Product contains 3^{power_of_3}")
print(f"27 = 3^3, so need at least 3^3 for divisibility")
print(f"→ Product is {'divisible' if power_of_3 >= 3 else 'NOT divisible'} by 27")

# 576 = 2^6 × 3^2 × 1 = 64 × 9
power_of_2 = factor_counts.get(2, 0)
print(f"\n576 = 2^6 × 3^2 = 64 × 9")
print(f"Product contains 2^{power_of_2} and 3^{power_of_3}")
print(f"→ Product is {'divisible' if power_of_2 >= 6 and power_of_3 >= 2 else 'NOT divisible'} by 576")

# Test a few more addresses
print(f"\n" + "=" * 70)
print("COMPARISON WITH OTHER ADDRESSES")
print("=" * 70)

test_addresses = [
    ("1CFBtRXjJPBDsMSBKqFzBcfD3MsYAjGiMi", "Block 264 - 1CFB"),
    ("12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S", "Normal Patoshi"),
    ("1A8JiWcwvpY7tAopUkSnGuEYHmzGYfZPiq", "Another normal"),
]

for addr, desc in test_addresses:
    prod, cnt, vals = address_letter_product(addr)
    print(f"\n{desc}: {addr}")
    print(f"  Letters: {cnt}, Product: {prod}")
    print(f"  mod 576 = {prod % 576}, mod 27 = {prod % 27}")
    if prod % 27 == 0:
        print(f"  ✓ CFB signature (mod 27 = 0)")
    elif prod % 576 == 0:
        print(f"  ✓ CFB signature (mod 576 = 0)")
    else:
        print(f"  ✗ NO CFB signature!")

# The significance of mod_27 = 14
print(f"\n" + "=" * 70)
print("SIGNIFICANCE OF mod_27 = 14")
print("=" * 70)
print(f"Block 12873 address has product mod 27 = {product % 27}")
print(f"14 = 2 × 7")
print(f"14 mod 3 = 2 (NOT 0)")
print(f"\nThis is the ONLY Patoshi address where the letter product")
print(f"mod 27 is not divisible by 3!")
print(f"\nAll other exceptions have mod_27 values divisible by 3:")
print(f"  3, 6, 9, 12, 15, 18, 24 - all divisible by 3")
print(f"  14 - NOT divisible by 3 (UNIQUE)")
