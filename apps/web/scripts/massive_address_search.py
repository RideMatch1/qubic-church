#!/usr/bin/env python3
"""
Massive Address Search - Find ALL potential 50 BTC addresses
=============================================================
Searches the entire Anna Matrix for CFB signature values and maps to Bitcoin blocks
"""

import json
import os
from collections import defaultdict

# CFB Signature Values to search for
CFB_VALUES = {
    27: "3³ (CFB ternary)",
    -27: "-(3³)",
    7: "Prime, transformation key",
    -7: "-7",
    121: "11² (NXT constant)",
    -121: "-11²",
    100: "Special position [22,22]",
    37: "CFB number",
    42: "CFB number",
    127: "2⁷-1 (Mersenne)",
    -128: "Min value",
}

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load Anna Matrix
    matrix_path = os.path.join(script_dir, '../public/data/anna-matrix.json')
    print("Loading Anna Matrix...")
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    matrix = data['matrix']
    print(f"Matrix size: {len(matrix)}x{len(matrix[0])}")

    # Load 3D layered addresses
    layered_path = os.path.join(script_dir, '../../../outputs/3d_layered_addresses.json')
    print("Loading 3d_layered_addresses.json...")
    with open(layered_path, 'r') as f:
        layered_data = json.load(f)

    # Create mappings
    addr_by_block = {a['blockHeight']: a for a in layered_data['all_addresses']}
    print(f"Loaded {len(addr_by_block)} addresses")
    print()

    # SEARCH 1: All cells with ±27 value
    print("=" * 70)
    print("SEARCH 1: ALL CELLS WITH VALUE ±27")
    print("=" * 70)

    cells_27 = []
    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value == 27 or value == -27:
                cells_27.append({
                    'row': row,
                    'col': col,
                    'value': value
                })

    print(f"Found {len(cells_27)} cells with ±27")
    print()

    # SEARCH 2: Diagonal cells with ±27 (Layer 0 mapping)
    print("=" * 70)
    print("SEARCH 2: DIAGONAL ±27 → DIRECT BLOCK MAPPING (Layer 0)")
    print("=" * 70)

    diagonal_blocks = []
    for i in range(128):
        value = matrix[i][i]
        if value == 27 or value == -27:
            if i in addr_by_block:
                diagonal_blocks.append({
                    'block': i,
                    'address': addr_by_block[i]['address'],
                    'diagonal_value': value,
                    'layer': 0
                })

    print(f"Diagonal ±27 blocks with addresses: {len(diagonal_blocks)}")
    for b in diagonal_blocks:
        print(f"  Block {b['block']}: {b['address']} (diagonal={b['diagonal_value']})")
    print()

    # SEARCH 3: 3D Layer mapping - check if matrix[block%128][block%128] = ±27
    print("=" * 70)
    print("SEARCH 3: 3D LAYER MAPPING (block → matrix[block%128, block%128])")
    print("=" * 70)

    layer_mapped = []
    for block, addr_data in addr_by_block.items():
        row = block % 128
        col = block % 128  # Same position for diagonal check
        value = matrix[row][col]
        if value == 27 or value == -27:
            layer = block // 16384
            layer_mapped.append({
                'block': block,
                'address': addr_data['address'],
                'matrix_position': [row, col],
                'diagonal_value': value,
                'layer': layer
            })

    print(f"Blocks where matrix[block%128, block%128] = ±27: {len(layer_mapped)}")

    # Group by layer
    by_layer = defaultdict(list)
    for b in layer_mapped:
        by_layer[b['layer']].append(b)

    for layer in sorted(by_layer.keys()):
        blocks = by_layer[layer]
        print(f"\n  Layer {layer}: {len(blocks)} blocks")
        for b in blocks[:5]:  # Show first 5 per layer
            print(f"    Block {b['block']}: {b['address']}")
        if len(blocks) > 5:
            print(f"    ... and {len(blocks)-5} more")
    print()

    # SEARCH 4: All cells with CFB values → map to blocks
    print("=" * 70)
    print("SEARCH 4: ALL CFB SIGNATURE VALUES IN MATRIX")
    print("=" * 70)

    cfb_cells = defaultdict(list)
    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value in CFB_VALUES:
                cfb_cells[value].append((row, col))

    for value, positions in sorted(cfb_cells.items()):
        desc = CFB_VALUES.get(value, "")
        print(f"Value {value:+4d} ({desc}): {len(positions)} occurrences")
    print()

    # SEARCH 5: Map position (row, col) to block height and find addresses
    print("=" * 70)
    print("SEARCH 5: POSITION-TO-BLOCK MAPPING FOR ±27 CELLS")
    print("=" * 70)

    # Formula: block = layer * 16384 + row * 128 + col
    position_mapped = []
    for cell in cells_27:
        row, col = cell['row'], cell['col']
        for layer in range(3):  # Check all 3 layers
            block = layer * 16384 + row * 128 + col
            if block in addr_by_block:
                position_mapped.append({
                    'row': row,
                    'col': col,
                    'value': cell['value'],
                    'layer': layer,
                    'block': block,
                    'address': addr_by_block[block]['address']
                })

    print(f"Total addresses from ±27 position mapping: {len(position_mapped)}")

    # Deduplicate by address
    unique_addresses = {}
    for pm in position_mapped:
        addr = pm['address']
        if addr not in unique_addresses:
            unique_addresses[addr] = pm

    print(f"Unique addresses: {len(unique_addresses)}")
    print()

    # Summary output
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    all_found_addresses = set()

    # Add diagonal blocks
    for b in diagonal_blocks:
        all_found_addresses.add(b['address'])

    # Add layer-mapped
    for b in layer_mapped:
        all_found_addresses.add(b['address'])

    # Add position-mapped
    for addr in unique_addresses:
        all_found_addresses.add(addr)

    print(f"\nTOTAL UNIQUE ADDRESSES FOUND: {len(all_found_addresses)}")
    print()

    # Save comprehensive results
    results = {
        'total_unique_addresses': len(all_found_addresses),
        'cells_with_27': len(cells_27),
        'diagonal_blocks': diagonal_blocks,
        'layer_mapped_blocks': layer_mapped,
        'position_mapped_blocks': list(unique_addresses.values()),
        'all_addresses': list(all_found_addresses)
    }

    output_path = os.path.join(script_dir, 'MASSIVE_ADDRESS_SEARCH_RESULTS.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_path}")

    # Print first 50 addresses
    print("\nFIRST 50 UNIQUE ADDRESSES:")
    print("-" * 50)
    for i, addr in enumerate(sorted(all_found_addresses)[:50]):
        print(f"{i+1:3d}. {addr}")

    if len(all_found_addresses) > 50:
        print(f"... and {len(all_found_addresses) - 50} more")

if __name__ == '__main__':
    main()
