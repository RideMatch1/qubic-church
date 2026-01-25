#!/usr/bin/env python3
"""
🔥 K12 PRIVATE KEY DERIVATION - THE CORRECT METHOD! 🔥
=====================================================

Based on official Qubic documentation:
"A 55 lowercase alpha seed is used externally, which is mapped
to binary values 0 to 25 and then K12 hashed twice to make the
actual 256 bit privatekey."

Source: https://medium.com/@qsilver97/qubic-crypto-details-2dc77ce27af4

CRITICAL: Using CORRECT Genesis issuer address:
POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD
(Not the old POCZRDYU... address!)
"""

# CORRECT GENESIS ISSUER ADDRESS
GENESIS_ISSUER = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

import json
import ecdsa
from ecdsa import SigningKey, SECP256k1

try:
    from Crypto.Hash import KangarooTwelve
    has_k12 = True
except ImportError:
    has_k12 = False
    print("⚠️  KangarooTwelve not available - trying alternative implementation")

def map_seed_to_binary(seed):
    """
    Map 55 lowercase alpha seed to binary values 0-25
    a=0, b=1, c=2, ..., z=25
    """
    binary = bytearray()
    for char in seed.lower():
        if 'a' <= char <= 'z':
            binary.append(ord(char) - ord('a'))
        else:
            # If non-alpha, skip or handle
            pass
    return bytes(binary)

def k12_hash_simple(data):
    """
    Simple K12 implementation using SHA3-256 as fallback
    (K12 is based on Keccak, similar to SHA3)
    """
    import hashlib
    # Use SHA3-256 as approximation if K12 not available
    return hashlib.sha3_256(data).digest()

def derive_private_key_k12(seed):
    """
    Derive private key using K12 double hash method

    Steps:
    1. Map seed characters to 0-25
    2. K12 hash once
    3. K12 hash twice
    4. Result is 256-bit private key
    """
    # Step 1: Map to binary
    binary = map_seed_to_binary(seed)

    # Step 2: First K12 hash
    if has_k12:
        k12_1 = KangarooTwelve.new()
        k12_1.update(binary)
        hash1 = k12_1.read(32)  # 256 bits (32 bytes)
    else:
        hash1 = k12_hash_simple(binary)

    # Step 3: Second K12 hash
    if has_k12:
        k12_2 = KangarooTwelve.new()
        k12_2.update(hash1)
        hash2 = k12_2.read(32)  # 256 bits (32 bytes)
    else:
        hash2 = k12_hash_simple(hash1)

    return hash2.hex()

def private_key_to_public_key(private_key_hex):
    """Convert private key to public key using secp256k1"""
    try:
        private_key_bytes = bytes.fromhex(private_key_hex)
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Uncompressed public key (04 + x + y)
        uncompressed = '04' + vk.to_string().hex()

        # Compressed public key
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        if y % 2 == 0:
            compressed = '02' + format(x, '064x')
        else:
            compressed = '03' + format(x, '064x')

        return uncompressed, compressed
    except Exception as e:
        return None, None

def load_data():
    """Load Patoshi addresses and Qubic seeds"""
    with open('public/data/patoshi-addresses.json', 'r') as f:
        patoshi = json.load(f).get('records', [])

    with open('public/data/qubic-seeds.json', 'r') as f:
        seeds = json.load(f).get('records', [])

    return patoshi, seeds

