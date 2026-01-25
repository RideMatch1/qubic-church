#!/usr/bin/env python3
"""
P=NP Key Hunter - Testing various hypotheses to find hidden private keys
========================================================================

This script tests whether Satoshi/CFB left a solvable puzzle in:
1. The Genesis Block structure
2. The Anna Matrix
3. Various mathematical relationships

We're NOT trying to "break" cryptography - we're testing if keys were
intentionally made discoverable through patterns.
"""

import hashlib
import json
from typing import Optional, List, Tuple
from dataclasses import dataclass

# Try to import bitcoin libraries
try:
    import ecdsa
    from ecdsa import SECP256k1
    HAS_ECDSA = True
except ImportError:
    HAS_ECDSA = False
    print("Warning: ecdsa library not installed. Run: pip install ecdsa")

try:
    import base58
    HAS_BASE58 = True
except ImportError:
    HAS_BASE58 = False
    print("Warning: base58 library not installed. Run: pip install base58")


@dataclass
class TestResult:
    hypothesis: str
    private_key_hex: str
    generated_address: str
    target_address: str
    match: bool
    notes: str


# ============================================================================
# KNOWN DATA
# ============================================================================

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
GENESIS_BLOCK_HASH = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
GENESIS_MERKLE_ROOT = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
GENESIS_TIMESTAMP = 1231006505  # 2009-01-03 18:15:05 UTC
GENESIS_NONCE = 2083236893
GENESIS_EXTRA_NONCE = 4
GENESIS_MESSAGE = "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"

# Easter egg mentioned on Bitcointalk
EASTER_EGG_NUMBER = "20082034"

# Qubic Genesis Seed (public)
QUBIC_GENESIS_SEED = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# Anna Matrix 50 BTC addresses (from our research)
ANNA_MATRIX_50BTC = [
    "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S",  # Block 1
    "1BW18n7MfpU35q4MTBSk8pse3XzQF8XvzT",
    "1JfbZRwdDHKZmuiZgYArJZhcuuzuw2HuMu",
    "1GkQmKAmHtNfnD3LHhTkewJxKHVSta4m2a",
    "1E6YYAaWGJsNnJBuYgYPjZJkaHRJh4m6Td",
    "12tgPXLPFtLVSdT2VJUFh2j1BMcFTkNQmG",
    "1LfV1tSt3KNyHpFJnAzrqsLFdeD2EvU1MK",
    "1JsMtbLQAWkNaaetBCJjWLPMUY1vXBMtP7",
    "1FU5MqXcskdVY4Q5kJ5ZJ7vbY5M5VJZvxY",
    "1DfZp8dBVFBJK3t6cYbGmJPT8rLjPZ2K4s",
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sha256(data: bytes) -> bytes:
    """Single SHA256 hash"""
    return hashlib.sha256(data).digest()

def double_sha256(data: bytes) -> bytes:
    """Double SHA256 (Bitcoin standard)"""
    return sha256(sha256(data))

def ripemd160(data: bytes) -> bytes:
    """RIPEMD160 hash"""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data: bytes) -> bytes:
    """Bitcoin Hash160 = RIPEMD160(SHA256(data))"""
    return ripemd160(sha256(data))

def private_key_to_public_key(private_key_hex: str, compressed: bool = True) -> bytes:
    """Convert private key to public key"""
    if not HAS_ECDSA:
        return b''

    private_key_bytes = bytes.fromhex(private_key_hex)
    signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    verifying_key = signing_key.get_verifying_key()

    if compressed:
        x = verifying_key.pubkey.point.x()
        y = verifying_key.pubkey.point.y()
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        return b'\x04' + verifying_key.to_string()

def public_key_to_address(public_key: bytes) -> str:
    """Convert public key to Bitcoin address"""
    if not HAS_BASE58:
        return ""

    h160 = hash160(public_key)
    versioned = b'\x00' + h160
    checksum = double_sha256(versioned)[:4]
    return base58.b58encode(versioned + checksum).decode()

def private_key_to_address(private_key_hex: str, compressed: bool = True) -> str:
    """Convert private key directly to Bitcoin address"""
    if not HAS_ECDSA or not HAS_BASE58:
        return ""

    try:
        public_key = private_key_to_public_key(private_key_hex, compressed)
        return public_key_to_address(public_key)
    except Exception as e:
        return f"ERROR: {e}"


# ============================================================================
# HYPOTHESIS TESTS
# ============================================================================

