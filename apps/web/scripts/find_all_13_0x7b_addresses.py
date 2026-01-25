#!/usr/bin/env python3
"""
FIND ALL 13 ADDRESSES WITH 0x7b + BYTE SUM 2299

The search output showed 13 addresses with first byte 0x7b.
Let's find ALL of them across ALL result files!
"""

import json
import os
from collections import defaultdict

def base58_decode(address):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    try:
        num = 0
        for char in address:
            num = num * 58 + alphabet.index(char)
        combined = num.to_bytes(25, byteorder='big')
        return combined[1:-4]
    except:
        return None

def search_recursively(obj, source):
    """Recursively find addresses"""
    found = []

    if isinstance(obj, dict):
        addr = obj.get('address') or obj.get('btcAddress')
        if addr and isinstance(addr, str):
            h160 = base58_decode(addr)
            if h160 and len(h160) == 20:
                byte_sum = sum(h160)
                if byte_sum == 2299 and h160[0] == 0x7b:
                    found.append({
                        'address': addr,
                        'hash160': h160.hex(),
                        'source': source,
                        'record': obj
                    })

        for value in obj.values():
            found.extend(search_recursively(value, source))

    elif isinstance(obj, list):
        for item in obj:
            found.extend(search_recursively(item, source))

    return found

print("=" * 80)
print("FINDING ALL 0x7b + BYTE SUM 2299 ADDRESSES")
print("=" * 80)
print()

result_files = [
    'K12_OFFICIAL_QUBIC_RESULTS.json',
    'K12_TRANSFORM_RESULTS.json',
    'PATTERN_ANALYSIS_RESULTS.json',
    'UNEXPLORED_SEEDS_RESULTS.json',
    'CF_ADDRESS_ANALYSIS.json',
    'MATRIX_CF_ADDRESS_ANALYSIS.json',
    'CURL_HASH_TEST_RESULTS.json',
    'SIMILAR_ADDRESSES_ANALYSIS.json',
    'MULTI_ADDRESS_ANALYSIS.json',
    'MARIA_ADDRESS_MIRROR_ANALYSIS.json'
]

all_found = []

for filename in result_files:
    if not os.path.exists(filename):
        continue

    print(f"Searching: {filename}")

    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        found = search_recursively(data, filename)
        all_found.extend(found)
        print(f"  Found: {len(found)} addresses")

    except Exception as e:
        print(f"  Error: {e}")

print()
print("=" * 80)
print("DEDUPLICATION")
print("=" * 80)
print()

# Deduplicate by address
unique = {}
for item in all_found:
    addr = item['address']
    if addr not in unique:
        unique[addr] = item
        unique[addr]['sources'] = [item['source']]
    else:
        if item['source'] not in unique[addr]['sources']:
            unique[addr]['sources'].append(item['source'])

print(f"Total found (with duplicates): {len(all_found)}")
print(f"Unique addresses: {len(unique)}")
print()

print("=" * 80)
print("ALL UNIQUE 0x7b + BYTE SUM 2299 ADDRESSES")
print("=" * 80)
print()

sorted_addrs = sorted(unique.values(), key=lambda x: x['address'])

for i, item in enumerate(sorted_addrs, 1):
    print(f"{i}. {item['address']}")
    print(f"   Hash160: {item['hash160']}")
    print(f"   Sources: {', '.join(item['sources'])}")

    # Extract method if available
    rec = item['record']
    if 'method' in rec:
        print(f"   Method: {rec['method']}")
    if 'seed' in rec:
        seed = rec['seed']
        if seed:
            print(f"   Seed: {seed[:50]}...")
    if 'seed_id' in rec:
        print(f"   Seed ID: {rec['seed_id']}")

    print()

# Save results
output = {
    'total_unique': len(unique),
    'addresses': sorted_addrs
}

with open('ALL_0x7b_2299_ADDRESSES.json', 'w') as f:
    json.dump(output, f, indent=2)

print("=" * 80)
print(f"Results saved to: ALL_0x7b_2299_ADDRESSES.json")
print(f"Total unique: {len(unique)}")
print("=" * 80)
