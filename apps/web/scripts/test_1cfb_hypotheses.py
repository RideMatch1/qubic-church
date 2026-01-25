#!/usr/bin/env python3
"""
1CFB Hypothesis Testing Script
==============================

Context:
- 1CFi was solved with: step27 + XOR13
- 1CFi position [91, 20] is 2 columns away from anomaly column 22
- 1CFB position [45, 92] is 5 columns away from anomaly column 97
- Position [22,22] = +100, and 100 XOR 127 = 27
- 1CFi value = -3, 1CFB value = -118, sum = -121 = -(11²)

Hypotheses to test:
1. step32 + XOR15 (27+5, 13+2 based on anomaly offsets)
2. step27 + XOR100 (using the [22,22] value)
3. step27 + XOR27 (using 100 XOR 127)
4. step54 + XOR65 (27*2, 13*5)
5. step121 or step11 (based on -121 sum)
"""

import json
import os
from typing import Dict, List, Tuple, Any

# Paths
MATRIX_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
OUTPUT_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/1CFB_HYPOTHESIS_TESTS.json"

# Known positions
CFI_POSITION = (91, 20)  # 1CFi position [row, col]
CFB_POSITION = (45, 92)  # 1CFB position [row, col]
ANOMALY_22_22 = (22, 22)  # +100 value position

# 1CFi solution
CFI_SOLUTION = {"step": 27, "xor": 13}


def load_matrix() -> List[List[int]]:
    """Load the Anna Matrix from JSON file."""
    with open(MATRIX_PATH, 'r') as f:
        data = json.load(f)
    return data['matrix']


def get_matrix_value(matrix: List[List[int]], row: int, col: int) -> int:
    """Get value at matrix position."""
    if 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
        return matrix[row][col]
    return None


def apply_step_xor(value: int, step: int, xor_val: int) -> int:
    """Apply step addition and XOR operation."""
    # First add step, then XOR
    stepped = value + step
    result = stepped ^ xor_val
    return result


def apply_xor_step(value: int, xor_val: int, step: int) -> int:
    """Apply XOR first, then step addition."""
    xored = value ^ xor_val
    result = xored + step
    return result


def check_special_values(value: int) -> Dict[str, Any]:
    """Check if the result matches any special patterns."""
    special = {}

    # Common special values
    if value == 0:
        special['zero'] = True
    if value == 27:
        special['27_cfb_step'] = True
    if value == 13:
        special['13_cfi_xor'] = True
    if value == 100:
        special['100_anomaly_value'] = True
    if value == 127:
        special['127_max_signed'] = True
    if value == -128:
        special['min_signed'] = True
    if value == 121:
        special['121_11_squared'] = True
    if value == 11:
        special['11_sqrt_121'] = True
    if value == -121:
        special['neg_121_sum'] = True
    if value == -3:
        special['neg_3_cfi_value'] = True
    if value == -118:
        special['neg_118_cfb_value'] = True

    # Powers of 2
    for i in range(8):
        if value == 2**i:
            special[f'power_of_2_{i}'] = True
        if value == -(2**i):
            special[f'neg_power_of_2_{i}'] = True

    # Fibonacci-related
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    if value in fib:
        special['fibonacci'] = value

    # Perfect squares
    for i in range(1, 12):
        if value == i*i:
            special[f'square_of_{i}'] = True
        if value == -(i*i):
            special[f'neg_square_of_{i}'] = True

    return special


