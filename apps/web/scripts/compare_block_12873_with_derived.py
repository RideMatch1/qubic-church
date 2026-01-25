#!/usr/bin/env python3
"""
PHASE 1: Block 12873 Ähnlichkeitsanalyse
========================================
Compare Block 12873 address with all derived 1CF addresses.
"""

import json
import hashlib
import os

# Block 12873 address
BLOCK_12873_ADDRESS = "1Loo8Lw74rtdRA6PqRho8nq86SrNSDg99L"

def base58_decode(s):
    """Decode Base58 string to bytes."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = 0
    for char in s:
        if char not in alphabet:
            return None  # Invalid character
        num = num * 58 + alphabet.index(char)
    result = []
    while num > 0:
        result.append(num % 256)
        num //= 256
    for char in s:
        if char == '1':
            result.append(0)
        else:
            break
    return bytes(reversed(result))

def get_hash160(address):
    """Extract hash160 from Bitcoin address."""
    decoded = base58_decode(address)
    if decoded is None or len(decoded) < 21:
        return None
    return decoded[1:21]

def hamming_distance(bytes1, bytes2):
    """Calculate Hamming distance between two byte sequences."""
    if len(bytes1) != len(bytes2):
        return float('inf')
    return sum(b1 != b2 for b1, b2 in zip(bytes1, bytes2))

def xor_bytes(bytes1, bytes2):
    """XOR two byte sequences."""
    return bytes(a ^ b for a, b in zip(bytes1, bytes2))

def byte_sum(data):
    """Sum all bytes."""
    return sum(data)

def common_prefix_length(bytes1, bytes2):
    """Find length of common prefix."""
    length = 0
    for b1, b2 in zip(bytes1, bytes2):
        if b1 == b2:
            length += 1
        else:
            break
    return length

print("=" * 80)
print("PHASE 1: Block 12873 Similarity Analysis")
print("=" * 80)

# Get Block 12873 hash160
block_12873_hash160 = get_hash160(BLOCK_12873_ADDRESS)
block_12873_byte_sum = byte_sum(block_12873_hash160)

print("\nBlock 12873 Analysis:")
print("  Address: {}".format(BLOCK_12873_ADDRESS))
print("  Hash160: {}".format(block_12873_hash160.hex()))
print("  Byte Sum: {}".format(block_12873_byte_sum))
print("  First Byte: 0x{:02x} ({})".format(block_12873_hash160[0], block_12873_hash160[0]))

# Load derived addresses
derived_addresses = []

# Load from bitcoin-private-keys.json
btc_keys_path = "../public/data/bitcoin-private-keys.json"
if os.path.exists(btc_keys_path):
    with open(btc_keys_path) as f:
        btc_data = json.load(f)
    records = btc_data.get('records', [])
    for r in records:
        addr = r.get('address', '')
        if addr:
            derived_addresses.append({
                'address': addr,
                'source': 'bitcoin-private-keys',
                'method': r.get('method', 'unknown'),
                'position': r.get('position', [])
            })
    print("\nLoaded {} addresses from bitcoin-private-keys.json".format(len(records)))

# Load from CF_ADDRESS_ANALYSIS.json if exists
cf_path = "CF_ADDRESS_ANALYSIS.json"
if os.path.exists(cf_path):
    with open(cf_path) as f:
        cf_data = json.load(f)
    if isinstance(cf_data, list):
        for r in cf_data:
            addr = r.get('address', '')
            if addr and addr not in [d['address'] for d in derived_addresses]:
                derived_addresses.append({
                    'address': addr,
                    'source': 'CF_ADDRESS_ANALYSIS',
                    'byte_sum': r.get('byte_sum', 0)
                })
    print("Loaded additional addresses from CF_ADDRESS_ANALYSIS.json")

print("\nTotal derived addresses to compare: {}".format(len(derived_addresses)))

# Analyze similarities
print("\n" + "=" * 80)
print("SIMILARITY ANALYSIS")
print("=" * 80)

results = {
    'block_12873': {
        'address': BLOCK_12873_ADDRESS,
        'hash160': block_12873_hash160.hex(),
        'byte_sum': block_12873_byte_sum,
        'first_byte': block_12873_hash160[0]
    },
    'comparisons': [],
    'statistics': {}
}

# Compare with each derived address
best_matches = []
byte_sum_2299_matches = []
first_byte_matches = []

for entry in derived_addresses:
    addr = entry['address']
    hash160 = get_hash160(addr)

    if hash160 is None:
        continue

    # Calculate metrics
    hamming = hamming_distance(block_12873_hash160, hash160)
    xor_result = xor_bytes(block_12873_hash160, hash160)
    addr_byte_sum = byte_sum(hash160)
    prefix_len = common_prefix_length(block_12873_hash160, hash160)

    comparison = {
        'address': addr,
        'source': entry.get('source', 'unknown'),
        'method': entry.get('method', 'unknown'),
        'position': entry.get('position', []),
        'hash160': hash160.hex(),
        'byte_sum': addr_byte_sum,
        'first_byte': hash160[0],
        'hamming_distance': hamming,
        'xor_result_sum': byte_sum(xor_result),
        'common_prefix_length': prefix_len,
        'byte_sum_diff': abs(addr_byte_sum - block_12873_byte_sum)
    }

    results['comparisons'].append(comparison)

    # Track special matches
    if hamming <= 5:  # Very similar
        best_matches.append(comparison)

    if addr_byte_sum == 2299:
        byte_sum_2299_matches.append(comparison)

    if hash160[0] == block_12873_hash160[0]:
        first_byte_matches.append(comparison)

# Sort by Hamming distance
results['comparisons'].sort(key=lambda x: x['hamming_distance'])

# Statistics
hamming_values = [c['hamming_distance'] for c in results['comparisons']]
byte_sum_values = [c['byte_sum'] for c in results['comparisons']]

results['statistics'] = {
    'total_compared': len(results['comparisons']),
    'avg_hamming_distance': sum(hamming_values) / len(hamming_values) if hamming_values else 0,
    'min_hamming_distance': min(hamming_values) if hamming_values else 0,
    'max_hamming_distance': max(hamming_values) if hamming_values else 0,
    'byte_sum_2299_count': len(byte_sum_2299_matches),
    'first_byte_match_count': len(first_byte_matches),
    'block_12873_byte_sum': block_12873_byte_sum,
    'byte_sum_2299_diff': abs(block_12873_byte_sum - 2299)
}

# Print results
print("\nStatistics:")
print("  Total addresses compared: {}".format(results['statistics']['total_compared']))
print("  Average Hamming distance: {:.2f}".format(results['statistics']['avg_hamming_distance']))
print("  Min Hamming distance: {}".format(results['statistics']['min_hamming_distance']))
print("  Max Hamming distance: {}".format(results['statistics']['max_hamming_distance']))
print("  Addresses with byte_sum = 2299: {}".format(results['statistics']['byte_sum_2299_count']))
print("  Addresses with same first byte: {}".format(results['statistics']['first_byte_match_count']))
print("  Block 12873 byte_sum: {}".format(block_12873_byte_sum))
print("  Difference to 2299: {}".format(results['statistics']['byte_sum_2299_diff']))

print("\n" + "-" * 60)
print("TOP 10 MOST SIMILAR ADDRESSES (by Hamming distance)")
print("-" * 60)

for i, comp in enumerate(results['comparisons'][:10]):
    print("\n{}. {}".format(i+1, comp['address']))
    print("   Source: {}, Method: {}".format(comp['source'], comp['method']))
    print("   Hamming: {}, Byte Sum: {}, First Byte: 0x{:02x}".format(
        comp['hamming_distance'], comp['byte_sum'], comp['first_byte']))
    if comp.get('position'):
        print("   Position: {}".format(comp['position']))

if byte_sum_2299_matches:
    print("\n" + "-" * 60)
    print("ADDRESSES WITH BYTE_SUM = 2299")
    print("-" * 60)
    for comp in byte_sum_2299_matches[:10]:
        print("\n  {} (Hamming: {})".format(comp['address'], comp['hamming_distance']))

# Check for 11-chain connections
print("\n" + "-" * 60)
print("11-CHAIN CONNECTION ANALYSIS")
print("-" * 60)

print("\nBlock 12873 byte_sum = {}".format(block_12873_byte_sum))
print("  mod 11 = {}".format(block_12873_byte_sum % 11))
print("  mod 121 = {}".format(block_12873_byte_sum % 121))
print("  mod 2299 = {}".format(block_12873_byte_sum % 2299))

# Check if byte_sum relates to 11-chain
if block_12873_byte_sum % 11 == 0:
    print("  DIVISIBLE BY 11!")
if block_12873_byte_sum % 121 == 0:
    print("  DIVISIBLE BY 121!")

# XOR analysis with key numbers
print("\n" + "-" * 60)
print("XOR ANALYSIS WITH CFB SIGNATURE NUMBERS")
print("-" * 60)

cfb_numbers = [27, 121, 127, 137, 2299, 343, 576]
for n in cfb_numbers:
    xor_val = block_12873_byte_sum ^ n
    print("  {} XOR {} = {}".format(block_12873_byte_sum, n, xor_val))

# Save results
output_path = "BLOCK_12873_SIMILARITY_ANALYSIS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 80)
print("Results saved to {}".format(output_path))
print("=" * 80)
