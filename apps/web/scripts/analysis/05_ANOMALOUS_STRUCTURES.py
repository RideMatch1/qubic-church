#!/usr/bin/env python3
"""
Phase 5: Anomalous Structures Investigation
=============================================
Row 6 deep dive, entropy profiles, all-row anomaly scan.

The existing control test proved:
- H2: Row 6 has 24/128 cells with value 26 (p=0.0, random max was 13)
- H4: Mean row entropy 5.05 vs 6.22 random (p=0.0)

This script investigates WHY these anomalies exist and what they mean.
"""
import sys
import os
import json
import numpy as np
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.matrix_loader import load_matrix
from lib.statistical_tests import TestReport, empirical_p_value, format_p_value
from lib.control_generator import generate_uniform, generate_symmetric

SEED = 42
N_CONTROLS = 1000
OUTPUT_DIR = Path(__file__).parent
RESULTS_FILE = OUTPUT_DIR / "05_ANOMALOUS_STRUCTURES_RESULTS.json"


def row_entropy(row):
    """Shannon entropy of a single row."""
    counts = Counter(row)
    total = len(row)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * np.log2(p)
    return entropy


def most_common_value_frequency(row):
    """Return (most_common_value, frequency, fraction) for a row."""
    counts = Counter(row)
    val, freq = counts.most_common(1)[0]
    return int(val), freq, freq / len(row)


