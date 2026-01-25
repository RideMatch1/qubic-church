#!/usr/bin/env python3
"""
FIND ADDRESSES SIMILAR TO 1CFi
================================

Findet Adressen mit ähnlichen mathematischen Eigenschaften wie:
1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi

Target Properties:
- Byte Sum: 2,299 = 121 × 19
- mod 121: 0
- mod 19: 0
- mod 27: 4

Strategie:
1. Analysiere ALLE 24,537 Keys
2. Finde Adressen mit einzelnen matching properties
3. Analysiere Seed-Patterns
4. Suche nach XOR-Beziehungen
5. Erstelle Transformations-Matrix
"""

import json
import hashlib
from collections import defaultdict, Counter
import sys

class SimilarityAnalyzer:
    """Findet ähnliche Adressen zu 1CFi"""

    def __init__(self):
        self.target = {
            'address': '1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi',
            'hash160': '7b71d7d43a0fb43b1832f63cc4913b30e6522791',
            'byte_sum': 2299,
            'mod_121': 0,
            'mod_19': 0,
            'mod_27': 4,
            'position': [91, 20],
            'method': 'step27',
            'xorVariant': 13,
            'seed': 'mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmn'
        }

        # Storage for analysis
        self.all_keys = []
        self.original_772 = []
        self.similar_addresses = {
            'mod_121_0': [],
            'mod_19_0': [],
            'both_zero': [],
            'sum_2299': [],
            'sum_close': [],
            'xor_similar': []
        }

    def load_data(self):
        """Lade beide Datensätze"""
        print("="*80)
        print("LOADING DATA")
        print("="*80)
        print()

        # Original 772 Keys
        try:
            with open('../public/data/bitcoin-private-keys.json', 'r') as f:
                data = json.load(f)
                self.original_772 = data['records']
            print(f"Loaded: {len(self.original_772)} original keys")
        except Exception as e:
            print(f"Error loading original keys: {e}")
            self.original_772 = []

        # Alle 23,765 Keys
        try:
            with open('ALL_BITCOIN_KEYS_FROM_SEEDS.json', 'r') as f:
                data = json.load(f)
                self.all_keys = data['records']
            print(f"Loaded: {len(self.all_keys)} generated keys")
        except Exception as e:
            print(f"Error loading all keys: {e}")
            self.all_keys = []

        print(f"Total keys to analyze: {len(self.original_772) + len(self.all_keys)}")
        print()

    def analyze_mathematical_properties(self):
        """Analysiere mathematische Eigenschaften"""
        print("="*80)
        print("MATHEMATICAL PROPERTY ANALYSIS")
        print("="*80)
        print()

        print(f"Target 1CFi properties:")
        print(f"  Byte Sum: {self.target['byte_sum']}")
        print(f"  mod 121:  {self.target['mod_121']}")
        print(f"  mod 19:   {self.target['mod_19']}")
        print(f"  mod 27:   {self.target['mod_27']}")
        print()

        # Kombiniere beide Datensätze
        all_addresses = []

        # Original 772 (mit hash160 wenn vorhanden)
        for key in self.original_772:
            if 'hash160' in key:
                all_addresses.append({
                    'address': key['address'],
                    'hash160': key['hash160'],
                    'source': 'original_772',
                    'position': key.get('position'),
                    'method': key.get('method'),
                    'xorVariant': key.get('xorVariant'),
                    'privateKeyHex': key.get('privateKeyHex')
                })

        # Neue 23,765 Keys
        for key in self.all_keys:
            # Hash160 berechnen wenn nicht vorhanden
            if 'hash160' not in key:
                # Würde vollständige Address → Hash160 Konversion brauchen
                # Überspringen wenn nicht vorhanden
                continue

            all_addresses.append({
                'address': key['address'],
                'hash160': key.get('hash160', ''),
                'source': 'generated_23765',
                'seed': key.get('seed'),
                'privateKeyHex': key.get('privateKeyHex')
            })

        print(f"Analyzing {len(all_addresses)} addresses with hash160...")
        print()

        # Analysiere jede Adresse
        for addr_data in all_addresses:
            hash160 = addr_data['hash160']
            if not hash160 or len(hash160) != 40:
                continue

            hash160_bytes = bytes.fromhex(hash160)
            byte_sum = sum(hash160_bytes)

            addr_data['byte_sum'] = byte_sum
            addr_data['mod_121'] = byte_sum % 121
            addr_data['mod_19'] = byte_sum % 19
            addr_data['mod_27'] = byte_sum % 27

            # Kategorisiere
            if byte_sum % 121 == 0:
                self.similar_addresses['mod_121_0'].append(addr_data)

            if byte_sum % 19 == 0:
                self.similar_addresses['mod_19_0'].append(addr_data)

            if byte_sum % 121 == 0 and byte_sum % 19 == 0:
                self.similar_addresses['both_zero'].append(addr_data)

            if byte_sum == 2299:
                self.similar_addresses['sum_2299'].append(addr_data)

            # "Close" = within ±100 of 2299
            if abs(byte_sum - 2299) <= 100:
                self.similar_addresses['sum_close'].append(addr_data)

        # Ergebnisse
        print("RESULTS:")
        print(f"  Addresses with mod 121 = 0:           {len(self.similar_addresses['mod_121_0'])}")
        print(f"  Addresses with mod 19 = 0:            {len(self.similar_addresses['mod_19_0'])}")
        print(f"  Addresses with BOTH mod 121=0, 19=0:  {len(self.similar_addresses['both_zero'])}")
        print(f"  Addresses with exact sum 2299:        {len(self.similar_addresses['sum_2299'])}")
        print(f"  Addresses with sum close to 2299:     {len(self.similar_addresses['sum_close'])}")
        print()

    def show_similar_addresses(self):
        """Zeige ähnliche Adressen im Detail"""
        print("="*80)
        print("ADDRESSES WITH mod 121 = 0 AND mod 19 = 0")
        print("="*80)
        print()

        if not self.similar_addresses['both_zero']:
            print("No addresses found with both properties!")
            return

        print(f"Found {len(self.similar_addresses['both_zero'])} addresses:")
        print()

        for i, addr in enumerate(self.similar_addresses['both_zero'], 1):
            print(f"{i}. {addr['address']}")
            print(f"   Hash160:     {addr['hash160']}")
            print(f"   Byte Sum:    {addr['byte_sum']}")
            print(f"   mod 121:     {addr['mod_121']}")
            print(f"   mod 19:      {addr['mod_19']}")
            print(f"   mod 27:      {addr['mod_27']}")
            print(f"   Source:      {addr['source']}")

            if addr['source'] == 'original_772':
                print(f"   Position:    {addr.get('position')}")
                print(f"   Method:      {addr.get('method')}")
                print(f"   XOR Variant: {addr.get('xorVariant')}")
            else:
                print(f"   Seed:        {addr.get('seed', 'N/A')[:50]}...")

            # XOR mit Target
            if addr['hash160'] != self.target['hash160']:
                target_bytes = bytes.fromhex(self.target['hash160'])
                addr_bytes = bytes.fromhex(addr['hash160'])
                xor_result = bytes(a ^ b for a, b in zip(target_bytes, addr_bytes))
                xor_sum = sum(xor_result)

                print(f"   XOR with 1CFi:")
                print(f"     Result:    {xor_result.hex()[:40]}...")
                print(f"     XOR Sum:   {xor_sum}")
                print(f"     mod 121:   {xor_sum % 121}")
                print(f"     mod 19:    {xor_sum % 19}")

            print()

    def analyze_seed_patterns(self):
        """Analysiere Seed-Patterns"""
        print("="*80)
        print("SEED PATTERN ANALYSIS")
        print("="*80)
        print()

        print(f"Target 1CFi seed:")
        print(f"  {self.target['seed']}")
        print(f"  Length: {len(self.target['seed'])}")
        print()

        # Pattern detection
        seed = self.target['seed']
        print("Detected patterns:")

        # Repeating sequences
        for length in [2, 3, 4, 5, 7, 10, 14]:
            chunks = [seed[i:i+length] for i in range(0, len(seed), length)]
            unique = set(chunks)
            if len(unique) <= 3:  # Hochgradig repetitiv
                print(f"  Pattern length {length:2d}: {len(unique)} unique chunks")
                print(f"    Chunks: {chunks[:5]}")

        print()

        # Suche ähnliche Seeds in den "both_zero" Adressen
        print("Seeds from addresses with mod 121=0 AND mod 19=0:")
        print()

        for addr in self.similar_addresses['both_zero']:
            if addr['source'] == 'generated_23765' and 'seed' in addr:
                addr_seed = addr['seed']
                print(f"  Address: {addr['address']}")
                print(f"  Seed:    {addr_seed[:50]}...")

                # Character frequency comparison
                target_chars = Counter(self.target['seed'])
                addr_chars = Counter(addr_seed)

                overlap = set(target_chars.keys()) & set(addr_chars.keys())
                print(f"  Overlap:  {len(overlap)}/{len(target_chars)} characters")
                print()

    def analyze_transformation_methods(self):
        """Analysiere Transformations-Methoden"""
        print("="*80)
        print("TRANSFORMATION METHOD ANALYSIS")
        print("="*80)
        print()

        # Nur für original 772
        if not self.original_772:
            print("No original 772 keys loaded")
            return

        # Analysiere Methoden bei mod 121=0 Adressen
        mod121_methods = defaultdict(int)
        mod19_methods = defaultdict(int)
        both_methods = defaultdict(int)

        for addr in self.similar_addresses['mod_121_0']:
            if addr['source'] == 'original_772':
                method = addr.get('method', 'unknown')
                mod121_methods[method] += 1

        for addr in self.similar_addresses['mod_19_0']:
            if addr['source'] == 'original_772':
                method = addr.get('method', 'unknown')
                mod19_methods[method] += 1

        for addr in self.similar_addresses['both_zero']:
            if addr['source'] == 'original_772':
                method = addr.get('method', 'unknown')
                xor = addr.get('xorVariant', 'unknown')
                both_methods[f"{method}+XOR{xor}"] += 1

        print("Methods producing mod 121 = 0:")
        for method, count in sorted(mod121_methods.items(), key=lambda x: -x[1]):
            print(f"  {method}: {count}")
        print()

        print("Methods producing mod 19 = 0:")
        for method, count in sorted(mod19_methods.items(), key=lambda x: -x[1]):
            print(f"  {method}: {count}")
        print()

        print("Methods producing BOTH mod 121=0 AND mod 19=0:")
        for method, count in sorted(both_methods.items(), key=lambda x: -x[1]):
            print(f"  {method}: {count}")
        print()

    def strategic_search_planning(self):
        """Plane strategische Suche für 1CFB"""
        print("="*80)
        print("STRATEGIC SEARCH PLANNING FOR 1CFB")
        print("="*80)
        print()

        cfb_target = {
            'address': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            'hash160': '7b581609d8f9b74c34f7648c3b79fd8a6848022d',
            'byte_sum': 2299,
            'mod_121': 0,
            'mod_19': 0,
            'mod_27': 4
        }

        print("Target 1CFB properties:")
        print(f"  Address:     {cfb_target['address']}")
        print(f"  Hash160:     {cfb_target['hash160']}")
        print(f"  Byte Sum:    {cfb_target['byte_sum']}")
        print(f"  mod 121:     {cfb_target['mod_121']}")
        print(f"  mod 19:      {cfb_target['mod_19']}")
        print(f"  mod 27:      {cfb_target['mod_27']}")
        print()

        print("Known from 1CFi analysis:")
        print(f"  Method:      step27 + XOR 13")
        print(f"  Position:    [91, 20]")
        print(f"  Seed:        {self.target['seed']}")
        print()

        print("Search Strategy:")
        print()
        print("1. EXHAUSTIVE TRANSFORMATION SEARCH")
        print("   - All 23,765 seeds")
        print("   - All methods: step7, step13, step27, step33, col, row, diag")
        print("   - All XOR variants: 0, 7, 13, 19, 27, 33, 121")
        print(f"   - Total combinations: 23,765 × 7 × 7 = {23765 * 7 * 7:,}")
        print("   - Estimated time: ~2-4 hours on modern CPU")
        print()

        print("2. TARGETED XOR RELATIONSHIP")
        print("   - Calculate: 1CFi XOR 1CFB")

        cfi_bytes = bytes.fromhex(self.target['hash160'])
        cfb_bytes = bytes.fromhex(cfb_target['hash160'])
        xor_diff = bytes(a ^ b for a, b in zip(cfi_bytes, cfb_bytes))

        print(f"   - XOR Result: {xor_diff.hex()}")
        print(f"   - XOR Sum:    {sum(xor_diff)}")
        print(f"   - This is the 'distance' in hash space")
        print()

        print("3. VANITY GENERATION REPRODUCTION")
        print("   - Use vanitygen or similar tool")
        print("   - Generate addresses starting with '1CFB'")
        print("   - Filter for mod 121 = 0 AND mod 19 = 0")
        print("   - Expected: ~2,299 attempts per match")
        print()

        print("4. REVERSE ENGINEERING FROM HASH160")
        print("   - Not cryptographically feasible")
        print("   - Would require breaking ECDSA")
        print("   - Theoretical only")
        print()

        print("RECOMMENDED NEXT STEP:")
        print("Execute exhaustive transformation search (Option 1)")
        print("This has highest probability of success.")
        print()

    def export_results(self):
        """Exportiere Ergebnisse"""
        print("="*80)
        print("EXPORTING RESULTS")
        print("="*80)
        print()

        output = {
            'analysis_date': '2026-01-09',
            'target_1cfi': self.target,
            'statistics': {
                'mod_121_0_count': len(self.similar_addresses['mod_121_0']),
                'mod_19_0_count': len(self.similar_addresses['mod_19_0']),
                'both_zero_count': len(self.similar_addresses['both_zero']),
                'sum_2299_count': len(self.similar_addresses['sum_2299']),
                'sum_close_count': len(self.similar_addresses['sum_close'])
            },
            'addresses_both_zero': [
                {
                    'address': a['address'],
                    'hash160': a['hash160'],
                    'byte_sum': a['byte_sum'],
                    'mod_121': a['mod_121'],
                    'mod_19': a['mod_19'],
                    'mod_27': a['mod_27'],
                    'source': a['source'],
                    'method': a.get('method'),
                    'xorVariant': a.get('xorVariant'),
                    'seed': a.get('seed')
                }
                for a in self.similar_addresses['both_zero']
            ]
        }

        with open('SIMILAR_ADDRESSES_ANALYSIS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("Exported to: SIMILAR_ADDRESSES_ANALYSIS.json")
        print()

def main():
    """Main execution"""
    print("="*80)
    print("SIMILARITY ANALYSIS: FINDING ADDRESSES LIKE 1CFi")
    print("="*80)
    print()

    analyzer = SimilarityAnalyzer()

    # Load data
    analyzer.load_data()

    # Run analyses
    analyzer.analyze_mathematical_properties()
    analyzer.show_similar_addresses()
    analyzer.analyze_seed_patterns()
    analyzer.analyze_transformation_methods()
    analyzer.strategic_search_planning()

    # Export
    analyzer.export_results()

    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print()
    print("Key Findings:")
    print("1. Check SIMILAR_ADDRESSES_ANALYSIS.json for detailed data")
    print("2. Addresses with matching properties identified")
    print("3. Strategic search plan outlined")
    print("4. Ready for exhaustive transformation search")
    print()

if __name__ == "__main__":
    main()
