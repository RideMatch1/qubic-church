#!/usr/bin/env python3
"""
P=NP ADVANCED Key Hunter
========================

Testing more sophisticated hypotheses based on:
1. The "Address as Nonce" theory (Sergio Lerner)
2. The 6-day mining mystery
3. Iterative hash chains
4. Public key revelation attack vector
"""

import hashlib
import json
import itertools
from typing import List, Tuple, Optional

try:
    import ecdsa
    from ecdsa import SECP256k1
    import base58
except ImportError:
    print("Run: pip3 install ecdsa base58")
    exit(1)


# ============================================================================
# CONSTANTS
# ============================================================================

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
GENESIS_BLOCK_HASH = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
GENESIS_MERKLE_ROOT = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
GENESIS_TIMESTAMP = 1231006505
GENESIS_NONCE = 2083236893
BLOCK_1_TIMESTAMP = 1231469665  # 6 days later
SIX_DAYS_SECONDS = BLOCK_1_TIMESTAMP - GENESIS_TIMESTAMP  # 463160 seconds

# The public key of Genesis address (from blockchain)
# This is revealed when coins are spent - Genesis coins were never spent!
# So we're looking for the private key that generates THIS public key
GENESIS_PUBKEY_HEX = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def double_sha256(data: bytes) -> bytes:
    return sha256(sha256(data))

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data: bytes) -> bytes:
    return ripemd160(sha256(data))

