#!/usr/bin/env python3
"""
Analyze other prefix families (1CA, 1CB, 1CC, 1CD, 1CE, etc.)
to see if there are other mathematical families we're missing
"""

import json
from pathlib import Path
from collections import defaultdict

def load_all_addresses():
    """Load all addresses from datasets"""
    print("=" * 80)
    print("LOADING ALL ADDRESSES")
    print("=" * 80)

    all_addresses = []

    files = [
        "../public/data/bitcoin-private-keys.json",
        "../public/data/matrix-addresses.json",
        "../public/data/bitcoin-derived-addresses.json",
        "../public/data/interesting-addresses.json",
    ]

    for file_path in files:
        path = Path(file_path)
        if path.exists():
            print(f"\nLoading: {path.name}")
            with open(path) as f:
                data = json.load(f)

            if isinstance(data, list):
                all_addresses.extend(data)
                print(f"  Added: {len(data):,} addresses")
            elif isinstance(data, dict):
                # Try different keys
                for key in ['addresses', 'records', 'data']:
                    if key in data and isinstance(data[key], list):
                        all_addresses.extend(data[key])
                        print(f"  Added: {len(data[key]):,} addresses (from '{key}')")
                        break

    print(f"\nTotal addresses loaded: {len(all_addresses):,}")
    return all_addresses

def analyze_prefix_distribution(addresses):
    """Analyze distribution of 3-character prefixes"""
    print("\n" + "=" * 80)
    print("PREFIX DISTRIBUTION ANALYSIS (3-char)")
    print("=" * 80)

    prefix_counts = defaultdict(int)
    prefix_byte_sums = defaultdict(list)

    for addr_data in addresses:
        if isinstance(addr_data, dict):
            address = addr_data.get('address', '')
            hash160 = addr_data.get('hash160', '')
        else:
            continue

        if len(address) >= 3 and address.startswith('1'):
            prefix = address[:3]
            prefix_counts[prefix] += 1

            # Calculate byte sum if we have hash160
            if hash160:
                try:
                    byte_sum = sum(bytes.fromhex(hash160))
                    prefix_byte_sums[prefix].append(byte_sum)
                except:
                    pass

    # Sort by count
    sorted_prefixes = sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\nTop 50 most common 3-character prefixes:")
    print(f"{'Prefix':<8} {'Count':<10} {'Avg ByteSum':<12} {'2299 Count':<12}")
    print("-" * 80)

    for prefix, count in sorted_prefixes[:50]:
        sums = prefix_byte_sums[prefix]
        avg_sum = sum(sums) / len(sums) if sums else 0
        count_2299 = sum(1 for s in sums if s == 2299)

        marker = ""
        if prefix.startswith("1C"):
            marker = " ⭐" if count > 50 else " ←"

        print(f"{prefix:<8} {count:<10,} {avg_sum:<12.1f} {count_2299:<12}{marker}")

    return prefix_counts, prefix_byte_sums

def analyze_1c_family(addresses):
    """Deep dive into all 1C* prefixes"""
    print("\n" + "=" * 80)
    print("1C* FAMILY ANALYSIS")
    print("=" * 80)

    c_prefixes = defaultdict(list)

    for addr_data in addresses:
        if isinstance(addr_data, dict):
            address = addr_data.get('address', '')
            hash160 = addr_data.get('hash160', '')
        else:
            continue

        if len(address) >= 3 and address.startswith('1C'):
            prefix = address[:3]

            # Get first byte and byte sum
            first_byte = None
            byte_sum = None
            if hash160:
                try:
                    hash_bytes = bytes.fromhex(hash160)
                    first_byte = hash_bytes[0]
                    byte_sum = sum(hash_bytes)
                except:
                    pass

            c_prefixes[prefix].append({
                'address': address,
                'hash160': hash160,
                'first_byte': first_byte,
                'byte_sum': byte_sum,
            })

    print(f"\nAll 1C* prefix families:")
    print(f"{'Prefix':<8} {'Total':<8} {'0x7b':<6} {'Sum=2299':<10} {'Both':<6}")
    print("-" * 80)

    for prefix in sorted(c_prefixes.keys()):
        addrs = c_prefixes[prefix]
        total = len(addrs)

        count_0x7b = sum(1 for a in addrs if a['first_byte'] == 0x7b)
        count_2299 = sum(1 for a in addrs if a['byte_sum'] == 2299)
        count_both = sum(1 for a in addrs if a['first_byte'] == 0x7b and a['byte_sum'] == 2299)

        marker = ""
        if count_both > 0:
            marker = f" ⭐ {count_both} in 0x7b family!"

        print(f"{prefix:<8} {total:<8,} {count_0x7b:<6} {count_2299:<10} {count_both:<6}{marker}")

        # Show the special ones
        if count_both > 0:
            print(f"\n  Special addresses in {prefix} family (0x7b + 2299):")
            for addr in addrs:
                if addr['first_byte'] == 0x7b and addr['byte_sum'] == 2299:
                    print(f"    {addr['address']}")
            print()

    return c_prefixes

