#!/usr/bin/env python3
"""
Derive actual Bitcoin addresses from public keys in Patoshi data.
This allows us to verify addresses on blockchain explorers.
"""
import json
import hashlib
import base58

def hash160(data):
    """RIPEMD160(SHA256(data))"""
    sha = hashlib.sha256(data).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    return ripe

def pubkey_to_address(pubkey_hex):
    """Convert public key to Bitcoin address (P2PKH)"""
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    
    # Hash160
    h160 = hash160(pubkey_bytes)
    
    # Add version byte (0x00 for mainnet)
    versioned = b'\x00' + h160
    
    # Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    
    # Encode in Base58
    address = base58.b58encode(versioned + checksum).decode('ascii')
    return address

def extract_addresses():
    patoshi_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/patoshi-addresses.json"
    matches_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/expanded_patoshi_matches.json"
    
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)
    
    with open(matches_path, 'r') as f:
        matches_data = json.load(f)
    
    # Get all matched block heights
    matched_heights = set()
    for m in matches_data['matches']:
        matched_heights.add(m['record']['blockHeight'])
    
    # Convert to addresses
    address_list = []
    for record in patoshi_data['records']:
        if record['blockHeight'] in matched_heights:
            pubkey = record['pubkey']
            address = pubkey_to_address(pubkey)
            address_list.append({
                'blockHeight': record['blockHeight'],
                'address': address,
                'amount': record['amount'],
                'pubkey': pubkey
            })
    
    # Sort by block height
    address_list.sort(key=lambda x: x['blockHeight'])
    
    # Save full list
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_btc_addresses.json"
    with open(output_path, 'w') as f:
        json.dump({
            'total_addresses': len(address_list),
            'total_btc': len(address_list) * 50,
            'addresses': address_list
        }, f, indent=2)
    
    print(f"✅ Converted {len(address_list)} addresses")
    print(f"💰 Total BTC: {len(address_list) * 50:,} BTC")
    print(f"💵 Value at $96k: ${len(address_list) * 50 * 96000:,.0f}")
    
    # Extract 5 random samples for verification
    import random
    samples = random.sample(address_list, min(5, len(address_list)))
    
    print("\n🎲 5 RANDOM SAMPLES FOR VERIFICATION:")
    print("=" * 80)
    for i, s in enumerate(samples, 1):
        print(f"\n{i}. Block {s['blockHeight']}")
        print(f"   Address: {s['address']}")
        print(f"   Amount:  {s['amount']} BTC")
        print(f"   Verify:  https://blockchair.com/bitcoin/address/{s['address']}")
    
    return address_list

if __name__ == "__main__":
    extract_addresses()
