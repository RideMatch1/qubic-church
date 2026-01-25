#!/usr/bin/env python3
"""
===============================================================================
            🔬 CFB KEY VALIDATION 🔬
===============================================================================
Critical test: Is the "CFB Key" a valid Bitcoin private key?
Does it correspond to any known address?

Key to test: 535e5a396c7c48785b3d143b7c7c2878647b71184d381d0e666d7c3e705c4564
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("           🔬 CFB KEY CRITICAL VALIDATION 🔬")
print("=" * 80)

# The key extracted from CFB column XOR
cfb_key_hex = "535e5a396c7c48785b3d143b7c7c2878647b71184d381d0e666d7c3e705c4564"
cfb_key_bytes = bytes.fromhex(cfb_key_hex)

print(f"\nKey to validate: {cfb_key_hex}")
print(f"Key length: {len(cfb_key_bytes)} bytes = {len(cfb_key_hex)} hex chars")

# ==============================================================================
# TEST 1: Is it a valid secp256k1 private key?
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 1: Valid secp256k1 Private Key?")
print("=" * 80)

# secp256k1 curve order
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

key_int = int(cfb_key_hex, 16)
print(f"\nKey as integer: {key_int}")
print(f"secp256k1 order: {SECP256K1_ORDER}")

if 0 < key_int < SECP256K1_ORDER:
    print("✅ VALID: Key is within valid range for secp256k1")
    valid_btc_key = True
else:
    print("❌ INVALID: Key is outside secp256k1 range")
    valid_btc_key = False

# ==============================================================================
# TEST 2: Derive Bitcoin address (if valid)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 2: Derive Bitcoin Address")
print("=" * 80)

try:
    # Try using ecdsa library
    from ecdsa import SigningKey, SECP256k1
    import ecdsa

    sk = SigningKey.from_string(cfb_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()

    # Compressed public key
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()

    if y % 2 == 0:
        compressed_pubkey = b'\x02' + x.to_bytes(32, 'big')
    else:
        compressed_pubkey = b'\x03' + x.to_bytes(32, 'big')

    print(f"\nCompressed pubkey: {compressed_pubkey.hex()}")

    # Derive P2PKH address
    sha256_hash = hashlib.sha256(compressed_pubkey).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # Add version byte (0x00 for mainnet)
    versioned_payload = b'\x00' + ripemd160_hash

    # Double SHA256 checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]

    # Base58Check encode
    ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    def b58encode(data):
        n = int.from_bytes(data, 'big')
        result = ''
        while n > 0:
            n, r = divmod(n, 58)
            result = ALPHABET[r] + result
        # Add leading zeros
        for byte in data:
            if byte == 0:
                result = '1' + result
            else:
                break
        return result

    address = b58encode(versioned_payload + checksum)
    print(f"Bitcoin Address (P2PKH): {address}")

    derived_address = address
    has_ecdsa = True

except ImportError:
    print("⚠️ ecdsa library not installed, trying alternative...")
    has_ecdsa = False
    derived_address = None

# ==============================================================================
# TEST 3: Check if address exists in our datasets
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 3: Check Against Known Addresses")
print("=" * 80)

# Load our Bitcoin address datasets
datasets = [
    ("Patoshi addresses", script_dir.parent / "public" / "data" / "patoshi-addresses.json"),
    ("Satoshi 145 addresses", script_dir.parent / "public" / "data" / "satoshi-145-addresses.json"),
]

found_in_dataset = False

for name, path in datasets:
    try:
        with open(path) as f:
            data = json.load(f)

        addresses = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key in ['address', 'Address', 'btc_address']:
                        if key in item:
                            addresses.append(item[key])
                elif isinstance(item, str):
                    addresses.append(item)
        elif isinstance(data, dict):
            if 'addresses' in data:
                addresses = data['addresses']

        print(f"\n{name}: {len(addresses)} addresses loaded")

        if derived_address and derived_address in addresses:
            print(f"  🎯 FOUND! Address {derived_address} is in {name}!")
            found_in_dataset = True
        else:
            print(f"  ❌ Not found in {name}")

    except Exception as e:
        print(f"  ⚠️ Error loading {name}: {e}")

# ==============================================================================
# TEST 4: Check blockchain for address activity
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 4: Blockchain Activity Check")
print("=" * 80)

if derived_address:
    import urllib.request
    import urllib.error

    try:
        url = f"https://blockchain.info/rawaddr/{derived_address}?limit=1"
        print(f"\nQuerying: {url}")

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        n_tx = data.get('n_tx', 0)
        total_received = data.get('total_received', 0) / 1e8
        final_balance = data.get('final_balance', 0) / 1e8

        print(f"\n  Address: {derived_address}")
        print(f"  Transactions: {n_tx}")
        print(f"  Total Received: {total_received:.8f} BTC")
        print(f"  Final Balance: {final_balance:.8f} BTC")

        if n_tx > 0:
            print(f"\n  🎯 ADDRESS HAS ACTIVITY!")
            has_activity = True
        else:
            print(f"\n  ❌ No activity - unused address")
            has_activity = False

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  ❌ Address not found in blockchain (never used)")
            has_activity = False
        else:
            print(f"  ⚠️ HTTP Error: {e}")
            has_activity = None
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
        has_activity = None
else:
    print("  ⚠️ No address derived, skipping blockchain check")
    has_activity = None

# ==============================================================================
# TEST 5: How was this key "derived"? Is the method legitimate?
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 5: Key Derivation Method Analysis")
print("=" * 80)

print("""
The "CFB Key" was derived by:
1. Taking column 67 (ASCII 'C') from the matrix
2. XORing with column 70 (ASCII 'F')
3. XORing with column 66 (ASCII 'B')