def main():
    print("\n" + "="*80)
    print("🔥 K12 PRIVATE KEY DERIVATION - QUBIC OFFICIAL METHOD! 🔥")
    print("="*80)
    print()

    if not has_k12:
        print("⚠️  Using SHA3-256 fallback (K12 not installed)")
        print("   Install with: pip install pycryptodomex")
        print()

    # Load data
    print("📂 Loading data...")
    patoshi, seeds = load_data()
    print(f"✓ Loaded {len(patoshi):,} Patoshi addresses")
    print(f"✓ Loaded {len(seeds):,} Qubic seeds")
    print()

    # Test K12 derivation method
    print("="*80)
    print("🔍 TESTING K12 DOUBLE-HASH METHOD ON 10 ADDRESSES")
    print("="*80)
    print()

    matches = []

    for i, record in enumerate(patoshi[:10], 1):
        block = record.get('blockHeight', 0)
        known_pubkey = record.get('pubkey', '')
        amount = record.get('amount', 0)

        if not known_pubkey:
            continue

        print(f"\n{'─'*80}")
        print(f"ADDRESS #{i} - BLOCK {block} ({amount} BTC)")
        print(f"{'─'*80}")
        print(f"Known Public Key: {known_pubkey[:40]}...")

        # Get seed for this block
        seed_data = seeds[block-1] if block <= len(seeds) else {}
        seed = seed_data.get('seed', '')

        if not seed:
            print("  ❌ No seed available for this block")
            continue

        print(f"Seed: {seed[:30]}...")

        # Derive private key using K12 method
        private_key_hex = derive_private_key_k12(seed)
        print(f"Private Key: {private_key_hex[:32]}...")

        # Derive public key
        uncompressed_pub, compressed_pub = private_key_to_public_key(private_key_hex)

        if not uncompressed_pub:
            print("  ❌ Failed to derive public key")
            continue

        # Compare with known public key
        match = False
        match_type = None

        if uncompressed_pub.lower() == known_pubkey.lower():
            match = True
            match_type = 'UNCOMPRESSED'
        elif compressed_pub.lower() == known_pubkey.lower():
            match = True
            match_type = 'COMPRESSED'

        if match:
            print(f"\n  🔥🔥🔥 MATCH FOUND! 🔥🔥🔥")
            print(f"  Method: K12 Double Hash (Official Qubic)")
            print(f"  Match Type: {match_type}")
            print(f"  Private Key: {private_key_hex}")
            print(f"  Public Key: {uncompressed_pub}")
            print(f"  🚀 WE HAVE ACCESS TO {amount} BTC! 🚀")

            matches.append({
                'block': block,
                'method': 'K12 Double Hash',
                'private_key': private_key_hex,
                'public_key': uncompressed_pub,
                'amount': amount
            })
        else:
            print(f"  ⚪ No match")
            print(f"     Derived: {uncompressed_pub[:40]}...")
            print(f"     Expected: {known_pubkey[:40]}...")

    # Summary
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print()
    print(f"Addresses tested: 10")
    print(f"Matches found: {len(matches)}")
    print()

    if matches:
        print("🔥🔥🔥 SUCCESS! WE FOUND THE KEYS! 🔥🔥🔥")
        print()
        for match in matches:
            print(f"Block {match['block']}:")
            print(f"  Private Key: {match['private_key']}")
            print(f"  Amount: {match['amount']} BTC")
            print()

        # Save matches
        with open('K12_PRIVATE_KEY_MATCHES.json', 'w') as f:
            json.dump({
                'method': 'K12 Double Hash (Official Qubic)',
                'total_matches': len(matches),
                'total_btc': sum(m['amount'] for m in matches),
                'matches': matches
            }, f, indent=2)

        print("✓ Saved to: K12_PRIVATE_KEY_MATCHES.json")
        print()
        print("🎯 NEXT STEPS:")
        print("1. SECURE THESE PRIVATE KEYS IMMEDIATELY!")
        print("2. Test with Bitcoin wallet (testnet first!)")
        print("3. Verify by signing a message")
        print("4. MOON! 🚀💰")
    else:
        print("⚠️  No matches with K12 method")
        print()
        print("POSSIBLE REASONS:")
        print("1. K12 library not installed (using SHA3 fallback)")
        print("   → Install: pip install pycryptodomex")
        print("2. Additional transformation needed")
        print("3. Different seed set required (Computor seeds vs Qubic seeds)")
        print("4. Seeds not directly mapped to these specific addresses")
        print()
        print("NEXT STEPS:")
        print("1. Install proper K12 library")
        print("2. Search for actual Computor operator seeds (676 of them)")
        print("3. Check Genesis token distribution mechanism")
        print("4. Look for CFB's hints about claim process")

    print("="*80)
    print()

if __name__ == "__main__":
    main()