def main():
    print("=" * 80)
    print("  PHASE 5: ANOMALOUS STRUCTURES INVESTIGATION")
    print("=" * 80)
    print(f"Seed: {SEED} | Controls: {N_CONTROLS}")
    print()

    matrix = load_matrix(verify_hash=False)

    # =========================================================================
    # SECTION 1: ROW 6 DEEP DIVE
    # =========================================================================
    print("=" * 80)
    print("SECTION 1: ROW 6 DEEP DIVE")
    print("=" * 80)
    print()

    row6 = matrix[6, :]
    row6_counts = Counter(row6)
    print(f"Row 6 value distribution (top 10):")
    for val, count in row6_counts.most_common(10):
        print(f"  Value {val:4d}: {count:3d} times ({count/128*100:.1f}%)")

    # Where is value 26?
    val26_cols = np.where(row6 == 26)[0]
    print(f"\nValue 26 appears at {len(val26_cols)} column positions:")
    print(f"  Columns: {sorted(val26_cols.tolist())}")

    # Check differences between consecutive positions
    if len(val26_cols) > 1:
        diffs = np.diff(sorted(val26_cols))
        print(f"  Gaps between positions: {diffs.tolist()}")
        print(f"  Mean gap: {np.mean(diffs):.1f}, Std: {np.std(diffs):.1f}")

    # Row 121 = mirror of Row 6
    row121 = matrix[121, :]
    print(f"\nRow 121 (= 127 - 6, mirror of Row 6):")
    row121_counts = Counter(row121)
    for val, count in row121_counts.most_common(10):
        print(f"  Value {val:4d}: {count:3d} times ({count/128*100:.1f}%)")

    # Check symmetry: row6[c] + row121[127-c] should = -1
    symmetry_check = []
    for c in range(128):
        s = int(row6[c]) + int(row121[127 - c])
        symmetry_check.append(s)
    n_minus1 = sum(1 for s in symmetry_check if s == -1)
    exceptions = [(c, symmetry_check[c]) for c in range(128) if symmetry_check[c] != -1]
    print(f"\nRow 6/121 symmetry: {n_minus1}/128 cells satisfy row6[c] + row121[127-c] = -1")
    if exceptions:
        print(f"  Exceptions: {exceptions}")

    # Verify: if row6[c]=26, then row121[127-c] should = -27
    val_minus27_cols_121 = np.where(row121 == -27)[0]
    mirror_cols = sorted([127 - c for c in val26_cols])
    print(f"\nVerification of symmetry consequence:")
    print(f"  Row 6 has value 26 at {len(val26_cols)} positions")
    print(f"  Row 121 has value -27 at {len(val_minus27_cols_121)} positions")
    print(f"  Mirror columns of Row6-26: {mirror_cols}")
    print(f"  Row121-(-27) columns:      {sorted(val_minus27_cols_121.tolist())}")
    matches = set(mirror_cols) & set(val_minus27_cols_121.tolist())
    print(f"  Overlap: {len(matches)} out of {len(val26_cols)} (100% expected if symmetric)")

    # =========================================================================
    # SECTION 2: ALL-ROW ANOMALY SCAN
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 2: ALL-ROW VALUE CONCENTRATION SCAN")
    print("=" * 80)
    print()

    row_anomalies = []
    for r in range(128):
        row = matrix[r, :]
        val, freq, frac = most_common_value_frequency(row)
        ent = row_entropy(row)
        row_anomalies.append({
            "row": r,
            "most_common_value": val,
            "frequency": freq,
            "fraction": frac,
            "entropy": ent
        })

    # Sort by frequency (highest concentration first)
    row_anomalies.sort(key=lambda x: x["frequency"], reverse=True)

    print("Top 20 most concentrated rows:")
    print(f"  {'Row':>4} {'Value':>6} {'Freq':>5} {'Frac':>7} {'Entropy':>8}")
    print(f"  {'-'*36}")
    for ra in row_anomalies[:20]:
        mirror = 127 - ra["row"]
        print(f"  {ra['row']:4d} {ra['most_common_value']:6d} {ra['frequency']:5d} "
              f"{ra['fraction']:7.1%} {ra['entropy']:8.3f}  (mirror: row {mirror})")

    # Check if anomalous rows come in mirror pairs
    print("\nMirror pair analysis:")
    top_rows = set(ra["row"] for ra in row_anomalies[:20])
    for ra in row_anomalies[:20]:
        mirror = 127 - ra["row"]
        if mirror in top_rows:
            print(f"  Row {ra['row']} <-> Row {mirror}: BOTH anomalous (mirror pair)")

    # =========================================================================
    # SECTION 3: ENTROPY PROFILE
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 3: ROW ENTROPY PROFILE")
    print("=" * 80)
    print()

    entropies = [row_entropy(matrix[r, :]) for r in range(128)]
    col_entropies = [row_entropy(matrix[:, c]) for c in range(128)]

    print(f"Row entropies: mean={np.mean(entropies):.3f}, std={np.std(entropies):.3f}")
    print(f"  Min: row {np.argmin(entropies)} = {min(entropies):.3f}")
    print(f"  Max: row {np.argmax(entropies)} = {max(entropies):.3f}")
    print()
    print(f"Column entropies: mean={np.mean(col_entropies):.3f}, std={np.std(col_entropies):.3f}")
    print(f"  Min: col {np.argmin(col_entropies)} = {min(col_entropies):.3f}")
    print(f"  Max: col {np.argmax(col_entropies)} = {max(col_entropies):.3f}")

    # 5 lowest entropy rows
    row_ent_sorted = sorted(enumerate(entropies), key=lambda x: x[1])
    print(f"\n5 lowest-entropy rows:")
    for r, e in row_ent_sorted[:5]:
        val, freq, frac = most_common_value_frequency(matrix[r, :])
        print(f"  Row {r:3d}: entropy={e:.3f}, dominant value={val} ({freq}/128)")

    # =========================================================================
    # SECTION 4: ROW 6 vs CONTROLS
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 4: STATISTICAL TESTING")
    print("=" * 80)
    print()

    rng = np.random.default_rng(SEED)
    report = TestReport("Phase 5: Anomalous Structures", N_CONTROLS, SEED)

    # Generate symmetric controls (most relevant comparison)
    print(f"Generating {N_CONTROLS} symmetric control matrices...")
    ctrl_max_freq = []
    ctrl_min_entropy = []
    ctrl_n_anomalous_rows = []  # rows with most-common-freq > 15

    for i in range(N_CONTROLS):
        ctrl = generate_symmetric(rng)
        max_freq = 0
        min_ent = 999
        n_anom = 0
        for r in range(128):
            _, freq, _ = most_common_value_frequency(ctrl[r, :])
            ent = row_entropy(ctrl[r, :])
            max_freq = max(max_freq, freq)
            min_ent = min(min_ent, ent)
            if freq > 15:
                n_anom += 1
        ctrl_max_freq.append(max_freq)
        ctrl_min_entropy.append(min_ent)
        ctrl_n_anomalous_rows.append(n_anom)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{N_CONTROLS}...")

    ctrl_max_freq = np.array(ctrl_max_freq)
    ctrl_min_entropy = np.array(ctrl_min_entropy)
    ctrl_n_anomalous_rows = np.array(ctrl_n_anomalous_rows)

    # Anna's values
    anna_max_freq = max(ra["frequency"] for ra in row_anomalies)
    anna_min_entropy = min(entropies)
    anna_n_anomalous = sum(1 for ra in row_anomalies if ra["frequency"] > 15)

    # Test: Max frequency in any row
    report.add_test(
        "max_row_concentration_vs_symmetric",
        "Anna's maximum row value concentration is consistent with symmetric matrices",
        anna_max_freq,
        ctrl_max_freq,
        alternative="greater",
        unit="count"
    )

    # Test: Minimum row entropy
    report.add_test(
        "min_row_entropy_vs_symmetric",
        "Anna's minimum row entropy is consistent with symmetric matrices",
        anna_min_entropy,
        ctrl_min_entropy,
        alternative="less",
        unit="bits"
    )

    # Test: Number of anomalous rows (freq > 15)
    report.add_test(
        "n_anomalous_rows_vs_symmetric",
        "Anna's count of anomalous rows is consistent with symmetric matrices",
        anna_n_anomalous,
        ctrl_n_anomalous_rows,
        alternative="greater",
        unit="rows"
    )

    # =========================================================================
    # SECTION 5: VALUE 26 GLOBAL ANALYSIS
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 5: VALUE 26 GLOBAL ANALYSIS")
    print("=" * 80)
    print()

    # How often does value 26 appear in the entire matrix?
    total_26 = int(np.sum(matrix == 26))
    total_minus27 = int(np.sum(matrix == -27))
    print(f"Value  26 appears {total_26} times globally ({total_26/16384*100:.2f}%)")
    print(f"Value -27 appears {total_minus27} times globally ({total_minus27/16384*100:.2f}%)")
    print(f"Expected per value (uniform): {16384/256:.1f} = {16384/256/16384*100:.2f}%")
    print(f"Ratio 26/expected: {total_26 / (16384/256):.1f}x")

    # Which rows contain value 26 most?
    rows_with_26 = []
    for r in range(128):
        count = int(np.sum(matrix[r, :] == 26))
        if count > 0:
            rows_with_26.append((r, count))
    rows_with_26.sort(key=lambda x: x[1], reverse=True)
    print(f"\nRows with value 26 (top 10):")
    for r, c in rows_with_26[:10]:
        print(f"  Row {r:3d}: {c} times")

    # =========================================================================
    # SECTION 6: COLUMN SUM SYMMETRY AS CONSEQUENCE
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 6: COLUMN SUM SYMMETRY (is it just a consequence?)")
    print("=" * 80)
    print()

    print("If matrix[r,c] + matrix[127-r,127-c] = -1 for all cells,")
    print("then sum(col_c) + sum(col_{127-c}) = 128 * (-1) = -128")
    print("Testing this prediction vs reality:")
    print()

    col_sums = matrix.sum(axis=0)
    breaking_pairs = []
    perfect_pairs = 0
    for c in range(64):
        expected = -128
        actual = int(col_sums[c]) + int(col_sums[127 - c])
        if actual == expected:
            perfect_pairs += 1
        else:
            breaking_pairs.append((c, 127 - c, actual, actual - expected))

    print(f"Perfect pairs (sum = -128): {perfect_pairs}/64")
    print(f"Breaking pairs: {len(breaking_pairs)}/64")
    if breaking_pairs:
        print(f"\nBreaking pairs detail:")
        for c1, c2, actual, dev in breaking_pairs:
            print(f"  Col {c1:3d} + Col {c2:3d} = {actual:5d} (deviation: {dev:+d} from -128)")
            # Count how many exception cells are in these columns
            n_exceptions_c1 = 0
            n_exceptions_c2 = 0
            for r in range(128):
                if int(matrix[r, c1]) + int(matrix[127 - r, 127 - c1]) != -1:
                    n_exceptions_c1 += 1
                if int(matrix[r, c2]) + int(matrix[127 - r, 127 - c2]) != -1:
                    n_exceptions_c2 += 1
            print(f"    Exception cells in col {c1}: {n_exceptions_c1}, col {c2}: {n_exceptions_c2}")

    print(f"\nCONCLUSION: Column sum symmetry is {'ENTIRELY' if len(breaking_pairs) == 0 else 'MOSTLY'} "
          f"a mathematical consequence of point symmetry.")
    print("It is NOT an independent discovery.")

    # Same for rows
    row_sums = matrix.sum(axis=1)
    row_perfect = sum(1 for r in range(64) if int(row_sums[r]) + int(row_sums[127-r]) == -128)
    print(f"\nRow sum pairs = -128: {row_perfect}/64")

    # =========================================================================
    # PRINT REPORT & SAVE
    # =========================================================================
    print()
    report.print_report()
    report.save_json(str(RESULTS_FILE))

    # Save detailed results
    detail = {
        "row6_value26_columns": sorted(val26_cols.tolist()),
        "row_anomalies_top20": [
            {k: (int(v) if isinstance(v, (np.int64, np.integer)) else v)
             for k, v in ra.items()}
            for ra in row_anomalies[:20]
        ],
        "entropy_profile": {
            "row_entropies": [float(e) for e in entropies],
            "col_entropies": [float(e) for e in col_entropies],
        },
        "value_26_global_count": total_26,
        "value_minus27_global_count": total_minus27,
        "column_sum_symmetry": {
            "perfect_pairs": perfect_pairs,
            "breaking_pairs": len(breaking_pairs),
        },
    }
    with open(str(OUTPUT_DIR / "05_ANOMALOUS_DETAILS.json"), "w") as f:
        json.dump(detail, f, indent=2)
    print(f"\nDetailed results saved to 05_ANOMALOUS_DETAILS.json")


if __name__ == "__main__":
    main()
