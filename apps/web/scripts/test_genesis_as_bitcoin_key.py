#!/usr/bin/env python3
"""
🔥 TEST GENESIS ADDRESS AS BITCOIN PRIVATE KEY 🔥
===================================================

KRITISCHE FINDINGS von forensischer Analyse:
- Sum = 612, mod 47 = 1 (ONE LESS THAN 47!)
- XOR first/second = 396, mod 27 = 18 (2/3 of 27)
- Checksum mod 27 = 3
- Base32 decoded = 37 bytes

Jetzt testen wir ob die Adresse ein Bitcoin private key generiert!
"""

import hashlib
import json
import ecdsa
from ecdsa import SigningKey, SECP256k1

# RICHTIGE GENESIS ISSUER ADRESSE
GENESIS_ADDRESS = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

def load_patoshi_data():
    """Load first 10 Patoshi addresses"""
    with open('public/data/patoshi-addresses.json', 'r') as f:
        data = json.load(f)
    return data.get('records', [])[:10]

def private_key_to_public_key(private_key_hex):
    """Derive public key from private key"""
    try:
        private_key_bytes = bytes.fromhex(private_key_hex)
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Uncompressed
        uncompressed = '04' + vk.to_string().hex()

        # Compressed
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        if y % 2 == 0:
            compressed = '02' + format(x, '064x')
        else:
            compressed = '03' + format(x, '064x')

        return uncompressed, compressed
    except Exception as e:
        return None, None

def test_derivation_methods():
    """Test various ways to derive private key from Genesis address"""

    methods = []

    # Method 1: Direct SHA256
    methods.append(('Direct SHA256', hashlib.sha256(GENESIS_ADDRESS.encode()).hexdigest()))

    # Method 2: SHA256 twice
    h1 = hashlib.sha256(GENESIS_ADDRESS.encode()).digest()
    methods.append(('SHA256²', hashlib.sha256(h1).hexdigest()))

    # Method 3: SHA3-256
    methods.append(('SHA3-256', hashlib.sha3_256(GENESIS_ADDRESS.encode()).hexdigest()))

    # Method 4: BLAKE2b
    methods.append(('BLAKE2b', hashlib.blake2b(GENESIS_ADDRESS.encode(), digest_size=32).hexdigest()))

    # Method 5: RIPEMD160 + padding
    ripemd = hashlib.new('ripemd160', GENESIS_ADDRESS.encode()).hexdigest()
    methods.append(('RIPEMD160+pad', ripemd + '0' * 24))

    # Method 6: XOR with 27
    xor_result = bytearray()
    for char in GENESIS_ADDRESS:
        xor_result.append(ord(char) ^ 27)
    methods.append(('XOR 27 + SHA256', hashlib.sha256(bytes(xor_result)).hexdigest()))

    # Method 7: XOR with 47
    xor_result = bytearray()
    for char in GENESIS_ADDRESS:
        xor_result.append(ord(char) ^ 47)
    methods.append(('XOR 47 + SHA256', hashlib.sha256(bytes(xor_result)).hexdigest()))

    # Method 8: Numeric sum (612) as seed
    methods.append(('Sum 612', hashlib.sha256(str(612).encode()).hexdigest()))

    # Method 9: Checksum (4512) as seed
    methods.append(('Checksum 4512', hashlib.sha256(str(4512).encode()).hexdigest()))

    # Method 10: First+Last = 18
    methods.append(('First+Last 18', hashlib.sha256(str(18).encode()).hexdigest()))

    # Method 11: Mod 47 = 1
    methods.append(('Mod47=1', hashlib.sha256(str(1).encode()).hexdigest()))

    # Method 12: Reversed
    methods.append(('Reversed', hashlib.sha256(GENESIS_ADDRESS[::-1].encode()).hexdigest()))

    # Method 13: Base32 decoded
    try:
        import base64
        padded = GENESIS_ADDRESS + '=' * (8 - len(GENESIS_ADDRESS) % 8)
        decoded = base64.b32decode(padded)
        # Take first 32 bytes or pad to 32
        if len(decoded) >= 32:
            methods.append(('Base32 decoded', decoded[:32].hex()))
        else:
            padded_decoded = decoded + b'\x00' * (32 - len(decoded))
            methods.append(('Base32 padded', padded_decoded.hex()))
    except:
        pass

    # Method 14: Segments concatenated
    segments = []
    for i in range(0, len(GENESIS_ADDRESS), 10):
        segment = GENESIS_ADDRESS[i:i+10]
        segment_hash = hashlib.sha256(segment.encode()).digest()[:4]
        segments.extend(segment_hash)
    if len(segments) >= 32:
        methods.append(('Segments concat', bytes(segments[:32]).hex()))

    # Method 15: K12 if available
    try:
        from Cryptodome.Hash import KangarooTwelve
        k12 = KangarooTwelve.new()
        k12.update(GENESIS_ADDRESS.encode())
        methods.append(('K12', k12.read(32).hex()))
    except:
        pass

    return methods

