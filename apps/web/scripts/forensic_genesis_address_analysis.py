#!/usr/bin/env python3
"""
🔥 FORENSISCHE ANALYSE - RICHTIGE GENESIS ISSUER ADRESSE 🔥
============================================================

KRITISCH: Alle bisherigen Analysen waren mit FALSCHER Adresse!

FALSCH (alt): POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD
RICHTIG (neu): POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD

Diese Analyse untersucht die RICHTIGE Adresse auf:
1. Character patterns & frequency
2. Mathematical properties (mod 27, 283, etc.)
3. Connections to Bitcoin Genesis
4. Embedded private key patterns
5. CFB number signatures
6. XOR operations
7. Segment analysis
8. Base58/Base32 decoding attempts
"""

import hashlib
import json
from collections import Counter
import re

# RICHTIGE GENESIS ISSUER ADRESSE
CORRECT_ADDRESS = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OLD_WRONG_ADDRESS = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# CFB Signature Numbers
CFB_NUMBERS = [27, 283, 47, 137, 121, 43, 19, 7, 14]

# Bitcoin Genesis Block Hash
BITCOIN_GENESIS = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"

def basic_properties():
    """Grundlegende Eigenschaften der Adresse"""
    print("\n" + "="*80)
    print("📊 BASIC PROPERTIES")
    print("="*80)

    addr = CORRECT_ADDRESS
    old = OLD_WRONG_ADDRESS

    print(f"\n✅ CORRECT ADDRESS:")
    print(f"   {addr}")
    print(f"\n❌ OLD (WRONG) ADDRESS:")
    print(f"   {old}")

    print(f"\n📏 Length: {len(addr)} characters")
    print(f"📏 Old length: {len(old)} characters")
    print(f"   Difference: {len(addr) - len(old)} characters")

    # Character difference
    print(f"\n🔄 CHARACTER DIFFERENCES:")
    for i, (c1, c2) in enumerate(zip(addr, old)):
        if c1 != c2:
            print(f"   Position {i}: '{c1}' vs '{c2}' (old)")

    # Unique characters
    unique_correct = len(set(addr))
    unique_old = len(set(old))
    print(f"\n🎯 Unique characters:")
    print(f"   Correct: {unique_correct}")
    print(f"   Old: {unique_old}")

    return addr

def character_frequency_analysis(addr):
    """Character frequency und patterns"""
    print("\n" + "="*80)
    print("📈 CHARACTER FREQUENCY ANALYSIS")
    print("="*80)

    freq = Counter(addr)

    print(f"\n📊 Most common characters:")
    for char, count in freq.most_common(10):
        percentage = (count / len(addr)) * 100
        print(f"   '{char}': {count} times ({percentage:.1f}%)")

    # Character categories
    letters = sum(1 for c in addr if c.isalpha())
    digits = sum(1 for c in addr if c.isdigit())

    print(f"\n📝 Character categories:")
    print(f"   Letters: {letters} ({letters/len(addr)*100:.1f}%)")
    print(f"   Digits: {digits} ({digits/len(addr)*100:.1f}%)")

    # Consecutive repeats
    print(f"\n🔄 Consecutive repeats:")
    for i in range(len(addr)-1):
        if addr[i] == addr[i+1]:
            print(f"   Position {i}-{i+1}: '{addr[i]}{addr[i+1]}'")

    return freq

def mathematical_analysis(addr):
    """Mathematische Eigenschaften"""
    print("\n" + "="*80)
    print("🔢 MATHEMATICAL ANALYSIS")
    print("="*80)

    # Convert to numbers (A=0, B=1, ..., Z=25)
    numeric_values = []
    for char in addr:
        if char.isalpha():
            numeric_values.append(ord(char) - ord('A'))
        elif char.isdigit():
            numeric_values.append(int(char))

    print(f"\n📊 Numeric value statistics:")
    print(f"   Sum: {sum(numeric_values)}")
    print(f"   Mean: {sum(numeric_values)/len(numeric_values):.2f}")
    print(f"   Min: {min(numeric_values)}")
    print(f"   Max: {max(numeric_values)}")

    # CFB modulo tests
    addr_sum = sum(numeric_values)
    print(f"\n🎯 CFB NUMBER MODULO TESTS (Sum = {addr_sum}):")
    for cfb in CFB_NUMBERS:
        mod_result = addr_sum % cfb
        print(f"   mod {cfb:3d} = {mod_result:3d}")
        if mod_result == 0:
            print(f"      ⭐ EXACT MATCH! Divisible by {cfb}")
        elif mod_result == cfb - 1:
            print(f"      ⭐ One less than {cfb}!")

    # Length modulo tests
    length = len(addr)
    print(f"\n📏 LENGTH MODULO TESTS (Length = {length}):")
    for cfb in CFB_NUMBERS:
        mod_result = length % cfb
        print(f"   mod {cfb:3d} = {mod_result:3d}")
        if mod_result == 0:
            print(f"      ⭐ EXACT MATCH!")

    return numeric_values

