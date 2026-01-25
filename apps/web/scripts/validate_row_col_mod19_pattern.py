#!/usr/bin/env python3
"""
CRITICAL TEST: Validate (Row + Col) mod 19 Pattern

1CF4 is at index 439558 → Row 443, Col 545
(Row + Col) = 988
988 mod 19 = 0  ⭐

HYPOTHESIS: ALL 0x7b family members have (Row + Col) mod 19 = 0

If TRUE: We can search the matrix systematically for ALL positions
         where (Row + Col) mod 19 = 0 and generate addresses.
         1CFB might be one of them!
"""

import json
from pathlib import Path
from collections import defaultdict

def load_matrix_addresses():
    """Load matrix addresses with positions"""
    matrix_file = Path("../public/data/matrix-addresses.json")
    if not matrix_file.exists():
        print(f"❌ Matrix file not found: {matrix_file}")
        return []

    with open(matrix_file) as f:
        data = json.load(f)

    # Handle different structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        for key in ['addresses', 'records', 'data']:
            if key in data and isinstance(data[key], list):
                return data[key]

    return []

def calculate_position_from_index(index, matrix_size=991):
    """Calculate row/col from linear index"""
    row = index // matrix_size
    col = index % matrix_size
    return row, col

def find_0x7b_family_members():
    """Find all 0x7b family members (0x7b + byte sum 2299)"""
    print("=" * 80)
    print("FINDING 0x7b FAMILY MEMBERS")
    print("=" * 80)

    matrix_addresses = load_matrix_addresses()
    print(f"\nLoaded {len(matrix_addresses):,} matrix addresses")

    family_members = []

    for idx, addr_data in enumerate(matrix_addresses):
        if isinstance(addr_data, dict):
            address = addr_data.get('address', '')
            hash160 = addr_data.get('hash160', '')

            if hash160:
                try:
                    hash_bytes = bytes.fromhex(hash160)
                    first_byte = hash_bytes[0]
                    byte_sum = sum(hash_bytes)

                    # Check if 0x7b family member
                    if first_byte == 0x7b and byte_sum == 2299:
                        row, col = calculate_position_from_index(idx)

                        family_members.append({
                            'address': address,
                            'hash160': hash160,
                            'index': idx,
                            'row': row,
                            'col': col,
                            'row_plus_col': row + col,
                            'mod_19': (row + col) % 19,
                        })
                except:
                    pass

    print(f"\n✅ Found {len(family_members)} family members in matrix")
    return family_members

def validate_pattern(family_members):
    """Validate the (Row + Col) mod 19 = 0 pattern"""
    print("\n" + "=" * 80)
    print("VALIDATING (ROW + COL) MOD 19 PATTERN")
    print("=" * 80)

    if not family_members:
        print("\n❌ No family members found!")
        return False

    print(f"\n{'Address':<36} {'Index':<10} {'Row':<6} {'Col':<6} {'R+C':<6} {'mod 19':<8}")
    print("-" * 80)

    pattern_holds = []

    for member in family_members:
        addr = member['address']
        idx = member['index']
        row = member['row']
        col = member['col']
        sum_val = member['row_plus_col']
        mod19 = member['mod_19']

        marker = "✓" if mod19 == 0 else "✗"
        pattern_holds.append(mod19 == 0)

        print(f"{addr:<36} {idx:<10,} {row:<6} {col:<6} {sum_val:<6} {mod19:<8} {marker}")

    # Statistics
    print("\n" + "=" * 80)
    print("PATTERN VALIDATION RESULTS")
    print("=" * 80)

    total = len(pattern_holds)
    matches = sum(pattern_holds)
    match_rate = matches / total * 100 if total > 0 else 0

    print(f"\nTotal family members: {total}")
    print(f"Pattern matches (mod 19 = 0): {matches}")
    print(f"Pattern fails (mod 19 ≠ 0): {total - matches}")
    print(f"Match rate: {match_rate:.1f}%")

    if match_rate == 100.0:
        print("\n⭐⭐⭐ PATTERN IS PERFECT! All family members have (Row + Col) mod 19 = 0")
        print("\nThis is a MATHEMATICAL CONSTRAINT for the 0x7b family!")
        return True
    elif match_rate >= 80.0:
        print(f"\n⚠️  Pattern holds for {match_rate:.1f}% of members")
        print("This is SIGNIFICANT but not absolute")
        return True
    else:
        print(f"\n❌ Pattern does NOT hold ({match_rate:.1f}% match rate)")
        return False