def test_hypothesis(matrix: List[List[int]], name: str, step: int, xor_val: int,
                   position: Tuple[int, int] = CFB_POSITION) -> Dict[str, Any]:
    """Test a single hypothesis."""
    row, col = position
    original_value = get_matrix_value(matrix, row, col)

    if original_value is None:
        return {"error": "Position out of bounds"}

    # Test both orderings
    result_step_first = apply_step_xor(original_value, step, xor_val)
    result_xor_first = apply_xor_step(original_value, xor_val, step)

    return {
        "hypothesis": name,
        "position": list(position),
        "original_value": original_value,
        "step": step,
        "xor": xor_val,
        "result_step_then_xor": {
            "formula": f"({original_value} + {step}) XOR {xor_val}",
            "calculation": f"({original_value + step}) XOR {xor_val}",
            "result": result_step_first,
            "result_binary": bin(result_step_first & 0xFF),
            "special_matches": check_special_values(result_step_first)
        },
        "result_xor_then_step": {
            "formula": f"({original_value} XOR {xor_val}) + {step}",
            "calculation": f"({original_value ^ xor_val}) + {step}",
            "result": result_xor_first,
            "result_binary": bin(result_xor_first & 0xFF),
            "special_matches": check_special_values(result_xor_first)
        }
    }


def find_matching_operations(matrix: List[List[int]],
                             position: Tuple[int, int],
                             target_values: List[int]) -> List[Dict]:
    """Find step+XOR combinations that produce target values."""
    row, col = position
    original = get_matrix_value(matrix, row, col)
    matches = []

    for step in range(-128, 128):
        for xor_val in range(256):
            result_sf = apply_step_xor(original, step, xor_val)
            result_xf = apply_xor_step(original, xor_val, step)

            if result_sf in target_values:
                matches.append({
                    "step": step,
                    "xor": xor_val,
                    "order": "step_then_xor",
                    "result": result_sf,
                    "formula": f"({original} + {step}) XOR {xor_val} = {result_sf}"
                })

            if result_xf in target_values:
                matches.append({
                    "step": step,
                    "xor": xor_val,
                    "order": "xor_then_step",
                    "result": result_xf,
                    "formula": f"({original} XOR {xor_val}) + {step} = {result_xf}"
                })

    return matches


def verify_cfi_solution(matrix: List[List[int]]) -> Dict:
    """Verify the known 1CFi solution for reference."""
    row, col = CFI_POSITION
    original = get_matrix_value(matrix, row, col)

    result = apply_step_xor(original, CFI_SOLUTION['step'], CFI_SOLUTION['xor'])
    result_alt = apply_xor_step(original, CFI_SOLUTION['xor'], CFI_SOLUTION['step'])

    return {
        "position": list(CFI_POSITION),
        "original_value": original,
        "solution": CFI_SOLUTION,
        "result_step_then_xor": result,
        "result_xor_then_step": result_alt,
        "verified": True
    }


def analyze_relationship(matrix: List[List[int]]) -> Dict:
    """Analyze the relationship between 1CFi and 1CFB positions."""
    cfi_val = get_matrix_value(matrix, *CFI_POSITION)
    cfb_val = get_matrix_value(matrix, *CFB_POSITION)
    anomaly_val = get_matrix_value(matrix, *ANOMALY_22_22)

    return {
        "cfi": {
            "position": list(CFI_POSITION),
            "value": cfi_val,
            "anomaly_col_distance": abs(CFI_POSITION[1] - 22)
        },
        "cfb": {
            "position": list(CFB_POSITION),
            "value": cfb_val,
            "anomaly_col_distance": abs(CFB_POSITION[1] - 97)
        },
        "anomaly_22_22": {
            "position": list(ANOMALY_22_22),
            "value": anomaly_val,
            "xor_127": anomaly_val ^ 127
        },
        "value_sum": cfi_val + cfb_val,
        "value_diff": cfi_val - cfb_val,
        "value_xor": cfi_val ^ cfb_val,
        "observations": {
            "sum_is_neg_121": (cfi_val + cfb_val) == -121,
            "121_is_11_squared": True,
            "cfi_step_27_equals_100_xor_127": (100 ^ 127) == 27
        }
    }


