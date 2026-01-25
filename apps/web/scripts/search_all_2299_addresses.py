#!/usr/bin/env python3
"""
SEARCH ALL RESULT FILES FOR ADDRESSES WITH BYTE SUM 2299

The user says we had more addresses with 0x7b!
Let's search ALL our result files for addresses with byte sum 2299.
"""

import json
import hashlib
from typing import Dict, List, Optional, Set
import os
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

class Comprehensive2299Search:
    def __init__(self):
        self.result_files = [
            'K12_OFFICIAL_QUBIC_RESULTS.json',
            'K12_TRANSFORM_RESULTS.json',
            'PATTERN_ANALYSIS_RESULTS.json',
            'UNEXPLORED_SEEDS_RESULTS.json',
            'CF_ADDRESS_ANALYSIS.json',
            'MATRIX_CF_ADDRESS_ANALYSIS.json',
            'CURL_HASH_TEST_RESULTS.json',
            'SIMILAR_ADDRESSES_ANALYSIS.json',
            'MULTI_ADDRESS_ANALYSIS.json'
        ]

        self.addresses_2299 = []
        self.by_first_byte = defaultdict(list)

    def analyze_address(self, address: str) -> Optional[Dict]:
        """Analyze an address"""
        hash160_bytes = base58_decode(address)

        if not hash160_bytes:
            return None

        byte_sum = sum(hash160_bytes)

        if byte_sum == 2299:
            return {
                'address': address,
                'hash160': hash160_bytes.hex(),
                'byte_sum': byte_sum,
                'first_byte': hash160_bytes[0],
                'first_byte_hex': f'0x{hash160_bytes[0]:02x}',
                'mod_121': byte_sum % 121,
                'mod_19': byte_sum % 19
            }

        return None

    def search_json_recursively(self, obj, file_source: str):
        """Recursively search JSON object for addresses"""
        if isinstance(obj, dict):
            # Check for address fields
            addr = obj.get('address') or obj.get('btcAddress')
            if addr and isinstance(addr, str):
                props = self.analyze_address(addr)
                if props:
                    props['source'] = file_source
                    props['full_record'] = obj
                    self.addresses_2299.append(props)
                    self.by_first_byte[props['first_byte']].append(props)

            # Recurse into dict values
            for value in obj.values():
                self.search_json_recursively(value, file_source)

        elif isinstance(obj, list):
            for item in obj:
                self.search_json_recursively(item, file_source)

    def search_file(self, filename: str):
        """Search a single JSON file"""
        if not os.path.exists(filename):
            return

        print(f"Searching: {filename}")

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.search_json_recursively(data, filename)

        except Exception as e:
            print(f"  Error: {e}")

    def run_search(self):
        """Search all files"""
        print("=" * 80)
        print("SEARCHING ALL RESULT FILES FOR BYTE SUM 2299")
        print("=" * 80)
        print()

        for filename in self.result_files:
            self.search_file(filename)

        print()
        print("=" * 80)
        print("SEARCH COMPLETE")
        print("=" * 80)
        print()

        print(f"Total addresses with byte sum 2299: {len(self.addresses_2299)}")
        print()

        # Group by first byte
        print("BY FIRST BYTE:")
        for first_byte in sorted(self.by_first_byte.keys()):
            addrs = self.by_first_byte[first_byte]
            print(f"  0x{first_byte:02x}: {len(addrs)} addresses")
        print()

        # Show all addresses
        print("=" * 80)
        print("ALL ADDRESSES WITH BYTE SUM 2299")
        print("=" * 80)
        print()

        # Deduplicate by address
        unique_addrs = {}
        for props in self.addresses_2299:
            addr = props['address']
            if addr not in unique_addrs:
                unique_addrs[addr] = props
            else:
                # Track multiple sources
                if 'sources' not in unique_addrs[addr]:
                    unique_addrs[addr]['sources'] = [unique_addrs[addr]['source']]
                unique_addrs[addr]['sources'].append(props['source'])

        print(f"Unique addresses: {len(unique_addrs)}")
        print()

        # Sort by first byte
        sorted_addrs = sorted(unique_addrs.values(), key=lambda x: x['first_byte'])

        for i, props in enumerate(sorted_addrs, 1):
            print(f"{i}. {props['address']}")
            print(f"   Hash160: {props['hash160']}")
            print(f"   First byte: {props['first_byte_hex']} ({props['first_byte']})")
            print(f"   Byte sum: {props['byte_sum']} (mod 121={props['mod_121']}, mod 19={props['mod_19']})")

            # Show sources
            if 'sources' in props:
                print(f"   Sources: {', '.join(props['sources'])}")
            else:
                print(f"   Source: {props['source']}")

            # Show seed if available
            if 'seed' in props.get('full_record', {}):
                seed = props['full_record']['seed']
                print(f"   Seed: {seed[:50]}...")

            # Show method if available
            if 'method' in props.get('full_record', {}):
                print(f"   Method: {props['full_record']['method']}")

            print()

        # Save results
        output = {
            'total_found': len(self.addresses_2299),
            'unique_addresses': len(unique_addrs),
            'by_first_byte': {
                f'0x{fb:02x}': len(addrs)
                for fb, addrs in self.by_first_byte.items()
            },
            'addresses': sorted_addrs
        }

        with open('ALL_2299_ADDRESSES_COMPREHENSIVE.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("=" * 80)
        print("Results saved to: ALL_2299_ADDRESSES_COMPREHENSIVE.json")
        print("=" * 80)

if __name__ == '__main__':
    print()
    print("🔍" * 40)
    print("COMPREHENSIVE SEARCH FOR ALL BYTE SUM 2299 ADDRESSES")
    print("🔍" * 40)
    print()

    searcher = Comprehensive2299Search()
    searcher.run_search()
