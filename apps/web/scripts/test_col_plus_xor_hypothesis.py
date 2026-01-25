#!/usr/bin/env python3
"""
TEST COL + XOR HYPOTHESIS
==========================

KRITISCHER DURCHBRUCH:
Col (20) + XOR (13) = 33

Hypothese:
CFB wählt Positionen [row, col] where:
  col + xor = step_value

Für 1CFB:
- Wahrscheinlich col + xor = 27 (step27 wie bei 1CFi)
- Oder col + xor = 33 (wie bei 1CFi!)
- Seed an dieser Position
- step27 + XOR variant

Dieser Script testet ALLE 180 Kandidaten-Positionen!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58

class ColPlusXORTester:
    """Test the col + xor = step hypothesis"""

    def __init__(self):
        self.target = {
            'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
        }

        self.seeds = []
        self.tested = 0
        self.close_matches = []

    def load_seeds(self):
        """Load all seeds"""
        print("="*80)
        print("LOADING SEEDS")
        print("="*80)
        print()

        try:
            with open('../public/data/qubic-seeds.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.seeds = data
                elif isinstance(data, dict) and 'records' in data:
                    self.seeds = [r.get('seed', r.get('value', '')) for r in data['records']]

            print(f"Loaded {len(self.seeds)} seeds")
            print()
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def apply_transformation(self, seed, method, xor_variant):
        """Apply transformation"""
        base_hash = hashlib.sha256(seed.encode()).digest()

        if method == 'step7':
            transformed = bytes((b + 7) % 256 for b in base_hash)
        elif method == 'step13':
            transformed = bytes((b + 13) % 256 for b in base_hash)
        elif method == 'step27':
            transformed = bytes((b + 27) % 256 for b in base_hash)
        elif method == 'step33':
            transformed = bytes((b + 33) % 256 for b in base_hash)
        else:
            transformed = base_hash

        if xor_variant != 0:
            transformed = bytes(b ^ xor_variant for b in transformed)

        return transformed

    def derive_address(self, private_key_bytes):
        """Derive Bitcoin address"""
        try:
            sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()

            public_key_bytes = vk.to_string()
            if public_key_bytes[63] % 2 == 0:
                public_key = b'\x02' + public_key_bytes[:32]
            else:
                public_key = b'\x03' + public_key_bytes[:32]

            sha256_hash = hashlib.sha256(public_key).digest()
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_hash)
            hash160 = ripemd160.digest()

            versioned = b'\x00' + hash160
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            address = base58.b58encode(versioned + checksum).decode('utf-8')

            return address, hash160.hex()

        except:
            return None, None

    def test_col_plus_xor_candidates(self):
        """Test all col + xor = step candidates"""
        print("="*80)
        print("TESTING COL + XOR = STEP HYPOTHESIS")
        print("="*80)
        print()

        print("Target: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
        print()

        # Generate candidates where col + xor = step
        candidates = []

        # Test all combinations
        for step in [7, 13, 27, 33]:
            for xor_var in [0, 7, 13, 19, 27, 33]:
                col = step - xor_var
                if 0 <= col < 128:
                    # All rows
                    for row in range(128):
                        index = row * 128 + col
                        if index < len(self.seeds):
                            candidates.append({
                                'row': row,
                                'col': col,
                                'index': index,
                                'step': f'step{step}',
                                'xor': xor_var,
                                'col_plus_xor': col + xor_var
                            })

        print(f"Testing {len(candidates)} candidates...")
        print(f"This might take 10-20 minutes")
        print()

        for i, cand in enumerate(candidates):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(candidates)} ({i/len(candidates)*100:.1f}%)")

            index = cand['index']
            seed = self.seeds[index]

            # Apply transformation
            private_key = self.apply_transformation(seed, cand['step'], cand['xor'])

            # Derive address
            address, hash160 = self.derive_address(private_key)

            if not address:
                continue

            self.tested += 1

            # Check exact match
            if address == self.target['address']:
                print()
                print("="*80)
                print("*** FOUND 1CFB!!! ***")
                print("="*80)
                print()
                print(f"Address:      {address}")
                print(f"Hash160:      {hash160}")
                print(f"Position:     [{cand['row']}, {cand['col']}]")
                print(f"Index:        {index}")
                print(f"Seed:         {seed}")
                print(f"Method:       {cand['step']}")
                print(f"XOR Variant:  {cand['xor']}")
                print(f"Col + XOR:    {cand['col_plus_xor']} = {cand['step']}")
                print(f"Private Key:  {private_key.hex()}")
                print()

                result = {
                    'found': True,
                    'address': address,
                    'position': [cand['row'], cand['col']],
                    'seed': seed,
                    'method': cand['step'],
                    'xor_variant': cand['xor'],
                    'col_plus_xor': cand['col_plus_xor'],
                    'private_key': private_key.hex()
                }

                with open('1CFB_COL_PLUS_XOR_FOUND.json', 'w') as f:
                    json.dump(result, f, indent=2)

                return result

            # Track close matches
            if address.startswith('1CFB'):
                self.close_matches.append({
                    'address': address,
                    'position': [cand['row'], cand['col']],
                    'method': cand['step'],
                    'xor': cand['xor'],
                    'col_plus_xor': cand['col_plus_xor']
                })

                print(f"  Close: {address} at [{cand['row']:3d}, {cand['col']:3d}], {cand['step']}+XOR{cand['xor']}")

        print()
        print("="*80)
        print("TESTING COMPLETE")
        print("="*80)
        print()
        print(f"Total tests: {self.tested}")
        print(f"Close matches: {len(self.close_matches)}")
        print()

        if self.close_matches:
            print("Close matches (starting with '1CFB'):")
            for match in self.close_matches[:10]:
                print(f"  {match['address']}")
                print(f"    Position: {match['position']}")
                print(f"    Method: {match['method']} + XOR {match['xor']}")
                print(f"    Col + XOR: {match['col_plus_xor']}")

        print()
        print("1CFB not found with col + xor = step hypothesis")
        print()

        result = {
            'found': False,
            'tested': self.tested,
            'close_matches': len(self.close_matches)
        }

        with open('1CFB_COL_PLUS_XOR_RESULTS.json', 'w') as f:
            json.dump(result, f, indent=2)

        return result

def main():
    print("="*80)
    print("COL + XOR = STEP HYPOTHESIS TEST")
    print("="*80)
    print()
    print("Testing the critical discovery:")
    print("  Col + XOR = Step Value")
    print()
    print("For 1CFi: Col (20) + XOR (13) = 33")
    print("For 1CFB: Testing all valid combinations")
    print()

    tester = ColPlusXORTester()

    if not tester.load_seeds():
        return

    result = tester.test_col_plus_xor_candidates()

    if result and result.get('found'):
        print("SUCCESS! The col + xor = step hypothesis was correct!")
    else:
        print("Hypothesis not confirmed with standard methods.")
        print("CFB may use additional constraints or different transformations.")

if __name__ == "__main__":
    main()
