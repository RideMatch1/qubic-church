#!/usr/bin/env python3
"""
TEST IOTA CURL HASH FOR 1CFB GENERATION

Critical hypothesis from God's Eye View:
CFB invented the Curl hash for IOTA.
Could he have used Curl for Bitcoin address generation?

Curl(seed) → private key?

This would be his "signature" - using his own invention.
"""

import hashlib
import json
from typing import Dict, List, Optional
import ecdsa

# Target
TARGET = '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg'
TARGET_HASH160 = '7b581609d8f9b74c34f7648c3b79fd8a6848022d'

# Curl-P-27 constants (simplified implementation)
# Note: This is a simplified version - full Curl is more complex
STATE_LENGTH = 729  # 3^6
HASH_LENGTH = 243   # One third of STATE_LENGTH

def curl_transform(state: List[int]) -> None:
    """
    Simplified Curl transformation
    Note: Real Curl-P is more complex, but this captures the essence
    """
    state_copy = state.copy()

    for i in range(STATE_LENGTH):
        idx1 = i
        idx2 = (i + 364) % STATE_LENGTH

        if state_copy[idx1] == state_copy[idx2]:
            state[i] = 1
        else:
            state[i] = -1

def curl_hash(input_trits: List[int], num_rounds: int = 27) -> List[int]:
    """
    Simplified Curl-P hash
    """
    state = [0] * STATE_LENGTH

    # Absorb
    for i in range(len(input_trits)):
        state[i % STATE_LENGTH] = input_trits[i]

    # Transform
    for _ in range(num_rounds):
        curl_transform(state)

    # Squeeze
    return state[:HASH_LENGTH]

def bytes_to_trits(data: bytes) -> List[int]:
    """Convert bytes to trits (ternary: -1, 0, 1)"""
    trits = []
    for byte in data:
        # Convert each byte to base-3
        value = byte
        for _ in range(6):  # Each byte -> 6 trits (3^6 > 256)
            trits.append((value % 3) - 1)  # Map to -1, 0, 1
            value //= 3
    return trits

def trits_to_bytes(trits: List[int]) -> bytes:
    """Convert trits back to bytes"""
    result = []
    for i in range(0, len(trits), 6):
        chunk = trits[i:i+6]
        value = 0
        for j, trit in enumerate(chunk):
            value += (trit + 1) * (3 ** j)
        result.append(value % 256)
    return bytes(result[:32])  # Take first 32 bytes for private key

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

