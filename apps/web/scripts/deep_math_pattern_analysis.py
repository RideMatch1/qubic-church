#!/usr/bin/env python3
"""
Deep Mathematical Pattern Analysis
===================================

Analyze block numbers for:
- Prime numbers
- CFB-related numbers (27, 121, 137, 576, 2299)
- Fibonacci relations
- Digit patterns
- Sum/product relationships
"""

import json
from pathlib import Path
from math import sqrt, gcd
from functools import reduce

# CFB Significant Numbers
CFB_NUMBERS = {
    3: "ternary base",
    9: "3²",
    11: "Qubic base",
    13: "13th (date pattern)",
    27: "3³ (ternary cube)",
    37: "prime",
    121: "11² (Qubic square)",
    127: "2⁷-1 (Mersenne prime, XOR key)",
    128: "2⁷ (matrix row size)",
    137: "fine structure constant",
    576: "24² (CFB signature)",
    2299: "CFB prime",
    16384: "layer size (128²)"
}

# Anti-pattern blocks
ANTI_PATTERN_BLOCKS = [1115, 2720, 5057, 5279, 11221, 12778, 12873, 13752, 19214, 21232, 22574, 40252]

# Anomaly blocks (from matrix position [22,22], etc.)
ANOMALY_BLOCKS = [2838, 2966, 3734, 7777, 8094, 2582, 2710, 3094, 3222, 3606, 3862, 3990, 4118]

# Block 264 (1CFB address)
SPECIAL_BLOCKS = [264, 9, 170]  # 9 = first Finney TX, 170 = first Satoshi-Finney TX


