#!/usr/bin/env python3
"""
SYZYGY KEYS VERIFICATION
========================

Tests all 10 theoretical private key candidates from syzygy_keys.json
to see if any derive to the target 1CFB address.

CRITICAL: This has NEVER been tested before!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58

class SyzygyKeyTester:
    """Test theoretical private keys against target address"""

    def __init__(self):
        self.target_address = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"
        self.results = []

    def private_key_to_address(self, private_key_hex):
        """
        Derive Bitcoin address from private key

        Process:
        1. Private Key (32 bytes hex)
        2. -> ECDSA Public Key (secp256k1)
        3. -> SHA256
        4. -> RIPEMD160 (Hash160)
        5. -> Add version byte (0x00)
        6. -> Double SHA256 checksum
        7. -> Base58 encode
        """
        try:
            # Step 1: Private key to public key
            private_key_bytes = bytes.fromhex(private_key_hex)
            sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()

            # Get uncompressed public key (04 + x + y)
            public_key = b'\x04' + vk.to_string()

            # Step 2: SHA256(public_key)
            sha256_hash = hashlib.sha256(public_key).digest()

            # Step 3: RIPEMD160(SHA256(public_key))
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_hash)
            hash160 = ripemd160.digest()

            # Step 4: Add version byte (0x00 for mainnet)
            versioned = b'\x00' + hash160

            # Step 5: Calculate checksum (first 4 bytes of double SHA256)
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

            # Step 6: Base58 encode
            address = base58.b58encode(versioned + checksum).decode('utf-8')

            return address, hash160.hex()

        except Exception as e:
            return f"Error: {e}", None

    def test_all_keys(self):
        """Test all candidates from syzygy_keys.json"""
        print("="*80)
        print("SYZYGY KEYS VERIFICATION TEST")
        print("="*80)
        print()
        print(f"Target Address: {self.target_address}")
        print()

        # Load candidates
        with open('../syzygy_keys.json', 'r') as f:
            data = json.load(f)

        candidates = data['candidates']
        print(f"Testing {len(candidates)} private key candidates...")
        print()

        matches_found = []

        for i, candidate in enumerate(candidates, 1):
            method = candidate['method']
            private_key_hex = candidate['private_key_hex']
            confidence = candidate['confidence']

            print(f"Test {i}/{len(candidates)}: {method}")
            print(f"  Confidence: {confidence}%")
            print(f"  Private Key: {private_key_hex}")

            # Derive address
            derived_address, hash160 = self.private_key_to_address(private_key_hex)

            print(f"  Derived Address: {derived_address}")

            # Check match
            if derived_address == self.target_address:
                print("  *** MATCH FOUND!!! ***")
                matches_found.append({
                    'method': method,
                    'private_key': private_key_hex,
                    'confidence': confidence,
                    'address': derived_address,
                    'hash160': hash160
                })
            else:
                print("  No match")

            # Store result
            self.results.append({
                'test_number': i,
                'method': method,
                'confidence': confidence,
                'private_key_hex': private_key_hex,
                'derived_address': derived_address,
                'hash160': hash160,
                'match': derived_address == self.target_address
            })

            print()

        # Summary
        print("="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        print()

        if matches_found:
            print(f"SUCCESS! Found {len(matches_found)} matching key(s):")
            print()
            for match in matches_found:
                print(f"Method: {match['method']}")
                print(f"Private Key: {match['private_key']}")
                print(f"Address: {match['address']}")
                print(f"Hash160: {match['hash160']}")
                print()
        else:
            print("No matches found.")
            print()
            print("This means:")
            print("1. None of the theoretical keys derive to 1CFB address")
            print("2. The syzygy mathematics approach needs refinement")
            print("3. We need alternative key derivation methods")
            print()
            print("Negative results are still valuable scientific data!")

        print()
        print(f"Total tests: {len(candidates)}")
        print(f"Matches: {len(matches_found)}")
        print(f"Failures: {len(candidates) - len(matches_found)}")

        # Export results
        output = {
            'test_date': '2026-01-09',
            'target_address': self.target_address,
            'total_tests': len(candidates),
            'matches_found': len(matches_found),
            'matches': matches_found,
            'all_results': self.results
        }

        with open('syzygy_key_test_results.json', 'w') as f:
            json.dump(output, f, indent=2)

        print()
        print("Results exported to: syzygy_key_test_results.json")
        print()

        return matches_found

def main():
    """Main execution"""
    tester = SyzygyKeyTester()
    matches = tester.test_all_keys()

    if matches:
        print("="*80)
        print("CRITICAL DISCOVERY!")
        print("="*80)
        print()
        print("We have found the private key for the 1CFB address!")
        print("This is a major breakthrough in the research.")
        print()
    else:
        print("="*80)
        print("DOCUMENTATION UPDATE NEEDED")
        print("="*80)
        print()
        print("We need to document that:")
        print("1. Syzygy keys were tested (important!)")
        print("2. None matched (negative result)")
        print("3. Alternative approaches needed")
        print()

if __name__ == "__main__":
    main()