CRITICAL QUESTIONS:
- Why these specific columns?
- Why XOR operation?
- Is there any cryptographic justification?

ANSWER: This is ARBITRARY.
- We CHOSE columns C, F, B because of "CFB" letters
- Any 3 columns XOR'd together would produce "a key"
- There are C(128,3) = 341,376 possible 3-column combinations
- Each produces a different "key"
- We cherry-picked ONE that happens to spell "CFB"

This is CONFIRMATION BIAS, not discovery!
""")

method_legitimate = False

# ==============================================================================
# TEST 6: Alternative interpretations
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 6: Alternative Key Interpretations")
print("=" * 80)

# Try as WIF
print("\n  As WIF private key: Not valid format (32 bytes, not WIF)")

# Try as Qubic seed
qubic_chars = 'abcdefghijklmnopqrstuvwxyz'
is_valid_qubic_seed = len(cfb_key_hex) == 55 and all(c in qubic_chars for c in cfb_key_hex)
print(f"  As Qubic seed: {'Valid' if is_valid_qubic_seed else 'Invalid (wrong length/chars)'}")

# Try as hash
print(f"  As SHA256 hash: Could be any data's hash (meaningless)")

# ==============================================================================
# FINAL VERDICT
# ==============================================================================
print("\n" + "=" * 80)
print("🔬 FINAL VERDICT ON CFB KEY 🔬")
print("=" * 80)

verdict = {
    "key": cfb_key_hex,
    "valid_secp256k1": valid_btc_key,
    "derived_address": derived_address,
    "found_in_datasets": found_in_dataset,
    "blockchain_activity": has_activity,
    "derivation_method_legitimate": method_legitimate,
}

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   KEY: {cfb_key_hex}   ║
║                                                                               ║
║   ✓ Valid secp256k1 private key: {'YES' if valid_btc_key else 'NO':40}     ║
║   ✓ Derived Bitcoin address: {(derived_address or 'N/A')[:40]:40}     ║
║   ✓ Found in Patoshi/Satoshi datasets: {'YES' if found_in_dataset else 'NO':32}     ║
║   ✓ Blockchain activity: {str(has_activity):44}     ║
║   ✓ Derivation method legitimate: {'NO - ARBITRARY':36}     ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   🔴 CONCLUSION: The "CFB Key" is MEANINGLESS.                               ║
║                                                                               ║
║   While it IS a valid Bitcoin private key (any 32 bytes in range are),       ║
║   the derivation method is ARBITRARY and amounts to numerology.              ║
║                                                                               ║
║   We chose columns 67, 70, 66 (C, F, B) BECAUSE they spell CFB.             ║
║   This is circular reasoning, not discovery.                                 ║
║                                                                               ║
║   There are 341,376 ways to XOR 3 columns together.                         ║
║   Finding one that "means something" is CONFIRMATION BIAS.                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "key": cfb_key_hex,
    "tests": {
        "valid_secp256k1": valid_btc_key,
        "derived_address": derived_address,
        "found_in_datasets": found_in_dataset,
        "blockchain_activity": has_activity,
        "derivation_method_legitimate": method_legitimate,
    },
    "conclusion": "The CFB Key is a valid Bitcoin private key but was derived through arbitrary column selection (C=67, F=70, B=66). This is confirmation bias, not a real discovery. Any 3 columns XOR'd produce a 'key' - we cherry-picked one that spells CFB.",
    "recommendation": "DISCARD this finding. Focus on mathematically proven properties like the 99.58% point symmetry.",
}

output_path = script_dir / "CFB_KEY_VALIDATION_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved: {output_path}")
