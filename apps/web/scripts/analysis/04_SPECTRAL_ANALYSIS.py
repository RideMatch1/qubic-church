#!/usr/bin/env python3
"""
Phase 4: Spectral and Linear Algebra Analysis
==============================================
2D FFT, SVD, eigenvalues - compared against 1000 control matrices.

Null hypothesis: The Anna Matrix's spectral properties are consistent with
random matrices (either uniform, matched-distribution, or symmetric).
"""
import sys
import os
import json
import numpy as np
from scipy import linalg
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.matrix_loader import load_matrix, print_matrix_stats
from lib.statistical_tests import TestReport, empirical_p_value, format_p_value
from lib.control_generator import generate_uniform, generate_symmetric, generate_matched

SEED = 42
N_CONTROLS = 1000
OUTPUT_DIR = Path(__file__).parent
RESULTS_FILE = OUTPUT_DIR / "04_SPECTRAL_ANALYSIS_RESULTS.json"


def spectral_features(matrix):
    """Extract spectral features from a matrix."""
    m = matrix.astype(np.float64)

    # 2D FFT
    fft2d = np.fft.fft2(m)
    magnitude = np.abs(fft2d)

    # Remove DC component for analysis
    mag_no_dc = magnitude.copy()
    mag_no_dc[0, 0] = 0

    # Top-k frequency magnitudes (excluding DC)
    flat_mag = mag_no_dc.flatten()
    top_k_indices = np.argsort(flat_mag)[-20:][::-1]
    top_k_mags = flat_mag[top_k_indices]

    # Dominant frequency (excluding DC)
    dom_idx = np.unravel_index(np.argmax(mag_no_dc), magnitude.shape)
    dom_mag = mag_no_dc[dom_idx]

    # Energy concentration: what fraction of total energy is in top-10 frequencies?
    total_energy = np.sum(mag_no_dc ** 2)
    top10_energy = np.sum(np.sort(flat_mag)[-10:] ** 2)
    energy_concentration = top10_energy / total_energy if total_energy > 0 else 0

    # SVD
    U, S, Vt = linalg.svd(m)
    singular_values = S

    # Effective rank (number of singular values > 1% of max)
    threshold = 0.01 * S[0]
    effective_rank = np.sum(S > threshold)

    # Condition number
    condition_number = S[0] / S[-1] if S[-1] > 0 else np.inf

    # Singular value entropy (normalized)
    s_norm = S / np.sum(S)
    sv_entropy = -np.sum(s_norm * np.log2(s_norm + 1e-15))

    # Eigenvalues (matrix is not symmetric, so eigenvalues may be complex)
    eigenvalues = linalg.eigvals(m)
    spectral_radius = np.max(np.abs(eigenvalues))
    n_real_eigenvalues = np.sum(np.abs(eigenvalues.imag) < 1e-10)

    # Trace (sum of eigenvalues = sum of diagonal)
    trace = np.trace(m)

    # Determinant (via LU decomposition for numerical stability)
    try:
        sign, logdet = np.linalg.slogdet(m)
        log_abs_det = logdet
    except:
        log_abs_det = 0.0

    return {
        "dominant_freq_row": int(dom_idx[0]),
        "dominant_freq_col": int(dom_idx[1]),
        "dominant_magnitude": float(dom_mag),
        "top5_magnitudes": top_k_mags[:5].tolist(),
        "energy_concentration_top10": float(energy_concentration),
        "total_spectral_energy": float(total_energy),
        "effective_rank": int(effective_rank),
        "condition_number": float(condition_number),
        "sv_entropy": float(sv_entropy),
        "top5_singular_values": S[:5].tolist(),
        "singular_value_ratio_1_2": float(S[0] / S[1]) if S[1] > 0 else float("inf"),
        "spectral_radius": float(spectral_radius),
        "n_real_eigenvalues": int(n_real_eigenvalues),
        "trace": float(trace),
        "log_abs_determinant": float(log_abs_det),
    }


