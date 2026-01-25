#!/usr/bin/env python3
"""
PHASE 2: Patoshi-Derived Key Überlappung
========================================
Find overlaps between 21,953 Patoshi addresses and all derived keys.
"""

import json
import hashlib
import os
from collections import defaultdict

def pubkey_to_address(pubkey_hex):
    """Convert public key to Bitcoin P2PKH address."""
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        sha256 = hashlib.sha256(pubkey_bytes).digest()
        ripemd160 = hashlib.new('ripemd160', sha256).digest()
        versioned = b'\x00' + ripemd160
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        address_bytes = versioned + checksum

        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = int.from_bytes(address_bytes, 'big')
        result = ''
        while n > 0:
            n, remainder = divmod(n, 58)
            result = alphabet[remainder] + result

        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break

        return result
    except Exception as e:
        return None

def base58_decode(s):
    """Decode Base58 string to bytes."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = 0
    for char in s:
        if char not in alphabet:
            return None
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

print("=" * 80)
print("PHASE 2: Patoshi-Derived Key Overlap Detection")
print("=" * 80)

# Load Patoshi addresses
print("\n[1] Loading Patoshi addresses...")
patoshi_path = "../public/data/patoshi-addresses.json"
with open(patoshi_path) as f:
    patoshi_data = json.load(f)

patoshi_records = patoshi_data.get('records', [])
print("  Total Patoshi records: {}".format(len(patoshi_records)))

# Derive addresses from pubkeys
print("\n[2] Deriving addresses from Patoshi pubkeys...")
patoshi_addresses = set()
patoshi_address_to_block = {}

for record in patoshi_records:
    pubkey = record.get('pubkey', '')
    block = record.get('blockHeight', 0)
    if pubkey:
        addr = pubkey_to_address(pubkey)
        if addr:
            patoshi_addresses.add(addr)
            patoshi_address_to_block[addr] = block

print("  Successfully derived {} addresses".format(len(patoshi_addresses)))

# Load derived addresses from multiple sources
print("\n[3] Loading derived addresses from all sources...")
derived_addresses = {}  # address -> source info

# Source 1: bitcoin-private-keys.json
btc_keys_path = "../public/data/bitcoin-private-keys.json"
if os.path.exists(btc_keys_path):
    with open(btc_keys_path) as f:
        btc_data = json.load(f)
    for r in btc_data.get('records', []):
        addr = r.get('address', '')
        if addr:
            derived_addresses[addr] = {
                'source': 'bitcoin-private-keys',
                'method': r.get('method', 'unknown'),
                'position': r.get('position', []),
                'privateKey': r.get('privateKeyHex', '')
            }
    print("  bitcoin-private-keys.json: {} addresses".format(len(btc_data.get('records', []))))

# Source 2: bitcoin-derived-addresses.json
btc_derived_path = "../public/data/bitcoin-derived-addresses.json"
if os.path.exists(btc_derived_path):
    with open(btc_derived_path) as f:
        btc_derived_data = json.load(f)
    records = btc_derived_data.get('records', [])
    for r in records:
        addr = r.get('address', '')
        if addr and addr not in derived_addresses:
            derived_addresses[addr] = {
                'source': 'bitcoin-derived-addresses',
                'method': r.get('derivationMethod', 'unknown'),
                'seedIndex': r.get('seedIndex', -1)
            }
    print("  bitcoin-derived-addresses.json: {} addresses".format(len(records)))

# Source 3: ALL_BITCOIN_KEYS_FROM_SEEDS.json
seeds_keys_path = "ALL_BITCOIN_KEYS_FROM_SEEDS.json"
if os.path.exists(seeds_keys_path):
    with open(seeds_keys_path) as f:
        seeds_data = json.load(f)
    count = 0
    if isinstance(seeds_data, dict):
        for addr, info in seeds_data.items():
            if addr not in derived_addresses:
                derived_addresses[addr] = {
                    'source': 'ALL_BITCOIN_KEYS_FROM_SEEDS',
                    'method': info.get('method', 'sha256') if isinstance(info, dict) else 'sha256'
                }
                count += 1
    print("  ALL_BITCOIN_KEYS_FROM_SEEDS.json: {} new addresses".format(count))

print("\n  Total unique derived addresses: {}".format(len(derived_addresses)))

# Find exact matches
print("\n" + "=" * 80)
print("SEARCHING FOR EXACT MATCHES")
print("=" * 80)

exact_matches = []
for addr, info in derived_addresses.items():
    if addr in patoshi_addresses:
        exact_matches.append({
            'address': addr,
            'patoshi_block': patoshi_address_to_block.get(addr),
            'derived_info': info
        })

print("\n  EXACT MATCHES FOUND: {}".format(len(exact_matches)))

if exact_matches:
    print("\n" + "-" * 60)
    for match in exact_matches:
        print("\n  Address: {}".format(match['address']))
        print("  Patoshi Block: {}".format(match['patoshi_block']))
        print("  Derived Source: {}".format(match['derived_info'].get('source')))
        print("  Derived Method: {}".format(match['derived_info'].get('method')))
        if match['derived_info'].get('position'):
            print("  Matrix Position: {}".format(match['derived_info'].get('position')))

# Check for hash160 near-matches (first byte = 0x7b)
print("\n" + "=" * 80)
print("HASH160 FIRST BYTE ANALYSIS")
print("=" * 80)

# Count first bytes in Patoshi addresses
print("\n[4] Analyzing Patoshi address first bytes...")
patoshi_first_bytes = defaultdict(int)
patoshi_0x7b = []

for addr in patoshi_addresses:
    hash160 = get_hash160(addr)
    if hash160:
        first_byte = hash160[0]
        patoshi_first_bytes[first_byte] += 1
        if first_byte == 0x7b:
            patoshi_0x7b.append(addr)

print("\n  Top 10 most common first bytes in Patoshi:")
sorted_bytes = sorted(patoshi_first_bytes.items(), key=lambda x: x[1], reverse=True)
for fb, count in sorted_bytes[:10]:
    print("    0x{:02x} ({}): {} addresses".format(fb, fb, count))

print("\n  Patoshi addresses with first byte 0x7b: {}".format(len(patoshi_0x7b)))

if patoshi_0x7b:
    print("\n  These Patoshi addresses have 0x7b first byte:")
    for addr in patoshi_0x7b[:10]:
        block = patoshi_address_to_block.get(addr, '?')
        print("    Block {}: {}".format(block, addr))

# Check CFB signature addresses
print("\n" + "=" * 80)
print("CFB SIGNATURE ADDRESS CHECK")
print("=" * 80)

# Look for 1CFB in Patoshi
cfb_patterns = ['1CFB', '1CFi', '1CF4', '1CFZ', '1CFM']
print("\n  Checking for CFB pattern addresses in Patoshi...")

for pattern in cfb_patterns:
    matches = [addr for addr in patoshi_addresses if addr.startswith(pattern)]
    if matches:
        print("\n  Pattern '{}': {} matches".format(pattern, len(matches)))
        for addr in matches[:5]:
            block = patoshi_address_to_block.get(addr, '?')
            print("    Block {}: {}".format(block, addr))

# Save results
results = {
    'total_patoshi': len(patoshi_addresses),
    'total_derived': len(derived_addresses),
    'exact_matches': exact_matches,
    'patoshi_0x7b_count': len(patoshi_0x7b),
    'patoshi_0x7b_addresses': patoshi_0x7b[:100],  # First 100
    'first_byte_distribution': {hex(k): v for k, v in sorted_bytes[:20]}
}

output_path = "PATOSHI_DERIVED_OVERLAP_RESULTS.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 80)
print("Results saved to {}".format(output_path))
print("=" * 80)
