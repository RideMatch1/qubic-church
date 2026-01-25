#!/usr/bin/env python3
"""
TEST UNEXPLORED SEEDS (16384-23764)

Critical Discovery: We assumed 128×128 = 16,384 seeds
But there are actually 23,765 seeds!

The "extra" 7,381 seeds were NEVER tested because we thought
they didn't exist!

This script tests seeds 16384-23764 for 1CFB generation.
"""

import hashlib
import json
from typing import Dict, List, Optional
import ecdsa

# Target addresses
TARGETS = {
    '1CFB': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
    '1CFB_hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
}

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
        'public_key': public_key.hex(),
        'compressed': compressed
    }

def step_transform(data: bytes, steps: int, xor_value: int = 0) -> bytes:
    """Apply step transformation with optional XOR"""
    result = bytearray(data)
    for i in range(len(result)):
        result[i] = (result[i] + steps * (i + 1) + xor_value) % 256
    return bytes(result)

def mult_transform(data: bytes, mult: int, xor_value: int = 0) -> bytes:
    """Apply multiplication transformation"""
    result = bytearray(data)
    for i in range(len(result)):
        result[i] = ((result[i] * mult) + xor_value) % 256
    return bytes(result)

class UnexploredSeedsTester:
    def __init__(self):
        self.methods = {
            'step7': lambda d, x: step_transform(d, 7, x),
            'step13': lambda d, x: step_transform(d, 13, x),
            'step19': lambda d, x: step_transform(d, 19, x),
            'step27': lambda d, x: step_transform(d, 27, x),
            'step33': lambda d, x: step_transform(d, 33, x),
            'step121': lambda d, x: step_transform(d, 121, x),
            'mult7': lambda d, x: mult_transform(d, 7, x),
            'mult13': lambda d, x: mult_transform(d, 13, x),
            'mult19': lambda d, x: mult_transform(d, 19, x),
            'mult27': lambda d, x: mult_transform(d, 27, x),
        }

        self.xor_variants = [0, 7, 11, 13, 19, 27, 33, 121]

        self.results = {
            'search_range': 'Seeds 16384-23764 (the unexplored zone)',
            'total_seeds': 0,
            'combinations_tested': 0,
            'matches_found': [],
            'special_properties': []
        }

    def load_seeds(self) -> List[Dict]:
        """Load seeds from qubic-seeds.json"""
        print("Loading seeds from qubic-seeds.json...")

        with open('../public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)

        all_seeds = data['records']

        # Get ONLY the unexplored seeds (16384-23764)
        unexplored = all_seeds[16384:]

        print(f"Total seeds in file: {len(all_seeds)}")
        print(f"Unexplored seeds (16384+): {len(unexplored)}")
        print(f"These seeds were NEVER tested because we assumed 128×128!")

        return unexplored

    def test_seed(self, seed_data: Dict) -> Optional[Dict]:
        """Test a seed with all transformation combinations"""
        seed = seed_data['seed']
        seed_id = seed_data['id']

        # Hash the seed
        seed_hash = sha256(seed.encode('utf-8'))

        for method_name, method_func in self.methods.items():
            for xor_val in self.xor_variants:
                self.results['combinations_tested'] += 1

                # Apply transformation
                transformed = method_func(seed_hash, xor_val)

                # Generate address (compressed)
                try:
                    addr_data = private_key_to_address(transformed, compressed=True)

                    # Check if match
                    if addr_data['address'] == TARGETS['1CFB']:
                        return {
                            'seed_id': seed_id,
                            'seed': seed,
                            'method': method_name,
                            'xor_variant': xor_val,
                            'address': addr_data['address'],
                            'hash160': addr_data['hash160'],
                            'FOUND': True
                        }

                    # Check for special properties
                    hash160_bytes = bytes.fromhex(addr_data['hash160'])
                    byte_sum = sum(hash160_bytes)

                    if byte_sum % 121 == 0 and byte_sum % 19 == 0:
                        self.results['special_properties'].append({
                            'seed_id': seed_id,
                            'seed': seed,
                            'method': method_name,
                            'xor_variant': xor_val,
                            'address': addr_data['address'],
                            'byte_sum': byte_sum,
                            'from_unexplored_zone': True
                        })

                except Exception:
                    pass

        return None

    def run_search(self):
        """Run the complete search"""
        print("=" * 80)
        print("TESTING UNEXPLORED SEEDS (16384-23764)")
        print("=" * 80)
        print()
        print("Discovery: We assumed 128×128 = 16,384 seeds")
        print("Reality: There are 23,765 seeds total")
        print("Missing: 7,381 seeds were NEVER tested!")
        print()
        print("Target: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
        print()

        seeds = self.load_seeds()
        self.results['total_seeds'] = len(seeds)

        print(f"\nTesting {len(seeds)} unexplored seeds...")
        print(f"Methods: {len(self.methods)}")
        print(f"XOR variants: {len(self.xor_variants)}")
        print(f"Total combinations per seed: {len(self.methods) * len(self.xor_variants)}")
        print(f"TOTAL COMBINATIONS: {len(seeds) * len(self.methods) * len(self.xor_variants):,}")
        print()

        for i, seed_data in enumerate(seeds):
            if i % 500 == 0:
                progress = (i / len(seeds)) * 100
                print(f"Progress: {i}/{len(seeds)} seeds ({progress:.1f}%)")

            match = self.test_seed(seed_data)

            if match:
                print("\n" + "=" * 80)
                print("🎯 MATCH FOUND!!!")
                print("=" * 80)
                print(json.dumps(match, indent=2))
                self.results['matches_found'].append(match)

                # Save immediately
                with open('UNEXPLORED_SEEDS_MATCH_FOUND.json', 'w') as f:
                    json.dump(self.results, f, indent=2)

                return

        print("\n" + "=" * 80)
        print("SEARCH COMPLETE")
        print("=" * 80)
        print(f"Combinations tested: {self.results['combinations_tested']:,}")
        print(f"Matches found: {len(self.results['matches_found'])}")
        print(f"Special properties found: {len(self.results['special_properties'])}")
        print()

        # Save results
        output_file = 'UNEXPLORED_SEEDS_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {output_file}")

        if self.results['special_properties']:
            print(f"\nFound {len(self.results['special_properties'])} addresses with mod 121=0 AND mod 19=0")
            print("in the UNEXPLORED ZONE!")

if __name__ == '__main__':
    tester = UnexploredSeedsTester()
    tester.run_search()
