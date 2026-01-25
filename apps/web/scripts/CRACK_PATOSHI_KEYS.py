#!/usr/bin/env python3
"""
===============================================================================
   💰 CRACK PATOSHI PRIVATE KEYS 💰
===============================================================================
Die Bridge-Blocks (1776, 2115, 4263, 5151) haben je 50 BTC die NIE bewegt wurden!
Vielleicht enthält die Matrix den Schlüssel zu diesen Wallets?

Block 1776: 50 BTC = ~$5,000,000 (bei $100k/BTC)
Block 2115: 50 BTC = ~$5,000,000
Block 4263: 50 BTC = ~$5,000,000
Block 5151: 50 BTC = ~$5,000,000
TOTAL: 200 BTC = ~$20,000,000 !!!
===============================================================================
"""

import json
import hashlib
import numpy as np
from pathlib import Path

try:
    import ecdsa
    ECDSA_LIB = True
except:
    ECDSA_LIB = False

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗██████╗  █████╗  ██████╗██╗  ██╗
  ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
  ██║     ██████╔╝███████║██║     █████╔╝
  ██║     ██╔══██╗██╔══██║██║     ██╔═██╗
  ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗
   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
   💰 PATOSHI PRIVATE KEY CRACKER 💰
   Target: 200 BTC (~$20,000,000)
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# Load Patoshi data
patoshi_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"
with open(patoshi_path) as f:
    patoshi_data = json.load(f)

block_lookup = {r['blockHeight']: r for r in patoshi_data['records']}

# Target blocks
target_blocks = {
    1776: (17, 76),
    2115: (21, 15),
    4263: (42, 63),
    5151: (51, 51),
}

def pubkey_to_address(pubkey_hex):
    """Convert public key to Bitcoin address"""
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha256 = hashlib.sha256(pubkey_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    versioned = b'\x00' + ripemd160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    address_bytes = versioned + checksum

    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(address_bytes, 'big')
    result = ''
    while num > 0:
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result
    for byte in address_bytes:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result

def private_key_to_pubkey(private_key_hex):
    """Derive public key from private key"""
    if not ECDSA_LIB:
        return None
    try:
        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(private_key_hex),
            curve=ecdsa.SECP256k1
        )
        vk = sk.get_verifying_key()
        return '04' + vk.to_string().hex()
    except:
        return None

def check_key(private_key_hex, target_pubkey):
    """Check if private key matches target public key"""
    derived_pubkey = private_key_to_pubkey(private_key_hex)
    if derived_pubkey:
        return derived_pubkey.lower() == target_pubkey.lower()
    return False

print("\n📋 TARGET BLOCKS:")
for block, (r, c) in target_blocks.items():
    info = block_lookup.get(block)
    if info:
        addr = pubkey_to_address(info['pubkey'])
        print(f"\n  Block {block} (from {r},{c}):")
        print(f"    Pubkey: {info['pubkey'][:32]}...")
        print(f"    Address: {addr}")
        print(f"    Amount: {info['amount']} BTC 💰")

print("\n" + "=" * 80)
print("🔑 ATTEMPTING PRIVATE KEY DERIVATION")
print("=" * 80)

# Strategy: Use matrix values in various ways to derive private keys
# The key insight: The row/col of the bridge cell might be the key!

attempts = []

for block, (r, c) in target_blocks.items():
    target_pubkey = block_lookup[block]['pubkey']
    target_addr = pubkey_to_address(target_pubkey)

    print(f"\n🎯 Block {block} (Target: {target_addr[:20]}...)")

    # Method 1: Row as key seed
    row_data = [abs(int(matrix[r, col])) % 256 for col in range(128)]
    row_sha = hashlib.sha256(bytes(row_data[:32])).hexdigest()

    # Method 2: Column as key seed
    col_data = [abs(int(matrix[row, c])) % 256 for row in range(128)]
    col_sha = hashlib.sha256(bytes(col_data[:32])).hexdigest()

    # Method 3: Row XOR Column
    xor_data = [row_data[i] ^ col_data[i] for i in range(128)]
    xor_sha = hashlib.sha256(bytes(xor_data[:32])).hexdigest()

    # Method 4: Block number as part of key
    block_bytes = block.to_bytes(4, 'big') + bytes(row_data[:28])
    block_sha = hashlib.sha256(block_bytes).hexdigest()

    # Method 5: r,c as coordinates into deeper matrix structure
    cell_value = int(matrix[r, c])
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 128 and 0 <= nc < 128:
                neighbors.append(abs(int(matrix[nr, nc])) % 256)
    neighbor_sha = hashlib.sha256(bytes(neighbors * 4)[:32]).hexdigest()

    # Method 6: Symmetric position
    sym_r, sym_c = 127 - r, 127 - c
    sym_value = int(matrix[sym_r, sym_c])
    sym_data = [abs(int(matrix[sym_r, col])) % 256 for col in range(128)]
    sym_sha = hashlib.sha256(bytes(sym_data[:32])).hexdigest()

    # Method 7: XOR with symmetric row
    sym_xor = [row_data[i] ^ sym_data[i] for i in range(128)]
    sym_xor_sha = hashlib.sha256(bytes(sym_xor[:32])).hexdigest()

    # Method 8: Block + Row + Col encoded
    encoded = f"{block}{r:03d}{c:03d}".encode()
    encoded_sha = hashlib.sha256(encoded).hexdigest()

    # Method 9: Using the "key" position (107, 127)
    key_row = [abs(int(matrix[107, col])) % 256 for col in range(128)]
    key_context = key_row[:16] + row_data[:16]
    key_sha = hashlib.sha256(bytes(key_context)).hexdigest()

    # Method 10: Pubkey XOR with matrix
    pk_bytes = bytes.fromhex(target_pubkey)[:32]
    pk_xor = [pk_bytes[i] ^ row_data[i] for i in range(32)]
    # If the private key was used to XOR with matrix, this should be it!
    pk_xor_hex = bytes(pk_xor).hex()

    methods = [
        ("Row SHA256", row_sha),
        ("Col SHA256", col_sha),
        ("Row⊕Col SHA256", xor_sha),
        ("Block+Row SHA256", block_sha),
        ("Neighbors SHA256", neighbor_sha),
        ("Symmetric SHA256", sym_sha),
        ("Row⊕Symmetric SHA256", sym_xor_sha),
        ("Encoded SHA256", encoded_sha),
        ("Key Context SHA256", key_sha),
        ("Pubkey⊕Row", pk_xor_hex),
    ]

    for method_name, key in methods:
        if len(key) == 64:
            match = check_key(key, target_pubkey)
            if match:
                print(f"  ✅ {method_name}: MATCH! 🎉🎉🎉")
                attempts.append((block, method_name, key, True))
            else:
                derived_pk = private_key_to_pubkey(key)
                if derived_pk:
                    derived_addr = pubkey_to_address(derived_pk)
                    attempts.append((block, method_name, key, False, derived_addr))

