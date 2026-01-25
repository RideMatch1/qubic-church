#!/usr/bin/env python3
"""
PATTERN ANALYSIS: QUBIC SEEDS → BITCOIN ADDRESSES
==================================================

Analysiert die Beziehung zwischen Qubic Seeds und generierten Bitcoin Adressen.
Versucht Muster zu finden, die erklären wie die 772 "1CF" Keys entstanden sind.

Ziel: Die Methode für 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg rekonstruieren!
"""

import json
import hashlib
from collections import defaultdict, Counter
import re

class PatternAnalyzer:
    """Analysiert Patterns zwischen Seeds und Adressen"""

    def __init__(self):
        self.all_keys = []
        self.original_772_keys = []
        self.cf_addresses = []
        self.patterns = {}

    def load_data(self):
        """Lade beide Datensätze"""
        print("="*80)
        print("LOADING DATA")
        print("="*80)

        # Neue 23,765 Keys
        print("\n1. Loading 23,765 new keys...")
        with open('ALL_BITCOIN_KEYS_FROM_SEEDS.json', 'r') as f:
            data = json.load(f)
            self.all_keys = data['records']
        print(f"   Loaded: {len(self.all_keys)} keys")

        # Ursprüngliche 772 Keys
        print("\n2. Loading original 772 keys...")
        with open('../public/data/bitcoin-private-keys.json', 'r') as f:
            data = json.load(f)
            self.original_772_keys = data['records']
        print(f"   Loaded: {len(self.original_772_keys)} keys")

        # Filtere "1CF" Adressen aus neuen Keys
        self.cf_addresses = [k for k in self.all_keys if k['address'].startswith('1CF')]
        print(f"\n3. Found {len(self.cf_addresses)} addresses starting with '1CF' in new keys")

        print()

    def analyze_seed_patterns(self):
        """Analysiere Patterns in den Seeds selbst"""
        print("="*80)
        print("SEED PATTERN ANALYSIS")
        print("="*80)
        print()

        patterns = {
            'length_distribution': Counter(),
            'hex_char_frequency': Counter(),
            'starts_with': Counter(),
            'ends_with': Counter(),
            'repeating_patterns': []
        }

        for key in self.all_keys[:1000]:  # Sample first 1000
            seed = key['seed']

            patterns['length_distribution'][len(seed)] += 1

            # Character frequency
            for char in seed.lower():
                if char in '0123456789abcdef':
                    patterns['hex_char_frequency'][char] += 1

            # Start/End patterns
            if len(seed) >= 4:
                patterns['starts_with'][seed[:4]] += 1
                patterns['ends_with'][seed[-4:]] += 1

            # Repeating bytes
            if len(seed) >= 8:
                for i in range(len(seed) - 8):
                    chunk = seed[i:i+8]
                    if seed.count(chunk) > 1:
                        patterns['repeating_patterns'].append(chunk)

        print("Seed Length Distribution:")
        for length, count in sorted(patterns['length_distribution'].items()):
            print(f"  {length} chars: {count} seeds")

        print("\nMost common starting patterns:")
        for pattern, count in patterns['starts_with'].most_common(10):
            print(f"  {pattern}: {count} times")

        print("\nMost common hex characters:")
        for char, count in patterns['hex_char_frequency'].most_common(16):
            print(f"  '{char}': {count} times")

        print()
        self.patterns['seeds'] = patterns

    def analyze_address_prefixes(self):
        """Analysiere Address-Präfixe"""
        print("="*80)
        print("ADDRESS PREFIX ANALYSIS")
        print("="*80)
        print()

        # Prefix-Verteilung in ALLEN neuen Keys
        prefix_counter = Counter()
        for key in self.all_keys:
            prefix_counter[key['address'][:3]] += 1

        print("Top 20 most common address prefixes (from 23,765 keys):")
        for prefix, count in prefix_counter.most_common(20):
            percentage = (count / len(self.all_keys)) * 100
            print(f"  {prefix}: {count:4d} ({percentage:.2f}%)")

        # Spezifische "1CF" Analyse
        print("\n\n'1CF' Prefix Analysis:")
        print(f"  Total addresses with '1CF': {len(self.cf_addresses)}")
        print(f"  Percentage: {(len(self.cf_addresses) / len(self.all_keys)) * 100:.3f}%")
        print(f"  Expected (random): ~0.0028% (1 in ~35,000)")
        print(f"  Observed: {(len(self.cf_addresses) / len(self.all_keys)) * 100:.3f}%")

        enrichment = (len(self.cf_addresses) / len(self.all_keys)) / 0.000028
        print(f"  Enrichment factor: {enrichment:.1f}x")

        # Original 772 Keys Analyse
        print("\n\nOriginal 772 Keys Analysis:")
        original_prefix_counter = Counter()
        for key in self.original_772_keys:
            original_prefix_counter[key['address'][:3]] += 1

        print("Top prefixes in original 772 keys:")
        for prefix, count in original_prefix_counter.most_common(10):
            percentage = (count / len(self.original_772_keys)) * 100
            print(f"  {prefix}: {count:4d} ({percentage:.2f}%)")

        print()
        self.patterns['prefixes'] = {
            'all_keys': prefix_counter,
            'original': original_prefix_counter
        }

    def compare_generation_methods(self):
        """Vergleiche die Generierungs-Methoden"""
        print("="*80)
        print("GENERATION METHOD COMPARISON")
        print("="*80)
        print()

        # Analysiere die "method" Felder in original 772
        if self.original_772_keys and 'method' in self.original_772_keys[0]:
            method_counter = Counter()
            for key in self.original_772_keys:
                method_counter[key.get('method', 'unknown')] += 1

            print("Methods used in original 772 keys:")
            for method, count in method_counter.most_common():
                percentage = (count / len(self.original_772_keys)) * 100
                print(f"  {method}: {count} ({percentage:.1f}%)")
            print()

        # Analysiere XOR Varianten
        if 'xorVariant' in self.original_772_keys[0]:
            xor_counter = Counter()
            for key in self.original_772_keys:
                xor_counter[key.get('xorVariant', 'none')] += 1

            print("XOR variants in original 772 keys:")
            for variant, count in sorted(xor_counter.items()):
                percentage = (count / len(self.original_772_keys)) * 100
                print(f"  XOR {variant}: {count} ({percentage:.1f}%)")
            print()

        # Analysiere Positionen
        if 'position' in self.original_772_keys[0]:
            print("Sample positions from original 772 keys:")
            for i, key in enumerate(self.original_772_keys[:10]):
                pos = key.get('position', 'unknown')
                method = key.get('method', 'unknown')
                print(f"  {i+1}. Position {pos}, Method: {method}, Address: {key['address']}")
            print()

    def find_1cf_seed_patterns(self):
        """Finde Patterns in Seeds die zu '1CF' Adressen führen"""
        print("="*80)
        print("ANALYZING SEEDS THAT PRODUCE '1CF' ADDRESSES")
        print("="*80)
        print()

        if not self.cf_addresses:
            print("No '1CF' addresses found in new keys!")
            return

        print(f"Analyzing {len(self.cf_addresses)} seeds that produced '1CF' addresses:\n")

        for i, key in enumerate(self.cf_addresses, 1):
            seed = key['seed']
            address = key['address']
            private_key_hex = key['privateKeyHex']

            print(f"{i}. Address: {address}")
            print(f"   Seed:        {seed[:40]}... (len: {len(seed)})")
            print(f"   Private Key: {private_key_hex[:40]}...")

            # Analysiere den Seed
            seed_hash = hashlib.sha256(seed.encode()).hexdigest()
            print(f"   SHA256(seed): {seed_hash[:40]}...")

            # Byte-Summe
            seed_bytes = bytes.fromhex(private_key_hex)
            byte_sum = sum(seed_bytes)
            print(f"   Byte Sum: {byte_sum}")
            print(f"   mod 121: {byte_sum % 121}")
            print(f"   mod 19:  {byte_sum % 19}")
            print(f"   mod 27:  {byte_sum % 27}")
            print()

    def search_for_1cfb_method(self):
        """Versuche die Methode für 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg zu finden"""
        print("="*80)
        print("SEARCHING FOR 1CFB GENERATION METHOD")
        print("="*80)
        print()

        target_address = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"
        target_hash160 = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"

        print(f"Target Address: {target_address}")
        print(f"Target Hash160: {target_hash160}")
        print()

        # Methode 1: Direct match in original 772?
        print("1. Checking if target is in original 772 keys...")
        found_in_original = False
        for key in self.original_772_keys:
            if key['address'] == target_address:
                print(f"   FOUND IN ORIGINAL 772!")
                print(f"   Position: {key.get('position', 'unknown')}")
                print(f"   Method: {key.get('method', 'unknown')}")
                print(f"   XOR Variant: {key.get('xorVariant', 'unknown')}")
                print(f"   Private Key: {key['privateKeyHex']}")
                found_in_original = True
                break

        if not found_in_original:
            print("   NOT FOUND in original 772 keys")
        print()

        # Methode 2: Analysiere die Hash160 Eigenschaften
        print("2. Analyzing target Hash160 properties...")
        target_bytes = bytes.fromhex(target_hash160)
        byte_sum = sum(target_bytes)

        print(f"   Byte Sum: {byte_sum}")
        print(f"   mod 121: {byte_sum % 121}")
        print(f"   mod 19:  {byte_sum % 19}")
        print(f"   mod 27:  {byte_sum % 27}")
        print(f"   mod 256: {byte_sum % 256}")
        print()

        # Methode 3: Suche ähnliche Hash160 Patterns
        print("3. Searching for similar Hash160 patterns in original 772...")
        similar_count = 0
        for key in self.original_772_keys:
            if 'hash160' in key:
                key_bytes = bytes.fromhex(key['hash160'])
                key_sum = sum(key_bytes)

                # Gleiche modulo properties?
                if (key_sum % 121 == byte_sum % 121 and
                    key_sum % 19 == byte_sum % 19):
                    similar_count += 1
                    if similar_count <= 5:
                        print(f"   Similar: {key['address']}")
                        print(f"     Sum: {key_sum}, mod 121: {key_sum % 121}, mod 19: {key_sum % 19}")

        print(f"   Found {similar_count} addresses with similar modulo patterns")
        print()

        # Methode 4: Reverse-Engineering Ansatz
        print("4. Reverse-Engineering Approach...")
        print("   Testing if we can derive a seed from the Hash160...")

        # Verschiedene Ableitungs-Versuche
        attempts = [
            ("Direct Hash160", target_hash160),
            ("Reversed Hash160", target_hash160[::-1]),
            ("XOR with 121", bytes((b ^ 121) for b in target_bytes).hex()),
            ("XOR with 19", bytes((b ^ 19) for b in target_bytes).hex()),
            ("Add 27", bytes((b + 27) % 256 for b in target_bytes).hex()),
        ]

        for method, derived_seed in attempts:
            # Versuche diesen als Seed zu verwenden
            try:
                test_private_key = hashlib.sha256(derived_seed.encode()).digest()
                # Hier könnte man weitermachen mit ECDSA...
                print(f"   {method}: {derived_seed[:40]}...")
            except:
                pass

        print()

    def export_analysis(self):
        """Exportiere alle Analysen"""
        print("="*80)
        print("EXPORTING ANALYSIS")
        print("="*80)
        print()

        output = {
            'analysis_date': '2026-01-09',
            'datasets': {
                'new_keys': len(self.all_keys),
                'original_keys': len(self.original_772_keys),
                'cf_addresses_in_new': len(self.cf_addresses)
            },
            'patterns': self.patterns,
            'cf_addresses': [
                {
                    'address': k['address'],
                    'seed': k['seed'],
                    'privateKeyHex': k['privateKeyHex']
                }
                for k in self.cf_addresses
            ]
        }

        with open('PATTERN_ANALYSIS_RESULTS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("Exported to: PATTERN_ANALYSIS_RESULTS.json")
        print()

def main():
    """Main execution"""
    print("="*80)
    print("PATTERN ANALYSIS: SEEDS → ADDRESSES")
    print("="*80)
    print()

    analyzer = PatternAnalyzer()

    # Load data
    analyzer.load_data()

    # Run analyses
    analyzer.analyze_seed_patterns()
    analyzer.analyze_address_prefixes()
    analyzer.compare_generation_methods()
    analyzer.find_1cf_seed_patterns()
    analyzer.search_for_1cfb_method()

    # Export
    analyzer.export_analysis()

    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print()
    print("Key Findings:")
    print("1. Check PATTERN_ANALYSIS_RESULTS.json for detailed data")
    print("2. Compare '1CF' generation methods")
    print("3. Look for patterns that could lead to 1CFB address")
    print()

if __name__ == "__main__":
    main()