def find_all_mod19_positions(matrix_size=991):
    """Find ALL matrix positions where (Row + Col) mod 19 = 0"""
    print("\n" + "=" * 80)
    print("FINDING ALL (ROW + COL) MOD 19 = 0 POSITIONS")
    print("=" * 80)

    positions = []

    for row in range(matrix_size):
        for col in range(matrix_size):
            if (row + col) % 19 == 0:
                index = row * matrix_size + col
                positions.append({
                    'row': row,
                    'col': col,
                    'index': index,
                })

    print(f"\n✅ Found {len(positions):,} positions where (Row + Col) mod 19 = 0")
    print(f"   Out of {matrix_size * matrix_size:,} total positions")
    print(f"   Percentage: {len(positions) / (matrix_size * matrix_size) * 100:.2f}%")

    # Expected percentage (approximately 1/19 of all positions)
    expected_pct = 100 / 19
    print(f"\n   Expected (1/19): {expected_pct:.2f}%")

    return positions

def check_if_1cfb_in_positions(mod19_positions):
    """Check if any mod19 positions contain 1CFB"""
    print("\n" + "=" * 80)
    print("CHECKING MOD19 POSITIONS FOR 1CFB")
    print("=" * 80)

    matrix_addresses = load_matrix_addresses()

    print(f"\nSearching {len(mod19_positions):,} positions for 1CFB...")

    found_1cfb = False

    for pos in mod19_positions:
        idx = pos['index']

        if idx < len(matrix_addresses):
            addr_data = matrix_addresses[idx]

            if isinstance(addr_data, dict):
                address = addr_data.get('address', '')

                if address.startswith('1CFB'):
                    print(f"\n⭐⭐⭐ FOUND 1CFB!")
                    print(f"   Address: {address}")
                    print(f"   Index: {idx}")
                    print(f"   Row: {pos['row']}")
                    print(f"   Col: {pos['col']}")
                    found_1cfb = True

    if not found_1cfb:
        print("\n❌ 1CFB NOT found in mod19 positions")
        print("\nPossible reasons:")
        print("  1. 1CFB is NOT in the matrix-addresses dataset")
        print("  2. 1CFB uses different generation method")
        print("  3. 1CFB is in a different batch/dataset")

    return found_1cfb

def main():
    print("🔍 VALIDATING (ROW + COL) MOD 19 PATTERN")
    print("=" * 80)

    # Step 1: Find 0x7b family members
    family_members = find_0x7b_family_members()

    if not family_members:
        print("\n❌ No family members found in matrix!")
        print("   Checking other datasets...")
        return

    # Step 2: Validate pattern
    pattern_valid = validate_pattern(family_members)

    if pattern_valid:
        # Step 3: Find all mod19 positions
        mod19_positions = find_all_mod19_positions()

        # Step 4: Check for 1CFB
        found_1cfb = check_if_1cfb_in_positions(mod19_positions)

        if found_1cfb:
            print("\n" + "=" * 80)
            print("🎉 SUCCESS! 1CFB FOUND!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            print("\n1. Search OTHER datasets for 1CFB")
            print("2. Generate Bitcoin addresses for ALL mod19 positions")
            print("3. Test if any match 1CFB pattern")
    else:
        print("\n" + "=" * 80)
        print("PATTERN FAILED")
        print("=" * 80)
        print("\n(Row + Col) mod 19 is NOT the constraint")
        print("Need to find different pattern!")

    # Save results
    output_file = Path("MOD19_PATTERN_VALIDATION_RESULTS.json")
    results = {
        'date': '2026-01-10',
        'pattern': '(Row + Col) mod 19 = 0',
        'family_members_found': len(family_members),
        'pattern_valid': pattern_valid,
        'family_members': family_members,
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved: {output_file}")

if __name__ == "__main__":
    main()
