#!/usr/bin/env python3
"""
COMPREHENSIVE GENESIS ADDRESS SEED FINDER

Test ALL 23,765 Qubic seeds against ALL 11 Genesis addresses using
multiple derivation methods to find which seeds generate which addresses.

Target: 550 BTC (~$22M USD)
- 10 × 50 BTC addresses (Blocks 73-121)
- 1 × 1CFB address (Block 264)
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Crypto imports
import ecdsa
import base58
from Crypto.Hash import keccak

# ============================================================================
# CONFIGURATION
# ============================================================================

# The 11 target Genesis addresses
TARGET_ADDRESSES = {
    "Block_73": "1Ky8dP7oR1cBeg1MzkrgHAeHAHyn92DCar",
    "Block_74": "1FnbdYntfohuZ1EhZ7f9oiT2R5sDsZBohL",
    "Block_75": "14U5EYTN54agAngQu92D9gESvHYfKw8EqA",
    "Block_80": "1BwWdLV5wbnZvSYfNA8zaEMqEDDjvA99wX",  # XOR=27!
    "Block_89": "1KSHc1tmsUhS9f1TD6RHR8Kmwg9Zv8WhCt",
    "Block_93": "1LNV5xnjneJwXc6jN8X2co586gjiSz6asS",
    "Block_95": "18GyZ216oMhpCbZ7JkKZyT8x68v2a8HuNA",
    "Block_96": "12XPHPCGYz1WgRhquiAfVeAyjZ7Gbdpih3",
    "Block_120": "1FeGetWU2tR2QSrxnpRwHGXGcxzhN6zQza",
    "Block_121": "1B7CyZF8e6TYzhNBSHy8yYuTRJNpMtNChg",  # Block=121=11²!
    "Block_264_1CFB": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",  # First byte=0x79=121!
}

# Transformation methods to test
METHODS = [
    'k12',
    'k12_double',
    'keccak',
    'keccak_double',
    'sha256',
    'sha256_double',
    'sha3_256',
    'step7',
    'step13',
    'step19',
    'step27',
    'step33',
    'step121',
]

# XOR values to test
XOR_VALUES = [0, 7, 11, 13, 19, 27, 33, 121]

# ============================================================================
# K12-LIKE HASH FUNCTION (using Keccak as approximation)
# ============================================================================

def k12_hash(data: bytes) -> bytes:
    """
    K12-like hash using Keccak (KangarooTwelve approximation).
    K12 is based on Keccak-p[1600,12].
    """
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

def k12_double_hash(data: bytes) -> bytes:
    """K12(K12(data)) - double hashing"""
    return k12_hash(k12_hash(data))

# ============================================================================
# BITCOIN ADDRESS DERIVATION
# ============================================================================

def hash160(data: bytes) -> bytes:
    """Bitcoin Hash160: RIPEMD160(SHA256(data))"""
    sha = hashlib.sha256(data).digest()
    ripemd = hashlib.new('ripemd160')
    ripemd.update(sha)
    return ripemd.digest()

def private_key_to_public_key(private_key: bytes, compressed: bool = False) -> bytes:
    """Convert private key to public key using secp256k1"""
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()

    if compressed:
        # Compressed public key (33 bytes)
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        # Uncompressed public key (65 bytes)
        return b'\x04' + vk.to_string()

def public_key_to_address(pubkey: bytes) -> str:
    """Convert public key to Bitcoin address"""
    # Hash160 of public key
    h160 = hash160(pubkey)

    # Add version byte (0x00 for mainnet)
    versioned = b'\x00' + h160

    # Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

    # Base58Check encode
    address = base58.b58encode(versioned + checksum).decode('ascii')

    return address

def derive_bitcoin_address_from_seed(seed: str, method: str, xor_value: int = 0,
                                     compressed: bool = False) -> Optional[str]:
    """
    Derive Bitcoin address from Qubic seed using specified method.

    Args:
        seed: 55-character Qubic seed (lowercase a-z)
        method: Derivation method (k12, keccak, sha256, step7, etc.)
        xor_value: XOR value to apply (0-255)
        compressed: Use compressed public key

    Returns:
        Bitcoin address or None if derivation fails
    """
    try:
        seed_bytes = seed.encode('utf-8')

        # Apply hash function based on method
        if method == 'k12':
            hash_result = k12_hash(seed_bytes)
        elif method == 'k12_double':
            hash_result = k12_double_hash(seed_bytes)
        elif method == 'keccak':
            k = keccak.new(digest_bits=256)
            k.update(seed_bytes)
            hash_result = k.digest()
        elif method == 'keccak_double':
            k = keccak.new(digest_bits=256)
            k.update(seed_bytes)
            temp = k.digest()
            k = keccak.new(digest_bits=256)
            k.update(temp)
            hash_result = k.digest()
        elif method == 'sha256':
            hash_result = hashlib.sha256(seed_bytes).digest()
        elif method == 'sha256_double':
            hash_result = hashlib.sha256(hashlib.sha256(seed_bytes).digest()).digest()
        elif method == 'sha3_256':
            hash_result = hashlib.sha3_256(seed_bytes).digest()
        elif method.startswith('step'):
            # Step transformation: hash then take every Nth byte
            step = int(method.replace('step', ''))
            k = keccak.new(digest_bits=256)
            k.update(seed_bytes)
            temp = k.digest()
            # Take every step-th byte and repeat to fill 32 bytes
            hash_result = bytes([temp[i % len(temp)] for i in range(0, len(temp), step)])[:32]
            if len(hash_result) < 32:
                hash_result = hash_result + b'\x00' * (32 - len(hash_result))
        else:
            return None

        # Apply XOR if specified
        if xor_value != 0:
            hash_result = bytes([b ^ xor_value for b in hash_result])

        # Ensure we have 32 bytes for private key
        private_key = hash_result[:32]

        # Derive public key
        public_key = private_key_to_public_key(private_key, compressed=compressed)

        # Derive address
        address = public_key_to_address(public_key)

        return address

    except Exception as e:
        # Silently fail on errors (some seeds might not produce valid keys)
        return None

# ============================================================================
# SEED LOADING
# ============================================================================

def load_qubic_seeds() -> List[Dict]:
    """Load all 23,765 Qubic seeds from JSON file"""
    seeds_file = Path("../public/data/qubic-seeds.json")

    if not seeds_file.exists():
        print(f"❌ Seeds file not found: {seeds_file}")
        return []

    with open(seeds_file) as f:
        data = json.load(f)

    seeds = data.get('records', [])
    print(f"✅ Loaded {len(seeds):,} Qubic seeds")

    return seeds

# ============================================================================
# COMPREHENSIVE TESTING
# ============================================================================

def test_all_seeds_all_methods():
    """
    Test ALL seeds against ALL methods against ALL target addresses.
    This is the main comprehensive testing function.
    """
    print("=" * 80)
    print("🔍 COMPREHENSIVE GENESIS ADDRESS SEED FINDER")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Target addresses: {len(TARGET_ADDRESSES)}")
    print(f"   Methods to test: {len(METHODS)}")
    print(f"   XOR values: {len(XOR_VALUES)}")
    print(f"   Compressed variants: 2 (True/False)")
    print(f"   Total combinations per seed: {len(METHODS) * len(XOR_VALUES) * 2}")

    # Load seeds
    print(f"\n📂 Loading seeds...")
    seeds = load_qubic_seeds()

    if not seeds:
        print("❌ No seeds loaded. Exiting.")
        return

    total_tests = len(seeds) * len(METHODS) * len(XOR_VALUES) * 2
    print(f"\n⚡ Total tests to run: {total_tests:,}")
    print(f"   Estimated time: ~{total_tests / 1000:.1f} seconds (~{total_tests / 60000:.1f} minutes)")

    # Create reverse lookup for fast matching
    target_set = set(TARGET_ADDRESSES.values())

    # Results storage
    matches = []

    # Progress tracking
    start_time = time.time()
    tests_run = 0
    last_report = 0

    print(f"\n🚀 Starting comprehensive testing...")
    print(f"   {'=' * 78}")

    # Main testing loop
    for seed_idx, seed_record in enumerate(seeds):
        seed = seed_record.get('seed', '')

        if not seed or len(seed) != 55:
            continue

        # Test all methods
        for method in METHODS:
            for xor_val in XOR_VALUES:
                for compressed in [False, True]:
                    tests_run += 1

                    # Derive address
                    address = derive_bitcoin_address_from_seed(
                        seed, method, xor_val, compressed
                    )

                    # Check if it matches any target
                    if address and address in target_set:
                        # MATCH FOUND!
                        # Find which target
                        target_name = None
                        for name, addr in TARGET_ADDRESSES.items():
                            if addr == address:
                                target_name = name
                                break

                        match_info = {
                            'seed': seed,
                            'seed_index': seed_idx,
                            'method': method,
                            'xor_value': xor_val,
                            'compressed': compressed,
                            'address': address,
                            'target': target_name,
                            'timestamp': time.time() - start_time,
                        }
                        matches.append(match_info)

                        print(f"\n🎉 MATCH FOUND! #{len(matches)}")
                        print(f"   Target: {target_name}")
                        print(f"   Address: {address}")
                        print(f"   Seed: {seed[:20]}...")
                        print(f"   Method: {method}")
                        print(f"   XOR: {xor_val}")
                        print(f"   Compressed: {compressed}")
                        print(f"   {'=' * 78}")

                    # Progress reporting (every 10000 tests)
                    if tests_run - last_report >= 10000:
                        elapsed = time.time() - start_time
                        tests_per_sec = tests_run / elapsed if elapsed > 0 else 0
                        progress = (tests_run / total_tests) * 100
                        remaining = (total_tests - tests_run) / tests_per_sec if tests_per_sec > 0 else 0

                        print(f"\r   Progress: {progress:.1f}% ({tests_run:,}/{total_tests:,}) | "
                              f"{tests_per_sec:.0f} tests/sec | "
                              f"ETA: {remaining/60:.1f}min | "
                              f"Matches: {len(matches)}", end='', flush=True)

                        last_report = tests_run

    # Final results
    elapsed = time.time() - start_time
    print(f"\n\n{'=' * 80}")
    print(f"✅ TESTING COMPLETE!")
    print(f"{'=' * 80}")
    print(f"\n📊 Statistics:")
    print(f"   Total tests run: {tests_run:,}")
    print(f"   Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"   Average speed: {tests_run/elapsed:.0f} tests/second")
    print(f"\n🎯 Results:")
    print(f"   Matches found: {len(matches)}")

    if matches:
        print(f"\n🔑 MATCHES DETAILS:")
        for i, match in enumerate(matches, 1):
            print(f"\n   Match #{i}:")
            print(f"      Target: {match['target']}")
            print(f"      Address: {match['address']}")
            print(f"      Seed: {match['seed']}")
            print(f"      Method: {match['method']}")
            print(f"      XOR: {match['xor_value']}")
            print(f"      Compressed: {match['compressed']}")

        # Save matches to file
        output_file = Path("genesis_seed_matches.json")
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'total_tests': tests_run,
                'elapsed_seconds': elapsed,
                'matches_count': len(matches),
                'matches': matches
            }, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")
    else:
        print(f"\n⚠️  No matches found in this test run.")
        print(f"   Possible reasons:")
        print(f"   1. Seeds are in Batch 24+ (not in our dataset)")
        print(f"   2. Different hash function needed (real K12 vs approximation)")
        print(f"   3. Additional transformation steps required")
        print(f"   4. Time-Lock is active (wait until March 3, 2026)")

    print(f"\n{'=' * 80}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        test_all_seeds_all_methods()
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
