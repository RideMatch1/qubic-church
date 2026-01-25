#!/usr/bin/env python3
"""
Analyze 1CF4's matrix position - Why index 439558?
Calculate row/col and check for special properties.
"""

import json
from pathlib import Path

def analyze_index_439558():
    """Reverse-engineer the mystery of index 439558"""

    index = 439558

    print("=" * 80)
    print("1CF4 MATRIX POSITION ANALYSIS")
    print("=" * 80)
    print(f"\nAddress: 1CF4DUoCirfAbU2E1gkwupaaaC1j1RDZGA")
    print(f"Index: {index}")
    print(f"Hash160: 7b51e4166322e898ff7f3406766fb377bd1b0d84")
    print(f"Byte sum: 2299 = 121 × 19")

    # Matrix dimensions
    matrix_size = 991  # Standard Anna Matrix is 991×991
    total_size = matrix_size * matrix_size

    print(f"\nMatrix size: {matrix_size} × {matrix_size} = {total_size:,}")

    # Calculate row/col
    row = index // matrix_size
    col = index % matrix_size

    print(f"\n" + "=" * 80)
    print("POSITION CALCULATION")
    print("=" * 80)
    print(f"Row: {row}")
    print(f"Col: {col}")
    print(f"Position: [{row}, {col}]")

    # Check if row/col have special properties
    print(f"\n" + "=" * 80)
    print("ROW ANALYSIS")
    print("=" * 80)
    print(f"Row {row}:")
    print(f"  - Is prime: {is_prime(row)}")
    print(f"  - Factors: {factorize(row)}")
    print(f"  - mod 121: {row % 121}")
    print(f"  - mod 19: {row % 19}")
    print(f"  - mod 27: {row % 27}")
    print(f"  - mod 11: {row % 11}")
    print(f"  - Binary: {bin(row)}")

    print(f"\n" + "=" * 80)
    print("COLUMN ANALYSIS")
    print("=" * 80)
    print(f"Col {col}:")
    print(f"  - Is prime: {is_prime(col)}")
    print(f"  - Factors: {factorize(col)}")
    print(f"  - mod 121: {col % 121}")
    print(f"  - mod 19: {col % 19}")
    print(f"  - mod 27: {col % 27}")
    print(f"  - mod 11: {col % 11}")
    print(f"  - Binary: {bin(col)}")

    # Check INDEX properties
    print(f"\n" + "=" * 80)
    print("INDEX ANALYSIS")
    print("=" * 80)
    print(f"Index {index}:")
    print(f"  - Is prime: {is_prime(index)}")
    print(f"  - Factors: {factorize(index)}")
    print(f"  - mod 121: {index % 121}")
    print(f"  - mod 19: {index % 19}")
    print(f"  - mod 27: {index % 27}")
    print(f"  - mod 11: {index % 11}")
    print(f"  - mod 2299: {index % 2299}")
    print(f"  - Binary: {bin(index)}")
    print(f"  - Hex: {hex(index)}")

    # Sum and product
    print(f"\n" + "=" * 80)
    print("ROW/COL RELATIONSHIPS")
    print("=" * 80)
    print(f"Row + Col: {row + col}")
    print(f"Row × Col: {row * col}")
    print(f"Row - Col: {row - col}")
    print(f"Row / Col: {row / col if col != 0 else 'N/A'}")
    print(f"(Row + Col) mod 121: {(row + col) % 121}")
    print(f"(Row + Col) mod 19: {(row + col) % 19}")
    print(f"(Row × Col) mod 2299: {(row * col) % 2299}")

    # Check distance from center
    center = matrix_size // 2
    dist_from_center = ((row - center)**2 + (col - center)**2)**0.5
    print(f"\nDistance from center [{center}, {center}]: {dist_from_center:.2f}")

    # Check if on diagonal
    print(f"\n" + "=" * 80)
    print("SPECIAL POSITIONS")
    print("=" * 80)
    print(f"On main diagonal: {row == col}")
    print(f"On anti-diagonal: {row + col == matrix_size - 1}")
    print(f"Distance from main diagonal: {abs(row - col)}")
    print(f"Distance from anti-diagonal: {abs((row + col) - (matrix_size - 1))}")

    # Load matrix to check surrounding indices
    print(f"\n" + "=" * 80)
    print("LOADING MATRIX DATA...")
    print("=" * 80)

    matrix_file = Path("public/data/matrix-addresses.json")
    if matrix_file.exists():
        with open(matrix_file) as f:
            matrix_data = json.load(f)

        # Find our address
        found = None
        for i, addr_data in enumerate(matrix_data):
            if i == index:
                found = addr_data
                break

        if found:
            print(f"\nFound at index {index}:")
            print(f"  Address: {found.get('address', 'N/A')}")
            print(f"  Method: {found.get('method', 'MISSING!')}")
            print(f"  Row: {found.get('row', 'MISSING!')}")
            print(f"  Col: {found.get('col', 'MISSING!')}")
            print(f"  Seed: {found.get('seed', 'MISSING!')}")

            # Check surrounding indices
            print(f"\n" + "=" * 80)
            print("SURROUNDING ADDRESSES (±5 indices)")
            print("=" * 80)
            for offset in range(-5, 6):
                idx = index + offset
                if 0 <= idx < len(matrix_data):
                    addr = matrix_data[idx]
                    marker = " ← TARGET" if offset == 0 else ""
                    print(f"  [{idx:6d}] {addr.get('address', 'N/A')[:20]}... "
                          f"sum={sum(bytes.fromhex(addr.get('hash160', '00'*20))) if 'hash160' in addr else '?'}{marker}")
    else:
        print(f"Matrix file not found: {matrix_file}")

    # Mathematical significance
    print(f"\n" + "=" * 80)
    print("MATHEMATICAL SIGNIFICANCE")
    print("=" * 80)

    # Check if 439558 appears in known sequences
    print(f"\nChecking {index} in known sequences:")
    print(f"  - Is Fibonacci: {is_fibonacci(index)}")
    print(f"  - Is Triangular: {is_triangular(index)}")
    print(f"  - Is Perfect Square: {int(index**0.5)**2 == index}")
    print(f"  - Is Perfect Cube: {int(index**(1/3))**3 == index}")

    # Sum of digits
    digit_sum = sum(int(d) for d in str(index))
    print(f"\n  - Sum of digits: {digit_sum}")
    print(f"  - Digital root: {digital_root(index)}")

    # Prime factorization special check
    factors = factorize(index)
    print(f"\n  - Prime factorization: {' × '.join(map(str, factors))}")
    if 121 in factors or 19 in factors or 11 in factors:
        print(f"  ⭐ CONTAINS SPECIAL FACTOR!")

    # Report
    print(f"\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print(f"\nIndex 439558 = {' × '.join(map(str, factors))}")
    print(f"Position: [{row}, {col}]")
    print(f"Special properties:")
    if index % 121 == 0 or index % 19 == 0:
        print(f"  ⭐ Index divisible by special numbers!")
    if row % 121 == 0 or row % 19 == 0 or col % 121 == 0 or col % 19 == 0:
        print(f"  ⭐ Row/Col divisible by special numbers!")
    if (row + col) % 121 == 0 or (row + col) % 19 == 0:
        print(f"  ⭐ Row+Col divisible by special numbers!")

    return {
        'index': index,
        'row': row,
        'col': col,
        'factors': factors,
        'mod_121': index % 121,
        'mod_19': index % 19,
    }

def is_prime(n):
    """Check if number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def factorize(n):
    """Prime factorization"""
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

def is_fibonacci(n):
    """Check if n is a Fibonacci number"""
    # A number is Fibonacci if one of (5*n^2 + 4) or (5*n^2 - 4) is a perfect square
    return is_perfect_square(5*n*n + 4) or is_perfect_square(5*n*n - 4)

def is_perfect_square(n):
    """Check if n is a perfect square"""
    root = int(n**0.5)
    return root * root == n

def is_triangular(n):
    """Check if n is a triangular number"""
    # Solve: n = k(k+1)/2 → k = (-1 + sqrt(1 + 8n)) / 2
    k = (-1 + (1 + 8*n)**0.5) / 2
    return k == int(k)

def digital_root(n):
    """Calculate digital root (repeated sum of digits)"""
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n

if __name__ == "__main__":
    result = analyze_index_439558()

    # Save results
    output_file = Path("1CF4_POSITION_ANALYSIS.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Results saved to: {output_file}")
