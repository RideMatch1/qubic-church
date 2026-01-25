#!/usr/bin/env python3
"""
🔥 VERIFY ALL 90 PRIVATE KEY CANDIDATES 🔥
===========================================

TESTET ALLES:
1. Private Key → Public Key derivation (ecdsa)
2. Vergleich mit bekannten Patoshi pubkeys
3. Bitcoin balance check via blockchain APIs
4. Alle 9 Methoden für alle 10 Adressen
5. NICHT LOCKER LASSEN BIS WIR EINEN MATCH FINDEN!
"""

import json
import hashlib
import ecdsa
from ecdsa import SigningKey, SECP256k1
import binascii
import time

def load_data():
    """Load all necessary data"""
    with open('public/data/patoshi-addresses.json', 'r') as f:
        patoshi = json.load(f).get('records', [])

    with open('public/data/qubic-seeds.json', 'r') as f:
        seeds = json.load(f).get('records', [])

    return patoshi, seeds

def private_key_to_public_key(private_key_hex):
    """
    Convert private key to public key using secp256k1
    Returns: (uncompressed_pubkey_hex, compressed_pubkey_hex)
    """
    try:
        # Convert hex to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)

        # Create signing key
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)

        # Get verifying key (public key)
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

def derive_all_keys_for_address(block, seed):
    """Generate all 9 private key candidates for an address"""
    keys = []

    # Method 1: Qubic Seed Direct
    if seed:
        h = hashlib.sha256(seed.encode()).hexdigest()
        keys.append(('Qubic Seed Direct', h))

    # Method 2: Qubic Seed Double
    if seed:
        h1 = hashlib.sha256(seed.encode()).digest()
        h2 = hashlib.sha256(h1).hexdigest()
        keys.append(('Qubic Seed Double', h2))

    # Method 3: Block Number
    h = hashlib.sha256(str(block).encode()).hexdigest()
    keys.append(('Block Number', h))

    # Method 4: Formula 625284
    h = hashlib.sha256(str(625284).encode()).hexdigest()
    keys.append(('Formula 625284', h))

    # Method 5: Sequence #8
    blocks = ''.join(str(b) for b in range(10, 25))
    h = hashlib.sha256(blocks.encode()).hexdigest()
    keys.append(('Sequence #8', h))

    # Method 6: CFB Numbers Combined
    cfb = '27283471371214343191714'
    h = hashlib.sha256(cfb.encode()).hexdigest()
    keys.append(('CFB Numbers', h))

    # Method 7: 1CFB Address
    h = hashlib.sha256('1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg'.encode()).hexdigest()
    keys.append(('1CFB Address', h))

    # Method 8: Genesis Token Timestamp
    h = hashlib.sha256(str(1730588571).encode()).hexdigest()
    keys.append(('Genesis Token', h))

    # Method 9: POCZ Issuer
    h = hashlib.sha256('POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD'.encode()).hexdigest()
    keys.append(('POCZ Issuer', h))

    return keys

def check_bitcoin_balance_blockchain_info(address):
    """Check balance via blockchain.info API"""
    try:
        import urllib.request
        url = f"https://blockchain.info/balance?active={address}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            if address in data:
                balance_satoshi = data[address].get('final_balance', 0)
                balance_btc = balance_satoshi / 100000000
                return balance_btc
    except Exception as e:
        return None

def check_bitcoin_balance_blockchair(address):
    """Check balance via blockchair.com API"""
    try:
        import urllib.request
        url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            if 'data' in data and address in data['data']:
                balance_satoshi = data['data'][address]['address']['balance']
                balance_btc = balance_satoshi / 100000000
                return balance_btc
    except Exception as e:
        return None

