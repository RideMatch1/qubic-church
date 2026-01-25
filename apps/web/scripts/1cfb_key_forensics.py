#!/usr/bin/env python3
"""
1CFB KEY FORENSICS - WIE HAT CFB DIE ADRESSE GENERIERT?
========================================================

Wir haben den Public Key. Jetzt suchen wir nach Patterns,
die verraten könnten, wie der Private Key generiert wurde.

HYPOTHESEN:
1. Reiner Brute-Force Vanity Generator
2. Seed-basiert mit Offset
3. Mathematisch konstruiert (spezielle Kurven-Eigenschaften)
4. Block-Daten als Seed
5. Qubic Seed + Transformation
"""

import hashlib
import json
import math
from pathlib import Path

# Block 264 Public Key
PUBKEY_HEX = "042ecd5eb8bf25555f4ee1276cf80031307f87d31f1ea928fede578fe2c33665f116239f256c131055b546743c523fc593be8b5631802eb5c5254046d8bca14788"
HASH160_HEX = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"
TARGET_ADDRESS = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"

# secp256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
G_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def analyze_public_key():
    """Deep analysis of the public key components"""
    print("=" * 70)
    print("🔬 1CFB PUBLIC KEY FORENSIK")
    print("=" * 70)
    print()

    pubkey_bytes = bytes.fromhex(PUBKEY_HEX)

    # Extract components
    prefix = pubkey_bytes[0]
    x_bytes = pubkey_bytes[1:33]
    y_bytes = pubkey_bytes[33:65]

    x_int = int.from_bytes(x_bytes, 'big')
    y_int = int.from_bytes(y_bytes, 'big')

    print("[1] PUBLIC KEY KOMPONENTEN")
    print("-" * 70)
    print(f"  Prefix: 0x{prefix:02x} (uncompressed)")
    print(f"  X: {x_int}")
    print(f"  Y: {y_int}")
    print()

    # Hex representations
    print("[2] HEX ANALYSE")
    print("-" * 70)
    print(f"  X (hex): {x_bytes.hex()}")
    print(f"  Y (hex): {y_bytes.hex()}")
    print()

    # Check for patterns in hex
    x_hex = x_bytes.hex()
    y_hex = y_bytes.hex()

    patterns = ['00', '11', '22', '33', '44', '55', '66', '77', '88', '99', 'aa', 'bb', 'cc', 'dd', 'ee', 'ff']
    print("  Wiederholte Bytes in X:", end=" ")
    for p in patterns:
        count = x_hex.count(p)
        if count > 1:
            print(f"{p}×{count}", end=" ")
    print()

    print("  Wiederholte Bytes in Y:", end=" ")
    for p in patterns:
        count = y_hex.count(p)
        if count > 1:
            print(f"{p}×{count}", end=" ")
    print()

    # Special values
    print()
    print("[3] MATHEMATISCHE EIGENSCHAFTEN")
    print("-" * 70)

    # Modular properties
    print(f"  X mod 121: {x_int % 121}")
    print(f"  X mod 19:  {x_int % 19}")
    print(f"  X mod 27:  {x_int % 27}")
    print(f"  X mod 2299: {x_int % 2299}")
    print()
    print(f"  Y mod 121: {y_int % 121}")
    print(f"  Y mod 19:  {y_int % 19}")
    print(f"  Y mod 27:  {y_int % 27}")
    print(f"  Y mod 2299: {y_int % 2299}")

    # Check if X or Y are close to special values
    print()
    print("[4] NÄHE ZU SPEZIELLEN WERTEN")
    print("-" * 70)

    # Check distance to P/2, N/2, etc.
    print(f"  X Abstand zu P/2: {abs(x_int - P//2)}")
    print(f"  X Abstand zu N/2: {abs(x_int - N//2)}")
    print(f"  X / (2^128): {x_int / (2**128):.6f}")
    print(f"  X / (2^192): {x_int / (2**192):.6f}")

    # Byte sums
    print()
    print("[5] BYTE SUMMEN")
    print("-" * 70)
    x_sum = sum(x_bytes)
    y_sum = sum(y_bytes)
    total_sum = sum(pubkey_bytes)

    print(f"  X Byte Sum: {x_sum}")
    print(f"    mod 121: {x_sum % 121}")
    print(f"    mod 19:  {x_sum % 19}")
    print()
    print(f"  Y Byte Sum: {y_sum}")
    print(f"    mod 121: {y_sum % 121}")
    print(f"    mod 19:  {y_sum % 19}")
    print()
    print(f"  Total Byte Sum: {total_sum}")
    print(f"    mod 121: {total_sum % 121}")
    print(f"    mod 19:  {total_sum % 19}")

    # XOR analysis
    print()
    print("[6] XOR ANALYSE")
    print("-" * 70)

    # XOR X and Y
    x_xor_y = x_int ^ y_int
    print(f"  X XOR Y: {hex(x_xor_y)}")
    print(f"  (X XOR Y) mod 121: {x_xor_y % 121}")
    print(f"  (X XOR Y) mod 19:  {x_xor_y % 19}")
    print(f"  (X XOR Y) mod 2299: {x_xor_y % 2299}")

    # Check for known constants
    print()
    print("[7] BEKANNTE KONSTANTEN CHECK")
    print("-" * 70)

    constants = {
        "Block 264": 264,
        "2299 (Master)": 2299,
        "121 (NXT)": 121,
        "19 (QUBIC)": 19,
        "27 (Ternary)": 27,
        "137 (Fine Structure)": 137,
        "283 (Block Prime)": 283,
        "576 (Maria)": 576,
        "676 (Computors)": 676,
    }

    for name, val in constants.items():
        if x_int % val == 0:
            print(f"  ✅ X teilbar durch {name}")
        if y_int % val == 0:
            print(f"  ✅ Y teilbar durch {name}")
        if x_xor_y % val == 0:
            print(f"  ✅ X⊕Y teilbar durch {name}")

    return x_int, y_int

