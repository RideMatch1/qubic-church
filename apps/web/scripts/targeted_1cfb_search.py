#!/usr/bin/env python3
"""
TARGETED 1CFB SEARCH
====================

Schnellere, gezielte Suche die nur die vielversprechendsten Seeds testet:
1. Seeds mit 14-Zeichen Muster
2. Seeds mit hoher Character-Overlap
3. Seeds von Adressen mit mod 121=0 AND mod 19=0
4. Reverse alphabet Seed

Estimated time: 5-15 minutes (vs 2-4 hours for exhaustive)
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from datetime import datetime

class TargetedSearcher:
    """Targeted search focusing on most promising candidates"""

    def __init__(self):
        self.target = {
            'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
        }

        # Erweiterte Methoden und XOR Varianten
        self.methods = [
            'step7', 'step13', 'step27', 'step33',
            'col', 'row', 'diag',
            'step7_reverse', 'step13_reverse', 'step27_reverse',
            'double_step27', 'triple_step27'
        ]

        self.xor_variants = [0, 7, 13, 19, 27, 33, 121, 127, 255]

        self.priority_seeds = []
        self.total_tests = 0

    def load_priority_seeds(self):
        """Lade nur die vielversprechendsten Seeds"""
        print("="*80)
        print("LOADING PRIORITY SEEDS")
        print("="*80)
        print()

        # Seeds from addresses with mod 121=0 AND mod 19=0
        priority_candidates = [
            "aaaaauwnwmenauukuyelaguvxlwrriimiukiknijmfwviisjym",
            "aqqsysdvnsaaauqkksquakkkkcakacamasqsabpizcakaurkns",
            "buqdvkqeweaayebuqdvkqeweaayebuqdvkqeweaayebuqdvkqe",
            "emcigqgywucmuwuymosmcmkooekwgymgciewzuwwcwwagyeosq",
            "emqtgbksvkugusemqtgbksvkugusemqtgbksvkugusemqtgbks",
            "examcxctwtxnsnfkwttteqrjuxxjefxacacccccsypuocpcqum",
            "gecgqewufkkxaaaakuodsycakmcyweeezbmnwwyextxxxqrmnv",  # Full overlap!
            "ifdcmcmasyaaooifdcmcmasyaaooifdcmcmasyaaooifdcmcma",
            "iuuluusmsksuskiuuluusmsksuskiuuluusmsksuskiuuluusm",
            "jjfjemsgsqwqtjjjfjemsgsqwqtjjjfjemsgsqwqtjjjfjemsg",
            "jphhvvpglfaaaaaaaaaewamanayeyaaaaaywrlaebhiepesefa",
            "kfeuurvrpnlnvokfeuurvrpnlnvokfeuurvrpnlnvokfeuurvr",
            "mhmkujikwdwdqdivwlnmaaammmammmammmmkayammmacepsmmk",
            "mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn",  # 1CFi seed!
            "ngegagagcaaaaangegagagcaaaaangegagagcaaaaangegagag",
            "nlterahabvxzpznlterahabvxzpznlterahabvxzpznlteraha",
            "nmlkjihgfedcbazyxwvutsrqponmlkjihgfedcbazyxwvutsrq",  # Reverse alphabet!
            "qxezqtwynjkkmkqxezqtwynjkkmkqxezqtwynjkkmkqxezqtwy",
            "rjnsffguesiqmqrjnsffguesiqmqrjnsffguesiqmqrjnsffgu",
            "sspgsstsyolzvstxzwjdkarbnqjxjpztqyeyqmqaicpqqmkmiq",  # Full overlap!
            "ulxjwjvppvrzrhulxjwjvppvrzrhulxjwjvppvrzrhulxjwjvp",
            "uqgtcecamaecemuqgtcecamaecemuqgtcecamaecemuqgtceca",
            "uvqqasaruxamijqusasqgwqwevaygrykstnkeboxmxlfiffeke",
            "wwaawwwwigcisuwwaawwwwigcisuwwaawwwwigcisuwwaawwww",
            "zsescsahvdxnznzsescsahvdxnznzsescsahvdxnznzsescsah",
        ]

        # Zusätzliche Variationen der vielversprechendsten Seeds
        variations = []

        # Reverse alphabet variations
        variations.append("zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba")
        variations.append("abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz")

        # 1CFi seed variations
        base_1cfi = "mmmacecvbddmny"
        variations.append(base_1cfi * 4)  # Repeat 4x
        variations.append((base_1cfi[::-1]) * 4)  # Reversed pattern

        # Character swap variations
        variations.append("mmmececvbddmnymmmececvbddmnymmmececvbddmnymmmececvbddmn")
        variations.append("nynmddbvcecammnynmddbvcecammnynmddbvcecammnynmddbvce")

        self.priority_seeds = priority_candidates + variations
        print(f"Loaded {len(self.priority_seeds)} priority seeds")
        print(f"Total tests: {len(self.priority_seeds) * len(self.methods) * len(self.xor_variants):,}")
        print()

    def apply_transformation(self, seed, method, xor_variant):
        """Erweiterte Transformations-Methoden"""
        base_hash = hashlib.sha256(seed.encode()).digest()

        # Standard transformations
        if method == 'step7':
            transformed = bytes((b + 7) % 256 for b in base_hash)
        elif method == 'step13':
            transformed = bytes((b + 13) % 256 for b in base_hash)
        elif method == 'step27':
            transformed = bytes((b + 27) % 256 for b in base_hash)
        elif method == 'step33':
            transformed = bytes((b + 33) % 256 for b in base_hash)

        # Reverse transformations (subtract instead of add)
        elif method == 'step7_reverse':
            transformed = bytes((b - 7) % 256 for b in base_hash)
        elif method == 'step13_reverse':
            transformed = bytes((b - 13) % 256 for b in base_hash)
        elif method == 'step27_reverse':
            transformed = bytes((b - 27) % 256 for b in base_hash)

        # Double/Triple applications
        elif method == 'double_step27':
            temp = bytes((b + 27) % 256 for b in base_hash)
            transformed = bytes((b + 27) % 256 for b in temp)
        elif method == 'triple_step27':
            temp1 = bytes((b + 27) % 256 for b in base_hash)
            temp2 = bytes((b + 27) % 256 for b in temp1)
            transformed = bytes((b + 27) % 256 for b in temp2)

        # Hypothetical transformations
        elif method == 'col':
            transformed = bytes((b * 7) % 256 for b in base_hash)
        elif method == 'row':
            transformed = bytes((b * 13) % 256 for b in base_hash)
        elif method == 'diag':
            transformed = bytes((b * 27) % 256 for b in base_hash)
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

        except:
            return None, None

    def search(self):
        """Targeted search"""
        print("="*80)
        print("STARTING TARGETED SEARCH")
        print("="*80)
        print()

        print(f"Target: {self.target['address']}")
        print(f"Testing {len(self.priority_seeds)} priority seeds")
        print(f"Methods: {len(self.methods)}")
        print(f"XOR variants: {len(self.xor_variants)}")
        print(f"Total combinations: {len(self.priority_seeds) * len(self.methods) * len(self.xor_variants):,}")
        print()

        start_time = datetime.now()

        for seed_idx, seed in enumerate(self.priority_seeds):
            print(f"\nTesting seed {seed_idx + 1}/{len(self.priority_seeds)}: {seed[:30]}...")

            for method in self.methods:
                for xor_variant in self.xor_variants:
                    self.total_tests += 1

                    private_key = self.apply_transformation(seed, method, xor_variant)
                    address, hash160 = self.derive_address(private_key)

                    if not address:
                        continue

                    # Check match
                    if address == self.target['address']:
                        print()
                        print("="*80)
                        print("*** FOUND 1CFB! ***")
                        print("="*80)
                        print()
                        print(f"Address:      {address}")
                        print(f"Hash160:      {hash160}")
                        print(f"Seed:         {seed}")
                        print(f"Method:       {method}")
                        print(f"XOR Variant:  {xor_variant}")
                        print(f"Private Key:  {private_key.hex()}")
                        print()

                        result = {
                            'found': True,
                            'address': address,
                            'hash160': hash160,
                            'seed': seed,
                            'method': method,
                            'xor_variant': xor_variant,
                            'private_key_hex': private_key.hex(),
                            'tests': self.total_tests,
                            'time': str(datetime.now() - start_time)
                        }

                        with open('1CFB_TARGETED_FOUND.json', 'w') as f:
                            json.dump(result, f, indent=2)

                        return result

                    # Also track close matches
                    if address.startswith('1CFB'):
                        print(f"  Close: {address} (method={method}, xor={xor_variant})")

        elapsed = datetime.now() - start_time
        print()
        print("="*80)
        print("TARGETED SEARCH COMPLETE")
        print("="*80)
        print()
        print(f"Tests performed: {self.total_tests:,}")
        print(f"Time elapsed: {elapsed}")
        print()
        print("1CFB not found in priority seeds.")
        print("Consider running exhaustive search next.")
        print()

        result = {
            'found': False,
            'tests': self.total_tests,
            'time': str(elapsed)
        }

        with open('1CFB_TARGETED_RESULTS.json', 'w') as f:
            json.dump(result, f, indent=2)

        return result

def main():
    print("="*80)
    print("TARGETED 1CFB SEARCH")
    print("="*80)
    print()
    print("Fast search focusing on most promising seeds")
    print("Estimated time: 5-15 minutes")
    print()

    searcher = TargetedSearcher()
    searcher.load_priority_seeds()

    print("Starting in 3 seconds...")
    import time
    time.sleep(3)

    result = searcher.search()

    if result and result.get('found'):
        print("SUCCESS!")
    else:
        print("Not found in targeted search. Run exhaustive search for complete coverage.")

if __name__ == "__main__":
    main()
