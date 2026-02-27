#!/usr/bin/env python3
"""
676 Blocks Analysis using Mempool.space API

More reliable than blockchain.info for early blocks.

Author: Claude Code
Date: 2026-02-07
"""

import json
import base58
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

def load_anna_matrix() -> np.ndarray:
    """Load Anna Matrix"""
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    return np.array(data['matrix'], dtype=np.int8)

def bitcoin_address_to_hash160(address: str) -> Optional[bytes]:
    """Convert Bitcoin address to Hash160"""
    try:
        decoded = base58.b58decode_check(address)
        return decoded[1:]
    except Exception:
        return None

def hash160_to_matrix_coordinates(hash160: bytes) -> Tuple[int, int]:
    """Map Hash160 to Anna Matrix coordinates"""
    hash160_int = int.from_bytes(hash160, 'big')
    position = hash160_int % 16384
    row = position // 128
    col = position % 128
    return row, col

def get_block_data(block_height: int) -> Optional[Dict]:
    """Get block data from mempool.space"""
    try:
        url = f"https://mempool.space/api/block-height/{block_height}"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            block_hash = response.text

            # Get block details
            time.sleep(0.5)  # Rate limit
            url2 = f"https://mempool.space/api/block/{block_hash}"
            response2 = requests.get(url2, timeout=15)

            if response2.status_code == 200:
                return response2.json()

        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None

def get_coinbase_address(block_hash: str) -> Optional[str]:
    """Get coinbase address from block"""
    try:
        url = f"https://mempool.space/api/block/{block_hash}/txs/0"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            coinbase_tx = response.json()

            # Get first output address
            if 'vout' in coinbase_tx and len(coinbase_tx['vout']) > 0:
                first_output = coinbase_tx['vout'][0]
                if 'scriptpubkey_address' in first_output:
                    return first_output['scriptpubkey_address']

        return None
    except Exception as e:
        print(f"    Error getting coinbase: {e}")
        return None

def check_address_utxo(address: str) -> Optional[float]:
    """Check if address has UTXO (unspent balance)"""
    try:
        url = f"https://mempool.space/api/address/{address}/utxo"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            utxos = response.json()
            total_sats = sum(utxo['value'] for utxo in utxos)
            return total_sats / 100_000_000

        return 0.0
    except Exception:
        return None

def check_special_positions(row: int, col: int) -> Dict:
    """Check special matrix positions"""
    exception_cols = [0, 22, 30, 41, 86, 97, 105, 127]
    factory_rows = [0, 1, 2, 126, 127]

    return {
        "exception_column": col in exception_cols,
        "factory_row": row in factory_rows,
        "row_21": row == 21
    }

