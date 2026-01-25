#!/usr/bin/env python3
"""
EXTENDED Address Search - Find the remaining ~1,300 addresses
==============================================================
Additional strategies beyond the ultimate search
"""

import json
import os
from collections import defaultdict

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

# Load already found addresses
ultimate_path = os.path.join(script_dir, 'ULTIMATE_ALL_ADDRESSES.txt')
already_found = set()
if os.path.exists(ultimate_path):
    with open(ultimate_path, 'r') as f:
        already_found = set(line.strip() for line in f if line.strip())
print(f"Already found: {len(already_found)} addresses")

all_found = {}  # address -> info

# All CFB values
CFB_VALUES = [27, -27, 7, -7, 121, -121, 100, 37, -37, 42, -42, 127, -127, -128, 19, -19, 13, -13, 11, -11, 3, -3]
CFB_SET = set(CFB_VALUES)

# ========================================
# STRATEGY 8: ANTI-DIAGONAL (matrix[i, 127-i])
# ========================================
print("=" * 70)
print("STRATEGY 8: ANTI-DIAGONAL")
print("=" * 70)

for i in range(128):
    value = matrix[i][127 - i]
    if value in CFB_SET:
        for layer in range(3):
            block = layer * 16384 + i * 128 + (127 - i)
            if block in addr_by_block:
                addr = addr_by_block[block]['address']
                if addr not in already_found and addr not in all_found:
                    all_found[addr] = {
                        'block': block,
                        'strategy': 'anti_diagonal',
                        'value': value,
                        'position': [i, 127 - i],
                        'layer': layer
                    }

print(f"Strategy 8: {len(all_found)} new addresses")

# ========================================
# STRATEGY 9: COLUMN-BASED (5+ CFB values in column)
# ========================================
print("=" * 70)
print("STRATEGY 9: COLUMN-BASED SELECTION")
print("=" * 70)

before = len(all_found)
for col in range(128):
    # Count CFB values in this column
    cfb_count = sum(1 for row in range(128) if matrix[row][col] in CFB_SET)
    if cfb_count >= 5:
        for block, addr_data in addr_by_block.items():
            if block % 128 == col:  # Block maps to this column
                addr = addr_data['address']
                if addr not in already_found and addr not in all_found:
                    all_found[addr] = {
                        'block': block,
                        'strategy': 'column_cfb_count',
                        'cfb_count': cfb_count,
                        'layer': block // 16384
                    }

