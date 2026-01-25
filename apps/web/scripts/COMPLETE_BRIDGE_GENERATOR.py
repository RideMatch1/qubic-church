#!/usr/bin/env python3
"""
COMPLETE BRIDGE GENERATOR
=========================

Systematically derives ALL Bitcoin-Qubic bridges from the Anna Matrix.

Methods:
1. Single columns (128 columns × 128 offsets = 16,384 tests)
2. XOR column pairs (64 pairs × various methods)
3. Single rows (128 rows × 128 offsets = 16,384 tests)

Output: COMPLETE_BRIDGE_DATASET.json

Author: qubic-academic-docs
Date: 2026-01-23
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import ecdsa
    from ecdsa import SECP256k1, SigningKey
    HAS_ECDSA = True
except ImportError:
    HAS_ECDSA = False
    print("WARNING: ecdsa not installed. Run: pip install ecdsa")

try:
    from qubipy.crypto import (
        get_subseed_from_seed,
        get_private_key_from_subseed,
        get_public_key_from_private_key,
        get_identity_from_public_key
    )
    HAS_QUBIPY = True
except ImportError:
    HAS_QUBIPY = False
    print("WARNING: qubipy not installed. Run: pip install qubipy")

from anna_matrix_utils import load_anna_matrix


# Base58 alphabet for Bitcoin addresses
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58."""
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = BASE58_ALPHABET[remainder] + result

    # Add leading zeros
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break

    return result


def base58check_encode(data: bytes) -> str:
    """Encode bytes to Base58Check (with checksum)."""
    checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    return base58_encode(data + checksum)


def private_key_to_wif(private_key: bytes, compressed: bool = True) -> str:
    """Convert private key bytes to WIF format."""
    version = b'\x80'  # Mainnet
    if compressed:
        data = version + private_key + b'\x01'
    else:
        data = version + private_key
    return base58check_encode(data)


def bytes_to_btc_address(key_bytes: bytes) -> Tuple[str, str, str]:
    """
    Convert 32 bytes to Bitcoin address.

    Returns:
        Tuple of (address, hash160_hex, wif)
    """
    if not HAS_ECDSA:
        return ("", "", "")

    try:
        # Create signing key from bytes
        sk = SigningKey.from_string(key_bytes, curve=SECP256k1)
        vk = sk.get_verifying_key()

        # Compressed public key
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        if y % 2 == 0:
            public_key = b'\x02' + x.to_bytes(32, 'big')
        else:
            public_key = b'\x03' + x.to_bytes(32, 'big')

        # Hash160 = RIPEMD160(SHA256(pubkey))
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()

        # Bitcoin address with version byte 0x00 (mainnet)
        address = base58check_encode(b'\x00' + ripemd160)

        # WIF
        wif = private_key_to_wif(key_bytes, compressed=True)

        return (address, ripemd160.hex(), wif)
    except Exception as e:
        return ("", "", "")


def safe_value(v: Any) -> int:
    """Convert matrix value to int, handling strings like '00000000'."""
    if isinstance(v, str):
        try:
            return int(v, 16) if len(v) == 8 else int(v)
        except:
            return 0
    return v


def extract_column_bytes(matrix: List[List[int]], column: int, offset: int = 0) -> bytes:
    """
    Extract 32 bytes from a column starting at offset (with wrapping).

    Args:
        matrix: 128x128 Anna matrix
        column: Column index (0-127)
        offset: Starting row offset (0-127)

    Returns:
        32 bytes extracted from the column
    """
    result = []
    for i in range(32):
        row = (offset + i) % 128
        value = safe_value(matrix[row][column])
        # Convert signed byte to unsigned
        result.append(value & 0xFF)
    return bytes(result)


def extract_row_bytes(matrix: List[List[int]], row: int, offset: int = 0) -> bytes:
    """
    Extract 32 bytes from a row starting at offset (with wrapping).

    Args:
        matrix: 128x128 Anna matrix
        row: Row index (0-127)
        offset: Starting column offset (0-127)

    Returns:
        32 bytes extracted from the row
    """
    result = []
    for i in range(32):
        col = (offset + i) % 128
        value = safe_value(matrix[row][col])
        # Convert signed byte to unsigned
        result.append(value & 0xFF)
    return bytes(result)


def extract_xor_seed(matrix: List[List[int]], col1: int, col2: int) -> str:
    """
    Extract Qubic seed from XOR of two columns.
    Only extracts lowercase letters (a-z).

    Args:
        matrix: 128x128 Anna matrix
        col1: First column index
        col2: Second column index (typically 127 - col1)

    Returns:
        55-character seed string (padded with 'a' if needed)
    """
    letters = []
    for row in range(128):
        v1 = safe_value(matrix[row][col1]) & 0xFF
        v2 = safe_value(matrix[row][col2]) & 0xFF
        xor_val = v1 ^ v2

        # Check if it's a lowercase letter (97-122 = 'a'-'z')
        if 97 <= xor_val <= 122:
            letters.append(chr(xor_val))

    # Create 55-character seed (pad with 'a' if needed)
    seed = ''.join(letters[:55])
    seed = seed.ljust(55, 'a')

    return seed


