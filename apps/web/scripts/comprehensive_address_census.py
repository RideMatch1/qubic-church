#!/usr/bin/env python3
"""
Comprehensive Address Census
=============================

Categorizes all 21,953 Patoshi addresses by multiple criteria:
- Prefix patterns (1CF, 1QB, etc.)
- All-letter addresses (no digits 2-9)
- CFB modulo signatures (27, 121, 137, 2299)
- Hash160 patterns (0x7b family, byte-sum)
- Mathematical properties

Author: qubic-academic-docs
Date: 2026-01-23
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Base58 alphabet for Bitcoin addresses
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58_LETTERS = set("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
BASE58_DIGITS = set("23456789")  # 0 and 1 are not in base58

# CFB signature numbers
CFB_NUMBERS = {
    27: "3^3 - Ternary cube",
    121: "11^2 - Qubic constant",
    137: "Fine structure constant inverse",
    2299: "CFB prime",
    47: "CFB prime",
    19: "CFB prime",
    576: "24^2",
    676: "26^2",
    283: "CFB prime"
}


def decode_base58(address: str) -> bytes:
    """Decode a base58 address to bytes."""
    result = 0
    for char in address:
        result = result * 58 + BASE58_ALPHABET.index(char)

    # Convert to bytes
    result_bytes = []
    while result > 0:
        result_bytes.append(result % 256)
        result //= 256

    # Add leading zeros for leading '1's
    for char in address:
        if char == '1':
            result_bytes.append(0)
        else:
            break

    return bytes(reversed(result_bytes))


def get_hash160(address: str) -> bytes:
    """Extract Hash160 from a Bitcoin address."""
    try:
        decoded = decode_base58(address)
        # First byte is version, last 4 bytes are checksum
        if len(decoded) >= 25:
            return decoded[1:21]  # Hash160 is 20 bytes
        return b''
    except:
        return b''


def address_letter_product(address: str) -> int:
    """Calculate product of letter values (A=1, B=2, etc.)."""
    product = 1
    for char in address[1:]:  # Skip the leading '1'
        if char.upper() in "ABCDEFGHJKLMNPQRSTUVWXYZ":
            # Base58 letter values
            if char.isupper():
                val = ord(char) - ord('A') + 1
                if char > 'I':  # Skip I
                    val -= 1
                if char > 'O':  # Skip O
                    val -= 1
            else:
                val = ord(char) - ord('a') + 1
                if char > 'l':  # Skip l
                    val -= 1
                if char > 'o':  # Skip o (already skipped in base58)
                    val -= 1
            product *= val
    return product


def is_all_letters(address: str) -> bool:
    """Check if address contains no digits after the leading '1'."""
    return all(c not in BASE58_DIGITS for c in address[1:])


def categorize_by_prefix(address: str) -> List[str]:
    """Categorize address by its prefix."""
    categories = []

    # Check various prefixes
    prefixes = {
        "1CF": "1CF-prefix",
        "1CFB": "1CFB-exact",
        "1QB": "1QB-prefix",
        "1NXT": "1NXT-prefix",
        "1BTC": "1BTC-prefix",
        "1SAT": "1SAT-prefix",
    }

    for prefix, category in prefixes.items():
        if address.startswith(prefix):
            categories.append(category)

    return categories


def categorize_by_modulo(address: str) -> Dict[str, bool]:
    """Check CFB modulo signatures."""
    product = address_letter_product(address)

    return {
        f"mod_{num}": (product % num == 0)
        for num in CFB_NUMBERS.keys()
    }


def analyze_hash160(address: str) -> Dict[str, Any]:
    """Analyze Hash160 properties."""
    h160 = get_hash160(address)
    if not h160:
        return {}

    return {
        "starts_with_0x7b": h160[0] == 0x7b,
        "byte_sum": sum(h160),
        "byte_sum_is_2299": sum(h160) == 2299,
        "first_byte": hex(h160[0]),
        "xor_all": reduce_xor(h160)
    }


def reduce_xor(data: bytes) -> int:
    """XOR all bytes together."""
    result = 0
    for b in data:
        result ^= b
    return result


def pubkey_to_address(pubkey_hex: str) -> str:
    """Convert public key to Bitcoin address."""
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)

        # SHA256
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()

        # RIPEMD160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()

        # Add version byte (0x00 for mainnet)
        versioned = b'\x00' + hash160

        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

        # Encode to base58
        address_bytes = versioned + checksum

        # Convert to base58
        num = int.from_bytes(address_bytes, 'big')
        result = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            result = BASE58_ALPHABET[remainder] + result

        # Add leading '1's for leading zero bytes
        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break

        return result
    except:
        return ""


def load_patoshi_data() -> List[Dict]:
    """Load Patoshi addresses from JSON."""
    script_dir = Path(__file__).parent
    data_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"

    with open(data_path, 'r') as f:
        data = json.load(f)

    return data.get('records', data)


def run_census():
    """Run the comprehensive address census."""
    print("Loading Patoshi data...")
    records = load_patoshi_data()
    print(f"Loaded {len(records)} records")

    # Results containers
    results = {
        "metadata": {
            "total_records": len(records),
            "date": "2026-01-23"
        },
        "categories": defaultdict(list),
        "prefix_counts": defaultdict(int),
        "modulo_counts": defaultdict(int),
        "special_addresses": [],
        "all_letter_addresses": [],
        "hash160_analysis": {
            "0x7b_family": [],
            "bytesum_2299": []
        }
    }

    # Process each record
    for i, record in enumerate(records):
        if i % 5000 == 0:
            print(f"Processing {i}/{len(records)}...")

        # Get address from pubkey
        pubkey = record.get('pubkey', '')
        if not pubkey:
            continue

        address = pubkey_to_address(pubkey)
        if not address:
            continue

        block = record.get('blockHeight', 0)

        # Create address entry
        entry = {
            "address": address,
            "block": block,
            "pubkey": pubkey[:32] + "..."  # Truncate for readability
        }

        # Check prefix categories
        prefixes = categorize_by_prefix(address)
        for prefix in prefixes:
            results["categories"][prefix].append(entry)
            results["prefix_counts"][prefix] += 1

        # Check if all letters
        if is_all_letters(address):
            results["all_letter_addresses"].append(entry)

        # Check modulo signatures
        modulos = categorize_by_modulo(address)
        for mod_key, matches in modulos.items():
            if matches:
                results["modulo_counts"][mod_key] += 1

        # Check if matches MULTIPLE CFB modulos (special)
        cfb_match_count = sum(1 for v in modulos.values() if v)
        if cfb_match_count >= 5:
            entry["cfb_matches"] = cfb_match_count
            entry["modulos"] = {k: v for k, v in modulos.items() if v}
            results["special_addresses"].append(entry)

        # Analyze Hash160
        h160_analysis = analyze_hash160(address)
        if h160_analysis.get("starts_with_0x7b"):
            results["hash160_analysis"]["0x7b_family"].append(entry)
        if h160_analysis.get("byte_sum_is_2299"):
            results["hash160_analysis"]["bytesum_2299"].append(entry)

    # Convert defaultdicts to regular dicts for JSON serialization
    results["categories"] = dict(results["categories"])
    results["prefix_counts"] = dict(results["prefix_counts"])
    results["modulo_counts"] = dict(results["modulo_counts"])

    # Summary statistics
    results["summary"] = {
        "total_processed": len(records),
        "all_letter_count": len(results["all_letter_addresses"]),
        "special_cfb_count": len(results["special_addresses"]),
        "0x7b_family_count": len(results["hash160_analysis"]["0x7b_family"]),
        "bytesum_2299_count": len(results["hash160_analysis"]["bytesum_2299"]),
        "prefix_summary": dict(results["prefix_counts"]),
        "modulo_summary": dict(results["modulo_counts"])
    }

    return results


def main():
    print("=" * 60)
    print("COMPREHENSIVE ADDRESS CENSUS")
    print("=" * 60)

    results = run_census()

    # Save results
    output_path = Path(__file__).parent / "COMPREHENSIVE_ADDRESS_CENSUS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    summary = results["summary"]
    print(f"\nTotal Processed: {summary['total_processed']}")
    print(f"\nAll-Letter Addresses: {summary['all_letter_count']}")
    print(f"Special CFB Addresses (5+ modulo matches): {summary['special_cfb_count']}")
    print(f"0x7b Hash160 Family: {summary['0x7b_family_count']}")
    print(f"ByteSum=2299 Addresses: {summary['bytesum_2299_count']}")

    print("\nPrefix Counts:")
    for prefix, count in sorted(summary['prefix_summary'].items()):
        print(f"  {prefix}: {count}")

    print("\nModulo Signature Counts:")
    for mod, count in sorted(summary['modulo_summary'].items(), key=lambda x: -x[1]):
        print(f"  {mod}: {count}")

    # Show some special addresses
    print("\n" + "=" * 60)
    print("NOTABLE ADDRESSES")
    print("=" * 60)

    if results["categories"].get("1CFB-exact"):
        print("\n1CFB Exact Matches:")
        for entry in results["categories"]["1CFB-exact"][:5]:
            print(f"  {entry['address']} (Block {entry['block']})")

    if results["all_letter_addresses"]:
        print(f"\nAll-Letter Addresses (showing first 10 of {len(results['all_letter_addresses'])}):")
        for entry in results["all_letter_addresses"][:10]:
            print(f"  {entry['address']} (Block {entry['block']})")

    if results["special_addresses"]:
        print(f"\nSpecial CFB Addresses (5+ modulo matches, showing first 5):")
        for entry in results["special_addresses"][:5]:
            print(f"  {entry['address']} (Block {entry['block']}, {entry['cfb_matches']} matches)")


if __name__ == "__main__":
    main()
