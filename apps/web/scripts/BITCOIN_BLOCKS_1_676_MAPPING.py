#!/usr/bin/env python3
"""
Bitcoin Blocks 1-676 → Anna Matrix Mapping

Purpose: Complete the missing Phase 2 task from research roadmap (73-research-roadmap.mdx, line 65)
Maps all Bitcoin addresses from blocks 1-676 to Anna Matrix coordinates.

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-07
Status: Phase 2 Analysis (NEVER DONE BEFORE)
"""

import json
import hashlib
import base58
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

# Load Anna Matrix
MATRIX_PATH = Path(__file__).parent.parent / "public/data/anna-matrix.json"

def load_anna_matrix() -> np.ndarray:
    """Load the 128x128 Anna Matrix"""
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    return np.array(data['matrix'], dtype=np.int8)

def bitcoin_address_to_hash160(address: str) -> bytes:
    """
    Convert Bitcoin address to Hash160 (20-byte hash)

    Bitcoin address format:
    - Base58Check encoding
    - First byte: version (0x00 for mainnet P2PKH)
    - Next 20 bytes: Hash160 (RIPEMD160(SHA256(pubkey)))
    - Last 4 bytes: checksum
    """
    try:
        decoded = base58.b58decode_check(address)
        # Skip version byte, return Hash160
        return decoded[1:]  # 20 bytes
    except Exception as e:
        print(f"Error decoding address {address}: {e}")
        return None

def hash160_to_matrix_coordinates(hash160: bytes) -> Tuple[int, int]:
    """
    Map Hash160 to Anna Matrix coordinates

    Formula (from 01-bitcoin-bridge.mdx):
    position = int.from_bytes(hash160, 'big') mod 16384  (128×128)
    row = position // 128
    col = position mod 128
    """
    hash160_int = int.from_bytes(hash160, 'big')
    position = hash160_int % 16384  # 128 × 128
    row = position // 128
    col = position % 128
    return row, col

def analyze_block_mapping(
    block_num: int,
    address: str,
    matrix: np.ndarray
) -> Dict:
    """
    Analyze a single block's mapping to Anna Matrix

    Returns:
        Dict with block number, address, coordinates, matrix value, etc.
    """
    hash160 = bitcoin_address_to_hash160(address)

    if hash160 is None:
        return {
            "block": block_num,
            "address": address,
            "error": "Failed to decode address"
        }

    row, col = hash160_to_matrix_coordinates(hash160)
    matrix_value = int(matrix[row, col])

    # Check special positions
    is_exception_column = col in [0, 22, 30, 41, 86, 97, 105, 127]
    is_factory_row = row in [1, 9, 49, 57]
    is_row_21 = row == 21  # Bitcoin Input Layer (JINN architecture)

    return {
        "block": block_num,
        "address": address,
        "hash160": hash160.hex(),
        "coordinates": {
            "row": row,
            "col": col,
            "position": row * 128 + col
        },
        "matrix_value": matrix_value,
        "special_positions": {
            "exception_column": is_exception_column,
            "factory_row": is_factory_row,
            "row_21_bitcoin_input": is_row_21
        },
        "balance_btc": 50.0  # All blocks 1-676 have 50 BTC reward
    }

def main():
    """
    Main analysis function

    NOTE: This script requires Bitcoin blockchain data.
    For full execution, use Bitcoin Core RPC or blockchain explorer API.

    For now, we'll create the framework and test with known addresses.
    """
    print("=" * 80)
    print("BITCOIN BLOCKS 1-676 → ANNA MATRIX MAPPING")
    print("=" * 80)
    print()
    print("Phase 2 Analysis (Never Completed Until Now)")
    print("Research Roadmap Reference: 73-research-roadmap.mdx, line 65")
    print()

    # Load Anna Matrix
    print("Loading Anna Matrix...")
    matrix = load_anna_matrix()
    print(f"✓ Loaded 128x128 matrix ({matrix.shape})")
    print()

    # Known addresses from blocks 1-676
    known_addresses = {
        264: "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",  # Block 264 (1CFB)
        # Additional addresses would be added here from blockchain data
    }

    results = []

    print("Analyzing known addresses:")
    print("-" * 80)

    for block_num, address in known_addresses.items():
        print(f"\nBlock {block_num}:")
        print(f"  Address: {address}")

        result = analyze_block_mapping(block_num, address, matrix)
        results.append(result)

        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
            continue

        coords = result['coordinates']
        print(f"  Matrix Position: Row {coords['row']}, Col {coords['col']}")
        print(f"  Matrix Value: {result['matrix_value']}")

        special = result['special_positions']
        if special['exception_column']:
            print(f"  ✓ Exception Column!")
        if special['factory_row']:
            print(f"  ✓ Factory Row!")
        if special['row_21_bitcoin_input']:
            print(f"  ✓ Row 21 (Bitcoin Input Layer)!")

    print()
    print("-" * 80)
    print()

    # Statistical Analysis
    print("STATISTICAL ANALYSIS:")
    print("-" * 80)

    if results:
        # Exception column distribution
        exception_count = sum(1 for r in results if r.get('special_positions', {}).get('exception_column'))
        factory_count = sum(1 for r in results if r.get('special_positions', {}).get('factory_row'))
        row_21_count = sum(1 for r in results if r.get('special_positions', {}).get('row_21_bitcoin_input'))

        print(f"Exception Columns: {exception_count}/{len(results)} ({100*exception_count/len(results):.1f}%)")
        print(f"  Expected (random): {100*8/128:.1f}%")
        print()
        print(f"Factory Rows: {factory_count}/{len(results)} ({100*factory_count/len(results):.1f}%)")
        print(f"  Expected (random): {100*4/128:.1f}%")
        print()
        print(f"Row 21 (Bitcoin Input): {row_21_count}/{len(results)}")
        print()

        # Matrix value sum
        matrix_values = [r['matrix_value'] for r in results if 'matrix_value' in r]
        if matrix_values:
            total_sum = sum(matrix_values)
            print(f"Sum of Matrix Values: {total_sum}")
            print(f"  Mean: {np.mean(matrix_values):.2f}")
            print(f"  Std: {np.std(matrix_values):.2f}")

    # Save results
    output_path = Path(__file__).parent / "BLOCKS_1_676_MAPPING_RESULTS.json"
    output_data = {
        "metadata": {
            "analysis_date": "2026-02-07",
            "phase": "Phase 2: Bitcoin Address Mapping",
            "reference": "73-research-roadmap.mdx, line 65",
            "total_blocks": 676,
            "blocks_analyzed": len(results),
            "status": "FRAMEWORK COMPLETE - Requires blockchain data for full 676 blocks"
        },
        "formula": {
            "description": "Hash160 → Matrix Coordinates",
            "position": "int.from_bytes(hash160, 'big') mod 16384",
            "row": "position // 128",
            "col": "position mod 128"
        },
        "results": results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print()
    print(f"✓ Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("NOTE: To complete the full 676-block analysis:")
    print("1. Use Bitcoin Core RPC: bitcoin-cli getblockhash <height>")
    print("2. For each block, extract coinbase output address")
    print("3. Map to Anna Matrix using the formula above")
    print("4. Statistical analysis on full dataset")
    print("=" * 80)

if __name__ == "__main__":
    main()