def segment_analysis(addr):
    """Segment-basierte Analyse"""
    print("\n" + "="*80)
    print("🧩 SEGMENT ANALYSIS")
    print("="*80)

    # Split into chunks
    print(f"\n📦 10-character segments:")
    for i in range(0, len(addr), 10):
        segment = addr[i:i+10]
        segment_sum = sum(ord(c) for c in segment)
        print(f"   {i:2d}-{i+9:2d}: {segment:10s} (sum={segment_sum}, mod27={segment_sum%27})")

    # First/Last analysis
    print(f"\n🎯 First/Last character analysis:")
    print(f"   First char: '{addr[0]}' = {ord(addr[0])-ord('A')} (A=0)")
    print(f"   Last char: '{addr[-1]}' = {ord(addr[-1])-ord('A')} (A=0)")
    print(f"   First+Last: {ord(addr[0])-ord('A') + ord(addr[-1])-ord('A')}")

    # POCZ prefix analysis
    prefix = addr[:4]
    print(f"\n🏷️  Prefix 'POCZ' analysis:")
    prefix_values = [ord(c)-ord('A') for c in prefix]
    print(f"   P={prefix_values[0]}, O={prefix_values[1]}, C={prefix_values[2]}, Z={prefix_values[3]}")
    print(f"   Sum: {sum(prefix_values)}")
    print(f"   Product: {prefix_values[0] * prefix_values[1] * prefix_values[2] * prefix_values[3]}")

    # FOBD suffix analysis
    suffix = addr[-4:]
    print(f"\n🏷️  Suffix 'FOBD' analysis:")
    suffix_values = [ord(c)-ord('A') for c in suffix]
    print(f"   F={suffix_values[0]}, O={suffix_values[1]}, B={suffix_values[2]}, D={suffix_values[3]}")
    print(f"   Sum: {sum(suffix_values)}")
    print(f"   Product: {suffix_values[0] * suffix_values[1] * suffix_values[2] * suffix_values[3]}")

def xor_analysis(addr):
    """XOR operations mit verschiedenen keys"""
    print("\n" + "="*80)
    print("⚡ XOR ANALYSIS")
    print("="*80)

    # XOR mit CFB numbers
    print(f"\n🔐 XOR with CFB numbers:")
    for cfb in CFB_NUMBERS:
        result = []
        for i, char in enumerate(addr[:20]):  # First 20 chars
            xor_val = (ord(char) ^ cfb) % 256
            if 32 <= xor_val < 127:  # Printable
                result.append(chr(xor_val))
            else:
                result.append('.')
        xor_string = ''.join(result)
        print(f"   XOR {cfb:3d}: {xor_string}")

    # XOR mit sich selbst (first half vs second half)
    mid = len(addr) // 2
    first_half = addr[:mid]
    second_half = addr[mid:mid+len(first_half)]

    print(f"\n🔄 XOR first half with second half:")
    xor_result = []
    for c1, c2 in zip(first_half, second_half):
        xor_val = ord(c1) ^ ord(c2)
        xor_result.append(xor_val)

    print(f"   XOR values: {xor_result[:20]}...")
    print(f"   Sum: {sum(xor_result)}")
    print(f"   Mod 27: {sum(xor_result) % 27}")
    print(f"   Mod 283: {sum(xor_result) % 283}")

