#!/usr/bin/env python3
"""
EXHAUSTIVE 1CFB SEARCH
======================

Versucht ALLE möglichen Transformationen auf ALLE Seeds anzuwenden
um die exakte Generierungs-Methode für 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg zu finden.

Strategie:
1. Lade alle 23,765 Qubic Seeds
2. Wende ALLE Transformationen an:
   - step7, step13, step27, step33
   - col, row, diag
3. Wende ALLE XOR Varianten an:
   - 0, 7, 13, 19, 27, 33, 121
4. Generiere Bitcoin Adresse
5. Vergleiche mit 1CFB

Total: 23,765 × 7 methods × 7 XOR = 1,164,485 tests
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
import sys
from datetime import datetime

class ExhaustiveSearcher:
    """Exhaustive search for 1CFB generation method"""

    def __init__(self):
        self.target = {
            'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
        }

        self.methods = ['step7', 'step13', 'step27', 'step33', 'col', 'row', 'diag']
        self.xor_variants = [0, 7, 13, 19, 27, 33, 121]

        self.seeds = []
        self.total_tests = 0
        self.progress_counter = 0

    def load_seeds(self):
        """Lade alle Qubic Seeds"""
        print("="*80)
        print("LOADING QUBIC SEEDS")
        print("="*80)
        print()

        try:
            with open('../public/data/qubic-seeds.json', 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                self.seeds = data
            elif isinstance(data, dict) and 'records' in data:
                self.seeds = [r.get('seed', r.get('value', '')) for r in data['records']]
            else:
                print("ERROR: Cannot parse qubic-seeds.json")
                return False

            print(f"Loaded {len(self.seeds)} seeds")
            print(f"Total combinations to test: {len(self.seeds) * len(self.methods) * len(self.xor_variants):,}")
            print()
            return True

        except Exception as e:
            print(f"Error loading seeds: {e}")
            return False

    def apply_transformation(self, seed, method, xor_variant):
        """Wende eine spezifische Transformation an"""
        # SHA256 als Basis
        base_hash = hashlib.sha256(seed.encode()).digest()

        # Apply method transformation
        if method == 'step7':
            transformed = bytes((b + 7) % 256 for b in base_hash)
        elif method == 'step13':
            transformed = bytes((b + 13) % 256 for b in base_hash)
        elif method == 'step27':
            transformed = bytes((b + 27) % 256 for b in base_hash)
        elif method == 'step33':
            transformed = bytes((b + 33) % 256 for b in base_hash)
        elif method == 'col':
            # Column-based transformation (hypothetical)
            transformed = bytes((b * 7) % 256 for b in base_hash)
        elif method == 'row':
            # Row-based transformation (hypothetical)
            transformed = bytes((b * 13) % 256 for b in base_hash)
        elif method == 'diag':
            # Diagonal transformation (hypothetical)
            transformed = bytes((b * 27) % 256 for b in base_hash)
        else:
            transformed = base_hash

        # Apply XOR
        if xor_variant != 0:
            transformed = bytes(b ^ xor_variant for b in transformed)

        return transformed

    def derive_address(self, private_key_bytes):
        """Derive Bitcoin address from private key"""
        try:
            # Create signing key
            sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()

            # Compressed public key
            public_key_bytes = vk.to_string()
            if public_key_bytes[63] % 2 == 0:
                public_key = b'\x02' + public_key_bytes[:32]
            else:
                public_key = b'\x03' + public_key_bytes[:32]

            # Hash160
            sha256_hash = hashlib.sha256(public_key).digest()
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_hash)
            hash160 = ripemd160.digest()

            # Address
            versioned = b'\x00' + hash160
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            address = base58.b58encode(versioned + checksum).decode('utf-8')

            return address, hash160.hex()

        except Exception as e:
            return None, None

    def search(self):
        """Hauptsuchfunktion"""
        print("="*80)
        print("STARTING EXHAUSTIVE SEARCH")
        print("="*80)
        print()

        print(f"Target: {self.target['address']}")
        print(f"Hash160: {self.target['hash160']}")
        print()
        print(f"Testing {len(self.seeds)} seeds × {len(self.methods)} methods × {len(self.xor_variants)} XOR variants")
        print(f"Total tests: {len(self.seeds) * len(self.methods) * len(self.xor_variants):,}")
        print()
        print("This will take approximately 2-4 hours...")
        print("Progress updates every 10,000 tests")
        print()

        start_time = datetime.now()
        results = []

        for seed_idx, seed in enumerate(self.seeds):
            if not seed or len(seed) == 0:
                continue

            for method in self.methods:
                for xor_variant in self.xor_variants:
                    self.progress_counter += 1

                    # Progress update
                    if self.progress_counter % 10000 == 0:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        tests_per_sec = self.progress_counter / elapsed if elapsed > 0 else 0
                        remaining = (len(self.seeds) * len(self.methods) * len(self.xor_variants) - self.progress_counter) / tests_per_sec if tests_per_sec > 0 else 0

                        print(f"Progress: {self.progress_counter:,} tests ({self.progress_counter/(len(self.seeds)*len(self.methods)*len(self.xor_variants))*100:.1f}%)")
                        print(f"  Speed: {tests_per_sec:.0f} tests/sec")
                        print(f"  ETA: {remaining/60:.0f} minutes")
                        print()

                    # Apply transformation
                    private_key = self.apply_transformation(seed, method, xor_variant)

                    # Derive address
                    address, hash160 = self.derive_address(private_key)

                    if not address:
                        continue

                    # Check match
                    if address == self.target['address']:
                        print()
                        print("="*80)
                        print("*** FOUND 1CFB GENERATION METHOD! ***")
                        print("="*80)
                        print()
                        print(f"Address:         {address}")
                        print(f"Hash160:         {hash160}")
                        print(f"Seed:            {seed}")
                        print(f"Seed Index:      {seed_idx}")
                        print(f"Method:          {method}")
                        print(f"XOR Variant:     {xor_variant}")
                        print(f"Private Key:     {private_key.hex()}")
                        print()

                        result = {
                            'found': True,
                            'address': address,
                            'hash160': hash160,
                            'seed': seed,
                            'seed_index': seed_idx,
                            'method': method,
                            'xor_variant': xor_variant,
                            'private_key_hex': private_key.hex(),
                            'tests_performed': self.progress_counter,
                            'time_elapsed': str(datetime.now() - start_time)
                        }

                        results.append(result)

                        # Save immediately
                        with open('1CFB_FOUND.json', 'w') as f:
                            json.dump(result, f, indent=2)

                        print("Result saved to: 1CFB_FOUND.json")
                        print()

                        return result

                    # Also check if we get the right hash160 (even if address differs)
                    if hash160 == self.target['hash160']:
                        print()
                        print("="*80)
                        print("*** FOUND MATCHING HASH160! ***")
                        print("="*80)
                        print()
                        print(f"Address:         {address}")
                        print(f"Hash160:         {hash160}")
                        print(f"Seed:            {seed}")
                        print(f"Method:          {method}")
                        print(f"XOR Variant:     {xor_variant}")
                        print()

        # No match found
        elapsed = datetime.now() - start_time
        print()
        print("="*80)
        print("SEARCH COMPLETE - NO MATCH FOUND")
        print("="*80)
        print()
        print(f"Total tests performed: {self.progress_counter:,}")
        print(f"Time elapsed: {elapsed}")
        print()
        print("1CFB was not generated using these transformation methods.")
        print("The generation method may be more complex or use different seeds.")
        print()

        result = {
            'found': False,
            'tests_performed': self.progress_counter,
            'time_elapsed': str(elapsed),
            'conclusion': 'No match found with standard transformation methods'
        }

        with open('1CFB_SEARCH_RESULTS.json', 'w') as f:
            json.dump(result, f, indent=2)

        return result

def main():
    """Main execution"""
    print("="*80)
    print("EXHAUSTIVE SEARCH FOR 1CFB GENERATION METHOD")
    print("="*80)
    print()
    print("This script will test ALL possible transformations")
    print("to find the exact method used to generate:")
    print("1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
    print()
    print("WARNING: This will take 2-4 hours to complete!")
    print()

    searcher = ExhaustiveSearcher()

    if not searcher.load_seeds():
        print("Failed to load seeds. Exiting.")
        return

    print("Starting search in 5 seconds...")
    print("Press Ctrl+C to cancel")
    print()

    import time
    time.sleep(5)

    result = searcher.search()

    if result and result.get('found'):
        print()
        print("SUCCESS! The generation method has been discovered!")
    else:
        print()
        print("Search complete. Method not found in standard transformations.")

if __name__ == "__main__":
    main()
