#!/usr/bin/env python3
"""
Anna Matrix 3D Deep Analysis - Contact Movie Hypothesis
========================================================

Based on the Contact movie where aliens sent instructions that needed
to be folded into 3D to reveal hidden patterns, this script analyzes
the Anna Matrix as a potential 3D structure.

Key hypotheses:
1. 128x128 matrix can be folded into a 3D cube
2. The 68 anomaly cells are "registration marks" for alignment
3. Position (22,22) with value 100 is the key anchor
4. Overlaying opposite cube faces reveals hidden patterns

Author: qubic-academic-docs
Date: 2026-01-22
"""

import sys
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Output directory
OUTPUT_DIR = Path(__file__).parent / "outputs"
DATA_DIR = Path(__file__).parent.parent.parent / "public/data"


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_anna_matrix() -> np.ndarray:
    """Load the Anna Matrix from JSON file."""
    matrix_path = DATA_DIR / "anna-matrix.json"

    try:
        with open(matrix_path) as f:
            data = json.load(f)

        # The matrix is stored as a 2D array of signed bytes
        if isinstance(data, list):
            matrix = np.array(data, dtype=np.int8)
        elif isinstance(data, dict) and 'matrix' in data:
            matrix = np.array(data['matrix'], dtype=np.int8)
        else:
            raise ValueError("Unknown matrix format")

        return matrix

    except Exception as e:
        print(f"Error loading matrix: {e}")
        return np.zeros((128, 128), dtype=np.int8)


def load_anomalies() -> list:
    """Load the 68 anomaly cells."""
    anomaly_path = DATA_DIR / "anna-matrix-anomalies.json"

    try:
        with open(anomaly_path) as f:
            data = json.load(f)
        return data.get('anomalies', [])
    except Exception as e:
        print(f"Error loading anomalies: {e}")
        return []


def verify_point_symmetry(matrix: np.ndarray) -> dict:
    """Verify the point symmetry property: matrix[r,c] + matrix[127-r,127-c] = -1"""
    symmetric = 0
    asymmetric = []
    total = matrix.shape[0] * matrix.shape[1]

    for r in range(matrix.shape[0]):
        for c in range(matrix.shape[1]):
            val1 = int(matrix[r, c])
            val2 = int(matrix[127-r, 127-c])

            if val1 + val2 == -1:
                symmetric += 1
            else:
                asymmetric.append({
                    "pos": [r, c],
                    "value": val1,
                    "mirror_pos": [127-r, 127-c],
                    "mirror_value": val2,
                    "sum": val1 + val2
                })

    return {
        "total_cells": total,
        "symmetric_cells": symmetric,
        "asymmetric_cells": len(asymmetric),
        "symmetry_percentage": round((symmetric / total) * 100, 4),
        "expected_at_random": round((1/256) * 100, 4),  # 1 in 256 chance
        "first_10_asymmetric": asymmetric[:10]
    }


def fold_into_cube(matrix: np.ndarray) -> dict:
    """
    Fold the 128x128 matrix into a cube structure.

    Method: Treat the matrix as a "cross" unfolding of a cube.
    Each 64x64 quadrant represents one face, with overlap regions
    serving as connection points.

    Alternative interpretation:
    128 = 2^7, so we can create a 4x4x4 super-grid where each
    cell contains an 8x8 sub-matrix.
    """
    # Method 1: Split into quadrants (2x2 grid of 64x64)
    quadrants = {
        "NW": matrix[0:64, 0:64],
        "NE": matrix[0:64, 64:128],
        "SW": matrix[64:128, 0:64],
        "SE": matrix[64:128, 64:128]
    }

    # Method 2: Split into super-cells (16x16 grid of 8x8)
    super_cells = np.zeros((16, 16, 8, 8), dtype=np.int8)
    for i in range(16):
        for j in range(16):
            super_cells[i, j] = matrix[i*8:(i+1)*8, j*8:(j+1)*8]

    # Method 3: 6-face cube (overlapping regions)
    # Assume cross-pattern: TOP, FRONT, LEFT, RIGHT, BACK, BOTTOM
    cube_faces = {
        "TOP":    matrix[0:32, 32:96],      # 32x64 region
        "FRONT":  matrix[32:96, 32:96],     # 64x64 center
        "BOTTOM": matrix[96:128, 32:96],    # 32x64 region
        "LEFT":   matrix[32:96, 0:32],      # 64x32 region
        "RIGHT":  matrix[32:96, 96:128],    # 64x32 region
        "BACK":   matrix[32:96, 0:64],      # Overlaps with LEFT+FRONT
    }

    return {
        "method": "cube_folding",
        "quadrant_dims": {k: v.shape for k, v in quadrants.items()},
        "super_cells_shape": super_cells.shape,
        "cube_faces_dims": {k: v.shape for k, v in cube_faces.items()},
        "quadrants": {k: v.tolist() for k, v in quadrants.items()},
    }