def bitcoin_genesis_comparison(addr):
    """Vergleich mit Bitcoin Genesis Block"""
    print("\n" + "="*80)
    print("₿ BITCOIN GENESIS BLOCK COMPARISON")
    print("="*80)

    genesis = BITCOIN_GENESIS

    print(f"\n📊 Address vs Genesis hash:")
    print(f"   Address length: {len(addr)}")
    print(f"   Genesis length: {len(genesis)}")

    # SHA256 of address
    addr_sha256 = hashlib.sha256(addr.encode()).hexdigest()
    print(f"\n🔐 SHA256(address):")
    print(f"   {addr_sha256}")

    # Compare patterns
    print(f"\n🔍 Pattern comparison:")
    addr_lower = addr.lower()
    common_chars = set(addr_lower) & set(genesis)
    print(f"   Common characters: {len(common_chars)} -> {sorted(common_chars)}")

    # Hash to Bitcoin Genesis style
    print(f"\n🔗 Various hash transformations:")
    print(f"   SHA256: {hashlib.sha256(addr.encode()).hexdigest()[:32]}...")
    print(f"   SHA3-256: {hashlib.sha3_256(addr.encode()).hexdigest()[:32]}...")
    print(f"   BLAKE2b: {hashlib.blake2b(addr.encode(), digest_size=32).hexdigest()[:32]}...")

    # Check for "1" in address (Bitcoin address start)
    if '1' in addr:
        print(f"\n⚠️  Contains '1' (Bitcoin address marker) at positions: {[i for i, c in enumerate(addr) if c == '1']}")

def private_key_pattern_search(addr):
    """Suche nach private key patterns"""
    print("\n" + "="*80)
    print("🔑 PRIVATE KEY PATTERN SEARCH")
    print("="*80)

    # 256-bit private key = 64 hex characters
    # Or 52 base58 characters (WIF)

    print(f"\n🎯 Key format checks:")
    print(f"   Length 60 chars: ✓ (Qubic address format)")
    print(f"   Length 64 chars: ✗ (not hex private key)")
    print(f"   Length 52 chars: ✗ (not WIF)")

    # Try to extract hex-like patterns
    hex_pattern = re.findall(r'[0-9A-F]{8,}', addr)
    if hex_pattern:
        print(f"\n🔍 Hex-like patterns found:")
        for pattern in hex_pattern:
            print(f"   {pattern} (length {len(pattern)})")
    else:
        print(f"\n   No long hex patterns found")

    # Try interpreting as base32 (Qubic uses uppercase letters)
    print(f"\n📝 Base32 interpretation attempt:")
    try:
        # Qubic addresses might be base32-encoded
        import base64
        # Need to pad to multiple of 8
        padded = addr + '=' * (8 - len(addr) % 8) if len(addr) % 8 else addr
        decoded = base64.b32decode(padded)
        print(f"   ✓ Base32 decodes to {len(decoded)} bytes")
        print(f"   Hex: {decoded.hex()[:64]}...")

        # Try as private key
        if len(decoded) == 32:
            print(f"   ⭐ EXACTLY 32 bytes (256-bit private key size!)")
            print(f"   Full hex: {decoded.hex()}")
    except Exception as e:
        print(f"   ✗ Base32 decode failed: {e}")

    # Try direct SHA256 as private key
    print(f"\n🔐 SHA256(address) as potential private key:")
    potential_key = hashlib.sha256(addr.encode()).hexdigest()
    print(f"   {potential_key}")
    print(f"   Length: {len(potential_key)} chars (64 hex = 32 bytes ✓)")

def cfb_signature_search(addr):
    """Suche nach CFB's mathematischen Signaturen"""
    print("\n" + "="*80)
    print("✍️  CFB SIGNATURE PATTERN SEARCH")
    print("="*80)

    # Look for 27, 283, 47, 137, 121 encoded in the address
    print(f"\n🔍 Direct number appearances:")
    for cfb in CFB_NUMBERS:
        if str(cfb) in addr:
            positions = [i for i in range(len(addr)) if addr[i:i+len(str(cfb))] == str(cfb)]
            print(f"   {cfb} found at positions: {positions}")
        else:
            print(f"   {cfb} not found directly")

    # Consecutive character values
    print(f"\n🔢 Consecutive character numeric sequences:")
    for i in range(len(addr)-2):
        if addr[i:i+3].isalpha():
            vals = [ord(c)-ord('A') for c in addr[i:i+3]]
            # Check if forms a CFB number
            num = vals[0]*100 + vals[1]*10 + vals[2]
            if num in CFB_NUMBERS:
                print(f"   Position {i}: '{addr[i:i+3]}' = {vals} = {num} ⭐ CFB NUMBER!")

