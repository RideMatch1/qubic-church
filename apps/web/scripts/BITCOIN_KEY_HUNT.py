#!/usr/bin/env python3
"""
===============================================================================
   🔑 BITCOIN PRIVATE KEY HUNT 🔑
===============================================================================
Die Qubic Seeds haben 0 Balance - vielleicht ist der Schatz ein BITCOIN Key!

Methoden:
1. Matrix-Werte als Private Key
2. Bridge-Zellen Koordinaten als Key
3. "key" Position (107,127) als Hinweis
4. XOR-Ergebnisse als Keys
5. SHA256 von Mustern
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
import hashlib

# Try to import Bitcoin libraries
try:
    from bitcoin import privkey_to_pubkey, pubkey_to_address
    BITCOIN_LIB = True
except ImportError:
    BITCOIN_LIB = False

try:
    import ecdsa
    import binascii
    ECDSA_LIB = True
except ImportError:
    ECDSA_LIB = False

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗ ██╗████████╗ ██████╗ ██████╗ ██╗███╗   ██╗
   ██╔══██╗██║╚══██╔══╝██╔════╝██╔═══██╗██║████╗  ██║
   ██████╔╝██║   ██║   ██║     ██║   ██║██║██╔██╗ ██║
   ██╔══██╗██║   ██║   ██║     ██║   ██║██║██║╚██╗██║
   ██████╔╝██║   ██║   ╚██████╗╚██████╔╝██║██║ ╚████║
   ╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝
              🔑 BITCOIN KEY HUNT 🔑
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def private_key_to_address(private_key_hex):
    """Convert private key to Bitcoin address (simplified)"""
    if len(private_key_hex) != 64:
        return None

    try:
        # Validate hex
        int(private_key_hex, 16)

        if ECDSA_LIB:
            # Use ecdsa library
            sk = ecdsa.SigningKey.from_string(
                bytes.fromhex(private_key_hex),
                curve=ecdsa.SECP256k1
            )
            vk = sk.get_verifying_key()
            public_key = b'\x04' + vk.to_string()

            # SHA256 then RIPEMD160
            sha256 = hashlib.sha256(public_key).digest()
            ripemd160 = hashlib.new('ripemd160', sha256).digest()

            # Add version byte (0x00 for mainnet)
            versioned = b'\x00' + ripemd160

            # Double SHA256 for checksum
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]

            # Base58 encode
            address_bytes = versioned + checksum

            # Simple base58 encoding
            alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(address_bytes, 'big')
            result = ''
            while num > 0:
                num, rem = divmod(num, 58)
                result = alphabet[rem] + result

            # Add leading 1s for leading zero bytes
            for byte in address_bytes:
                if byte == 0:
                    result = '1' + result
                else:
                    break

            return result
        else:
            return f"[Need ecdsa lib] Key: {private_key_hex[:16]}..."

    except Exception as e:
        return None

# ==============================================================================
# METHOD 1: BRIDGE CELLS AS BITCOIN KEY
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 1: BRIDGE CELLS COORDINATES AS BITCOIN KEY")
print("=" * 80)

bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

# Method 1a: Coordinates as hex bytes
coords_hex = ''.join(f'{r:02x}{c:02x}' for r, c in bridge_cells)
print(f"\n  Bridge coordinates as hex: {coords_hex}")
print(f"  Length: {len(coords_hex)} chars (need 64 for Bitcoin key)")

# Pad to 64 chars
coords_hex_padded = coords_hex.ljust(64, '0')
print(f"  Padded to 64: {coords_hex_padded}")

addr = private_key_to_address(coords_hex_padded)
if addr:
    print(f"  Bitcoin Address: {addr}")

# Method 1b: SHA256 of coordinates
coords_bytes = bytes([r for r, c in bridge_cells] + [c for r, c in bridge_cells])
coords_sha256 = hashlib.sha256(coords_bytes).hexdigest()
print(f"\n  SHA256 of coordinates: {coords_sha256}")

addr = private_key_to_address(coords_sha256)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 2: "KEY" POSITION VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 2: 'KEY' POSITION (107-109, 127) AS SEED")
print("=" * 80)

key_values = [int(matrix[107, 127]), int(matrix[108, 127]), int(matrix[109, 127])]
print(f"\n  'key' values: {key_values}")
print(f"  As hex: {' '.join(f'{abs(v):02x}' for v in key_values)}")

# Use row 107 as potential key source
row107 = [int(matrix[107, c]) for c in range(128)]
row107_hex = ''.join(f'{abs(v):02x}' for v in row107[:32])
print(f"\n  Row 107 (first 32 bytes) as hex: {row107_hex}")

addr = private_key_to_address(row107_hex)
if addr:
    print(f"  Bitcoin Address: {addr}")

# SHA256 of row 107
row107_sha = hashlib.sha256(bytes([abs(v) % 256 for v in row107])).hexdigest()
print(f"\n  SHA256 of Row 107: {row107_sha}")

addr = private_key_to_address(row107_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 3: COLUMN 127 (WHERE "KEY" WAS FOUND)
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 3: COLUMN 127 AS BITCOIN KEY")
print("=" * 80)

col127 = [int(matrix[r, 127]) for r in range(128)]

# Direct hex
col127_hex = ''.join(f'{abs(v):02x}' for v in col127[:32])
print(f"\n  Column 127 (first 32 bytes) as hex: {col127_hex}")

addr = private_key_to_address(col127_hex)
if addr:
    print(f"  Bitcoin Address: {addr}")

# SHA256
col127_sha = hashlib.sha256(bytes([abs(v) % 256 for v in col127])).hexdigest()
print(f"\n  SHA256 of Column 127: {col127_sha}")

addr = private_key_to_address(col127_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 4: DIAGONAL VALUES
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 4: MAIN DIAGONAL AS BITCOIN KEY")
print("=" * 80)

diagonal = [int(matrix[i, i]) for i in range(128)]

# First 32 bytes
diag_hex = ''.join(f'{abs(v):02x}' for v in diagonal[:32])
print(f"\n  Diagonal (first 32 bytes) as hex: {diag_hex}")

addr = private_key_to_address(diag_hex)
if addr:
    print(f"  Bitcoin Address: {addr}")

# SHA256
diag_sha = hashlib.sha256(bytes([abs(v) % 256 for v in diagonal])).hexdigest()
print(f"\n  SHA256 of Diagonal: {diag_sha}")

addr = private_key_to_address(diag_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 5: XOR PATTERNS AS KEYS
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 5: XOR PATTERNS AS BITCOIN KEYS")
print("=" * 80)

# Row 13 XOR Row 114 (longest palindrome)
row13 = [int(matrix[13, c]) for c in range(128)]
row114 = [int(matrix[114, c]) for c in range(128)]
xor_13_114 = [row13[i] ^ row114[i] for i in range(128)]

xor_hex = ''.join(f'{abs(v):02x}' for v in xor_13_114[:32])
print(f"\n  Row 13 ⊕ Row 114 (first 32 bytes): {xor_hex}")

addr = private_key_to_address(xor_hex)
if addr:
    print(f"  Bitcoin Address: {addr}")

# SHA256 of XOR
xor_sha = hashlib.sha256(bytes([abs(v) % 256 for v in xor_13_114])).hexdigest()
print(f"\n  SHA256 of XOR result: {xor_sha}")

addr = private_key_to_address(xor_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 6: "mmmmcceeii" DERIVATIONS
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 6: 'mmmmcceeii' AS BITCOIN KEY SEED")
print("=" * 80)

# SHA256 of mmmmcceeii
mmm_sha = hashlib.sha256(b"mmmmcceeii").hexdigest()
print(f"\n  SHA256('mmmmcceeii'): {mmm_sha}")

addr = private_key_to_address(mmm_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# Double SHA256
mmm_double_sha = hashlib.sha256(bytes.fromhex(mmm_sha)).hexdigest()
print(f"\n  Double SHA256: {mmm_double_sha}")

addr = private_key_to_address(mmm_double_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# The values 12, 2, 4, 8 as key
values_key = '0c020408' * 8  # Repeat to get 64 chars
print(f"\n  Values 12,2,4,8 repeated: {values_key}")

addr = private_key_to_address(values_key)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 7: ENTIRE MATRIX HASH
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 7: ENTIRE MATRIX AS KEY SOURCE")
print("=" * 80)

# SHA256 of entire matrix
matrix_bytes = matrix.astype(np.int8).tobytes()
matrix_sha = hashlib.sha256(matrix_bytes).hexdigest()
print(f"\n  SHA256 of entire matrix: {matrix_sha}")

addr = private_key_to_address(matrix_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# METHOD 8: SPECIFIC PATTERNS
# ==============================================================================
print("\n" + "=" * 80)
print("METHOD 8: SPECIAL PATTERNS")
print("=" * 80)

# (42, 63) - "The Answer" position
answer_row = [int(matrix[42, c]) for c in range(128)]
answer_sha = hashlib.sha256(bytes([abs(v) % 256 for v in answer_row])).hexdigest()
print(f"\n  SHA256 of Row 42 ('The Answer'): {answer_sha}")

addr = private_key_to_address(answer_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# Value 127 appears at 8 positions - use all of them
bridge_values_row = [int(matrix[r, c]) for r, c in bridge_cells]
bridge_context = []
for r, c in bridge_cells:
    # Get 4 neighbors
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < 128 and 0 <= nc < 128:
            bridge_context.append(abs(int(matrix[nr, nc])))

bridge_context_sha = hashlib.sha256(bytes(bridge_context[:32])).hexdigest()
print(f"\n  SHA256 of bridge cell neighbors: {bridge_context_sha}")

addr = private_key_to_address(bridge_context_sha)
if addr:
    print(f"  Bitcoin Address: {addr}")

# ==============================================================================
# COLLECT ALL POTENTIAL KEYS
# ==============================================================================
print("\n" + "=" * 80)
print("📋 ALL POTENTIAL BITCOIN PRIVATE KEYS")
print("=" * 80)

all_keys = [
    ("Bridge coords padded", coords_hex_padded),
    ("Bridge coords SHA256", coords_sha256),
    ("Row 107 hex", row107_hex),
    ("Row 107 SHA256", row107_sha),
    ("Column 127 hex", col127_hex),
    ("Column 127 SHA256", col127_sha),
    ("Diagonal hex", diag_hex),
    ("Diagonal SHA256", diag_sha),
    ("XOR 13⊕114 hex", xor_hex),
    ("XOR 13⊕114 SHA256", xor_sha),
    ("mmmmcceeii SHA256", mmm_sha),
    ("mmmmcceeii double SHA", mmm_double_sha),
    ("12,2,4,8 repeated", values_key),
    ("Matrix SHA256", matrix_sha),
    ("Row 42 SHA256", answer_sha),
    ("Bridge neighbors SHA256", bridge_context_sha),
]

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    POTENTIAL BITCOIN PRIVATE KEYS                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
""")

for name, key in all_keys:
    addr = private_key_to_address(key)
    print(f"║  {name}:")
    print(f"║    Key: {key}")
    if addr:
        print(f"║    Address: {addr}")
    print(f"║")

print("╚═══════════════════════════════════════════════════════════════════════════════╝")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "potential_keys": [
        {"name": name, "private_key": key, "address": private_key_to_address(key)}
        for name, key in all_keys
    ],
    "instructions": "Check each address on blockchain.info or blockchair.com for balance"
}

with open(script_dir / "BITCOIN_KEY_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✓ Results saved to BITCOIN_KEY_RESULTS.json")

print(f"""

{'='*80}
🎯 NEXT STEPS
{'='*80}

1. Check each Bitcoin address for balance:
   https://www.blockchain.com/explorer/addresses/btc/[ADDRESS]

2. If any has balance, the private key is the treasure!

3. Import into a Bitcoin wallet to access funds

⚠️  IMPORTANT: Never share private keys publicly!
    These are derived from public matrix data.
""")
