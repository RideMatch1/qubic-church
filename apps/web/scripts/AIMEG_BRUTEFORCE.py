#!/usr/bin/env python3
"""
===============================================================================
   🔐 AI.MEG.GOU BRUTEFORCE 🔐
===============================================================================
Verwende AI.MEG.GOU und alle Bridge-Cells kombiniert als Schlüssel!
===============================================================================
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from itertools import permutations
import requests
import time

try:
    import ecdsa
    ECDSA_LIB = True
except:
    ECDSA_LIB = False

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   █████╗ ██╗   ███╗   ███╗███████╗ ██████╗
  ██╔══██╗██║   ████╗ ████║██╔════╝██╔════╝
  ███████║██║   ██╔████╔██║█████╗  ██║  ███╗
  ██╔══██║██║   ██║╚██╔╝██║██╔══╝  ██║   ██║
  ██║  ██║██║██╗██║ ╚═╝ ██║███████╗╚██████╔╝
  ╚═╝  ╚═╝╚═╝╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝
   🔐 AI.MEG.GOU BRUTEFORCE 🔐
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

# All bridge cells
bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

def private_key_to_address(private_key_hex):
    """Convert private key to Bitcoin address"""
    if len(private_key_hex) != 64:
        return None
    try:
        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(private_key_hex),
            curve=ecdsa.SECP256k1
        )
        vk = sk.get_verifying_key()
        public_key = b'\x04' + vk.to_string()
        sha256 = hashlib.sha256(public_key).digest()
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
    except:
        return None

def check_balance(address):
    """Check if address has balance"""
    try:
        url = f'https://blockstream.info/api/address/{address}'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            balance = data.get('chain_stats', {}).get('funded_txo_sum', 0) - \
                     data.get('chain_stats', {}).get('spent_txo_sum', 0)
            return balance / 100000000
    except:
        pass
    return 0

# ==============================================================================
# AI.MEG.GOU VARIATIONS
# ==============================================================================
print("\n" + "=" * 80)
print("🔑 AI.MEG.GOU AS KEY SOURCE")
print("=" * 80)

aimeg_variations = [
    "AI.MEG.GOU",
    "AIMEGGOU",
    "ai.meg.gou",
    "aimeggou",
    "AI MEG GOU",
    "MEGAI",
    "MEGAIGOU",
    "GOUAIMEG",
    "AI.MEG",
    "MEG.GOU",
    # Numerische Interpretationen
    "1.13.5.7.15.21",  # AI=1, M=13, E=5, G=7, O=15, U=21
    "0113050715.2105.0715.21",
]

print("\n📌 Testing AI.MEG.GOU variations as keys:")

all_generated = []

for variation in aimeg_variations:
    # SHA256
    sha = hashlib.sha256(variation.encode()).hexdigest()
    addr = private_key_to_address(sha)
    if addr:
        all_generated.append((f"SHA256({variation})", sha, addr))
        print(f"  {variation} → {addr[:20]}...")

    # Double SHA256
    double_sha = hashlib.sha256(bytes.fromhex(sha)).hexdigest()
    addr = private_key_to_address(double_sha)
    if addr:
        all_generated.append((f"2xSHA256({variation})", double_sha, addr))

# ==============================================================================
# ALL 8 BRIDGE CELLS COMBINED
# ==============================================================================
print("\n" + "=" * 80)
print("🔗 ALL 8 BRIDGE CELLS COMBINED")
print("=" * 80)

# Method 1: Coordinates as bytes
coords_bytes = bytes([r for r, c in bridge_cells] + [c for r, c in bridge_cells])
coords_sha = hashlib.sha256(coords_bytes).hexdigest()
addr = private_key_to_address(coords_sha)
if addr:
    all_generated.append(("All Coords SHA256", coords_sha, addr))
    print(f"  All Coords → {addr}")

# Method 2: Values at bridge cells
bridge_values = [int(matrix[r, c]) for r, c in bridge_cells]
values_bytes = bytes([v % 256 for v in bridge_values])
values_sha = hashlib.sha256(values_bytes * 4).hexdigest()
addr = private_key_to_address(values_sha)
if addr:
    all_generated.append(("Bridge Values SHA256", values_sha, addr))
    print(f"  Bridge Values → {addr}")

# Method 3: Concatenate row data from all bridge cells
all_rows = []
for r, c in bridge_cells:
    row_data = [abs(int(matrix[r, col])) % 256 for col in range(128)]
    all_rows.extend(row_data[:16])  # First 16 from each row = 128 bytes

all_rows_sha = hashlib.sha256(bytes(all_rows[:32])).hexdigest()
addr = private_key_to_address(all_rows_sha)
if addr:
    all_generated.append(("All Rows Combined", all_rows_sha, addr))
    print(f"  All Rows → {addr}")

# Method 4: XOR all bridge row data
xor_result = [0] * 128
for r, c in bridge_cells:
    row_data = [abs(int(matrix[r, col])) % 256 for col in range(128)]
    xor_result = [xor_result[i] ^ row_data[i] for i in range(128)]

xor_sha = hashlib.sha256(bytes(xor_result[:32])).hexdigest()
addr = private_key_to_address(xor_sha)
if addr:
    all_generated.append(("XOR All Bridge Rows", xor_sha, addr))
    print(f"  XOR All Rows → {addr}")

# Method 5: Block numbers combined
block_numbers = [1776, 2078, 20120, 2115, 4263, 5151, 57124, 81108]
blocks_str = ''.join(str(b) for b in block_numbers)
blocks_sha = hashlib.sha256(blocks_str.encode()).hexdigest()
addr = private_key_to_address(blocks_sha)
if addr:
    all_generated.append(("Block Numbers", blocks_sha, addr))
    print(f"  Block Numbers → {addr}")

# ==============================================================================
# AI.MEG.GOU + BRIDGE CELLS COMBINED
# ==============================================================================
print("\n" + "=" * 80)
print("🔀 AI.MEG.GOU + BRIDGE CELLS COMBINED")
print("=" * 80)

for variation in ["AI.MEG.GOU", "AIMEGGOU", "aimeggou"]:
    # Combine with coords
    combined = variation.encode() + coords_bytes
    combined_sha = hashlib.sha256(combined).hexdigest()
    addr = private_key_to_address(combined_sha)
    if addr:
        all_generated.append((f"{variation}+Coords", combined_sha, addr))
        print(f"  {variation}+Coords → {addr}")

    # Combine with block numbers
    combined2 = variation.encode() + blocks_str.encode()
    combined2_sha = hashlib.sha256(combined2).hexdigest()
    addr = private_key_to_address(combined2_sha)
    if addr:
        all_generated.append((f"{variation}+Blocks", combined2_sha, addr))
        print(f"  {variation}+Blocks → {addr}")

# ==============================================================================
# THE "KEY" POSITION COMBINED WITH AI.MEG
# ==============================================================================
print("\n" + "=" * 80)
print("🔑 'KEY' POSITION + AI.MEG.GOU")
print("=" * 80)

# Key is at (107-109, 127)
key_data = [abs(int(matrix[107, 127])), abs(int(matrix[108, 127])), abs(int(matrix[109, 127]))]

for variation in ["AI.MEG.GOU", "key", "KEY"]:
    combined = variation.encode() + bytes(key_data)
    combined_sha = hashlib.sha256(combined).hexdigest()
    addr = private_key_to_address(combined_sha)
    if addr:
        all_generated.append((f"{variation}+KeyPos", combined_sha, addr))
        print(f"  {variation}+KeyPos → {addr}")

# ==============================================================================
# SPECIAL: SATOSHI MESSAGE COMBINATIONS
# ==============================================================================
print("\n" + "=" * 80)
print("📜 SATOSHI-STYLE COMBINATIONS")
print("=" * 80)

satoshi_phrases = [
    "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks",
    "1776",
    "4263",  # The Answer
    "bitcoin",
    "genesis",
]

for phrase in satoshi_phrases:
    combined = phrase.encode() + bytes([127] * 8)  # 8 bridge values (all 127)
    combined_sha = hashlib.sha256(combined).hexdigest()
    addr = private_key_to_address(combined_sha)
    if addr:
        all_generated.append((f"Satoshi:{phrase[:20]}", combined_sha, addr))
        print(f"  {phrase[:30]}... → {addr}")

# ==============================================================================
# CHECK ALL ADDRESSES FOR BALANCE
# ==============================================================================
print("\n" + "=" * 80)
print("💰 CHECKING ALL GENERATED ADDRESSES FOR BALANCE")
print("=" * 80)

print(f"\n  Total addresses to check: {len(all_generated)}")
print("  Checking (this may take a moment)...\n")

found_with_balance = []

for i, (name, key, addr) in enumerate(all_generated[:30]):  # Check first 30 to avoid rate limit
    balance = check_balance(addr)
    if balance > 0:
        print(f"  💰 {name}: {addr} = {balance} BTC!")
        found_with_balance.append((name, key, addr, balance))
    else:
        print(f"  ❌ {name}: {addr[:25]}... = 0")
    time.sleep(0.3)  # Rate limiting

print("\n" + "=" * 80)
print("📊 RESULTS")
print("=" * 80)

if found_with_balance:
    print("\n🎉🎉🎉 ADDRESSES WITH BALANCE FOUND! 🎉🎉🎉")
    for name, key, addr, balance in found_with_balance:
        print(f"\n  {name}:")
        print(f"  Address: {addr}")
        print(f"  Private Key: {key}")
        print(f"  Balance: {balance} BTC = ${balance * 100000:,.0f} !!!")
else:
    print("\n  Keine Adressen mit Balance gefunden in dieser Runde")
    print(f"  Getestet: {min(30, len(all_generated))} von {len(all_generated)} Kombinationen")

# Save all generated addresses for future reference
output = {
    "total_generated": len(all_generated),
    "addresses": [
        {"method": name, "private_key": key, "address": addr}
        for name, key, addr in all_generated
    ]
}

with open(script_dir / "AIMEG_BRUTEFORCE_RESULTS.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n✓ Alle Adressen gespeichert in AIMEG_BRUTEFORCE_RESULTS.json")
