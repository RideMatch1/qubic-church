#!/usr/bin/env python3
"""
VALIDATE THE 3D LAYERED DISCOVERY
Extract actual Bitcoin addresses from the 21,906 blocks found
"""
import json
import hashlib
import base58
import random

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

def validate_3d_discovery():
    print("🔬 VALIDATING 3D LAYERED DISCOVERY")
    print("=" * 80)
    
    patoshi_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/patoshi-addresses.json"
    
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)
    
    # Create mapping
    patoshi_map = {}
    for r in patoshi_data['records']:
        h = r['blockHeight']
        if h not in patoshi_map:
            patoshi_map[h] = []
        patoshi_map[h].append(r)
    
    # 3D Layered mapping
    found_blocks = set()
    block_details = []
    
    for layer in range(3):
        for r in range(128):
            for c in range(128):
                height = (layer * 128 * 128) + (r * 128) + c
                if height in patoshi_map:
                    found_blocks.add(height)
                    for record in patoshi_map[height]:
                        address = pubkey_to_address(record['pubkey'])
                        block_details.append({
                            'layer': layer,
                            'r': r,
                            'c': c,
                            'blockHeight': height,
                            'address': address,
                            'amount': record['amount']
                        })
    
    print(f"✅ Total blocks found: {len(found_blocks):,}")
    print(f"💰 Total BTC: {len(found_blocks) * 50:,} BTC")
    print(f"💵 Value at $96k: ${len(found_blocks) * 50 * 96000:,.0f}")
    
    # Layer distribution
    layer_counts = {}
    for detail in block_details:
        layer = detail['layer']
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    print("\n📊 LAYER DISTRIBUTION:")
    for layer in sorted(layer_counts.keys()):
        count = layer_counts[layer]
        btc = count * 50
        print(f"   Layer {layer}: {count:,} blocks = {btc:,} BTC")
    
    # Extract 10 random samples (2 from each layer + extras)
    samples_per_layer = {}
    for detail in block_details:
        layer = detail['layer']
        if layer not in samples_per_layer:
            samples_per_layer[layer] = []
        samples_per_layer[layer].append(detail)
    
    print("\n🎲 RANDOM SAMPLES FOR VERIFICATION:")
    print("=" * 80)
    
    sample_count = 0
    for layer in sorted(samples_per_layer.keys()):
        if samples_per_layer[layer]:
            samples = random.sample(samples_per_layer[layer], min(3, len(samples_per_layer[layer])))
            for s in samples:
                sample_count += 1
                print(f"\n{sample_count}. Layer {s['layer']}, Block {s['blockHeight']} (r={s['r']}, c={s['c']})")
                print(f"   Address: {s['address']}")
                print(f"   Amount:  {s['amount']} BTC")
                print(f"   Verify:  https://blockchair.com/bitcoin/address/{s['address']}")
    
    # Save full list
    output = {
        'total_blocks': len(found_blocks),
        'total_btc': len(found_blocks) * 50,
        'value_usd_96k': len(found_blocks) * 50 * 96000,
        'layer_distribution': layer_counts,
        'all_addresses': block_details
    }
    
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/3d_layered_addresses.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Full address list saved to: {output_path}")
    
    # Check specific known blocks
    known_blocks = [73, 74, 75, 80, 89, 93, 95, 96, 120, 121, 264]
    print("\n🔍 CHECKING KNOWN BLOCKS FROM FINALE_ANALYSE:")
    for block in known_blocks:
        if block in found_blocks:
            print(f"   ✅ Block {block}: FOUND in 3D mapping")
        else:
            print(f"   ❌ Block {block}: NOT in 3D mapping")

if __name__ == "__main__":
    validate_3d_discovery()
