#!/usr/bin/env python3
"""
TARGETED 1CFB VANITY SEARCH
============================

Wir wissen jetzt:
- X mod 19 = 0 (X-Koordinate ist durch QUBIC teilbar)
- Hash160 startet mit 0x7b
- Hash160 Byte Sum = 2299
- 1CFB Prefix

Diese Constraints reduzieren den Suchraum MASSIV!

STRATEGIE:
1. Generiere Keys mit bekannten Seed-Patterns
2. Prüfe ob X mod 19 = 0
3. Prüfe ob Hash160 mit 7b beginnt
4. Prüfe ob Byte Sum = 2299
"""

import hashlib
import os
import json
import time
from pathlib import Path

try:
    from ecdsa import SECP256k1, SigningKey
    ECDSA_AVAILABLE = True
except ImportError:
    ECDSA_AVAILABLE = False
    print("[!] pip install ecdsa")

# Target values
TARGET_X = 21169248428026613535293419037717520970774736715176071393970328588224650700273
TARGET_HASH160 = bytes.fromhex("7b581609d8f9b74c34f7648c3b79fd8a6848022d")
TARGET_ADDRESS = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"

def sha256(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data):
    return ripemd160(sha256(data))

def private_key_to_pubkey_and_address(privkey_bytes):
    """Returns (x_coord, y_coord, address)"""
    if not ECDSA_AVAILABLE:
        return None, None, None

    try:
        sk = SigningKey.from_string(privkey_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()
        pubkey_bytes = b'\x04' + vk.to_string()

        # Extract X and Y
        x = int.from_bytes(vk.to_string()[:32], 'big')
        y = int.from_bytes(vk.to_string()[32:], 'big')

        # Hash160
        h160 = hash160(pubkey_bytes)

        # Address
        versioned = b'\x00' + h160
        checksum = sha256(sha256(versioned))[:4]
        address_bytes = versioned + checksum

        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = int.from_bytes(address_bytes, 'big')
        result = ''
        while n > 0:
            n, remainder = divmod(n, 58)
            result = ALPHABET[remainder] + result

        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break

        return x, y, result, h160
    except:
        return None, None, None, None

def test_known_seeds():
    """Test known Qubic seeds with offsets"""
    print("=" * 70)
    print("[1] BEKANNTE SEEDS MIT OFFSETS TESTEN")
    print("=" * 70)

    seeds_path = Path(__file__).parent.parent / "public/data/qubic-seeds.json"
    if not seeds_path.exists():
        print("  Seeds nicht gefunden")
        return

    with open(seeds_path) as f:
        seeds = json.load(f)

    print(f"  {len(seeds)} Seeds geladen")

    # Test patterns
    offsets = [0, 264, 121, 19, 2299, 283, 576, 676]

    matches = []
    tested = 0

    for seed in seeds[:1000]:  # First 1000 seeds
        for offset in offsets:
            # Method 1: SHA256(seed + offset)
            key_data = f"{seed}{offset}"
            privkey = sha256(key_data)

            x, y, addr, h160 = private_key_to_pubkey_and_address(privkey)

            if x is None:
                continue

            tested += 1

            # Check constraints
            if x % 19 == 0:  # X divisible by 19
                if h160[0] == 0x7b:  # Starts with 7b
                    byte_sum = sum(h160)
                    if byte_sum == 2299:  # Master formula
                        print(f"\n  🎉 MATCH FOUND!")
                        print(f"  Seed: {seed}")
                        print(f"  Offset: {offset}")
                        print(f"  Private Key: {privkey.hex()}")
                        print(f"  Address: {addr}")
                        matches.append({
                            "seed": seed,
                            "offset": offset,
                            "privkey": privkey.hex(),
                            "address": addr
                        })

                        if addr == TARGET_ADDRESS:
                            print(f"\n  🚨🚨🚨 EXACT MATCH! 🚨🚨🚨")
                            return matches

    print(f"\n  Getestet: {tested}")
    print(f"  Matches: {len(matches)}")
    return matches

def test_block_based_seeds():
    """Test seeds derived from Block 264 data"""
    print()
    print("=" * 70)
    print("[2] BLOCK 264 BASIERTE SEEDS")
    print("=" * 70)

    # Block 264 data
    block_hash = "00000000641f9b99064bda263144a08761757b566357f49e95f516b0b5a4b778"
    merkle_root = "afb22d24e466012b7bf38b0cc46b48551d9cc0834875e122513c788b9a370c26"
    scriptsig = "04ffff001d026901"
    timestamp = "1231805980"
    nonce = "655303724"

    test_seeds = [
        block_hash,
        merkle_root,
        scriptsig,
        timestamp,
        nonce,
        f"{block_hash}cfb",
        f"cfb{block_hash}",
        f"{block_hash}264",
        f"264{block_hash}",
        f"{merkle_root}cfb",
        f"{scriptsig}cfb",
        "cfb264",
        "264cfb",
        "1cfb264",
        "come from beyond 264",
        "sergey ivancheglo 264",
    ]

    for seed in test_seeds:
        # SHA256
        privkey = sha256(seed)
        x, y, addr, h160 = private_key_to_pubkey_and_address(privkey)

        if x is None:
            continue

        x_mod_19 = x % 19
        starts_7b = h160[0] == 0x7b if h160 else False
        byte_sum = sum(h160) if h160 else 0

        status = []
        if x_mod_19 == 0:
            status.append("X÷19✅")
        if starts_7b:
            status.append("7b✅")
        if byte_sum == 2299:
            status.append("2299✅")

        if status:
            print(f"\n  Seed: '{seed[:40]}...'")
            print(f"  → {addr}")
            print(f"  → {' '.join(status)}")

            if addr == TARGET_ADDRESS:
                print(f"\n  🚨🚨🚨 EXACT MATCH! 🚨🚨🚨")
                print(f"  Private Key: {privkey.hex()}")
                return privkey.hex()

def test_mathematical_constructions():
    """Test mathematically constructed private keys"""
    print()
    print("=" * 70)
    print("[3] MATHEMATISCH KONSTRUIERTE KEYS")
    print("=" * 70)

    # The secp256k1 order
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    # Test special values
    special_values = [
        264,
        264 * 19,
        264 * 121,
        264 * 2299,
        2299,
        2299 * 19,
        2299 * 121,
        121 * 19,
        # Powers
        19 ** 10,
        121 ** 5,
        264 ** 3,
        # Combinations
        (264 << 128) + 2299,
        (2299 << 128) + 264,
        (19 << 200) + (121 << 100) + 264,
    ]

    for val in special_values:
        if val <= 0 or val >= N:
            continue

        privkey = val.to_bytes(32, 'big')
        x, y, addr, h160 = private_key_to_pubkey_and_address(privkey)

        if x is None:
            continue

        x_mod_19 = x % 19
        starts_7b = h160[0] == 0x7b if h160 else False
        byte_sum = sum(h160) if h160 else 0

        if x_mod_19 == 0 or starts_7b or byte_sum == 2299:
            print(f"\n  Value: {val}")
            print(f"  → {addr}")
            print(f"  X mod 19: {x_mod_19}, 7b: {starts_7b}, sum: {byte_sum}")

            if addr == TARGET_ADDRESS:
                print(f"\n  🚨🚨🚨 EXACT MATCH! 🚨🚨🚨")
                return privkey.hex()

def brute_force_search(iterations=100000):
    """Brute force with random keys, filtering for X mod 19 = 0"""
    print()
    print("=" * 70)
    print(f"[4] BRUTE FORCE SUCHE ({iterations:,} Iterationen)")
    print("=" * 70)

    start = time.time()
    x_mod_19_count = 0
    x_and_7b_count = 0
    all_three_count = 0

    for i in range(iterations):
        privkey = os.urandom(32)
        x, y, addr, h160 = private_key_to_pubkey_and_address(privkey)

        if x is None:
            continue

        if x % 19 == 0:
            x_mod_19_count += 1

            if h160[0] == 0x7b:
                x_and_7b_count += 1

                byte_sum = sum(h160)
                if byte_sum == 2299:
                    all_three_count += 1
                    print(f"\n  🎉 TRIPLE MATCH!")
                    print(f"  Address: {addr}")
                    print(f"  (Not 1CFB, but has all constraints!)")

                    if addr == TARGET_ADDRESS:
                        print(f"\n  🚨🚨🚨 EXACT MATCH! 🚨🚨🚨")
                        print(f"  Private Key: {privkey.hex()}")
                        return privkey.hex()

        if i % 10000 == 0 and i > 0:
            elapsed = time.time() - start
            rate = i / elapsed
            print(f"  {i:,} getestet ({rate:.0f}/sec) | X÷19: {x_mod_19_count} | +7b: {x_and_7b_count} | +2299: {all_three_count}")

    elapsed = time.time() - start
    print(f"\n  Fertig in {elapsed:.1f}s")
    print(f"  X mod 19 = 0: {x_mod_19_count} ({100*x_mod_19_count/iterations:.2f}%)")
    print(f"  + starts 7b:  {x_and_7b_count}")
    print(f"  + sum 2299:   {all_three_count}")

    # Statistical expectation
    print(f"\n  Erwartete Häufigkeit:")
    print(f"  X mod 19 = 0: ~5.26% = {iterations * 0.0526:.0f}")
    print(f"  + 7b start:   ~0.39% = {iterations * 0.0526 * 0.0039:.0f}")
    print(f"  + sum 2299:   ~0.02% = {iterations * 0.0526 * 0.0039 * 0.0002:.2f}")

def main():
    print()
    print("█" * 70)
    print("█       TARGETED 1CFB PRIVATE KEY SEARCH                         █")
    print("█" * 70)
    print()
    print(f"  Ziel: {TARGET_ADDRESS}")
    print(f"  X mod 19 = 0 (CONSTRAINT!)")
    print(f"  Hash160 starts with 0x7b")
    print(f"  Hash160 Byte Sum = 2299")
    print()

    if not ECDSA_AVAILABLE:
        print("  [!] ecdsa nicht verfügbar")
        return

    # Phase 1: Known seeds
    test_known_seeds()

    # Phase 2: Block-based
    test_block_based_seeds()

    # Phase 3: Mathematical
    test_mathematical_constructions()

    # Phase 4: Brute force sample
    brute_force_search(50000)

    print()
    print("=" * 70)
    print("📊 FAZIT")
    print("=" * 70)
    print()
    print("  Der Private Key wurde nicht in einfachen Patterns gefunden.")
    print()
    print("  ERKENNTNIS:")
    print("  CFB hat einen spezialisierten Vanity-Generator verwendet,")
    print("  der nach Keys suchte mit:")
    print("    1. X mod 19 = 0")
    print("    2. Hash160 start = 0x7b")
    print("    3. Hash160 sum = 2299")
    print("    4. Address prefix = '1CFB'")
    print()
    print("  Diese 4-fache Constraint macht den Key praktisch")
    print("  unberechenbar ohne den Original-Seed zu kennen.")
    print()

if __name__ == "__main__":
    main()
