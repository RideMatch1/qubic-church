#!/usr/bin/env python3
"""
Export all found addresses to clean formats
"""

import json
import os
import csv

script_dir = os.path.dirname(os.path.abspath(__file__))

# Load results
with open(os.path.join(script_dir, 'MASSIVE_ADDRESS_SEARCH_RESULTS.json'), 'r') as f:
    data = json.load(f)

# Export 1: Simple address list (one per line)
addresses = data['all_addresses']
with open(os.path.join(script_dir, 'ALL_2288_ADDRESSES.txt'), 'w') as f:
    for addr in sorted(addresses):
        f.write(f"{addr}\n")

print(f"Exported {len(addresses)} addresses to ALL_2288_ADDRESSES.txt")

# Export 2: CSV with block info
with open(os.path.join(script_dir, 'ALL_2288_ADDRESSES.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Block', 'Address', 'Layer', 'Matrix_Position', 'Diagonal_Value'])

    # From layer_mapped_blocks
    for b in data['layer_mapped_blocks']:
        writer.writerow([
            b['block'],
            b['address'],
            b['layer'],
            f"[{b['matrix_position'][0]},{b['matrix_position'][1]}]",
            b['diagonal_value']
        ])

print(f"Exported detailed CSV to ALL_2288_ADDRESSES.csv")

# Export 3: Summary by layer
by_layer = {0: [], 1: [], 2: []}
for b in data['layer_mapped_blocks']:
    by_layer[b['layer']].append(b)

print("\nSUMMARY BY LAYER:")
print("=" * 50)
for layer in [0, 1, 2]:
    blocks = by_layer[layer]
    block_range = f"{min(b['block'] for b in blocks)}-{max(b['block'] for b in blocks)}" if blocks else "N/A"
    potential_btc = len(blocks) * 50
    print(f"Layer {layer}: {len(blocks):4d} blocks ({block_range})")
    print(f"         Potential: {potential_btc:,} BTC (${potential_btc * 100000:,.0f} @ $100k/BTC)")

total_btc = len(data['layer_mapped_blocks']) * 50
print(f"\nTOTAL POTENTIAL: {total_btc:,} BTC (${total_btc * 100000:,.0f})")

# Export 4: Quick copy-paste format for blockchain checking
with open(os.path.join(script_dir, 'ADDRESSES_FOR_BLOCKCHAIN_CHECK.txt'), 'w') as f:
    f.write("# First 100 addresses from Layer 0 (most likely to have 50 BTC)\n")
    f.write("# Copy-paste to any blockchain explorer\n\n")

    layer0_blocks = [b for b in data['layer_mapped_blocks'] if b['layer'] == 0]
    layer0_blocks.sort(key=lambda x: x['block'])

    for b in layer0_blocks[:100]:
        f.write(f"{b['address']}\n")

print("\nExported first 100 Layer 0 addresses for quick checking")