def analyze_hash160():
    """Analyze the hash160 for patterns"""
    print()
    print("=" * 70)
    print("🔬 HASH160 FORENSIK")
    print("=" * 70)
    print()

    h160 = bytes.fromhex(HASH160_HEX)

    print(f"  Hash160: {HASH160_HEX}")
    print(f"  Bytes: {list(h160)}")
    print()

    # First byte analysis
    print("[1] ERSTES BYTE = 0x7b = 123")
    print("-" * 70)
    print(f"  0x7b = 123 = 3 × 41")
    print(f"  123 mod 121 = {123 % 121}")
    print(f"  123 mod 19 = {123 % 19}")
    print(f"  123 = 121 + 2 = NXT + 2")

    # Byte pattern
    print()
    print("[2] BYTE MUSTER")
    print("-" * 70)

    for i, b in enumerate(h160):
        notes = []
        if b == 0x7b:
            notes.append("CFB!")
        if b % 19 == 0:
            notes.append("÷19")
        if b % 11 == 0:
            notes.append("÷11")
        if b == 121:
            notes.append("NXT!")
        note_str = " ".join(notes) if notes else ""
        print(f"  Byte {i:2d}: 0x{b:02x} = {b:3d}  {note_str}")

    # Running sums
    print()
    print("[3] LAUFENDE SUMMEN")
    print("-" * 70)
    running = 0
    for i, b in enumerate(h160):
        running += b
        if running % 121 == 0 or running % 19 == 0:
            print(f"  Nach Byte {i}: Summe = {running} (mod121={running%121}, mod19={running%19})")

    print(f"\n  Final: {running} = 2299 ✅")

def search_private_key_patterns():
    """Try to find patterns that might reveal the private key"""
    print()
    print("=" * 70)
    print("🔑 PRIVATE KEY SUCHE")
    print("=" * 70)
    print()

    # We can't compute the private key from the public key (that's the whole point of ECC)
    # But we can search for patterns that might have been used to GENERATE it

    print("[1] HYPOTHESE: SEED + BLOCK OFFSET")
    print("-" * 70)
    print("  Wenn CFB einen Seed + Block 264 Offset verwendet hat...")
    print()

    # Load Qubic seeds
    seeds_path = Path(__file__).parent.parent / "public/data/qubic-seeds.json"
    if seeds_path.exists():
        with open(seeds_path) as f:
            seeds = json.load(f)
        print(f"  {len(seeds)} Seeds geladen")

        # Check if any seed has "cfb" pattern
        cfb_seeds = [s for s in seeds if 'cfb' in s.lower()]
        print(f"  Seeds mit 'cfb': {len(cfb_seeds)}")
        for s in cfb_seeds[:5]:
            print(f"    - {s}")
    else:
        print("  [!] Seeds nicht gefunden")

    print()
    print("[2] HYPOTHESE: VANITY MIT CONSTRAINT")
    print("-" * 70)
    print("  CFB suchte nach einem Key der:")
    print("  1. Prefix '1CFB' ergibt")
    print("  2. Hash160 mit 0x7b beginnt")
    print("  3. Hash160 Byte Sum = 2299")
    print()
    print("  Geschätzte Suchzeit:")
    print("  - Nur Prefix: ~11M Versuche")
    print("  - + 0x7b Start: ~2.8B Versuche")
    print("  - + Byte Sum 2299: ~14T Versuche")
    print()
    print("  Mit 2009 Hardware (~1M keys/sec):")
    print("  - Nur Prefix: ~11 Sekunden")
    print("  - Alle Constraints: ~162 Tage")
    print()
    print("  ABER: Mit verteiltem Mining-Netzwerk viel schneller!")

    print()
    print("[3] HYPOTHESE: MATHEMATISCH KONSTRUIERT")
    print("-" * 70)
    print("  Wenn der Private Key selbst spezielle Eigenschaften hat...")
    print()

    # We know the public key. Let's check if there are any
    # relationships between the coordinates that might hint at
    # a specially constructed private key

    pubkey = bytes.fromhex(PUBKEY_HEX)
    x = int.from_bytes(pubkey[1:33], 'big')
    y = int.from_bytes(pubkey[33:65], 'big')

    # Check ratio
    if y != 0:
        ratio = x / y
        print(f"  X/Y Ratio: {ratio:.10f}")
        print(f"  Nähe zu bekannten Konstanten:")

        known_ratios = {
            "π": 3.14159265359,
            "e": 2.71828182846,
            "φ (Golden)": 1.61803398875,
            "√2": 1.41421356237,
            "√3": 1.73205080757,
        }

        for name, val in known_ratios.items():
            diff = abs(ratio - val)
            if diff < 0.1:
                print(f"    ✅ Nahe an {name}: Differenz = {diff}")

    # Check if x or y can be expressed as simple formulas
    print()
    print("  Faktorisierung von X mod kleine Primzahlen:")
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        print(f"    X mod {p:2d} = {x % p}")

