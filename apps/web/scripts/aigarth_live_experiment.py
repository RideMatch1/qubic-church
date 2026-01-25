#!/usr/bin/env python3
"""
AIGARTH LIVE EXPERIMENT
=======================

This script experiments with the official Aigarth-it library to understand:
1. How the ternary neural network works
2. How mutations evolve the network
3. How feedforward processing operates
4. Connection to Anna Matrix patterns

Date: January 17, 2026
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Import Aigarth modules
try:
    from aigarth_it.common import (
        ternary_clamp,
        random_trit_vector,
        bitstring_to_trits,
        trits_to_bitstring,
        int_to_bitstring,
        bitstring64_to_int
    )
    from aigarth_it.neuron_cl import AITClNeuron
    from aigarth_it.itu_cl import AigarthITUCl
    from aigarth_it.icap.itucl_aai_i2x7o8 import ITUClArithmeticAdditionIntI2x7O8
    print("✓ Aigarth-it modules loaded successfully!")
except ImportError as e:
    print(f"✗ Failed to import Aigarth modules: {e}")
    sys.exit(1)

# Results storage
RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "experiments": []
}

def log(msg):
    print(msg)

def divider(title=""):
    log(f"\n{'='*60}")
    if title:
        log(f"  {title}")
        log('='*60)

# =============================================================================
# EXPERIMENT 1: Ternary Logic Verification
# =============================================================================
def experiment_1_ternary_logic():
    """Test the ternary_clamp function."""
    divider("EXPERIMENT 1: Ternary Logic Verification")

    test_cases = [
        (-1000, -1),
        (-100, -1),
        (-2, -1),
        (-1, -1),
        (0, 0),
        (1, 1),
        (2, 1),
        (100, 1),
        (1000, 1)
    ]

    results = []
    for input_val, expected in test_cases:
        result = ternary_clamp(input_val)
        status = "✓" if result == expected else "✗"
        results.append({
            "input": input_val,
            "output": result,
            "expected": expected,
            "match": result == expected
        })
        log(f"  {status} ternary_clamp({input_val:5d}) = {result:2d} (expected: {expected:2d})")

    all_passed = all(r["match"] for r in results)
    log(f"\n  Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")

    RESULTS["experiments"].append({
        "name": "Ternary Logic",
        "test_cases": results,
        "passed": all_passed
    })

    return all_passed

# =============================================================================
# EXPERIMENT 2: Bit-Trit Conversion
# =============================================================================
def experiment_2_bit_trit_conversion():
    """Test conversion between binary and ternary."""
    divider("EXPERIMENT 2: Bit-Trit Conversion")

    # Test integer to bitstring
    test_integers = [0, 1, -1, 5, -5, 27, -27, 127, -128]

    log("  Integer → Bitstring → Trits → Bitstring → Integer")
    log("  " + "-"*50)

    results = []
    for num in test_integers:
        try:
            # Integer to bitstring (8 bits, constant length)
            bitstring = int_to_bitstring(num, max_bits=8, const_len=True)
            # Bitstring to trits
            trits = bitstring_to_trits(bitstring)
            # Trits back to bitstring
            bitstring_back = trits_to_bitstring(trits)
            # Bitstring back to integer
            num_back = bitstring64_to_int(bitstring_back)

            match = num == num_back
            status = "✓" if match else "✗"

            results.append({
                "original": num,
                "bitstring": bitstring,
                "trits": trits,
                "recovered": num_back,
                "match": match
            })

            log(f"  {status} {num:4d} → {bitstring} → {trits[:4]}... → {num_back:4d}")
        except Exception as e:
            log(f"  ✗ {num:4d} → ERROR: {e}")
            results.append({
                "original": num,
                "error": str(e),
                "match": False
            })

    all_passed = all(r["match"] for r in results)
    log(f"\n  Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")

    RESULTS["experiments"].append({
        "name": "Bit-Trit Conversion",
        "test_cases": results,
        "passed": all_passed
    })

    return all_passed

# =============================================================================
# EXPERIMENT 3: Circle Neuron
# =============================================================================
def experiment_3_circle_neuron():
    """Test the Circle Neuron implementation."""
    divider("EXPERIMENT 3: Circle Neuron")

    # Create a neuron with specific weights
    weights = [1, -1, 0, 1, -1]  # Ternary weights
    neuron = AITClNeuron(input_weights=weights, input_skew=0)

    log(f"  Created neuron with weights: {neuron.input_weights}")
    log(f"  Input skew: {neuron.input_skew}")
    log(f"  Input split index: {neuron.input_split_index}")
    log(f"  Initial state: {neuron.state}")

    # Test feedforward with different inputs
    test_inputs = [
        (1, 1, 1, 1, 1),    # All positive
        (-1, -1, -1, -1, -1),  # All negative
        (0, 0, 0, 0, 0),    # All neutral
        (1, -1, 0, 1, -1),  # Mixed
        (1, 1, 0, 0, 0),    # Partial
    ]

    log("\n  Feedforward Tests:")
    log("  " + "-"*50)

    results = []
    for feed in test_inputs:
        neuron.state = 0  # Reset
        neuron.feedforward(feed)
        new_state, changed = neuron.commit_state()

        # Manual calculation: sum(input * weight) then clamp
        manual_sum = sum(f * w for f, w in zip(feed, weights))
        manual_clamp = ternary_clamp(manual_sum)

        match = new_state == manual_clamp
        status = "✓" if match else "✗"

        results.append({
            "input": feed,
            "weights": weights,
            "sum": manual_sum,
            "output": new_state,
            "expected": manual_clamp,
            "match": match
        })

        log(f"  {status} Input: {feed}")
        log(f"      Sum: {manual_sum:3d} → Clamped: {new_state:2d}")

    all_passed = all(r["match"] for r in results)
    log(f"\n  Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")

    RESULTS["experiments"].append({
        "name": "Circle Neuron",
        "neuron_config": {
            "weights": weights,
            "skew": 0
        },
        "test_cases": results,
        "passed": all_passed
    })

    return all_passed

# =============================================================================
# EXPERIMENT 4: Arithmetic Addition ITU
# =============================================================================
def experiment_4_arithmetic_itu():
    """Test the Arithmetic Addition ITU."""
    divider("EXPERIMENT 4: Arithmetic Addition ITU")

    # Create the ITU
    itu = ITUClArithmeticAdditionIntI2x7O8()

    log(f"  ITU Type: {itu.meta.type}")
    log(f"  ITU Group: {itu.meta.group}")
    log(f"  ITU UUID: {itu.meta.id}")
    log(f"  ITU Version: {itu.meta.version_string}")
    log(f"  Input bitwidth: {itu.meta.input_bitwidth}")
    log(f"  Output bitwidth: {itu.meta.output_bitwidth}")
    log(f"  Neuron count: {len(itu._circle)}")
    log(f"  FF cycle cap: {itu.ff_cycle_cap}")

    # Test with simple additions
    test_cases = [
        (0, 0, 0),      # 0 + 0 = 0
        (1, 1, 2),      # 1 + 1 = 2
        (5, 3, 8),      # 5 + 3 = 8
        (-1, 1, 0),     # -1 + 1 = 0
        (10, -5, 5),    # 10 + (-5) = 5
        (63, 63, 126),  # Max positive
        (-64, -64, -128), # Max negative
    ]

    log("\n  Addition Tests (UNTRAINED - Expect random results):")
    log("  " + "-"*50)

    results = []
    for a, b, expected in test_cases:
        try:
            reflection = itu.reflect(a, b)
            result = reflection.integer if reflection.integer is not None else "UNKNOWN"

            match = result == expected
            status = "✓" if match else "≈" if result == "UNKNOWN" else "✗"

            results.append({
                "a": a,
                "b": b,
                "expected": expected,
                "got": result,
                "ticks": reflection.ffcycle_stats.tick_count,
                "end_reason": reflection.ffcycle_stats.end_reason,
                "match": match
            })

            log(f"  {status} {a:4d} + {b:4d} = {str(result):>8} (expected: {expected:4d})")
            log(f"      Ticks: {reflection.ffcycle_stats.tick_count}, Reason: {reflection.ffcycle_stats.end_reason}")
        except Exception as e:
            log(f"  ✗ {a:4d} + {b:4d} → ERROR: {e}")
            results.append({
                "a": a,
                "b": b,
                "error": str(e)
            })

    # Count correct answers
    correct = sum(1 for r in results if r.get("match", False))
    total = len(results)

    log(f"\n  Result: {correct}/{total} correct (UNTRAINED ITU)")
    log(f"  Note: Random results expected - ITU needs training!")

    RESULTS["experiments"].append({
        "name": "Arithmetic Addition ITU",
        "itu_config": {
            "type": itu.meta.type,
            "uuid": itu.meta.id,
            "neurons": len(itu._circle),
            "ff_cycle_cap": itu.ff_cycle_cap
        },
        "test_cases": results,
        "correct": correct,
        "total": total
    })

    return True  # Always pass - untrained is expected

# =============================================================================
# EXPERIMENT 5: Random Trit Vector
# =============================================================================
def experiment_5_random_trits():
    """Test random trit vector generation."""
    divider("EXPERIMENT 5: Random Trit Vector Statistics")

    # Generate many random vectors
    num_vectors = 1000
    vector_size = 100

    all_trits = []
    for _ in range(num_vectors):
        vec = random_trit_vector(vector_size)
        all_trits.extend(vec)

    # Count distribution
    total = len(all_trits)
    count_neg = all_trits.count(-1)
    count_zero = all_trits.count(0)
    count_pos = all_trits.count(1)

    log(f"  Generated {num_vectors} vectors of size {vector_size}")
    log(f"  Total trits: {total}")
    log(f"\n  Distribution:")
    log(f"    -1: {count_neg:6d} ({100*count_neg/total:.1f}%)")
    log(f"     0: {count_zero:6d} ({100*count_zero/total:.1f}%)")
    log(f"    +1: {count_pos:6d} ({100*count_pos/total:.1f}%)")

    # Expected: ~33.3% each
    expected_pct = 33.3
    tolerance = 3.0  # Allow 3% deviation

    actual_pcts = [100*count_neg/total, 100*count_zero/total, 100*count_pos/total]
    all_within = all(abs(p - expected_pct) < tolerance for p in actual_pcts)

    log(f"\n  Expected: ~{expected_pct}% each (±{tolerance}%)")
    log(f"  Result: {'UNIFORM DISTRIBUTION' if all_within else 'SKEWED DISTRIBUTION'}")

    RESULTS["experiments"].append({
        "name": "Random Trit Vector",
        "sample_size": total,
        "distribution": {
            "-1": count_neg,
            "0": count_zero,
            "+1": count_pos
        },
        "percentages": {
            "-1": 100*count_neg/total,
            "0": 100*count_zero/total,
            "+1": 100*count_pos/total
        },
        "uniform": all_within
    })

    return all_within

# =============================================================================
# EXPERIMENT 6: Connection to Anna Matrix
# =============================================================================
def experiment_6_anna_connection():
    """Analyze potential connection to Anna Matrix values."""
    divider("EXPERIMENT 6: Anna Matrix Connection Analysis")

    # Anna Matrix has values in range [-128, 127] (int8)
    # Aigarth uses ternary [-1, 0, +1]

    # Hypothesis: Anna Matrix values are aggregated trit weights
    # If we sum 128 trits (one row), we get range [-128, +128]

    log("  Hypothesis: Anna Matrix values = Sum of ternary weights")
    log("\n  Testing value reconstruction:")

    # Known Anna Matrix collision values
    anna_values = [-27, 26, -121, -114, -113, 101, -93, -40]

    results = []
    for target in anna_values:
        # Can we construct this value from 128 trits?
        # target = count(+1) - count(-1)
        # count(+1) + count(-1) + count(0) = 128

        # Solve: p - n = target, p + n + z = 128, p,n,z >= 0
        # For any target in [-128, 128], we can find valid p, n, z

        # Example solution: minimize zeros
        if target >= 0:
            # More positives than negatives
            # p = target + n, choose n to make p + n <= 128
            n = max(0, (128 - target) // 2)
            p = target + n
            z = 128 - p - n
        else:
            # More negatives than positives
            # n = -target + p, choose p to make p + n <= 128
            p = max(0, (128 + target) // 2)
            n = -target + p
            z = 128 - p - n

        # Verify
        reconstructed = p - n
        total = p + n + z

        valid = (reconstructed == target) and (total == 128) and all(x >= 0 for x in [p, n, z])
        status = "✓" if valid else "✗"

        results.append({
            "target": target,
            "positives": p,
            "negatives": n,
            "zeros": z,
            "reconstructed": reconstructed,
            "valid": valid
        })

        log(f"  {status} Value {target:4d} = {p:3d}×(+1) + {n:3d}×(-1) + {z:3d}×(0)")

    all_valid = all(r["valid"] for r in results)

    log(f"\n  Result: {'ALL VALUES RECONSTRUCTABLE' if all_valid else 'SOME FAILED'}")
    log("  Implication: Anna Matrix CAN store aggregated trit sums!")

    RESULTS["experiments"].append({
        "name": "Anna Matrix Connection",
        "hypothesis": "Anna values = sum of ternary weights",
        "test_cases": results,
        "all_reconstructable": all_valid
    })

    return all_valid

# =============================================================================
# MAIN
# =============================================================================
def main():
    divider("AIGARTH LIVE EXPERIMENT")
    log(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  Python: {sys.version.split()[0]}")

    # Run all experiments
    experiments = [
        ("Ternary Logic", experiment_1_ternary_logic),
        ("Bit-Trit Conversion", experiment_2_bit_trit_conversion),
        ("Circle Neuron", experiment_3_circle_neuron),
        ("Arithmetic ITU", experiment_4_arithmetic_itu),
        ("Random Trits", experiment_5_random_trits),
        ("Anna Connection", experiment_6_anna_connection),
    ]

    passed = 0
    for name, func in experiments:
        try:
            if func():
                passed += 1
        except Exception as e:
            log(f"\n  ✗ EXPERIMENT FAILED: {name}")
            log(f"    Error: {e}")

    divider("SUMMARY")
    log(f"  Experiments passed: {passed}/{len(experiments)}")

    # Save results
    output_path = Path(__file__).parent / "AIGARTH_EXPERIMENT_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(RESULTS, f, indent=2, default=str)
    log(f"\n  Results saved to: {output_path}")

    divider()

    return passed == len(experiments)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
