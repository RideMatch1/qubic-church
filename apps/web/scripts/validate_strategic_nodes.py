#!/usr/bin/env python3
"""
MANHATTAN PROJECT - Phase 3: Strategic Node Validation
========================================================

This script validates ALL strategic node matrix values by:
1. Using the CORRECT coordinate transformation formula
2. Looking up values in anna-matrix.json
3. Comparing with documented expected values
4. Verifying coordinate system consistency

Author: qubic-academic-docs
Date: 2026-01-16
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from anna_matrix_utils import (
    anna_to_matrix,
    matrix_to_anna,
    load_anna_matrix,
    lookup_anna,
    STRATEGIC_NODES
)


# Expected matrix values for each strategic node
# These are documented values that we need to verify
EXPECTED_VALUES = {
    "CORE": {"coords": (6, 33), "expected_value": -93, "description": "Central processor"},
    "VOID": {"coords": (0, 0), "expected_value": -40, "description": "Origin/null state"},
    "MEMORY": {"coords": (21, 21), "expected_value": -50, "description": "Memory storage"},
    "GUARDIAN": {"coords": (19, 18), "expected_value": 36, "description": "Security/protection"},
    "DATE": {"coords": (3, 3), "expected_value": -122, "description": "Temporal reference"},
    "ENTRY": {"coords": (45, 92), "expected_value": 106, "description": "Entry portal"},
    "EXIT": {"coords": (82, 39), "expected_value": -75, "description": "Exit portal"},
    "VISION": {"coords": (64, 64), "expected_value": None, "description": "Vision/perception (value unknown)"},
    "ORACLE": {"coords": (11, 110), "expected_value": None, "description": "Oracle/prediction (value unknown)"},
    "ROOT_ALPHA": {"coords": (13, 71), "expected_value": None, "description": "Primary root (value unknown)"},
    "ROOT_BETA": {"coords": (18, 110), "expected_value": None, "description": "Secondary root (value unknown)"},
}

# Known verified coordinate-value pairs from Twitter/Batch8 validation
VERIFICATION_SET = [
    # Core verified values
    {"anna": (6, 33), "expected": -93, "source": "Twitter verified - CORE"},
    {"anna": (0, 0), "expected": -40, "source": "Twitter verified - VOID"},
    {"anna": (0, 7), "expected": -94, "source": "Twitter verified"},
    {"anna": (0, 1), "expected": -38, "source": "Twitter verified"},
    {"anna": (-27, 3), "expected": -110, "source": "Twitter verified - CFB signature"},
    {"anna": (-27, 0), "expected": -102, "source": "Twitter verified"},
    {"anna": (-1, 0), "expected": 69, "source": "Twitter verified"},
    {"anna": (0, -1), "expected": -70, "source": "Twitter verified"},
    {"anna": (-60, 10), "expected": 90, "source": "Twitter verified"},
    {"anna": (2, 2), "expected": -123, "source": "Twitter verified"},
    {"anna": (7, 0), "expected": -102, "source": "Twitter verified"},
]


def validate_coordinate_transformation():
    """Validate the coordinate transformation formula."""
    print("\n" + "=" * 60)
    print("COORDINATE TRANSFORMATION VALIDATION")
    print("=" * 60)
    print()
    print("Formula:")
    print("  col = (X + 64) % 128")
    print("  row = (63 - Y) % 128")
    print()

    # Test specific examples
    test_cases = [
        ((6, 33), (30, 70), "CORE"),
        ((0, 0), (63, 64), "VOID"),
        ((45, 92), (99, 109), "ENTRY"),
        ((82, 39), (24, 18), "EXIT"),
        ((64, 64), (127, 0), "VISION"),
    ]

    all_pass = True
    print("Test Cases:")
    print("-" * 60)
    print(f"{'Anna (X,Y)':<15} {'Expected [r][c]':<18} {'Actual [r][c]':<15} {'Status':<10}")
    print("-" * 60)

    for anna_coords, expected_matrix, name in test_cases:
        actual_row, actual_col = anna_to_matrix(*anna_coords)
        expected_row, expected_col = expected_matrix

        match = (actual_row == expected_row and actual_col == expected_col)
        status = "PASS" if match else "FAIL"
        if not match:
            all_pass = False

        anna_str = f"({anna_coords[0]}, {anna_coords[1]})"
        exp_str = f"[{expected_row}][{expected_col}]"
        act_str = f"[{actual_row}][{actual_col}]"
        print(f"{anna_str:<15} {exp_str:<18} {act_str:<15} {status:<10} {name}")

    print("-" * 60)
    print(f"Transformation Validation: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


def validate_matrix_values(matrix):
    """Validate matrix values for strategic nodes."""
    print("\n" + "=" * 60)
    print("STRATEGIC NODE VALUE VALIDATION")
    print("=" * 60)
    print()

    results = []
    passed = 0
    failed = 0
    unknown = 0

    print(f"{'Node':<12} {'Anna (X,Y)':<12} {'Matrix [r][c]':<15} {'Value':<8} {'Expected':<10} {'Status':<10}")
    print("-" * 75)

    for name, data in EXPECTED_VALUES.items():
        anna_x, anna_y = data["coords"]
        expected = data["expected_value"]

        row, col = anna_to_matrix(anna_x, anna_y)
        actual_value = matrix[row][col]

        if expected is None:
            status = "UNKNOWN"
            unknown += 1
        elif actual_value == expected:
            status = "MATCH"
            passed += 1
        else:
            status = "MISMATCH"
            failed += 1

        anna_str = f"({anna_x}, {anna_y})"
        matrix_str = f"[{row}][{col}]"
        exp_str = str(expected) if expected is not None else "?"

        icon = "✓" if status == "MATCH" else "?" if status == "UNKNOWN" else "✗"
        print(f"{name:<12} {anna_str:<12} {matrix_str:<15} {actual_value:<8} {exp_str:<10} {icon} {status}")

        results.append({
            "node": name,
            "anna_coords": (anna_x, anna_y),
            "matrix_pos": (row, col),
            "actual_value": actual_value,
            "expected_value": expected,
            "status": status
        })

    print("-" * 75)
    print(f"Passed: {passed}  |  Failed: {failed}  |  Unknown: {unknown}")

    return results, passed, failed, unknown


def validate_verification_set(matrix):
    """Validate the core verification set (Twitter/Batch8)."""
    print("\n" + "=" * 60)
    print("CORE VERIFICATION SET (Twitter/Batch8)")
    print("=" * 60)
    print()

    all_pass = True
    passed = 0

    for v in VERIFICATION_SET:
        anna_x, anna_y = v["anna"]
        expected = v["expected"]

        actual = lookup_anna(matrix, anna_x, anna_y)
        match = (actual == expected)

        if match:
            passed += 1
        else:
            all_pass = False
            print(f"MISMATCH: Anna({anna_x}, {anna_y}) = {actual}, expected {expected} ({v['source']})")

    print(f"Verification: {passed}/{len(VERIFICATION_SET)} = {passed/len(VERIFICATION_SET)*100:.1f}%")
    return all_pass, passed


def validate_round_trip():
    """Validate anna_to_matrix and matrix_to_anna are inverses."""
    print("\n" + "=" * 60)
    print("ROUND-TRIP TRANSFORMATION VALIDATION")
    print("=" * 60)
    print()

    all_pass = True
    test_count = 0

    # Test all positions within standard range
    for x in range(-64, 64, 16):  # Sample every 16th
        for y in range(-64, 64, 16):
            row, col = anna_to_matrix(x, y)
            recovered_x, recovered_y = matrix_to_anna(row, col)

            # Handle wrapping for extended coordinates
            if x != recovered_x or y != recovered_y:
                all_pass = False
                print(f"MISMATCH: ({x}, {y}) -> [{row}][{col}] -> ({recovered_x}, {recovered_y})")

            test_count += 1

    print(f"Tested {test_count} coordinate pairs")
    print(f"Round-trip validation: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


def main():
    print("=" * 60)
    print("MANHATTAN PROJECT - PHASE 3: STRATEGIC NODE VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load matrix
    print("\n[1/5] Loading Anna Matrix...")
    try:
        matrix = load_anna_matrix()
        print(f"  Matrix loaded: {len(matrix)}x{len(matrix[0])}")
    except Exception as e:
        print(f"  ERROR: {e}")
        return 1

    # Validate transformations
    print("\n[2/5] Validating Coordinate Transformations...")
    transform_ok = validate_coordinate_transformation()

    # Validate round-trip
    print("\n[3/5] Validating Round-Trip Transformations...")
    roundtrip_ok = validate_round_trip()

    # Validate verification set
    print("\n[4/5] Validating Core Verification Set...")
    verify_ok, verify_count = validate_verification_set(matrix)

    # Validate strategic nodes
    print("\n[5/5] Validating Strategic Node Values...")
    node_results, passed, failed, unknown = validate_matrix_values(matrix)

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Coordinate Transformation: {'PASS' if transform_ok else 'FAIL'}")
    print(f"  Round-Trip Validation:     {'PASS' if roundtrip_ok else 'FAIL'}")
    print(f"  Verification Set:          {verify_count}/{len(VERIFICATION_SET)} = {'PASS' if verify_ok else 'FAIL'}")
    print(f"  Strategic Nodes:           {passed} matched, {failed} failed, {unknown} unknown")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "validations": {
            "coordinate_transformation": transform_ok,
            "round_trip": roundtrip_ok,
            "verification_set": {"passed": verify_ok, "count": f"{verify_count}/{len(VERIFICATION_SET)}"},
            "strategic_nodes": {"passed": passed, "failed": failed, "unknown": unknown}
        },
        "node_results": node_results
    }

    output_path = Path(__file__).parent / "STRATEGIC_NODE_VALIDATION.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Final verdict
    print("\n" + "=" * 60)
    critical_pass = transform_ok and roundtrip_ok and verify_ok and failed == 0

    if critical_pass:
        print("PHASE 3 RESULT: PASS - All validations successful!")
        print("Ready for Phase 4: Transaction Builder Test")
        return 0
    else:
        print("PHASE 3 RESULT: FAIL - Validation issues detected!")
        if not transform_ok:
            print("  - Coordinate transformation failed")
        if not roundtrip_ok:
            print("  - Round-trip transformation failed")
        if not verify_ok:
            print("  - Core verification set failed")
        if failed > 0:
            print(f"  - {failed} strategic node value mismatches")
        return 1


if __name__ == "__main__":
    sys.exit(main())
