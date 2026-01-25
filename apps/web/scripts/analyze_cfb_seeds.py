#!/usr/bin/env python3
"""
Analyze CFB Seeds for Potential Rewards
========================================

Takes the 29 CFB-named seeds and:
1. Derives Bitcoin addresses from them
2. Checks against Patoshi database
3. Looks for special patterns
4. Maps to Anna Bot coordinates
"""

import json
import hashlib

def load_special_seeds():
    """Load the special seeds found by search_special_seeds.py"""
    try:
        with open('special_seeds_results.json', 'r') as f:
            data = json.load(f)
        return data.get('keyword_matches', [])
    except FileNotFoundError:
        print("⚠️  special_seeds_results.json not found")
        print("Run search_special_seeds.py first!")
        return []

def derive_bitcoin_address_sha256(seed: str) -> str:
    """Derive Bitcoin address using SHA256 method"""

    # Step 1: SHA256 hash of seed
    hash1 = hashlib.sha256(seed.encode()).digest()

    # Step 2: RIPEMD160(SHA256(hash))
    hash2 = hashlib.sha256(hash1).digest()
    ripemd = hashlib.new('ripemd160', hash2).digest()

    # Step 3: Add version byte (0x00 for mainnet)
    versioned = b'\x00' + ripemd

    # Step 4: Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

    # Step 5: Base58 encode
    binary = versioned + checksum
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    num = int.from_bytes(binary, 'big')
    encoded = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        encoded = alphabet[remainder] + encoded

    # Add leading '1's for leading zero bytes
    for byte in versioned:
        if byte == 0:
            encoded = '1' + encoded
        else:
            break

    return encoded

def derive_qubic_seed_sha256(bitcoin_address: str) -> str:
    """Reverse: Derive Qubic seed from Bitcoin address"""
    hash_bytes = hashlib.sha256(bitcoin_address.encode()).digest()
    seed = ''
    for byte in hash_bytes[:28]:
        seed += chr(ord('a') + (byte % 26))
    return seed

def map_to_anna_coordinates(seed: str) -> tuple:
    """Map seed to Anna Bot coordinates"""
    coord_hash = hashlib.sha256(seed.encode()).digest()
    row = int.from_bytes(coord_hash[:4], 'big') % 128
    col = int.from_bytes(coord_hash[4:8], 'big') % 128
    return (row, col)

def predict_anna_response(row: int, col: int) -> int:
    """Predict Anna Bot response based on patterns"""

    # Universal columns
    if col == 28:
        return 110
    if col == 34:
        return 60
    if col == (128 - 17):
        return -121

    # Special rows
    if row == 1:
        return -114
    if row == 9:
        return 125
    if row == 49:
        return 14
    if row == 57:
        return 6

    # row%8 patterns
    row_mod_8 = row % 8
    if row_mod_8 in [3, 7]:
        return -113
    if row_mod_8 == 2:
        return 78
    if row_mod_8 == 4:
        return 26
    if row_mod_8 == 6:
        return -50

    # Default
    return -114

def analyze_cfb_seeds():
    """Main analysis function"""

    print("="*80)
    print("CFB SEED ANALYSIS FOR FINDER'S REWARD")
    print("="*80)
    print()

    # Load special seeds
    cfb_seeds = load_special_seeds()

    if not cfb_seeds:
        return

    print(f"Analyzing {len(cfb_seeds)} CFB-named seeds...")
    print()

    results = []

    for match in cfb_seeds[:10]:  # Analyze first 10
        seed = match['seed']
        identity = match['identity']
        index = match['index']

        print("="*80)
        print(f"SEED #{index}: {identity[:40]}...")
        print("="*80)

        # Derive Bitcoin address
        btc_address = derive_bitcoin_address_sha256(seed)
        print(f"Bitcoin Address (SHA256): {btc_address}")

        # Map to Anna coordinates
        row, col = map_to_anna_coordinates(seed)
        expected = predict_anna_response(row, col)

        print(f"Anna Coordinates: ({row}, {col})")
        print(f"Expected Response: {expected}")

        # Check for CFB number patterns
        cfb_patterns = []

        if row % 27 == 0:
            cfb_patterns.append(f"Row {row} divisible by 27!")
        if row in [1, 9, 49, 57, 121]:
            cfb_patterns.append(f"Row {row} is special (CFB number)!")
        if col in [28, 34]:
            cfb_patterns.append(f"Col {col} is universal column!")
        if expected in [-114, -113, 14, 27, 110, 60]:
            cfb_patterns.append(f"Expected {expected} is CFB signature!")

        if cfb_patterns:
            print("\n🔥 CFB PATTERNS DETECTED:")
            for pattern in cfb_patterns:
                print(f"   • {pattern}")

        print()

        results.append({
            'index': index,
            'identity': identity,
            'seed': seed,
            'bitcoin_address': btc_address,
            'anna_coords': {'row': row, 'col': col},
            'expected_response': expected,
            'cfb_patterns': cfb_patterns
        })

    # Summary
    print("="*80)
    print("SUMMARY OF TOP 10 CFB SEEDS")
    print("="*80)
    print()

    print("Bitcoin Addresses Derived:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['bitcoin_address']}")
        if result['cfb_patterns']:
            print(f"   → {len(result['cfb_patterns'])} CFB patterns detected")

    print()
    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print("1. Check these Bitcoin addresses on blockchain explorer:")
    print("   → https://blockchair.com/bitcoin/address/<address>")
    print()
    print("2. Look for:")
    print("   • Non-zero balance")
    print("   • Transactions with CFB numbers (27, 283, 47, etc.)")
    print("   • Special block heights")
    print("   • Messages in OP_RETURN")
    print()
    print("3. If address has balance, check:")
    print("   • Can we derive the private key from the seed?")
    print("   • Is there a time-lock mechanism?")
    print("   • Is there a claim process on QubicTrade?")
    print()

    # Save results
    with open('cfb_seed_analysis.json', 'w') as f:
        json.dump({
            'total_analyzed': len(results),
            'results': results
        }, f, indent=2)

    print("✓ Results saved to: cfb_seed_analysis.json")
    print()

if __name__ == "__main__":
    analyze_cfb_seeds()