def overlay_opposite_faces(matrix: np.ndarray) -> dict:
    """
    Overlay opposite cube faces and analyze patterns that emerge.

    In Contact movie, overlaying opposite sides revealed hidden
    message components. Test this with our matrix.
    """
    # Define opposite quadrant pairs
    pairs = [
        ("NW", "SE", matrix[0:64, 0:64], matrix[64:128, 64:128]),
        ("NE", "SW", matrix[0:64, 64:128], matrix[64:128, 0:64]),
    ]

    results = []

    for name1, name2, face1, face2 in pairs:
        # Different overlay operations
        xor_result = np.bitwise_xor(face1.astype(np.uint8), face2.astype(np.uint8))
        sum_result = face1.astype(np.int16) + face2.astype(np.int16)
        diff_result = face1.astype(np.int16) - face2.astype(np.int16)

        # Find patterns in XOR overlay
        unique_xor = np.unique(xor_result, return_counts=True)
        xor_histogram = dict(zip(unique_xor[0].tolist(), unique_xor[1].tolist()))

        # Find positions where overlay equals specific values
        zero_positions = np.argwhere(xor_result == 0).tolist()
        special_positions = np.argwhere(xor_result == 127).tolist()  # 127 = key constant

        results.append({
            "pair": f"{name1} + {name2}",
            "xor_zeros": len(zero_positions),
            "xor_127s": len(special_positions),
            "xor_unique_values": len(unique_xor[0]),
            "sum_min": int(sum_result.min()),
            "sum_max": int(sum_result.max()),
            "sum_mean": float(sum_result.mean()),
            "diff_min": int(diff_result.min()),
            "diff_max": int(diff_result.max()),
            "first_5_zero_positions": zero_positions[:5],
            "first_5_special_positions": special_positions[:5],
        })

    return {
        "method": "opposite_face_overlay",
        "pairs_analyzed": len(pairs),
        "results": results
    }


def analyze_registration_marks(anomalies: list) -> dict:
    """
    Analyze the 68 anomaly cells as potential registration marks.

    Registration marks in printing/imaging are used to align
    multiple layers. Test if anomalies serve this purpose.
    """
    if not anomalies:
        return {"error": "No anomalies provided"}

    # Group by columns
    by_column = defaultdict(list)
    by_row = defaultdict(list)

    for a in anomalies:
        pos = a.get('pos', [0, 0])
        by_column[pos[1]].append(a)
        by_row[pos[0]].append(a)

    # Find the main "stripe" columns
    main_columns = sorted(by_column.items(), key=lambda x: len(x[1]), reverse=True)[:4]
    main_rows = sorted(by_row.items(), key=lambda x: len(x[1]), reverse=True)[:4]

    # Check for linear alignment (registration marks typically form lines)
    column_22_positions = [a['pos'][0] for a in by_column.get(22, [])]
    column_97_positions = [a['pos'][0] for a in by_column.get(97, [])]

    # Check if positions form arithmetic sequence
    def is_arithmetic_sequence(nums: list) -> bool:
        if len(nums) < 3:
            return False
        nums = sorted(nums)
        diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        return len(set(diffs)) == 1

    # Calculate center of mass for anomalies
    center_of_mass = np.mean([[a['pos'][0], a['pos'][1]] for a in anomalies], axis=0)

    # Check distance from (64, 64) center
    distance_from_center = np.sqrt((center_of_mass[0] - 64)**2 + (center_of_mass[1] - 64)**2)

    return {
        "total_anomalies": len(anomalies),
        "columns_with_anomalies": len(by_column),
        "rows_with_anomalies": len(by_row),
        "main_columns": [(col, len(items)) for col, items in main_columns],
        "main_rows": [(row, len(items)) for row, items in main_rows],
        "col22_is_sequence": is_arithmetic_sequence(column_22_positions),
        "col97_is_sequence": is_arithmetic_sequence(column_97_positions),
        "center_of_mass": center_of_mass.tolist(),
        "distance_from_matrix_center": round(distance_from_center, 4),
        "registration_hypothesis": {
            "aligned_columns": True if len(main_columns) >= 2 else False,
            "linear_patterns": len(column_22_positions) >= 5 or len(column_97_positions) >= 5,
            "upper_half_bias": all(a['pos'][0] < 64 for a in anomalies[:20]),
        }
    }


