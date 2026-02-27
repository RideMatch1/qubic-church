#!/usr/bin/env python3
"""
Blocks 1-676 Special Patterns Analysis

Purpose: Find ALL special patterns in Bitcoin blocks 1-676.
This is the complete Phase 2 analysis that was identified but never completed.

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-07
"""

import json
import base58
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

def load_anna_matrix() -> np.ndarray:
    """Load the Anna Matrix from JSON file"""
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    return np.array(data['matrix'], dtype=np.int8)

def bitcoin_address_to_hash160(address: str) -> bytes:
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

def check_vanity_patterns(address: str) -> Dict:
    """
    Check if address has readable vanity patterns

    Common patterns:
    - Repeated characters (e.g., "111", "AAA")
    - Readable words or abbreviations
    - Numerical sequences
    """
    patterns = {
        "has_cfb": "CFB" in address.upper(),
        "has_btc": "BTC" in address.upper(),
        "has_satoshi": "SAT" in address.upper(),
        "has_god": "GOD" in address.upper(),
        "has_hal": "HAL" in address.upper(),
        "starts_with_1": address.startswith("1"),
        "repeated_chars": [],
        "readable_segments": []
    }

    # Check for repeated characters (3+ in a row)
    for i in range(len(address) - 2):
        if address[i] == address[i+1] == address[i+2]:
            patterns["repeated_chars"].append(address[i:i+3])

    # Check for readable 3+ character segments
    readable_words = ["CFB", "BTC", "SAT", "GOD", "HAL", "BIT", "COIN", "KEY", "PUB"]
    for word in readable_words:
        if word in address.upper():
            patterns["readable_segments"].append(word)

    patterns["is_vanity"] = (
        patterns["has_cfb"] or
        patterns["has_btc"] or
        patterns["has_satoshi"] or
        len(patterns["repeated_chars"]) > 0 or
        len(patterns["readable_segments"]) > 1
    )

    return patterns

def analyze_timestamp_patterns(timestamp: int) -> Dict:
    """
    Analyze timestamp for modular arithmetic patterns

    Note: After Bonferroni correction, most modular patterns are NOT significant
    We report them for completeness but mark significance level
    """
    return {
        "timestamp": timestamp,
        "mod_27": timestamp % 27,
        "mod_121": timestamp % 121,
        "mod_676": timestamp % 676,
        "mod_16384": timestamp % 16384,
        "note": "Modular patterns require Bonferroni correction for significance"
    }

def analyze_coinbase_data(coinbase_hex: str) -> Dict:
    """
    Analyze coinbase data for ASCII messages

    Early blocks had Satoshi's messages in coinbase
    """
    try:
        # Try to decode as ASCII
        coinbase_bytes = bytes.fromhex(coinbase_hex)
        ascii_text = ""
        for byte in coinbase_bytes:
            if 32 <= byte <= 126:  # Printable ASCII
                ascii_text += chr(byte)
            else:
                ascii_text += "."

        has_ascii = any(32 <= b <= 126 for b in coinbase_bytes)

        return {
            "hex": coinbase_hex,
            "has_ascii": has_ascii,
            "ascii_text": ascii_text if has_ascii else None,
            "length": len(coinbase_bytes)
        }
    except Exception:
        return {
            "hex": coinbase_hex,
            "has_ascii": False,
            "error": "Failed to decode"
        }

def check_patoshi_signature(nonce: int, block: int) -> Dict:
    """
    Check for Patoshi signature pattern

    Patoshi blocks have characteristic nonce patterns:
    - Last byte typically 0-49
    - Non-random distribution

    Note: This requires full block data including nonce
    """
    if nonce is None:
        return {
            "status": "PENDING - requires blockchain data",
            "block": block
        }

    nonce_bytes = nonce.to_bytes(4, 'little')
    last_byte = nonce_bytes[3]

    return {
        "nonce": nonce,
        "last_byte": last_byte,
        "in_patoshi_range": 0 <= last_byte <= 49,
        "pattern": "Patoshi" if 0 <= last_byte <= 49 else "Non-Patoshi",
        "note": "Patoshi typically used nonce last byte 0-49"
    }

