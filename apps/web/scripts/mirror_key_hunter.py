#!/usr/bin/env python3
"""
Mirror Key Hunter - Testing CFB's "Mirror" Hint
===============================================

CFB hint: "man muss die Adresse spiegeln" (you have to mirror the address)

Testing various mirroring/reflection operations:
1. String reversal
2. Byte reversal
3. Bit reflection
4. XOR complement
5. Coordinate swapping
"""

import hashlib
import json

try:
    import ecdsa
    from ecdsa import SECP256k1
    import base58
except ImportError:
    print("Run: pip3 install ecdsa base58")
    exit(1)


# ============================================================================
# KNOWN DATA
# ============================================================================

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
GENESIS_PUBKEY_HEX = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"

# CFB Address mentioned in research
CFB_ADDRESS_1 = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"
CFB_ADDRESS_HASH160 = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"

# First 10 Patoshi blocks addresses (50 BTC each)
PATOSHI_50BTC_ADDRESSES = [
    ("Block 1", "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S"),
    ("Block 2", "1BW18n7MfpU35q4MTBSk8pse3XzQF8XvzT"),
    ("Block 9", "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"),  # Known Satoshi
    ("Block 170", "1PSSGeFHDnKNxiEyFrD1wcEaHr9hrQDDWc"),  # First TX ever
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

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
    h160 = hash160(pub)
    versioned = b'\x00' + h160
    checksum = double_sha256(versioned)[:4]
    return base58.b58encode(versioned + checksum).decode()

def test_key(priv_hex: str, target_addr: str) -> tuple:
    """Test a private key against target address"""
    for compressed in [False, True]:
        pub = private_to_public(priv_hex, compressed)
        if pub:
            addr = public_to_address(pub)
            if addr == target_addr:
                return True, addr, "compressed" if compressed else "uncompressed"
    return False, public_to_address(private_to_public(priv_hex, False)) if private_to_public(priv_hex, False) else "", ""


def reverse_bits_in_byte(b: int) -> int:
    """Reverse the bits in a single byte"""
    result = 0
    for i in range(8):
        if b & (1 << i):
            result |= (1 << (7 - i))
    return result

def mirror_bytes(data: bytes) -> bytes:
    """Reverse byte order"""
    return data[::-1]

def mirror_bits(data: bytes) -> bytes:
    """Reverse bits in each byte"""
    return bytes(reverse_bits_in_byte(b) for b in data)

def xor_complement(data: bytes) -> bytes:
    """XOR with 0xFF (complement)"""
    return bytes(b ^ 0xFF for b in data)


# ============================================================================
# MIRROR TESTS
# ============================================================================

def test_mirror_methods():
    """Test various mirroring interpretations"""
    print("\n" + "=" * 70)
    print("MIRROR KEY HUNTER - Testing CFB's 'Mirror' Hint")
    print("=" * 70)

    results = []

    # Get Genesis pubkey components
    pubkey_bytes = bytes.fromhex(GENESIS_PUBKEY_HEX[2:])  # Remove 04
    x_coord = pubkey_bytes[:32]
    y_coord = pubkey_bytes[32:]

    # Get Genesis address hash160
    genesis_decoded = base58.b58decode(GENESIS_ADDRESS)
    genesis_hash160 = genesis_decoded[1:-4]

    # Get CFB address hash160
    cfb_hash160 = bytes.fromhex(CFB_ADDRESS_HASH160)

    print(f"\nGenesis Address: {GENESIS_ADDRESS}")
    print(f"Genesis Hash160: {genesis_hash160.hex()}")
    print(f"CFB Address: {CFB_ADDRESS_1}")
    print(f"CFB Hash160: {cfb_hash160.hex()}")

    mirror_tests = [
        # String-based mirrors
        ("Genesis address reversed (string)", sha256(GENESIS_ADDRESS[::-1].encode()).hex()),
        ("CFB address reversed (string)", sha256(CFB_ADDRESS_1[::-1].encode()).hex()),

        # Byte-based mirrors
        ("Genesis Hash160 reversed (bytes)", genesis_hash160[::-1].hex().zfill(64)),
        ("CFB Hash160 reversed (bytes)", cfb_hash160[::-1].hex().zfill(64)),
        ("SHA256(Genesis Hash160 reversed)", sha256(genesis_hash160[::-1]).hex()),
        ("SHA256(CFB Hash160 reversed)", sha256(cfb_hash160[::-1]).hex()),

        # Public key mirrors
        ("X coord reversed", x_coord[::-1].hex()),
        ("Y coord reversed", y_coord[::-1].hex()),
        ("X and Y swapped (SHA256)", sha256(y_coord + x_coord).hex()),
        ("X XOR Y as key", bytes(a ^ b for a, b in zip(x_coord, y_coord)).hex()),

        # Bit-level mirrors
        ("Genesis Hash160 bits mirrored", mirror_bits(genesis_hash160).hex().zfill(64)),
        ("X coord bits mirrored", mirror_bits(x_coord).hex()),

        # XOR/Complement operations
        ("Genesis Hash160 XOR 0xFF", xor_complement(genesis_hash160).hex().zfill(64)),
        ("X XOR 0xFF as key", xor_complement(x_coord).hex()),

        # Genesis XOR CFB
        ("Genesis XOR CFB Hash160", bytes(a ^ b for a, b in zip(genesis_hash160, cfb_hash160)).hex().zfill(64)),
        ("SHA256(Genesis XOR CFB)", sha256(bytes(a ^ b for a, b in zip(genesis_hash160, cfb_hash160))).hex()),

        # Combined mirrors
        ("SHA256(reversed X + reversed Y)", sha256(x_coord[::-1] + y_coord[::-1]).hex()),
        ("SHA256(Y reversed + X reversed)", sha256(y_coord[::-1] + x_coord[::-1]).hex()),
    ]

    print("\n" + "-" * 70)
    print("Testing mirror hypotheses against Genesis address:")
    print("-" * 70)

    for name, key in mirror_tests:
        if len(key) != 64:
            key = key.zfill(64)[-64:]  # Ensure 64 chars

        match, addr, key_type = test_key(key, GENESIS_ADDRESS)
        status = "✓ MATCH!" if match else "✗"
        print(f"{status} {name}")
        print(f"   Key: {key[:32]}...")
        print(f"   Addr: {addr[:30]}...")

        results.append({
            "test": name,
            "key": key,
            "generated": addr,
            "target": GENESIS_ADDRESS,
            "match": match
        })

        if match:
            print(f"\n🎉 FOUND PRIVATE KEY! 🎉")
            print(f"Key: {key}")
            return results

    # Also test against CFB address
    print("\n" + "-" * 70)
    print("Testing mirror hypotheses against CFB address:")
    print("-" * 70)

    cfb_tests = [
        ("Genesis Hash160 reversed", genesis_hash160[::-1].hex().zfill(64)),
        ("SHA256(Genesis Hash160)", sha256(genesis_hash160).hex()),
        ("Genesis XOR CFB", bytes(a ^ b for a, b in zip(genesis_hash160, cfb_hash160)).hex().zfill(64)),
    ]

    for name, key in cfb_tests:
        if len(key) != 64:
            key = key.zfill(64)[-64:]

        match, addr, key_type = test_key(key, CFB_ADDRESS_1)
        status = "✓ MATCH!" if match else "✗"
        print(f"{status} {name} -> {addr[:25]}...")

        if match:
            print(f"\n🎉 FOUND CFB PRIVATE KEY! 🎉")
            print(f"Key: {key}")

    return results


def test_patoshi_patterns():
    """Test if Patoshi addresses have related private keys"""
    print("\n" + "=" * 70)
    print("Testing Patoshi Address Patterns")
    print("=" * 70)

    for name, addr in PATOSHI_50BTC_ADDRESSES:
        try:
            decoded = base58.b58decode(addr)
            h160 = decoded[1:-4]

            # Test various derivations
            tests = [
                sha256(h160).hex(),
                h160[::-1].hex().zfill(64),
                sha256(addr.encode()).hex(),
            ]

            print(f"\n{name}: {addr}")
            for i, key in enumerate(tests):
                match, gen_addr, _ = test_key(key, addr)
                if match:
                    print(f"  ✓ MATCH with method {i}!")
                    print(f"  Key: {key}")
        except Exception as e:
            print(f"Error with {name}: {e}")


def test_cfb_27_pattern():
    """
    CFB loves the number 27.
    Test if 27 is involved in the key derivation.
    """
    print("\n" + "=" * 70)
    print("Testing CFB's '27' Pattern")
    print("=" * 70)

    genesis_decoded = base58.b58decode(GENESIS_ADDRESS)
    genesis_hash160 = genesis_decoded[1:-4]

    tests_27 = [
        ("27 as key seed", sha256(b"27").hex()),
        ("Genesis Hash160 * 27 (mod curve)", None),  # Special
        ("SHA256 iterated 27 times", None),  # Special
        ("Genesis hash160[27:] as key", genesis_hash160[7:].hex().zfill(64) if len(genesis_hash160) > 7 else ""),
        ("Rotate bytes by 27", bytes(genesis_hash160[(i + 27) % 20] for i in range(20)).hex().zfill(64)),
    ]

    # SHA256 iterated 27 times
    current = genesis_hash160
    for i in range(27):
        current = sha256(current)
    tests_27[2] = ("SHA256^27(Genesis Hash160)", current.hex())

    for name, key in tests_27:
        if key is None or len(key) == 0:
            continue
        if len(key) != 64:
            key = key.zfill(64)[-64:]

        match, addr, _ = test_key(key, GENESIS_ADDRESS)
        status = "✓ MATCH!" if match else "✗"
        print(f"{status} {name} -> {addr[:25]}...")


def test_numogram_connection():
    """
    Test if Numogram numbers (from CFB's Qubic hints) relate to keys
    """
    print("\n" + "=" * 70)
    print("Testing Numogram/Qubic Connections")
    print("=" * 70)

    numogram_seeds = [
        "NUMOGRAM",
        "QUBIC",
        "AIGARTH",
        "ANNA",
        "SYZYGY",
        "CFB",
        "COMEFROMBEYOND",
        "19",  # Qubic tick
        "676",  # Computors
        "451",  # Quorum
    ]

    for seed in numogram_seeds:
        key = sha256(seed.encode()).hex()
        match, addr, _ = test_key(key, GENESIS_ADDRESS)
        status = "✓" if match else "✗"
        print(f"{status} SHA256('{seed}') -> {addr[:20]}...")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("MIRROR KEY HUNTER")
    print("Testing CFB's hint: 'You have to mirror the address'")
    print("=" * 70)

    results = test_mirror_methods()
    test_patoshi_patterns()
    test_cfb_27_pattern()
    test_numogram_connection()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    matches = [r for r in results if r["match"]]
    if matches:
        print(f"\n✓ Found {len(matches)} matching key(s)!")
        for m in matches:
            print(f"  Test: {m['test']}")
            print(f"  Key:  {m['key']}")
    else:
        print("\n✗ No matching keys found")
        print("\nThe 'mirror' hint might refer to:")
        print("1. A more complex mathematical operation")
        print("2. Mirroring across the elliptic curve")
        print("3. A metaphorical/philosophical hint")
        print("4. Something we haven't discovered yet...")

    with open("mirror_key_results.json", "w") as f:
        json.dump({"results": results, "matches": matches}, f, indent=2)

    print("\nResults saved to mirror_key_results.json")


if __name__ == "__main__":
    main()