class CurlHashTester:
    def __init__(self):
        self.results = {
            'hypothesis': 'CFB used his IOTA Curl hash invention for Bitcoin addresses',
            'tested_approaches': [],
            'matches_found': [],
            'special_properties': []
        }

    def test_approach_1_direct_curl(self, seed: str) -> Optional[Dict]:
        """Approach 1: Curl(seed) → private key"""
        # Convert seed to bytes then to trits
        seed_bytes = seed.encode('utf-8')
        trits = bytes_to_trits(seed_bytes)

        # Apply Curl hash
        hash_trits = curl_hash(trits, num_rounds=27)

        # Convert back to bytes for private key
        private_key = trits_to_bytes(hash_trits)

        # Generate address
        addr_data = private_key_to_address(private_key, compressed=True)

        if addr_data.get('valid'):
            return {
                'approach': 'direct_curl',
                'address': addr_data['address'],
                'hash160': addr_data['hash160'],
                'seed': seed
            }

        return None

    def test_approach_2_curl_then_sha256(self, seed: str) -> Optional[Dict]:
        """Approach 2: SHA256(Curl(seed)) → private key"""
        seed_bytes = seed.encode('utf-8')
        trits = bytes_to_trits(seed_bytes)
        hash_trits = curl_hash(trits, num_rounds=27)
        curl_bytes = trits_to_bytes(hash_trits)

        # Then SHA256
        private_key = sha256(curl_bytes)

        addr_data = private_key_to_address(private_key, compressed=True)

        if addr_data.get('valid'):
            return {
                'approach': 'curl_then_sha256',
                'address': addr_data['address'],
                'hash160': addr_data['hash160'],
                'seed': seed
            }

        return None

    def test_approach_3_sha256_then_curl(self, seed: str) -> Optional[Dict]:
        """Approach 3: Curl(SHA256(seed)) → private key"""
        seed_bytes = seed.encode('utf-8')
        sha_hash = sha256(seed_bytes)

        trits = bytes_to_trits(sha_hash)
        hash_trits = curl_hash(trits, num_rounds=27)
        private_key = trits_to_bytes(hash_trits)

        addr_data = private_key_to_address(private_key, compressed=True)

        if addr_data.get('valid'):
            return {
                'approach': 'sha256_then_curl',
                'address': addr_data['address'],
                'hash160': addr_data['hash160'],
                'seed': seed
            }

        return None

    def test_approach_4_curl_variants(self, seed: str) -> List[Dict]:
        """Approach 4: Different Curl round counts"""
        results = []

        for rounds in [7, 13, 19, 27, 81, 121]:
            seed_bytes = seed.encode('utf-8')
            trits = bytes_to_trits(seed_bytes)
            hash_trits = curl_hash(trits, num_rounds=rounds)
            private_key = trits_to_bytes(hash_trits)

            addr_data = private_key_to_address(private_key, compressed=True)

            if addr_data.get('valid'):
                results.append({
                    'approach': f'curl_rounds_{rounds}',
                    'address': addr_data['address'],
                    'hash160': addr_data['hash160'],
                    'seed': seed,
                    'rounds': rounds
                })

        return results

    def test_seed(self, seed_data: Dict) -> None:
        """Test a seed with all Curl approaches"""
        seed = seed_data['seed']
        seed_id = seed_data['id']

        approaches = [
            self.test_approach_1_direct_curl(seed),
            self.test_approach_2_curl_then_sha256(seed),
            self.test_approach_3_sha256_then_curl(seed),
        ] + self.test_approach_4_curl_variants(seed)

        for result in approaches:
            if result and result.get('valid', True):
                # Check if match
                if result['address'] == TARGET:
                    print(f"\n🎯 MATCH FOUND with Curl hash!")
                    print(f"Seed ID: {seed_id}")
                    print(f"Approach: {result['approach']}")
                    self.results['matches_found'].append({
                        'seed_id': seed_id,
                        **result,
                        'BREAKTHROUGH': 'CFB used his Curl invention!'
                    })

                # Check for special properties
                if result.get('hash160'):
                    hash160_bytes = bytes.fromhex(result['hash160'])
                    byte_sum = sum(hash160_bytes)

                    if byte_sum % 121 == 0 and byte_sum % 19 == 0:
                        self.results['special_properties'].append({
                            'seed_id': seed_id,
                            **result,
                            'byte_sum': byte_sum
                        })

    def run_test(self):
        """Run Curl hash test on special seeds"""
        print("=" * 80)
        print("TESTING IOTA CURL HASH HYPOTHESIS")
        print("=" * 80)
        print()
        print("Hypothesis: CFB used his IOTA Curl hash invention")
        print("Target: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
        print()

        # Load seeds
        with open('../public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)

        all_seeds = data['records']

        # Test priority seeds first
        priority_seeds = [
            # Reverse alphabet
            next((s for s in all_seeds if 'nmlkjihgfedcba' in s['seed']), None),
            # 1CFi seed
            next((s for s in all_seeds if 'mmmacecvbddmny' in s['seed']), None),
        ]

        priority_seeds = [s for s in priority_seeds if s is not None]

        print(f"Testing {len(priority_seeds)} priority seeds first...")
        print()

        for seed_data in priority_seeds:
            print(f"Testing seed {seed_data['id']}: {seed_data['seed'][:30]}...")
            self.test_seed(seed_data)

        if self.results['matches_found']:
            print("\n" + "=" * 80)
            print("CURL HASH BREAKTHROUGH!!!")
            print("=" * 80)
            print(json.dumps(self.results['matches_found'], indent=2))

            with open('CURL_HASH_BREAKTHROUGH.json', 'w') as f:
                json.dump(self.results, f, indent=2)

            return

        print("\nPriority seeds: No match with Curl")
        print("Testing ALL seeds with Curl hash...")
        print(f"Total seeds: {len(all_seeds)}")
        print()

        for i, seed_data in enumerate(all_seeds):
            if i % 1000 == 0:
                print(f"Progress: {i}/{len(all_seeds)} ({i/len(all_seeds)*100:.1f}%)")

            self.test_seed(seed_data)

        print("\n" + "=" * 80)
        print("CURL HASH TEST COMPLETE")
        print("=" * 80)
        print(f"Matches: {len(self.results['matches_found'])}")
        print(f"Special properties: {len(self.results['special_properties'])}")

        with open('CURL_HASH_TEST_RESULTS.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print("\nResults saved to: CURL_HASH_TEST_RESULTS.json")

if __name__ == '__main__':
    tester = CurlHashTester()
    tester.run_test()