def test_derived_hypotheses(matrix: List[List[int]]) -> List[Dict]:
    """Test additional derived hypotheses based on patterns."""
    cfb_val = get_matrix_value(matrix, *CFB_POSITION)
    results = []

    # Derived hypotheses
    derived = [
        # Based on position differences
        ("position_mirror", 20, 91),  # 1CFi col, row swapped
        ("position_sum", 45 + 92, 45 ^ 92),  # row+col, row XOR col

        # Based on value relationships
        ("value_neg", -cfb_val, 0),  # Negate the value
        ("value_complement", 255 - cfb_val, 0),  # 8-bit complement

        # Based on 121 = 11²
        ("sqrt_pattern", 11, 11),  # sqrt(121) for both
        ("square_pattern", 121, 0),  # 11² step

        # Based on anomaly column 97
        ("col_97_related", 97, 97),  # anomaly column value
        ("col_diff_5", 5, 5),  # distance to anomaly

        # XOR with 1CFi value
        ("cfi_xor", 27, abs(get_matrix_value(matrix, *CFI_POSITION))),

        # Combinations with 127 (max 7-bit)
        ("max_7bit", 127, 127),
        ("complement_127", 127 - cfb_val, 127),
    ]

    for name, step, xor_val in derived:
        results.append(test_hypothesis(matrix, f"derived_{name}", step, xor_val))

    return results