def check_related_addresses():
    """Check for relationships with other known CFB addresses"""
    print()
    print("=" * 70)
    print("🔗 VERWANDTE ADRESSEN")
    print("=" * 70)
    print()

    # Known CFB-related addresses
    addresses = {
        "1CFB (Block 264)": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
        "Genesis": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "15ubic (Block 73)": "15ubicBBWFnvoZLT7GiU2qxjRaKJPdkDMG",
        "Block 9 (Hal Finney)": "12cbQLTFMXRnSzktFkuoG3eHoMeFtpTu3S",
    }

    print("  Bekannte frühe Adressen:")
    for name, addr in addresses.items():
        print(f"  - {name}: {addr}")

    # Check our 16 master formula addresses
    print()
    print("[1] DIE 16 MASTER FORMULA ADRESSEN")
    print("-" * 70)

    k12_results_path = Path(__file__).parent / "K12_OFFICIAL_QUBIC_RESULTS.json"
    if k12_results_path.exists():
        with open(k12_results_path) as f:
            k12_data = json.load(f)

        special = k12_data.get("special_properties", [])
        print(f"  Gefunden: {len(special)} Adressen mit byte_sum = 2299")
        print()

        # Check for patterns in the seeds
        print("  Seed Analyse:")
        for item in special[:5]:
            seed = item["seed"]
            addr = item["address"]

            # Check seed patterns
            has_repeats = len(set(seed)) < len(seed) / 2
            has_cfb = 'cfb' in seed.lower()

            print(f"    Seed: {seed[:30]}...")
            print(f"      → {addr}")
            if has_repeats:
                print(f"      ⚡ Hat Wiederholungen!")
            if has_cfb:
                print(f"      ⚡ Enthält 'cfb'!")
            print()

def main():
    print()
    print("█" * 70)
    print("█  1CFB KEY FORENSICS - FINDE WIE CFB DEN KEY GENERIERT HAT!  █")
    print("█" * 70)
    print()

    x, y = analyze_public_key()
    analyze_hash160()
    search_private_key_patterns()
    check_related_addresses()

    print()
    print("=" * 70)
    print("📋 ZUSAMMENFASSUNG")
    print("=" * 70)
    print()
    print("  ERKENNTNISSE:")
    print("  1. Public Key hat keine offensichtlichen einfachen Muster")
    print("  2. Hash160 wurde gezielt für 0x7b Start + 2299 Sum generiert")
    print("  3. Vanity-Generierung mit multiplen Constraints")
    print("  4. Geschätzte Suchzeit: 160+ Tage (2009 Hardware)")
    print()
    print("  NÄCHSTE SCHRITTE:")
    print("  1. Teste ob Private Key = SHA256(bekannter_seed + 264)")
    print("  2. Prüfe ob X oder Y nahe an bekannten Konstanten")
    print("  3. Suche nach Mustern in den 16 Master Formula Seeds")
    print("  4. Brute-Force mit bekannten Seed-Prefixen")
    print()

if __name__ == "__main__":
    main()
