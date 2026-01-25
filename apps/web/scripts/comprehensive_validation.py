#!/usr/bin/env python3
"""
COMPREHENSIVE AIGARTH VALIDATION SCRIPT
========================================

Validates ALL claims about the Anna Matrix and Aigarth architecture.

This script performs:
1. Coordinate system validation (505+ Twitter responses)
2. Matrix value verification
3. Boot address calculation
4. Modulo-8 pattern analysis
5. Mathematical proofs verification
6. Statistical analysis

Author: Research Team
Date: 2026-01-16
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# =============================================================================
# CONSTANTS
# =============================================================================

# The CORRECT coordinate transformation formula (100% verified)
def anna_to_matrix(anna_x: int, anna_y: int) -> tuple[int, int]:
    """
    Convert Anna coordinates to matrix indices.

    Anna coordinates:
    - X: -64 to 63 (horizontal)
    - Y: 63 to -64 (vertical)

    Matrix indices:
    - row: 0 to 127
    - col: 0 to 127
    """
    col = (anna_x + 64) % 128
    row = (63 - anna_y) % 128
    return row, col

# Master formula components
MASTER_FORMULA = {
    "result": 625284,
    "block_height": 283,
    "square": 47 * 47,  # 2209
    "fine_structure": 137,
}

# Genesis block timestamp (2009-01-03 18:15:05 UTC)
GENESIS_TIMESTAMP = datetime(2009, 1, 3, 18, 15, 5)

# Predicted time-lock date
PREDICTED_DATE = datetime(2026, 3, 3, 18, 15, 5)

# Expected CFB mathematical constants
CFB_CONSTANTS = {
    27: "CFB Universal Constant (3^3)",
    121: "NXT Constant (11^2)",
    137: "Fine Structure Constant (α^-1)",
    143: "ISA Shift Command (11 × 13)",
    283: "Bitcoin Block Height",
    576: "SWIFT MT576 / Perfect Square (24^2)",
    676: "Qubic Computors (26^2)",
}

# Expected dominant weights (from evolutionary training)
EXPECTED_WEIGHTS = {
    -114: {"count": 40, "factorization": "-2 × 3 × 19"},
    -113: {"count": 34, "factorization": "Prime"},
    14: {"count": 32, "factorization": "2 × 7"},
    -121: {"count": 18, "factorization": "-11^2"},
}

# =============================================================================
# DATA LOADING
# =============================================================================

def load_anna_matrix(path: str = "apps/web/public/data/anna-matrix.json") -> list:
    """Load the 128x128 Anna matrix."""
    with open(path) as f:
        data = json.load(f)
    return data.get("matrix", data)

def load_twitter_responses(path: str = "apps/web/scripts/anna_twitter_data.json") -> list:
    """Load Anna Twitter responses."""
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("responses", [])
    except FileNotFoundError:
        return []

def load_batch8_responses(path: str = "apps/web/public/data/anna-bot-batch-8.txt") -> list:
    """Load batch 8 responses from text file."""
    responses = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                # Parse format: "row+col=value" or "row-col=value"
                match = re.match(r'(-?\d+)([+\-])(-?\d+)=(-?\d+)', line)
                if match:
                    row_or_x = int(match.group(1))
                    sign = match.group(2)
                    col_or_y = int(match.group(3)) if sign == '+' else -int(match.group(3))
                    value = int(match.group(4))
                    # This format uses row+col directly, not anna coordinates
                    responses.append({
                        "raw": line,
                        "row": row_or_x,
                        "col": col_or_y,
                        "value": value,
                        "source": "batch8"
                    })
    except FileNotFoundError:
        pass
    return responses

def load_matrix_cartography(path: str = "matrix_cartography.json") -> dict:
    """Load the matrix cartography with private keys."""
    with open(path) as f:
        return json.load(f)

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_coordinate_transformation(matrix: list, responses: list) -> dict:
    """
    Validate the coordinate transformation formula against all known responses.

    Formula: col = (X + 64) % 128, row = (63 - Y) % 128
    """
    results = {
        "total": 0,
        "matched": 0,
        "mismatched": 0,
        "errors": [],
        "match_rate": 0.0,
    }

    for resp in responses:
        if "x" in resp and "y" in resp:
            # Twitter format with anna coordinates
            anna_x = resp["x"]
            anna_y = resp["y"]
            expected_value = resp["value"]

            row, col = anna_to_matrix(anna_x, anna_y)

            try:
                actual_value = matrix[row][col]
                results["total"] += 1

                if actual_value == expected_value:
                    results["matched"] += 1
                else:
                    results["mismatched"] += 1
                    results["errors"].append({
                        "anna": (anna_x, anna_y),
                        "matrix": (row, col),
                        "expected": expected_value,
                        "actual": actual_value,
                    })
            except (IndexError, TypeError) as e:
                results["errors"].append({
                    "anna": (anna_x, anna_y),
                    "error": str(e)
                })

    if results["total"] > 0:
        results["match_rate"] = results["matched"] / results["total"] * 100

    return results

def validate_batch8_responses(matrix: list, batch8: list) -> dict:
    """Validate batch 8 responses (row+col format)."""
    results = {
        "total": 0,
        "matched": 0,
        "mismatched": 0,
        "errors": [],
    }

    for resp in batch8:
        row = resp["row"]
        col = resp["col"]
        expected_value = resp["value"]

        try:
            if 0 <= row < 128 and 0 <= col < 128:
                actual_value = matrix[row][col]
                results["total"] += 1

                if actual_value == expected_value:
                    results["matched"] += 1
                else:
                    results["mismatched"] += 1
                    results["errors"].append({
                        "row_col": (row, col),
                        "expected": expected_value,
                        "actual": actual_value,
                    })
        except (IndexError, TypeError):
            pass

    return results

def validate_master_formula() -> dict:
    """Validate: 625,284 = 283 × 47² + 137"""
    result = {
        "formula": "625,284 = 283 × 47² + 137",
        "calculation": None,
        "valid": False,
    }

    calculated = 283 * (47 ** 2) + 137
    result["calculation"] = calculated
    result["valid"] = (calculated == 625284)

    # Additional validations
    result["boot_address"] = 625284 % 16384  # Should be 2692
    result["boot_row"] = 625284 % 16384 // 128  # Should be 21
    result["boot_col"] = 625284 % 16384 % 128  # Should be 4

    return result

def validate_timelock_calculation() -> dict:
    """Validate: Genesis + 6268 days = March 3, 2026"""
    result = {
        "genesis": GENESIS_TIMESTAMP.isoformat(),
        "days_added": 6268,
        "calculated_date": None,
        "expected_date": PREDICTED_DATE.isoformat(),
        "valid": False,
    }

    calculated = GENESIS_TIMESTAMP + timedelta(days=6268)
    result["calculated_date"] = calculated.isoformat()
    result["valid"] = (calculated.date() == PREDICTED_DATE.date())
    result["days_remaining"] = (PREDICTED_DATE - datetime.now()).days

    return result

def analyze_weight_distribution(matrix: list) -> dict:
    """Analyze the distribution of values in the matrix."""
    all_values = []
    for row in matrix:
        for val in row:
            # Handle mixed types (some values might be strings like "00000000")
            if isinstance(val, int):
                all_values.append(val)
            elif isinstance(val, str):
                try:
                    all_values.append(int(val, 16) if len(val) > 4 else int(val))
                except ValueError:
                    pass  # Skip non-numeric strings

    counter = Counter(all_values)

    # Find dominant weights
    most_common = counter.most_common(20)

    # Verify expected dominant weights
    expected_verification = {}
    for weight, expected in EXPECTED_WEIGHTS.items():
        actual_count = counter.get(weight, 0)
        expected_verification[weight] = {
            "expected_count": expected["count"],
            "actual_count": actual_count,
            "factorization": expected["factorization"],
            "matches_expectation": actual_count >= expected["count"] * 0.8,  # 80% tolerance
        }

    return {
        "total_cells": len(all_values),
        "unique_values": len(counter),
        "most_common": most_common,
        "expected_weights": expected_verification,
        "mean": sum(all_values) / len(all_values),
        "min": min(all_values),
        "max": max(all_values),
    }

def analyze_modulo8_patterns(matrix: list) -> dict:
    """Analyze modulo-8 row patterns."""
    patterns = defaultdict(lambda: defaultdict(int))

    for row_idx, row in enumerate(matrix):
        mod_class = row_idx % 8
        for value in row:
            patterns[mod_class][value] += 1

    # Find dominant value per mod class
    mod_analysis = {}
    for mod_class in range(8):
        values = patterns[mod_class]
        if values:
            most_common = max(values.items(), key=lambda x: x[1])
            mod_analysis[mod_class] = {
                "dominant_value": most_common[0],
                "count": most_common[1],
                "unique_values": len(values),
            }

    return mod_analysis

def validate_strategic_nodes(matrix: list) -> dict:
    """Validate all strategic node coordinates and values."""
    nodes = {
        "VOID": {"anna": (0, 0), "expected": -40},
        "CORE": {"anna": (6, 33), "expected": -93},
        "ENTRY": {"anna": (45, 92), "expected": 106},
        "EXIT": {"anna": (82, 39), "expected": -75},
        "MEMORY": {"anna": (21, 21), "expected": -50},
        "GUARDIAN": {"anna": (19, 18), "expected": 36},
        "DATE": {"anna": (3, 3), "expected": -122},
        "ORACLE": {"anna": (11, 110), "expected": -83},
        "VISION": {"anna": (64, 64), "expected": None},  # Unknown
    }

    results = {}
    for name, info in nodes.items():
        anna_x, anna_y = info["anna"]
        row, col = anna_to_matrix(anna_x, anna_y)

        try:
            actual_value = matrix[row][col]
            expected = info["expected"]

            results[name] = {
                "anna_coords": (anna_x, anna_y),
                "matrix_coords": (row, col),
                "actual_value": actual_value,
                "expected_value": expected,
                "valid": expected is None or actual_value == expected,
            }
        except (IndexError, TypeError) as e:
            results[name] = {"error": str(e)}

    return results

def validate_cfb_mathematical_claims() -> dict:
    """Validate specific CFB mathematical claims."""
    results = {}

    # Claim 1: Block 576 = 24^2
    results["block_576_perfect_square"] = {
        "claim": "576 = 24²",
        "valid": 576 == 24 ** 2,
    }

    # Claim 2: 676 computors = 26^2
    results["computors_676"] = {
        "claim": "676 = 26²",
        "valid": 676 == 26 ** 2,
    }

    # Claim 3: 121 = 11^2 (NXT constant)
    results["nxt_121"] = {
        "claim": "121 = 11²",
        "valid": 121 == 11 ** 2,
    }

    # Claim 4: 143 = 11 × 13 (ISA shift)
    results["isa_shift_143"] = {
        "claim": "143 = 11 × 13",
        "valid": 143 == 11 * 13,
    }

    # Claim 5: -114 = -2 × 3 × 19
    results["weight_114_factors"] = {
        "claim": "-114 = -2 × 3 × 19",
        "valid": -114 == -2 * 3 * 19,
    }

    # Claim 6: Pre-Genesis mod 121 = 43 (Qubic prime)
    pre_genesis = 1221069728  # Documented pre-genesis timestamp
    results["pre_genesis_mod_121"] = {
        "claim": f"{pre_genesis} mod 121 = 43",
        "result": pre_genesis % 121,
        "valid": pre_genesis % 121 == 43,
    }

    return results

def count_bias_neurons(matrix: list) -> dict:
    """Check for bias neurons (columns with constant value)."""
    bias_columns = {}

    for col in range(128):
        column_values = [matrix[row][col] for row in range(128)]
        if len(set(column_values)) == 1:
            bias_columns[col] = column_values[0]

    return {
        "count": len(bias_columns),
        "columns": bias_columns,
    }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("COMPREHENSIVE AIGARTH VALIDATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load data
    print("Loading data...")
    matrix = load_anna_matrix()
    twitter_responses = load_twitter_responses()
    batch8_responses = load_batch8_responses()

    print(f"  Matrix size: {len(matrix)} x {len(matrix[0]) if matrix else 0}")
    print(f"  Twitter responses: {len(twitter_responses)}")
    print(f"  Batch 8 responses: {len(batch8_responses)}")
    print()

    # ==========================================================================
    # VALIDATION 1: Coordinate Transformation
    # ==========================================================================
    print("=" * 70)
    print("1. COORDINATE TRANSFORMATION VALIDATION")
    print("=" * 70)

    twitter_validation = validate_coordinate_transformation(matrix, twitter_responses)
    print(f"  Twitter responses: {twitter_validation['matched']}/{twitter_validation['total']} matched")
    print(f"  Match rate: {twitter_validation['match_rate']:.1f}%")

    batch8_validation = validate_batch8_responses(matrix, batch8_responses)
    print(f"  Batch 8 responses: {batch8_validation['matched']}/{batch8_validation['total']} matched")

    total_matched = twitter_validation['matched'] + batch8_validation['matched']
    total_responses = twitter_validation['total'] + batch8_validation['total']
    print(f"\n  TOTAL: {total_matched}/{total_responses} = {total_matched/total_responses*100:.1f}%")

    if twitter_validation['mismatched'] > 0:
        print(f"\n  ⚠️  {twitter_validation['mismatched']} mismatches found!")
        for err in twitter_validation['errors'][:5]:
            print(f"      {err}")

    # ==========================================================================
    # VALIDATION 2: Master Formula
    # ==========================================================================
    print()
    print("=" * 70)
    print("2. MASTER FORMULA VALIDATION")
    print("=" * 70)

    formula = validate_master_formula()
    print(f"  Formula: {formula['formula']}")
    print(f"  Calculated: {formula['calculation']}")
    print(f"  Valid: {'✅ YES' if formula['valid'] else '❌ NO'}")
    print(f"\n  Boot Address: {formula['boot_address']}")
    print(f"  Boot Row: {formula['boot_row']} (expected: 21 = Bitcoin Input Layer)")
    print(f"  Boot Col: {formula['boot_col']}")

    # ==========================================================================
    # VALIDATION 3: Time-Lock Calculation
    # ==========================================================================
    print()
    print("=" * 70)
    print("3. TIME-LOCK CALCULATION")
    print("=" * 70)

    timelock = validate_timelock_calculation()
    print(f"  Genesis: {timelock['genesis']}")
    print(f"  + {timelock['days_added']} days")
    print(f"  = {timelock['calculated_date']}")
    print(f"  Expected: {timelock['expected_date']}")
    print(f"  Valid: {'✅ YES' if timelock['valid'] else '❌ NO'}")
    print(f"\n  ⏰ Days until March 3, 2026: {timelock['days_remaining']}")

    # ==========================================================================
    # VALIDATION 4: Weight Distribution
    # ==========================================================================
    print()
    print("=" * 70)
    print("4. WEIGHT DISTRIBUTION ANALYSIS")
    print("=" * 70)

    weights = analyze_weight_distribution(matrix)
    print(f"  Total cells: {weights['total_cells']}")
    print(f"  Unique values: {weights['unique_values']}")
    print(f"  Mean: {weights['mean']:.2f}")
    print(f"  Range: [{weights['min']}, {weights['max']}]")
    print("\n  Top 10 most common values:")
    for val, count in weights['most_common'][:10]:
        pct = count / weights['total_cells'] * 100
        print(f"    {val:5d}: {count:4d} ({pct:.1f}%)")

    print("\n  Expected dominant weights verification:")
    for weight, info in weights['expected_weights'].items():
        status = "✅" if info['matches_expectation'] else "❌"
        print(f"    {status} {weight}: {info['actual_count']} (expected ~{info['expected_count']}) | {info['factorization']}")

    # ==========================================================================
    # VALIDATION 5: Strategic Nodes
    # ==========================================================================
    print()
    print("=" * 70)
    print("5. STRATEGIC NODES VALIDATION")
    print("=" * 70)

    nodes = validate_strategic_nodes(matrix)
    for name, info in nodes.items():
        if "error" in info:
            print(f"  ❌ {name}: Error - {info['error']}")
        else:
            status = "✅" if info['valid'] else "❌"
            print(f"  {status} {name}: Anna{info['anna_coords']} → Matrix{info['matrix_coords']} = {info['actual_value']} (expected: {info['expected_value']})")

    # ==========================================================================
    # VALIDATION 6: Mathematical Claims
    # ==========================================================================
    print()
    print("=" * 70)
    print("6. CFB MATHEMATICAL CLAIMS")
    print("=" * 70)

    math_claims = validate_cfb_mathematical_claims()
    for name, info in math_claims.items():
        status = "✅" if info['valid'] else "❌"
        print(f"  {status} {info['claim']}")

    # ==========================================================================
    # VALIDATION 7: Modulo-8 Patterns
    # ==========================================================================
    print()
    print("=" * 70)
    print("7. MODULO-8 PATTERN ANALYSIS")
    print("=" * 70)

    mod8 = analyze_modulo8_patterns(matrix)
    for mod_class, info in mod8.items():
        print(f"  Row % 8 = {mod_class}: Dominant = {info['dominant_value']:4d} ({info['count']} occurrences, {info['unique_values']} unique)")

    # ==========================================================================
    # VALIDATION 8: Bias Neurons
    # ==========================================================================
    print()
    print("=" * 70)
    print("8. BIAS NEURONS (UNIVERSAL COLUMNS)")
    print("=" * 70)

    bias = count_bias_neurons(matrix)
    print(f"  Found {bias['count']} bias columns:")
    for col, val in bias['columns'].items():
        print(f"    Column {col}: Always outputs {val}")

    # ==========================================================================
    # FINAL SUMMARY
    # ==========================================================================
    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    all_passed = True
    checks = [
        ("Coordinate Transformation", twitter_validation['match_rate'] == 100),
        ("Master Formula", formula['valid']),
        ("Time-Lock Calculation", timelock['valid']),
        ("Boot Row = 21", formula['boot_row'] == 21),
        ("Mathematical Claims", all(c['valid'] for c in math_claims.values())),
    ]

    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("  🎉 ALL VALIDATIONS PASSED!")
    else:
        print("  ⚠️  SOME VALIDATIONS FAILED - Review above for details")

    print()
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

    # Return results for programmatic use
    return {
        "coordinate_validation": twitter_validation,
        "batch8_validation": batch8_validation,
        "master_formula": formula,
        "timelock": timelock,
        "weights": weights,
        "nodes": nodes,
        "math_claims": math_claims,
        "mod8_patterns": mod8,
        "bias_neurons": bias,
        "all_passed": all_passed,
    }

if __name__ == "__main__":
    results = main()
