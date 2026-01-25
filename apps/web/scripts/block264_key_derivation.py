#!/usr/bin/env python3
"""
BLOCK 264 KEY DERIVATION - ALTERNATIVE METHODS
===============================================

Da K12 die 1CFB Adresse nicht in den 23.765 Seeds gefunden hat,
testen wir alternative Derivationsmethoden basierend auf Block 264 Daten.

FAKTEN:
- 1CFB IST die Block 264 Coinbase (50 BTC, gemined 13.1.2009)
- Block 264 = 8 × 33 (CORE column = 33!)
- Block 264 mod 19 = 17 (Triple Encode Row)
- Block 264 mod 121 = 22
- Block 264 mod 128 = 8

HYPOTHESEN:
1. Private Key = SHA256(Block 264 Hash)
2. Private Key = SHA256(Coinbase Scriptsig)
3. Private Key = K12(Block 264 Header)
4. Private Key aus Matrix Position (8, 33) oder (6, 33)
5. Kombination aus Block-Daten und Qubic Seed
"""

import hashlib
import requests
import json
from pathlib import Path

# Bitcoin Key Generation
try:
    from ecdsa import SECP256k1, SigningKey
    ECDSA_AVAILABLE = True
except ImportError:
    ECDSA_AVAILABLE = False
    print("[!] ecdsa nicht installiert - verwende vereinfachte Methode")

TARGET_ADDRESS = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"