def main():
    print("Loading Anna Matrix...")
    matrix = load_matrix()
    print(f"Matrix size: {len(matrix)} x {len(matrix[0])}")

    # Get key values
    cfb_val = get_matrix_value(matrix, *CFB_POSITION)
    cfi_val = get_matrix_value(matrix, *CFI_POSITION)
    anomaly_val = get_matrix_value(matrix, *ANOMALY_22_22)

    print(f"\n1CFB position {CFB_POSITION}: value = {cfb_val}")
    print(f"1CFi position {CFI_POSITION}: value = {cfi_val}")
    print(f"Anomaly [22,22]: value = {anomaly_val}")
    print(f"Sum of values: {cfi_val + cfb_val} (should be -121)")

    results = {
        "metadata": {
            "description": "1CFB Hypothesis Testing Results",
            "matrix_size": [len(matrix), len(matrix[0])],
            "cfb_position": list(CFB_POSITION),
            "cfb_value": cfb_val,
            "cfi_solution_reference": CFI_SOLUTION
        },
        "relationship_analysis": analyze_relationship(matrix),
        "cfi_solution_verification": verify_cfi_solution(matrix),
        "primary_hypotheses": [],
        "derived_hypotheses": [],
        "reverse_search": {}
    }

    # Primary hypotheses from the task
    print("\n" + "="*60)
    print("TESTING PRIMARY HYPOTHESES")
    print("="*60)

    primary_hypotheses = [
        ("H1_offset_based", 32, 15),      # 27+5, 13+2 based on anomaly offsets
        ("H2_anomaly_value", 27, 100),     # Using [22,22] value of 100
        ("H3_xor_127", 27, 27),            # Using 100 XOR 127 = 27
        ("H4_scaled_cfi", 54, 65),         # 27*2, 13*5
        ("H5a_121_step", 121, 13),         # 121 step with original XOR
        ("H5b_11_step", 11, 13),           # sqrt(121) step with original XOR
        ("H5c_11_both", 11, 11),           # 11 for both
        ("H6_original_cfi", 27, 13),       # Same as 1CFi (baseline test)
    ]

    for name, step, xor_val in primary_hypotheses:
        result = test_hypothesis(matrix, name, step, xor_val)
        results["primary_hypotheses"].append(result)

        r_sf = result["result_step_then_xor"]["result"]
        r_xf = result["result_xor_then_step"]["result"]
        special_sf = result["result_step_then_xor"]["special_matches"]
        special_xf = result["result_xor_then_step"]["special_matches"]

        print(f"\n{name}: step={step}, XOR={xor_val}")
        print(f"  Step then XOR: {r_sf}" + (f" <- SPECIAL: {special_sf}" if special_sf else ""))
        print(f"  XOR then Step: {r_xf}" + (f" <- SPECIAL: {special_xf}" if special_xf else ""))

    # Test derived hypotheses
    print("\n" + "="*60)
    print("TESTING DERIVED HYPOTHESES")
    print("="*60)

    derived_results = test_derived_hypotheses(matrix)
    results["derived_hypotheses"] = derived_results

    for result in derived_results:
        r_sf = result["result_step_then_xor"]["result"]
        r_xf = result["result_xor_then_step"]["result"]
        special_sf = result["result_step_then_xor"]["special_matches"]
        special_xf = result["result_xor_then_step"]["special_matches"]

        if special_sf or special_xf:
            print(f"\n{result['hypothesis']}: step={result['step']}, XOR={result['xor']}")
            print(f"  Step then XOR: {r_sf}" + (f" <- SPECIAL: {special_sf}" if special_sf else ""))
            print(f"  XOR then Step: {r_xf}" + (f" <- SPECIAL: {special_xf}" if special_xf else ""))

    # Reverse search: what step+XOR gives us special values?
    print("\n" + "="*60)
    print("REVERSE SEARCH: Finding operations that produce special values")
    print("="*60)

    target_values = [0, 27, 13, 100, 127, 121, 11, -121, -3, -118, 1, -1]
    matches = find_matching_operations(matrix, CFB_POSITION, target_values)

    # Group by result
    by_result = {}
    for match in matches:
        key = match['result']
        if key not in by_result:
            by_result[key] = []
        by_result[key].append(match)

    results["reverse_search"] = {
        "target_values": target_values,
        "matches_by_result": by_result,
        "total_matches": len(matches)
    }

    for val, match_list in sorted(by_result.items()):
        print(f"\nTo get {val}:")
        for m in match_list[:5]:  # Show first 5
            print(f"  {m['formula']} ({m['order']})")
        if len(match_list) > 5:
            print(f"  ... and {len(match_list) - 5} more")

    # Additional analysis: what if we need to match the 1CFi pattern exactly?
    print("\n" + "="*60)
    print("PATTERN MATCHING ANALYSIS")
    print("="*60)

    # The 1CFi solution: -3 + 27 = 24, 24 XOR 13 = 21
    cfi_result_sf = apply_step_xor(cfi_val, 27, 13)
    print(f"\n1CFi solution verification: ({cfi_val} + 27) XOR 13 = {cfi_result_sf}")

    # If 1CFB follows a similar pattern, what would we need?
    # -118 + step = X, X XOR xor = result
    print(f"\n1CFB value: {cfb_val}")
    print(f"If we want similar result to 1CFi ({cfi_result_sf}):")

    # Find step+XOR that gives same result as 1CFi
    same_result_matches = find_matching_operations(matrix, CFB_POSITION, [cfi_result_sf])
    results["pattern_matching"] = {
        "cfi_result": cfi_result_sf,
        "cfb_matches_for_same_result": same_result_matches[:20]  # First 20
    }

    print(f"  Found {len(same_result_matches)} combinations that produce {cfi_result_sf}")
    for m in same_result_matches[:5]:
        print(f"    {m['formula']}")

    # Save results
    print("\n" + "="*60)
    print(f"Saving results to {OUTPUT_PATH}")
    print("="*60)

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("Done!")

    # Summary of interesting findings
    print("\n" + "="*60)
    print("SUMMARY OF INTERESTING FINDINGS")
    print("="*60)

    interesting = []
    for hyp in results["primary_hypotheses"] + results["derived_hypotheses"]:
        for order in ["result_step_then_xor", "result_xor_then_step"]:
            if hyp[order]["special_matches"]:
                interesting.append({
                    "hypothesis": hyp["hypothesis"],
                    "order": order,
                    "step": hyp["step"],
                    "xor": hyp["xor"],
                    "result": hyp[order]["result"],
                    "special": hyp[order]["special_matches"]
                })

    for item in interesting:
        print(f"\n{item['hypothesis']} ({item['order']}):")
        print(f"  step={item['step']}, XOR={item['xor']} -> {item['result']}")
        print(f"  Special: {item['special']}")


if __name__ == "__main__":
    main()