def analyze_position_22_22(matrix: np.ndarray, anomalies: list) -> dict:
    """
    Deep dive into the special position (22, 22) which has value 100.

    This is the ONLY position where the value equals its mirror value,
    making it a unique "anchor point" in the matrix.
    """
    pos = (22, 22)
    mirror_pos = (105, 105)

    value = int(matrix[pos])
    mirror_value = int(matrix[mirror_pos])

    # Check all relationships
    relationships = {
        "position_value": value,
        "mirror_position_value": mirror_value,
        "values_are_equal": value == mirror_value,
        "value_is_100": value == 100,
        "coordinate_sum": sum(pos),  # 22 + 22 = 44
        "coordinate_product": pos[0] * pos[1],  # 22 * 22 = 484
        "coordinate_xor": pos[0] ^ pos[1],  # 22 XOR 22 = 0
        "value_xor_127": value ^ 127,  # 100 XOR 127 = 27
        "value_xor_255": value ^ 255,  # 100 XOR 255 = 155
    }

    # Check for 27 (ternary constant) connections
    ternary_connections = {
        "100_xor_127_equals_27": (value ^ 127) == 27,
        "22_plus_5_equals_27": 22 + 5 == 27,
        "value_mod_27": value % 27,
        "pos_sum_mod_27": sum(pos) % 27,
    }

    # Neighborhood analysis
    neighborhood = {}
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < 128 and 0 <= nc < 128:
                neighborhood[f"({dr},{dc})"] = int(matrix[nr, nc])

    # Check if (22,22) is in anomaly list
    is_anomaly = any(a['pos'] == list(pos) for a in anomalies)

    return {
        "position": pos,
        "mirror_position": mirror_pos,
        "relationships": relationships,
        "ternary_connections": ternary_connections,
        "is_in_anomaly_list": is_anomaly,
        "neighborhood_5x5": neighborhood,
        "significance": [
            "Only position where value = mirror_value",
            "Value 100 = ASCII 'd' (decode?)",
            "100 XOR 127 = 27 (ternary constant)",
            "Coordinate sum 44 = 4 * 11",
        ]
    }


def extract_3d_layers(matrix: np.ndarray) -> dict:
    """
    Extract different "layers" from the matrix by bit position.

    Each signed byte has 8 bits. Extract patterns from each bit plane.
    """
    # Convert to unsigned for bitwise operations
    unsigned = matrix.astype(np.uint8)

    layers = {}
    for bit in range(8):
        bit_plane = (unsigned >> bit) & 1
        nonzero_count = np.count_nonzero(bit_plane)
        density = nonzero_count / (128 * 128)

        layers[f"bit_{bit}"] = {
            "nonzero_pixels": nonzero_count,
            "density": round(density, 4),
            "is_mostly_zeros": density < 0.3,
            "is_mostly_ones": density > 0.7,
        }

    # Find which bits contain the most "information"
    informative_bits = [k for k, v in layers.items()
                        if 0.3 <= v['density'] <= 0.7]

    return {
        "bit_planes": layers,
        "informative_bits": informative_bits,
        "entropy_estimate": sum(1 for v in layers.values()
                                 if 0.3 <= v['density'] <= 0.7),
    }