def extract_direct_seed(matrix: List[List[int]], column: int) -> str:
    """
    Extract Qubic seed directly from column values as letters.

    Args:
        matrix: 128x128 Anna matrix
        column: Column index

    Returns:
        55-character seed string
    """
    letters = []
    for row in range(128):
        value = safe_value(matrix[row][column]) & 0xFF
        # Check if it's a lowercase letter
        if 97 <= value <= 122:
            letters.append(chr(value))

    seed = ''.join(letters[:55])
    seed = seed.ljust(55, 'a')

    return seed


def seed_to_qubic_identity(seed: str) -> str:
    """
    Convert a 55-character seed to Qubic Identity.

    Args:
        seed: 55-character lowercase seed

    Returns:
        60-character Qubic Identity or empty string on error
    """
    if not HAS_QUBIPY:
        return ""

    try:
        if len(seed) != 55:
            seed = seed[:55].ljust(55, 'a')

        subseed = get_subseed_from_seed(seed.encode('ascii'))
        private_key = get_private_key_from_subseed(subseed)
        public_key = get_public_key_from_private_key(private_key)
        identity = get_identity_from_public_key(public_key)

        return identity
    except Exception as e:
        return ""


def to_ternary(value: int) -> int:
    """Convert matrix value to ternary state (-1, 0, +1)."""
    if value > 42:
        return 1
    elif value < -42:
        return -1
    else:
        return 0


def categorize_ternary(matrix: List[List[int]], column: int) -> Dict[str, Any]:
    """
    Categorize a column based on ternary states.

    Returns:
        Dict with ternary analysis
    """
    ternary_sum = 0
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for row in range(128):
        value = safe_value(matrix[row][column])
        t = to_ternary(value)
        ternary_sum += t

        if t == 1:
            positive_count += 1
        elif t == -1:
            negative_count += 1
        else:
            neutral_count += 1

    if ternary_sum > 32:
        category = "POSITIVE"
    elif ternary_sum < -32:
        category = "NEGATIVE"
    else:
        category = "NEUTRAL"

    return {
        "sum": ternary_sum,
        "category": category,
        "positive_neurons": positive_count,
        "negative_neurons": negative_count,
        "neutral_neurons": neutral_count
    }


def compute_3d_position(column: int, offset: int) -> Dict[str, Any]:
    """
    Compute 3D position for visualization.

    Returns:
        Dict with 3D coordinates and layer info
    """
    x = column
    y = offset
    z = (column + offset) % 3  # Layer 0, 1, or 2

    return {
        "position": [x, y, z],
        "layer": z
    }


def find_mirror_info(column: int, offset: int) -> Dict[str, Any]:
    """
    Find mirror/symmetry information for a bridge position.

    Returns:
        Dict with symmetry info
    """
    mirror_col = 127 - column
    mirror_offset = 127 - offset

    is_self_symmetric = (column == mirror_col and offset == mirror_offset)

    return {
        "mirror_column": mirror_col,
        "mirror_offset": mirror_offset,
        "is_self_symmetric": is_self_symmetric
    }