def sha256(data):
    """SHA256 hash"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).digest()

def ripemd160(data):
    """RIPEMD160 hash"""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data):
    """SHA256 + RIPEMD160"""
    return ripemd160(sha256(data))

def private_key_to_address(private_key_bytes):
    """Convert private key bytes to Bitcoin address"""
    if not ECDSA_AVAILABLE:
        return None

    try:
        sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Uncompressed public key
        pub_key = b'\x04' + vk.to_string()

        # Hash160
        h160 = hash160(pub_key)

        # Add version byte
        versioned = b'\x00' + h160

        # Checksum
        checksum = sha256(sha256(versioned))[:4]

        # Base58Check encode
        address_bytes = versioned + checksum

        # Base58 encoding
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = int.from_bytes(address_bytes, 'big')
        result = ''
        while n > 0:
            n, remainder = divmod(n, 58)
            result = ALPHABET[remainder] + result

        # Add leading '1's for leading zero bytes
        for byte in address_bytes:
            if byte == 0:
                result = '1' + result
            else:
                break

        return result
    except Exception as e:
        print(f"  [!] Fehler bei Key-Konvertierung: {e}")
        return None

def get_block_264_data():
    """Fetch Block 264 data from Blockstream API"""
    print("[1] BLOCK 264 DATEN ABRUFEN")
    print("-" * 50)

    try:
        # Get block hash
        url = "https://blockstream.info/api/block-height/264"
        r = requests.get(url, timeout=10)
        block_hash = r.text.strip()
        print(f"  Block Hash: {block_hash}")

        # Get block details
        block_url = f"https://blockstream.info/api/block/{block_hash}"
        block = requests.get(block_url, timeout=10).json()

        # Get coinbase TX
        coinbase_url = f"https://blockstream.info/api/block/{block_hash}/txs/0"
        cb = requests.get(coinbase_url, timeout=10).json()[0]

        scriptsig = cb.get('vin', [{}])[0].get('scriptsig', '')
        print(f"  Coinbase Scriptsig: {scriptsig[:40]}...")

        merkle_root = block.get('merkle_root', '')
        print(f"  Merkle Root: {merkle_root[:40]}...")

        timestamp = block.get('timestamp', 0)
        nonce = block.get('nonce', 0)
        print(f"  Timestamp: {timestamp}")
        print(f"  Nonce: {nonce}")

        return {
            'block_hash': block_hash,
            'merkle_root': merkle_root,
            'scriptsig': scriptsig,
            'timestamp': timestamp,
            'nonce': nonce,
            'bits': block.get('bits', 0),
            'version': block.get('version', 0)
        }
    except Exception as e:
        print(f"  [X] Fehler: {e}")
        return None

def load_matrix_seeds():
    """Load Matrix seeds from qubic-seeds.json"""
    seeds_path = Path(__file__).parent.parent / "public/data/qubic-seeds.json"
    if seeds_path.exists():
        with open(seeds_path) as f:
            return json.load(f)
    return []

def test_derivation_methods(block_data):
    """Test various key derivation methods"""
    print("\n[2] KEY DERIVATION TESTS")
    print("=" * 50)
    print(f"  Ziel-Adresse: {TARGET_ADDRESS}")
    print()

    results = []

    # METHOD 1: Block Hash as Private Key
    print("[2.1] Block Hash → Private Key")
    block_hash_bytes = bytes.fromhex(block_data['block_hash'])
    addr = private_key_to_address(block_hash_bytes)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Block Hash Direct", addr, addr == TARGET_ADDRESS))

    # METHOD 2: SHA256(Block Hash)
    print("\n[2.2] SHA256(Block Hash) → Private Key")
    key = sha256(block_hash_bytes)
    addr = private_key_to_address(key)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("SHA256(Block Hash)", addr, addr == TARGET_ADDRESS))

    # METHOD 3: Coinbase Scriptsig
    print("\n[2.3] SHA256(Coinbase Scriptsig) → Private Key")
    scriptsig_bytes = bytes.fromhex(block_data['scriptsig'])
    key = sha256(scriptsig_bytes)
    addr = private_key_to_address(key)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("SHA256(Scriptsig)", addr, addr == TARGET_ADDRESS))

    # METHOD 4: Double SHA256 (Bitcoin Standard)
    print("\n[2.4] SHA256(SHA256(Block Hash)) → Private Key")
    key = sha256(sha256(block_hash_bytes))
    addr = private_key_to_address(key)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Double SHA256", addr, addr == TARGET_ADDRESS))

    # METHOD 5: Merkle Root
    print("\n[2.5] Merkle Root → Private Key")
    merkle_bytes = bytes.fromhex(block_data['merkle_root'])
    addr = private_key_to_address(merkle_bytes)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Merkle Root Direct", addr, addr == TARGET_ADDRESS))

    # METHOD 6: Block Number as Seed
    print("\n[2.6] '264' als Seed → Private Key")
    key = sha256(b'264')
    addr = private_key_to_address(key)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("'264' as Seed", addr, addr == TARGET_ADDRESS))

    # METHOD 7: Block Hash + "CFB"
    print("\n[2.7] Block Hash + 'CFB' → Private Key")
    combined = block_hash_bytes + b'CFB'
    key = sha256(combined)
    addr = private_key_to_address(key)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Block Hash + CFB", addr, addr == TARGET_ADDRESS))

    # METHOD 8: Timestamp-based
    print("\n[2.8] Timestamp → Private Key")
    ts_bytes = str(block_data['timestamp']).encode()
    key = sha256(ts_bytes)
    addr = private_key_to_address(key)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Timestamp", addr, addr == TARGET_ADDRESS))

    # METHOD 9: Block 264 reversed
    print("\n[2.9] Block Hash (reversed) → Private Key")
    reversed_hash = block_hash_bytes[::-1]
    addr = private_key_to_address(reversed_hash)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Block Hash Reversed", addr, addr == TARGET_ADDRESS))

    # METHOD 10: Nonce-based
    print("\n[2.10] Nonce → Private Key")
    nonce = block_data['nonce']
    nonce_bytes = nonce.to_bytes(32, byteorder='big')
    addr = private_key_to_address(nonce_bytes)
    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
    print(f"  Nonce: {nonce}")
    print(f"  Resultat: {addr}")
    print(f"  Match: {match}")
    results.append(("Nonce Direct", addr, addr == TARGET_ADDRESS))

    return results

def test_matrix_position_keys():
    """Test keys derived from Matrix positions related to 264"""
    print("\n[3] MATRIX POSITION KEYS")
    print("=" * 50)
    print("  264 = 8 × 33 → Row 8, Column 33 (CORE!)")
    print("  CORE Position: (6, 33)")
    print()

    # Load matrix cartography if available
    matrix_path = Path(__file__).parent.parent.parent.parent / "matrix_cartography.json"
    if not matrix_path.exists():
        matrix_path = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

    results = []

    if matrix_path.exists():
        with open(matrix_path) as f:
            matrix = json.load(f)

        # Test positions related to 264
        positions = [
            (8, 33),   # 264 = 8 × 33
            (6, 33),   # CORE position
            (8, 0),    # Row 8
            (0, 33),   # Column 33
            (2, 64),   # 264 = 2 × 132, but 132 mod 128 = 4, so (2, 4)?
        ]

        for row, col in positions:
            key_str = f"{row},{col}"
            if key_str in matrix:
                key_hex = matrix[key_str]
                print(f"  Position ({row}, {col}): {key_hex[:32]}...")

                # Try as private key
                try:
                    key_bytes = bytes.fromhex(key_hex)[:32]  # First 32 bytes
                    addr = private_key_to_address(key_bytes)
                    match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
                    print(f"    → Address: {addr}")
                    print(f"    → {match}")
                    results.append((f"Matrix ({row},{col})", addr, addr == TARGET_ADDRESS))
                except Exception as e:
                    print(f"    → Fehler: {e}")
            else:
                print(f"  Position ({row}, {col}): Nicht in Matrix")
    else:
        print("  [!] matrix_cartography.json nicht gefunden")

    return results

def test_264_mathematical_relations():
    """Test keys based on mathematical properties of 264"""
    print("\n[4] MATHEMATISCHE ABLEITUNGEN")
    print("=" * 50)

    results = []

    # 264 = 8 × 33
    # 264 mod 19 = 17
    # 264 mod 121 = 22
    # 264 mod 27 = 21

    test_values = [
        ("264", 264),
        ("8*33", 8 * 33),
        ("264 mod 19 = 17", 17),
        ("264 mod 121 = 22", 22),
        ("264 mod 27 = 21", 21),
        ("264 - 121 = 143", 143),
        ("264 + 19 = 283", 283),  # Block Prime!
        ("264 * 19 = 5016", 5016),
        ("2299 (Master Formula)", 2299),
        ("264 XOR 121", 264 ^ 121),
    ]

    for name, value in test_values:
        # Convert value to 32-byte key
        key_bytes = value.to_bytes(32, byteorder='big')
        addr = private_key_to_address(key_bytes)
        match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
        print(f"  {name:25} = {value:10} → {addr} {match}")
        results.append((name, addr, addr == TARGET_ADDRESS))

    # Also test SHA256 of these values
    print("\n  SHA256 Ableitungen:")
    for name, value in test_values[:5]:  # First 5
        key = sha256(str(value).encode())
        addr = private_key_to_address(key)
        match = "✅ MATCH!" if addr == TARGET_ADDRESS else "❌"
        print(f"  SHA256({name:15}) → {addr} {match}")
        results.append((f"SHA256({name})", addr, addr == TARGET_ADDRESS))

    return results

def main():
    print("=" * 60)
    print("🔑 BLOCK 264 KEY DERIVATION - ALTERNATIVE METHODS")
    print("=" * 60)
    print()
    print(f"ZIEL: {TARGET_ADDRESS}")
    print(f"BEKANNT: Block 264 Coinbase mit 50 BTC (~$4.8M)")
    print()

    if not ECDSA_AVAILABLE:
        print("⚠️  Installiere ecdsa: pip install ecdsa")
        print()

    # Get Block 264 data
    block_data = get_block_264_data()

    if block_data:
        # Test derivation methods
        all_results = []

        results1 = test_derivation_methods(block_data)
        all_results.extend(results1)

        results2 = test_matrix_position_keys()
        all_results.extend(results2)

        results3 = test_264_mathematical_relations()
        all_results.extend(results3)

        # Summary
        print("\n" + "=" * 60)
        print("📊 ZUSAMMENFASSUNG")
        print("=" * 60)

        matches = [r for r in all_results if r[2]]
        if matches:
            print("\n🎉 TREFFER GEFUNDEN!")
            for method, addr, _ in matches:
                print(f"  ✅ {method}: {addr}")
        else:
            print(f"\n  Getestet: {len(all_results)} Methoden")
            print(f"  Treffer: 0")
            print()
            print("  MÖGLICHE ERKLÄRUNGEN:")
            print("  1. 1CFB wurde mit Vanity-Generator erstellt (Brute-Force)")
            print("  2. Private Key aus anderem Seed + Block-Offset")
            print("  3. Hybride Methode: K12 + Block-Transformation")
            print("  4. Early Bitcoin Mining Software Eigenheit")

        # Save results
        output = {
            "target": TARGET_ADDRESS,
            "block_264": block_data,
            "tests": [{"method": r[0], "address": r[1], "match": r[2]} for r in all_results],
            "matches_found": len(matches)
        }

        with open("BLOCK264_DERIVATION_RESULTS.json", "w") as f:
            json.dump(output, f, indent=2)
        print("\n  Ergebnisse gespeichert: BLOCK264_DERIVATION_RESULTS.json")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