print(f"Strategy 9: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 10: XOR PATTERNS (row XOR col = CFB value)
# ========================================
print("=" * 70)
print("STRATEGY 10: XOR PATTERNS")
print("=" * 70)

before = len(all_found)
cfb_xor_values = {27, 7, 121, 100, 42, 127, 19, 13, 11, 3}

for row in range(128):
    for col in range(128):
        xor_val = row ^ col
        if xor_val in cfb_xor_values:
            for layer in range(3):
                block = layer * 16384 + row * 128 + col
                if block in addr_by_block:
                    addr = addr_by_block[block]['address']
                    if addr not in already_found and addr not in all_found:
                        all_found[addr] = {
                            'block': block,
                            'strategy': 'xor_pattern',
                            'xor_value': xor_val,
                            'position': [row, col],
                            'layer': layer
                        }

print(f"Strategy 10: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 11: ROW + COL SUM = CFB NUMBER
# ========================================
print("=" * 70)
print("STRATEGY 11: ROW + COL SUM")
print("=" * 70)

before = len(all_found)
cfb_sum_values = {27, 54, 81, 108, 121, 128, 100, 127, 7, 14, 21, 42, 84}

for row in range(128):
    for col in range(128):
        if (row + col) in cfb_sum_values:
            for layer in range(3):
                block = layer * 16384 + row * 128 + col
                if block in addr_by_block:
                    addr = addr_by_block[block]['address']
                    if addr not in already_found and addr not in all_found:
                        all_found[addr] = {
                            'block': block,
                            'strategy': 'sum_pattern',
                            'sum_value': row + col,
                            'position': [row, col],
                            'layer': layer
                        }

print(f"Strategy 11: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 12: POWERS OF 2 BLOCKS
# ========================================
print("=" * 70)
print("STRATEGY 12: POWERS OF 2 BLOCKS")
print("=" * 70)

before = len(all_found)
powers_of_2 = {2**i for i in range(20)}  # Up to 2^19

for block, addr_data in addr_by_block.items():
    if block in powers_of_2:
        addr = addr_data['address']
        if addr not in already_found and addr not in all_found:
            all_found[addr] = {
                'block': block,
                'strategy': 'power_of_2',
                'layer': block // 16384
            }

print(f"Strategy 12: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 13: PERFECT SQUARES
# ========================================
print("=" * 70)
print("STRATEGY 13: PERFECT SQUARE BLOCKS")
print("=" * 70)

before = len(all_found)
perfect_squares = {i*i for i in range(300)}  # Up to 299^2

for block, addr_data in addr_by_block.items():
    if block in perfect_squares:
        addr = addr_data['address']
        if addr not in already_found and addr not in all_found:
            all_found[addr] = {
                'block': block,
                'strategy': 'perfect_square',
                'layer': block // 16384
            }

print(f"Strategy 13: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 14: TRIANGULAR NUMBERS
# ========================================
print("=" * 70)
print("STRATEGY 14: TRIANGULAR NUMBER BLOCKS")
print("=" * 70)

before = len(all_found)
triangular = {n*(n+1)//2 for n in range(500)}

for block, addr_data in addr_by_block.items():
    if block in triangular:
        addr = addr_data['address']
        if addr not in already_found and addr not in all_found:
            all_found[addr] = {
                'block': block,
                'strategy': 'triangular',
                'layer': block // 16384
            }

print(f"Strategy 14: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 15: PALINDROME BLOCK NUMBERS
# ========================================
print("=" * 70)
print("STRATEGY 15: PALINDROME BLOCKS")
print("=" * 70)

before = len(all_found)
def is_palindrome(n):
    s = str(n)
    return s == s[::-1]

for block, addr_data in addr_by_block.items():
    if is_palindrome(block):
        addr = addr_data['address']
        if addr not in already_found and addr not in all_found:
            all_found[addr] = {
                'block': block,
                'strategy': 'palindrome',
                'layer': block // 16384
            }

print(f"Strategy 15: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 16: MATRIX VALUE = BLOCK MOD 128
# ========================================
print("=" * 70)
print("STRATEGY 16: SELF-REFERENTIAL POSITIONS")
print("=" * 70)

before = len(all_found)
for block, addr_data in addr_by_block.items():
    row = (block // 128) % 128
    col = block % 128
    value = matrix[row][col]
    # Self-reference: value equals position
    if value == row or value == col or value == (row + col) % 128:
        addr = addr_data['address']
        if addr not in already_found and addr not in all_found:
            all_found[addr] = {
                'block': block,
                'strategy': 'self_reference',
                'value': value,
                'position': [row, col],
                'layer': block // 16384
            }

print(f"Strategy 16: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 17: BLOCKS CONTAINING DIGIT 7
# ========================================
print("=" * 70)
print("STRATEGY 17: BLOCKS WITH DIGIT 7")
print("=" * 70)

before = len(all_found)
for block, addr_data in addr_by_block.items():
    if '7' in str(block):
        addr = addr_data['address']
        if addr not in already_found and addr not in all_found:
            all_found[addr] = {
                'block': block,
                'strategy': 'digit_7',
                'layer': block // 16384
            }

print(f"Strategy 17: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# STRATEGY 18: ALL REMAINING PATOSHI ADDRESSES
# ========================================
print("=" * 70)
print("STRATEGY 18: ALL REMAINING PATOSHI ADDRESSES")
print("=" * 70)

before = len(all_found)
for block, addr_data in addr_by_block.items():
    addr = addr_data['address']
    if addr not in already_found and addr not in all_found:
        all_found[addr] = {
            'block': block,
            'strategy': 'remaining_patoshi',
            'layer': block // 16384
        }

print(f"Strategy 18: +{len(all_found) - before} new (total: {len(all_found)})")

# ========================================
# FINAL SUMMARY
# ========================================
print()
print("=" * 70)
print("EXTENDED SEARCH SUMMARY")
print("=" * 70)

# Group by strategy
by_strategy = defaultdict(list)
for addr, info in all_found.items():
    by_strategy[info['strategy']].append(addr)

print("\nNEW Addresses by Strategy:")
for strategy, addrs in sorted(by_strategy.items(), key=lambda x: -len(x[1])):
    print(f"  {strategy}: {len(addrs)}")

# Group by layer
by_layer = defaultdict(list)
for addr, info in all_found.items():
    by_layer[info['layer']].append(addr)

print("\nNEW Addresses by Layer:")
for layer in [0, 1, 2]:
    addrs = by_layer[layer]
    print(f"  Layer {layer}: {len(addrs)}")

print(f"\nNEW UNIQUE ADDRESSES: {len(all_found)}")
print(f"PREVIOUSLY FOUND: {len(already_found)}")
print(f"COMBINED TOTAL: {len(all_found) + len(already_found)}")
print(f"TOTAL PATOSHI: {len(addr_by_block)}")

coverage = (len(all_found) + len(already_found)) / len(addr_by_block) * 100
print(f"COVERAGE: {coverage:.1f}%")

# Save new addresses
new_output_path = os.path.join(script_dir, 'EXTENDED_NEW_ADDRESSES.json')
with open(new_output_path, 'w') as f:
    json.dump({
        'new_addresses_count': len(all_found),
        'previously_found': len(already_found),
        'total_combined': len(all_found) + len(already_found),
        'total_patoshi': len(addr_by_block),
        'by_strategy': {k: len(v) for k, v in by_strategy.items()},
        'addresses': all_found
    }, f, indent=2)

# Combine all addresses into master list
all_combined = set(already_found)
all_combined.update(all_found.keys())

master_path = os.path.join(script_dir, 'MASTER_ALL_ADDRESSES.txt')
with open(master_path, 'w') as f:
    for addr in sorted(all_combined):
        f.write(f"{addr}\n")

print(f"\nNew addresses saved to: {new_output_path}")
print(f"Master list saved to: {master_path}")
print(f"Master list contains: {len(all_combined)} addresses")

# Final potential
total_btc = len(all_combined) * 50
print(f"\nTOTAL POTENTIAL: {total_btc:,} BTC")
print(f"VALUE @ $100k: ${total_btc * 100000:,.0f}")
