#!/usr/bin/env python3
"""
MULTI-ADDRESS CROSS-VALIDATION
===============================

Geniale Strategie: Analysiere ALLE bekannten CFB/Maria Adressen!

Bekannte Adressen:
1. 1CFB... - CFB main address
2. 15ubic... - Qubic donation address (WICHTIG!)
3. 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa - Genesis Block
4. Andere 1CF... Adressen aus den 772 keys
5. Maria's Adressen (wenn bekannt)

Ziel:
- Cross-validation zwischen mehreren Adressen
- Gemeinsame Patterns finden
- Systematik BEWEISEN statt raten
- Datenbank aufbauen für weitere Analysen

"Wie Gott denken" - außerhalb der Box!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from collections import Counter, defaultdict

class MultiAddressAnalyzer:
    """Analyze multiple CFB addresses to find common patterns"""

    def __init__(self):
        # ALLE bekannten CFB/Qubic Adressen
        self.known_addresses = {
            '1CFB_main': {
                'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
                'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d',
                'owner': 'CFB',
                'purpose': 'Main address',
                'known': False
            },
            '15ubic_donation': {
                'address': '15ubicKDqW9q3Y4K2Uaq59jtNNYLy8JWkz',
                'hash160': None,  # Calculate
                'owner': 'Qubic/CFB',
                'purpose': 'Donation address',
                'known': False
            },
            'genesis': {
                'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'hash160': '62e907b15cbf27d5425399ebf6f0fb50ebb88f18',
                'owner': 'Satoshi/CFB?',
                'purpose': 'Genesis Block',
                'known': False
            },
            '1CFi_special': {
                'address': '1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi',
                'hash160': '7b71d7d43a0fb43b1832f63cc4913b30e6522791',
                'owner': 'CFB',
                'purpose': 'Special pattern (known)',
                'known': True,
                'seed': 'mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn',
                'method': 'step27',
                'xor': 13,
                'position': [91, 20]
            }
        }

        self.seeds = []
        self.original_772 = []
        self.found_matches = {}

    def calculate_hash160_from_address(self, address):
        """Calculate hash160 from Bitcoin address"""
        try:
            decoded = base58.b58decode(address)
            # Remove version byte (first) and checksum (last 4)
            hash160 = decoded[1:-4]
            return hash160.hex()
        except:
            return None

    def load_data(self):
        """Load all data"""
        print("="*80)
        print("LOADING DATA")
        print("="*80)
        print()

        # Calculate missing hash160s
        for name, data in self.known_addresses.items():
            if data['hash160'] is None:
                hash160 = self.calculate_hash160_from_address(data['address'])
                if hash160:
                    data['hash160'] = hash160
                    print(f"Calculated hash160 for {name}: {hash160}")

        # Load seeds
        try:
            with open('../public/data/qubic-seeds.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.seeds = data
                elif isinstance(data, dict) and 'records' in data:
                    self.seeds = [r.get('seed', r.get('value', '')) for r in data['records']]
            print(f"Loaded {len(self.seeds)} seeds from Anna Matrix")
        except Exception as e:
            print(f"Error loading seeds: {e}")

        # Load original 772
        try:
            with open('../public/data/bitcoin-private-keys.json', 'r') as f:
                data = json.load(f)
                self.original_772 = data['records']
            print(f"Loaded {len(self.original_772)} original keys")
        except Exception as e:
            print(f"Error loading original keys: {e}")

        print()

    def analyze_all_addresses_properties(self):
        """Analyze mathematical properties of all addresses"""
        print("="*80)
        print("MATHEMATICAL PROPERTIES - ALL ADDRESSES")
        print("="*80)
        print()

        for name, data in self.known_addresses.items():
            print(f"{name}: {data['address']}")
            print(f"  Owner:   {data['owner']}")
            print(f"  Purpose: {data['purpose']}")

            if data['hash160']:
                hash160_bytes = bytes.fromhex(data['hash160'])
                byte_sum = sum(hash160_bytes)

                print(f"  Hash160: {data['hash160']}")
                print(f"  Byte Sum: {byte_sum}")
                print(f"  mod 121: {byte_sum % 121}")
                print(f"  mod 19:  {byte_sum % 19}")
                print(f"  mod 27:  {byte_sum % 27}")
                print(f"  mod 11:  {byte_sum % 11}")
                print(f"  mod 13:  {byte_sum % 13}")
                print(f"  mod 33:  {byte_sum % 33}")

                # Check if it's 121 × 19
                if byte_sum % 121 == 0 and byte_sum % 19 == 0:
                    print(f"  *** HAS mod 121=0 AND mod 19=0! ***")
                    print(f"  *** Byte sum = {byte_sum} = 121 × {byte_sum // 121} = 19 × {byte_sum // 19} ***")

                # Check other special patterns
                if byte_sum == 2299:
                    print(f"  *** SAME SUM AS 1CFB! (2299 = 121 × 19) ***")

            print()

    def search_15ubic_in_anna_matrix(self):
        """Intensive search for 15ubic donation address"""
        print("="*80)
        print("SEARCHING FOR 15ubic DONATION ADDRESS")
        print("="*80)
        print()

        target = self.known_addresses['15ubic_donation']
        print(f"Target: {target['address']}")
        print(f"This is the QUBIC DONATION ADDRESS!")
        print()

        # Extended methods
        methods = [
            'step7', 'step13', 'step27', 'step33',
            'double_step27', 'triple_step27',
            'step27_reverse', 'step13_reverse',
            'mult27', 'mult13', 'mult19'
        ]

        xor_variants = [0, 7, 11, 13, 19, 27, 33, 121]

        print(f"Testing {len(methods)} methods × {len(xor_variants)} XOR variants")
        print(f"on ALL {len(self.seeds)} seeds...")
        print()

        tested = 0
        for seed_idx, seed in enumerate(self.seeds):
            if seed_idx % 1000 == 0:
                print(f"Progress: {seed_idx}/{len(self.seeds)} seeds ({seed_idx/len(self.seeds)*100:.1f}%)")

            for method in methods:
                for xor_var in xor_variants:
                    tested += 1

                    private_key = self.apply_transformation(seed, method, xor_var)
                    address, hash160 = self.derive_address(private_key)

                    if not address:
                        continue

                    # Check match
                    if address == target['address']:
                        print()
                        print("="*80)
                        print("*** FOUND 15ubic DONATION ADDRESS! ***")
                        print("="*80)
                        print()
                        print(f"Address:      {address}")
                        print(f"Seed:         {seed}")
                        print(f"Seed Index:   {seed_idx}")
                        print(f"Position:     [{seed_idx // 128}, {seed_idx % 128}]")
                        print(f"Method:       {method}")
                        print(f"XOR Variant:  {xor_var}")
                        print(f"Private Key:  {private_key.hex()}")
                        print()

                        self.found_matches['15ubic'] = {
                            'found': True,
                            'address': address,
                            'seed': seed,
                            'position': [seed_idx // 128, seed_idx % 128],
                            'method': method,
                            'xor': xor_var,
                            'private_key': private_key.hex()
                        }

                        return True

        print()
        print(f"15ubic tested: {tested} combinations")
        print("Not found in Anna Matrix seeds")
        print()

        return False

    def search_all_1cf_addresses(self):
        """Search for ALL addresses starting with 1CF"""
        print("="*80)
        print("FINDING ALL 1CF ADDRESSES IN ORIGINAL 772")
        print("="*80)
        print()

        cf_addresses = []

        for key in self.original_772:
            if key['address'].startswith('1CF'):
                cf_addresses.append(key)

        print(f"Found {len(cf_addresses)} addresses starting with '1CF'")
        print()

        # Analyze their properties
        special_properties = []

        for addr in cf_addresses:
            if 'hash160' in addr:
                hash160_bytes = bytes.fromhex(addr['hash160'])
                byte_sum = sum(hash160_bytes)

                if byte_sum % 121 == 0 and byte_sum % 19 == 0:
                    special_properties.append({
                        'address': addr['address'],
                        'sum': byte_sum,
                        'position': addr.get('position'),
                        'method': addr.get('method'),
                        'xor': addr.get('xorVariant'),
                        'seed': addr.get('seed')
                    })

        print(f"Addresses with mod 121=0 AND mod 19=0: {len(special_properties)}")
        print()

        for i, addr in enumerate(special_properties, 1):
            print(f"{i}. {addr['address']}")
            print(f"   Sum: {addr['sum']}, Position: {addr['position']}")
            print(f"   Method: {addr['method']}, XOR: {addr['xor']}")
            print()

        return cf_addresses, special_properties

    def deep_anna_matrix_analysis(self):
        """TIEFER in die Anna Matrix schauen"""
        print("="*80)
        print("DEEP ANNA MATRIX ANALYSIS")
        print("="*80)
        print()

        print("Searching for hidden patterns in Anna Matrix...")
        print()

        # Frage: Gibt es mehr als 23,765 seeds?
        print(f"Current seed count: {len(self.seeds)}")
        print()

        # Analysiere seed properties
        print("Seed Length Distribution:")
        length_counter = Counter()
        for seed in self.seeds[:1000]:
            length_counter[len(seed)] += 1

        for length, count in sorted(length_counter.items()):
            print(f"  Length {length}: {count} seeds")

        print()

        # Suche nach special seed patterns
        print("Looking for special seed patterns:")

        # Pattern 1: Seeds mit sum = 2299
        print("\n1. Seeds where character sum = 2299:")
        count_2299 = 0
        for seed in self.seeds:
            if len(seed) >= 14:
                pattern = seed[:55]  # Full seed
                char_sum = sum(ord(c) - ord('a') for c in pattern if c.isalpha())
                if char_sum == 2299:
                    count_2299 += 1
                    if count_2299 <= 5:
                        print(f"  {seed[:40]}... (sum={char_sum})")

        print(f"  Total found: {count_2299}")

        # Pattern 2: Perfect palindromes
        print("\n2. Perfect palindrome seeds:")
        count_palindrome = 0
        for seed in self.seeds[:1000]:
            if seed == seed[::-1]:
                count_palindrome += 1
                print(f"  {seed[:40]}...")

        print(f"  Total found: {count_palindrome}")

        # Pattern 3: All same character
        print("\n3. Homogeneous seeds (same character repeated):")
        count_homo = 0
        for seed in self.seeds[:1000]:
            if len(set(seed)) == 1:
                count_homo += 1
                print(f"  {seed[:40]}... (char: '{seed[0]}')")

        print(f"  Total found: {count_homo}")

        print()

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
        elif method == 'double_step27':
            temp = bytes((b + 27) % 256 for b in base_hash)
            transformed = bytes((b + 27) % 256 for b in temp)
        elif method == 'triple_step27':
            temp1 = bytes((b + 27) % 256 for b in base_hash)
            temp2 = bytes((b + 27) % 256 for b in temp1)
            transformed = bytes((b + 27) % 256 for b in temp2)
        elif method == 'step27_reverse':
            transformed = bytes((b - 27) % 256 for b in base_hash)
        elif method == 'step13_reverse':
            transformed = bytes((b - 13) % 256 for b in base_hash)
        elif method == 'mult27':
            transformed = bytes((b * 27) % 256 for b in base_hash)
        elif method == 'mult13':
            transformed = bytes((b * 13) % 256 for b in base_hash)
        elif method == 'mult19':
            transformed = bytes((b * 19) % 256 for b in base_hash)
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

    def cross_validate_findings(self):
        """Cross-validate between found addresses"""
        print("="*80)
        print("CROSS-VALIDATION")
        print("="*80)
        print()

        if not self.found_matches:
            print("No matches found yet for cross-validation")
            return

        print("Found matches:")
        for name, match in self.found_matches.items():
            print(f"\n{name}:")
            print(f"  Address:  {match['address']}")
            print(f"  Position: {match['position']}")
            print(f"  Method:   {match['method']}")
            print(f"  XOR:      {match['xor']}")

        # Look for common patterns
        if len(self.found_matches) >= 2:
            print("\nLooking for common patterns:")

            methods = [m['method'] for m in self.found_matches.values()]
            xors = [m['xor'] for m in self.found_matches.values()]

            print(f"  Methods: {methods}")
            print(f"  XORs: {xors}")

            if len(set(methods)) == 1:
                print(f"  *** ALL use same method: {methods[0]} ***")

            if len(set(xors)) == 1:
                print(f"  *** ALL use same XOR: {xors[0]} ***")

    def save_results(self):
        """Save all results"""
        output = {
            'date': '2026-01-09',
            'known_addresses': self.known_addresses,
            'found_matches': self.found_matches,
            'analysis_complete': True
        }

        with open('MULTI_ADDRESS_ANALYSIS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("\nResults saved to: MULTI_ADDRESS_ANALYSIS.json")

def main():
    print("="*80)
    print("MULTI-ADDRESS CROSS-VALIDATION")
    print("="*80)
    print()
    print("Strategy: Analyze ALL known CFB addresses!")
    print("Goal: Find common patterns through cross-validation")
    print()

    analyzer = MultiAddressAnalyzer()
    analyzer.load_data()

    # Analyze properties
    analyzer.analyze_all_addresses_properties()

    # Deep matrix analysis
    analyzer.deep_anna_matrix_analysis()

    # Find all 1CF addresses
    analyzer.search_all_1cf_addresses()

    # Search for 15ubic (IMPORTANT!)
    print("Starting intensive search for 15ubic...")
    print("This may take 30-60 minutes...")
    print()

    analyzer.search_15ubic_in_anna_matrix()

    # Cross-validate
    analyzer.cross_validate_findings()

    # Save
    analyzer.save_results()

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