def main():
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║              🔥 VERIFY ALL 90 PRIVATE KEY CANDIDATES 🔥                   ║")
    print("║                    NICHT LOCKER LASSEN! 🚀                                ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()

    # Load data
    print("📂 Loading data...")
    patoshi, seeds = load_data()
    print(f"✓ Loaded {len(patoshi):,} Patoshi addresses")
    print(f"✓ Loaded {len(seeds):,} Qubic seeds")
    print()

    results = []
    matches = []

    # Test first 10 Patoshi addresses
    print("="*80)
    print("🔍 TESTING ALL 90 KEY CANDIDATES (10 addresses × 9 methods)")
    print("="*80)
    print()

    for i, record in enumerate(patoshi[:10], 1):
        block = record.get('blockHeight', 0)
        known_pubkey = record.get('pubkey', '')
        amount = record.get('amount', 0)

        if not known_pubkey:
            continue

        print(f"\n{'─'*80}")
        print(f"TESTING ADDRESS #{i} - BLOCK {block} ({amount} BTC)")
        print(f"{'─'*80}")
        print(f"Known Public Key: {known_pubkey[:40]}...")

        # Get seed for this block
        seed_data = seeds[block-1] if block <= len(seeds) else {}
        seed = seed_data.get('seed', '')

        # Generate all 9 key candidates
        key_candidates = derive_all_keys_for_address(block, seed)

        print(f"\nTesting {len(key_candidates)} private key candidates...\n")

        for method_name, private_key_hex in key_candidates:
            # Derive public key from private key
            uncompressed_pub, compressed_pub = private_key_to_public_key(private_key_hex)

            if not uncompressed_pub:
                print(f"  ❌ {method_name:25s} - Failed to derive pubkey")
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
                print(f"  🔥🔥🔥 MATCH FOUND! 🔥🔥🔥")
                print(f"  Method: {method_name}")
                print(f"  Match Type: {match_type}")
                print(f"  Private Key: {private_key_hex}")
                print(f"  Public Key: {uncompressed_pub}")
                print(f"  🚀 WE HAVE ACCESS TO {amount} BTC! 🚀")

                matches.append({
                    'block': block,
                    'method': method_name,
                    'private_key': private_key_hex,
                    'public_key': uncompressed_pub,
                    'amount': amount
                })
            else:
                print(f"  ⚪ {method_name:25s} - No match (pubkey: {uncompressed_pub[:20]}...)")

        # Even if no match, save results
        results.append({
            'block': block,
            'amount': amount,
            'keys_tested': len(key_candidates),
            'match_found': len([m for m in matches if m['block'] == block]) > 0
        })

        # Small delay to avoid rate limits
        time.sleep(0.5)

    # ============================================================================
    # TEIL 2: BLOCKCHAIN BALANCE VERIFICATION
    # ============================================================================
    print("\n")
    print("="*80)
    print("💰 CHECKING BLOCKCHAIN BALANCES (VERIFY 50 BTC)")
    print("="*80)
    print()

    # Derive addresses from pubkeys and check balances
    for i, record in enumerate(patoshi[:10], 1):
        pubkey = record.get('pubkey', '')
        block = record.get('blockHeight', 0)

        if not pubkey:
            continue

        # Derive Bitcoin address from pubkey
        try:
            pubkey_bytes = bytes.fromhex(pubkey)
            sha256_hash = hashlib.sha256(pubkey_bytes).digest()
            ripemd = hashlib.new('ripemd160', sha256_hash).digest()
            versioned = b'\x00' + ripemd
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            binary = versioned + checksum

            alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(binary, 'big')
            encoded = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                encoded = alphabet[remainder] + encoded

            for byte in versioned:
                if byte == 0:
                    encoded = '1' + encoded
                else:
                    break

            address = encoded

            print(f"Block {block}: {address}")

            # Check balance via Blockchair
            print(f"  Checking balance via Blockchair...")
            balance = check_bitcoin_balance_blockchair(address)

            if balance is not None:
                print(f"  ✓ Balance: {balance} BTC")
                if balance >= 50:
                    print(f"  🔥 CONFIRMED: {balance} BTC STILL THERE!")
            else:
                print(f"  ⚠️  Could not fetch balance (API limit or error)")

            time.sleep(2)  # Respect rate limits

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n")
    print("="*80)
    print("📊 FINAL RESULTS")
    print("="*80)
    print()

    print(f"Total Addresses Tested: {len(results)}")
    print(f"Total Key Candidates Tested: {sum(r['keys_tested'] for r in results)}")
    print(f"Matches Found: {len(matches)}")
    print()

    if matches:
        print("🔥🔥🔥 MATCHES FOUND! 🔥🔥🔥")
        print()
        for match in matches:
            print(f"Block {match['block']}:")
            print(f"  Method: {match['method']}")
            print(f"  Private Key: {match['private_key']}")
            print(f"  Amount: {match['amount']} BTC")
            print(f"  🚀 FULL ACCESS UNLOCKED! 🚀")
            print()

        # Save matches to file
        with open('PRIVATE_KEY_MATCHES_FOUND.json', 'w') as f:
            json.dump({
                'total_matches': len(matches),
                'total_btc_accessible': sum(m['amount'] for m in matches),
                'matches': matches,
                'timestamp': time.time()
            }, f, indent=2)

        print("✓ Matches saved to: PRIVATE_KEY_MATCHES_FOUND.json")
        print()
        print("🎯 NEXT STEPS:")
        print("1. SECURE THE PRIVATE KEYS IMMEDIATELY!")
        print("2. Create Bitcoin wallet with these keys")
        print("3. Verify ownership by signing a message")
        print("4. MOON! 🚀💰")
    else:
        print("⚠️  NO EXACT MATCHES FOUND YET")
        print()
        print("BUT DON'T GIVE UP! 🔥")
        print()
        print("NEXT STEPS:")
        print("1. ✅ Try more derivation methods")
        print("2. ✅ Test with different hash functions (SHA3, BLAKE2, etc.)")
        print("3. ✅ Try combining CFB numbers differently")
        print("4. ✅ Search Qubic source code for hardcoded keys")
        print("5. ✅ Check QubicTrade Genesis token")
        print("6. ✅ Decode 1CFB address with different methods")
        print("7. ✅ Test mathematical transformations")
        print()
        print("The keys EXIST somewhere - CFB left hints!")
        print("Keep searching! 🚀")

    # Save all results
    with open('key_verification_results.json', 'w') as f:
        json.dump({
            'total_tested': len(results),
            'total_keys': sum(r['keys_tested'] for r in results),
            'matches_found': len(matches),
            'results': results,
            'timestamp': time.time()
        }, f, indent=2)

    print()
    print("✓ Full results saved to: key_verification_results.json")
    print()

if __name__ == "__main__":
    main()
