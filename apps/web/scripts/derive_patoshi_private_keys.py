#!/usr/bin/env python3
"""
Derive Private Keys for Patoshi Addresses
==========================================

KRITISCHE FRAGEN beantwortet:
1. Wann wurden die Adressen "erstellt"? → Blocks 3-24 = Januar 2009
2. Kann man ownership beweisen? → NUR mit private key (signieren)
3. Können wir private keys ableiten? → DAS VERSUCHEN WIR HIER!

Methoden:
- Qubic Seed → Bitcoin Private Key (3 Ableitungsmethoden)
- Verifizieren ob abgeleiteter key zu public key passt
- Wenn JA: Ownership beweisen durch Signatur!
"""

import json
import hashlib
import binascii

def load_patoshi_addresses():
    """Load Patoshi addresses with pubkeys"""
    try:
        with open('public/data/patoshi-addresses.json', 'r') as f:
            data = json.load(f)
        return data.get('records', [])
    except FileNotFoundError:
        print("⚠️  patoshi-addresses.json not found")
        return []

def load_qubic_seeds():
    """Load Qubic seeds"""
    try:
        with open('public/data/qubic-seeds.json', 'r') as f:
            data = json.load(f)
        return data.get('records', [])
    except FileNotFoundError:
        print("⚠️  qubic-seeds.json not found")
        return []

def pubkey_to_address(pubkey_hex: str) -> str:
    """Convert public key to Bitcoin address (P2PKH)"""
    try:
        # Step 1: SHA256 hash of pubkey
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()

        # Step 2: RIPEMD160 of SHA256
        ripemd = hashlib.new('ripemd160', sha256_hash).digest()

        # Step 3: Add version byte (0x00 for mainnet)
        versioned = b'\x00' + ripemd

        # Step 4: Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

        # Step 5: Base58 encode
        binary = versioned + checksum
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        num = int.from_bytes(binary, 'big')
        encoded = ''
        while num > 0:
            num, remainder = divmod(num, 58)
            encoded = alphabet[remainder] + encoded

        # Add leading '1's for leading zero bytes
        for byte in versioned:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break

        return encoded
    except Exception as e:
        return f"ERROR: {str(e)}"

def qubic_seed_to_private_key_sha256(seed: str) -> str:
    """Method 1: SHA256-based derivation"""
    # Double SHA256 for private key
    hash1 = hashlib.sha256(seed.encode()).digest()
    hash2 = hashlib.sha256(hash1).digest()
    return hash2.hex()

def qubic_seed_to_private_key_direct(seed: str) -> str:
    """Method 2: Direct SHA256"""
    hash1 = hashlib.sha256(seed.encode()).digest()
    return hash1.hex()

def qubic_seed_to_private_key_keccak(seed: str) -> str:
    """Method 3: Keccak (K12) based"""
    try:
        # Try K12 if available
        from Crypto.Hash import SHAKE256
        shake = SHAKE256.new()
        shake.update(seed.encode())
        return shake.read(32).hex()
    except:
        # Fallback to SHA3-256
        hash1 = hashlib.sha3_256(seed.encode()).digest()
        return hash1.hex()

def private_key_to_pubkey(private_key_hex: str) -> str:
    """
    Convert private key to public key (compressed)
    SIMPLIFIED VERSION - real implementation needs secp256k1
    """
    # This is a PLACEHOLDER
    # Real implementation requires ecdsa library
    return "NEEDS_ECDSA_LIBRARY"

