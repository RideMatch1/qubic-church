#!/usr/bin/env python3
"""
GENERATE ALL POSSIBLE BITCOIN KEYS FROM QUBIC SEEDS
====================================================

Converts ALL 23,765 Qubic Seeds into Bitcoin Private Keys.

Current: 772 keys (3.3%)
Target:  23,765 keys (100%)

Potential: 30x MORE KEYS!
"""

import json
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58

class MassiveKeyGenerator:
    """Generate Bitcoin keys from ALL Qubic seeds"""

    def __init__(self):
        self.seeds = []
        self.generated_keys = []
        self.stats = {
            'total_seeds': 0,
            'successful': 0,
            'failed': 0,
            'duplicates': 0
        }
        self.seen_addresses = set()

    def load_qubic_seeds(self):
        """Load all 23,765 Qubic seeds"""
        print("="*80)
        print("LOADING QUBIC SEEDS")
        print("="*80)

        with open('../public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)

        # Extract seeds (structure may vary)
        if isinstance(data, dict):
            if 'seeds' in data:
                self.seeds = data['seeds']
            elif 'records' in data:
                self.seeds = [r.get('seed', r.get('value', '')) for r in data['records']]
            else:
                # Assume it's a flat list or try total
                self.seeds = data.get('total', [])
        elif isinstance(data, list):
            self.seeds = data

        self.stats['total_seeds'] = len(self.seeds)

        print(f"Loaded {self.stats['total_seeds']} Qubic seeds")
        print()

        if self.stats['total_seeds'] == 0:
            print("ERROR: No seeds loaded!")
            print("Trying alternative extraction...")
            # Try to read raw
            with open('../public/data/qubic-seeds.json', 'r') as f:
                raw = f.read()
                # Extract hex strings manually
                import re
                hex_pattern = r'"([0-9a-f]{40,66})"'
                matches = re.findall(hex_pattern, raw)
                self.seeds = matches[:23765]  # Limit to 23,765

            self.stats['total_seeds'] = len(self.seeds)
            print(f"Extracted {self.stats['total_seeds']} seeds via regex")
            print()

    def seed_to_bitcoin_key(self, seed, index):
        """
        Convert Qubic seed to Bitcoin private key

        Method:
        1. Qubic seed (55-char hex) → SHA256 → 32 bytes
        2. Use as Bitcoin private key
        3. Derive public key (ECDSA secp256k1)
        4. Hash160 (SHA256 + RIPEMD160)
        5. Create Bitcoin address
        """
        try:
            # Ensure seed is valid hex
            if not isinstance(seed, str):
                seed = str(seed)

            # Remove any whitespace
            seed = seed.strip()

            # Method 1: Direct use (if already 32 bytes / 64 hex chars)
            if len(seed) == 64:
                private_key_bytes = bytes.fromhex(seed)
            else:
                # Method 2: Hash to 32 bytes
                private_key_bytes = hashlib.sha256(seed.encode()).digest()

            # Create ECDSA private key
            sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()

            # Uncompressed public key
            public_key = b'\x04' + vk.to_string()

            # Hash160
            sha256_hash = hashlib.sha256(public_key).digest()
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_hash)
            hash160 = ripemd160.digest()

            # Bitcoin address
            versioned = b'\x00' + hash160
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            address = base58.b58encode(versioned + checksum).decode('utf-8')

            # WIF format
            extended = b'\x80' + private_key_bytes + b'\x01'  # Compressed
            wif_checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
            wif = base58.b58encode(extended + wif_checksum).decode('utf-8')

            # Check for duplicates
            if address in self.seen_addresses:
                self.stats['duplicates'] += 1
                return None

            self.seen_addresses.add(address)
            self.stats['successful'] += 1

            return {
                'id': index,
                'seed': seed,
                'privateKeyHex': private_key_bytes.hex(),
                'privateKeyWIF': wif,
                'address': address,
                'hash160': hash160.hex(),
                'compressed': True,
                'validationStatus': 'SUCCESS',
                'method': 'qubic_seed_sha256'
            }

        except Exception as e:
            self.stats['failed'] += 1
            print(f"  Failed seed {index}: {str(e)[:50]}")
            return None

    def generate_all_keys(self):
        """Generate Bitcoin keys from ALL seeds"""
        print("="*80)
        print("GENERATING BITCOIN KEYS FROM ALL SEEDS")
        print("="*80)
        print()

        batch_size = 1000
        total_batches = (self.stats['total_seeds'] + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, self.stats['total_seeds'])

            print(f"Processing batch {batch_num + 1}/{total_batches} (seeds {start_idx}-{end_idx})...")

            for i in range(start_idx, end_idx):
                seed = self.seeds[i]
                key_data = self.seed_to_bitcoin_key(seed, i)

                if key_data:
                    self.generated_keys.append(key_data)

            # Show progress
            progress = (end_idx / self.stats['total_seeds']) * 100
            print(f"  Progress: {progress:.1f}% | Successful: {self.stats['successful']} | Failed: {self.stats['failed']} | Duplicates: {self.stats['duplicates']}")

        print()
        print("="*80)
        print("GENERATION COMPLETE")
        print("="*80)
        print(f"Total Seeds Processed: {self.stats['total_seeds']}")
        print(f"Successful Keys:       {self.stats['successful']}")
        print(f"Failed:                {self.stats['failed']}")
        print(f"Duplicates Skipped:    {self.stats['duplicates']}")
        print(f"Unique Keys Generated: {len(self.generated_keys)}")
        print()

    def export_results(self):
        """Export all generated keys"""
        output = {
            'generationDate': '2026-01-09',
            'total': len(self.generated_keys),
            'source': 'qubic-seeds.json',
            'method': 'SHA256(seed) as private key',
            'stats': self.stats,
            'records': self.generated_keys
        }

        with open('ALL_BITCOIN_KEYS_FROM_SEEDS.json', 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Exported to: ALL_BITCOIN_KEYS_FROM_SEEDS.json")
        print(f"File size: ~{len(json.dumps(output)) // 1024} KB")
        print()

    def show_samples(self):
        """Show first 10 keys as examples"""
        print("="*80)
        print("SAMPLE KEYS (First 10)")
        print("="*80)
        print()

        for i, key in enumerate(self.generated_keys[:10], 1):
            print(f"{i}. Address: {key['address']}")
            print(f"   WIF:     {key['privateKeyWIF']}")
            print(f"   Status:  {key['validationStatus']}")
            print()

def main():
    """Main execution"""
    print("="*80)
    print("MASSIVE BITCOIN KEY GENERATION")
    print("From 23,765 Qubic Seeds")
    print("="*80)
    print()

    generator = MassiveKeyGenerator()

    # Load seeds
    generator.load_qubic_seeds()

    if generator.stats['total_seeds'] == 0:
        print("ERROR: No seeds to process!")
        return

    print(f"Ready to generate up to {generator.stats['total_seeds']} Bitcoin private keys")
    print()

    # Confirm
    response = input("This will take a few minutes. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    print()

    # Generate
    generator.generate_all_keys()

    # Show samples
    generator.show_samples()

    # Export
    generator.export_results()

    # Compare
    print("="*80)
    print("COMPARISON")
    print("="*80)
    print(f"Previous keys (bitcoin-private-keys.json): 772")
    print(f"NEW keys generated:                        {len(generator.generated_keys)}")
    print(f"Increase:                                  {len(generator.generated_keys) - 772}")
    print(f"Total potential:                           {generator.stats['total_seeds']}")
    print()

    print("NEXT STEPS:")
    print("1. Validate all generated keys")
    print("2. Check for blockchain activity")
    print("3. Compare with existing 772 keys")
    print("4. Look for patterns in prefixes")

if __name__ == "__main__":
    main()
