#!/usr/bin/env python3
"""
ANALYZE 1CFi METHOD
===================

Analysiert die Generierungs-Methode der 1CFiVYy5... Adresse.
Sie hat IDENTISCHE mathematische Eigenschaften wie die echte 1CFB!

Ziel: Methode rekonstruieren und auf 1CFB anwenden!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58

class CFiMethodAnalyzer:
    """Analysiert die 1CFi Generierungs-Methode"""

    def __init__(self):
        self.cfi_data = {
            "address": "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi",
            "privateKeyHex": "f08e3057f5ca5c6156ddcb5b7829fc12f5752821378275a9e48630439a8f17a9",
            "privateKeyWIF": "L5HKU27h5uS4Mq3KTNkSTvKVJqbe174unP2K3g4q5JcxZHXrcKnx",
            "position": [91, 20],
            "method": "step27",
            "xorVariant": 13,
            "hash160": "7b71d7d43a0fb43b1832f63cc4913b30e6522791"
        }

        self.cfb_target = {
            "address": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
            "hash160": "7b581609d8f9b74c34f7648c3b79fd8a6848022d"
        }

    def analyze_cfi_properties(self):
        """Analysiere die 1CFi Adresse im Detail"""
        print("="*80)
        print("1CFi ADDRESS ANALYSIS")
        print("="*80)
        print()

        print("ADDRESS PROPERTIES:")
        print(f"  Address:     {self.cfi_data['address']}")
        print(f"  Hash160:     {self.cfi_data['hash160']}")
        print(f"  Private Key: {self.cfi_data['privateKeyHex']}")
        print()

        # Byte Sum Analysis
        hash160_bytes = bytes.fromhex(self.cfi_data['hash160'])
        byte_sum = sum(hash160_bytes)

        print("MATHEMATICAL PROPERTIES:")
        print(f"  Byte Sum:    {byte_sum}")
        print(f"  mod 121:     {byte_sum % 121}")
        print(f"  mod 19:      {byte_sum % 19}")
        print(f"  mod 27:      {byte_sum % 27}")
        print(f"  mod 13:      {byte_sum % 13}")
        print()

        print("GENERATION METHOD:")
        print(f"  Position:    {self.cfi_data['position']}")
        print(f"  Method:      {self.cfi_data['method']}")
        print(f"  XOR Variant: {self.cfi_data['xorVariant']}")
        print()

    def compare_with_cfb(self):
        """Vergleiche mit der echten 1CFB"""
        print("="*80)
        print("COMPARISON: 1CFi vs 1CFB")
        print("="*80)
        print()

        # 1CFi Properties
        cfi_bytes = bytes.fromhex(self.cfi_data['hash160'])
        cfi_sum = sum(cfi_bytes)

        # 1CFB Properties
        cfb_bytes = bytes.fromhex(self.cfb_target['hash160'])
        cfb_sum = sum(cfb_bytes)

        print("1CFi (FOUND in original 772):")
        print(f"  Address:     {self.cfi_data['address']}")
        print(f"  Hash160:     {self.cfi_data['hash160']}")
        print(f"  Byte Sum:    {cfi_sum}")
        print(f"  mod 121:     {cfi_sum % 121}")
        print(f"  mod 19:      {cfi_sum % 19}")
        print()

        print("1CFB (TARGET - real CFB address):")
        print(f"  Address:     {self.cfb_target['address']}")
        print(f"  Hash160:     {self.cfb_target['hash160']}")
        print(f"  Byte Sum:    {cfb_sum}")
        print(f"  mod 121:     {cfb_sum % 121}")
        print(f"  mod 19:      {cfb_sum % 19}")
        print()

        print("COMPARISON:")
        print(f"  Both have mod 121 = 0: {'YES' if cfi_sum % 121 == 0 and cfb_sum % 121 == 0 else 'NO'}")
        print(f"  Both have mod 19 = 0:  {'YES' if cfi_sum % 19 == 0 and cfb_sum % 19 == 0 else 'NO'}")
        print(f"  Same byte sum (2299):  {'YES' if cfi_sum == cfb_sum == 2299 else 'NO'}")
        print()

        # XOR Analysis
        xor_result = bytes(a ^ b for a, b in zip(cfi_bytes, cfb_bytes))
        xor_sum = sum(xor_result)

        print("XOR ANALYSIS (1CFi XOR 1CFB):")
        print(f"  XOR Result:  {xor_result.hex()}")
        print(f"  XOR Sum:     {xor_sum}")
        print(f"  mod 121:     {xor_sum % 121}")
        print(f"  mod 19:      {xor_sum % 19}")
        print()

    def load_qubic_seed_at_position(self):
        """Versuche den Qubic Seed an Position [91,20] zu laden"""
        print("="*80)
        print("LOADING QUBIC SEED AT POSITION [91, 20]")
        print("="*80)
        print()

        try:
            with open('../public/data/qubic-seeds.json', 'r') as f:
                data = json.load(f)

            # Anna Matrix ist 128x128
            # Position [91, 20] = row 91, col 20
            # Index = 91 * 128 + 20 = 11668

            index = 91 * 128 + 20
            print(f"Calculated index: {index}")

            if isinstance(data, list) and len(data) > index:
                seed = data[index]
                print(f"Seed at [91,20]: {seed}")
                return seed
            elif isinstance(data, dict) and 'records' in data:
                if len(data['records']) > index:
                    seed = data['records'][index].get('seed', data['records'][index].get('value', ''))
                    print(f"Seed at [91,20]: {seed}")
                    return seed

            print("Could not extract seed from qubic-seeds.json structure")
            return None

        except Exception as e:
            print(f"Error loading seed: {e}")
            return None

    def test_step27_xor13_method(self, seed):
        """Teste die step27 + xorVariant 13 Methode"""
        print()
        print("="*80)
        print("TESTING: step27 + XOR Variant 13")
        print("="*80)
        print()

        if not seed:
            print("No seed provided, skipping...")
            return

        print(f"Input Seed: {seed[:50]}...")
        print()

        # Vermutung: "step27" bedeutet +27 zu jedem Byte
        # "xorVariant 13" bedeutet XOR mit 13

        # Versuch 1: SHA256(seed) + 27 + XOR 13
        print("Attempt 1: SHA256(seed) → +27 → XOR 13")
        base_hash = hashlib.sha256(seed.encode()).digest()
        print(f"  SHA256(seed): {base_hash.hex()[:40]}...")

        # Apply step27: add 27 to each byte
        step27_result = bytes((b + 27) % 256 for b in base_hash)
        print(f"  After +27:    {step27_result.hex()[:40]}...")

        # Apply XOR 13
        xor13_result = bytes(b ^ 13 for b in step27_result)
        print(f"  After XOR 13: {xor13_result.hex()[:40]}...")

        # Check if this matches the known private key
        if xor13_result.hex() == self.cfi_data['privateKeyHex']:
            print("\n  *** MATCH FOUND! This is the correct method! ***")
            return xor13_result
        else:
            print(f"\n  No match. Expected: {self.cfi_data['privateKeyHex'][:40]}...")
            print(f"            Got:      {xor13_result.hex()[:40]}...")

        # Versuch 2: Andere Reihenfolge
        print("\nAttempt 2: SHA256(seed) → XOR 13 → +27")
        xor13_first = bytes(b ^ 13 for b in base_hash)
        step27_second = bytes((b + 27) % 256 for b in xor13_first)

        if step27_second.hex() == self.cfi_data['privateKeyHex']:
            print("\n  *** MATCH FOUND! This is the correct method! ***")
            return step27_second
        else:
            print(f"  No match. Got: {step27_second.hex()[:40]}...")

        # Versuch 3: Direkt ohne SHA256?
        print("\nAttempt 3: Direct seed bytes → +27 → XOR 13")
        try:
            seed_bytes = bytes.fromhex(seed) if len(seed) == 64 else hashlib.sha256(seed.encode()).digest()
            direct_step27 = bytes((b + 27) % 256 for b in seed_bytes)
            direct_xor13 = bytes(b ^ 13 for b in direct_step27)

            if direct_xor13.hex() == self.cfi_data['privateKeyHex']:
                print("\n  *** MATCH FOUND! This is the correct method! ***")
                return direct_xor13
            else:
                print(f"  No match. Got: {direct_xor13.hex()[:40]}...")
        except:
            print("  Could not convert seed to bytes")

        print("\nNone of the methods matched. The actual algorithm may be more complex.")
        return None

    def apply_method_to_find_1cfb(self, method_func):
        """Wende die gefundene Methode an um 1CFB zu finden"""
        print()
        print("="*80)
        print("APPLYING METHOD TO FIND 1CFB")
        print("="*80)
        print()

        if not method_func:
            print("No method found to apply")
            return

        # Lade alle Seeds
        print("Loading all Qubic seeds to test...")
        with open('../public/data/qubic-seeds.json', 'r') as f:
            seeds_data = json.load(f)

        if isinstance(seeds_data, list):
            seeds = seeds_data[:1000]  # Test first 1000
        elif isinstance(seeds_data, dict) and 'records' in seeds_data:
            seeds = [r.get('seed', r.get('value', '')) for r in seeds_data['records'][:1000]]
        else:
            print("Cannot extract seeds")
            return

        print(f"Testing {len(seeds)} seeds...")
        print()

        # Test each seed
        for i, seed in enumerate(seeds):
            if i % 100 == 0:
                print(f"  Testing seed {i}/{len(seeds)}...")

            # Apply method
            private_key = method_func(seed)
            if not private_key:
                continue

            # Derive address
            try:
                sk = SigningKey.from_string(private_key, curve=SECP256k1)
                vk = sk.get_verifying_key()
                public_key = b'\x04' + vk.to_string()

                sha256_hash = hashlib.sha256(public_key).digest()
                ripemd160 = hashlib.new('ripemd160')
                ripemd160.update(sha256_hash)
                hash160 = ripemd160.digest()

                versioned = b'\x00' + hash160
                checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
                address = base58.b58encode(versioned + checksum).decode('utf-8')

                # Check if it's 1CFB!
                if address == self.cfb_target['address']:
                    print(f"\n*** FOUND 1CFB!!! ***")
                    print(f"  Seed:        {seed}")
                    print(f"  Private Key: {private_key.hex()}")
                    print(f"  Address:     {address}")
                    return True

            except:
                continue

        print("\n1CFB not found in tested seeds.")
        return False

def main():
    """Main execution"""
    print("="*80)
    print("ANALYZING 1CFi GENERATION METHOD")
    print("="*80)
    print()

    analyzer = CFiMethodAnalyzer()

    # Analyze 1CFi
    analyzer.analyze_cfi_properties()

    # Compare with 1CFB
    analyzer.compare_with_cfb()

    # Load seed
    seed = analyzer.load_qubic_seed_at_position()

    # Test method
    if seed:
        method_result = analyzer.test_step27_xor13_method(seed)

        # If we found the method, try to apply it
        if method_result:
            # Create method function
            def method_func(s):
                base = hashlib.sha256(s.encode()).digest()
                step27 = bytes((b + 27) % 256 for b in base)
                xor13 = bytes(b ^ 13 for b in step27)
                return xor13

            analyzer.apply_method_to_find_1cfb(method_func)

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