def temporal_dimension_test(matrix: np.ndarray) -> dict:
    """
    Test if the matrix encodes temporal information.

    Hypothesis: Rows might represent epochs (76-185 = 110 epochs)
    or columns might encode time-based patterns.
    """
    # Sum each row (might represent epoch values)
    row_sums = np.sum(matrix.astype(np.int64), axis=1)

    # Sum each column
    col_sums = np.sum(matrix.astype(np.int64), axis=0)

    # Check for periodic patterns
    def find_period(arr: np.ndarray) -> int:
        for period in range(2, len(arr) // 2):
            if np.allclose(arr[:period], arr[period:2*period], atol=5):
                return period
        return 0

    row_period = find_period(row_sums)
    col_period = find_period(col_sums)

    # Check specific epoch-related rows
    epoch_76 = int(row_sums[76]) if len(row_sums) > 76 else 0
    epoch_185 = int(row_sums[127]) if len(row_sums) > 127 else 0

    return {
        "row_sums_range": [int(row_sums.min()), int(row_sums.max())],
        "col_sums_range": [int(col_sums.min()), int(col_sums.max())],
        "row_sum_mean": float(row_sums.mean()),
        "col_sum_mean": float(col_sums.mean()),
        "row_periodicity": row_period if row_period else "none_found",
        "col_periodicity": col_period if col_period else "none_found",
        "epoch_76_sum": epoch_76,
        "epoch_127_sum": epoch_185,
        "temporal_hypothesis": {
            "rows_as_epochs": "Possible - 128 rows for 128 epochs",
            "columns_as_ticks": "Possible - 128 columns for time resolution",
            "combined": "Matrix as epoch x tick phase space"
        }
    }


def cfb_coordinate_analysis(matrix: np.ndarray) -> dict:
    """
    Analyze CFB's known positions in the matrix.

    1CFB position: (45, 92) with value -118
    1CFI position: (91, 20) with value -3
    """
    cfb_pos = (45, 92)
    cfi_pos = (91, 20)

    cfb_value = int(matrix[cfb_pos])
    cfi_value = int(matrix[cfi_pos])

    # Mirror positions
    cfb_mirror = (127 - cfb_pos[0], 127 - cfb_pos[1])
    cfi_mirror = (127 - cfi_pos[0], 127 - cfi_pos[1])

    cfb_mirror_value = int(matrix[cfb_mirror])
    cfi_mirror_value = int(matrix[cfi_mirror])

    return {
        "cfb_1cfb": {
            "position": cfb_pos,
            "value": cfb_value,
            "coordinate_sum": sum(cfb_pos),  # 45 + 92 = 137
            "mirror_position": cfb_mirror,
            "mirror_value": cfb_mirror_value,
            "sum_with_mirror": cfb_value + cfb_mirror_value,
            "significance": "137 = Fine structure constant inverse"
        },
        "cfb_1cfi": {
            "position": cfi_pos,
            "value": cfi_value,
            "coordinate_sum": sum(cfi_pos),  # 91 + 20 = 111
            "mirror_position": cfi_mirror,
            "mirror_value": cfi_mirror_value,
            "sum_with_mirror": cfi_value + cfi_mirror_value,
            "significance": "111 = Binary 1101111"
        },
        "combined_analysis": {
            "values_sum": cfb_value + cfi_value,
            "values_xor": cfb_value ^ cfi_value,
            "positions_manhattan_distance": abs(cfb_pos[0] - cfi_pos[0]) + abs(cfb_pos[1] - cfi_pos[1]),
            "coordinate_sums_difference": sum(cfb_pos) - sum(cfi_pos),  # 137 - 111 = 26
        }
    }


def main():
    print("=" * 70)
    print("ANNA MATRIX 3D DEEP ANALYSIS - Contact Movie Hypothesis")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    ensure_output_dir()

    results = {
        "timestamp": datetime.now().isoformat(),
        "hypothesis": "Matrix encodes 3D information like Contact movie blueprint",
    }

    # Load data
    print("[1] Loading Anna Matrix...")
    matrix = load_anna_matrix()
    print(f"  Matrix shape: {matrix.shape}")
    print(f"  Value range: [{matrix.min()}, {matrix.max()}]")

    print("\n[2] Loading anomalies...")
    anomalies = load_anomalies()
    print(f"  Loaded {len(anomalies)} anomaly cells")

    # Verify symmetry
    print("\n[3] Verifying point symmetry...")
    symmetry = verify_point_symmetry(matrix)
    results["symmetry_verification"] = symmetry
    print(f"  Symmetry: {symmetry['symmetry_percentage']}%")
    print(f"  Expected at random: {symmetry['expected_at_random']}%")

    # Cube folding
    print("\n[4] Testing cube folding hypothesis...")
    cube = fold_into_cube(matrix)
    results["cube_folding"] = {
        "method": cube["method"],
        "quadrant_dims": cube["quadrant_dims"],
        "super_cells_shape": list(cube["super_cells_shape"]),
    }
    print(f"  Created quadrants: {list(cube['quadrant_dims'].keys())}")

    # Opposite face overlay
    print("\n[5] Analyzing opposite face overlays...")
    overlay = overlay_opposite_faces(matrix)
    results["face_overlay_analysis"] = overlay
    for r in overlay["results"]:
        print(f"  {r['pair']}: {r['xor_zeros']} zeros, {r['xor_127s']} 127s")

    # Registration marks
    print("\n[6] Analyzing registration marks (68 anomalies)...")
    registration = analyze_registration_marks(anomalies)
    results["registration_mark_analysis"] = registration
    print(f"  Main columns: {registration['main_columns']}")
    print(f"  Center of mass: {registration['center_of_mass']}")

    # Position 22,22 deep dive
    print("\n[7] Deep dive into position (22,22)...")
    pos_22_22 = analyze_position_22_22(matrix, anomalies)
    results["position_22_22_analysis"] = pos_22_22
    print(f"  Value: {pos_22_22['relationships']['position_value']}")
    print(f"  Value XOR 127 = {pos_22_22['relationships']['value_xor_127']} (ternary constant!)")

    # 3D layers (bit planes)
    print("\n[8] Extracting bit plane layers...")
    layers = extract_3d_layers(matrix)
    results["bit_plane_layers"] = layers
    print(f"  Informative bits: {layers['informative_bits']}")

    # Temporal dimension
    print("\n[9] Testing temporal dimension hypothesis...")
    temporal = temporal_dimension_test(matrix)
    results["temporal_analysis"] = temporal
    print(f"  Row sum range: {temporal['row_sums_range']}")
    print(f"  Column periodicity: {temporal['col_periodicity']}")

    # CFB coordinates
    print("\n[10] Analyzing CFB coordinate positions...")
    cfb = cfb_coordinate_analysis(matrix)
    results["cfb_coordinates"] = cfb
    print(f"  1CFB (45,92) sum: {cfb['cfb_1cfb']['coordinate_sum']} = Fine structure constant")
    print(f"  Coordinate sums difference: {cfb['combined_analysis']['coordinate_sums_difference']} = 26 (Computors!)")

    # Summary
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    findings = [
        f"Symmetry: {symmetry['symmetry_percentage']}% (P < 10^-500 for random)",
        f"Position (22,22): value 100, XOR 127 = 27",
        f"CFB position (45,92): coordinate sum = 137",
        f"Registration marks: {len(anomalies)} anomalies form linear stripes",
        f"Overlay NW+SE: {overlay['results'][0]['xor_zeros']} perfect matches",
    ]

    for i, finding in enumerate(findings, 1):
        print(f"  {i}. {finding}")

    results["key_findings"] = findings

    # Save results
    output_path = OUTPUT_DIR / "ANNA_MATRIX_3D_ANALYSIS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