def test_easter_egg_20082034() -> List[TestResult]:
    """
    Test the '20082034' easter egg hypothesis
    - 2008: Year of whitepaper
    - 2034: Unknown significance
    """
    results = []

    # Test 1: Direct as hex (padded)
    key1 = "0" * 56 + EASTER_EGG_NUMBER  # Pad to 64 chars
    addr1 = private_key_to_address(key1)
    results.append(TestResult(
        hypothesis="20082034 as direct hex (padded)",
        private_key_hex=key1,
        generated_address=addr1,
        target_address=GENESIS_ADDRESS,
        match=addr1 == GENESIS_ADDRESS,
        notes="Testing if 20082034 is the private key"
    ))

    # Test 2: SHA256 of "20082034"
    key2 = sha256(EASTER_EGG_NUMBER.encode()).hex()
    addr2 = private_key_to_address(key2)
    results.append(TestResult(
        hypothesis="SHA256('20082034')",
        private_key_hex=key2,
        generated_address=addr2,
        target_address=GENESIS_ADDRESS,
        match=addr2 == GENESIS_ADDRESS,
        notes="Testing SHA256 hash of easter egg"
    ))

    # Test 3: 20082034 as timestamp interpretation
    # 2008-20-34 doesn't make sense as date
    # But 2008 + 2034 = 4042, or 2034 - 2008 = 26
    key3 = sha256(str(2034 - 2008).encode()).hex()  # "26"
    addr3 = private_key_to_address(key3)
    results.append(TestResult(
        hypothesis="SHA256('26') - difference 2034-2008",
        private_key_hex=key3,
        generated_address=addr3,
        target_address=GENESIS_ADDRESS,
        match=addr3 == GENESIS_ADDRESS,
        notes="26 years difference"
    ))

    return results


def test_genesis_block_data() -> List[TestResult]:
    """Test various Genesis Block data as private keys"""
    results = []

    # Test 1: Genesis block hash as private key
    # Remove leading zeros and use rest
    key1 = GENESIS_BLOCK_HASH.replace("0", "", 10)[:64].zfill(64)
    addr1 = private_key_to_address(key1)
    results.append(TestResult(
        hypothesis="Genesis block hash (modified)",
        private_key_hex=key1,
        generated_address=addr1,
        target_address=GENESIS_ADDRESS,
        match=addr1 == GENESIS_ADDRESS,
        notes="Block hash with leading zeros trimmed"
    ))

    # Test 2: Merkle root as private key
    addr2 = private_key_to_address(GENESIS_MERKLE_ROOT)
    results.append(TestResult(
        hypothesis="Genesis Merkle root as private key",
        private_key_hex=GENESIS_MERKLE_ROOT,
        generated_address=addr2,
        target_address=GENESIS_ADDRESS,
        match=addr2 == GENESIS_ADDRESS,
        notes="Direct merkle root"
    ))

    # Test 3: Reversed Merkle root
    merkle_reversed = bytes.fromhex(GENESIS_MERKLE_ROOT)[::-1].hex()
    addr3 = private_key_to_address(merkle_reversed)
    results.append(TestResult(
        hypothesis="Genesis Merkle root REVERSED",
        private_key_hex=merkle_reversed,
        generated_address=addr3,
        target_address=GENESIS_ADDRESS,
        match=addr3 == GENESIS_ADDRESS,
        notes="Reversed byte order (little endian)"
    ))

    # Test 4: SHA256 of Times headline
    key4 = sha256(GENESIS_MESSAGE.encode()).hex()
    addr4 = private_key_to_address(key4)
    results.append(TestResult(
        hypothesis="SHA256(Times headline)",
        private_key_hex=key4,
        generated_address=addr4,
        target_address=GENESIS_ADDRESS,
        match=addr4 == GENESIS_ADDRESS,
        notes="Hash of embedded message"
    ))

    # Test 5: Double SHA256 of Times headline
    key5 = double_sha256(GENESIS_MESSAGE.encode()).hex()
    addr5 = private_key_to_address(key5)
    results.append(TestResult(
        hypothesis="Double SHA256(Times headline)",
        private_key_hex=key5,
        generated_address=addr5,
        target_address=GENESIS_ADDRESS,
        match=addr5 == GENESIS_ADDRESS,
        notes="Bitcoin-style double hash of message"
    ))

    # Test 6: Timestamp as key
    key6 = hex(GENESIS_TIMESTAMP)[2:].zfill(64)
    addr6 = private_key_to_address(key6)
    results.append(TestResult(
        hypothesis="Genesis timestamp as key",
        private_key_hex=key6,
        generated_address=addr6,
        target_address=GENESIS_ADDRESS,
        match=addr6 == GENESIS_ADDRESS,
        notes=f"Timestamp: {GENESIS_TIMESTAMP}"
    ))

    # Test 7: Nonce as key
    key7 = hex(GENESIS_NONCE)[2:].zfill(64)
    addr7 = private_key_to_address(key7)
    results.append(TestResult(
        hypothesis="Genesis nonce as key",
        private_key_hex=key7,
        generated_address=addr7,
        target_address=GENESIS_ADDRESS,
        match=addr7 == GENESIS_ADDRESS,
        notes=f"Nonce: {GENESIS_NONCE}"
    ))

    # Test 8: Extra nonce (the mysterious 4)
    key8 = hex(GENESIS_EXTRA_NONCE)[2:].zfill(64)
    addr8 = private_key_to_address(key8)
    results.append(TestResult(
        hypothesis="Genesis extra nonce (4) as key",
        private_key_hex=key8,
        generated_address=addr8,
        target_address=GENESIS_ADDRESS,
        match=addr8 == GENESIS_ADDRESS,
        notes="The mysterious extra nonce = 4"
    ))

    return results