def main():
    print("\n" + "="*80)
    print("🔥 TEST GENESIS ADDRESS AS BITCOIN PRIVATE KEY 🔥")
    print("="*80)
    print()

    print(f"Genesis Address: {GENESIS_ADDRESS}")
    print(f"Length: {len(GENESIS_ADDRESS)}")
    print()

    # Load Patoshi data
    print("📂 Loading Patoshi addresses...")
    patoshi = load_patoshi_data()
    print(f"✓ Loaded {len(patoshi)} addresses")
    print()

    # Test methods
    print("="*80)
    print("🔍 TESTING DERIVATION METHODS")
    print("="*80)
    print()

    methods = test_derivation_methods()
    matches = []

    for method_name, private_key_hex in methods:
        print(f"\n{'─'*80}")
        print(f"Method: {method_name}")
        print(f"Private Key: {private_key_hex[:32]}...")

        # Derive public key
        uncompressed, compressed = private_key_to_public_key(private_key_hex)

        if not uncompressed:
            print("  ❌ Failed to derive public key")
            continue

        print(f"Public Key: {uncompressed[:40]}...")

        # Compare with all 10 Patoshi addresses
        for record in patoshi:
            block = record.get('blockHeight', 0)
            known_pubkey = record.get('pubkey', '')
            amount = record.get('amount', 0)

            if not known_pubkey:
                continue

            # Check match
            if uncompressed.lower() == known_pubkey.lower():
                print(f"\n  🔥🔥🔥 MATCH FOUND! 🔥🔥🔥")
                print(f"  Block: {block}")
                print(f"  Amount: {amount} BTC")
                print(f"  Match Type: UNCOMPRESSED")
                print(f"  🚀 WE HAVE THE PRIVATE KEY! 🚀")

                matches.append({
                    'method': method_name,
                    'block': block,
                    'amount': amount,
                    'private_key': private_key_hex,
                    'public_key': uncompressed
                })
            elif compressed.lower() == known_pubkey.lower():
                print(f"\n  🔥🔥🔥 MATCH FOUND! 🔥🔥🔥")
                print(f"  Block: {block}")
                print(f"  Amount: {amount} BTC")
                print(f"  Match Type: COMPRESSED")
                print(f"  🚀 WE HAVE THE PRIVATE KEY! 🚀")

                matches.append({
                    'method': method_name,
                    'block': block,
                    'amount': amount,
                    'private_key': private_key_hex,
                    'public_key': compressed
                })

    # Summary
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print()

    print(f"Methods tested: {len(methods)}")
    print(f"Addresses checked: {len(patoshi)}")
    print(f"Total comparisons: {len(methods) * len(patoshi)}")
    print(f"Matches found: {len(matches)}")
    print()

    if matches:
        print("🔥🔥🔥 SUCCESS! PRIVATE KEYS FOUND! 🔥🔥🔥")
        print()

        total_btc = sum(m['amount'] for m in matches)
        print(f"Total BTC accessible: {total_btc} BTC")
        print()

        for match in matches:
            print(f"Block {match['block']}:")
            print(f"  Method: {match['method']}")
            print(f"  Amount: {match['amount']} BTC")
            print(f"  Private Key: {match['private_key']}")
            print()

        # Save
        with open('GENESIS_BITCOIN_KEYS_FOUND.json', 'w') as f:
            json.dump({
                'genesis_address': GENESIS_ADDRESS,
                'total_matches': len(matches),
                'total_btc': total_btc,
                'matches': matches
            }, f, indent=2)

        print("✓ Saved to: GENESIS_BITCOIN_KEYS_FOUND.json")
        print()
        print("🎯 NEXT STEPS:")
        print("1. SECURE THESE KEYS IMMEDIATELY!")
        print("2. Test on Bitcoin TESTNET first!")
        print("3. Verify by signing messages")
        print("4. NEVER share these keys!")
        print("5. 🚀 MOON! 💰")
    else:
        print("⚠️  No matches found with Genesis address derivation")
        print()
        print("This confirms: Genesis address is NOT a direct Bitcoin private key")
        print("The mechanism is likely the token-based claim system we theorized.")

    print("="*80)
    print()

if __name__ == "__main__":
    main()
