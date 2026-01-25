#!/usr/bin/env python3
"""
COMPREHENSIVE MIRROR ANALYSIS
==============================

Applies ALL mirror operations to Genesis, 1CFB, and 15ubic addresses.
Tests all generated addresses and looks for patterns.
"""

import hashlib
import base58
import json
from typing import List, Dict, Tuple

class ComprehensiveMirrorAnalysis:
    """Complete mirror analysis for all three key addresses"""

    def __init__(self):
        # The three key addresses
        self.addresses = {
            'Genesis': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            '1CFB': '1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg',
            '15ubic': '15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG'
        }

        self.hash160s = {}
        self.results = {}

        # Extract hash160 for each
        for name, addr in self.addresses.items():
            self.hash160s[name] = self.hash160_from_address(addr)

    def hash160_from_address(self, address):
        """Extract hash160 from Bitcoin address"""
        try:
            decoded = base58.b58decode(address)
            return decoded[1:21].hex()
        except:
            return None

    def address_from_hash160(self, hash160_hex):
        """Create Bitcoin address from hash160"""
        try:
            hash160_bytes = bytes.fromhex(hash160_hex)
            version_hash = bytes([0x00]) + hash160_bytes
            checksum = hashlib.sha256(hashlib.sha256(version_hash).digest()).digest()[:4]
            address = base58.b58encode(version_hash + checksum).decode('utf-8')
            return address
        except Exception as e:
            return f"Error: {e}"

    def reverse_bytes(self, hex_string):
        """Reverse bytes of hex string"""
        return bytes.fromhex(hex_string)[::-1].hex()

    def mirror_operations_single(self, name, hash160):
        """Apply all mirror operations to a single address"""
        print(f"\n{'='*80}")
        print(f"MIRROR OPERATIONS: {name}")
        print(f"{'='*80}\n")
        print(f"Original Address: {self.addresses[name]}")
        print(f"Hash160:          {hash160}")
        print()

        operations = []
        hash_bytes = bytes.fromhex(hash160)

        # Operation 1: Reverse Hash160
        reversed_hash = self.reverse_bytes(hash160)
        reversed_addr = self.address_from_hash160(reversed_hash)
        operations.append(('Reverse Hash160', reversed_addr, reversed_hash))
        print(f"1. Reverse Hash160:     {reversed_addr}")

        # Operation 2: Bitwise Complement (255-x)
        complement = bytes(255 - b for b in hash_bytes).hex()
        complement_addr = self.address_from_hash160(complement)
        operations.append(('Bitwise Complement', complement_addr, complement))
        print(f"2. Bitwise Complement:  {complement_addr}")

        # Operation 3: Mirror Palindrome (first half + reversed first half)
        half = hash160[:20]  # 10 bytes in hex = 20 chars
        mirror = half + half[::-1]
        mirror_addr = self.address_from_hash160(mirror)
        operations.append(('Mirror Palindrome', mirror_addr, mirror))
        print(f"3. Mirror Palindrome:   {mirror_addr}")

        # Operation 4: Rotate by 121
        rotated_121 = bytes((b + 121) % 256 for b in hash_bytes).hex()
        rotated_addr = self.address_from_hash160(rotated_121)
        operations.append(('Rotate +121', rotated_addr, rotated_121))
        print(f"4. Rotate +121:         {rotated_addr}")

        # Operation 5: Rotate by 19
        rotated_19 = bytes((b + 19) % 256 for b in hash_bytes).hex()
        rotated_19_addr = self.address_from_hash160(rotated_19)
        operations.append(('Rotate +19', rotated_19_addr, rotated_19))
        print(f"5. Rotate +19:          {rotated_19_addr}")

        # Operation 6: Rotate by 27
        rotated_27 = bytes((b + 27) % 256 for b in hash_bytes).hex()
        rotated_27_addr = self.address_from_hash160(rotated_27)
        operations.append(('Rotate +27', rotated_27_addr, rotated_27))
        print(f"6. Rotate +27:          {rotated_27_addr}")

        # Operation 7: Syzygy 255 (255-x, same as complement)
        # Already done in Operation 2

        # Operation 8: XOR with all 0xFF
        xor_ff = bytes(b ^ 0xFF for b in hash_bytes).hex()
        xor_ff_addr = self.address_from_hash160(xor_ff)
        operations.append(('XOR 0xFF', xor_ff_addr, xor_ff))
        print(f"7. XOR 0xFF:            {xor_ff_addr}")

        # Operation 9: Swap halves
        first_half = hash160[:20]
        second_half = hash160[20:]
        swapped = second_half + first_half
        swapped_addr = self.address_from_hash160(swapped)
        operations.append(('Swap Halves', swapped_addr, swapped))
        print(f"8. Swap Halves:         {swapped_addr}")

        return operations

    def cross_address_operations(self):
        """Operations between different addresses"""
        print(f"\n{'='*80}")
        print("CROSS-ADDRESS OPERATIONS")
        print(f"{'='*80}\n")

        cross_ops = []

        # XOR between each pair
        pairs = [
            ('Genesis', '1CFB'),
            ('Genesis', '15ubic'),
            ('1CFB', '15ubic')
        ]

        for name1, name2 in pairs:
            hash1 = bytes.fromhex(self.hash160s[name1])
            hash2 = bytes.fromhex(self.hash160s[name2])

            xor_result = bytes(a ^ b for a, b in zip(hash1, hash2)).hex()
            xor_addr = self.address_from_hash160(xor_result)
            xor_sum = sum(bytes.fromhex(xor_result))

            print(f"\n{name1} XOR {name2}:")
            print(f"  Address: {xor_addr}")
            print(f"  Hash:    {xor_result}")
            print(f"  Sum:     {xor_sum}")
            print(f"  mod 121: {xor_sum % 121}")
            print(f"  mod 19:  {xor_sum % 19}")
            print(f"  mod 27:  {xor_sum % 27}")
            print(f"  mod 9:   {xor_sum % 9}")

            cross_ops.append({
                'operation': f'{name1} XOR {name2}',
                'address': xor_addr,
                'hash': xor_result,
                'sum': xor_sum,
                'mod_121': xor_sum % 121,
                'mod_19': xor_sum % 19,
                'mod_27': xor_sum % 27,
                'mod_9': xor_sum % 9
            })

        # ADD between each pair
        for name1, name2 in pairs:
            hash1 = bytes.fromhex(self.hash160s[name1])
            hash2 = bytes.fromhex(self.hash160s[name2])

            add_result = bytes((a + b) % 256 for a, b in zip(hash1, hash2)).hex()
            add_addr = self.address_from_hash160(add_result)

            print(f"\n{name1} + {name2} (mod 256):")
            print(f"  Address: {add_addr}")
            print(f"  Hash:    {add_result}")

            cross_ops.append({
                'operation': f'{name1} + {name2}',
                'address': add_addr,
                'hash': add_result
            })

        return cross_ops

    def analyze_patterns(self, all_results):
        """Look for patterns in generated addresses"""
        print(f"\n{'='*80}")
        print("PATTERN ANALYSIS")
        print(f"{'='*80}\n")

        all_addresses = []

        # Collect all addresses
        for name, ops in all_results.items():
            for op_name, addr, hash_val in ops:
                all_addresses.append({
                    'source': name,
                    'operation': op_name,
                    'address': addr,
                    'hash': hash_val
                })

        print(f"Total addresses generated: {len(all_addresses)}")
        print()

        # Check for duplicates
        addr_list = [a['address'] for a in all_addresses]
        duplicates = [addr for addr in addr_list if addr_list.count(addr) > 1]

        if duplicates:
            print("DUPLICATES FOUND:")
            for dup in set(duplicates):
                sources = [a for a in all_addresses if a['address'] == dup]
                print(f"\n  {dup}")
                for s in sources:
                    print(f"    - {s['source']}: {s['operation']}")
        else:
            print("No duplicate addresses found")

        print()

        # Check if any start with interesting prefixes
        interesting_prefixes = ['1CFB', '1A1z', '15ub', '1BTC', '1QUB', '1SAT']

        print("Addresses with interesting prefixes:")
        for prefix in interesting_prefixes:
            matches = [a for a in all_addresses if a['address'].startswith(prefix)]
            if matches:
                print(f"\n  Starting with '{prefix}':")
                for m in matches:
                    print(f"    {m['address']} ({m['source']} - {m['operation']})")

        return all_addresses

    def export_results(self, all_results, cross_ops, all_addresses):
        """Export all results to JSON"""
        output = {
            'timestamp': '2026-01-09',
            'original_addresses': self.addresses,
            'hash160_values': self.hash160s,
            'mirror_operations': {},
            'cross_operations': cross_ops,
            'all_generated_addresses': all_addresses,
            'summary': {
                'total_addresses_generated': len(all_addresses),
                'unique_addresses': len(set(a['address'] for a in all_addresses))
            }
        }

        for name, ops in all_results.items():
            output['mirror_operations'][name] = [
                {
                    'operation': op_name,
                    'address': addr,
                    'hash160': hash_val
                }
                for op_name, addr, hash_val in ops
            ]

        with open('comprehensive_mirror_results.json', 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n{'='*80}")
        print("RESULTS EXPORTED")
        print(f"{'='*80}\n")
        print("Saved to: comprehensive_mirror_results.json")
        print()
        print("Next steps:")
        print("1. Check each address on blockchain explorers")
        print("2. Look for any with transactions or balances")
        print("3. Document any interesting findings")
        print()

def main():
    """Main execution"""
    print("="*80)
    print("COMPREHENSIVE MIRROR ANALYSIS")
    print("Testing Genesis, 1CFB, and 15ubic addresses")
    print("="*80)

    analyzer = ComprehensiveMirrorAnalysis()

    # Show original values
    print(f"\n{'='*80}")
    print("ORIGINAL ADDRESSES")
    print(f"{'='*80}\n")
    for name, addr in analyzer.addresses.items():
        print(f"{name:10s}: {addr}")
        print(f"{'':10s}  Hash160: {analyzer.hash160s[name]}")
        print()

    # Mirror operations for each address
    all_results = {}
    for name, hash160 in analyzer.hash160s.items():
        all_results[name] = analyzer.mirror_operations_single(name, hash160)

    # Cross-address operations
    cross_ops = analyzer.cross_address_operations()

    # Pattern analysis
    all_addresses = analyzer.analyze_patterns(all_results)

    # Export
    analyzer.export_results(all_results, cross_ops, all_addresses)

    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
