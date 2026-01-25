#!/usr/bin/env python3
"""
TEST SEED XOR COMBINATIONS

From God's Eye View:
"Was wir NICHT testeten: Seed combinations (seed1 + seed2)"

Hypothesis: 1CFB might be generated from XOR of two seeds:
- Reverse alphabet seed XOR 1CFi seed?
- Special pattern combinations?

Example:
Seed1 = 1CFi seed
Seed2 = Reverse alphabet
Seed3 = Seed1 XOR Seed2
→ Could that be 1CFB?
"""

import hashlib
import json
from typing import Dict, List, Optional
import ecdsa

# Target
TARGET = '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg'
TARGET_HASH160 = '7b581609d8f9b74c34f7648c3b79fd8a6848022d'

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

def private_key_to_address(private_key_bytes: bytes, compressed: bool = True) -> Dict:
    try:
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()

        if compressed:
            if vk.pubkey.point.y() & 1:
                public_key = b'\x03' + vk.to_string()[:32]
            else:
                public_key = b'\x02' + vk.to_string()[:32]
        else:
            public_key = b'\x04' + vk.to_string()

        h160 = hash160(public_key)
        address = base58_encode_check(b'\x00', h160)

        return {
            'address': address,
            'hash160': h160.hex(),
            'compressed': compressed,
            'valid': True
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    """XOR two byte strings"""
    # Make them same length
    max_len = max(len(b1), len(b2))
    b1_padded = b1 + b'\x00' * (max_len - len(b1))
    b2_padded = b2 + b'\x00' * (max_len - len(b2))

    return bytes(a ^ b for a, b in zip(b1_padded, b2_padded))

def step_transform(data: bytes, steps: int, xor_value: int = 0) -> bytes:
    result = bytearray(data)
    for i in range(len(result)):
        result[i] = (result[i] + steps * (i + 1) + xor_value) % 256
    return bytes(result)

class SeedXORTester:
    def __init__(self):
        self.methods = {
            'direct': lambda d: d,
            'step7': lambda d: step_transform(d, 7, 0),
            'step13': lambda d: step_transform(d, 13, 0),
            'step27': lambda d: step_transform(d, 27, 0),
            'step27_xor13': lambda d: step_transform(d, 27, 13),
        }

        self.results = {
            'hypothesis': 'XOR combination of two seeds generates 1CFB',
            'combinations_tested': 0,
            'matches_found': []
        }

    def test_xor_combination(self, seed1: str, seed2: str, label: str) -> Optional[Dict]:
        """Test XOR combination of two seeds"""

        # Approach 1: XOR the seeds directly, then hash
        seed1_bytes = seed1.encode('utf-8')
        seed2_bytes = seed2.encode('utf-8')

        xor_seed = xor_bytes(seed1_bytes, seed2_bytes)
        xor_hash = sha256(xor_seed)

        for method_name, method_func in self.methods.items():
            self.results['combinations_tested'] += 1

            transformed = method_func(xor_hash)

            addr_data = private_key_to_address(transformed, compressed=True)

            if addr_data.get('valid') and addr_data['address'] == TARGET:
                return {
                    'seed1': seed1,
                    'seed2': seed2,
                    'combination': label,
                    'method': method_name,
                    'address': addr_data['address'],
                    'BREAKTHROUGH': True
                }

        # Approach 2: Hash both seeds, then XOR
        hash1 = sha256(seed1_bytes)
        hash2 = sha256(seed2_bytes)
        xor_hashes = xor_bytes(hash1, hash2)

        for method_name, method_func in self.methods.items():
            self.results['combinations_tested'] += 1

            transformed = method_func(xor_hashes)

            addr_data = private_key_to_address(transformed, compressed=True)

            if addr_data.get('valid') and addr_data['address'] == TARGET:
                return {
                    'seed1': seed1,
                    'seed2': seed2,
                    'combination': label,
                    'method': f'{method_name}_hash_xor',
                    'address': addr_data['address'],
                    'BREAKTHROUGH': True
                }

        return None

    def run_test(self):
        """Run XOR combination tests"""
        print("=" * 80)
        print("TESTING SEED XOR COMBINATIONS")
        print("=" * 80)
        print()
        print("Hypothesis: 1CFB = Transform(Seed1 XOR Seed2)")
        print("Target: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
        print()

        # Load seeds
        with open('../public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)

        all_seeds = data['records']

        # Find special seeds
        cfi_seed = None
        reverse_alphabet_seed = None

        for seed_data in all_seeds:
            if 'mmmacecvbddmny' in seed_data['seed']:
                cfi_seed = seed_data['seed']
            if seed_data['seed'].startswith('nmlkjihgfedcba'):
                reverse_alphabet_seed = seed_data['seed']

        print(f"1CFi seed: {cfi_seed[:40]}...")
        print(f"Reverse alphabet: {reverse_alphabet_seed[:40]}...")
        print()

        # Test high-priority combinations
        priority_tests = [
            (cfi_seed, reverse_alphabet_seed, "1CFi XOR Reverse Alphabet"),
        ]

        print("Testing priority combinations...")
        print()

        for seed1, seed2, label in priority_tests:
            print(f"Testing: {label}")
            result = self.test_xor_combination(seed1, seed2, label)

            if result:
                print("\n" + "=" * 80)
                print("🎯 XOR COMBINATION BREAKTHROUGH!!!")
                print("=" * 80)
                print(json.dumps(result, indent=2))
                self.results['matches_found'].append(result)

                with open('XOR_COMBINATION_BREAKTHROUGH.json', 'w') as f:
                    json.dump(self.results, f, indent=2)

                return

        # Find all seeds with special properties
        print("\nFinding all seeds with mod 121=0 AND mod 19=0...")

        with open('SIMILAR_ADDRESSES_ANALYSIS.json', 'r') as f:
            similar = json.load(f)

        special_seeds = [
            s['seed'] for s in similar['addresses_both_zero']
            if 'seed' in s and s['seed'] is not None
        ]

        print(f"Found {len(special_seeds)} special seeds")
        print()

        # Test all pairwise combinations of special seeds
        print("Testing pairwise XOR of all special seeds...")
        print(f"Combinations: {len(special_seeds) * (len(special_seeds) - 1) // 2}")
        print()

        tested = 0
        for i in range(len(special_seeds)):
            for j in range(i + 1, len(special_seeds)):
                tested += 1

                if tested % 10 == 0:
                    print(f"Progress: {tested}/{len(special_seeds) * (len(special_seeds) - 1) // 2}")

                result = self.test_xor_combination(
                    special_seeds[i],
                    special_seeds[j],
                    f"Special seed {i} XOR {j}"
                )

                if result:
                    print("\n" + "=" * 80)
                    print("🎯 XOR BREAKTHROUGH!!!")
                    print("=" * 80)
                    print(json.dumps(result, indent=2))
                    self.results['matches_found'].append(result)

                    with open('XOR_COMBINATION_BREAKTHROUGH.json', 'w') as f:
                        json.dump(self.results, f, indent=2)

                    return

        print("\n" + "=" * 80)
        print("XOR COMBINATION TEST COMPLETE")
        print("=" * 80)
        print(f"Combinations tested: {self.results['combinations_tested']}")
        print(f"Matches found: {len(self.results['matches_found'])}")

        with open('XOR_COMBINATION_RESULTS.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print("\nResults saved to: XOR_COMBINATION_RESULTS.json")

if __name__ == '__main__':
    tester = SeedXORTester()
    tester.run_test()
