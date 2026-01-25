#!/usr/bin/env python3
"""
ULTIMATE Address Search - Find ALL potential addresses using ALL criteria
=========================================================================
Searches using multiple CFB signature values and mapping strategies
"""

import json
import os
from collections import defaultdict

# ALL CFB Signature Values
CFB_VALUES = [27, -27, 7, -7, 121, -121, 100, 37, -37, 42, -42, 127, -127, -128, 19, -19, 13, -13, 11, -11, 3, -3]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load Anna Matrix
    matrix_path = os.path.join(script_dir, '../public/data/anna-matrix.json')
    print("Loading Anna Matrix...")
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    matrix = data['matrix']

    # Load 3D layered addresses
    layered_path = os.path.join(script_dir, '../../../outputs/3d_layered_addresses.json')
    print("Loading 3d_layered_addresses.json...")
    with open(layered_path, 'r') as f:
        layered_data = json.load(f)

    addr_by_block = {a['blockHeight']: a for a in layered_data['all_addresses']}
    print(f"Loaded {len(addr_by_block)} addresses from Patoshi dataset")
    print()

    all_found = {}  # address -> info

    # ========================================
    # STRATEGY 1: Diagonal with ALL CFB values
    # ========================================
    print("=" * 70)
    print("STRATEGY 1: DIAGONAL WITH ALL CFB VALUES")
    print("=" * 70)

    for i in range(128):
        value = matrix[i][i]
        if value in CFB_VALUES:
            for layer in range(3):
                block = layer * 16384 + i
                if block in addr_by_block:
                    addr = addr_by_block[block]['address']
                    if addr not in all_found:
                        all_found[addr] = {
                            'block': block,
                            'strategy': 'diagonal',
                            'value': value,
                            'position': [i, i],
                            'layer': layer
                        }

    print(f"Strategy 1: {len(all_found)} addresses")

    # ========================================
    # STRATEGY 2: ANY cell with CFB value → block mapping
    # ========================================
    print("=" * 70)
    print("STRATEGY 2: ALL CELLS WITH CFB VALUES → BLOCK MAPPING")
    print("=" * 70)

    before = len(all_found)
    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value in CFB_VALUES:
                for layer in range(3):
                    block = layer * 16384 + row * 128 + col
                    if block in addr_by_block:
                        addr = addr_by_block[block]['address']
                        if addr not in all_found:
                            all_found[addr] = {
                                'block': block,
                                'strategy': 'cell_mapping',
                                'value': value,
                                'position': [row, col],
                                'layer': layer
                            }

    print(f"Strategy 2: +{len(all_found) - before} new addresses (total: {len(all_found)})")

    # ========================================
    # STRATEGY 3: Block where matrix[block%128, X] contains CFB value
    # ========================================
    print("=" * 70)
    print("STRATEGY 3: ROW-BASED SELECTION")
    print("=" * 70)

    before = len(all_found)
    for block, addr_data in addr_by_block.items():
        row = block % 128
        # Check if any cell in this row has a CFB value
        row_values = matrix[row]
        cfb_count = sum(1 for v in row_values if v in CFB_VALUES)
        if cfb_count >= 5:  # Row has at least 5 CFB values
            addr = addr_data['address']
            if addr not in all_found:
                all_found[addr] = {
                    'block': block,
                    'strategy': 'row_cfb_count',
                    'cfb_count': cfb_count,
                    'layer': block // 16384
                }

    print(f"Strategy 3: +{len(all_found) - before} new addresses (total: {len(all_found)})")

    # ========================================
    # STRATEGY 4: Symmetric positions (point symmetry)
    # ========================================
    print("=" * 70)
    print("STRATEGY 4: SYMMETRIC POSITIONS")
    print("=" * 70)

    before = len(all_found)
    # Load anomalies (positions that break symmetry)
    anomaly_path = os.path.join(script_dir, '../public/data/anna-matrix-anomalies.json')
    try:
        with open(anomaly_path, 'r') as f:
            anomalies = json.load(f)

        anomaly_positions = set()
        if isinstance(anomalies, list):
            for a in anomalies:
                if 'row' in a and 'col' in a:
                    anomaly_positions.add((a['row'], a['col']))
                elif 'pos' in a:
                    anomaly_positions.add(tuple(a['pos']))

        # Map anomaly positions to blocks
        for (row, col) in anomaly_positions:
            for layer in range(3):
                block = layer * 16384 + row * 128 + col
                if block in addr_by_block:
                    addr = addr_by_block[block]['address']
                    if addr not in all_found:
                        all_found[addr] = {
                            'block': block,
                            'strategy': 'anomaly_position',
                            'position': [row, col],
                            'layer': layer
                        }

        print(f"Strategy 4: +{len(all_found) - before} new addresses (total: {len(all_found)})")
    except Exception as e:
        print(f"Strategy 4: Skipped ({e})")

    # ========================================
    # STRATEGY 5: Special value positions (100, 0, max, min)
    # ========================================
    print("=" * 70)
    print("STRATEGY 5: SPECIAL VALUE POSITIONS")
    print("=" * 70)

    before = len(all_found)
    special_values = [0, 100, 127, -128, 64, -64, 32, -32]

    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value in special_values:
                for layer in range(3):
                    block = layer * 16384 + row * 128 + col
                    if block in addr_by_block:
                        addr = addr_by_block[block]['address']
                        if addr not in all_found:
                            all_found[addr] = {
                                'block': block,
                                'strategy': 'special_value',
                                'value': value,
                                'position': [row, col],
                                'layer': layer
                            }

    print(f"Strategy 5: +{len(all_found) - before} new addresses (total: {len(all_found)})")

    # ========================================
    # STRATEGY 6: Fibonacci positions
    # ========================================
    print("=" * 70)
    print("STRATEGY 6: FIBONACCI POSITIONS")
    print("=" * 70)

    before = len(all_found)
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    fib_positions = [(f1, f2) for f1 in fib for f2 in fib if f1 < 128 and f2 < 128]

    for (row, col) in fib_positions:
        for layer in range(3):
            block = layer * 16384 + row * 128 + col
            if block in addr_by_block:
                addr = addr_by_block[block]['address']
                if addr not in all_found:
                    all_found[addr] = {
                        'block': block,
                        'strategy': 'fibonacci',
                        'position': [row, col],
                        'layer': layer
                    }

    print(f"Strategy 6: +{len(all_found) - before} new addresses (total: {len(all_found)})")

    # ========================================
    # STRATEGY 7: Prime number positions
    # ========================================
    print("=" * 70)
    print("STRATEGY 7: PRIME NUMBER BLOCKS")
    print("=" * 70)

    before = len(all_found)

    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    for block, addr_data in addr_by_block.items():
        if is_prime(block):
            addr = addr_data['address']
            if addr not in all_found:
                all_found[addr] = {
                    'block': block,
                    'strategy': 'prime_block',
                    'layer': block // 16384
                }

    print(f"Strategy 7: +{len(all_found) - before} new addresses (total: {len(all_found)})")

    # ========================================
    # FINAL SUMMARY
    # ========================================
    print()
    print("=" * 70)
    print("ULTIMATE SUMMARY")
    print("=" * 70)

    # Group by strategy
    by_strategy = defaultdict(list)
    for addr, info in all_found.items():
        by_strategy[info['strategy']].append(addr)

    print("\nAddresses by Strategy:")
    for strategy, addrs in sorted(by_strategy.items(), key=lambda x: -len(x[1])):
        print(f"  {strategy}: {len(addrs)}")

    # Group by layer
    by_layer = defaultdict(list)
    for addr, info in all_found.items():
        by_layer[info['layer']].append(addr)

    print("\nAddresses by Layer:")
    for layer in [0, 1, 2]:
        addrs = by_layer[layer]
        potential_btc = len(addrs) * 50
        print(f"  Layer {layer}: {len(addrs):,} addresses = {potential_btc:,} potential BTC")

    total_btc = len(all_found) * 50
    print(f"\n🎯 TOTAL UNIQUE ADDRESSES: {len(all_found):,}")
    print(f"💰 POTENTIAL BTC: {total_btc:,} BTC")
    print(f"💵 VALUE @ $100k: ${total_btc * 100000:,.0f}")

    # Save results
    output = {
        'total_addresses': len(all_found),
        'potential_btc': total_btc,
        'by_strategy': {k: len(v) for k, v in by_strategy.items()},
        'by_layer': {k: len(v) for k, v in by_layer.items()},
        'all_addresses': list(all_found.keys()),
        'address_details': all_found
    }

    output_path = os.path.join(script_dir, 'ULTIMATE_ADDRESS_SEARCH_RESULTS.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Export simple list
    list_path = os.path.join(script_dir, 'ULTIMATE_ALL_ADDRESSES.txt')
    with open(list_path, 'w') as f:
        for addr in sorted(all_found.keys()):
            f.write(f"{addr}\n")

    print(f"\nResults saved to: {output_path}")
    print(f"Address list saved to: {list_path}")

if __name__ == '__main__':
    main()
