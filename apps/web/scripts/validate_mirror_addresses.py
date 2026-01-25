#!/usr/bin/env python3
"""
VALIDATE MIRROR ADDRESSES
=========================

Checks if all generated mirror addresses are valid Bitcoin addresses.
"""

import json
import base58
import hashlib

def validate_bitcoin_address(address):
    """
    Validate Bitcoin address checksum
    Returns: (is_valid, error_message)
    """
    try:
        # Decode base58
        decoded = base58.b58decode(address)

        # Must be 25 bytes (1 version + 20 hash160 + 4 checksum)
        if len(decoded) != 25:
            return False, f"Wrong length: {len(decoded)} bytes (expected 25)"

        # Split components
        version = decoded[0:1]
        hash160 = decoded[1:21]
        checksum = decoded[21:25]

        # Recalculate checksum
        version_hash = version + hash160
        calculated_checksum = hashlib.sha256(hashlib.sha256(version_hash).digest()).digest()[:4]

        # Compare
        if checksum != calculated_checksum:
            return False, f"Invalid checksum: {checksum.hex()} != {calculated_checksum.hex()}"

        return True, "Valid"

    except Exception as e:
        return False, f"Decode error: {e}"

def test_all_addresses():
    """Test all addresses from comprehensive_mirror_results.json"""

    print("="*80)
    print("BITCOIN ADDRESS VALIDATION")
    print("="*80)
    print()

    # Load results
    with open('comprehensive_mirror_results.json', 'r') as f:
        data = json.load(f)

    # Test original addresses first
    print("ORIGINAL ADDRESSES:")
    print("-"*80)
    for name, addr in data['original_addresses'].items():
        is_valid, msg = validate_bitcoin_address(addr)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{name:10s}: {addr:40s} {status}")
        if not is_valid:
            print(f"           Error: {msg}")
    print()

    # Test all generated addresses
    print("GENERATED ADDRESSES:")
    print("-"*80)

    valid_count = 0
    invalid_count = 0
    invalid_addresses = []

    for addr_data in data['all_generated_addresses']:
        source = addr_data['source']
        operation = addr_data['operation']
        address = addr_data['address']

        is_valid, msg = validate_bitcoin_address(address)

        if is_valid:
            valid_count += 1
            status = "✓"
        else:
            invalid_count += 1
            status = "✗"
            invalid_addresses.append({
                'source': source,
                'operation': operation,
                'address': address,
                'error': msg
            })

        print(f"{status} {source:10s} | {operation:25s} | {address}")
        if not is_valid:
            print(f"  Error: {msg}")

    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total addresses tested: {valid_count + invalid_count}")
    print(f"Valid addresses:        {valid_count}")
    print(f"Invalid addresses:      {invalid_count}")
    print()

    if invalid_addresses:
        print("INVALID ADDRESSES DETAILS:")
        print("-"*80)
        for inv in invalid_addresses:
            print(f"\nSource:    {inv['source']}")
            print(f"Operation: {inv['operation']}")
            print(f"Address:   {inv['address']}")
            print(f"Error:     {inv['error']}")

    # Export validation results
    output = {
        'validation_date': '2026-01-09',
        'total_tested': valid_count + invalid_count,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'invalid_addresses': invalid_addresses
    }

    with open('address_validation_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("Results saved to: address_validation_results.json")

if __name__ == "__main__":
    test_all_addresses()
