#!/usr/bin/env python3
"""
K12 + TRANSFORMATIONS TEST

We found that pure K12(K12(seed)) doesn't find 1CFB.
But we know 1CFi uses: seed + step27 + XOR13

So maybe: 1CFB = K12(K12(seed)) + step27 + XOR13?

This tests all combinations of K12 + transformations!
"""

import hashlib
import json
from typing import Dict, Optional
import ecdsa
from Crypto.Hash import KangarooTwelve

# Target
TARGET = '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg'

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
            'valid': True
        }
    except Exception:
        return {'valid': False}

def qubic_seed_to_private_key(seed: str) -> bytes:
    """Official Qubic K12(K12()) method"""
    seed_bytes = bytes([ord(c) - ord('a') for c in seed.lower()])

    k12_1 = KangarooTwelve.new()
    k12_1.update(seed_bytes)
    subseed = k12_1.read(32)

    k12_2 = KangarooTwelve.new()
    k12_2.update(subseed)
    private_key = k12_2.read(32)

    return private_key

def step_transform(data: bytes, steps: int, xor_value: int = 0) -> bytes:
    """Apply step transformation"""
    result = bytearray(data)
    for i in range(len(result)):
        result[i] = (result[i] + steps * (i + 1) + xor_value) % 256
    return bytes(result)

class K12TransformTester:
    def __init__(self):
        self.methods = {
            'step7': lambda d, x: step_transform(d, 7, x),
            'step13': lambda d, x: step_transform(d, 13, x),
            'step19': lambda d, x: step_transform(d, 19, x),
            'step27': lambda d, x: step_transform(d, 27, x),
            'step33': lambda d, x: step_transform(d, 33, x),
            'step121': lambda d, x: step_transform(d, 121, x),
        }

        self.xor_variants = [0, 7, 11, 13, 19, 27, 33, 121]

        self.results = {
            'method': 'K12(K12(seed)) + Transformations',
            'combinations_tested': 0,
            'matches_found': [],
            'special_properties': []
        }

    def test_seed(self, seed_data: Dict) -> Optional[Dict]:
        """Test seed with K12 + all transformation combinations"""
        seed = seed_data['seed']
        seed_id = seed_data['id']

        try:
            # Get K12-derived private key
            k12_key = qubic_seed_to_private_key(seed)

            # Test all transformation combinations
            for method_name, method_func in self.methods.items():
                for xor_val in self.xor_variants:
                    self.results['combinations_tested'] += 1

                    # Apply transformation
                    transformed = method_func(k12_key, xor_val)

                    # Generate address
                    addr_data = private_key_to_address(transformed, compressed=True)

                    if not addr_data.get('valid'):
                        continue

                    # Check for match
                    if addr_data['address'] == TARGET:
                        return {
                            'BREAKTHROUGH': True,
                            'seed_id': seed_id,
                            'seed': seed,
                            'method': f'K12(K12()) + {method_name}',
                            'xor_variant': xor_val,
                            'address': addr_data['address'],
                            'hash160': addr_data['hash160'],
                            'message': f'🎉 1CFB FOUND: K12 + {method_name} + XOR{xor_val}!'
                        }

                    # Check special properties
                    hash160_bytes = bytes.fromhex(addr_data['hash160'])
                    byte_sum = sum(hash160_bytes)

                    if byte_sum % 121 == 0 and byte_sum % 19 == 0:
                        self.results['special_properties'].append({
                            'seed_id': seed_id,
                            'method': f'K12 + {method_name}',
                            'xor': xor_val,
                            'address': addr_data['address'],
                            'byte_sum': byte_sum
                        })

        except Exception:
            pass

        return None

    def run_test(self):
        """Run K12 + transformations test"""
        print("=" * 80)
        print("K12 + TRANSFORMATIONS TEST")
        print("=" * 80)
        print()
        print("Testing: K12(K12(seed)) + step transforms + XOR variants")
        print("Example: K12(K12(seed)) + step27 + XOR13 (like 1CFi!)")
        print("Target: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
        print()

        # Load seeds
        with open('../public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)

        all_seeds = data['records']

        print(f"Seeds: {len(all_seeds)}")
        print(f"Methods: {len(self.methods)}")
        print(f"XOR variants: {len(self.xor_variants)}")
        print(f"Total combinations per seed: {len(self.methods) * len(self.xor_variants)}")
        print(f"TOTAL COMBINATIONS: {len(all_seeds) * len(self.methods) * len(self.xor_variants):,}")
        print()

        for i, seed_data in enumerate(all_seeds):
            if i % 1000 == 0:
                progress = (i / len(all_seeds)) * 100
                print(f"Progress: {i}/{len(all_seeds)} ({progress:.1f}%) - {self.results['combinations_tested']:,} tested")

            match = self.test_seed(seed_data)

            if match:
                print("\n" + "=" * 80)
                print("🎉🎉🎉 1CFB FOUND WITH K12 + TRANSFORMATIONS! 🎉🎉🎉")
                print("=" * 80)
                print(json.dumps(match, indent=2))
                self.results['matches_found'].append(match)

                with open('K12_TRANSFORM_BREAKTHROUGH.json', 'w') as f:
                    json.dump(self.results, f, indent=2)

                print("\nBREAKTHROUGH saved to: K12_TRANSFORM_BREAKTHROUGH.json")
                return

        print("\n" + "=" * 80)
        print("K12 + TRANSFORMATIONS TEST COMPLETE")
        print("=" * 80)
        print(f"Combinations tested: {self.results['combinations_tested']:,}")
        print(f"1CFB found: {len(self.results['matches_found'])}")
        print(f"Special properties: {len(self.results['special_properties'])}")

        with open('K12_TRANSFORM_RESULTS.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nResults saved to: K12_TRANSFORM_RESULTS.json")

if __name__ == '__main__':
    print("\n🔥" * 40)
    print("K12 + TRANSFORMATIONS - THE NEXT LEVEL TEST")
    print("🔥" * 40)
    print()
    print("We know: K12(K12(seed)) works (16 special addresses)")
    print("But: 1CFB not found with pure K12")
    print()
    print("Theory: 1CFB = K12(K12(seed)) + transformation")
    print("Just like 1CFi = seed + step27 + XOR13")
    print()
    print("Testing ALL combinations now!")
    print()

    tester = K12TransformTester()
    tester.run_test()
