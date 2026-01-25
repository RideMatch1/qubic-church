#!/usr/bin/env python3
"""
===============================================================================
   🔍 CHECK BITCOIN BLOCKS FROM BRIDGE COORDINATES 🔍
===============================================================================
Bridge cells: (17,76), (20,78), (20,120), (21,15), (42,63), (51,51), (57,124), (81,108)

Possible block numbers:
- Combined: 1776, 2078, 20120, 2115, 4263, 5151, 57124, 81108
- Raw: 17, 76, 20, 78, 120, 21, 15, 42, 63, 51, 57, 124, 81, 108
- Sums: 93, 98, 140, 36, 105, 102, 181, 189
===============================================================================
"""

import requests
import json
from datetime import datetime

print("=" * 80)
print("""
   ██████╗ ██╗      ██████╗  ██████╗██╗  ██╗███████╗
   ██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝██╔════╝
   ██████╔╝██║     ██║   ██║██║     █████╔╝ ███████╗
   ██╔══██╗██║     ██║   ██║██║     ██╔═██╗ ╚════██║
   ██████╔╝███████╗╚██████╔╝╚██████╗██║  ██╗███████║
   ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝
        🔍 BITCOIN BLOCK INVESTIGATION 🔍
""")
print("=" * 80)

# Bridge cells
bridge_cells = [
    (17, 76), (20, 78), (20, 120), (21, 15),
    (42, 63), (51, 51), (57, 124), (81, 108),
]

# Different interpretations
combined_blocks = [1776, 2078, 20120, 2115, 4263, 5151, 57124, 81108]
raw_coords = [17, 76, 20, 78, 20, 120, 21, 15, 42, 63, 51, 51, 57, 124, 81, 108]
sum_blocks = [17+76, 20+78, 20+120, 21+15, 42+63, 51+51, 57+124, 81+108]

# Special numbers
special_blocks = [
    1,      # Genesis block
    9,      # First transaction to Hal Finney
    170,    # First Bitcoin transaction
    210000, # First halving
    127,    # The bridge value
    42,     # Answer to everything
    21,     # 21 million
]

def get_block_info(block_num):
    """Get block info from blockchain.info API"""
    try:
        url = f"https://blockchain.info/block-height/{block_num}?format=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'blocks' in data and len(data['blocks']) > 0:
                block = data['blocks'][0]
                return {
                    'height': block_num,
                    'hash': block.get('hash', '')[:16] + '...',
                    'time': datetime.fromtimestamp(block.get('time', 0)).strftime('%Y-%m-%d %H:%M'),
                    'n_tx': block.get('n_tx', 0),
                    'total_btc': block.get('fee', 0) / 100000000,
                    'miner': block.get('miner', 'Unknown'),
                }
    except Exception as e:
        return {'error': str(e)}
    return None

print("\n" + "=" * 80)
print("COMBINED COORDINATES AS BLOCK NUMBERS")
print("=" * 80)
print("\n  (17,76)→1776, (20,78)→2078, etc.\n")

for i, block_num in enumerate(combined_blocks):
    r, c = bridge_cells[i]
    print(f"\n  Block {block_num} (from {r},{c}):")
    info = get_block_info(block_num)
    if info and 'error' not in info:
        print(f"    Hash: {info['hash']}")
        print(f"    Date: {info['time']}")
        print(f"    Transactions: {info['n_tx']}")
    else:
        print(f"    Error fetching block info")

print("\n" + "=" * 80)
print("INTERESTING OBSERVATIONS")
print("=" * 80)

# Check some specific blocks
print("\n  Checking historically significant blocks...\n")

# Block 1776 - American independence year!
print("  🇺🇸 Block 1776 (American Independence year!):")
info = get_block_info(1776)
if info and 'error' not in info:
    print(f"     Date: {info['time']}")
    print(f"     This is during Satoshi's active mining period!")

# Block 5151 - palindrome!
print("\n  🔄 Block 5151 (Palindrome number!):")
info = get_block_info(5151)
if info and 'error' not in info:
    print(f"     Date: {info['time']}")

# Block 4263 - from (42, 63) "The Answer"!
print("\n  🎯 Block 4263 (from 'The Answer' position 42,63):")
info = get_block_info(4263)
if info and 'error' not in info:
    print(f"     Date: {info['time']}")

print("\n" + "=" * 80)
print("SUM OF COORDINATES AS BLOCK NUMBERS")
print("=" * 80)
print(f"\n  Sums: {sum_blocks}\n")

for i, block_num in enumerate(sum_blocks):
    r, c = bridge_cells[i]
    print(f"  Block {block_num} (sum of {r}+{c}):")
    info = get_block_info(block_num)
    if info and 'error' not in info:
        print(f"    Date: {info['time']}, Txs: {info['n_tx']}")

print("\n" + "=" * 80)
print("BLOCK 127 (THE BRIDGE VALUE)")
print("=" * 80)

info = get_block_info(127)
if info and 'error' not in info:
    print(f"\n  Block 127:")
    print(f"    Hash: {info['hash']}")
    print(f"    Date: {info['time']}")
    print(f"    Transactions: {info['n_tx']}")

# Check if any coinbase addresses match known patterns
print("\n" + "=" * 80)
print("CHECKING COINBASE ADDRESSES OF KEY BLOCKS")
print("=" * 80)

def get_coinbase_address(block_num):
    """Get the coinbase (mining reward) address of a block"""
    try:
        url = f"https://blockchain.info/block-height/{block_num}?format=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'blocks' in data and len(data['blocks']) > 0:
                block = data['blocks'][0]
                # First transaction is coinbase
                if 'tx' in block and len(block['tx']) > 0:
                    coinbase_tx = block['tx'][0]
                    if 'out' in coinbase_tx and len(coinbase_tx['out']) > 0:
                        return coinbase_tx['out'][0].get('addr', 'Unknown')
    except:
        pass
    return None

print("\n  Coinbase addresses of combined blocks:\n")
for block_num in combined_blocks[:4]:  # First 4 to avoid rate limiting
    addr = get_coinbase_address(block_num)
    if addr:
        print(f"    Block {block_num}: {addr}")

print("\n" + "=" * 80)
print("🎯 SUMMARY")
print("=" * 80)

print(f"""
  Bridge Cell Coordinates as Block Numbers:

  Combined (r*100+c or r||c):
    1776  - Block from Jan 2009 (Satoshi era!) 🇺🇸
    2078  - Block from Jan 2009 (Satoshi era!)
    20120 - Block from late 2009
    2115  - Block from Jan 2009 (Satoshi era!)
    4263  - Block from Feb 2009 (The Answer!)
    5151  - Block from Feb 2009 (Palindrome!)
    57124 - Block from mid 2010
    81108 - Block from late 2010

  Key Insight:
    Most of these blocks are from the SATOSHI ERA (2009)!
    Could these contain special transactions?

  Next Step:
    Check the actual TRANSACTIONS in these blocks
    for any connection to known Satoshi/Patoshi addresses!
""")

# Save results
results = {
    "combined_blocks": combined_blocks,
    "sum_blocks": sum_blocks,
    "observation": "Most blocks are from Satoshi era (2009)",
    "next_step": "Check transactions in these blocks"
}

with open("BITCOIN_BLOCKS_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

print("✓ Results saved to BITCOIN_BLOCKS_RESULTS.json")