# Advanced: Try using row/col directly as private key bytes
print("\n" + "=" * 80)
print("🔬 ADVANCED METHODS")
print("=" * 80)

for block, (r, c) in target_blocks.items():
    target_pubkey = block_lookup[block]['pubkey']

    print(f"\n🎯 Block {block}:")

    # Direct row as key
    row_direct = ''.join(f'{abs(int(matrix[r, col])):02x}' for col in range(32))

    # Row with offset based on column
    row_offset = ''.join(f'{abs(int(matrix[r, (col + c) % 128])):02x}' for col in range(32))

    # Double hash with block number
    double_data = str(block).encode() + bytes([abs(int(matrix[r, col])) % 256 for col in range(128)])
    double_sha = hashlib.sha256(hashlib.sha256(double_data).digest()).hexdigest()

    # RIPEMD160 + SHA256
    ripe_data = bytes([abs(int(matrix[r, col])) % 256 for col in range(128)])
    ripe = hashlib.new('ripemd160', ripe_data).digest()
    ripe_sha = hashlib.sha256(ripe + ripe[:12]).hexdigest()

    methods = [
        ("Row Direct", row_direct),
        ("Row+Offset", row_offset),
        ("Double SHA256", double_sha),
        ("RIPEMD+SHA", ripe_sha),
    ]

    for method_name, key in methods:
        if len(key) == 64:
            match = check_key(key, target_pubkey)
            if match:
                print(f"  ✅ {method_name}: MATCH! 🎉🎉🎉")
            else:
                print(f"  ❌ {method_name}")

# Check if any method worked
print("\n" + "=" * 80)
print("📊 RESULTS")
print("=" * 80)

matches = [a for a in attempts if len(a) > 3 and a[3] == True]
if matches:
    print("\n🎉🎉🎉 PRIVATE KEY GEFUNDEN! 🎉🎉🎉")
    for m in matches:
        print(f"\n  Block {m[0]}:")
        print(f"  Method: {m[1]}")
        print(f"  Private Key: {m[2]}")
        print(f"  VALUE: 50 BTC = ~$5,000,000 !!!")
else:
    print("\n❌ Keine direkten Matches gefunden")
    print("\n  Aber: Die Matrix ZEIGT auf diese Blocks!")
    print("  Der Schlüssel könnte komplexer kodiert sein...")

# Save results for further analysis
output = {
    "target_blocks": {str(k): {"coords": v, "pubkey": block_lookup[k]['pubkey']}
                     for k, v in target_blocks.items()},
    "attempts": len(attempts),
    "matches": len(matches),
    "note": "Bridge cells point to Patoshi blocks - key derivation method unknown"
}

with open(script_dir / "PATOSHI_CRACK_RESULTS.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("💡 NÄCHSTE IDEEN")
print("=" * 80)
print("""
  1. Die Pubkeys SELBST könnten der Schlüssel sein
     → XOR Pubkey mit etwas ergibt Private Key?

  2. Zeitbasierter Schlüssel
     → Vielleicht wird der Key erst zu einem Datum gültig?

  3. Mehrere Matrix-Zellen kombiniert
     → Alle 8 Bridge-Cells zusammen = Key?

  4. Die "AI.MEG.GOU" Nachricht
     → Könnte ein Passwort für BIP38 sein?

  5. Cross-Reference mit CFB Discord Messages
     → Vielleicht gibt es dort weitere Hinweise?
""")
