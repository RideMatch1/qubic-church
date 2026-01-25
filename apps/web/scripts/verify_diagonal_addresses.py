#!/usr/bin/env python3
"""
Verify Diagonal Addresses and Check Balance
============================================
Compares scanned ±27 positions with documented addresses
"""

import json
import os
import requests
import time

# Positions from our scan
SCANNED_POSITIONS = [72, 73, 74, 79, 88, 92, 94, 95, 119, 120]

# Documented positions from THE_10_GENESIS_ADDRESSES_500BTC.md
DOCUMENTED_POSITIONS = [73, 74, 75, 80, 89, 93, 95, 96, 120, 121]

# Known addresses from documentation
KNOWN_ADDRESSES = {
    73: "1Ky8dP7oR1cBeg1MzkrgHAeHAHyn92DCar",
    74: "1FnbdYntfohuZ1EhZ7f9oiT2R5sDsZBohL",
    75: "14U5EYTN54agAngQu92D9gESvHYfKw8EqA",
    80: "1BwWdLV5wbnZvSYfNA8zaEMqEDDjvA99wX",
    89: "1KSHc1tmsUhS9f1TD6RHR8Kmwg9Zv8WhCt",
    93: "1LNV5xnjneJwXc6jN8X2co586gjiSz6asS",
    95: "18GyZ216oMhpCbZ7JkKZyT8x68v2a8HuNA",
    96: "12XPHPCGYz1WgRhquiAfVeAyjZ7Gbdpih3",
    120: "1FeGetWU2tR2QSrxnpRwHGXGcxzhN6zQza",
    121: "1B7CyZF8e6TYzhNBSHy8yYuTRJNpMtNChg",
}

def get_balance(address):
    """Get balance from blockchain.info API"""
    try:
        url = f"https://blockchain.info/q/addressbalance/{address}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return int(resp.text) / 100_000_000  # Satoshis to BTC
        return None
    except Exception as e:
        print(f"Error checking {address}: {e}")
        return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load 3d_layered_addresses.json
    layered_path = os.path.join(script_dir, '../../../outputs/3d_layered_addresses.json')
    print("Loading 3d_layered_addresses.json...")
    with open(layered_path, 'r') as f:
        layered_data = json.load(f)

    # Create block -> address mapping
    addr_by_block = {a['blockHeight']: a['address'] for a in layered_data['all_addresses']}

    print()
    print("=" * 70)
    print("COMPARING SCANNED POSITIONS VS DOCUMENTED POSITIONS")
    print("=" * 70)
    print()

    # All unique positions
    all_positions = sorted(set(SCANNED_POSITIONS) | set(DOCUMENTED_POSITIONS))

    results = []

    print(f"{'Block':<6} {'In Scan':<10} {'In Docs':<10} {'Address':<40} {'Balance':<15}")
    print("-" * 85)

    for block in all_positions:
        in_scan = "YES" if block in SCANNED_POSITIONS else "no"
        in_docs = "YES" if block in DOCUMENTED_POSITIONS else "no"

        # Get address from layered data or known addresses
        address = addr_by_block.get(block) or KNOWN_ADDRESSES.get(block, "N/A")

        # Check balance
        if address != "N/A":
            time.sleep(1.5)  # Rate limiting - increased to avoid errors
            balance = get_balance(address)
            balance_str = f"{balance:.2f} BTC" if balance is not None else "ERROR"
        else:
            balance = None
            balance_str = "N/A"

        results.append({
            'block': block,
            'in_scan': block in SCANNED_POSITIONS,
            'in_docs': block in DOCUMENTED_POSITIONS,
            'address': address,
            'balance': balance
        })

        # Highlight important findings
        marker = ""
        if balance and balance >= 50:
            marker = "✅ 50 BTC"
        elif in_scan == "YES" and in_docs == "no":
            marker = "⭐ NEW?"
        elif in_scan == "no" and in_docs == "YES":
            marker = "❓ MISMATCH"

        print(f"{block:<6} {in_scan:<10} {in_docs:<10} {address[:38]:<40} {balance_str:<15} {marker}")

    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Count addresses with 50 BTC
    with_50btc = [r for r in results if r['balance'] and r['balance'] >= 50]
    print(f"\nAddresses with ≥50 BTC: {len(with_50btc)}")
    for r in with_50btc:
        print(f"  Block {r['block']}: {r['address']} = {r['balance']:.2f} BTC")

    # New positions from scan
    new_from_scan = [r for r in results if r['in_scan'] and not r['in_docs']]
    print(f"\nNEW positions from scan (not in docs): {len(new_from_scan)}")
    for r in new_from_scan:
        bal = f"{r['balance']:.2f}" if r['balance'] is not None else "N/A"
        print(f"  Block {r['block']}: {r['address']} = {bal} BTC")

    # Documented but not in scan
    docs_not_scan = [r for r in results if r['in_docs'] and not r['in_scan']]
    print(f"\nDocumented but NOT in scan: {len(docs_not_scan)}")
    for r in docs_not_scan:
        bal = f"{r['balance']:.2f}" if r['balance'] is not None else "N/A"
        print(f"  Block {r['block']}: {r['address']} = {bal} BTC")

    # Save results
    output_path = os.path.join(script_dir, 'DIAGONAL_ADDRESS_VERIFICATION.json')
    with open(output_path, 'w') as f:
        json.dump({
            'scanned_positions': SCANNED_POSITIONS,
            'documented_positions': DOCUMENTED_POSITIONS,
            'results': results,
            'addresses_with_50btc': [r for r in results if r['balance'] and r['balance'] >= 50]
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
