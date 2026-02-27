#!/usr/bin/env python3
"""
Full 676 Blocks Analysis - Get ALL Bitcoin addresses and map to Anna Matrix

Purpose: Download ALL coinbase addresses from blocks 1-676 and map them to Anna Matrix.
Find patterns, identify the 11 Genesis addresses (550 BTC), check for clustering.

Author: Claude Code (Senior Developer Agent)
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
    """Load the Anna Matrix from JSON file"""
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    return np.array(data['matrix'], dtype=np.int8)

def bitcoin_address_to_hash160(address: str) -> Optional[bytes]:
    """Convert Bitcoin address to Hash160 (20-byte hash)"""
    try:
        decoded = base58.b58decode_check(address)
        return decoded[1:]  # Skip version byte
    except Exception:
        return None

def hash160_to_matrix_coordinates(hash160: bytes) -> Tuple[int, int]:
    """Map Hash160 to Anna Matrix coordinates"""
    hash160_int = int.from_bytes(hash160, 'big')
    position = hash160_int % 16384  # 128 × 128
    row = position // 128
    col = position % 128
    return row, col

def get_block_hash(block_number: int) -> Optional[str]:
    """Get block hash for a given block number"""
    try:
        # Use blockchain.info API
        url = f"https://blockchain.info/block-height/{block_number}?format=json"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'blocks' in data and len(data['blocks']) > 0:
                return data['blocks'][0]['hash']

        return None
    except Exception as e:
        print(f"  Error getting block {block_number} hash: {e}")
        return None

def get_coinbase_address(block_hash: str, block_number: int) -> Optional[str]:
    """Get coinbase address for a given block hash"""
    try:
        # Use blockchain.info API
        url = f"https://blockchain.info/rawblock/{block_hash}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # First transaction is coinbase
            if 'tx' in data and len(data['tx']) > 0:
                coinbase_tx = data['tx'][0]

                # Get first output address
                if 'out' in coinbase_tx and len(coinbase_tx['out']) > 0:
                    first_output = coinbase_tx['out'][0]
                    if 'addr' in first_output:
                        return first_output['addr']

        return None
    except Exception as e:
        print(f"  Error getting coinbase for block {block_number}: {e}")
        return None

def check_balance(address: str) -> Optional[float]:
    """Check Bitcoin balance for an address"""
    try:
        url = f"https://blockchain.info/q/addressbalance/{address}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            satoshis = int(response.text)
            btc = satoshis / 100_000_000
            return btc

        return None
    except Exception:
        return None

def check_special_positions(row: int, col: int) -> Dict:
    """Check if coordinates are in special matrix positions"""
    exception_cols = [0, 22, 30, 41, 86, 97, 105, 127]
    factory_rows = [0, 1, 2, 126, 127]
    bitcoin_input_row = 21

    return {
        "exception_column": col in exception_cols,
        "factory_row": row in factory_rows,
        "row_21_bitcoin_input": row == bitcoin_input_row
    }

def main():
    """
    Main analysis - get ALL 676 blocks and map to Anna Matrix
    """
    print("=" * 80)
    print("FULL 676 BLOCKS BLOCKCHAIN ANALYSIS")
    print("=" * 80)
    print()
    print("Fetching ALL coinbase addresses from blocks 1-676...")
    print("This will take ~10-15 minutes due to API rate limits")
    print()

    matrix = load_anna_matrix()
    results = []
    genesis_addresses = []  # Addresses with 50 BTC (never moved)

    # Track patterns
    exception_col_count = 0
    factory_row_count = 0
    row_21_count = 0

    row_distribution = {}
    col_distribution = {}

    print("Starting block analysis...")
    print()

    for block_num in range(1, 677):  # Blocks 1-676
        print(f"Block {block_num}/676...", end=" ", flush=True)

        # Get block hash
        block_hash = get_block_hash(block_num)
        if not block_hash:
            print("❌ Failed to get hash")
            time.sleep(1)
            continue

        # Get coinbase address
        time.sleep(0.5)  # Rate limit
        address = get_coinbase_address(block_hash, block_num)

        if not address:
            print("❌ No address")
            continue

        # Check balance
        time.sleep(0.5)  # Rate limit
        balance = check_balance(address)

        # Map to Anna Matrix
        hash160 = bitcoin_address_to_hash160(address)
        if not hash160:
            print("❌ Invalid address")
            continue

        row, col = hash160_to_matrix_coordinates(hash160)
        value = matrix[row, col]
        position = row * 128 + col

        # Check special positions
        special = check_special_positions(row, col)

        # Track distributions
        row_distribution[row] = row_distribution.get(row, 0) + 1
        col_distribution[col] = col_distribution.get(col, 0) + 1

        if special['exception_column']:
            exception_col_count += 1
        if special['factory_row']:
            factory_row_count += 1
        if special['row_21_bitcoin_input']:
            row_21_count += 1

        # Check if Genesis address (50 BTC, never moved)
        is_genesis = False
        if balance is not None and balance >= 49.9:  # Allow small variance
            is_genesis = True
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
                "position": position,
                "value": int(value)
            },
            "special_positions": special,
            "is_genesis_candidate": is_genesis
        }

        results.append(result)

        status = "🟢" if balance and balance >= 49.9 else "⚪"
        bal_str = f"{balance:.1f}" if balance is not None else "0.0"
        print(f"{status} Row {row:3d}, Col {col:3d}, Val {value:4d}, Bal {bal_str} BTC")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()

    # Summary statistics
    print(f"Total blocks analyzed: {len(results)}")
    print(f"Genesis candidates (50 BTC): {len(genesis_addresses)}")
    print()

    print("MATRIX POSITION DISTRIBUTION:")
    print(f"  Exception Columns: {exception_col_count} ({exception_col_count/len(results)*100:.1f}%)")
    print(f"  Factory Rows: {factory_row_count} ({factory_row_count/len(results)*100:.1f}%)")
    print(f"  Row 21 (Bitcoin Input): {row_21_count} ({row_21_count/len(results)*100:.1f}%)")
    print()

    # Top rows
    print("TOP 10 MOST USED ROWS:")
    top_rows = sorted(row_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    for row, count in top_rows:
        print(f"  Row {row:3d}: {count:3d} addresses ({count/len(results)*100:.1f}%)")
    print()

    # Top columns
    print("TOP 10 MOST USED COLUMNS:")
    top_cols = sorted(col_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    for col, count in top_cols:
        print(f"  Col {col:3d}: {count:3d} addresses ({count/len(results)*100:.1f}%)")
    print()

    # Genesis addresses details
    if genesis_addresses:
        print("=" * 80)
        print(f"GENESIS ADDRESSES FOUND: {len(genesis_addresses)}")
        print("=" * 80)
        print()

        for ga in genesis_addresses:
            print(f"Block {ga['block']:3d}: {ga['address']}")
            print(f"  Balance: {ga['balance']:.8f} BTC")
            print(f"  Matrix: Row {ga['row']}, Col {ga['col']}, Value {ga['value']}")
            print(f"  Special: Exception Col={ga['special']['exception_column']}, "
                  f"Factory Row={ga['special']['factory_row']}, "
                  f"Row 21={ga['special']['row_21_bitcoin_input']}")
            print()

        # Check if they cluster
        genesis_rows = [ga['row'] for ga in genesis_addresses]
        genesis_cols = [ga['col'] for ga in genesis_addresses]

        print("GENESIS CLUSTERING ANALYSIS:")
        print(f"  Unique rows: {len(set(genesis_rows))}")
        print(f"  Unique cols: {len(set(genesis_cols))}")

        # Check exception columns
        genesis_exception = sum(1 for ga in genesis_addresses if ga['special']['exception_column'])
        print(f"  In exception columns: {genesis_exception}/{len(genesis_addresses)} "
              f"({genesis_exception/len(genesis_addresses)*100:.1f}%)")

        # Check factory rows
        genesis_factory = sum(1 for ga in genesis_addresses if ga['special']['factory_row'])
        print(f"  In factory rows: {genesis_factory}/{len(genesis_addresses)} "
              f"({genesis_factory/len(genesis_addresses)*100:.1f}%)")

        # Sum of matrix values
        genesis_value_sum = sum(ga['value'] for ga in genesis_addresses)
        print(f"  Sum of matrix values: {genesis_value_sum}")
        print(f"  Average matrix value: {genesis_value_sum/len(genesis_addresses):.2f}")
        print()

    # Save results
    output_data = {
        "metadata": {
            "analysis_date": "2026-02-07",
            "total_blocks": len(results),
            "genesis_candidates": len(genesis_addresses)
        },
        "all_blocks": results,
        "genesis_addresses": genesis_addresses,
        "statistics": {
            "exception_columns": exception_col_count,
            "factory_rows": factory_row_count,
            "row_21": row_21_count,
            "row_distribution": row_distribution,
            "col_distribution": col_distribution
        }
    }

    output_path = Path(__file__).parent / "FULL_676_BLOCKS_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Results saved to: {output_path}")
    print()

if __name__ == "__main__":
    main()