def main():
    print("=" * 80)
    print("676 BLOCKS ANALYSIS - Mempool.space API")
    print("=" * 80)
    print()
    print("Analyzing blocks 1-676 (Bitcoin Genesis era)")
    print("Rate limited to ~2 blocks/sec for API reliability")
    print()

    matrix = load_anna_matrix()
    results = []
    genesis_addresses = []

    failed_blocks = []
    success_count = 0

    exception_col_count = 0
    factory_row_count = 0
    row_21_count = 0

    row_dist = {}
    col_dist = {}

    print("Starting analysis...")
    print()

    for block_num in range(1, 677):
        print(f"Block {block_num}/676... ", end="", flush=True)

        # Get block data
        block_data = get_block_data(block_num)

        if not block_data or 'id' not in block_data:
            print("❌ Failed to get block")
            failed_blocks.append(block_num)
            time.sleep(1)
            continue

        block_hash = block_data['id']

        # Get coinbase address
        time.sleep(0.5)
        address = get_coinbase_address(block_hash)

        if not address:
            print("❌ No coinbase address")
            failed_blocks.append(block_num)
            continue

        # Check balance
        time.sleep(0.5)
        balance = check_address_utxo(address)

        # Map to matrix
        hash160 = bitcoin_address_to_hash160(address)
        if not hash160:
            print("❌ Invalid address format")
            continue

        row, col = hash160_to_matrix_coordinates(hash160)
        value = matrix[row, col]

        special = check_special_positions(row, col)

        # Track distributions
        row_dist[row] = row_dist.get(row, 0) + 1
        col_dist[col] = col_dist.get(col, 0) + 1

        if special['exception_column']:
            exception_col_count += 1
        if special['factory_row']:
            factory_row_count += 1
        if special['row_21']:
            row_21_count += 1

        # Check if Genesis (50 BTC unspent)
        is_genesis = balance is not None and balance >= 49.9

        if is_genesis:
            genesis_addresses.append({
                "block": block_num,
                "address": address,
                "balance": balance,
                "row": row,
                "col": col,
                "value": int(value),
                "special": special
            })

        result = {
            "block": block_num,
            "address": address,
            "balance": balance,
            "hash160": hash160.hex(),
            "matrix": {
                "row": row,
                "col": col,
                "value": int(value)
            },
            "special": special,
            "is_genesis": is_genesis
        }

        results.append(result)
        success_count += 1

        status = "🟢" if is_genesis else "⚪"
        bal_str = f"{balance:.1f}" if balance is not None else "?"
        print(f"{status} R{row:3d} C{col:3d} V{value:4d} = {bal_str} BTC")

    # Summary
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print(f"Success: {success_count}/676")
    print(f"Failed: {len(failed_blocks)}")
    print(f"Genesis (50 BTC): {len(genesis_addresses)}")
    print()

    if genesis_addresses:
        print("=" * 80)
        print(f"GENESIS ADDRESSES (50 BTC UNSPENT): {len(genesis_addresses)}")
        print("=" * 80)
        print()

        for ga in genesis_addresses:
            print(f"Block {ga['block']:3d}: {ga['address']}")
            print(f"  Balance: {ga['balance']:.8f} BTC")
            print(f"  Matrix: Row {ga['row']:3d}, Col {ga['col']:3d}, Value {ga['value']:4d}")
            print(f"  Special: ExCol={ga['special']['exception_column']}, "
                  f"FactRow={ga['special']['factory_row']}, Row21={ga['special']['row_21']}")
            print()

        # Clustering
        print("CLUSTERING ANALYSIS:")
        genesis_rows = [g['row'] for g in genesis_addresses]
        genesis_cols = [g['col'] for g in genesis_addresses]
        genesis_values = [g['value'] for g in genesis_addresses]

        print(f"  Unique rows: {len(set(genesis_rows))}/{len(genesis_addresses)}")
        print(f"  Unique cols: {len(set(genesis_cols))}/{len(genesis_addresses)}")
        print(f"  Exception columns: {sum(g['special']['exception_column'] for g in genesis_addresses)}/{len(genesis_addresses)}")
        print(f"  Factory rows: {sum(g['special']['factory_row'] for g in genesis_addresses)}/{len(genesis_addresses)}")
        print(f"  Row 21: {sum(g['special']['row_21'] for g in genesis_addresses)}/{len(genesis_addresses)}")
        print(f"  Sum of values: {sum(genesis_values)}")
        print(f"  Average value: {sum(genesis_values)/len(genesis_addresses):.2f}")
        print()

    # Save
    output = {
        "metadata": {
            "date": "2026-02-07",
            "total_blocks": len(results),
            "success_count": success_count,
            "failed_count": len(failed_blocks),
            "genesis_count": len(genesis_addresses)
        },
        "results": results,
        "genesis_addresses": genesis_addresses,
        "failed_blocks": failed_blocks,
        "statistics": {
            "exception_cols": exception_col_count,
            "factory_rows": factory_row_count,
            "row_21": row_21_count,
            "row_distribution": row_dist,
            "col_distribution": col_dist
        }
    }

    output_path = Path(__file__).parent / "BLOCKCHAIN_676_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Saved to: {output_path}")
    print()

if __name__ == "__main__":
    main()
