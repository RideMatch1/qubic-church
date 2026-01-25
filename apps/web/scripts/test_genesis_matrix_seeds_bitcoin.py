#!/usr/bin/env python3
"""
TEST GENESIS MATRIX SEEDS AGAINST BITCOIN ADDRESSES

Test the 3 Genesis Matrix seeds directly against all 11 Genesis Bitcoin addresses:
1. genesis_diagonal
2. genesis_row
3. genesis_col

These seeds come from Anna Matrix position (41, 29) - the Genesis position!
"""

import json
import hashlib
import ecdsa
import base58
from Crypto.Hash import keccak
from pathlib import Path

# ============================================================================
# GENESIS MATRIX SEEDS (from qubic-mystery-lab)
# ============================================================================

GENESIS_MATRIX_SEEDS = {
    "genesis_diagonal": "zkrzcquacawcewyajgdbquosgsturmdnpglzomfgjwtxzxzvzhjxzpn",
    "genesis_row": "zhvvuuuuocccgynuggzuqgtcecycqgrjnsffgwaweiwsoazygifbbkl",
    "genesis_col": "znrtdmddvhddthrnvpvtjhhfzxzhxnvjzpzppnllzzbhzntpzpzpppj",
}

# ============================================================================
# TARGET GENESIS ADDRESSES
# ============================================================================

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

# ============================================================================
# BITCOIN ADDRESS DERIVATION
# ============================================================================

def k12_hash(data: bytes) -> bytes:
    """K12-like hash using Keccak"""
    k = keccak.new(digest_bits=256)
    k.update(data)
    return k.digest()

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
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        return b'\x04' + vk.to_string()

def public_key_to_address(pubkey: bytes) -> str:
    """Convert public key to Bitcoin address"""
    h160 = hash160(pubkey)
    versioned = b'\x00' + h160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    address = base58.b58encode(versioned + checksum).decode('ascii')
    return address

def derive_bitcoin_address(seed: str, method: str, xor_val: int = 0, compressed: bool = False):
    """Derive Bitcoin address from seed"""
    try:
        seed_bytes = seed[:55].encode('utf-8')  # Use first 55 chars

        # Apply hash based on method
        if method == 'k12':
            hash_result = k12_hash(seed_bytes)
        elif method == 'k12_double':
            hash_result = k12_hash(k12_hash(seed_bytes))
        elif method == 'keccak':
            k = keccak.new(digest_bits=256)
            k.update(seed_bytes)
            hash_result = k.digest()
        elif method == 'sha256':
            hash_result = hashlib.sha256(seed_bytes).digest()
        elif method == 'sha256_double':
            hash_result = hashlib.sha256(hashlib.sha256(seed_bytes).digest()).digest()
        elif method.startswith('step'):
            step = int(method.replace('step', ''))
            k = keccak.new(digest_bits=256)
            k.update(seed_bytes)
            temp = k.digest()
            hash_result = bytes([temp[i % len(temp)] for i in range(0, len(temp), step)])[:32]
            if len(hash_result) < 32:
                hash_result = hash_result + b'\x00' * (32 - len(hash_result))
        else:
            return None

        # Apply XOR
        if xor_val != 0:
            hash_result = bytes([b ^ xor_val for b in hash_result])

        private_key = hash_result[:32]
        public_key = private_key_to_public_key(private_key, compressed=compressed)
        address = public_key_to_address(public_key)

        return address
    except:
        return None

# ============================================================================
# TESTING
# ============================================================================

