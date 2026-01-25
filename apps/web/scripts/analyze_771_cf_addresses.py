#!/usr/bin/env python3
"""
ANALYZE THE 771 1CF ADDRESSES

We found 771 addresses starting with 1CF.
Now let's analyze them for patterns:
- Which have byte_sum 2299 (like 1CFB and 1CFi)?
- What methods generated them?
- Are there clusters or patterns?
- Can we find mathematical relationships?
"""

import json
import hashlib
from typing import Dict, List, Optional
from collections import defaultdict

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def base58_decode(address: str) -> Optional[bytes]:
    """Decode a Base58Check address to hash160"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    try:
        num = 0
        for char in address:
            num = num * 58 + alphabet.index(char)

        combined = num.to_bytes(25, byteorder='big')
        checksum = combined[-4:]
        payload = combined[:-4]

        if sha256(sha256(payload))[:4] != checksum:
            return None

        return payload[1:]  # Remove version byte
    except Exception:
        return None

class CF_AddressAnalyzer:
    def __init__(self):
        self.cf_addresses = []
        self.analysis = {
            'total': 0,
            'with_2299_sum': [],
            'with_special_properties': [],
            'by_method': defaultdict(list),
            'by_byte_sum': defaultdict(list),
            'statistics': {}
        }

    def analyze_address(self, address: str) -> Optional[Dict]:
        """Analyze mathematical properties"""
        hash160_bytes = base58_decode(address)

        if not hash160_bytes:
            return None

        byte_sum = sum(hash160_bytes)

        return {
            'address': address,
            'hash160': hash160_bytes.hex(),
            'byte_sum': byte_sum,
            'mod_121': byte_sum % 121,
            'mod_19': byte_sum % 19,
            'mod_27': byte_sum % 27,
            'mod_11': byte_sum % 11,
            'mod_13': byte_sum % 13,
            'special_properties': byte_sum % 121 == 0 and byte_sum % 19 == 0,
            'is_2299': byte_sum == 2299
        }

    def load_and_analyze(self):
        """Load bitcoin-private-keys.json and analyze all 1CF addresses"""
        print("=" * 80)
        print("ANALYZING 771 1CF ADDRESSES")
        print("=" * 80)
        print()

        # Load data
        try:
            with open('../public/data/bitcoin-private-keys.json', 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                records = data
            elif isinstance(data, dict) and 'records' in data:
                records = data['records']
            else:
                print(f"Unknown JSON structure")
                return

            print(f"Loaded {len(records)} total addresses")
            print()

            # Filter 1CF addresses
            for record in records:
                addr = record.get('address', '')
                if addr.startswith('1CF'):
                    self.cf_addresses.append(record)

            print(f"Found {len(self.cf_addresses)} addresses starting with 1CF")
            print()

            # Analyze each
            print("Analyzing mathematical properties...")

            for i, record in enumerate(self.cf_addresses):
                if i % 100 == 0:
                    print(f"  Progress: {i}/{len(self.cf_addresses)}")

                address = record['address']
                method = record.get('method', 'unknown')

                props = self.analyze_address(address)

                if not props:
                    continue

                # Store by method
                self.analysis['by_method'][method].append({
                    'address': address,
                    'props': props,
                    'has_seed': 'seed' in record
                })

                # Store by byte sum
                byte_sum = props['byte_sum']
                self.analysis['by_byte_sum'][byte_sum].append(address)

                # Check for special properties
                if props['is_2299']:
                    self.analysis['with_2299_sum'].append({
                        'address': address,
                        'method': method,
                        'props': props,
                        'seed': record.get('seed', None)
                    })

                if props['special_properties']:
                    self.analysis['with_special_properties'].append({
                        'address': address,
                        'method': method,
                        'byte_sum': byte_sum,
                        'seed': record.get('seed', None)
                    })

            print(f"  Progress: {len(self.cf_addresses)}/{len(self.cf_addresses)} - DONE")
            print()

            # Generate statistics
            self.generate_statistics()

            # Display results
            self.display_results()

            # Save results
            self.save_results()

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    def generate_statistics(self):
        """Generate statistical analysis"""
        self.analysis['total'] = len(self.cf_addresses)

        # Count by method
        method_counts = {m: len(addrs) for m, addrs in self.analysis['by_method'].items()}
        self.analysis['statistics']['by_method'] = method_counts

        # Count by byte sum
        byte_sum_counts = {bs: len(addrs) for bs, addrs in self.analysis['by_byte_sum'].items()}
        self.analysis['statistics']['by_byte_sum'] = byte_sum_counts

        # Special counts
        self.analysis['statistics']['with_2299_sum'] = len(self.analysis['with_2299_sum'])
        self.analysis['statistics']['with_special_properties'] = len(self.analysis['with_special_properties'])

    def display_results(self):
        """Display analysis results"""
        print("=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print()

        print(f"Total 1CF addresses: {self.analysis['total']}")
        print()

        # Addresses with byte sum 2299
        print("🎯 ADDRESSES WITH BYTE SUM 2299 (LIKE 1CFB AND 1CFi):")
        print(f"Count: {self.analysis['statistics']['with_2299_sum']}")

        if self.analysis['with_2299_sum']:
            print()
            for item in self.analysis['with_2299_sum']:
                print(f"  {item['address']}")
                print(f"    Method: {item['method']}")
                print(f"    mod 121: {item['props']['mod_121']}, mod 19: {item['props']['mod_19']}")
                if item['seed']:
                    print(f"    Seed: {item['seed'][:50]}...")
                print()
        else:
            print("  (None found)")
        print()

        # Addresses with special properties
        print("🌟 ADDRESSES WITH SPECIAL PROPERTIES (mod 121=0 AND 19=0):")
        print(f"Count: {self.analysis['statistics']['with_special_properties']}")

        if self.analysis['with_special_properties']:
            print()
            # Group by byte sum
            by_sum = defaultdict(list)
            for item in self.analysis['with_special_properties']:
                by_sum[item['byte_sum']].append(item)

            for byte_sum in sorted(by_sum.keys()):
                items = by_sum[byte_sum]
                print(f"  Byte sum {byte_sum}: {len(items)} addresses")
                for item in items[:3]:  # Show first 3
                    print(f"    {item['address']} (method: {item['method']})")
                if len(items) > 3:
                    print(f"    ... and {len(items) - 3} more")
                print()
        print()

        # By method
        print("📊 DISTRIBUTION BY METHOD:")
        for method, count in sorted(self.analysis['statistics']['by_method'].items(),
                                    key=lambda x: x[1], reverse=True):
            print(f"  {method}: {count}")
        print()

        # Byte sum distribution
        print("📈 BYTE SUM DISTRIBUTION (top 10):")
        top_sums = sorted(self.analysis['statistics']['by_byte_sum'].items(),
                         key=lambda x: x[1], reverse=True)[:10]
        for byte_sum, count in top_sums:
            special = "⭐ SPECIAL" if byte_sum == 2299 else ""
            print(f"  {byte_sum}: {count} addresses {special}")
        print()

    def save_results(self):
        """Save analysis results"""
        output = {
            'total_cf_addresses': self.analysis['total'],
            'with_2299_sum': self.analysis['with_2299_sum'],
            'with_special_properties': self.analysis['with_special_properties'],
            'statistics': self.analysis['statistics'],
            'key_findings': {
                'addresses_with_target_sum': self.analysis['statistics']['with_2299_sum'],
                'total_special_properties': self.analysis['statistics']['with_special_properties'],
                'most_common_method': max(self.analysis['statistics']['by_method'].items(),
                                         key=lambda x: x[1]) if self.analysis['statistics']['by_method'] else None
            }
        }

        with open('CF_ADDRESS_ANALYSIS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("=" * 80)
        print("Results saved to: CF_ADDRESS_ANALYSIS.json")
        print("=" * 80)

if __name__ == '__main__':
    print()
    print("🔍" * 40)
    print("ANALYZING THE 771 1CF ADDRESSES")
    print("🔍" * 40)
    print()
    print("Looking for:")
    print("- Addresses with byte sum 2299 (like 1CFB and 1CFi)")
    print("- Addresses with special properties (mod 121=0 AND 19=0)")
    print("- Patterns in generation methods")
    print("- Mathematical relationships")
    print()

    analyzer = CF_AddressAnalyzer()
    analyzer.load_and_analyze()