def analyze_hash_patterns(block_hash: str) -> Dict:
    """
    Analyze block hash for encoded numbers

    Check if hash contains significant numbers:
    - 676, 26, 50, 576, 121, etc.
    """
    hash_hex = block_hash.lower()

    # Convert to integer
    hash_int = int(hash_hex, 16)

    patterns = {
        "hash": block_hash,
        "contains_676": "676" in hash_hex,
        "contains_26": "26" in hash_hex,
        "contains_50": "50" in hash_hex,
        "contains_576": "576" in hash_hex,
        "contains_121": "121" in hash_hex,
        "leading_zeros": len(hash_hex) - len(hash_hex.lstrip('0')),
        "hash_sum": sum(int(c, 16) for c in hash_hex),
        "hash_mod_676": hash_int % 676,
        "hash_mod_16384": hash_int % 16384
    }

    return patterns

def analyze_matrix_clustering(coordinates: List[Tuple[int, int]]) -> Dict:
    """
    Analyze if the 676 addresses cluster in certain areas of the matrix

    Statistical analysis:
    - Row distribution
    - Column distribution
    - Exception column concentration
    - Factory row concentration
    """
    rows = [coord[0] for coord in coordinates]
    cols = [coord[1] for coord in coordinates]

    # Exception columns from previous analysis
    exception_cols = [0, 22, 30, 41, 86, 97, 105, 127]
    factory_rows = [0, 1, 2, 126, 127]
    bitcoin_input_row = 21

    exception_col_count = sum(1 for col in cols if col in exception_cols)
    factory_row_count = sum(1 for row in rows if row in factory_rows)
    bitcoin_row_count = sum(1 for row in rows if row == bitcoin_input_row)

    # Row distribution
    row_counts = {}
    for row in rows:
        row_counts[row] = row_counts.get(row, 0) + 1

    # Column distribution
    col_counts = {}
    for col in cols:
        col_counts[col] = col_counts.get(col, 0) + 1

    # Top concentrated rows
    top_rows = sorted(row_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_cols = sorted(col_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_addresses": len(coordinates),
        "unique_rows": len(row_counts),
        "unique_cols": len(col_counts),
        "exception_column_count": exception_col_count,
        "exception_column_percentage": (exception_col_count / len(coordinates)) * 100,
        "factory_row_count": factory_row_count,
        "factory_row_percentage": (factory_row_count / len(coordinates)) * 100,
        "row_21_count": bitcoin_row_count,
        "row_21_percentage": (bitcoin_row_count / len(coordinates)) * 100,
        "top_10_rows": [(row, count) for row, count in top_rows],
        "top_10_cols": [(col, count) for col, count in top_cols],
        "interpretation": {
            "expected_uniform": "Each row/col should have ~5.3 addresses if uniform (676/128)",
            "clustering_threshold": "Count > 10 indicates clustering"
        }
    }

def analyze_corresponding_mechanism() -> Dict:
    """
    Analyze what "corresponding to Blocks 1 through 676" means

    From GENESIS Message #1:
    "Each will receive 50 units of account, corresponding to Blocks 1 through 676"

    Possible mechanisms:
    1. Block 1 → Holder 1, Block 2 → Holder 2, etc. (direct mapping)
    2. Weighted by holdings (more GENESIS = more blocks claimed)
    3. Random assignment during "the signal"
    4. Address-based mapping (Bitcoin address → Qubic address)
    """
    return {
        "quote": "corresponding to Blocks 1 through 676",
        "total_blocks": 676,
        "total_recipients": 676,
        "units_per_recipient": 50,
        "total_units": 33_800,
        "possible_mechanisms": {
            "mechanism_1": {
                "name": "Direct Block Mapping",
                "description": "Block 1 → Holder 1, Block 2 → Holder 2, etc.",
                "ratio": "1:1 (one block per holder)"
            },
            "mechanism_2": {
                "name": "Weighted by Holdings",
                "description": "More GENESIS tokens = claim more blocks",
                "ratio": "Proportional to holdings"
            },
            "mechanism_3": {
                "name": "Random Assignment",
                "description": "Random distribution during 'the signal'",
                "ratio": "Random (verifiable via protocol)"
            },
            "mechanism_4": {
                "name": "Address-Based Mapping",
                "description": "Bitcoin address Hash160 → Qubic address mapping",
                "ratio": "Cryptographic linkage"
            }
        },
        "evidence": {
            "direct_quote": "corresponding to",
            "unit_amount": "50 (same as BTC block reward)",
            "block_range": "1-676 (early mining era)",
            "recipients": "676 (same as block count)"
        },
        "interpretation": "Most likely: Each recipient corresponds to one specific block (1:1 mapping)"
    }

def main():
    """
    Main special patterns analysis
    """
    print("=" * 80)
    print("BLOCKS 1-676 SPECIAL PATTERNS ANALYSIS")
    print("=" * 80)
    print()
    print("Note: This is a FRAMEWORK for analyzing all 676 blocks.")
    print("Full analysis requires blockchain data for all blocks.")
    print()
    print("Demo: Analyzing Block 264 (1CFB) as example")
    print()
    print("-" * 80)
    print()

    matrix = load_anna_matrix()

    # Example block (Block 264 - 1CFB)
    example_blocks = [
        {
            "block": 264,
            "address": "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg",
            "timestamp": None,  # Would need blockchain data
            "coinbase": None,   # Would need blockchain data
            "hash": None,       # Would need blockchain data
            "nonce": None       # Would need blockchain data
        }
    ]

    # Results storage
    results = {
        "metadata": {
            "analysis_date": "2026-02-07",
            "total_blocks": 676,
            "blocks_analyzed": len(example_blocks),
            "status": "FRAMEWORK - Requires full blockchain data"
        },
        "vanity_addresses": [],
        "matrix_coordinates": [],
        "patoshi_blocks": [],
        "special_patterns": []
    }

    # Analyze example blocks
    for block_data in example_blocks:
        block = block_data["block"]
        address = block_data["address"]

        print(f"Analyzing Block {block}...")
        print(f"Address: {address}")
        print()

        # 1. Vanity Pattern Check
        print("1. VANITY PATTERN CHECK")
        print("-" * 80)
        vanity = check_vanity_patterns(address)
        print(f"Is Vanity: {vanity['is_vanity']}")
        print(f"Has CFB: {vanity['has_cfb']}")
        print(f"Has BTC: {vanity['has_btc']}")
        print(f"Readable Segments: {vanity['readable_segments']}")
        print()

        if vanity['is_vanity']:
            results['vanity_addresses'].append({
                "block": block,
                "address": address,
                "patterns": vanity
            })

        # 2. Matrix Mapping
        print("2. MATRIX MAPPING")
        print("-" * 80)
        hash160 = bitcoin_address_to_hash160(address)
        if hash160:
            row, col = hash160_to_matrix_coordinates(hash160)
            value = matrix[row, col]
            print(f"Coordinates: Row {row}, Col {col}")
            print(f"Matrix Value: {value}")
            print()

            results['matrix_coordinates'].append({
                "block": block,
                "address": address,
                "row": row,
                "col": col,
                "value": int(value)
            })

        # 3. Timestamp Patterns (if available)
        if block_data['timestamp']:
            print("3. TIMESTAMP PATTERNS")
            print("-" * 80)
            timestamp_analysis = analyze_timestamp_patterns(block_data['timestamp'])
            print(f"Timestamp: {timestamp_analysis['timestamp']}")
            print(f"mod 27: {timestamp_analysis['mod_27']}")
            print(f"mod 121: {timestamp_analysis['mod_121']}")
            print(f"mod 676: {timestamp_analysis['mod_676']}")
            print(f"Note: {timestamp_analysis['note']}")
            print()

        # 4. Coinbase Data (if available)
        if block_data['coinbase']:
            print("4. COINBASE MESSAGE")
            print("-" * 80)
            coinbase = analyze_coinbase_data(block_data['coinbase'])
            if coinbase['has_ascii']:
                print(f"ASCII Text: {coinbase['ascii_text']}")
            print()

        # 5. Patoshi Signature (if nonce available)
        if block_data['nonce']:
            print("5. PATOSHI SIGNATURE")
            print("-" * 80)
            patoshi = check_patoshi_signature(block_data['nonce'], block)
            print(f"Pattern: {patoshi['pattern']}")
            print(f"In Range: {patoshi['in_patoshi_range']}")
            print()

            if patoshi['in_patoshi_range']:
                results['patoshi_blocks'].append({
                    "block": block,
                    "nonce": block_data['nonce'],
                    "last_byte": patoshi['last_byte']
                })

        # 6. Hash Patterns (if hash available)
        if block_data['hash']:
            print("6. HASH PATTERNS")
            print("-" * 80)
            hash_analysis = analyze_hash_patterns(block_data['hash'])
            print(f"Contains 676: {hash_analysis['contains_676']}")
            print(f"Contains 26: {hash_analysis['contains_26']}")
            print(f"Hash mod 676: {hash_analysis['hash_mod_676']}")
            print()

        print("-" * 80)
        print()

    # Matrix Clustering Analysis
    if results['matrix_coordinates']:
        print("MATRIX CLUSTERING ANALYSIS")
        print("=" * 80)

        coords = [(item['row'], item['col']) for item in results['matrix_coordinates']]
        clustering = analyze_matrix_clustering(coords)

        print(f"Total Addresses: {clustering['total_addresses']}")
        print(f"Unique Rows: {clustering['unique_rows']}")
        print(f"Unique Cols: {clustering['unique_cols']}")
        print()
        print(f"Exception Columns: {clustering['exception_column_count']} ({clustering['exception_column_percentage']:.1f}%)")
        print(f"Factory Rows: {clustering['factory_row_count']} ({clustering['factory_row_percentage']:.1f}%)")
        print(f"Row 21 (Bitcoin): {clustering['row_21_count']} ({clustering['row_21_percentage']:.1f}%)")
        print()
        print(f"Expected Uniform Distribution: {clustering['interpretation']['expected_uniform']}")
        print()

        results['clustering_analysis'] = clustering
        print("-" * 80)
        print()

    # "Corresponding To" Mechanism
    print("'CORRESPONDING TO' MECHANISM ANALYSIS")
    print("=" * 80)

    mechanism = analyze_corresponding_mechanism()
    print(f"Quote: \"{mechanism['quote']}\"")
    print()
    print(f"Total Blocks: {mechanism['total_blocks']}")
    print(f"Total Recipients: {mechanism['total_recipients']}")
    print(f"Units per Recipient: {mechanism['units_per_recipient']}")
    print(f"Total Units: {mechanism['total_units']:,}")
    print()

    print("Possible Mechanisms:")
    for key, mech in mechanism['possible_mechanisms'].items():
        print(f"  {mech['name']}:")
        print(f"    {mech['description']}")
        print(f"    Ratio: {mech['ratio']}")
        print()

    print(f"Interpretation: {mechanism['interpretation']}")
    print()

    results['corresponding_mechanism'] = mechanism
    print("-" * 80)
    print()

    # Summary
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"✓ Framework created for analyzing all 676 blocks")
    print(f"✓ Vanity addresses found: {len(results['vanity_addresses'])}")
    print(f"✓ Matrix coordinates mapped: {len(results['matrix_coordinates'])}")
    print()
    print("NEXT STEPS:")
    print("  1. Obtain blockchain data for blocks 1-676")
    print("  2. Extract: addresses, timestamps, coinbase, hashes, nonces")
    print("  3. Run this analysis on all 676 blocks")
    print("  4. Identify which are the '11 Genesis addresses with 550 BTC'")
    print("  5. Map all addresses to Anna Matrix")
    print("  6. Analyze clustering patterns")
    print("  7. Determine 'corresponding to' mechanism")
    print()
    print("STATISTICAL REQUIREMENTS:")
    print("  - Bonferroni correction for all multi-test scenarios")
    print("  - Report ONLY p < 0.05 after correction as significant")
    print("  - Mark look-elsewhere effects explicitly")
    print("  - Use Monte Carlo controls where applicable")
    print()
    print("=" * 80)

    # Save results
    output_path = Path(__file__).parent / "BLOCKS_1_676_PATTERNS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"✓ Results saved to: {output_path}")
    print()
    print("Note: This is a FRAMEWORK. Full 676-block analysis requires:")
    print("  - Bitcoin Core node OR blockchain API access")
    print("  - Extract data for each block 1-676")
    print("  - Run this script with complete data")
    print()

if __name__ == "__main__":
    main()