def test_genesis_matrix_seeds():
    """Test all 3 Genesis Matrix seeds against all 11 addresses"""
    print("=" * 80)
    print("🔍 TESTING GENESIS MATRIX SEEDS AGAINST BITCOIN ADDRESSES")
    print("=" * 80)
    print()

    print(f"📊 Configuration:")
    print(f"   Matrix seeds: {len(GENESIS_MATRIX_SEEDS)}")
    print(f"   Target addresses: {len(TARGET_ADDRESSES)}")
    print(f"   Methods: k12, k12_double, keccak, sha256, sha256_double, step7, step13, step19, step27, step33, step121")
    print(f"   XOR values: 0, 7, 11, 13, 19, 27, 33, 121")
    print(f"   Compressed: True/False")
    print()

    target_set = set(TARGET_ADDRESSES.values())
    matches = []

    methods = ['k12', 'k12_double', 'keccak', 'sha256', 'sha256_double',
               'step7', 'step13', 'step19', 'step27', 'step33', 'step121']
    xor_values = [0, 7, 11, 13, 19, 27, 33, 121]

    tests_run = 0
    total_tests = len(GENESIS_MATRIX_SEEDS) * len(methods) * len(xor_values) * 2

    print(f"⚡ Total tests: {total_tests}")
    print(f"🚀 Starting...\n")

    for seed_name, seed in GENESIS_MATRIX_SEEDS.items():
        print(f"\n{'='*80}")
        print(f"Testing: {seed_name}")
        print(f"Seed: {seed[:40]}...")
        print(f"{'='*80}\n")

        for method in methods:
            for xor_val in xor_values:
                for compressed in [False, True]:
                    tests_run += 1

                    address = derive_bitcoin_address(seed, method, xor_val, compressed)

                    if address and address in target_set:
                        # MATCH FOUND!
                        target_name = None
                        for name, addr in TARGET_ADDRESSES.items():
                            if addr == address:
                                target_name = name
                                break

                        match_info = {
                            'seed_name': seed_name,
                            'seed': seed,
                            'method': method,
                            'xor_value': xor_val,
                            'compressed': compressed,
                            'address': address,
                            'target': target_name,
                        }
                        matches.append(match_info)

                        print(f"\n🎉🎉🎉 MATCH FOUND! 🎉🎉🎉")
                        print(f"   Seed name: {seed_name}")
                        print(f"   Target: {target_name}")
                        print(f"   Address: {address}")
                        print(f"   Method: {method}")
                        print(f"   XOR: {xor_val}")
                        print(f"   Compressed: {compressed}")
                        print(f"   {'='*80}\n")

                    if tests_run % 100 == 0:
                        progress = (tests_run / total_tests) * 100
                        print(f"\rProgress: {progress:.1f}% ({tests_run}/{total_tests}) | Matches: {len(matches)}", end='', flush=True)

    # Results
    print(f"\n\n{'='*80}")
    print(f"✅ TESTING COMPLETE!")
    print(f"{'='*80}\n")

    print(f"📊 Statistics:")
    print(f"   Total tests: {tests_run}")
    print(f"   Matches found: {len(matches)}\n")

    if matches:
        print(f"🔑 MATCHES DETAILS:\n")
        for i, match in enumerate(matches, 1):
            print(f"Match #{i}:")
            print(f"   Seed: {match['seed_name']}")
            print(f"   Target: {match['target']}")
            print(f"   Address: {match['address']}")
            print(f"   Method: {match['method']}")
            print(f"   XOR: {match['xor_value']}")
            print(f"   Compressed: {match['compressed']}")
            print()

        # Save
        output_file = Path("genesis_matrix_seed_matches.json")
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': str(Path(__file__).stat().st_mtime),
                'tests_run': tests_run,
                'matches_count': len(matches),
                'matches': matches
            }, f, indent=2)

        print(f"💾 Results saved to: {output_file}")
    else:
        print(f"⚠️  No matches found")
        print(f"\nThis means:")
        print(f"   - Genesis Matrix seeds ≠ Bitcoin private keys (direct)")
        print(f"   - Need different transformation")
        print(f"   - OR seeds are in Batch 24+")
        print(f"   - OR Time-Lock is active until March 3, 2026")

    print(f"\n{'='*80}")

if __name__ == "__main__":
    test_genesis_matrix_seeds()