def test_qubic_bitcoin_bridge() -> List[TestResult]:
    """Test Qubic-Bitcoin bridge hypotheses"""
    results = []

    # Test 1: SHA256 of Qubic Genesis Seed
    key1 = sha256(QUBIC_GENESIS_SEED.encode()).hex()
    addr1 = private_key_to_address(key1)
    results.append(TestResult(
        hypothesis="SHA256(Qubic Genesis Seed)",
        private_key_hex=key1,
        generated_address=addr1,
        target_address=GENESIS_ADDRESS,
        match=addr1 == GENESIS_ADDRESS,
        notes="Direct hash of Qubic seed"
    ))

    # Test 2: XOR of Genesis block hash with Qubic seed hash
    qubic_hash = sha256(QUBIC_GENESIS_SEED.encode())
    genesis_hash = bytes.fromhex(GENESIS_BLOCK_HASH)
    xor_result = bytes(a ^ b for a, b in zip(qubic_hash, genesis_hash))
    key2 = xor_result.hex()
    addr2 = private_key_to_address(key2)
    results.append(TestResult(
        hypothesis="XOR(SHA256(Qubic), Genesis Hash)",
        private_key_hex=key2,
        generated_address=addr2,
        target_address=GENESIS_ADDRESS,
        match=addr2 == GENESIS_ADDRESS,
        notes="XOR combination of both genesis data"
    ))

    return results


def test_sergio_lerner_hypothesis() -> List[TestResult]:
    """
    Test Sergio Lerner's hypothesis:
    The Genesis address might have been used as a nonce
    """
    results = []

    # Decode Genesis address and use its hash160 as key material
    if HAS_BASE58:
        try:
            decoded = base58.b58decode(GENESIS_ADDRESS)
            # Skip version byte (first) and checksum (last 4)
            hash160_bytes = decoded[1:-4]

            # Test 1: Hash160 padded as key
            key1 = hash160_bytes.hex().zfill(64)
            addr1 = private_key_to_address(key1)
            results.append(TestResult(
                hypothesis="Genesis address Hash160 as key",
                private_key_hex=key1,
                generated_address=addr1,
                target_address=GENESIS_ADDRESS,
                match=addr1 == GENESIS_ADDRESS,
                notes="Sergio's hypothesis: address as nonce"
            ))

            # Test 2: SHA256 of hash160
            key2 = sha256(hash160_bytes).hex()
            addr2 = private_key_to_address(key2)
            results.append(TestResult(
                hypothesis="SHA256(Genesis Hash160)",
                private_key_hex=key2,
                generated_address=addr2,
                target_address=GENESIS_ADDRESS,
                match=addr2 == GENESIS_ADDRESS,
                notes="Hash of the hash"
            ))
        except Exception as e:
            print(f"Error in Sergio test: {e}")

    return results