def find_other_families(addresses):
    """Look for other mathematical families (not 0x7b)"""
    print("\n" + "=" * 80)
    print("SEARCHING FOR OTHER MATHEMATICAL FAMILIES")
    print("=" * 80)

    # Group by first byte
    first_byte_groups = defaultdict(list)

    for addr_data in addresses:
        if isinstance(addr_data, dict):
            hash160 = addr_data.get('hash160', '')
            if hash160:
                try:
                    first_byte = bytes.fromhex(hash160)[0]
                    byte_sum = sum(bytes.fromhex(hash160))
                    first_byte_groups[first_byte].append({
                        'address': addr_data.get('address', ''),
                        'hash160': hash160,
                        'byte_sum': byte_sum,
                    })
                except:
                    pass

    print(f"\nLooking for other first_byte + byte_sum families...")
    print(f"(Similar to 0x7b family)\n")

    # Look for first bytes that have multiple addresses with same byte sum
    byte_sum_families = []

    for first_byte, addrs in sorted(first_byte_groups.items()):
        # Count byte sums
        sum_counts = defaultdict(list)
        for addr in addrs:
            sum_counts[addr['byte_sum']].append(addr)

        # Find sums with multiple addresses
        for byte_sum, sum_addrs in sum_counts.items():
            if len(sum_addrs) >= 3:  # At least 3 addresses with same sum
                byte_sum_families.append({
                    'first_byte': first_byte,
                    'byte_sum': byte_sum,
                    'count': len(sum_addrs),
                    'addresses': sum_addrs,
                })

    # Sort by count
    byte_sum_families.sort(key=lambda x: x['count'], reverse=True)

    print(f"Found {len(byte_sum_families)} potential families (3+ members):\n")
    print(f"{'First Byte':<12} {'Byte Sum':<10} {'Count':<8} {'Sample Addresses':<40}")
    print("-" * 100)

    for family in byte_sum_families[:20]:  # Top 20
        first = family['first_byte']
        bsum = family['byte_sum']
        count = family['count']

        # Get first 2 addresses as samples
        samples = family['addresses'][:2]
        sample_str = ', '.join(a['address'][:15] + '...' for a in samples)

        marker = ""
        if first == 0x7b:
            marker = " ⭐ (our 0x7b family!)"
        elif count >= 5:
            marker = " ← Large family!"

        print(f"0x{first:02x} ({first:3d}) {bsum:<10,} {count:<8} {sample_str}{marker}")

    return byte_sum_families

def analyze_special_byte_sums(addresses):
    """Find other special byte sums (not just 2299)"""
    print("\n" + "=" * 80)
    print("SPECIAL BYTE SUM ANALYSIS")
    print("=" * 80)

    byte_sum_counts = defaultdict(int)

    for addr_data in addresses:
        if isinstance(addr_data, dict):
            hash160 = addr_data.get('hash160', '')
            if hash160:
                try:
                    byte_sum = sum(bytes.fromhex(hash160))
                    byte_sum_counts[byte_sum] += 1
                except:
                    pass

    # Look for byte sums that are products of special numbers
    special_numbers = [11, 19, 27, 33, 121]
    special_sums = []

    for byte_sum, count in byte_sum_counts.items():
        # Check if it's a product of special numbers
        is_special = False
        factorization = []

        # Simple factorization check
        temp = byte_sum
        for num in sorted(special_numbers, reverse=True):
            while temp % num == 0:
                factorization.append(num)
                temp //= num
                is_special = True

        if is_special and count >= 5:  # At least 5 addresses
            special_sums.append({
                'sum': byte_sum,
                'count': count,
                'factors': factorization,
            })

    special_sums.sort(key=lambda x: x['count'], reverse=True)

    print(f"\nByte sums that are products of special numbers (11, 19, 27, 33, 121):")
    print(f"{'Byte Sum':<12} {'Count':<8} {'Factorization':<30}")
    print("-" * 60)

    for item in special_sums[:30]:  # Top 30
        factors_str = ' × '.join(map(str, item['factors']))
        marker = " ⭐" if item['sum'] == 2299 else ""
        print(f"{item['sum']:<12,} {item['count']:<8} {factors_str:<30}{marker}")

    return special_sums

def generate_report(addresses):
    """Generate comprehensive analysis report"""
    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("=" * 80)

    prefix_counts, prefix_sums = analyze_prefix_distribution(addresses)
    c_families = analyze_1c_family(addresses)
    other_families = find_other_families(addresses)
    special_sums = analyze_special_byte_sums(addresses)

    report = {
        'date': '2026-01-10',
        'total_addresses': len(addresses),
        'total_prefixes': len(prefix_counts),
        '1c_families': {k: len(v) for k, v in c_families.items()},
        'other_families': [
            {
                'first_byte': f'0x{f["first_byte"]:02x}',
                'byte_sum': f['byte_sum'],
                'count': f['count'],
            }
            for f in other_families[:10]
        ],
        'special_sums': [
            {
                'sum': s['sum'],
                'count': s['count'],
                'factors': s['factors'],
            }
            for s in special_sums[:10]
        ],
    }

    output_file = Path("OTHER_FAMILIES_ANALYSIS.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Report saved: {output_file}")

    # Key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    print("\n1. 1C* Family:")
    for prefix in sorted(c_families.keys()):
        count = len(c_families[prefix])
        count_both = sum(1 for a in c_families[prefix] if a['first_byte'] == 0x7b and a['byte_sum'] == 2299)
        if count_both > 0:
            print(f"   {prefix}: {count:,} total, {count_both} in 0x7b family")

    print("\n2. Other Families Found:")
    for family in other_families[:5]:
        if family['first_byte'] != 0x7b:
            print(f"   0x{family['first_byte']:02x} + sum {family['byte_sum']:,}: {family['count']} addresses")

    print("\n3. Special Byte Sums:")
    for item in special_sums[:5]:
        if item['sum'] != 2299:
            factors_str = ' × '.join(map(str, item['factors']))
            print(f"   {item['sum']:,} = {factors_str}: {item['count']} addresses")

    return report

if __name__ == "__main__":
    print("🔍 ANALYZING OTHER PREFIX FAMILIES")
    print("=" * 80)

    addresses = load_all_addresses()
    report = generate_report(addresses)

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext: Review OTHER_FAMILIES_ANALYSIS.json for patterns")
