#!/usr/bin/env python3
"""
ANALYZE THE 754 NEW 1CF ADDRESSES FROM MATRIX-ADDRESSES.JSON

We just discovered 754 1CF addresses in the 983k matrix!
Let's analyze them all for:
- Byte sum 2299 (like 1CFB and 1CFi)
- Special properties (mod 121=0, mod 19=0)
- Patterns and distribution
- Mathematical relationships
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

class MatrixCFAnalyzer:
    def __init__(self):
        self.cf_addresses = []
        self.analysis = {
            'total': 0,
            'with_2299_sum': [],
            'with_special_properties': [],
            'by_byte_sum': defaultdict(list),
            'statistics': {}
        }

    def analyze_address(self, address: str, record: Dict) -> Optional[Dict]:
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
            'is_2299': byte_sum == 2299,
            'record': record
        }

    def load_and_analyze(self):
        """Load matrix-addresses.json and analyze all 1CF addresses"""
        print("=" * 80)
        print("ANALYZING 754 1CF ADDRESSES FROM MATRIX-ADDRESSES.JSON")
        print("=" * 80)
        print()

        # Load data
        try:
            with open('../public/data/matrix-addresses.json', 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                records = data
            elif isinstance(data, dict) and 'records' in data:
                records = data['records']
            else:
                print(f"Unknown JSON structure")
                return

            print(f"Loaded {len(records):,} total addresses from matrix")
            print()

            # Filter and analyze 1CF addresses
            print("Filtering 1CF addresses...")

            for i, record in enumerate(records):
                if i % 100000 == 0:
                    print(f"  Progress: {i:,}/{len(records):,}")

                addr = record.get('address')
                if addr and addr.startswith('1CF'):
                    props = self.analyze_address(addr, record)

                    if props:
                        self.cf_addresses.append(props)

                        # Store by byte sum
                        byte_sum = props['byte_sum']
                        self.analysis['by_byte_sum'][byte_sum].append(props)

                        # Check for special properties
                        if props['is_2299']:
                            self.analysis['with_2299_sum'].append(props)

                        if props['special_properties']:
                            self.analysis['with_special_properties'].append(props)

            print(f"  Progress: {len(records):,}/{len(records):,} - DONE")
            print()
            print(f"Found and analyzed {len(self.cf_addresses)} 1CF addresses")
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

        print(f"Total 1CF addresses from matrix: {self.analysis['total']}")
        print()

        # Addresses with byte sum 2299
        print("🎯 ADDRESSES WITH BYTE SUM 2299 (LIKE 1CFB AND 1CFi):")
        print(f"Count: {self.analysis['statistics']['with_2299_sum']}")

        if self.analysis['with_2299_sum']:
            print()
            print("🎉🎉🎉 FOUND ADDRESSES WITH TARGET BYTE SUM! 🎉🎉🎉")
            print()
            for item in self.analysis['with_2299_sum']:
                print(f"  {item['address']}")
                print(f"    Byte sum: {item['byte_sum']}")
                print(f"    mod 121: {item['mod_121']}, mod 19: {item['mod_19']}")
                print(f"    Hash160: {item['hash160']}")

                # Show matrix coordinates if available
                if 'row' in item['record']:
                    print(f"    Matrix position: row={item['record']['row']}, col={item['record']['col']}")
                if 'method' in item['record']:
                    print(f"    Method: {item['record']['method']}")
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
                is_target = "⭐ TARGET!" if byte_sum == 2299 else ""
                print(f"  Byte sum {byte_sum}: {len(items)} addresses {is_target}")
                for item in items[:3]:  # Show first 3
                    print(f"    {item['address']}")
                if len(items) > 3:
                    print(f"    ... and {len(items) - 3} more")
                print()
        print()

        # Byte sum distribution
        print("📈 BYTE SUM DISTRIBUTION (top 20):")
        top_sums = sorted(self.analysis['statistics']['by_byte_sum'].items(),
                         key=lambda x: x[1], reverse=True)[:20]
        for byte_sum, count in top_sums:
            special = "⭐ SPECIAL" if byte_sum == 2299 else ""
            special_prop = "✓ mod 121&19=0" if byte_sum % 121 == 0 and byte_sum % 19 == 0 else ""
            print(f"  {byte_sum}: {count} addresses {special} {special_prop}")
        print()

        # Compare with 1CFi
        print("🔍 COMPARISON WITH 1CFi:")
        print("  1CFi: 1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi")
        print("  Byte sum: 2299, mod 121=0, mod 19=0")
        print()
        if self.analysis['with_2299_sum']:
            print(f"  Matrix contains {len(self.analysis['with_2299_sum'])} address(es) with same properties!")
        else:
            print("  No addresses in matrix with same byte sum 2299")
        print()

    def save_results(self):
        """Save analysis results"""
        # Prepare output (limit record details for size)
        output = {
            'total_cf_addresses': self.analysis['total'],
            'with_2299_sum': [
                {
                    'address': item['address'],
                    'byte_sum': item['byte_sum'],
                    'hash160': item['hash160'],
                    'mod_121': item['mod_121'],
                    'mod_19': item['mod_19'],
                    'mod_27': item['mod_27'],
                    'mod_11': item['mod_11'],
                    'mod_13': item['mod_13'],
                    'matrix_position': {
                        'row': item['record'].get('row'),
                        'col': item['record'].get('col')
                    } if 'row' in item['record'] else None,
                    'method': item['record'].get('method')
                }
                for item in self.analysis['with_2299_sum']
            ],
            'with_special_properties_summary': {
                byte_sum: len(items)
                for byte_sum, items in defaultdict(list,
                    [(item['byte_sum'], item) for item in self.analysis['with_special_properties']]
                ).items()
            },
            'statistics': self.analysis['statistics'],
            'key_findings': {
                'addresses_with_target_sum_2299': self.analysis['statistics']['with_2299_sum'],
                'total_special_properties': self.analysis['statistics']['with_special_properties'],
                'most_common_byte_sum': max(self.analysis['statistics']['by_byte_sum'].items(),
                                          key=lambda x: x[1]) if self.analysis['statistics']['by_byte_sum'] else None
            }
        }

        with open('MATRIX_CF_ADDRESS_ANALYSIS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("=" * 80)
        print("Results saved to: MATRIX_CF_ADDRESS_ANALYSIS.json")
        print("=" * 80)

if __name__ == '__main__':
    print()
    print("🔍" * 40)
    print("ANALYZING 754 1CF ADDRESSES FROM MATRIX")
    print("🔍" * 40)
    print()
    print("Looking for:")
    print("- Addresses with byte sum 2299 (like 1CFB and 1CFi)")
    print("- Addresses with special properties (mod 121=0 AND 19=0)")
    print("- Patterns in the 983k matrix")
    print("- Mathematical relationships")
    print()

    analyzer = MatrixCFAnalyzer()
    analyzer.load_and_analyze()
