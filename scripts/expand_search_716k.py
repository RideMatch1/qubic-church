#!/usr/bin/env python3
"""
EXPANDED MATRIX SEARCH - Looking for 716k BTC
CFB mentioned 716k BTC to be sold this year.
Let's expand our search beyond the current 231k BTC.
"""
import numpy as np
import json
from pathlib import Path

def expand_search():
    print("🔍 EXPANDING MATRIX SEARCH FOR 716K BTC TARGET")
    print("=" * 80)
    
    grid = np.load("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
    patoshi_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/patoshi-addresses.json"
    
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)
    
    total_patoshi = patoshi_data['total']
    print(f"📊 Total Patoshi records: {total_patoshi:,}")
    print(f"💰 Total Patoshi BTC: {total_patoshi * 50:,} BTC")
    
    # Create mapping for ALL Patoshi blocks
    patoshi_map = {}
    for r in patoshi_data['records']:
        h = r['blockHeight']
        if h not in patoshi_map:
            patoshi_map[h] = []
        patoshi_map[h].append(r)
    
    print(f"\n🎯 Unique Patoshi block heights: {len(patoshi_map):,}")
    
    # EXPANDED SEARCH STRATEGIES
    strategies = []
    
    # Strategy 1: Linear mapping (current - 128x128 = 16,384 blocks)
    strategy1_matches = set()
    for r in range(128):
        for c in range(128):
            height = r * 128 + c
            if height in patoshi_map:
                strategy1_matches.add(height)
    
    strategies.append({
        'name': 'Linear (r*128+c)',
        'formula': 'height = r * 128 + c',
        'max_height': 16383,
        'matches': len(strategy1_matches),
        'btc': len(strategy1_matches) * 50
    })
    
    # Strategy 2: Column-only mapping (128 blocks)
    strategy2_matches = set()
    for c in range(128):
        if c in patoshi_map:
            strategy2_matches.add(c)
    
    strategies.append({
        'name': 'Column-only (c)',
        'formula': 'height = c',
        'max_height': 127,
        'matches': len(strategy2_matches),
        'btc': len(strategy2_matches) * 50
    })
    
    # Strategy 3: Row-only mapping (128 blocks)
    strategy3_matches = set()
    for r in range(128):
        if r in patoshi_map:
            strategy3_matches.add(r)
    
    strategies.append({
        'name': 'Row-only (r)',
        'formula': 'height = r',
        'max_height': 127,
        'matches': len(strategy3_matches),
        'btc': len(strategy3_matches) * 50
    })
    
    # Strategy 4: Diagonal mapping (128 blocks)
    strategy4_matches = set()
    for i in range(128):
        if i in patoshi_map:
            strategy4_matches.add(i)
    
    strategies.append({
        'name': 'Diagonal (r=c)',
        'formula': 'height = r (where r=c)',
        'max_height': 127,
        'matches': len(strategy4_matches),
        'btc': len(strategy4_matches) * 50
    })
    
    # Strategy 5: Reverse linear (c*128+r)
    strategy5_matches = set()
    for r in range(128):
        for c in range(128):
            height = c * 128 + r
            if height in patoshi_map:
                strategy5_matches.add(height)
    
    strategies.append({
        'name': 'Reverse Linear (c*128+r)',
        'formula': 'height = c * 128 + r',
        'max_height': 16383,
        'matches': len(strategy5_matches),
        'btc': len(strategy5_matches) * 50
    })
    
    # Strategy 6: Layered mapping (using 3rd dimension)
    strategy6_matches = set()
    for r in range(128):
        for c in range(128):
            for layer in range(3):
                height = (layer * 128 * 128) + (r * 128) + c
                if height in patoshi_map:
                    strategy6_matches.add(height)
    
    strategies.append({
        'name': '3D Layered (layer*128²+r*128+c)',
        'formula': 'height = layer * 16384 + r * 128 + c',
        'max_height': 49151,
        'matches': len(strategy6_matches),
        'btc': len(strategy6_matches) * 50
    })
    
    # Strategy 7: XOR-based mapping
    strategy7_matches = set()
    for r in range(128):
        for c in range(128):
            val = int(grid[r, c, 1] ^ grid[r, c, 0])
            if val in patoshi_map:
                strategy7_matches.add(val)
    
    strategies.append({
        'name': 'XOR Value Direct',
        'formula': 'height = grid[r,c,1] XOR grid[r,c,0]',
        'max_height': 255,
        'matches': len(strategy7_matches),
        'btc': len(strategy7_matches) * 50
    })
    
    # Strategy 8: Combined r+c mapping
    strategy8_matches = set()
    for r in range(128):
        for c in range(128):
            height = r + c
            if height in patoshi_map:
                strategy8_matches.add(height)
    
    strategies.append({
        'name': 'Sum (r+c)',
        'formula': 'height = r + c',
        'max_height': 254,
        'matches': len(strategy8_matches),
        'btc': len(strategy8_matches) * 50
    })
    
    # Print results
    print("\n" + "=" * 80)
    print("MAPPING STRATEGY RESULTS")
    print("=" * 80)
    
    for s in strategies:
        print(f"\n📍 {s['name']}")
        print(f"   Formula: {s['formula']}")
        print(f"   Max Height: {s['max_height']:,}")
        print(f"   Matches: {s['matches']:,} blocks")
        print(f"   BTC: {s['btc']:,} BTC (${s['btc'] * 96000:,.0f} at $96k)")
    
    # Find best strategy
    best = max(strategies, key=lambda x: x['btc'])
    print("\n" + "=" * 80)
    print(f"🏆 BEST STRATEGY: {best['name']}")
    print(f"💰 Total BTC: {best['btc']:,} BTC")
    print(f"💵 Value: ${best['btc'] * 96000:,.0f}")
    print("=" * 80)
    
    # Check if we're close to 716k target
    target_btc = 716000
    target_blocks = target_btc // 50
    
    print(f"\n🎯 TARGET: {target_btc:,} BTC ({target_blocks:,} blocks)")
    print(f"📊 FOUND: {best['btc']:,} BTC ({best['matches']:,} blocks)")
    print(f"📉 GAP: {target_btc - best['btc']:,} BTC ({target_blocks - best['matches']:,} blocks)")
    print(f"📈 COVERAGE: {best['btc'] / target_btc * 100:.1f}%")
    
    # Save results
    output = {
        'target_btc': target_btc,
        'target_blocks': target_blocks,
        'strategies': strategies,
        'best_strategy': best,
        'gap_btc': target_btc - best['btc'],
        'gap_blocks': target_blocks - best['matches'],
        'coverage_percent': best['btc'] / target_btc * 100
    }
    
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/expanded_search_716k.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    
    return strategies, best

if __name__ == "__main__":
    expand_search()
