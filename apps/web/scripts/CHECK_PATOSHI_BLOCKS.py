#!/usr/bin/env python3
"""
===============================================================================
   🔍 CHECK IF BRIDGE BLOCKS ARE PATOSHI BLOCKS 🔍
===============================================================================
Are the blocks pointed to by bridge coordinates mined by Satoshi (Patoshi)?

Bridge cells: (17,76), (20,78), (20,120), (21,15), (42,63), (51,51), (57,124), (81,108)
Combined block numbers: 1776, 2078, 20120, 2115, 4263, 5151, 57124, 81108
===============================================================================
"""

import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗  █████╗ ████████╗ ██████╗ ███████╗██╗  ██╗██╗
   ██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝██║  ██║██║
   ██████╔╝███████║   ██║   ██║   ██║███████╗███████║██║
   ██╔═══╝ ██╔══██║   ██║   ██║   ██║╚════██║██╔══██║██║
   ██║     ██║  ██║   ██║   ╚██████╔╝███████║██║  ██║██║
   ╚═╝     ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝
        🔍 PATOSHI BLOCK CHECKER 🔍
""")
print("=" * 80)

# Bridge coordinates and their block interpretations
bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

combined_blocks = [1776, 2078, 20120, 2115, 4263, 5151, 57124, 81108]

# Load Patoshi addresses
print("\n📂 Loading Patoshi addresses...")
patoshi_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"

patoshi_addresses = set()
patoshi_blocks = {}

try:
    with open(patoshi_path) as f:
        data = json.load(f)

    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                addr = entry.get('address', '')
                block = entry.get('block', entry.get('blockHeight', 0))
                if addr:
                    patoshi_addresses.add(addr)
                    if block:
                        patoshi_blocks[block] = addr
            elif isinstance(entry, str):
                patoshi_addresses.add(entry)

    print(f"✓ Loaded {len(patoshi_addresses)} Patoshi addresses")
    print(f"✓ {len(patoshi_blocks)} blocks with addresses")

except Exception as e:
    print(f"✗ Error loading Patoshi data: {e}")

# Check if our blocks are Patoshi blocks
print("\n" + "=" * 80)
print("CHECKING IF BRIDGE BLOCKS ARE PATOSHI BLOCKS")
print("=" * 80)

def get_block_coinbase(block_num):
    """Get coinbase address from Blockstream API"""
    try:
        # Get block hash first
        hash_url = f"https://blockstream.info/api/block-height/{block_num}"
        response = requests.get(hash_url, timeout=10)
        if response.status_code != 200:
            return None, None

        block_hash = response.text.strip()

        # Get block details
        block_url = f"https://blockstream.info/api/block/{block_hash}"
        response = requests.get(block_url, timeout=10)
        if response.status_code != 200:
            return block_hash, None

        block_data = response.json()
        timestamp = block_data.get('timestamp', 0)

        # Get transactions
        txs_url = f"https://blockstream.info/api/block/{block_hash}/txs/0"
        response = requests.get(txs_url, timeout=10)
        if response.status_code != 200:
            return block_hash, None

        txs = response.json()
        if txs and len(txs) > 0:
            coinbase_tx = txs[0]
            if 'vout' in coinbase_tx and len(coinbase_tx['vout']) > 0:
                addr = coinbase_tx['vout'][0].get('scriptpubkey_address', '')
                return block_hash, addr, timestamp

    except Exception as e:
        return None, None, None
    return None, None, None

results = []

for i, block_num in enumerate(combined_blocks):
    r, c = bridge_cells[i]
    print(f"\n  Block {block_num} (from {r},{c}):")

    result = {
        "block": block_num,
        "coordinates": (r, c),
        "is_patoshi": False,
        "coinbase_address": None,
        "significance": []
    }

    # Check if in Patoshi blocks
    if block_num in patoshi_blocks:
        print(f"    ✅ IS A PATOSHI BLOCK!")
        print(f"    Coinbase: {patoshi_blocks[block_num]}")
        result["is_patoshi"] = True
        result["coinbase_address"] = patoshi_blocks[block_num]
        result["significance"].append("PATOSHI_BLOCK")
    else:
        # Fetch from API
        block_hash, addr, timestamp = get_block_coinbase(block_num)
        if addr:
            result["coinbase_address"] = addr
            print(f"    Coinbase: {addr}")

            if addr in patoshi_addresses:
                print(f"    ✅ Coinbase is a KNOWN PATOSHI ADDRESS!")
                result["is_patoshi"] = True
                result["significance"].append("PATOSHI_ADDRESS")
            else:
                print(f"    ❓ Not a known Patoshi address")
        else:
            print(f"    ⚠️ Could not fetch coinbase address")

    # Add symbolic significance
    if block_num == 1776:
        result["significance"].append("AMERICAN_INDEPENDENCE_YEAR")
        print(f"    🇺🇸 American Independence Year!")
    if block_num == 5151:
        result["significance"].append("PALINDROME")
        print(f"    🔄 Palindrome number!")
    if r == c:
        result["significance"].append("DIAGONAL_POSITION")
        print(f"    📐 On main diagonal!")
    if r == 42:
        result["significance"].append("ANSWER_TO_EVERYTHING")
        print(f"    🎯 Row 42 = Answer to Everything!")

    results.append(result)

# Summary
print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

patoshi_count = sum(1 for r in results if r["is_patoshi"])
print(f"\n  Total bridge blocks: {len(results)}")
print(f"  Patoshi blocks: {patoshi_count}")
print(f"  Patoshi ratio: {patoshi_count}/{len(results)} = {patoshi_count/len(results)*100:.1f}%")

if patoshi_count > 0:
    print(f"""
  ╔════════════════════════════════════════════════════════════════════════════╗
  ║   🎯 SIGNIFICANT FINDING: Bridge coordinates point to PATOSHI blocks!     ║
  ║   This suggests CFB encoded references to Satoshi's mining in the Matrix  ║
  ╚════════════════════════════════════════════════════════════════════════════╝