def is_prime(n):
    """Check if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factors(n):
    """Get prime factorization."""
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
    """Check if n is a Fibonacci number."""
    # n is Fibonacci iff 5n²+4 or 5n²-4 is a perfect square
    x1 = 5 * n * n + 4
    x2 = 5 * n * n - 4
    return is_perfect_square(x1) or is_perfect_square(x2)


def is_perfect_square(n):
    """Check if n is a perfect square."""
    if n < 0:
        return False
    root = int(sqrt(n))
    return root * root == n


def digit_sum(n):
    """Sum of digits."""
    return sum(int(d) for d in str(n))


def digit_product(n):
    """Product of digits (0 if any digit is 0)."""
    s = str(n)
    if '0' in s:
        return 0
    product = 1
    for d in s:
        product *= int(d)
    return product


def check_cfb_relations(n):
    """Check relationships to CFB numbers."""
    relations = []
    for cfb, meaning in CFB_NUMBERS.items():
        if n % cfb == 0:
            relations.append(f"divisible by {cfb} ({meaning})")
        if n + cfb in ANTI_PATTERN_BLOCKS or n - cfb in ANTI_PATTERN_BLOCKS:
            relations.append(f"±{cfb} = anti-pattern block")
        if n + cfb in ANOMALY_BLOCKS or n - cfb in ANOMALY_BLOCKS:
            relations.append(f"±{cfb} = anomaly block")
    return relations


def analyze_block(block):
    """Complete analysis of a block number."""
    analysis = {
        "block": block,
        "is_prime": is_prime(block),
        "prime_factors": prime_factors(block),
        "digit_sum": digit_sum(block),
        "digit_product": digit_product(block),
        "is_fibonacci": is_fibonacci(block),
        "is_perfect_square": is_perfect_square(block),
        "cfb_relations": check_cfb_relations(block)
    }

    # Check for special digit patterns
    s = str(block)
    if s == s[::-1]:
        analysis["palindrome"] = True
    if len(set(s)) == 1:
        analysis["repdigit"] = True

    # Matrix position
    layer = block // 16384
    remainder = block % 16384
    row = remainder // 128
    col = remainder % 128
    analysis["matrix_position"] = {"layer": layer, "row": row, "col": col}

    # Distance to nearest CFB number
    cfb_distances = {}
    for cfb in [27, 121, 137, 576, 2299]:
        nearest = round(block / cfb) * cfb
        cfb_distances[cfb] = block - nearest
    analysis["cfb_distances"] = cfb_distances

    return analysis


def find_relationships(blocks1, blocks2, name1, name2):
    """Find mathematical relationships between two sets of blocks."""
    relationships = []

    for b1 in blocks1:
        for b2 in blocks2:
            diff = abs(b1 - b2)
            ratio = b1 / b2 if b2 != 0 else 0

            # Check if difference is a CFB number
            if diff in CFB_NUMBERS:
                relationships.append(f"{name1}:{b1} - {name2}:{b2} = {diff} ({CFB_NUMBERS[diff]})")

            # Check if ratio is close to simple fraction
            if 0.99 < ratio < 1.01:
                relationships.append(f"{name1}:{b1} ≈ {name2}:{b2} (ratio {ratio:.4f})")
            elif abs(ratio - 2) < 0.01:
                relationships.append(f"{name1}:{b1} ≈ 2 × {name2}:{b2}")
            elif abs(ratio - 3) < 0.01:
                relationships.append(f"{name1}:{b1} ≈ 3 × {name2}:{b2}")
            elif abs(ratio - 0.5) < 0.01:
                relationships.append(f"{name1}:{b1} ≈ {name2}:{b2} / 2")

    return relationships


def main():
    print("=" * 70)
    print("DEEP MATHEMATICAL PATTERN ANALYSIS")
    print("=" * 70)

    results = {
        "anti_pattern_analysis": [],
        "anomaly_analysis": [],
        "relationships": [],
        "patterns_discovered": []
    }

    print("\n" + "-" * 70)
    print("ANTI-PATTERN BLOCKS (outside CFB modulo patterns)")
    print("-" * 70)

    for block in ANTI_PATTERN_BLOCKS:
        analysis = analyze_block(block)
        results["anti_pattern_analysis"].append(analysis)

        print(f"\nBlock {block}:")
        print(f"  Prime: {analysis['is_prime']}")
        print(f"  Factors: {analysis['prime_factors']}")
        print(f"  Digit sum: {analysis['digit_sum']}, product: {analysis['digit_product']}")
        print(f"  Matrix: Layer {analysis['matrix_position']['layer']}, Row {analysis['matrix_position']['row']}, Col {analysis['matrix_position']['col']}")
        if analysis['cfb_relations']:
            print(f"  CFB relations: {', '.join(analysis['cfb_relations'][:3])}")
        if analysis.get('palindrome'):
            print(f"  ⭐ PALINDROME")
        if analysis.get('repdigit'):
            print(f"  ⭐ REPDIGIT")

    print("\n" + "-" * 70)
    print("ANOMALY BLOCKS (from matrix positions)")
    print("-" * 70)

    for block in ANOMALY_BLOCKS:
        analysis = analyze_block(block)
        results["anomaly_analysis"].append(analysis)

        print(f"\nBlock {block}:")
        print(f"  Prime: {analysis['is_prime']}")
        print(f"  Factors: {analysis['prime_factors']}")
        print(f"  Digit sum: {analysis['digit_sum']}, product: {analysis['digit_product']}")
        print(f"  Matrix: Layer {analysis['matrix_position']['layer']}, Row {analysis['matrix_position']['row']}, Col {analysis['matrix_position']['col']}")

    # Find relationships
    print("\n" + "-" * 70)
    print("RELATIONSHIPS BETWEEN BLOCK SETS")
    print("-" * 70)

    rels = find_relationships(ANTI_PATTERN_BLOCKS, ANOMALY_BLOCKS, "Anti", "Anomaly")
    rels += find_relationships(ANTI_PATTERN_BLOCKS, SPECIAL_BLOCKS, "Anti", "Special")
    rels += find_relationships(ANOMALY_BLOCKS, SPECIAL_BLOCKS, "Anomaly", "Special")

    for rel in rels:
        print(f"  {rel}")
        results["relationships"].append(rel)

    # Pattern discovery
    print("\n" + "-" * 70)
    print("PATTERN DISCOVERIES")
    print("-" * 70)

    # Check for arithmetic sequences
    diffs_anti = [ANTI_PATTERN_BLOCKS[i+1] - ANTI_PATTERN_BLOCKS[i] for i in range(len(ANTI_PATTERN_BLOCKS)-1)]
    diffs_anom = [ANOMALY_BLOCKS[i+1] - ANOMALY_BLOCKS[i] for i in range(len(ANOMALY_BLOCKS)-1)]

    print(f"\nAnti-pattern block differences: {diffs_anti}")
    print(f"Anomaly block differences: {diffs_anom}")

    # Check for common divisors
    gcd_anti = reduce(gcd, ANTI_PATTERN_BLOCKS)
    gcd_anom = reduce(gcd, ANOMALY_BLOCKS)
    print(f"\nGCD of anti-pattern blocks: {gcd_anti}")
    print(f"GCD of anomaly blocks: {gcd_anom}")

    # Sum analysis
    sum_anti = sum(ANTI_PATTERN_BLOCKS)
    sum_anom = sum(ANOMALY_BLOCKS)
    print(f"\nSum of anti-pattern blocks: {sum_anti}")
    print(f"  Digit sum of sum: {digit_sum(sum_anti)}")
    print(f"  Sum mod 27: {sum_anti % 27}")
    print(f"  Sum mod 121: {sum_anti % 121}")

    print(f"\nSum of anomaly blocks: {sum_anom}")
    print(f"  Digit sum of sum: {digit_sum(sum_anom)}")
    print(f"  Sum mod 27: {sum_anom % 27}")
    print(f"  Sum mod 121: {sum_anom % 121}")

    # Cross-sum with XOR
    xor_anti = reduce(lambda x, y: x ^ y, ANTI_PATTERN_BLOCKS)
    xor_anom = reduce(lambda x, y: x ^ y, ANOMALY_BLOCKS)
    print(f"\nXOR of anti-pattern blocks: {xor_anti}")
    print(f"  Binary: {bin(xor_anti)}")
    print(f"\nXOR of anomaly blocks: {xor_anom}")
    print(f"  Binary: {bin(xor_anom)}")

    # Check if XOR relates to CFB numbers
    print(f"\n  XOR anti mod 27: {xor_anti % 27}")
    print(f"  XOR anti mod 121: {xor_anti % 121}")
    print(f"  XOR anti mod 127: {xor_anti % 127}")

    # Prime blocks
    prime_anti = [b for b in ANTI_PATTERN_BLOCKS if is_prime(b)]
    prime_anom = [b for b in ANOMALY_BLOCKS if is_prime(b)]

    print(f"\nPrime anti-pattern blocks: {prime_anti}")
    print(f"Prime anomaly blocks: {prime_anom}")

    # Discovery summary
    discoveries = []

    if prime_anti:
        discoveries.append(f"Prime anti-pattern blocks: {prime_anti}")

    if xor_anti % 27 == 0:
        discoveries.append(f"XOR of anti-pattern blocks is divisible by 27!")

    # Check for 128 (row size) patterns
    for b in ANTI_PATTERN_BLOCKS:
        if b % 128 == 0:
            discoveries.append(f"Block {b} is divisible by 128 (matrix row size)")

    results["patterns_discovered"] = discoveries

    # Save results
    script_dir = Path(__file__).parent
    output_path = script_dir / "DEEP_MATH_PATTERN_ANALYSIS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)

    print(f"""
1. Block 5279 is PRIME - unique among anti-pattern blocks
2. Anomaly block 7777 is a repdigit (7×1111)
3. Anti-pattern blocks sum to {sum_anti} (mod 27 = {sum_anti % 27})
4. XOR of anti-pattern blocks = {xor_anti} (mod 127 = {xor_anti % 127})
5. GCD of anti-patterns = {gcd_anti} (no common divisor)
6. Most anti-pattern blocks have factor 2 or 5 - low-entropy factors
""")


if __name__ == "__main__":
    main()
