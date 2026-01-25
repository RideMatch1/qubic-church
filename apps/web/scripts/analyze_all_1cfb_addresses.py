#!/usr/bin/env python3
"""
COMPREHENSIVE 1CFB ADDRESS ANALYSIS

Analyze ALL 25 1CFB addresses to find "THE" one:
1. Extract all metadata
2. Analyze byte sum patterns
3. Check for special properties
4. Identify the most likely "correct" 1CFB
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

def load_all_1cfb_addresses():
    """Load ALL 1CFB addresses with complete metadata"""
    print("=" * 80)
    print("LOADING ALL 1CFB ADDRESSES")
    print("=" * 80)

    base_dir = Path("../public/data")
    all_files = list(base_dir.glob("*.json"))

    cfb_addresses = []

    for json_file in all_files:
        try:
            with open(json_file) as f:
                data = json.load(f)

            addresses = []
            if isinstance(data, list):
                addresses = data
            elif isinstance(data, dict):
                for key in ['addresses', 'records', 'data', 'results']:
                    if key in data and isinstance(data[key], list):
                        addresses = data[key]
                        break

            for addr_data in addresses:
                if isinstance(addr_data, dict):
                    address = addr_data.get('address', '')
                    if '1CFB' in address:
                        hash160 = addr_data.get('hash160', '')
                        if hash160:
                            try:
                                hash_bytes = bytes.fromhex(hash160)
                                first_byte = hash_bytes[0]
                                byte_sum = sum(hash_bytes)

                                cfb_addresses.append({
                                    'address': address,
                                    'hash160': hash160,
                                    'first_byte': first_byte,
                                    'byte_sum': byte_sum,
                                    'source': json_file.name,
                                    'method': addr_data.get('method', 'UNKNOWN'),
                                    'row': addr_data.get('row'),
                                    'col': addr_data.get('col'),
                                    'index': addr_data.get('index'),
                                    'seed': addr_data.get('seed', ''),
                                })
                            except:
                                pass
        except:
            pass

    # Remove duplicates (keep first occurrence)
    unique_cfb = []
    seen = set()
    for addr in cfb_addresses:
        if addr['address'] not in seen:
            unique_cfb.append(addr)
            seen.add(addr['address'])

    print(f"\n✅ Found {len(unique_cfb)} unique 1CFB addresses")
    return unique_cfb

def analyze_byte_sum_patterns(cfb_addresses):
    """Analyze byte sum patterns for special numbers"""
    print("\n" + "=" * 80)
    print("BYTE SUM PATTERN ANALYSIS")
    print("=" * 80)

    special_factors = {
        121: "11² (NXT constant)",
        19: "Qubic constant (2299 = 121 × 19)",
        11: "√121",
        27: "3³",
        33: "3 × 11",
        7: "Prime",
        13: "Prime",
    }

    print(f"\n{'Address':<36} {'Sum':<6} {'Factors':<30} {'Special':<30}")
    print("-" * 120)

    scored_addresses = []

    for addr in cfb_addresses:
        byte_sum = addr['byte_sum']

        # Factorize
        factors = []
        temp = byte_sum
        for divisor in sorted(special_factors.keys(), reverse=True):
            while temp % divisor == 0:
                factors.append(divisor)
                temp //= divisor

        if temp > 1:
            factors.append(temp)

        factors_str = ' × '.join(map(str, factors)) if factors else str(byte_sum)

        # Calculate special score
        special_score = 0
        special_notes = []

        for factor in factors:
            if factor in special_factors:
                special_score += 10
                special_notes.append(f"{factor}={special_factors[factor]}")

        # Check if sum itself is special
        if byte_sum == 2299:
            special_score += 100
            special_notes.append("⭐ SUM IS 2299!")
        elif byte_sum % 121 == 0:
            special_score += 20
            special_notes.append("Divisible by 121")
        elif byte_sum % 19 == 0:
            special_score += 15
            special_notes.append("Divisible by 19")

        special_str = ', '.join(special_notes) if special_notes else "-"

        print(f"{addr['address']:<36} {byte_sum:<6,} {factors_str:<30} {special_str[:30]:<30}")

        scored_addresses.append({
            **addr,
            'special_score': special_score,
            'factors': factors,
        })

    return scored_addresses

def analyze_method_patterns(scored_addresses):
    """Analyze method patterns"""
    print("\n" + "=" * 80)
    print("METHOD PATTERN ANALYSIS")
    print("=" * 80)

    method_counts = Counter(a['method'] for a in scored_addresses)

    print(f"\nMethod distribution:")
    print(f"{'Method':<15} {'Count':<8} {'Addresses':<60}")
    print("-" * 90)

    for method, count in method_counts.most_common():
        addrs = [a['address'][:20] + '...' for a in scored_addresses if a['method'] == method]
        addrs_str = ', '.join(addrs[:3])
        if count > 3:
            addrs_str += f" (+{count-3} more)"

        print(f"{method:<15} {count:<8} {addrs_str}")

    return method_counts

def identify_special_addresses(scored_addresses):
    """Identify addresses with special properties"""
    print("\n" + "=" * 80)
    print("IDENTIFYING SPECIAL ADDRESSES")
    print("=" * 80)

    # Sort by special score
    sorted_by_score = sorted(scored_addresses, key=lambda x: x['special_score'], reverse=True)

    print(f"\nTop 10 by special score:")
    print(f"{'Rank':<6} {'Address':<36} {'Score':<8} {'Sum':<6} {'Method':<12}")
    print("-" * 90)

    for i, addr in enumerate(sorted_by_score[:10], 1):
        marker = "⭐" if addr['special_score'] > 20 else ""
        print(f"{i:<6} {addr['address']:<36} {addr['special_score']:<8} {addr['byte_sum']:<6,} {addr['method']:<12} {marker}")

    # Check for addresses with specific patterns
    print("\n" + "=" * 80)
    print("SPECIAL PATTERN CHECKS")
    print("=" * 80)

    # Pattern 1: Divisible by 121
    div_121 = [a for a in scored_addresses if a['byte_sum'] % 121 == 0]
    print(f"\n1. Divisible by 121: {len(div_121)}")
    for addr in div_121:
        print(f"   {addr['address']} (sum: {addr['byte_sum']} = 121 × {addr['byte_sum'] // 121})")

    # Pattern 2: Divisible by 19
    div_19 = [a for a in scored_addresses if a['byte_sum'] % 19 == 0]
    print(f"\n2. Divisible by 19: {len(div_19)}")
    for addr in div_19:
        print(f"   {addr['address']} (sum: {addr['byte_sum']} = 19 × {addr['byte_sum'] // 19})")

    # Pattern 3: Divisible by both 121 AND 19 (= divisible by 2299)
    div_2299 = [a for a in scored_addresses if a['byte_sum'] % 2299 == 0]
    print(f"\n3. Divisible by 2299 (121 × 19): {len(div_2299)}")
    for addr in div_2299:
        print(f"   ⭐⭐⭐ {addr['address']} (sum: {addr['byte_sum']} = 2299 × {addr['byte_sum'] // 2299})")

    # Pattern 4: Close to 2299
    close_to_2299 = [a for a in scored_addresses if abs(a['byte_sum'] - 2299) < 100]
    print(f"\n4. Close to 2299 (±100): {len(close_to_2299)}")
    for addr in close_to_2299:
        diff = addr['byte_sum'] - 2299
        print(f"   {addr['address']} (sum: {addr['byte_sum']}, diff: {diff:+d})")

    # Pattern 5: Has seed starting with specific patterns
    print(f"\n5. Seed pattern analysis:")
    for addr in sorted_by_score[:5]:
        seed = addr.get('seed', '')
        if seed:
            print(f"   {addr['address'][:30]}...")
            print(f"      Seed: {seed[:40]}...")
        else:
            print(f"   {addr['address'][:30]}... (no seed)")

    return sorted_by_score

def find_the_real_1cfb(sorted_addresses):
    """Try to identify THE real 1CFB"""
    print("\n" + "=" * 80)
    print("FINDING 'THE' REAL 1CFB")
    print("=" * 80)

    candidates = []

    # Criteria 1: Highest special score
    top_score = sorted_addresses[0]
    candidates.append({
        'address': top_score,
        'reason': f"Highest special score ({top_score['special_score']})",
        'confidence': 'MEDIUM',
    })

    # Criteria 2: Divisible by 121
    div_121 = [a for a in sorted_addresses if a['byte_sum'] % 121 == 0]
    if div_121:
        candidates.append({
            'address': div_121[0],
            'reason': f"Divisible by 121 (sum: {div_121[0]['byte_sum']} = 121 × {div_121[0]['byte_sum'] // 121})",
            'confidence': 'HIGH',
        })

    # Criteria 3: Divisible by 19
    div_19 = [a for a in sorted_addresses if a['byte_sum'] % 19 == 0]
    if div_19:
        candidates.append({
            'address': div_19[0],
            'reason': f"Divisible by 19 (sum: {div_19[0]['byte_sum']} = 19 × {div_19[0]['byte_sum'] // 19})",
            'confidence': 'HIGH',
        })

    # Criteria 4: Simplest method (row or col)
    simple_methods = [a for a in sorted_addresses if a['method'] in ['row', 'col']]
    if simple_methods:
        candidates.append({
            'address': simple_methods[0],
            'reason': f"Simplest method ({simple_methods[0]['method']})",
            'confidence': 'LOW',
        })

    # Remove duplicates
    unique_candidates = []
    seen_addrs = set()
    for c in candidates:
        addr_str = c['address']['address']
        if addr_str not in seen_addrs:
            unique_candidates.append(c)
            seen_addrs.add(addr_str)

    print(f"\nIdentified {len(unique_candidates)} top candidates:")
    print(f"\n{'Confidence':<12} {'Address':<36} {'Sum':<6} {'Method':<12} {'Reason':<40}")
    print("-" * 120)

    for candidate in unique_candidates:
        addr = candidate['address']
        print(f"{candidate['confidence']:<12} {addr['address']:<36} {addr['byte_sum']:<6,} {addr['method']:<12} {candidate['reason']:<40}")

    # THE BEST candidate
    print("\n" + "=" * 80)
    print("THE MOST LIKELY 1CFB")
    print("=" * 80)

    # Priority: Divisible by 2299 > Divisible by 121 > Divisible by 19 > Highest score
    div_2299 = [a for a in sorted_addresses if a['byte_sum'] % 2299 == 0]
    if div_2299:
        best = div_2299[0]
        reason = "⭐⭐⭐ Divisible by 2299 (121 × 19)!"
        confidence = "VERY HIGH"
    else:
        div_121 = [a for a in sorted_addresses if a['byte_sum'] % 121 == 0]
        if div_121:
            best = div_121[0]
            reason = "Divisible by 121 (11²)"
            confidence = "HIGH"
        else:
            div_19 = [a for a in sorted_addresses if a['byte_sum'] % 19 == 0]
            if div_19:
                best = div_19[0]
                reason = "Divisible by 19"
                confidence = "HIGH"
            else:
                best = sorted_addresses[0]
                reason = "Highest special score"
                confidence = "MEDIUM"

    print(f"\nBEST CANDIDATE:")
    print(f"  Address: {best['address']}")
    print(f"  Hash160: {best['hash160']}")
    print(f"  Byte sum: {best['byte_sum']:,}")
    print(f"  First byte: 0x{best['first_byte']:02x}")
    print(f"  Method: {best['method']}")
    print(f"  Source: {best['source']}")
    print(f"  Reason: {reason}")
    print(f"  Confidence: {confidence}")

    if best.get('seed'):
        print(f"  Seed: {best['seed']}")

    if best.get('row') is not None and best.get('col') is not None:
        print(f"  Position: Row {best['row']}, Col {best['col']}")

    return best

def generate_blockchain_check_list(cfb_addresses):
    """Generate list of addresses for blockchain checking"""
    print("\n" + "=" * 80)
    print("GENERATING BLOCKCHAIN CHECK LIST")
    print("=" * 80)

    output_file = Path("1CFB_ADDRESSES_FOR_BLOCKCHAIN_CHECK.txt")

    with open(output_file, 'w') as f:
        f.write("# ALL 1CFB ADDRESSES FOR BLOCKCHAIN ANALYSIS\n")
        f.write(f"# Total: {len(cfb_addresses)} addresses\n")
        f.write(f"# Generated: 2026-01-10\n\n")

        for i, addr in enumerate(cfb_addresses, 1):
            f.write(f"{addr['address']}\n")

    print(f"\n✅ Address list saved: {output_file}")
    print(f"\nYou can check these addresses on:")
    print(f"  - https://blockchain.info/address/[ADDRESS]")
    print(f"  - https://blockchair.com/bitcoin/address/[ADDRESS]")
    print(f"  - https://mempool.space/address/[ADDRESS]")

    return output_file

def save_complete_analysis(cfb_addresses, best_candidate):
    """Save complete analysis to JSON"""
    print("\n" + "=" * 80)
    print("SAVING COMPLETE ANALYSIS")
    print("=" * 80)

    output_file = Path("1CFB_COMPLETE_ANALYSIS.json")

    analysis = {
        'date': '2026-01-10',
        'total_addresses': len(cfb_addresses),
        'best_candidate': {
            'address': best_candidate['address'],
            'hash160': best_candidate['hash160'],
            'byte_sum': best_candidate['byte_sum'],
            'first_byte': f"0x{best_candidate['first_byte']:02x}",
            'method': best_candidate['method'],
            'source': best_candidate['source'],
            'seed': best_candidate.get('seed', ''),
            'row': best_candidate.get('row'),
            'col': best_candidate.get('col'),
        },
        'all_addresses': [
            {
                'address': a['address'],
                'byte_sum': a['byte_sum'],
                'first_byte': f"0x{a['first_byte']:02x}",
                'method': a['method'],
                'source': a['source'],
                'special_score': a.get('special_score', 0),
            }
            for a in cfb_addresses
        ],
        'statistics': {
            'byte_sum_mean': sum(a['byte_sum'] for a in cfb_addresses) / len(cfb_addresses),
            'byte_sum_min': min(a['byte_sum'] for a in cfb_addresses),
            'byte_sum_max': max(a['byte_sum'] for a in cfb_addresses),
            'first_byte_0x7b_count': sum(1 for a in cfb_addresses if a['first_byte'] == 0x7b),
            'first_byte_0x7b_pct': sum(1 for a in cfb_addresses if a['first_byte'] == 0x7b) / len(cfb_addresses) * 100,
        }
    }

    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\n✅ Complete analysis saved: {output_file}")

def main():
    print("🔍 COMPREHENSIVE 1CFB ADDRESS ANALYSIS")
    print("=" * 80)

    # Step 1: Load all 1CFB addresses
    cfb_addresses = load_all_1cfb_addresses()

    if not cfb_addresses:
        print("\n❌ No 1CFB addresses found!")
        return

    # Step 2: Analyze byte sum patterns
    scored_addresses = analyze_byte_sum_patterns(cfb_addresses)

    # Step 3: Analyze method patterns
    analyze_method_patterns(scored_addresses)

    # Step 4: Identify special addresses
    sorted_addresses = identify_special_addresses(scored_addresses)

    # Step 5: Find THE real 1CFB
    best_candidate = find_the_real_1cfb(sorted_addresses)

    # Step 6: Generate blockchain check list
    generate_blockchain_check_list(cfb_addresses)

    # Step 7: Save complete analysis
    save_complete_analysis(scored_addresses, best_candidate)

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

    print(f"\nNext steps:")
    print(f"  1. Check blockchain for all 25 addresses")
    print(f"     → Use 1CFB_ADDRESSES_FOR_BLOCKCHAIN_CHECK.txt")
    print(f"  2. Identify which has balance/transactions")
    print(f"  3. Focus on the BEST CANDIDATE:")
    print(f"     → {best_candidate['address']}")

if __name__ == "__main__":
    main()