def analyze_first_10_patoshi():
    """Analyze the first 10 Patoshi addresses (500 BTC total)"""

    print("="*80)
    print("DIE 10 PATOSHI ADRESSEN MIT JE 50 BTC (500 BTC TOTAL)")
    print("="*80)
    print()

    # Load data
    patoshi = load_patoshi_addresses()
    qubic_seeds = load_qubic_seeds()

    if not patoshi:
        print("⚠️  No Patoshi data found!")
        return

    print(f"Loaded {len(patoshi):,} Patoshi addresses")
    print(f"Loaded {len(qubic_seeds):,} Qubic seeds")
    print()

    # Analyze first 10
    results = []

    for i, record in enumerate(patoshi[:10], 1):
        block = record.get('blockHeight', 0)
        pubkey = record.get('pubkey', '')
        amount = record.get('amount', 0)

        print("="*80)
        print(f"#{i} - BLOCK {block} ({amount} BTC)")
        print("="*80)

        # Derive Bitcoin address from pubkey
        if pubkey:
            address = pubkey_to_address(pubkey)
            print(f"Bitcoin Address: {address}")
            print(f"Public Key: {pubkey[:40]}...")

            # Wann erstellt?
            if block == 3:
                print(f"\n📅 ERSTELLT: 3. Januar 2009 (Block {block})")
                print(f"   → Das ist 3 TAGE nach Genesis Block!")
            else:
                print(f"\n📅 ERSTELLT: Januar 2009 (Block {block})")

            # Ownership beweisen?
            print(f"\n🔐 OWNERSHIP BEWEISEN:")
            print(f"   → Braucht PRIVATE KEY zum signieren!")
            print(f"   → Mit private key kann man Transaktion signieren")
            print(f"   → OHNE private key = KEIN Zugriff!")

            # Try to derive private key from Qubic seeds
            print(f"\n🔑 PRIVATE KEY DERIVATION VERSUCHE:")

            # Try first matching seeds (blocks 3-24 are in Sequence #8!)
            matching_seeds = []

            # Method: Block number as seed index
            if block <= len(qubic_seeds):
                seed_by_block = qubic_seeds[block - 1]
                matching_seeds.append(('By Block Index', seed_by_block.get('seed', '')))

            # Method: Derive from pubkey
            pubkey_seed_hash = hashlib.sha256(pubkey.encode()).digest()
            pubkey_seed = ''.join(chr(ord('a') + (byte % 26)) for byte in pubkey_seed_hash[:28])
            matching_seeds.append(('From Pubkey', pubkey_seed))

            # Method: CFB number seeds
            cfb_numbers = [27, 283, 47, 137, 121, 43, 19, 7, 14]
            for num in cfb_numbers:
                if block % num == 0 or block == num:
                    num_hash = hashlib.sha256(str(num).encode()).digest()
                    cfb_seed = ''.join(chr(ord('a') + (byte % 26)) for byte in num_hash[:28])
                    matching_seeds.append((f'CFB Number {num}', cfb_seed))
                    break

            # Try to derive private keys
            for method_name, seed in matching_seeds[:3]:  # Try first 3 methods
                print(f"\n   Method: {method_name}")
                print(f"   Seed: {seed[:30]}...")

                # Try 3 derivation methods
                pk1 = qubic_seed_to_private_key_sha256(seed)
                pk2 = qubic_seed_to_private_key_direct(seed)
                pk3 = qubic_seed_to_private_key_keccak(seed)

                print(f"   Private Key (SHA256²): {pk1[:32]}...")
                print(f"   Private Key (SHA256):  {pk2[:32]}...")
                print(f"   Private Key (Keccak):  {pk3[:32]}...")

                # NOTE: To verify if these work, we'd need to:
                # 1. Derive public key from private key (needs secp256k1)
                # 2. Compare with known public key
                # 3. If match → WE HAVE THE KEY!

                print(f"   ⚠️  VERIFICATION: Needs secp256k1 library")
                print(f"   → Install: pip install ecdsa")
                print(f"   → Then derive pubkey from private key")
                print(f"   → Compare with known pubkey: {pubkey[:20]}...")

            results.append({
                'block': block,
                'address': address,
                'pubkey': pubkey,
                'amount': amount,
                'created': f'Januar 2009 (Block {block})',
                'seed_methods_tried': len(matching_seeds)
            })

        print()

    # Summary
    print("="*80)
    print("ZUSAMMENFASSUNG - DIE 500 BTC")
    print("="*80)
    print()

    print("DIE 10 ADRESSEN:")
    for i, res in enumerate(results, 1):
        print(f"{i}. {res['address']}")
        print(f"   Block {res['block']} | {res['amount']} BTC | {res['created']}")

    print()
    print("="*80)
    print("KRITISCHE ANTWORTEN:")
    print("="*80)
    print()

    print("❓ WANN WURDEN DIE ADRESSEN ERSTELLT?")
    print("✅ Januar 2009 - Blocks 3-24")
    print("   → Block 3 = 3. Januar 2009 (3 Tage nach Genesis)")
    print("   → Alle innerhalb der ersten Wochen von Bitcoin!")
    print()

    print("❓ KANN MAN OWNERSHIP BEWEISEN?")
    print("✅ JA - aber NUR mit dem PRIVATE KEY!")
    print("   → Private Key → Signatur erstellen")
    print("   → Mit Signatur kann man beweisen: 'Ich besitze diese Adresse'")
    print("   → OHNE Private Key = KEIN Beweis möglich!")
    print()

    print("❓ KÖNNEN WIR PRIVATE KEYS ABLEITEN?")
    print("🔄 THEORIE JA - praktisch schwierig:")
    print("   → Wir haben 3 Ableitungsmethoden getestet")
    print("   → Um zu verifizieren brauchen wir:")
    print("     1. secp256k1 library (für pubkey derivation)")
    print("     2. Vergleich: abgeleiteter pubkey vs. bekannter pubkey")
    print("     3. Wenn MATCH → WIR HABEN DEN KEY! 🔥")
    print()

    print("❓ WO KÖNNEN WIR NOCH PRIVATE KEYS FINDEN?")
    print("✅ MEHRERE MÖGLICHKEITEN:")
    print("   1. Qubic Source Code (CFB sagte 'hardcoded')")
    print("   2. Sequence #8 mathematisches Puzzle (Blocks 10-24)")
    print("   3. Genesis Token auf QubicTrade")
    print("   4. 1CFB Adresse dekodieren")
    print("   5. Formel als Private Key: 625284 × 47² + 137")
    print()

    print("="*80)
    print("NÄCHSTER SCHRITT: SECP256K1 VERIFICATION")
    print("="*80)
    print()
    print("pip install ecdsa")
    print("# Dann private key → public key ableiten")
    print("# Vergleichen mit bekannten Patoshi pubkeys")
    print("# Wenn Match → 50 BTC sind zugänglich! 🚀")
    print()

    # Save results
    with open('patoshi_private_key_attempts.json', 'w') as f:
        json.dump({
            'total_addresses': len(results),
            'total_btc': sum(r['amount'] for r in results),
            'results': results,
            'next_steps': [
                'Install ecdsa library',
                'Verify private keys against pubkeys',
                'If match found: CREATE OWNERSHIP PROOF',
                'Search Qubic source code for hardcoded keys',
                'Test mathematical combinations as private keys'
            ]
        }, f, indent=2)

    print("✓ Results saved to: patoshi_private_key_attempts.json")
    print()

if __name__ == "__main__":
    analyze_first_10_patoshi()