def generate_all_bridges(matrix: List[List[int]],
                         filter_0x7b: bool = True,
                         verbose: bool = True) -> List[Dict[str, Any]]:
    """
    Generate all bridges from the matrix.

    Args:
        matrix: 128x128 Anna matrix
        filter_0x7b: If True, only include bridges with 0x7b prefix
        verbose: Print progress information

    Returns:
        List of bridge dictionaries
    """
    bridges = []
    bridge_id = 0

    if verbose:
        print("Generating bridges from Anna Matrix...")
        print("=" * 60)

    # ========================================
    # Method 1: Single Columns
    # ========================================
    if verbose:
        print("\n[1/3] Scanning single columns (128 × 128 = 16,384 tests)...")

    column_bridges = 0
    for col in range(128):
        for offset in range(128):
            key_bytes = extract_column_bytes(matrix, col, offset)
            address, hash160, wif = bytes_to_btc_address(key_bytes)

            if not address:
                continue

            prefix = hash160[:2] if hash160 else ""

            # Filter by 0x7b prefix if requested
            if filter_0x7b and prefix != "7b":
                continue

            bridge_id += 1
            column_bridges += 1

            # Get symmetric column for XOR seed
            symmetric_col = 127 - col
            xor_seed = extract_xor_seed(matrix, col, symmetric_col)
            qubic_identity = seed_to_qubic_identity(xor_seed)

            # Also get direct seed
            direct_seed = extract_direct_seed(matrix, col)
            direct_identity = seed_to_qubic_identity(direct_seed)

            # Ternary analysis
            ternary = categorize_ternary(matrix, col)

            # 3D position
            position_3d = compute_3d_position(col, offset)

            # Symmetry info
            symmetry = find_mirror_info(col, offset)

            bridge = {
                "id": bridge_id,
                "type": "column",
                "name": f"Col{col}_Off{offset}",
                "column": col,
                "offset": offset,
                "symmetric_column": symmetric_col,
                "bitcoin": {
                    "address": address,
                    "hash160": hash160,
                    "wif": wif,
                    "private_key": key_bytes.hex(),
                    "prefix": f"0x{prefix}"
                },
                "qubic_xor": {
                    "seed": xor_seed,
                    "identity": qubic_identity,
                    "method": f"XOR columns {col}↔{symmetric_col}"
                },
                "qubic_direct": {
                    "seed": direct_seed,
                    "identity": direct_identity,
                    "method": f"Direct letters from column {col}"
                },
                "ternary": ternary,
                "3d": position_3d,
                "symmetry": symmetry
            }

            # Check for special addresses
            if address.startswith("1CFB"):
                bridge["name"] = f"1CFB (CFB Signature!) Col{col}"
                bridge["special"] = "CFB_SIGNATURE"
            elif address.startswith("1CF"):
                bridge["name"] = f"1CF* Col{col}"
                bridge["special"] = "CF_PREFIX"

            bridges.append(bridge)

    if verbose:
        print(f"   Found {column_bridges} bridges from columns")

    # ========================================
    # Method 2: Single Rows
    # ========================================
    if verbose:
        print("\n[2/3] Scanning single rows (128 × 128 = 16,384 tests)...")

    row_bridges = 0
    for row in range(128):
        for offset in range(128):
            key_bytes = extract_row_bytes(matrix, row, offset)
            address, hash160, wif = bytes_to_btc_address(key_bytes)

            if not address:
                continue

            prefix = hash160[:2] if hash160 else ""

            if filter_0x7b and prefix != "7b":
                continue

            bridge_id += 1
            row_bridges += 1

            # For rows, use row XOR with symmetric row
            symmetric_row = 127 - row

            # Ternary analysis (use row index as proxy)
            ternary = {
                "sum": sum(to_ternary(safe_value(matrix[row][c])) for c in range(128)),
                "category": "ROW",
                "row": row
            }

            # 3D position
            position_3d = compute_3d_position(row, offset)

            # Symmetry info
            symmetry = {
                "mirror_row": symmetric_row,
                "mirror_offset": 127 - offset,
                "is_self_symmetric": (row == symmetric_row and offset == 127 - offset)
            }

            bridge = {
                "id": bridge_id,
                "type": "row",
                "name": f"Row{row}_Off{offset}",
                "row": row,
                "offset": offset,
                "symmetric_row": symmetric_row,
                "bitcoin": {
                    "address": address,
                    "hash160": hash160,
                    "wif": wif,
                    "private_key": key_bytes.hex(),
                    "prefix": f"0x{prefix}"
                },
                "ternary": ternary,
                "3d": position_3d,
                "symmetry": symmetry
            }

            if address.startswith("1CFB"):
                bridge["name"] = f"1CFB (CFB!) Row{row}"
                bridge["special"] = "CFB_SIGNATURE"
            elif address.startswith("1CF"):
                bridge["name"] = f"1CF* Row{row}"
                bridge["special"] = "CF_PREFIX"

            bridges.append(bridge)

    if verbose:
        print(f"   Found {row_bridges} bridges from rows")

    # ========================================
    # Method 3: XOR Column Pairs (Additional)
    # ========================================
    if verbose:
        print("\n[3/3] Analyzing XOR column pairs (64 pairs)...")

    xor_pairs_analyzed = 0
    for col in range(64):
        symmetric_col = 127 - col
        xor_pairs_analyzed += 1

        # XOR the columns and create bytes directly
        xor_bytes = []
        for row in range(128):
            v1 = safe_value(matrix[row][col]) & 0xFF
            v2 = safe_value(matrix[row][symmetric_col]) & 0xFF
            xor_bytes.append(v1 ^ v2)

        # Take first 32 bytes as key
        for offset in range(128 - 31):
            key_bytes = bytes(xor_bytes[offset:offset + 32])
            address, hash160, wif = bytes_to_btc_address(key_bytes)

            if not address:
                continue

            prefix = hash160[:2] if hash160 else ""

            if filter_0x7b and prefix != "7b":
                continue

            bridge_id += 1

            bridge = {
                "id": bridge_id,
                "type": "xor_pair",
                "name": f"XOR_{col}_{symmetric_col}_Off{offset}",
                "column_1": col,
                "column_2": symmetric_col,
                "offset": offset,
                "bitcoin": {
                    "address": address,
                    "hash160": hash160,
                    "wif": wif,
                    "private_key": key_bytes.hex(),
                    "prefix": f"0x{prefix}"
                },
                "3d": compute_3d_position(col, offset),
                "symmetry": {
                    "is_xor_pair": True,
                    "partner_column": symmetric_col
                }
            }

            if address.startswith("1CFB"):
                bridge["name"] = f"1CFB (CFB!) XOR_{col}_{symmetric_col}"
                bridge["special"] = "CFB_SIGNATURE"
            elif address.startswith("1CF"):
                bridge["name"] = f"1CF* XOR_{col}_{symmetric_col}"
                bridge["special"] = "CF_PREFIX"

            bridges.append(bridge)

    if verbose:
        print(f"   Analyzed {xor_pairs_analyzed} XOR pairs")
        print(f"\n{'=' * 60}")
        print(f"TOTAL BRIDGES FOUND: {len(bridges)}")

    return bridges