def compare_with_old_address(addr, old):
    """Detaillierter Vergleich mit alter (falscher) Adresse"""
    print("\n" + "="*80)
    print("🔄 COMPARISON WITH OLD (WRONG) ADDRESS")
    print("="*80)

    print(f"\n📊 Character-by-character comparison:")
    differences = []
    for i, (c1, c2) in enumerate(zip(addr, old)):
        if c1 != c2:
            differences.append({
                'position': i,
                'correct': c1,
                'old': c2,
                'correct_val': ord(c1)-ord('A') if c1.isalpha() else c1,
                'old_val': ord(c2)-ord('A') if c2.isalpha() else c2
            })

    print(f"\n   Total differences: {len(differences)}")
    print(f"\n   Details:")
    for diff in differences:
        print(f"   Pos {diff['position']:2d}: '{diff['correct']}' ({diff['correct_val']}) vs '{diff['old']}' ({diff['old_val']}) old")

    # Analyze what changed
    correct_sum = sum(ord(c) for c in addr)
    old_sum = sum(ord(c) for c in old)

    print(f"\n🔢 Checksum comparison:")
    print(f"   Correct sum: {correct_sum}")
    print(f"   Old sum: {old_sum}")
    print(f"   Difference: {correct_sum - old_sum}")
    print(f"   Correct mod 27: {correct_sum % 27}")
    print(f"   Old mod 27: {old_sum % 27}")

def test_as_bitcoin_private_key(addr):
    """Teste ob Adresse als Bitcoin private key funktioniert"""
    print("\n" + "="*80)
    print("₿ TEST AS BITCOIN PRIVATE KEY")
    print("="*80)

    try:
        import ecdsa
        from ecdsa import SigningKey, SECP256k1

        # Try various derivations
        methods = [
            ("Direct SHA256", hashlib.sha256(addr.encode()).hexdigest()),
            ("SHA256 twice", hashlib.sha256(hashlib.sha256(addr.encode()).digest()).hexdigest()),
            ("SHA3-256", hashlib.sha3_256(addr.encode()).hexdigest()),
            ("BLAKE2b", hashlib.blake2b(addr.encode(), digest_size=32).hexdigest()),
        ]

        print(f"\n🔐 Testing address as private key source:")
        for method_name, private_key_hex in methods:
            try:
                private_key_bytes = bytes.fromhex(private_key_hex)
                sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
                vk = sk.get_verifying_key()
                pubkey = '04' + vk.to_string().hex()

                print(f"\n   ✓ {method_name}:")
                print(f"     Private: {private_key_hex[:32]}...")
                print(f"     Public:  {pubkey[:40]}...")
            except Exception as e:
                print(f"   ✗ {method_name}: {e}")

    except ImportError:
        print(f"   ⚠️  ecdsa library not available")

def main():
    print("\n" + "="*80)
    print("🔥 FORENSISCHE ANALYSE - RICHTIGE GENESIS ISSUER ADRESSE 🔥")
    print("="*80)
    print()

    addr = basic_properties()
    freq = character_frequency_analysis(addr)
    numeric = mathematical_analysis(addr)
    segment_analysis(addr)
    xor_analysis(addr)
    bitcoin_genesis_comparison(addr)
    private_key_pattern_search(addr)
    cfb_signature_search(addr)
    compare_with_old_address(addr, OLD_WRONG_ADDRESS)
    test_as_bitcoin_private_key(addr)

    # Save results
    results = {
        'correct_address': CORRECT_ADDRESS,
        'old_wrong_address': OLD_WRONG_ADDRESS,
        'length': len(CORRECT_ADDRESS),
        'character_frequency': dict(Counter(CORRECT_ADDRESS)),
        'sha256': hashlib.sha256(CORRECT_ADDRESS.encode()).hexdigest(),
        'sha3_256': hashlib.sha3_256(CORRECT_ADDRESS.encode()).hexdigest(),
        'blake2b': hashlib.blake2b(CORRECT_ADDRESS.encode(), digest_size=32).hexdigest(),
    }

    with open('genesis_address_forensic_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*80)
    print("✅ Analysis complete! Results saved to genesis_address_forensic_analysis.json")
    print("="*80)
    print()

if __name__ == "__main__":
    main()