def private_to_public(priv_hex: str, compressed: bool = False) -> bytes:
    """Convert private key to public key"""
    try:
        priv_bytes = bytes.fromhex(priv_hex)
        if len(priv_bytes) != 32:
            return b''
        sk = ecdsa.SigningKey.from_string(priv_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        if compressed:
            x = vk.pubkey.point.x()
            y = vk.pubkey.point.y()
            prefix = b'\x02' if y % 2 == 0 else b'\x03'
            return prefix + x.to_bytes(32, 'big')
        else:
            return b'\x04' + vk.to_string()
    except:
        return b''

def public_to_address(pub: bytes) -> str:
    """Convert public key to Bitcoin address"""
    h160 = hash160(pub)
    versioned = b'\x00' + h160
    checksum = double_sha256(versioned)[:4]
    return base58.b58encode(versioned + checksum).decode()

def test_key(priv_hex: str, target_addr: str = GENESIS_ADDRESS) -> Tuple[bool, str, str]:
    """Test if a private key generates the target address"""
    # Test both compressed and uncompressed
    pub_uncompressed = private_to_public(priv_hex, compressed=False)
    pub_compressed = private_to_public(priv_hex, compressed=True)

    if pub_uncompressed:
        addr_u = public_to_address(pub_uncompressed)
        if addr_u == target_addr:
            return True, addr_u, "uncompressed"

    if pub_compressed:
        addr_c = public_to_address(pub_compressed)
        if addr_c == target_addr:
            return True, addr_c, "compressed"

    addr = addr_u if pub_uncompressed else ""
    return False, addr, ""


# ============================================================================
# ADVANCED TESTS
# ============================================================================

def test_iterative_hashing():
    """
    Test iterative hashing - maybe the key is SHA256^n of something
    """
    print("\n[TEST] Iterative Hashing (SHA256^n)")

    seeds = [
        b"satoshi",
        b"bitcoin",
        b"genesis",
        b"nakamoto",
        GENESIS_MERKLE_ROOT.encode(),
        b"The Times 03/Jan/2009 Chancellor on brink of second bailout for banks",
        b"20082034",
    ]

    for seed in seeds:
        current = seed
        for i in range(1, 1001):  # Test up to 1000 iterations
            current = sha256(current)
            if i in [1, 2, 3, 6, 7, 27, 42, 43, 100, 145, 256, 512, 1000]:
                key = current.hex()
                match, addr, key_type = test_key(key)
                if match:
                    print(f"  ✓ MATCH! SHA256^{i}({seed[:20]}...) = {addr}")
                    return key
                if i <= 3:
                    print(f"  SHA256^{i}({seed[:15].decode('utf-8', errors='ignore')}...) -> {addr[:15]}...")


def test_six_day_mystery():
    """
    The Genesis block took 6 days - test time-based keys
    Block 0: 2009-01-03 18:15:05
    Block 1: 2009-01-09 02:54:25
    """
    print("\n[TEST] 6-Day Mining Mystery")

    # Various interpretations of "6 days"
    test_values = [
        6,
        6 * 24,  # 144 hours
        6 * 24 * 60,  # 8640 minutes
        6 * 24 * 60 * 60,  # 518400 seconds
        SIX_DAYS_SECONDS,  # Actual: 463160
        BLOCK_1_TIMESTAMP - GENESIS_TIMESTAMP,
        GENESIS_TIMESTAMP,
        BLOCK_1_TIMESTAMP,
    ]

    for val in test_values:
        # Direct as key
        key1 = hex(val)[2:].zfill(64)
        match1, addr1, _ = test_key(key1)
        if match1:
            print(f"  ✓ MATCH! Value {val} direct")
            return key1

        # SHA256 of value
        key2 = sha256(str(val).encode()).hex()
        match2, addr2, _ = test_key(key2)
        if match2:
            print(f"  ✓ MATCH! SHA256({val})")
            return key2

        print(f"  {val} -> {addr1[:20]}... / SHA256 -> {addr2[:20]}...")


def test_nonce_overflow_hypothesis():
    """
    Sergio Lerner noted: Extra nonce = 4, but should be ~2048 for 6 days
    The 500x discrepancy suggests something special about how the nonce was used
    """
    print("\n[TEST] Nonce Overflow Hypothesis (Sergio Lerner)")

    expected_overflows = 2048  # For 6 days of mining
    actual_extra_nonce = 4
    ratio = expected_overflows // actual_extra_nonce  # 512

    test_values = [
        4,  # Actual extra nonce
        2048,  # Expected
        512,  # Ratio
        4 * 2**32,  # 4 full nonce cycles
        GENESIS_NONCE,
        GENESIS_NONCE * 4,
        GENESIS_NONCE ^ 4,  # XOR with extra nonce
    ]

    for val in test_values:
        key = sha256(str(val).encode()).hex()
        match, addr, _ = test_key(key)
        if match:
            print(f"  ✓ MATCH! Value {val}")
            return key
        print(f"  {val} -> {addr[:20]}...")


def test_address_as_nonce():
    """
    Sergio's hypothesis: The Genesis address itself might have been
    used as a nonce during mining, not as a real destination
    """
    print("\n[TEST] Address-as-Nonce Hypothesis")

    # Decode Genesis address
    decoded = base58.b58decode(GENESIS_ADDRESS)
    hash160_bytes = decoded[1:-4]  # Remove version and checksum

    tests = [
        ("Hash160 direct", hash160_bytes.hex().zfill(64)),
        ("Hash160 reversed", hash160_bytes[::-1].hex().zfill(64)),
        ("SHA256(Hash160)", sha256(hash160_bytes).hex()),
        ("SHA256(address string)", sha256(GENESIS_ADDRESS.encode()).hex()),
        ("Double SHA256(address)", double_sha256(GENESIS_ADDRESS.encode()).hex()),
    ]

    for name, key in tests:
        match, addr, _ = test_key(key)
        if match:
            print(f"  ✓ MATCH! {name}")
            return key
        print(f"  {name} -> {addr[:25]}...")


def test_public_key_derivation():
    """
    The P=NP argument: If public key is known, private key can be found
    Genesis public key is in the blockchain but coins were never spent,
    so it was never "revealed" to casual observers

    Let's see if there's a pattern in the public key itself
    """
    print("\n[TEST] Public Key Analysis")

    pubkey_bytes = bytes.fromhex(GENESIS_PUBKEY_HEX[2:])  # Remove 04 prefix

    # Extract X and Y coordinates
    x_coord = pubkey_bytes[:32]
    y_coord = pubkey_bytes[32:]

    print(f"  X coordinate: {x_coord.hex()[:32]}...")
    print(f"  Y coordinate: {y_coord.hex()[:32]}...")

    # Test if coordinates have special properties
    tests = [
        ("SHA256(X)", sha256(x_coord).hex()),
        ("SHA256(Y)", sha256(y_coord).hex()),
        ("SHA256(X XOR Y)", sha256(bytes(a ^ b for a, b in zip(x_coord, y_coord))).hex()),
        ("X reversed as key", x_coord[::-1].hex()),
    ]

    for name, key in tests:
        match, addr, _ = test_key(key)
        if match:
            print(f"  ✓ MATCH! {name}")
            return key
        print(f"  {name} -> {addr[:25]}...")


def test_biblical_references():
    """
    Genesis = creation, 6 days of work + 1 day rest
    43 zero bits (special difficulty)
    """
    print("\n[TEST] Biblical/Symbolic References")

    phrases = [
        "In the beginning God created the heaven and the earth",
        "Let there be light",
        "And there was light",
        "Genesis 1:1",
        "Bereshit",  # Hebrew for Genesis
        "6 days of creation",
        "On the seventh day he rested",
        "43",  # Extra zero bits
        "27",  # CFB's favorite number
        "145",  # Another significant number
    ]

    for phrase in phrases:
        key = sha256(phrase.encode()).hex()
        match, addr, _ = test_key(key)
        if match:
            print(f"  ✓ MATCH! '{phrase}'")
            return key
        print(f"  '{phrase[:25]}...' -> {addr[:20]}...")


def test_combined_genesis_data():
    """
    Test combinations of all Genesis block data
    """
    print("\n[TEST] Combined Genesis Data")

    # Concatenate and hash various combinations
    components = [
        bytes.fromhex(GENESIS_BLOCK_HASH),
        bytes.fromhex(GENESIS_MERKLE_ROOT),
        GENESIS_TIMESTAMP.to_bytes(4, 'little'),
        GENESIS_NONCE.to_bytes(4, 'little'),
        b'\x04',  # Extra nonce
    ]

    # Test various combinations
    for r in range(2, len(components) + 1):
        for combo in itertools.combinations(range(len(components)), r):
            data = b''.join(components[i] for i in combo)
            key = sha256(data).hex()
            match, addr, _ = test_key(key)
            if match:
                print(f"  ✓ MATCH! Combination {combo}")
                return key

    # Also test XOR combinations
    print("  Testing XOR combinations...")
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            c1, c2 = components[i], components[j]
            min_len = min(len(c1), len(c2))
            xor_result = bytes(a ^ b for a, b in zip(c1[:min_len], c2[:min_len]))
            key = sha256(xor_result).hex()
            match, addr, _ = test_key(key)
            if match:
                print(f"  ✓ MATCH! XOR of components {i} and {j}")
                return key

    print("  No match in combinations")


def brute_force_short_keys():
    """
    What if Satoshi used a "weak" key intentionally?
    Test keys with many leading zeros or simple patterns
    """
    print("\n[TEST] Weak/Pattern Keys (limited search)")

    # Keys with many leading zeros
    for i in range(1, 1000):
        key = hex(i)[2:].zfill(64)
        match, addr, _ = test_key(key)
        if match:
            print(f"  ✓ MATCH! Small number: {i}")
            return key

    # Keys that are repeated bytes
    for byte_val in range(256):
        key = (chr(byte_val) * 32).encode().hex()[:64]
        if len(key) == 64:
            match, addr, _ = test_key(key)
            if match:
                print(f"  ✓ MATCH! Repeated byte: {byte_val}")
                return key

    print("  No weak key patterns found")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("P=NP ADVANCED KEY HUNTER")
    print("Testing sophisticated hypotheses based on Sergio Lerner's research")
    print("=" * 70)
    print(f"\nTarget: {GENESIS_ADDRESS}")
    print(f"Genesis Public Key: {GENESIS_PUBKEY_HEX[:40]}...")

    results = {
        "target": GENESIS_ADDRESS,
        "tests_run": [],
        "matches": []
    }

    tests = [
        ("Iterative Hashing", test_iterative_hashing),
        ("6-Day Mystery", test_six_day_mystery),
        ("Nonce Overflow", test_nonce_overflow_hypothesis),
        ("Address as Nonce", test_address_as_nonce),
        ("Public Key Analysis", test_public_key_derivation),
        ("Biblical References", test_biblical_references),
        ("Combined Data", test_combined_genesis_data),
        ("Weak Keys", brute_force_short_keys),
    ]

    for name, test_func in tests:
        try:
            result = test_func()
            results["tests_run"].append(name)
            if result:
                results["matches"].append({"test": name, "key": result})
                print(f"\n🎉 FOUND KEY IN {name}!")
                break
        except Exception as e:
            print(f"  Error in {name}: {e}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if results["matches"]:
        print("\n✓ PRIVATE KEY FOUND!")
        for m in results["matches"]:
            print(f"  Test: {m['test']}")
            print(f"  Key:  {m['key']}")
    else:
        print("\n✗ No private key found with current hypotheses")
        print("\nPossible explanations:")
        print("1. The key is truly random (no pattern)")
        print("2. The pattern requires more complex analysis")
        print("3. P ≠ NP and the key is computationally secure")
        print("4. The puzzle hasn't been solved yet...")

    with open("p_np_advanced_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to p_np_advanced_results.json")


if __name__ == "__main__":
    main()