def main():
    print("=" * 80)
    print("  PHASE 4: SPECTRAL AND LINEAR ALGEBRA ANALYSIS")
    print("=" * 80)
    print(f"Seed: {SEED} | Controls: {N_CONTROLS}")
    print()

    # Load matrix
    matrix = load_matrix(verify_hash=False)
    print("Anna Matrix:")
    print_matrix_stats(matrix)
    print()

    # Compute Anna features
    print("Computing Anna spectral features...")
    anna_features = spectral_features(matrix)

    print(f"  Dominant frequency: ({anna_features['dominant_freq_row']}, {anna_features['dominant_freq_col']})")
    print(f"  Dominant magnitude: {anna_features['dominant_magnitude']:.1f}")
    print(f"  Energy in top-10 freqs: {anna_features['energy_concentration_top10']*100:.1f}%")
    print(f"  Effective rank: {anna_features['effective_rank']}")
    print(f"  Condition number: {anna_features['condition_number']:.1f}")
    print(f"  SV entropy: {anna_features['sv_entropy']:.3f}")
    print(f"  Spectral radius: {anna_features['spectral_radius']:.1f}")
    print(f"  Real eigenvalues: {anna_features['n_real_eigenvalues']}/128")
    print(f"  Trace: {anna_features['trace']}")
    print(f"  Log|det|: {anna_features['log_abs_determinant']:.2f}")
    print(f"  Top-5 singular values: {[f'{v:.1f}' for v in anna_features['top5_singular_values']]}")
    print()

    # Generate controls
    rng = np.random.default_rng(SEED)

    control_types = {
        "uniform": lambda: generate_uniform(rng),
        "symmetric": lambda: generate_symmetric(rng),
    }

    all_results = {"anna": anna_features}
    report = TestReport("Phase 4: Spectral Analysis", N_CONTROLS, SEED)

    for ctype, gen_fn in control_types.items():
        print(f"\nGenerating {N_CONTROLS} {ctype} control matrices...")
        ctrl_features_list = []
        for i in range(N_CONTROLS):
            ctrl = gen_fn()
            feats = spectral_features(ctrl)
            ctrl_features_list.append(feats)
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{N_CONTROLS}...")

        # Collect control distributions
        ctrl_arrays = {}
        for key in anna_features:
            if isinstance(anna_features[key], (int, float)) and not isinstance(anna_features[key], bool):
                ctrl_arrays[key] = np.array([f[key] for f in ctrl_features_list])

        all_results[ctype] = {
            key: {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "p5": float(np.percentile(arr, 5)),
                "p95": float(np.percentile(arr, 95)),
            }
            for key, arr in ctrl_arrays.items()
        }

        # KEY TESTS
        # Test 1: Effective rank
        report.add_test(
            f"effective_rank_{ctype}",
            f"Anna's effective rank is consistent with {ctype} matrices",
            anna_features["effective_rank"],
            ctrl_arrays["effective_rank"],
            alternative="two-sided",
            unit="dimensions"
        )

        # Test 2: Energy concentration
        report.add_test(
            f"energy_concentration_{ctype}",
            f"Anna's spectral energy concentration is consistent with {ctype} matrices",
            anna_features["energy_concentration_top10"],
            ctrl_arrays["energy_concentration_top10"],
            alternative="greater",
            unit="fraction"
        )

        # Test 3: SV entropy
        report.add_test(
            f"sv_entropy_{ctype}",
            f"Anna's singular value entropy is consistent with {ctype} matrices",
            anna_features["sv_entropy"],
            ctrl_arrays["sv_entropy"],
            alternative="two-sided",
            unit="bits"
        )

        # Test 4: Condition number
        report.add_test(
            f"condition_number_{ctype}",
            f"Anna's condition number is consistent with {ctype} matrices",
            anna_features["condition_number"],
            ctrl_arrays["condition_number"],
            alternative="two-sided"
        )

        # Test 5: Spectral radius
        report.add_test(
            f"spectral_radius_{ctype}",
            f"Anna's spectral radius is consistent with {ctype} matrices",
            anna_features["spectral_radius"],
            ctrl_arrays["spectral_radius"],
            alternative="two-sided"
        )

        # Test 6: Real eigenvalue count
        report.add_test(
            f"n_real_eigenvalues_{ctype}",
            f"Anna's real eigenvalue count is consistent with {ctype} matrices",
            anna_features["n_real_eigenvalues"],
            ctrl_arrays["n_real_eigenvalues"],
            alternative="two-sided"
        )

        # Test 7: Dominant magnitude
        report.add_test(
            f"dominant_magnitude_{ctype}",
            f"Anna's dominant FFT magnitude is consistent with {ctype} matrices",
            anna_features["dominant_magnitude"],
            ctrl_arrays["dominant_magnitude"],
            alternative="greater"
        )

        # Print comparison table
        print(f"\n  --- {ctype.upper()} comparison ---")
        print(f"  {'Feature':<30} {'Anna':>12} {'Ctrl Mean':>12} {'Ctrl Std':>10} {'p-value':>10}")
        print(f"  {'-'*74}")
        for key, arr in sorted(ctrl_arrays.items()):
            anna_val = anna_features[key]
            p = empirical_p_value(anna_val, arr, "two-sided")
            sig = " ***" if p < 0.001 else ""
            print(f"  {key:<30} {anna_val:>12.2f} {np.mean(arr):>12.2f} {np.std(arr):>10.2f} {format_p_value(p):>10}{sig}")

    # Final report
    print()
    report.print_report()

    # Save results
    report.save_json(str(RESULTS_FILE))

    # Also save detailed features
    with open(str(OUTPUT_DIR / "04_SPECTRAL_FEATURES.json"), "w") as f:
        # Convert numpy types to native Python types
        def clean(obj):
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: clean(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [clean(v) for v in obj]
            return obj
        json.dump(clean(all_results), f, indent=2)
    print(f"\nDetailed features saved to 04_SPECTRAL_FEATURES.json")


if __name__ == "__main__":
    main()
