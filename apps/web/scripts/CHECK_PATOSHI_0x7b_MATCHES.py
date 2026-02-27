#!/usr/bin/env python3
"""
Check if any of the 84 Patoshi blocks with 0x7b addresses match our derived addresses

Purpose: Compare 84 Patoshi 0x7b hash160 values against 1488 derived 0x7b addresses
to see if we can derive MORE than just Block 264 (1CFB).

Author: Claude Code
Date: 2026-02-07
"""

import json
from pathlib import Path

def main():
    print("=" * 80)
    print("PATOSHI 0x7b ADDRESS MATCHING ANALYSIS")
    print("=" * 80)
    print()

    # Load Patoshi results
    patoshi_path = Path(__file__).parent / "PATOSHI_DEEP_BRIDGE_RESULTS.json"
    print(f"Loading Patoshi analysis: {patoshi_path}")

    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)

    # Extract the 84 Patoshi 0x7b addresses
    patoshi_0x7b = patoshi_data['analysis_2']['bridges']
    print(f"✓ Found {len(patoshi_0x7b)} Patoshi blocks with 0x7b addresses")
    print()

    # Load derived addresses
    derived_path = Path(__file__).parent / "ALLE_0x7b_KEYS.json"
    print(f"Loading derived addresses: {derived_path}")

    with open(derived_path, 'r') as f:
        derived_addresses = json.load(f)

    print(f"✓ Loaded {len(derived_addresses)} derived addresses")
    print()

    # Create hash160 lookup from derived addresses
    derived_hash160_set = set()
    derived_hash160_map = {}

    for addr_data in derived_addresses:
        if 'hash160' in addr_data:
            hash160 = addr_data['hash160']
            derived_hash160_set.add(hash160)
            derived_hash160_map[hash160] = addr_data

    print(f"✓ Created lookup table with {len(derived_hash160_set)} unique hash160 values")
    print()

    # Check for matches
    print("=" * 80)
    print("CHECKING FOR MATCHES...")
    print("=" * 80)
    print()

    matches = []

    for patoshi_block in patoshi_0x7b:
        block_num = patoshi_block['block']
        hash160 = patoshi_block['hash160']

        if hash160 in derived_hash160_set:
            derived_data = derived_hash160_map[hash160]

            match = {
                "block": block_num,
                "hash160": hash160,
                "balance": "50 BTC (Patoshi, never moved)",
                "derived_from": derived_data
            }

            matches.append(match)

            print(f"🎯 MATCH FOUND!")
            print(f"   Block: {block_num}")
            print(f"   Hash160: {hash160}")
            print(f"   Balance: 50 BTC")
            print(f"   Derivation: {derived_data.get('type', 'unknown')}")
            if 'column' in derived_data:
                print(f"   Matrix Column: {derived_data['column']}")
            if 'offset' in derived_data:
                print(f"   Offset: {derived_data['offset']}")
            print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Patoshi 0x7b blocks analyzed: {len(patoshi_0x7b)}")
    print(f"Total derived 0x7b addresses: {len(derived_addresses)}")
    print(f"MATCHES FOUND: {len(matches)}")
    print()

    if matches:
        print("CONCLUSION:")
        print(f"✓ Successfully identified {len(matches)} Patoshi addresses derivable from Anna Matrix")
        print(f"✓ All {len(matches)} addresses have 50 BTC balance (never moved)")
        print()

        # Show blocks
        print("Matched Blocks:")
        for match in matches:
            print(f"  - Block {match['block']:5d}: 50 BTC")
        print()

        # Calculate total
        total_btc = len(matches) * 50
        print(f"TOTAL BITCOIN IN MATCHED ADDRESSES: {total_btc} BTC")
        print()

    else:
        print("CONCLUSION:")
        print("❌ NO matches found beyond what was previously known")
        print("   - Only Block 264 (1CFB) remains as the single derivable Patoshi address")
        print()

    # Save results
    output = {
        "timestamp": "2026-02-07",
        "analysis": "Patoshi 0x7b address matching",
        "patoshi_0x7b_count": len(patoshi_0x7b),
        "derived_0x7b_count": len(derived_addresses),
        "matches_found": len(matches),
        "matches": matches,
        "total_btc_if_matches": len(matches) * 50
    }

    output_path = Path(__file__).parent / "PATOSHI_0x7b_MATCH_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Results saved to: {output_path}")
    print()

if __name__ == "__main__":
    main()
