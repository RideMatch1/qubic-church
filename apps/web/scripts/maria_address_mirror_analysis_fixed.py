#!/usr/bin/env python3
"""
MARIA & CFB ADDRESS MIRROR ANALYSIS - FIXED VERSION

Research all Bitcoin addresses associated with:
- CFB (Come-from-Beyond)
- Maria (CFB's sockpuppet/wife)
- NXT project
- IOTA project

Then test MIRROR operations on them:
- Hash160 reversal
- Address mirroring
- XOR operations
- Cross-validation with known addresses
"""

import hashlib
import json
from typing import Dict, List, Optional

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data: bytes) -> bytes:
    return ripemd160(sha256(data))

def base58_encode_check(prefix: bytes, data: bytes) -> str:
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    payload = prefix + data
    checksum = sha256(sha256(payload))[:4]
    num = int.from_bytes(payload + checksum, 'big')

    if num == 0:
        return alphabet[0]

    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result

    for byte in (payload + checksum):
        if byte == 0:
            result = alphabet[0] + result
        else:
            break

    return result

def base58_decode(address: str) -> Optional[bytes]:
    """Decode a Base58Check address to hash160"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    try:
        num = 0
        for char in address:
            num = num * 58 + alphabet.index(char)

        combined = num.to_bytes(25, byteorder='big')
        checksum = combined[-4:]
        payload = combined[:-4]

        if sha256(sha256(payload))[:4] != checksum:
            return None

        return payload[1:]  # Remove version byte
    except Exception:
        return None

class MariaAddressAnalyzer:
    def __init__(self):
        self.known_addresses = {
            '1CFB_main': {
                'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
                'owner': 'CFB',
                'context': 'Main CFB address'
            },
            '1CFi_special': {
                'address': '1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi',
                'owner': 'CFB',
                'context': 'Special pattern address (SOLVED)',
                'seed': 'mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn',
                'method': 'step27 + XOR13'
            },
            '15ubic_donation': {
                'address': '15ubicKDqW9q3Y4K2Uaq59jtNNYLy8JWkz',
                'owner': 'CFB/Qubic',
                'context': 'Qubic donation address'
            },
            'genesis_satoshi': {
                'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'owner': 'Satoshi/CFB?',
                'context': 'Bitcoin Genesis Block'
            }
        }

        self.mirror_results = {
            'hash160_mirrors': [],
            'xor_variants': [],
            'cross_references': []
        }

    def analyze_address(self, address: str) -> Optional[Dict]:
        """Analyze mathematical properties of an address"""
        hash160_bytes = base58_decode(address)

        if not hash160_bytes:
            print(f"    ⚠️  Failed to decode address: {address}")
            return None

        byte_sum = sum(hash160_bytes)

        return {
            'address': address,
            'hash160': hash160_bytes.hex(),
            'byte_sum': byte_sum,
            'mod_121': byte_sum % 121,
            'mod_19': byte_sum % 19,
            'mod_27': byte_sum % 27,
            'mod_11': byte_sum % 11,
            'mod_13': byte_sum % 13,
            'special_properties': byte_sum % 121 == 0 and byte_sum % 19 == 0,
            'hash160_reversed': hash160_bytes[::-1].hex()
        }

    def test_hash160_mirror(self, hash160_hex: str) -> str:
        """Test if reversing hash160 creates a valid address"""
        hash160_bytes = bytes.fromhex(hash160_hex)
        reversed_hash160 = hash160_bytes[::-1]

        # Create address from reversed hash160
        mirrored_address = base58_encode_check(b'\x00', reversed_hash160)

        return mirrored_address

    def test_xor_with_constant(self, hash160_hex: str, xor_constant: int) -> str:
        """XOR hash160 with a constant"""
        hash160_bytes = bytes.fromhex(hash160_hex)
        xor_bytes = bytes([b ^ xor_constant for b in hash160_bytes])

        return base58_encode_check(b'\x00', xor_bytes)

    def maria_specific_analysis(self):
        """Analyze Maria-specific patterns"""
        print("\n" + "=" * 80)
        print("MARIA & CFB ADDRESS ANALYSIS")
        print("=" * 80)
        print()
        print("Context: Maria = CFB sockpuppet (2,908 Bitcointalk posts)")
        print("Claim: Maria has 400k BTC + CFB has 700k = 1.1M total")
        print()

        # Analyze all known addresses
        print("Analyzing known addresses...")
        print()

        for name, addr_data in self.known_addresses.items():
            address = addr_data['address']
            print(f"{name}:")
            print(f"  Address: {address}")
            print(f"  Owner: {addr_data['owner']}")
            print(f"  Context: {addr_data['context']}")

            analysis = self.analyze_address(address)

            if analysis:
                print(f"  Hash160: {analysis['hash160']}")
                print(f"  Byte sum: {analysis['byte_sum']}")
                print(f"  mod 121: {analysis['mod_121']}, mod 19: {analysis['mod_19']}, mod 27: {analysis['mod_27']}")
                print(f"  Special (121=0 AND 19=0): {analysis['special_properties']}")

                # Store properties
                addr_data['hash160'] = analysis['hash160']
                addr_data['properties'] = analysis

                # Test mirrors
                print(f"  Testing mirrors...")

                # Hash160 reversal
                mirrored = self.test_hash160_mirror(analysis['hash160'])
                print(f"    Hash160 mirror: {mirrored}")

                self.mirror_results['hash160_mirrors'].append({
                    'original': address,
                    'mirrored': mirrored,
                    'owner': addr_data['owner']
                })

                # XOR variants
                for xor_val in [13, 19, 27, 121]:
                    xor_addr = self.test_xor_with_constant(analysis['hash160'], xor_val)
                    print(f"    XOR {xor_val}: {xor_addr}")

                    self.mirror_results['xor_variants'].append({
                        'source': name,
                        'xor_value': xor_val,
                        'result': xor_addr
                    })

                    # Check if this matches any known address
                    for check_name, check_data in self.known_addresses.items():
                        if xor_addr == check_data['address']:
                            print(f"      🎉 MATCH! This XOR creates {check_name}!")
                            self.mirror_results['cross_references'].append({
                                'source': name,
                                'target': check_name,
                                'method': f'XOR {xor_val}'
                            })
            print()

    def find_all_1cf_addresses(self) -> List[Dict]:
        """Find all addresses starting with 1CF from our datasets"""
        print("\n" + "=" * 80)
        print("FINDING ALL 1CF ADDRESSES")
        print("=" * 80)

        cf_addresses = []

        # Load from bitcoin keys
        try:
            with open('../public/data/bitcoin-private-keys.json', 'r') as f:
                keys_data = json.load(f)

            # Handle different JSON structures
            if isinstance(keys_data, list):
                records = keys_data
            elif isinstance(keys_data, dict) and 'records' in keys_data:
                records = keys_data['records']
            else:
                print(f"Unknown JSON structure: {type(keys_data)}")
                return cf_addresses

            for key in records:
                addr = key.get('address', '')
                if addr.startswith('1CF'):
                    cf_addresses.append({
                        'address': addr,
                        'source': 'bitcoin-private-keys.json',
                        'method': key.get('method', 'unknown'),
                        'has_seed': 'seed' in key
                    })
        except Exception as e:
            print(f"Error loading bitcoin keys: {e}")

        print(f"Found {len(cf_addresses)} addresses starting with 1CF")

        if cf_addresses:
            print("\n1CF Addresses found:")
            for addr in cf_addresses[:10]:  # Show first 10
                print(f"  {addr['address']} (method: {addr['method']})")
            if len(cf_addresses) > 10:
                print(f"  ... and {len(cf_addresses) - 10} more")

        return cf_addresses

    def run_analysis(self):
        """Run complete Maria & CFB address analysis"""
        print("\n🔍" * 40)
        print("MARIA & CFB BITCOIN ADDRESS MIRROR ANALYSIS")
        print("🔍" * 40)
        print()

        # Main analysis
        self.maria_specific_analysis()

        # Find all 1CF addresses
        cf_addresses = self.find_all_1cf_addresses()

        # Summary
        print("\n" + "=" * 80)
        print("MIRROR ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Addresses analyzed: {len(self.known_addresses)}")
        print(f"Hash160 mirrors tested: {len(self.mirror_results['hash160_mirrors'])}")
        print(f"XOR variants tested: {len(self.mirror_results['xor_variants'])}")
        print(f"Cross-references found: {len(self.mirror_results['cross_references'])}")
        print(f"1CF addresses found: {len(cf_addresses)}")
        print()

        # Save results
        output = {
            'known_addresses': self.known_addresses,
            'mirror_results': self.mirror_results,
            'cf_addresses': cf_addresses,
            'maria_context': {
                'bitcointalk_posts': 2908,
                'btc_claim': '400,000 BTC',
                'cfb_claim': '700,000 BTC',
                'total': '1,100,000 BTC (≈ Patoshi)',
                'relationship': 'Maria = CFB sockpuppet'
            }
        }

        with open('MARIA_ADDRESS_MIRROR_ANALYSIS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("Results saved to: MARIA_ADDRESS_MIRROR_ANALYSIS.json")
        print()

        # Check for any special findings
        if self.mirror_results['cross_references']:
            print("🎉 SPECIAL FINDINGS:")
            for ref in self.mirror_results['cross_references']:
                print(f"  {ref['source']} --[{ref['method']}]--> {ref['target']}")
            print()

if __name__ == '__main__':
    analyzer = MariaAddressAnalyzer()
    analyzer.run_analysis()
