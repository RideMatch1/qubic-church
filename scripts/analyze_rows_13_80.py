#!/usr/bin/env python3
"""
ROW 13 & 80 DEEP ANALYSIS
These rows have the highest concentration of Patoshi blocks.
They may hold the key to understanding the seed generation pattern.
"""
import json
import numpy as np
import hashlib
import base58
from collections import defaultdict

def hash160(data):
    sha = hashlib.sha256(data).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    return ripe

def pubkey_to_address(pubkey_hex):
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    h160 = hash160(pubkey_bytes)
    versioned = b'\x00' + h160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    address = base58.b58encode(versioned + checksum).decode('ascii')
    return address

def analyze_rows_13_80():
    print("🔬 DEEP ANALYSIS: ROWS 13 & 80")
    print("=" * 80)
    
    # Load data
    grid = np.load("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
    patoshi_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/patoshi-addresses.json"
    
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)
    
    patoshi_map = {}
    for r in patoshi_data['records']:
        h = r['blockHeight']
        if h not in patoshi_map:
            patoshi_map[h] = []
        patoshi_map[h].append(r)
    
    # Analyze specific rows
    target_rows = [13, 80]
    results = {}
    
    for target_row in target_rows:
        print(f"\n{'='*80}")
        print(f"ANALYZING ROW {target_row}")
        print(f"{'='*80}")
        
        row_blocks = []
        
        # Check all layers
        for layer in range(3):
            for c in range(128):
                height = (layer * 128 * 128) + (target_row * 128) + c
                if height in patoshi_map:
                    for record in patoshi_map[height]:
                        address = pubkey_to_address(record['pubkey'])
                        
                        # Calculate Hash160 properties
                        h160 = bytes.fromhex(record['pubkey'])
                        h160_hash = hash160(h160)
                        byte_sum = sum(h160_hash)
                        
                        # Matrix values at this position
                        v0 = int(grid[target_row, c, 0])
                        v1 = int(grid[target_row, c, 1])
                        v2 = int(grid[target_row, c, 2])
                        xor01 = v1 ^ v0
                        xor12 = v2 ^ v1
                        xor02 = v2 ^ v0
                        
                        row_blocks.append({
                            'layer': layer,
                            'row': target_row,
                            'col': c,
                            'height': height,
                            'address': address,
                            'pubkey': record['pubkey'],
                            'byte_sum': byte_sum,
                            'mod_121': byte_sum % 121,
                            'mod_27': byte_sum % 27,
                            'mod_19': byte_sum % 19,
                            'mod_13': byte_sum % 13,
                            'mod_11': byte_sum % 11,
                            'mod_7': byte_sum % 7,
                            'matrix_v0': v0,
                            'matrix_v1': v1,
                            'matrix_v2': v2,
                            'matrix_xor01': xor01,
                            'matrix_xor12': xor12,
                            'matrix_xor02': xor02
                        })
        
        # Sort by height
        row_blocks.sort(key=lambda x: x['height'])
        
        print(f"\n📊 STATISTICS FOR ROW {target_row}:")
        print(f"   Total blocks: {len(row_blocks)}")
        print(f"   Total BTC: {len(row_blocks) * 50:,}")
        
        # Layer distribution
        layer_dist = defaultdict(int)
        for b in row_blocks:
            layer_dist[b['layer']] += 1
        
        print(f"\n   Layer distribution:")
        for layer in sorted(layer_dist.keys()):
            print(f"      Layer {layer}: {layer_dist[layer]} blocks")
        
        # Analyze mathematical properties
        print(f"\n🔢 MATHEMATICAL PROPERTIES:")
        
        # Byte sum distribution
        byte_sums = [b['byte_sum'] for b in row_blocks]
        print(f"   Byte sum range: {min(byte_sums)} - {max(byte_sums)}")
        print(f"   Byte sum mean: {sum(byte_sums) / len(byte_sums):.1f}")
        
        # Special modulo counts
        mod_counts = {
            'mod_121_zero': sum(1 for b in row_blocks if b['mod_121'] == 0),
            'mod_27_zero': sum(1 for b in row_blocks if b['mod_27'] == 0),
            'mod_19_zero': sum(1 for b in row_blocks if b['mod_19'] == 0),
            'mod_13_zero': sum(1 for b in row_blocks if b['mod_13'] == 0),
            'mod_11_zero': sum(1 for b in row_blocks if b['mod_11'] == 0),
            'mod_7_zero': sum(1 for b in row_blocks if b['mod_7'] == 0)
        }
        
        print(f"\n   Special modulo properties:")
        for key, count in mod_counts.items():
            if count > 0:
                print(f"      {key}: {count} addresses ({count/len(row_blocks)*100:.1f}%)")
        
        # Matrix value patterns
        print(f"\n🎯 MATRIX VALUE PATTERNS:")
        
        # XOR value distribution
        xor01_values = defaultdict(int)
        xor12_values = defaultdict(int)
        xor02_values = defaultdict(int)
        
        for b in row_blocks:
            xor01_values[b['matrix_xor01']] += 1
            xor12_values[b['matrix_xor12']] += 1
            xor02_values[b['matrix_xor02']] += 1
        
        # Top XOR values
        print(f"\n   Top XOR(v1,v0) values:")
        for val, count in sorted(xor01_values.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {val}: {count} occurrences")
        
        print(f"\n   Top XOR(v2,v1) values:")
        for val, count in sorted(xor12_values.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {val}: {count} occurrences")
        
        # Sample addresses
        print(f"\n📋 SAMPLE ADDRESSES (first 5):")
        for i, b in enumerate(row_blocks[:5], 1):
            print(f"\n   {i}. Block {b['height']} (Layer {b['layer']}, Col {b['col']})")
            print(f"      Address: {b['address']}")
            print(f"      Byte sum: {b['byte_sum']} (mod 121={b['mod_121']}, mod 27={b['mod_27']})")
            print(f"      Matrix XOR: v01={b['matrix_xor01']}, v12={b['matrix_xor12']}")
        
        # Store results
        results[f'row_{target_row}'] = {
            'total_blocks': len(row_blocks),
            'total_btc': len(row_blocks) * 50,
            'layer_distribution': dict(layer_dist),
            'byte_sum_stats': {
                'min': min(byte_sums),
                'max': max(byte_sums),
                'mean': sum(byte_sums) / len(byte_sums)
            },
            'modulo_counts': mod_counts,
            'all_blocks': row_blocks
        }
    
    # Cross-row comparison
    print(f"\n{'='*80}")
    print("CROSS-ROW COMPARISON")
    print(f"{'='*80}")
    
    row13_sums = [b['byte_sum'] for b in results['row_13']['all_blocks']]
    row80_sums = [b['byte_sum'] for b in results['row_80']['all_blocks']]
    
    print(f"\nRow 13 vs Row 80:")
    print(f"   Blocks: {len(row13_sums)} vs {len(row80_sums)}")
    print(f"   Mean byte sum: {sum(row13_sums)/len(row13_sums):.1f} vs {sum(row80_sums)/len(row80_sums):.1f}")
    print(f"   Byte sum overlap: {len(set(row13_sums) & set(row80_sums))} common values")
    
    # Check for patterns
    print(f"\n🔍 PATTERN DETECTION:")
    
    # Check if row number correlates with properties
    for row_key in ['row_13', 'row_80']:
        row_num = int(row_key.split('_')[1])
        blocks = results[row_key]['all_blocks']
        
        # Check if row number appears in modulo operations
        mod_row_matches = sum(1 for b in blocks if b['byte_sum'] % row_num == 0)
        print(f"\n   Row {row_num}:")
        print(f"      Addresses with byte_sum % {row_num} == 0: {mod_row_matches} ({mod_row_matches/len(blocks)*100:.1f}%)")
        
        # Check if row number appears in XOR values
        xor_row_matches = sum(1 for b in blocks if b['matrix_xor01'] == row_num or b['matrix_xor12'] == row_num)
        print(f"      Addresses with XOR == {row_num}: {xor_row_matches}")
    
    # Save results
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/rows_13_80_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Full analysis saved to: {output_path}")
    
    return results

if __name__ == "__main__":
    analyze_rows_13_80()
