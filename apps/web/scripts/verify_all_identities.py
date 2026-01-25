#!/usr/bin/env python3
"""
MANHATTAN PROJECT - Phase 1: Identity Verification
===================================================

This script verifies ALL strategic node identities by:
1. Converting Anna coordinates to matrix positions using the CORRECT formula
2. Looking up private keys from matrix_cartography.json
3. Re-deriving Qubic identities using QubiPy
4. Comparing with known/hardcoded values

CRITICAL: This must pass 100% before any resonance tests.

Author: qubic-academic-docs
Date: 2026-01-16
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from anna_matrix_utils import anna_to_matrix, STRATEGIC_NODES

# QubiPy import - required for identity derivation
try:
    from qubipy.crypto.utils import (
        get_public_key_from_private_key,
        get_identity_from_public_key
    )
    QUBIPY_AVAILABLE = True
except ImportError:
    QUBIPY_AVAILABLE = False
    print("WARNING: QubiPy not available. Run with .venv_qubic/bin/python")


# Known identities from existing codebase (hardcoded values to verify against)
KNOWN_IDENTITIES = {
    # From check_responses.py
    "ROOT_ALPHA": {"coords": (13, 71), "identity": "AHMXRLTHWSCUUGTBCJXRSMRZDOAAZVCKNFIYDYDLQDQRZETRZMAQYHBACSWK"},
    "ROOT_BETA": {"coords": (18, 110), "identity": "OUMLINFCVWOAFCCPDDRUJARXUKJBJQUYVZFLIUKUUATMEQEIWOIUXHYGQERC"},
    "MEMORY": {"coords": (21, 21), "identity": "VHGZIFEFAPDXEAMCEMNQWJKMVCPAVTNXMECIEFKXXGOGLMYKKERCEMIDZYSD"},
    "VISION": {"coords": (64, 64), "identity": "WMPLINKVMRMPWBMOLFVRDIRJWJCAQDLTLJZJSRWMIEQOPJZWAESVWEFEFZMC"},
    "EXIT": {"coords": (82, 39), "identity": "YLGSNIMGRKONPEBTLCRLYHQDFHEAKMUSRKYOGLPFAFDOFUUYVRBJTNSAXUSM"},
    "VOID": {"coords": (0, 0), "identity": "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB"},
    "ORACLE": {"coords": (11, 110), "identity": "PASOUKIEPXXPXEMUNBKYCPSEIXZBWQCDFZXLUAEBHHENNEHTQNGMMFRGZHHA"},
    "GUARDIAN": {"coords": (19, 18), "identity": "DXASUXXKJAEJVGQEUXLIVNIQWDUCCNFTLEHCDCNZNBVGLPRTJRUQKZDECIPG"},
    "DATE": {"coords": (3, 3), "identity": "MOHTKRBCAEAASFFQQSKLAFBLMZAAKFEJRHIGOQRLOGFKFXZGOXZNSSVDEOOG"},
    # From derive_entry_id.py and broadcast scripts
    "ENTRY": {"coords": (45, 92), "identity": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH"},
    # CORE identity to be derived (not found in existing code)
    "CORE": {"coords": (6, 33), "identity": None},  # Will be derived
}


def load_matrix_cartography():
    """Load the matrix position to private key mapping."""
    cart_path = Path(__file__).parent.parent.parent.parent / "matrix_cartography.json"
    if not cart_path.exists():
        # Try alternative location
        cart_path = Path(__file__).parent.parent.parent.parent / "matrix_cartography.json"

    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "matrix_cartography.json",
        Path(__file__).parent / "matrix_cartography.json",
        Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json"),
    ]

    for p in possible_paths:
        if p.exists():
            with open(p, 'r') as f:
                return json.load(f)

    raise FileNotFoundError("matrix_cartography.json not found")


def derive_identity_from_privkey(privkey_hex: str) -> str:
    """Derive Qubic identity from private key hex string."""
    if not QUBIPY_AVAILABLE:
        return "QUBIPY_NOT_AVAILABLE"

    privkey_bytes = bytes.fromhex(privkey_hex)
    pubkey = get_public_key_from_private_key(privkey_bytes)
    identity = get_identity_from_public_key(pubkey)
    return identity


def verify_coordinate_transformation(anna_x: int, anna_y: int, expected_row: int = None, expected_col: int = None):
    """Verify the coordinate transformation is correct."""
    row, col = anna_to_matrix(anna_x, anna_y)

    # Log the transformation
    print(f"  Transformation: Anna({anna_x}, {anna_y}) -> matrix[{row}][{col}]")

    if expected_row is not None and expected_col is not None:
        if row != expected_row or col != expected_col:
            print(f"  WARNING: Expected [{expected_row}][{expected_col}]!")
            return False

    return row, col


def main():
    print("=" * 70)
    print("MANHATTAN PROJECT - PHASE 1: IDENTITY VERIFICATION")
    print("=" * 70)
    print()

    if not QUBIPY_AVAILABLE:
        print("ERROR: QubiPy not available!")
        print("Run with: .venv_qubic/bin/python verify_all_identities.py")
        sys.exit(1)

    # Load matrix cartography
    print("[1/4] Loading matrix_cartography.json...")
    try:
        cartography = load_matrix_cartography()
        print(f"  Loaded {len(cartography)} position->key mappings")
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # Verify all nodes
    print()
    print("[2/4] Verifying Strategic Node Identities...")
    print("-" * 70)

    results = []
    passed = 0
    failed = 0
    derived_new = 0

    for node_name, node_data in KNOWN_IDENTITIES.items():
        anna_x, anna_y = node_data["coords"]
        expected_identity = node_data["identity"]

        print(f"\n{node_name}:")
        print(f"  Anna Coordinates: ({anna_x}, {anna_y})")

        # Transform coordinates
        row, col = anna_to_matrix(anna_x, anna_y)
        print(f"  Matrix Position: [{row}][{col}]")

        # Look up private key using ANNA COORDINATES (not matrix position!)
        # matrix_cartography.json uses "anna_x,anna_y" as keys
        key_lookup = f"{anna_x},{anna_y}"
        if key_lookup not in cartography:
            # Try alternative format (row,col)
            key_lookup_alt = f"{row},{col}"
            if key_lookup_alt in cartography:
                key_lookup = key_lookup_alt
                print(f"  Note: Using matrix format [{row}][{col}] instead of Anna format")
            else:
                print(f"  ERROR: Position {key_lookup} not in cartography!")
                results.append({
                    "node": node_name,
                    "status": "KEY_NOT_FOUND",
                    "coords": (anna_x, anna_y),
                    "matrix": (row, col)
                })
                failed += 1
                continue

        privkey_hex = cartography[key_lookup]
        print(f"  Cartography Key: {key_lookup}")
        print(f"  Private Key: {privkey_hex[:16]}...{privkey_hex[-8:]}")

        # Derive identity
        derived_identity = derive_identity_from_privkey(privkey_hex)
        print(f"  Derived Identity: {derived_identity}")

        # Compare
        if expected_identity is None:
            print(f"  Status: NEW DERIVATION (no expected value)")
            results.append({
                "node": node_name,
                "status": "DERIVED_NEW",
                "coords": (anna_x, anna_y),
                "matrix": (row, col),
                "identity": derived_identity,
                "privkey": privkey_hex
            })
            derived_new += 1
        elif derived_identity == expected_identity:
            print(f"  Status: MATCH")
            results.append({
                "node": node_name,
                "status": "MATCH",
                "coords": (anna_x, anna_y),
                "matrix": (row, col),
                "identity": derived_identity
            })
            passed += 1
        else:
            print(f"  Expected: {expected_identity}")
            print(f"  Status: MISMATCH!")
            results.append({
                "node": node_name,
                "status": "MISMATCH",
                "coords": (anna_x, anna_y),
                "matrix": (row, col),
                "derived": derived_identity,
                "expected": expected_identity
            })
            failed += 1

    # Summary
    print()
    print("=" * 70)
    print("[3/4] VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"  Total Nodes:    {len(KNOWN_IDENTITIES)}")
    print(f"  Passed (MATCH): {passed}")
    print(f"  Failed:         {failed}")
    print(f"  New Derived:    {derived_new}")
    print()

    # Calculate pass rate
    total_verified = passed + failed
    if total_verified > 0:
        pass_rate = (passed / total_verified) * 100
        print(f"  Pass Rate: {passed}/{total_verified} = {pass_rate:.1f}%")

    # Output detailed results
    print()
    print("[4/4] DETAILED RESULTS TABLE")
    print("-" * 70)
    print(f"{'Node':<12} {'Anna Coords':<12} {'Matrix':<12} {'Status':<15}")
    print("-" * 70)

    for r in results:
        anna_str = f"({r['coords'][0]}, {r['coords'][1]})"
        matrix_str = f"[{r['matrix'][0]}][{r['matrix'][1]}]"
        status_icon = "" if r['status'] == 'MATCH' else "" if r['status'] == 'DERIVED_NEW' else ""
        print(f"{r['node']:<12} {anna_str:<12} {matrix_str:<12} {status_icon} {r['status']:<15}")

    # Save results
    output_path = Path(__file__).parent / "IDENTITY_VERIFICATION_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump({
            "summary": {
                "total": len(KNOWN_IDENTITIES),
                "passed": passed,
                "failed": failed,
                "derived_new": derived_new,
                "pass_rate": f"{passed}/{total_verified}" if total_verified > 0 else "N/A"
            },
            "results": results,
            "all_verified_identities": {
                r["node"]: r.get("identity", r.get("derived"))
                for r in results
                if r["status"] in ["MATCH", "DERIVED_NEW"]
            }
        }, f, indent=2)
    print()
    print(f"Results saved to: {output_path}")

    # Final verdict
    print()
    print("=" * 70)
    if failed == 0:
        print("PHASE 1 RESULT: PASS - All identities verified!")
        print("Ready for Phase 2: RPC Connectivity Test")
        return 0
    else:
        print(f"PHASE 1 RESULT: FAIL - {failed} identity mismatches!")
        print("DO NOT PROCEED until all identities are verified.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
