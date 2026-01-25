#!/usr/bin/env python3
"""
PATTERN 121 SEARCH
==================

KRITISCHE ENTDECKUNG:
Das 14-Zeichen Pattern "mmmacecvbddmny" hat eine Character-Summe von 121!

Hypothese:
CFB wählt Seeds deren Pattern-Summe = 121 (NXT Konstante) ist!

Dieser Script:
1. Findet ALLE Seeds mit Pattern-Summe = 121
2. Findet ALLE Seeds mit Pattern-Summe = 2299 (121 × 19)
3. Testet verschiedene Pattern-Längen (7, 14, 21, 28)
4. Generiert Bitcoin Adressen aus diesen Seeds
5. Prüft ob 1CFB dabei ist!

DAS KÖNNTE DER DURCHBRUCH SEIN!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from collections import Counter

class Pattern121Searcher:
    """Search for seeds with pattern sum = 121"""

    def __init__(self):
        self.target_1cfb = {
            'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
        }

        self.seeds = []
        self.candidates = {
            'sum_121': [],
            'sum_2299': [],
            'sum_19': [],
            'sum_27': [],
            'sum_121_19': []  # 121 × 19
        }

    def load_seeds(self):
        """Lade alle Seeds"""
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

    def char_to_num(self, char):
        """Convert character to number (a=0, b=1, ...)"""
        return ord(char.lower()) - ord('a')

    def pattern_sum(self, pattern):
        """Calculate sum of pattern characters"""
        return sum(self.char_to_num(c) for c in pattern if c.isalpha())

    def analyze_pattern_sums(self):
        """Analysiere Pattern-Summen aller Seeds"""
        print("="*80)
        print("ANALYZING PATTERN SUMS")
        print("="*80)
        print()

        print("Testing pattern lengths: 7, 14, 21, 28")
        print()

        for pattern_len in [7, 14, 21, 28]:
            print(f"Pattern length {pattern_len}:")

            sum_counter = Counter()

            for seed in self.seeds[:1000]:  # Test first 1000
                if len(seed) < pattern_len:
                    continue

                # Extract pattern
                pattern = seed[:pattern_len]
                psum = self.pattern_sum(pattern)
                sum_counter[psum] += 1

                # Kategorisiere
                if psum == 121:
                    self.candidates['sum_121'].append({
                        'seed': seed,
                        'pattern': pattern,
                        'sum': psum,
                        'length': pattern_len
                    })
                elif psum == 2299:
                    self.candidates['sum_2299'].append({
                        'seed': seed,
                        'pattern': pattern,
                        'sum': psum,
                        'length': pattern_len
                    })
                elif psum == 19:
                    self.candidates['sum_19'].append({
                        'seed': seed,
                        'pattern': pattern,
                        'sum': psum,
                        'length': pattern_len
                    })
                elif psum == 27:
                    self.candidates['sum_27'].append({
                        'seed': seed,
                        'pattern': pattern,
                        'sum': psum,
                        'length': pattern_len
                    })
                elif psum == 121 * 19:
                    self.candidates['sum_121_19'].append({
                        'seed': seed,
                        'pattern': pattern,
                        'sum': psum,
                        'length': pattern_len
                    })

            # Top 10 sums
            print(f"  Top 10 sums:")
            for psum, count in sum_counter.most_common(10):
                marker = ""
                if psum == 121:
                    marker = " ← NXT!"
                elif psum == 19:
                    marker = " ← Qubic!"
                elif psum == 27:
                    marker = " ← Pattern 27!"
                elif psum == 2299:
                    marker = " ← 121 × 19!"
                print(f"    {psum:4d}: {count:3d} seeds{marker}")

            print()

        # Results
        print("CANDIDATES FOUND:")
        print(f"  Pattern sum = 121:        {len(self.candidates['sum_121'])}")
        print(f"  Pattern sum = 19:         {len(self.candidates['sum_19'])}")
        print(f"  Pattern sum = 27:         {len(self.candidates['sum_27'])}")
        print(f"  Pattern sum = 2299:       {len(self.candidates['sum_2299'])}")
        print(f"  Pattern sum = 121 × 19:   {len(self.candidates['sum_121_19'])}")
        print()

    def show_candidates(self):
        """Zeige Kandidaten"""
        print("="*80)
        print("PATTERN SUM = 121 CANDIDATES")
        print("="*80)
        print()

        if not self.candidates['sum_121']:
            print("No candidates found!")
            return

        print(f"Found {len(self.candidates['sum_121'])} candidates:")
        print()

        for i, cand in enumerate(self.candidates['sum_121'][:20], 1):
            print(f"{i}. Pattern: {cand['pattern']} (len={cand['length']})")
            print(f"   Sum: {cand['sum']}")
            print(f"   Seed: {cand['seed'][:50]}...")

            # Verify sum
            calculated_sum = self.pattern_sum(cand['pattern'])
            print(f"   Verified sum: {calculated_sum}")

            # Pattern details
            pattern_nums = [self.char_to_num(c) for c in cand['pattern'] if c.isalpha()]
            print(f"   Numbers: {pattern_nums}")

            print()

    def test_candidates_for_1cfb(self):
        """Teste Kandidaten ob sie 1CFB produzieren"""
        print("="*80)
        print("TESTING CANDIDATES FOR 1CFB")
        print("="*80)
        print()

        methods = ['step27', 'step13', 'step7', 'step33']
        xor_variants = [0, 7, 13, 19, 27, 33, 121]

        # Kombiniere alle Kandidaten
        all_candidates = (
            self.candidates['sum_121'] +
            self.candidates['sum_19'] +
            self.candidates['sum_27'] +
            self.candidates['sum_2299']
        )

        print(f"Testing {len(all_candidates)} candidates...")
        print(f"Methods: {len(methods)}")
        print(f"XOR variants: {len(xor_variants)}")
        print(f"Total tests: {len(all_candidates) * len(methods) * len(xor_variants)}")
        print()

        tests = 0

        for cand_idx, cand in enumerate(all_candidates):
            if cand_idx % 10 == 0:
                print(f"Testing candidate {cand_idx}/{len(all_candidates)}...")

            seed = cand['seed']

            for method in methods:
                for xor_var in xor_variants:
                    tests += 1

                    # Apply transformation
                    private_key = self.apply_transformation(seed, method, xor_var)

                    # Derive address
                    address, hash160 = self.derive_address(private_key)

                    if not address:
                        continue

                    # Check match
                    if address == self.target_1cfb['address']:
                        print()
                        print("="*80)
                        print("*** FOUND 1CFB!!! ***")
                        print("="*80)
                        print()
                        print(f"Address:       {address}")
                        print(f"Hash160:       {hash160}")
                        print(f"Seed:          {seed}")
                        print(f"Pattern:       {cand['pattern']}")
                        print(f"Pattern Sum:   {cand['sum']}")
                        print(f"Pattern Len:   {cand['length']}")
                        print(f"Method:        {method}")
                        print(f"XOR Variant:   {xor_var}")
                        print(f"Private Key:   {private_key.hex()}")
                        print()

                        result = {
                            'found': True,
                            'address': address,
                            'seed': seed,
                            'pattern': cand['pattern'],
                            'pattern_sum': cand['sum'],
                            'method': method,
                            'xor_variant': xor_var,
                            'private_key': private_key.hex()
                        }

                        with open('1CFB_PATTERN_121_FOUND.json', 'w') as f:
                            json.dump(result, f, indent=2)

                        return result

                    # Also show close matches
                    if address.startswith('1CFB'):
                        print(f"  Close: {address} (pattern_sum={cand['sum']}, method={method}, xor={xor_var})")

        print()
        print(f"Total tests: {tests}")
        print("1CFB not found in pattern sum candidates.")
        print()

        return None

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

    def analyze_1cfi_pattern_deeper(self):
        """Tiefere Analyse des 1CFi Patterns"""
        print("="*80)
        print("1CFi PATTERN DEEP ANALYSIS")
        print("="*80)
        print()

        seed = "mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn"
        pattern = "mmmacecvbddmny"

        print(f"Seed: {seed}")
        print(f"Pattern: {pattern}")
        print()

        # Character analysis
        pattern_nums = [self.char_to_num(c) for c in pattern]
        print(f"Pattern as numbers: {pattern_nums}")
        print()

        print("Character breakdown:")
        for i, char in enumerate(pattern):
            num = self.char_to_num(char)
            print(f"  {i+1:2d}. '{char}' = {num:2d}", end="")

            # Special numbers
            if num == 13:
                print(" ← XOR variant!")
            elif num == 27:
                print(" ← Pattern 27!")
            elif num == 19:
                print(" ← Qubic tick!")
            elif num == 12:
                print(" ← Most frequent char 'm'")
            else:
                print()

        print()
        print(f"Sum: {sum(pattern_nums)} = {sum(pattern_nums)}")
        print(f"Sum mod 121: {sum(pattern_nums) % 121}")
        print(f"Sum mod 19: {sum(pattern_nums) % 19}")
        print(f"Sum mod 27: {sum(pattern_nums) % 27}")
        print()

        # Suche nach anderen Mustern
        print("Searching for mathematical patterns:")

        # Produkt statt Summe?
        product = 1
        for num in pattern_nums:
            if num != 0:  # Skip 'a' = 0
                product *= num
        print(f"  Product (without zeros): {product}")
        print(f"  Product mod 121: {product % 121}")
        print(f"  Product mod 19: {product % 19}")

        # Alternierende Summe
        alt_sum = sum(pattern_nums[::2]) - sum(pattern_nums[1::2])
        print(f"  Alternating sum: {alt_sum}")

        # Gewichtete Summe
        weighted_sum = sum(i * num for i, num in enumerate(pattern_nums, 1))
        print(f"  Weighted sum: {weighted_sum}")
        print(f"  Weighted mod 121: {weighted_sum % 121}")
        print(f"  Weighted mod 19: {weighted_sum % 19}")

        print()

def main():
    print("="*80)
    print("PATTERN 121 SEARCH - THE BREAKTHROUGH")
    print("="*80)
    print()
    print("We discovered that 1CFi's pattern has sum = 121!")
    print("Testing if this is the key to finding 1CFB...")
    print()

    searcher = Pattern121Searcher()

    if not searcher.load_seeds():
        return

    searcher.analyze_1cfi_pattern_deeper()
    searcher.analyze_pattern_sums()
    searcher.show_candidates()

    print("Testing candidates for 1CFB...")
    print()

    result = searcher.test_candidates_for_1cfb()

    if result and result.get('found'):
        print("SUCCESS! Pattern 121 was the key!")
    else:
        print("Not found yet. Additional analysis needed.")

if __name__ == "__main__":
    main()