""")

# Check additional interpretations
print("\n" + "=" * 80)
print("🔍 ALTERNATIVE INTERPRETATIONS")
print("=" * 80)

# Sum of coordinates as block numbers
sum_blocks = [r+c for r, c in bridge_cells]
print(f"\n  Sum of coordinates as blocks: {sum_blocks}")

for i, block_num in enumerate(sum_blocks):
    if block_num in patoshi_blocks:
        print(f"    Block {block_num} (sum of {bridge_cells[i]}) = PATOSHI!")

# Products
product_blocks = [r*c for r, c in bridge_cells]
print(f"\n  Product of coordinates as blocks: {product_blocks}")

for i, block_num in enumerate(product_blocks):
    if block_num in patoshi_blocks:
        print(f"    Block {block_num} (product of {bridge_cells[i]}) = PATOSHI!")

# XOR
xor_blocks = [r^c for r, c in bridge_cells]
print(f"\n  XOR of coordinates as blocks: {xor_blocks}")

for i, block_num in enumerate(xor_blocks):
    if block_num in patoshi_blocks:
        print(f"    Block {block_num} (XOR of {bridge_cells[i]}) = PATOSHI!")

# Save results
output = {
    "bridge_blocks_analysis": results,
    "patoshi_blocks_found": patoshi_count,
    "total_patoshi_in_dataset": len(patoshi_blocks),
    "significance": "Bridge coordinates may encode references to Satoshi-era blocks"
}

with open(script_dir / "PATOSHI_BLOCK_RESULTS.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n✓ Results saved to PATOSHI_BLOCK_RESULTS.json")

# Final check: early block range
print("\n" + "=" * 80)
print("🔍 CHECKING PATOSHI PATTERN IN EARLY BLOCKS")
print("=" * 80)

# Patoshi mined roughly blocks 1-36288 (first year)
early_blocks = [b for b in combined_blocks if b < 36288]
print(f"\n  Bridge blocks in first-year range (<36288): {early_blocks}")
print(f"  This is {len(early_blocks)}/{len(combined_blocks)} = {len(early_blocks)/len(combined_blocks)*100:.0f}% of bridge blocks!")

if len(early_blocks) == len(combined_blocks) - 2:  # 6 out of 8
    print("""
  ╔════════════════════════════════════════════════════════════════════════════╗
  ║   🎯 6/8 bridge blocks are from Satoshi's first year of mining!           ║
  ║   Blocks 57124 and 81108 are from later (2010) but still early history    ║
  ╚════════════════════════════════════════════════════════════════════════════╝
""")
