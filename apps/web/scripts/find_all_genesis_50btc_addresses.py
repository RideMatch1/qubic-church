#!/usr/bin/env python3
"""
FIND ALL GENESIS/PATOSHI 50 BTC ADDRESSES

We need to find the 10+ addresses with 50 BTC from early blocks
and analyze them the same way we analyzed 1CFB.

Known so far:
- Block 264: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg (0x79, sum 3,107)
- Need to find 9-10 more!
"""

import json
from pathlib import Path

# Known Genesis/Patoshi addresses with 50 BTC
# We need to find these from documentation or blockchain data
KNOWN_50BTC_ADDRESSES = {
    "Block 264": {
        "address": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
        "hash160": "79f8fa0da9e3d4dcb3ddff9802c10853a9e53a62",
        "block": 264,
        "date": "2009-01-13",
    },
    # Need to add the other 9-10!
}

def analyze_single_address(address_data):
    """Analyze a single 50 BTC address"""
    hash160 = address_data['hash160']
    hash_bytes = bytes.fromhex(hash160)

    first_byte = hash_bytes[0]
    byte_sum = sum(hash_bytes)

    # Factorize byte sum
    temp = byte_sum
    factors = []
    for divisor in [121, 19, 11, 7, 5, 3, 2]:
        while temp % divisor == 0:
            factors.append(divisor)
            temp //= divisor
    if temp > 1:
        factors.append(temp)

    return {
        **address_data,
        'first_byte': first_byte,
        'first_byte_hex': f'0x{first_byte:02x}',
        'byte_sum': byte_sum,
        'factors': factors,
        'div_by_121': byte_sum % 121 == 0,
        'div_by_19': byte_sum % 19 == 0,
        'div_by_2299': byte_sum % 2299 == 0,
    }

def search_documentation_for_addresses():
    """Search through documentation for Genesis/Patoshi addresses"""
    print("=" * 80)
    print("SEARCHING DOCUMENTATION FOR 50 BTC ADDRESSES")
    print("=" * 80)

    # Check patoshi-forensics doc
    patoshi_doc = Path("../../content/docs/en/03-results/21-patoshi-forensics.mdx")

    if patoshi_doc.exists():
        with open(patoshi_doc) as f:
            content = f.read()

        # Look for address patterns
        import re
        addresses = re.findall(r'1[a-zA-Z0-9]{25,34}', content)

        print(f"\nFound {len(addresses)} Bitcoin addresses in patoshi-forensics.mdx")

        # Filter to unique
        unique = list(set(addresses))
        print(f"Unique: {len(unique)}")

        return unique

    return []

def analyze_all_50btc_addresses():
    """Analyze all known 50 BTC addresses"""
    print("\n" + "=" * 80)
    print("ANALYZING ALL 50 BTC ADDRESSES")
    print("=" * 80)

    results = []

    for block_name, addr_data in KNOWN_50BTC_ADDRESSES.items():
        print(f"\n{block_name}:")
        analysis = analyze_single_address(addr_data)

        print(f"  Address: {analysis['address']}")
        print(f"  First byte: {analysis['first_byte_hex']} ({analysis['first_byte']})")
        print(f"  Byte sum: {analysis['byte_sum']:,}")

        if analysis['first_byte'] == 121:
            print(f"  ⭐ First byte = 121 (11²)!")

        if analysis['factors']:
            factors_str = ' × '.join(map(str, analysis['factors']))
            print(f"  Factorization: {factors_str}")

        results.append(analysis)

    return results

def find_pattern_across_addresses(results):
    """Find common patterns"""
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS")
    print("=" * 80)

    from collections import Counter

    first_bytes = Counter(r['first_byte'] for r in results)

    print(f"\nFirst byte distribution:")
    for byte_val, count in first_bytes.most_common():
        special = ""
        if byte_val == 121:
            special = " ⭐ (= 11²)"
        elif byte_val == 123:
            special = " (= 0x7b)"
        print(f"  0x{byte_val:02x} ({byte_val:3d}): {count} {special}")

    print(f"\nByte sum statistics:")
    sums = [r['byte_sum'] for r in results]
    print(f"  Min: {min(sums):,}")
    print(f"  Max: {max(sums):,}")
    print(f"  Mean: {sum(sums)/len(sums):.1f}")

    print(f"\nDivisibility:")
    div_121 = sum(1 for r in results if r['div_by_121'])
    div_19 = sum(1 for r in results if r['div_by_19'])
    div_2299 = sum(1 for r in results if r['div_by_2299'])

    print(f"  By 121: {div_121}/{len(results)}")
    print(f"  By 19: {div_19}/{len(results)}")
    print(f"  By 2299: {div_2299}/{len(results)}")

def main():
    print("🔍 FINDING ALL GENESIS/PATOSHI 50 BTC ADDRESSES")
    print("=" * 80)

    print("\nStep 1: Search documentation...")
    doc_addresses = search_documentation_for_addresses()

    print("\nStep 2: Analyze known 50 BTC addresses...")
    results = analyze_all_50btc_addresses()

    if len(results) > 1:
        print("\nStep 3: Find patterns...")
        find_pattern_across_addresses(results)

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    print("\n1. Find the OTHER 9-10 Patoshi/Genesis addresses with 50 BTC")
    print("   → Check blockchain explorers")
    print("   → Check early block coinbase addresses")
    print("\n2. Analyze ALL of them for patterns:")
    print("   → First bytes")
    print("   → Byte sums")
    print("   → Factorizations")
    print("\n3. Apply SAME reverse-engineering to find seeds:")
    print("   → Test all 23,765 seeds")
    print("   → With all methods (K12, step7, step13, etc.)")
    print("   → Match against hash160s")

    print("\n⭐ PRIORITY: First byte 0x79 (= 121) is SPECIAL!")
    print("   This is 11² = NXT constant!")
    print("   Search for seeds that produce 0x79 first byte!")

if __name__ == "__main__":
    main()
