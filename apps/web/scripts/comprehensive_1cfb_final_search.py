#!/usr/bin/env python3
"""
COMPREHENSIVE 1CFB FINAL SEARCH
================================

Multi-Ansatz Strategie:
1. REVERSE ALPHABET SEED - Intensive Testing (Hauptfokus)
2. Alle 24 anderen special seeds testen
3. Geometrische Anna Matrix Patterns
4. Extended Transformations (double/triple step)
5. Pattern-basierte Seed-Konstruktion

Alle Ansätze parallel verfolgen!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from collections import Counter, defaultdict

class ComprehensiveFinalSearcher:
    """Multi-approach comprehensive search"""

    def __init__(self):
        self.target = {
            'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
        }

        # The special seeds
        self.reverse_alphabet_seed = 'nmlkjihgfedcbazyxwvutsrqponmlkjihgfedcbazyxwvutsrq'

        self.all_special_seeds = [
            'mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn',  # 1CFi
            'aaaaauwnwmenauukuyelaguvxlwrriimiukiknijmfwviisjym',
            'aqqsysdvnsaaauqkksquakkkkcakacamasqsabpizcakaurkns',
            'buqdvkqeweaayebuqdvkqeweaayebuqdvkqeweaayebuqdvkqe',
            'emcigqgywucmuwuymosmcmkooekwgymgciewzuwwcwwagyeosq',
            'emqtgbksvkugusemqtgbksvkugusemqtgbksvkugusemqtgbks',
            'examcxctwtxnsnfkwttteqrjuxxjefxacacccccsypuocpcqum',
            'gecgqewufkkxaaaakuodsycakmcyweeezbmnwwyextxxxqrmnv',
            'ifdcmcmasyaaooifdcmcmasyaaooifdcmcmasyaaooifdcmcma',
            'iuuluusmsksuskiuuluusmsksuskiuuluusmsksuskiuuluusm',
            'jjfjemsgsqwqtjjjfjemsgsqwqtjjjfjemsgsqwqtjjjfjemsg',
            'jphhvvpglfaaaaaaaaaewamanayeyaaaaaywrlaebhiepesefa',
            'kfeuurvrpnlnvokfeuurvrpnlnvokfeuurvrpnlnvokfeuurvr',
            'mhmkujikwdwdqdivwlnmaaammmammmammmmkayammmacepsmmk',
            'ngegagagcaaaaangegagagcaaaaangegagagcaaaaangegagag',
            'nlterahabvxzpznlterahabvxzpznlterahabvxzpznlteraha',
            'nmlkjihgfedcbazyxwvutsrqponmlkjihgfedcbazyxwvutsrq',  # Reverse alphabet!
            'qxezqtwynjkkmkqxezqtwynjkkmkqxezqtwynjkkmkqxezqtwy',
            'rjnsffguesiqmqrjnsffguesiqmqrjnsffguesiqmqrjnsffgu',
            'sspgsstsyolzvstxzwjdkarbnqjxjpztqyeyqmqaicpqqmkmiq',
            'ulxjwjvppvrzrhulxjwjvppvrzrhulxjwjvppvrzrhulxjwjvp',
            'uqgtcecamaecemuqgtcecamaecemuqgtcecamaecemuqgtceca',
            'uvqqasaruxamijqusasqgwqwevaygrykstnkeboxmxlfiffeke',
            'wwaawwwwigcisuwwaawwwwigcisuwwaawwwwigcisuwwaawwww',
            'zsescsahvdxnznzsescsahvdxnznzsescsahvdxnznzsescsah',
        ]

        self.seeds = []
        self.results = {
            'approach_1_reverse_alphabet': None,
            'approach_2_all_special_seeds': [],
            'approach_3_geometric_patterns': [],
            'approach_4_extended_transforms': [],
            'approach_5_constructed_seeds': []
        }

    def load_seeds(self):
        """Load all seeds"""
        try:
            with open('../public/data/qubic-seeds.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.seeds = data
                elif isinstance(data, dict) and 'records' in data:
                    self.seeds = [r.get('seed', r.get('value', '')) for r in data['records']]
            return True
        except Exception as e:
            print(f"Error loading seeds: {e}")
            return False

    def apply_transformation(self, seed, method, xor_variant):
        """Apply transformation with extended methods"""
        base_hash = hashlib.sha256(seed.encode()).digest()

        # Standard methods
        if method == 'step7':
            transformed = bytes((b + 7) % 256 for b in base_hash)
        elif method == 'step13':
            transformed = bytes((b + 13) % 256 for b in base_hash)
        elif method == 'step27':
            transformed = bytes((b + 27) % 256 for b in base_hash)
        elif method == 'step33':
            transformed = bytes((b + 33) % 256 for b in base_hash)

        # Extended methods
        elif method == 'double_step27':
            temp = bytes((b + 27) % 256 for b in base_hash)
            transformed = bytes((b + 27) % 256 for b in temp)
        elif method == 'triple_step27':
            temp1 = bytes((b + 27) % 256 for b in base_hash)
            temp2 = bytes((b + 27) % 256 for b in temp1)
            transformed = bytes((b + 27) % 256 for b in temp2)

        # Reverse methods
        elif method == 'step27_reverse':
            transformed = bytes((b - 27) % 256 for b in base_hash)
        elif method == 'step13_reverse':
            transformed = bytes((b - 13) % 256 for b in base_hash)

        # Multiplication methods
        elif method == 'mult27':
            transformed = bytes((b * 27) % 256 for b in base_hash)
        elif method == 'mult13':
            transformed = bytes((b * 13) % 256 for b in base_hash)

        else:
            transformed = base_hash

        # Apply XOR
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

    def approach_1_reverse_alphabet_intensive(self):
        """APPROACH 1: Intensive testing of reverse alphabet seed"""
        print("="*80)
        print("APPROACH 1: REVERSE ALPHABET SEED INTENSIVE TEST")
        print("="*80)
        print()

        print(f"Seed: {self.reverse_alphabet_seed}")
        print()
        print("This seed is EXTREMELY special:")
        print("  - Complete alphabet sequence REVERSED")
        print("  - Perfect symmetry (mirror)")
        print("  - Has mod 121=0 AND mod 19=0 properties")
        print("  - Fits CFB's 'Mirror' hints perfectly!")
        print()

        # Extended method list for this special seed
        methods = [
            'step7', 'step13', 'step27', 'step33',
            'double_step27', 'triple_step27',
            'step27_reverse', 'step13_reverse',
            'mult27', 'mult13'
        ]

        # Extended XOR list
        xor_variants = [0, 7, 13, 19, 27, 33, 121, 127, 255]

        total_tests = len(methods) * len(xor_variants)
        print(f"Testing {total_tests} combinations on this ONE seed...")
        print()

        tested = 0
        for method in methods:
            for xor_var in xor_variants:
                tested += 1

                if tested % 10 == 0:
                    print(f"  Progress: {tested}/{total_tests} ({tested/total_tests*100:.1f}%)")

                private_key = self.apply_transformation(self.reverse_alphabet_seed, method, xor_var)
                address, hash160 = self.derive_address(private_key)

                if not address:
                    continue

                # Check match
                if address == self.target['address']:
                    print()
                    print("="*80)
                    print("*** FOUND 1CFB WITH REVERSE ALPHABET SEED! ***")
                    print("="*80)
                    print()
                    print(f"Address:      {address}")
                    print(f"Seed:         {self.reverse_alphabet_seed}")
                    print(f"Method:       {method}")
                    print(f"XOR Variant:  {xor_var}")
                    print(f"Private Key:  {private_key.hex()}")
                    print()

                    self.results['approach_1_reverse_alphabet'] = {
                        'found': True,
                        'address': address,
                        'seed': self.reverse_alphabet_seed,
                        'method': method,
                        'xor_variant': xor_var,
                        'private_key': private_key.hex()
                    }

                    return True

                # Track close matches
                if address.startswith('1CFB'):
                    print(f"  Close: {address} ({method} + XOR {xor_var})")

        print()
        print(f"Reverse alphabet seed tested: {tested} combinations")
        print("Not found with standard transformations")
        print()

        return False

    def approach_2_all_special_seeds(self):
        """APPROACH 2: Test all 25 special seeds"""
        print("="*80)
        print("APPROACH 2: ALL 25 SPECIAL SEEDS")
        print("="*80)
        print()

        print(f"Testing all {len(self.all_special_seeds)} special seeds...")
        print("Methods: step7, step13, step27, step33, double_step27")
        print("XOR variants: 0, 7, 13, 19, 27, 33")
        print()

        methods = ['step7', 'step13', 'step27', 'step33', 'double_step27']
        xor_variants = [0, 7, 13, 19, 27, 33]

        total = len(self.all_special_seeds) * len(methods) * len(xor_variants)
        tested = 0

        for seed_idx, seed in enumerate(self.all_special_seeds):
            for method in methods:
                for xor_var in xor_variants:
                    tested += 1

                    if tested % 100 == 0:
                        print(f"  Progress: {tested}/{total} ({tested/total*100:.1f}%)")

                    private_key = self.apply_transformation(seed, method, xor_var)
                    address, hash160 = self.derive_address(private_key)

                    if not address:
                        continue

                    if address == self.target['address']:
                        print()
                        print("="*80)
                        print("*** FOUND 1CFB! ***")
                        print("="*80)
                        print()
                        print(f"Address:      {address}")
                        print(f"Seed:         {seed}")
                        print(f"Seed Index:   {seed_idx}")
                        print(f"Method:       {method}")
                        print(f"XOR Variant:  {xor_var}")
                        print(f"Private Key:  {private_key.hex()}")
                        print()

                        result = {
                            'found': True,
                            'address': address,
                            'seed': seed,
                            'seed_index': seed_idx,
                            'method': method,
                            'xor_variant': xor_var,
                            'private_key': private_key.hex()
                        }

                        self.results['approach_2_all_special_seeds'].append(result)
                        return True

        print()
        print(f"All special seeds tested: {tested} combinations")
        print("Not found")
        print()

        return False

    def approach_3_geometric_patterns(self):
        """APPROACH 3: Geometric patterns in Anna Matrix"""
        print("="*80)
        print("APPROACH 3: GEOMETRIC ANNA MATRIX PATTERNS")
        print("="*80)
        print()

        print("Analyzing geometric patterns around 1CFi position [91, 20]...")
        print()

        # Test positions around 1CFi
        base_row, base_col = 91, 20

        # Mirror positions
        patterns = [
            ('Mirror center', 128 - base_row - 1, 128 - base_col - 1),
            ('Mirror row', 128 - base_row - 1, base_col),
            ('Mirror col', base_row, 128 - base_col - 1),
            ('Diagonal', base_col, base_row),  # Swap row/col
            ('Plus 27 row', base_row + 27, base_col),
            ('Plus 13 col', base_row, base_col + 13),
            ('Minus 27 row', base_row - 27, base_col),
        ]

        tested = 0
        for name, row, col in patterns:
            if not (0 <= row < 128 and 0 <= col < 128):
                continue

            index = row * 128 + col
            if index >= len(self.seeds):
                continue

            seed = self.seeds[index]
            print(f"Testing {name}: [{row}, {col}]")
            print(f"  Seed: {seed[:40]}...")

            # Test with 1CFi's method
            for xor_var in [0, 7, 13, 19, 27, 33]:
                tested += 1
                private_key = self.apply_transformation(seed, 'step27', xor_var)
                address, hash160 = self.derive_address(private_key)

                if address == self.target['address']:
                    print()
                    print(f"*** FOUND with {name} pattern! ***")
                    print(f"Position: [{row}, {col}]")
                    print(f"XOR: {xor_var}")
                    print()
                    return True

        print(f"Geometric patterns tested: {tested}")
        print("Not found")
        print()

        return False

    def approach_4_seed_variations(self):
        """APPROACH 4: Variations of 1CFi seed"""
        print("="*80)
        print("APPROACH 4: SEED VARIATIONS")
        print("="*80)
        print()

        base_seed = 'mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn'
        pattern = 'mmmacecvbddmny'

        print(f"Base seed: {base_seed}")
        print(f"Pattern: {pattern}")
        print()

        variations = []

        # Variation 1: Reverse pattern
        reversed_pattern = pattern[::-1]
        variations.append(('Reversed pattern', (reversed_pattern * 4)[:55]))

        # Variation 2: Shift pattern
        shifted_pattern = pattern[1:] + pattern[0]
        variations.append(('Shifted pattern', (shifted_pattern * 4)[:55]))

        # Variation 3: Character swap
        swapped = pattern.replace('m', 'M').replace('n', 'N')
        variations.append(('Case swapped', (swapped * 4)[:55].lower()))

        # Variation 4: Use 'b' instead of 'm' (m=12, b=1)
        replaced = pattern.replace('m', 'b')
        variations.append(('M→B replacement', (replaced * 4)[:55]))

        # Variation 5: Double pattern
        variations.append(('Double pattern', (pattern + pattern)[:55]))

        tested = 0
        for name, seed in variations:
            print(f"Testing: {name}")
            print(f"  Seed: {seed[:40]}...")

            for method in ['step27', 'step13', 'double_step27']:
                for xor_var in [0, 7, 13, 19, 27, 33]:
                    tested += 1
                    private_key = self.apply_transformation(seed, method, xor_var)
                    address, hash160 = self.derive_address(private_key)

                    if address == self.target['address']:
                        print()
                        print(f"*** FOUND with {name}! ***")
                        print(f"Method: {method}, XOR: {xor_var}")
                        print()
                        return True

        print(f"Variations tested: {tested}")
        print("Not found")
        print()

        return False

    def save_results(self):
        """Save all results"""
        output = {
            'date': '2026-01-09',
            'target': self.target,
            'results': self.results,
            'summary': {
                'reverse_alphabet_found': self.results['approach_1_reverse_alphabet'] is not None,
                'special_seeds_found': len(self.results['approach_2_all_special_seeds']) > 0,
                'geometric_found': len(self.results['approach_3_geometric_patterns']) > 0,
            }
        }

        with open('COMPREHENSIVE_FINAL_SEARCH_RESULTS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("Results saved to: COMPREHENSIVE_FINAL_SEARCH_RESULTS.json")

def main():
    print("="*80)
    print("COMPREHENSIVE 1CFB FINAL SEARCH")
    print("="*80)
    print()
    print("Multi-Approach Strategy:")
    print("1. Reverse alphabet seed (intensive)")
    print("2. All 25 special seeds")
    print("3. Geometric Anna Matrix patterns")
    print("4. Seed variations")
    print()
    print("Running ALL approaches...")
    print()

    searcher = ComprehensiveFinalSearcher()

    if not searcher.load_seeds():
        print("Failed to load seeds")
        return

    # Run all approaches
    found = False

    # Approach 1: Reverse alphabet (MAIN FOCUS)
    if not found:
        found = searcher.approach_1_reverse_alphabet_intensive()

    # Approach 2: All special seeds
    if not found:
        found = searcher.approach_2_all_special_seeds()

    # Approach 3: Geometric patterns
    if not found:
        found = searcher.approach_3_geometric_patterns()

    # Approach 4: Seed variations
    if not found:
        found = searcher.approach_4_seed_variations()

    # Save results
    searcher.save_results()

    print()
    print("="*80)
    print("COMPREHENSIVE SEARCH COMPLETE")
    print("="*80)
    print()

    if found:
        print("SUCCESS! 1CFB generation method discovered!")
    else:
        print("1CFB not found with tested approaches.")
        print("Further analysis needed.")

if __name__ == "__main__":
    main()
