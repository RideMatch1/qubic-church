#!/usr/bin/env python3
"""
NXT Curve25519 Key Derivation Test Script

Tests all 23,765 Qubic seeds with NXT's Curve25519 method to check for
Bitcoin address matches, specifically targeting 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg.

NXT uses Curve25519 differently from Bitcoin's secp256k1:
- Private key = SHA256(seed)[:32], then clamped for Curve25519
- Public key = Curve25519 scalar multiplication with base point
- Address uses RIPEMD160(SHA256(public_key)) with NXT-specific encoding

This script tests multiple derivation paths:
1. NXT-style Curve25519 derivation
2. SHA256 -> Curve25519 -> Bitcoin address conversion
3. Various clamping and encoding variations
"""

import json
import hashlib
import os
import sys
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

# Target Bitcoin address
TARGET_ADDRESS = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"

# Base58 alphabet for Bitcoin
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58 string."""
    num = int.from_bytes(data, 'big')
    result = ""
    while num > 0:
        num, remainder = divmod(num, 58)
        result = BASE58_ALPHABET[remainder] + result
    # Add leading zeros
    for byte in data:
        if byte == 0:
            result = "1" + result
        else:
            break
    return result


def base58check_encode(version: int, payload: bytes) -> str:
    """Encode with Base58Check (version + payload + checksum)."""
    versioned = bytes([version]) + payload
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58_encode(versioned + checksum)


def ripemd160(data: bytes) -> bytes:
    """Calculate RIPEMD160 hash."""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()


def hash160(data: bytes) -> bytes:
    """SHA256 followed by RIPEMD160."""
    return ripemd160(hashlib.sha256(data).digest())


def clamp_curve25519_private_key(key: bytes) -> bytes:
    """
    Clamp private key for Curve25519 according to the spec.
    - Clear the 3 least significant bits of the first byte
    - Clear the most significant bit of the last byte
    - Set the second-most significant bit of the last byte
    """
    key_array = bytearray(key[:32])
    key_array[0] &= 0xF8   # Clear bits 0, 1, 2
    key_array[31] &= 0x7F  # Clear bit 7
    key_array[31] |= 0x40  # Set bit 6
    return bytes(key_array)


def nxt_clamp_private_key(key: bytes) -> bytes:
    """
    NXT-style private key clamping (slightly different from standard).
    NXT does: key[0] &= 248, key[31] &= 127, key[31] |= 64
    """
    key_array = bytearray(key[:32])
    key_array[0] &= 248   # 0xF8
    key_array[31] &= 127  # 0x7F
    key_array[31] |= 64   # 0x40
    return bytes(key_array)


# Try to import PyNaCl for Curve25519 operations
try:
    import nacl.bindings
    from nacl.bindings import crypto_scalarmult_base, crypto_scalarmult
    NACL_AVAILABLE = True
except ImportError:
    try:
        from nacl.public import PrivateKey
        NACL_AVAILABLE = True
    except ImportError:
        NACL_AVAILABLE = False

# Fallback: Try to use pure Python implementation
if not NACL_AVAILABLE:
    try:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        CRYPTO_AVAILABLE = True
    except ImportError:
        CRYPTO_AVAILABLE = False
else:
    CRYPTO_AVAILABLE = False


def curve25519_public_key_nacl(private_key: bytes) -> Optional[bytes]:
    """Get Curve25519 public key using PyNaCl."""
    try:
        # Ensure 32 bytes
        priv = private_key[:32]
        # Use scalar multiplication with base point
        pub = crypto_scalarmult_base(priv)
        return pub
    except Exception as e:
        return None


def curve25519_public_key_cryptography(private_key: bytes) -> Optional[bytes]:
    """Get Curve25519 public key using cryptography library."""
    try:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives import serialization

        # Create private key from raw bytes
        priv_key = X25519PrivateKey.from_private_bytes(private_key[:32])
        pub_key = priv_key.public_key()

        # Get raw public key bytes
        pub_bytes = pub_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return pub_bytes
    except Exception as e:
        return None


def get_curve25519_public_key(private_key: bytes) -> Optional[bytes]:
    """Get Curve25519 public key using available library."""
    if NACL_AVAILABLE:
        return curve25519_public_key_nacl(private_key)
    elif CRYPTO_AVAILABLE:
        return curve25519_public_key_cryptography(private_key)
    else:
        return None


def curve25519_to_bitcoin_address(public_key: bytes, compressed: bool = True) -> str:
    """
    Convert Curve25519 public key to Bitcoin address.

    Note: This is non-standard since Bitcoin uses secp256k1.
    We're testing if CFB used Curve25519 and then converted to Bitcoin format.
    """
    # Curve25519 public keys are 32 bytes
    if len(public_key) != 32:
        return ""

    # Try different encoding methods
    # Method 1: Direct hash160 of the raw public key
    h160 = hash160(public_key)
    address1 = base58check_encode(0x00, h160)

    return address1


def curve25519_to_bitcoin_compressed(public_key: bytes) -> str:
    """
    Convert Curve25519 public key to Bitcoin address using compressed format.

    Curve25519 uses Montgomery form, we need to convert to a format
    that resembles compressed secp256k1.
    """
    if len(public_key) != 32:
        return ""

    # Prepend 0x02 or 0x03 based on the last bit (simulating compressed pubkey)
    prefix = 0x02 if (public_key[0] & 1) == 0 else 0x03
    compressed = bytes([prefix]) + public_key

    h160 = hash160(compressed)
    return base58check_encode(0x00, h160)


def curve25519_to_bitcoin_uncompressed(public_key: bytes) -> str:
    """
    Convert Curve25519 public key to Bitcoin address using uncompressed format.

    We'll pad to simulate 65-byte uncompressed format.
    """
    if len(public_key) != 32:
        return ""

    # Create pseudo-uncompressed format (0x04 + 32 bytes + 32 bytes padding)
    uncompressed = bytes([0x04]) + public_key + (b'\x00' * 32)

    h160 = hash160(uncompressed)
    return base58check_encode(0x00, h160)


def nxt_derive_keys(seed: str) -> Dict[str, Any]:
    """
    Derive keys using NXT's method.

    NXT derivation:
    1. SHA256(seed) to get 32-byte hash
    2. Clamp the hash for Curve25519
    3. Scalar multiply with base point
    """
    results = {
        "seed": seed,
        "methods_tested": [],
        "addresses": [],
        "match_found": False,
        "matching_method": None,
        "matching_address": None
    }

    # Method 1: SHA256 of seed string (UTF-8 encoded)
    seed_bytes = seed.encode('utf-8')
    sha256_hash = hashlib.sha256(seed_bytes).digest()

    # Method 2: SHA256 of seed as raw bytes if it's hex
    try:
        seed_hex_bytes = bytes.fromhex(seed)
        sha256_hash_hex = hashlib.sha256(seed_hex_bytes).digest()
    except ValueError:
        sha256_hash_hex = None

    # Test various derivation paths
    test_cases = [
        ("sha256_utf8_clamped", clamp_curve25519_private_key(sha256_hash)),
        ("sha256_utf8_nxt_clamped", nxt_clamp_private_key(sha256_hash)),
        ("sha256_utf8_unclamped", sha256_hash),
        ("sha256_utf8_reversed", sha256_hash[::-1]),
        ("sha256_utf8_reversed_clamped", clamp_curve25519_private_key(sha256_hash[::-1])),
    ]

    if sha256_hash_hex:
        test_cases.extend([
            ("sha256_hex_clamped", clamp_curve25519_private_key(sha256_hash_hex)),
            ("sha256_hex_nxt_clamped", nxt_clamp_private_key(sha256_hash_hex)),
            ("sha256_hex_unclamped", sha256_hash_hex),
        ])

    # Also test double SHA256 (used in some Bitcoin derivations)
    double_sha256 = hashlib.sha256(sha256_hash).digest()
    test_cases.extend([
        ("double_sha256_clamped", clamp_curve25519_private_key(double_sha256)),
        ("double_sha256_nxt_clamped", nxt_clamp_private_key(double_sha256)),
    ])

    for method_name, private_key in test_cases:
        public_key = get_curve25519_public_key(private_key)
        if public_key is None:
            continue

        results["methods_tested"].append(method_name)

        # Test different address derivation methods
        address_methods = [
            ("direct", curve25519_to_bitcoin_address(public_key)),
            ("compressed", curve25519_to_bitcoin_compressed(public_key)),
            ("uncompressed", curve25519_to_bitcoin_uncompressed(public_key)),
        ]

        for addr_method, address in address_methods:
            if address:
                full_method = f"{method_name}_{addr_method}"
                results["addresses"].append({
                    "method": full_method,
                    "address": address,
                    "private_key_hex": private_key.hex(),
                    "public_key_hex": public_key.hex()
                })

                if address == TARGET_ADDRESS:
                    results["match_found"] = True
                    results["matching_method"] = full_method
                    results["matching_address"] = address

    return results


def test_all_seeds(seeds_file: str, output_file: str) -> Dict[str, Any]:
    """Test all seeds from the JSON file."""
    print(f"Loading seeds from {seeds_file}...")

    with open(seeds_file, 'r') as f:
        data = json.load(f)

    records = data.get('records', [])
    total_seeds = len(records)

    print(f"Loaded {total_seeds} seeds")
    print(f"Target address: {TARGET_ADDRESS}")
    print(f"NaCl available: {NACL_AVAILABLE}")
    print(f"Cryptography available: {CRYPTO_AVAILABLE}")
    print()

    if not NACL_AVAILABLE and not CRYPTO_AVAILABLE:
        print("ERROR: No Curve25519 library available!")
        print("Please install PyNaCl: pip install pynacl")
        print("Or cryptography: pip install cryptography")
        return {"error": "No Curve25519 library available"}

    results = {
        "timestamp": datetime.now().isoformat(),
        "target_address": TARGET_ADDRESS,
        "total_seeds": total_seeds,
        "seeds_tested": 0,
        "matches_found": 0,
        "library_used": "nacl" if NACL_AVAILABLE else "cryptography",
        "matches": [],
        "sample_results": [],  # Store first few results as examples
        "cfb_prefix_results": [],  # Store all CFB-prefix results
        "address_statistics": {}
    }

    # Track unique addresses generated
    all_addresses = set()
    cfb_addresses = []

    print("Testing seeds with NXT Curve25519 derivation...")

    for i, record in enumerate(records):
        seed = record.get('seed', '')
        if not seed:
            continue

        result = nxt_derive_keys(seed)
        results["seeds_tested"] += 1

        # Collect addresses
        for addr_info in result["addresses"]:
            addr = addr_info["address"]
            all_addresses.add(addr)

            # Check for CFB prefix
            if addr.startswith("1CFB"):
                cfb_addresses.append({
                    "seed": seed,
                    "address": addr,
                    "method": addr_info["method"],
                    "private_key": addr_info["private_key_hex"],
                    "public_key": addr_info["public_key_hex"]
                })

        if result["match_found"]:
            results["matches_found"] += 1
            results["matches"].append({
                "seed": seed,
                "seed_index": i,
                "method": result["matching_method"],
                "address": result["matching_address"],
                "documented_identity": record.get("documentedIdentity", ""),
                "real_identity": record.get("realIdentity", ""),
                "source": record.get("source", "")
            })
            print(f"\n*** MATCH FOUND! ***")
            print(f"Seed: {seed}")
            print(f"Method: {result['matching_method']}")
            print(f"Address: {result['matching_address']}")

        # Store first 10 results as examples
        if i < 10:
            results["sample_results"].append({
                "seed": seed,
                "methods_tested": result["methods_tested"],
                "addresses_generated": len(result["addresses"]),
                "sample_addresses": [a["address"] for a in result["addresses"][:3]]
            })

        # Progress update
        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1}/{total_seeds} seeds... ({len(all_addresses)} unique addresses, {len(cfb_addresses)} CFB-prefix)")

    # Store CFB prefix results
    results["cfb_prefix_results"] = cfb_addresses

    # Calculate statistics
    results["address_statistics"] = {
        "unique_addresses_generated": len(all_addresses),
        "cfb_prefix_count": len(cfb_addresses),
        "prefix_distribution": {}
    }

    # Count address prefixes
    prefix_counts = {}
    for addr in all_addresses:
        prefix = addr[:4] if len(addr) >= 4 else addr
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

    # Get top 20 prefixes
    sorted_prefixes = sorted(prefix_counts.items(), key=lambda x: -x[1])[:20]
    results["address_statistics"]["prefix_distribution"] = dict(sorted_prefixes)

    # Save results
    print(f"\nSaving results to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    return results


def test_specific_seeds():
    """Test some specific seeds that might be interesting."""
    interesting_seeds = [
        "cfb",
        "CFB",
        "1CFB",
        "satoshi",
        "nakamoto",
        "bitcoin",
        "genesis",
        "bridge",
        "qubic",
        "QUBIC",
        "aigarth",
        "anna",
        "jinn",
        "iota",
        "come-from-beyond",
        "nxt",
        "NXT",
    ]

    print("\n" + "="*60)
    print("Testing interesting seed values:")
    print("="*60)

    results = []
    for seed in interesting_seeds:
        result = nxt_derive_keys(seed)
        print(f"\nSeed: '{seed}'")
        for addr_info in result["addresses"][:3]:  # Show first 3 addresses
            print(f"  {addr_info['method']}: {addr_info['address']}")

        results.append({
            "seed": seed,
            "addresses": [a["address"] for a in result["addresses"]]
        })

        if result["match_found"]:
            print(f"  *** MATCH FOUND: {result['matching_method']} ***")

    return results


def main():
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    seeds_file = os.path.join(script_dir, "..", "public", "data", "qubic-seeds.json")
    output_file = os.path.join(script_dir, "NXT_CURVE25519_RESULTS.json")

    print("="*70)
    print("NXT Curve25519 Key Derivation Test")
    print("="*70)
    print(f"Script: {__file__}")
    print(f"Seeds file: {seeds_file}")
    print(f"Output file: {output_file}")
    print(f"Target: {TARGET_ADDRESS}")
    print("="*70)
    print()

    # First test interesting seeds
    specific_results = test_specific_seeds()

    # Then test all seeds from the file
    print("\n" + "="*70)
    print("Testing all seeds from qubic-seeds.json")
    print("="*70)

    results = test_all_seeds(seeds_file, output_file)

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total seeds tested: {results.get('seeds_tested', 0)}")
    print(f"Unique addresses generated: {results.get('address_statistics', {}).get('unique_addresses_generated', 0)}")
    print(f"Matches found for target: {results.get('matches_found', 0)}")
    print(f"CFB-prefix addresses found: {len(results.get('cfb_prefix_results', []))}")

    if results.get("matches"):
        print("\n*** MATCHES ***")
        for match in results["matches"]:
            print(f"  Seed: {match['seed']}")
            print(f"  Method: {match['method']}")
            print(f"  Index: {match['seed_index']}")

    if results.get("cfb_prefix_results"):
        print("\n*** CFB-PREFIX ADDRESSES ***")
        for cfb in results["cfb_prefix_results"][:10]:  # Show first 10
            print(f"  {cfb['address']} <- {cfb['seed'][:30]}... ({cfb['method']})")
        if len(results["cfb_prefix_results"]) > 10:
            print(f"  ... and {len(results['cfb_prefix_results']) - 10} more")

    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    main()
