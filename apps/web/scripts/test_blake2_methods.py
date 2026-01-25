#!/usr/bin/env python3
"""
Blake2 Hash Methods Testing Script
===================================
Tests all 23,765 Qubic seeds with Blake2b and Blake2s hash functions
to find matches with target Bitcoin address and special mathematical properties.

Target Address: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg
Special Properties: byte_sum % 121 == 0 AND byte_sum % 19 == 0

Author: Qubic Research Team
Date: 2026-01-15
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Bitcoin address generation dependencies
try:
    import ecdsa
    import base58
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: ecdsa or base58 not installed. Install with: pip install ecdsa base58")

# Constants
TARGET_ADDRESS = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEEDS_FILE = os.path.join(SCRIPT_DIR, "..", "public", "data", "qubic-seeds.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "BLAKE2_HASH_RESULTS.json")


def blake2b_hash(data: bytes, digest_size: int = 32) -> bytes:
    """Compute Blake2b hash of data."""
    return hashlib.blake2b(data, digest_size=digest_size).digest()


def blake2s_hash(data: bytes, digest_size: int = 32) -> bytes:
    """Compute Blake2s hash of data."""
    return hashlib.blake2s(data, digest_size=digest_size).digest()


def private_key_to_bitcoin_address(private_key: bytes) -> Optional[str]:
    """Convert a 32-byte private key to a Bitcoin address (P2PKH, compressed)."""
    if not CRYPTO_AVAILABLE:
        return None

    try:
        # Ensure private key is 32 bytes
        if len(private_key) != 32:
            return None

        # Check if private key is valid (non-zero and less than curve order)
        key_int = int.from_bytes(private_key, 'big')
        if key_int == 0 or key_int >= ecdsa.SECP256k1.order:
            return None

        # Create signing key from private key
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()

        # Get compressed public key
        public_key_point = verifying_key.pubkey.point
        x = public_key_point.x()
        y = public_key_point.y()

        if y % 2 == 0:
            compressed_pubkey = b'\x02' + x.to_bytes(32, 'big')
        else:
            compressed_pubkey = b'\x03' + x.to_bytes(32, 'big')

        # SHA256 of public key
        sha256_hash = hashlib.sha256(compressed_pubkey).digest()

        # RIPEMD160 of SHA256
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        pubkey_hash = ripemd160.digest()

        # Add version byte (0x00 for mainnet)
        versioned_hash = b'\x00' + pubkey_hash

        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]

        # Base58Check encoding
        address = base58.b58encode(versioned_hash + checksum).decode('utf-8')

        return address

    except Exception as e:
        return None


def check_special_properties(data: bytes) -> Dict[str, Any]:
    """Check for special mathematical properties in byte data."""
    byte_sum = sum(data)

    return {
        "byte_sum": byte_sum,
        "mod_121": byte_sum % 121,
        "mod_19": byte_sum % 19,
        "is_special": (byte_sum % 121 == 0) and (byte_sum % 19 == 0),
        "mod_27": byte_sum % 27,
        "mod_7": byte_sum % 7
    }


def process_seed(seed: str, seed_id: int) -> Dict[str, Any]:
    """Process a single seed with all Blake2 hash methods."""
    seed_bytes = seed.encode('utf-8')

    result = {
        "id": seed_id,
        "seed": seed,
        "methods": {}
    }

    # Method 1: Blake2b(seed)
    blake2b_result = blake2b_hash(seed_bytes)
    blake2b_address = private_key_to_bitcoin_address(blake2b_result)
    blake2b_props = check_special_properties(blake2b_result)

    result["methods"]["blake2b"] = {
        "private_key_hex": blake2b_result.hex(),
        "bitcoin_address": blake2b_address,
        "matches_target": blake2b_address == TARGET_ADDRESS,
        "properties": blake2b_props
    }

    # Method 2: Blake2s(seed)
    blake2s_result = blake2s_hash(seed_bytes)
    blake2s_address = private_key_to_bitcoin_address(blake2s_result)
    blake2s_props = check_special_properties(blake2s_result)

    result["methods"]["blake2s"] = {
        "private_key_hex": blake2s_result.hex(),
        "bitcoin_address": blake2s_address,
        "matches_target": blake2s_address == TARGET_ADDRESS,
        "properties": blake2s_props
    }

    # Method 3: Blake2b(Blake2b(seed))
    blake2b_double = blake2b_hash(blake2b_result)
    blake2b_double_address = private_key_to_bitcoin_address(blake2b_double)
    blake2b_double_props = check_special_properties(blake2b_double)

    result["methods"]["blake2b_double"] = {
        "private_key_hex": blake2b_double.hex(),
        "bitcoin_address": blake2b_double_address,
        "matches_target": blake2b_double_address == TARGET_ADDRESS,
        "properties": blake2b_double_props
    }

    # Method 4: Blake2s(Blake2s(seed))
    blake2s_double = blake2s_hash(blake2s_result)
    blake2s_double_address = private_key_to_bitcoin_address(blake2s_double)
    blake2s_double_props = check_special_properties(blake2s_double)

    result["methods"]["blake2s_double"] = {
        "private_key_hex": blake2s_double.hex(),
        "bitcoin_address": blake2s_double_address,
        "matches_target": blake2s_double_address == TARGET_ADDRESS,
        "properties": blake2s_double_props
    }

    return result


def main():
    """Main execution function."""
    print("=" * 70)
    print("Blake2 Hash Methods Testing Script")
    print("=" * 70)
    print(f"Target Address: {TARGET_ADDRESS}")
    print(f"Start Time: {datetime.now().isoformat()}")
    print()

    # Check dependencies
    if not CRYPTO_AVAILABLE:
        print("ERROR: Required dependencies not available.")
        print("Install with: pip install ecdsa base58")
        return

    # Load seeds
    print(f"Loading seeds from: {SEEDS_FILE}")
    try:
        with open(SEEDS_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Seeds file not found: {SEEDS_FILE}")
        return
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in seeds file: {e}")
        return

    records = data.get("records", [])
    total_seeds = len(records)
    print(f"Loaded {total_seeds} seeds")
    print()

    # Process all seeds
    print("Processing seeds with Blake2 hash methods...")
    print("-" * 70)

    results = {
        "metadata": {
            "target_address": TARGET_ADDRESS,
            "total_seeds": total_seeds,
            "methods_tested": ["blake2b", "blake2s", "blake2b_double", "blake2s_double"],
            "start_time": datetime.now().isoformat(),
            "special_property_criteria": "byte_sum % 121 == 0 AND byte_sum % 19 == 0"
        },
        "target_matches": [],
        "special_property_matches": [],
        "statistics": {
            "blake2b": {"addresses_generated": 0, "target_matches": 0, "special_matches": 0},
            "blake2s": {"addresses_generated": 0, "target_matches": 0, "special_matches": 0},
            "blake2b_double": {"addresses_generated": 0, "target_matches": 0, "special_matches": 0},
            "blake2s_double": {"addresses_generated": 0, "target_matches": 0, "special_matches": 0}
        },
        "sample_results": []
    }

    target_matches = []
    special_matches = []

    for idx, record in enumerate(records):
        seed = record.get("seed", "")
        if not seed:
            continue

        seed_result = process_seed(seed, record.get("id", idx))

        # Check each method for matches
        for method_name, method_result in seed_result["methods"].items():
            if method_result["bitcoin_address"]:
                results["statistics"][method_name]["addresses_generated"] += 1

            # Check for target match
            if method_result["matches_target"]:
                results["statistics"][method_name]["target_matches"] += 1
                match_info = {
                    "seed_id": seed_result["id"],
                    "seed": seed,
                    "method": method_name,
                    "private_key_hex": method_result["private_key_hex"],
                    "bitcoin_address": method_result["bitcoin_address"]
                }
                target_matches.append(match_info)
                print(f"*** TARGET MATCH FOUND! ***")
                print(f"    Seed: {seed}")
                print(f"    Method: {method_name}")
                print(f"    Address: {method_result['bitcoin_address']}")

            # Check for special properties
            if method_result["properties"]["is_special"]:
                results["statistics"][method_name]["special_matches"] += 1
                special_info = {
                    "seed_id": seed_result["id"],
                    "seed": seed,
                    "method": method_name,
                    "private_key_hex": method_result["private_key_hex"],
                    "bitcoin_address": method_result["bitcoin_address"],
                    "byte_sum": method_result["properties"]["byte_sum"]
                }
                special_matches.append(special_info)

        # Store first 100 as samples
        if idx < 100:
            results["sample_results"].append(seed_result)

        # Progress update
        if (idx + 1) % 5000 == 0:
            print(f"Processed {idx + 1:,} / {total_seeds:,} seeds...")

    results["target_matches"] = target_matches
    results["special_property_matches"] = special_matches
    results["metadata"]["end_time"] = datetime.now().isoformat()

    # Summary
    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"Total seeds processed: {total_seeds:,}")
    print()
    print("By Method:")
    for method, stats in results["statistics"].items():
        print(f"  {method}:")
        print(f"    - Addresses generated: {stats['addresses_generated']:,}")
        print(f"    - Target matches: {stats['target_matches']}")
        print(f"    - Special property matches: {stats['special_matches']}")
    print()
    print(f"Total target matches: {len(target_matches)}")
    print(f"Total special property matches: {len(special_matches)}")

    if target_matches:
        print()
        print("TARGET ADDRESS MATCHES:")
        for match in target_matches:
            print(f"  Seed: {match['seed']}")
            print(f"  Method: {match['method']}")
            print(f"  Private Key: {match['private_key_hex']}")
            print()

    if special_matches and len(special_matches) <= 20:
        print()
        print("SPECIAL PROPERTY MATCHES (byte_sum % 121 == 0 AND byte_sum % 19 == 0):")
        for match in special_matches:
            print(f"  Seed ID: {match['seed_id']}")
            print(f"  Seed: {match['seed']}")
            print(f"  Method: {match['method']}")
            print(f"  Byte Sum: {match['byte_sum']}")
            print(f"  Address: {match['bitcoin_address']}")
            print()
    elif special_matches:
        print()
        print(f"SPECIAL PROPERTY MATCHES: {len(special_matches)} found (see JSON for details)")

    # Save results
    print()
    print(f"Saving results to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("Done!")
    print("=" * 70)


if __name__ == "__main__":
    main()