def test_43_zero_bits() -> List[TestResult]:
    """
    The Genesis block has 43 leading zero bits instead of required ~32
    This was intentional - test if 43 is significant
    """
    results = []

    # Test 1: 43 as part of key
    key1 = sha256(b"43").hex()
    addr1 = private_key_to_address(key1)
    results.append(TestResult(
        hypothesis="SHA256('43') - extra zero bits",
        private_key_hex=key1,
        generated_address=addr1,
        target_address=GENESIS_ADDRESS,
        match=addr1 == GENESIS_ADDRESS,
        notes="43 leading zeros was intentional"
    ))

    # Test 2: 43 * something
    key2 = hex(43 * GENESIS_NONCE)[2:].zfill(64)[:64]
    addr2 = private_key_to_address(key2)
    results.append(TestResult(
        hypothesis="43 * Genesis Nonce",
        private_key_hex=key2,
        generated_address=addr2,
        target_address=GENESIS_ADDRESS,
        match=addr2 == GENESIS_ADDRESS,
        notes="Combining 43 with nonce"
    ))

    return results


def test_satoshi_wordplay() -> List[TestResult]:
    """Test various wordplay that Satoshi might have used"""
    results = []

    phrases = [
        "satoshi nakamoto",
        "SATOSHI NAKAMOTO",
        "Satoshi Nakamoto",
        "genesis",
        "bitcoin",
        "In the beginning",
        "Let there be light",
        "Chancellor on brink of second bailout for banks",
        "The Times 03/Jan/2009",
        "P2P",
        "peer-to-peer electronic cash",
    ]

    for phrase in phrases:
        key = sha256(phrase.encode()).hex()
        addr = private_key_to_address(key)
        results.append(TestResult(
            hypothesis=f"SHA256('{phrase[:30]}...')" if len(phrase) > 30 else f"SHA256('{phrase}')",
            private_key_hex=key[:16] + "...",  # Truncate for display
            generated_address=addr,
            target_address=GENESIS_ADDRESS,
            match=addr == GENESIS_ADDRESS,
            notes="Wordplay hypothesis"
        ))

    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_all_tests():
    """Run all hypothesis tests"""

    print("=" * 80)
    print("P=NP KEY HUNTER - Testing Hidden Private Key Hypotheses")
    print("=" * 80)
    print()

    if not HAS_ECDSA or not HAS_BASE58:
        print("ERROR: Required libraries missing!")
        print("Run: pip install ecdsa base58")
        print()
        return

    all_results = []

    # Run all test categories
    print("[1/6] Testing '20082034' Easter Egg...")
    all_results.extend(test_easter_egg_20082034())

    print("[2/6] Testing Genesis Block Data...")
    all_results.extend(test_genesis_block_data())

    print("[3/6] Testing Qubic-Bitcoin Bridge...")
    all_results.extend(test_qubic_bitcoin_bridge())

    print("[4/6] Testing Sergio Lerner Hypothesis...")
    all_results.extend(test_sergio_lerner_hypothesis())

    print("[5/6] Testing 43 Zero Bits Mystery...")
    all_results.extend(test_43_zero_bits())

    print("[6/6] Testing Satoshi Wordplay...")
    all_results.extend(test_satoshi_wordplay())

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    matches = []
    for result in all_results:
        status = "✓ MATCH!" if result.match else "✗"
        print(f"{status} {result.hypothesis}")
        print(f"   Generated: {result.generated_address}")
        if result.match:
            print(f"   PRIVATE KEY: {result.private_key_hex}")
            matches.append(result)
        print()

    print("=" * 80)
    print(f"SUMMARY: Tested {len(all_results)} hypotheses")
    print(f"MATCHES FOUND: {len(matches)}")
    print("=" * 80)

    if matches:
        print("\n🎉 POTENTIAL MATCHES FOUND! 🎉\n")
        for m in matches:
            print(f"Hypothesis: {m.hypothesis}")
            print(f"Private Key: {m.private_key_hex}")
            print(f"Address: {m.generated_address}")
            print()
    else:
        print("\nNo matches found with current hypotheses.")
        print("The puzzle remains unsolved...")

    # Save results
    output = {
        "total_tests": len(all_results),
        "matches": len(matches),
        "results": [
            {
                "hypothesis": r.hypothesis,
                "generated_address": r.generated_address,
                "target_address": r.target_address,
                "match": r.match,
                "notes": r.notes
            }
            for r in all_results
        ]
    }

    with open("p_np_key_hunter_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to p_np_key_hunter_results.json")


if __name__ == "__main__":
    run_all_tests()