def generate_statistics(bridges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate statistics about the bridges."""
    stats = {
        "total": len(bridges),
        "by_type": {},
        "by_prefix": {},
        "by_ternary": {},
        "by_layer": {},
        "special": {
            "1CFB": 0,
            "1CF": 0,
            "AI_MEG_GOU": 0
        }
    }

    for bridge in bridges:
        # By type
        btype = bridge.get("type", "unknown")
        stats["by_type"][btype] = stats["by_type"].get(btype, 0) + 1

        # By prefix
        prefix = bridge.get("bitcoin", {}).get("prefix", "unknown")
        stats["by_prefix"][prefix] = stats["by_prefix"].get(prefix, 0) + 1

        # By ternary category
        ternary_cat = bridge.get("ternary", {}).get("category", "unknown")
        stats["by_ternary"][ternary_cat] = stats["by_ternary"].get(ternary_cat, 0) + 1

        # By 3D layer
        layer = bridge.get("3d", {}).get("layer", "unknown")
        layer_key = f"layer_{layer}"
        stats["by_layer"][layer_key] = stats["by_layer"].get(layer_key, 0) + 1

        # Special addresses
        address = bridge.get("bitcoin", {}).get("address", "")
        if address.startswith("1CFB"):
            stats["special"]["1CFB"] += 1
        elif address.startswith("1CF"):
            stats["special"]["1CF"] += 1

        # Check for AI.MEG.GOU in seeds
        xor_seed = bridge.get("qubic_xor", {}).get("seed", "")
        if "aimeg" in xor_seed.lower() or "gou" in xor_seed.lower():
            stats["special"]["AI_MEG_GOU"] += 1

    return stats


def main():
    """Main function."""
    print("=" * 60)
    print("COMPLETE BRIDGE GENERATOR")
    print("Anna Matrix → Bitcoin + Qubic Bridges")
    print("=" * 60)

    # Check dependencies
    if not HAS_ECDSA:
        print("\nERROR: ecdsa library required. Install with: pip install ecdsa")
        return

    if not HAS_QUBIPY:
        print("\nWARNING: qubipy not available. Qubic IDs will be empty.")
        print("Install with: pip install qubipy")

    # Load matrix
    print("\nLoading Anna Matrix...")
    try:
        matrix = load_anna_matrix()
        print(f"Matrix loaded: {len(matrix)}×{len(matrix[0])}")
    except Exception as e:
        print(f"ERROR loading matrix: {e}")
        return

    # Generate bridges
    print("\nGenerating bridges (filtering for 0x7b prefix)...")
    bridges = generate_all_bridges(matrix, filter_0x7b=True, verbose=True)

    # Generate statistics
    stats = generate_statistics(bridges)

    # Create output
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "generator": "COMPLETE_BRIDGE_GENERATOR.py",
            "matrix_size": "128x128",
            "filter": "0x7b prefix",
            "methods": ["column", "row", "xor_pair"]
        },
        "statistics": stats,
        "bridges": bridges
    }

    # Save to file
    output_path = Path(__file__).parent / "COMPLETE_BRIDGE_DATASET.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Output saved to: {output_path}")
    print(f"\nSTATISTICS:")
    print(f"  Total bridges: {stats['total']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  1CFB addresses: {stats['special']['1CFB']}")
    print(f"  1CF* addresses: {stats['special']['1CF']}")
    print(f"  AI.MEG.GOU seeds: {stats['special']['AI_MEG_GOU']}")
    print(f"\n{'=' * 60}")
    print("COMPLETE!")


if __name__ == "__main__":
    main()
