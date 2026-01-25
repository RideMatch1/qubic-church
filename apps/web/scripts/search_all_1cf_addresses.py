#!/usr/bin/env python3
"""
SEARCH ALL JSON FILES FOR 1CF ADDRESSES

We found 771 in bitcoin-private-keys.json
But there are many more large JSON files:
- bitcoin-derived-addresses.json (4.1M)
- matrix-addresses.json (61M)
- matrix_addresses_with_xor.json (180M)
- patoshi-addresses.json (4.7M)

Let's search ALL of them for 1CF addresses!
"""

import json
import os
from typing import Dict, List, Set
from collections import defaultdict

class ComprehensiveCFSearch:
    def __init__(self):
        self.data_dir = '../public/data'
        self.files_to_search = [
            'bitcoin-private-keys.json',
            'bitcoin-derived-addresses.json',
            'matrix-addresses.json',
            'matrix_addresses_with_xor.json',
            'patoshi-addresses.json',
            'interesting-addresses.json',
            'anna-matrix.json'
        ]

        self.results = {
            'by_file': {},
            'unique_addresses': set(),
            'total_1cf_found': 0
        }

    def search_file(self, filename: str) -> Dict:
        """Search a single JSON file for 1CF addresses"""
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            return {'error': 'File not found', 'count': 0}

        file_size = os.path.getsize(filepath)
        print(f"\n{'=' * 80}")
        print(f"Searching: {filename}")
        print(f"Size: {file_size / (1024*1024):.1f} MB")
        print(f"{'=' * 80}")

        cf_addresses = []
        total_records = 0

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                if 'records' in data:
                    records = data['records']
                elif 'addresses' in data:
                    records = data['addresses']
                elif 'nodes' in data:
                    # Neuraxon network structure
                    records = data['nodes']
                else:
                    # Treat dict values as records
                    records = []
                    for key, value in data.items():
                        if isinstance(value, dict):
                            value['_key'] = key
                            records.append(value)
                        elif isinstance(value, str) and value.startswith('1'):
                            records.append({'address': value})
            else:
                print(f"  Unknown structure: {type(data)}")
                return {'count': 0, 'addresses': []}

            total_records = len(records)
            print(f"Total records: {total_records:,}")

            # Search for 1CF addresses
            for i, record in enumerate(records):
                if i % 100000 == 0 and i > 0:
                    print(f"  Progress: {i:,}/{total_records:,} ({i/total_records*100:.1f}%)")

                # Get address from record
                addr = None
                if isinstance(record, str):
                    addr = record
                elif isinstance(record, dict):
                    addr = record.get('address') or record.get('btcAddress') or record.get('id')

                if addr and isinstance(addr, str) and addr.startswith('1CF'):
                    cf_addresses.append({
                        'address': addr,
                        'source': filename,
                        'record': record
                    })
                    self.results['unique_addresses'].add(addr)

            print(f"  Found: {len(cf_addresses)} addresses starting with 1CF")

            return {
                'count': len(cf_addresses),
                'addresses': cf_addresses,
                'total_records': total_records
            }

        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'count': 0}

    def run_search(self):
        """Search all files"""
        print("\n" + "🔍" * 40)
        print("COMPREHENSIVE 1CF ADDRESS SEARCH")
        print("🔍" * 40)
        print()
        print("Searching ALL JSON files for 1CF addresses...")

        for filename in self.files_to_search:
            result = self.search_file(filename)
            self.results['by_file'][filename] = result
            self.results['total_1cf_found'] += result.get('count', 0)

        # Summary
        print("\n" + "=" * 80)
        print("SEARCH COMPLETE - SUMMARY")
        print("=" * 80)
        print()

        for filename, result in self.results['by_file'].items():
            count = result.get('count', 0)
            total = result.get('total_records', 0)
            if count > 0:
                print(f"✓ {filename}: {count:,} 1CF addresses (from {total:,} records)")
            else:
                print(f"  {filename}: 0 1CF addresses (from {total:,} records)")

        print()
        print(f"Total 1CF addresses found (with duplicates): {self.results['total_1cf_found']:,}")
        print(f"Unique 1CF addresses: {len(self.results['unique_addresses']):,}")
        print()

        # Check for 1CFB
        print("🎯 CHECKING FOR 1CFB...")
        target = '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg'

        if target in self.results['unique_addresses']:
            print(f"🎉 FOUND 1CFB in the datasets!")
            for filename, result in self.results['by_file'].items():
                for item in result.get('addresses', []):
                    if item['address'] == target:
                        print(f"  Found in: {filename}")
        else:
            print(f"❌ 1CFB NOT found in any dataset")
        print()

        # Save results
        output = {
            'total_1cf_found': self.results['total_1cf_found'],
            'unique_count': len(self.results['unique_addresses']),
            'unique_addresses': sorted(list(self.results['unique_addresses'])),
            'by_file': {
                filename: {
                    'count': result.get('count', 0),
                    'total_records': result.get('total_records', 0)
                }
                for filename, result in self.results['by_file'].items()
            },
            'contains_1cfb': target in self.results['unique_addresses']
        }

        with open('COMPREHENSIVE_1CF_SEARCH.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("Results saved to: COMPREHENSIVE_1CF_SEARCH.json")
        print()

if __name__ == '__main__':
    searcher = ComprehensiveCFSearch()
    searcher.run_search()
