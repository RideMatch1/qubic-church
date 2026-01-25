#!/usr/bin/env python3
"""
Find Modulo Exceptions
======================

Find addresses that DON'T have CFB signatures (mod_576≠0 or mod_27≠0).
These exceptions might be specially significant.
"""

import json
import hashlib
from pathlib import Path

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def pubkey_to_address(pubkey_hex: str) -> str:
    """Convert public key to Bitcoin address."""
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        hash160 = ripemd160.digest()
        versioned = b'\x00' + hash160
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        address_bytes = versioned + checksum
        num = int.from_bytes(address_bytes, 'big')
        result = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            result = BASE58_ALPHABET[remainder] + result
        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break
        return result
    except:
        return ""


def address_letter_product(address: str) -> int:
    """Calculate product of letter values."""
    product = 1
    for char in address[1:]:
        if char.upper() in "ABCDEFGHJKLMNPQRSTUVWXYZ":
            if char.isupper():
                val = ord(char) - ord('A') + 1
                if char > 'I': val -= 1
                if char > 'O': val -= 1
            else:
                val = ord(char) - ord('a') + 1
                if char > 'l': val -= 1
            product *= val
    return product


def main():
    script_dir = Path(__file__).parent
    data_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"

    with open(data_path, 'r') as f:
        data = json.load(f)

    records = data.get('records', data)
    print(f"Analyzing {len(records)} records for modulo exceptions...\n")

    exceptions_576 = []
    exceptions_27 = []

    for record in records:
        pubkey = record.get('pubkey', '')
        if not pubkey:
            continue

        address = pubkey_to_address(pubkey)
        if not address:
            continue

        block = record.get('blockHeight', 0)
        product = address_letter_product(address)

        if product % 576 != 0:
            exceptions_576.append({
                "address": address,
                "block": block,
                "product_mod_576": product % 576
            })

        if product % 27 != 0:
            exceptions_27.append({
                "address": address,
                "block": block,
                "product_mod_27": product % 27
            })

    print(f"=== MODULO 576 EXCEPTIONS ({len(exceptions_576)}) ===")
    print("These addresses do NOT have mod_576=0:\n")
    for e in sorted(exceptions_576, key=lambda x: x['block'])[:20]:
        print(f"  Block {e['block']:6d}: {e['address']} (mod 576 = {e['product_mod_576']})")

    print(f"\n=== MODULO 27 EXCEPTIONS ({len(exceptions_27)}) ===")
    print("These addresses do NOT have mod_27=0:\n")
    for e in sorted(exceptions_27, key=lambda x: x['block'])[:20]:
        print(f"  Block {e['block']:6d}: {e['address']} (mod 27 = {e['product_mod_27']})")

    # Save results
    results = {
        "mod_576_exceptions": {
            "count": len(exceptions_576),
            "addresses": exceptions_576
        },
        "mod_27_exceptions": {
            "count": len(exceptions_27),
            "addresses": exceptions_27
        }
    }

    output_path = script_dir / "MODULO_EXCEPTIONS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
