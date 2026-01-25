#!/usr/bin/env python3
"""
===============================================================================
            FFT FREQUENCY ANALYSIS - PURE DATA
===============================================================================
Look for periodic patterns in rows and columns using FFT.
NO interpretation - only report dominant frequencies and compare to baseline.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent

print("=" * 80)
print("           FFT FREQUENCY ANALYSIS")
print("           Looking for periodic patterns")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]], dtype=np.float64)

# ==============================================================================
# ROW FFT ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("ROW FFT ANALYSIS")
print("=" * 80)

row_dominant_freqs = []

for r in range(128):
    row = matrix[r, :]

    # Compute FFT
    fft = np.fft.fft(row)
    magnitudes = np.abs(fft[:64])  # First half (Nyquist)

    # Find dominant frequency (excluding DC component at index 0)
    dominant_idx = np.argmax(magnitudes[1:]) + 1
    dominant_mag = magnitudes[dominant_idx]

    row_dominant_freqs.append({
        "row": r,
        "dominant_freq_idx": int(dominant_idx),
        "dominant_magnitude": float(dominant_mag),
        "dc_component": float(magnitudes[0]),
    })

# Statistics on dominant frequencies
freq_counts = {}
for rf in row_dominant_freqs:
    idx = rf["dominant_freq_idx"]
    freq_counts[idx] = freq_counts.get(idx, 0) + 1

print(f"\n  Dominant frequency distribution across rows:")
for freq_idx in sorted(freq_counts.keys(), key=lambda x: freq_counts[x], reverse=True)[:10]:
    count = freq_counts[freq_idx]
    period = 128 / freq_idx if freq_idx > 0 else "∞"
    print(f"    Freq idx {freq_idx:3} (period≈{period if isinstance(period, str) else f'{period:.1f}':5}): {count:3} rows")

# ==============================================================================
# COLUMN FFT ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("COLUMN FFT ANALYSIS")
print("=" * 80)

col_dominant_freqs = []

for c in range(128):
    col = matrix[:, c]

    fft = np.fft.fft(col)
    magnitudes = np.abs(fft[:64])

    dominant_idx = np.argmax(magnitudes[1:]) + 1
    dominant_mag = magnitudes[dominant_idx]

    col_dominant_freqs.append({
        "col": c,
        "dominant_freq_idx": int(dominant_idx),
        "dominant_magnitude": float(dominant_mag),
        "dc_component": float(magnitudes[0]),
    })

freq_counts_col = {}
for cf in col_dominant_freqs:
    idx = cf["dominant_freq_idx"]
    freq_counts_col[idx] = freq_counts_col.get(idx, 0) + 1

print(f"\n  Dominant frequency distribution across columns:")
for freq_idx in sorted(freq_counts_col.keys(), key=lambda x: freq_counts_col[x], reverse=True)[:10]:
    count = freq_counts_col[freq_idx]
    period = 128 / freq_idx if freq_idx > 0 else "∞"
    print(f"    Freq idx {freq_idx:3} (period≈{period if isinstance(period, str) else f'{period:.1f}':5}): {count:3} cols")

# ==============================================================================
# 2D FFT OF ENTIRE MATRIX
# ==============================================================================
print("\n" + "=" * 80)
print("2D FFT OF ENTIRE MATRIX")
print("=" * 80)

fft_2d = np.fft.fft2(matrix)
magnitude_2d = np.abs(fft_2d)

# Find top 10 frequency components (excluding DC)
flat_mag = magnitude_2d.copy()
flat_mag[0, 0] = 0  # Zero out DC

# Get indices of top magnitudes
flat_indices = np.argsort(flat_mag.flatten())[::-1][:20]
top_freqs_2d = []

for idx in flat_indices:
    row_freq = idx // 128
    col_freq = idx % 128
    mag = flat_mag[row_freq, col_freq]

    # Convert to more interpretable form
    row_period = 128 / row_freq if row_freq > 0 else float('inf')
    col_period = 128 / col_freq if col_freq > 0 else float('inf')

    top_freqs_2d.append({
        "row_freq": int(row_freq),
        "col_freq": int(col_freq),
        "magnitude": float(mag),
        "row_period": row_period if row_period != float('inf') else "∞",
        "col_period": col_period if col_period != float('inf') else "∞",
    })

print(f"\n  Top 10 2D frequency components:")
print(f"  {'Row Freq':10} {'Col Freq':10} {'Magnitude':12} {'Row Period':12} {'Col Period':12}")
print("  " + "-" * 60)
for f in top_freqs_2d[:10]:
    rp = f['row_period'] if isinstance(f['row_period'], str) else f"{f['row_period']:.1f}"
    cp = f['col_period'] if isinstance(f['col_period'], str) else f"{f['col_period']:.1f}"
    print(f"  {f['row_freq']:10} {f['col_freq']:10} {f['magnitude']:12.1f} {rp:12} {cp:12}")

# ==============================================================================
# COMPARE TO RANDOM MATRIX
# ==============================================================================
print("\n" + "=" * 80)
print("BASELINE: RANDOM MATRIX COMPARISON")
print("=" * 80)

# Generate random matrix with same value range
random_matrix = np.random.randint(-128, 128, size=(128, 128)).astype(np.float64)

random_fft_2d = np.fft.fft2(random_matrix)
random_mag_2d = np.abs(random_fft_2d)
random_mag_2d[0, 0] = 0

# Compare peak magnitudes
anna_max = np.max(flat_mag)
random_max = np.max(random_mag_2d)

# Compare mean of top 10
anna_top10_mean = np.mean([f["magnitude"] for f in top_freqs_2d[:10]])

random_flat = random_mag_2d.flatten()
random_top10 = np.sort(random_flat)[::-1][:10]
random_top10_mean = np.mean(random_top10)

print(f"\n  Peak magnitude comparison:")
print(f"    Anna matrix max: {anna_max:.1f}")
print(f"    Random matrix max: {random_max:.1f}")
print(f"    Ratio: {anna_max/random_max:.2f}x")

print(f"\n  Top 10 mean magnitude:")
print(f"    Anna matrix: {anna_top10_mean:.1f}")
print(f"    Random matrix: {random_top10_mean:.1f}")
print(f"    Ratio: {anna_top10_mean/random_top10_mean:.2f}x")

# ==============================================================================
# SYMMETRY IN FREQUENCY DOMAIN
# ==============================================================================
print("\n" + "=" * 80)
print("FREQUENCY DOMAIN SYMMETRY")
print("=" * 80)

# Check if FFT has special symmetry properties
# For real symmetric matrices, FFT should show specific patterns

# Check conjugate symmetry (should be true for real input)
conjugate_diff = np.mean(np.abs(fft_2d - np.conj(fft_2d[::-1, ::-1])))
print(f"\n  Conjugate symmetry error: {conjugate_diff:.6f}")

# Check for point symmetry in magnitude
mag_sym_error = np.mean(np.abs(magnitude_2d - magnitude_2d[::-1, ::-1]))
print(f"  Magnitude point symmetry error: {mag_sym_error:.6f}")

# ==============================================================================
# SPECIFIC FREQUENCY ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("SPECIFIC FREQUENCIES OF INTEREST")
print("=" * 80)

# Check frequencies that might relate to known patterns
# Period 2 (alternating), Period 4, Period 8, etc.
specific_periods = [2, 4, 8, 16, 32, 64]

print(f"\n  Magnitude at specific periods:")
for period in specific_periods:
    freq_idx = 128 // period
    row_mag = np.mean([magnitude_2d[freq_idx, c] for c in range(128)])
    col_mag = np.mean([magnitude_2d[r, freq_idx] for r in range(128)])
    print(f"    Period {period:2}: Row avg mag = {row_mag:.1f}, Col avg mag = {col_mag:.1f}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("FFT ANALYSIS COMPLETE")
print("=" * 80)

# Check if any frequency is significantly above random
significant_freqs = [f for f in top_freqs_2d if f["magnitude"] > random_max * 1.5]

print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         FFT SUMMARY                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  2D FFT RESULTS:                                                              ║
║  • Peak magnitude: {anna_max:.1f}                                                ║
║  • Random baseline peak: {random_max:.1f}                                        ║
║  • Ratio: {anna_max/random_max:.2f}x                                                          ║
║                                                                               ║
║  FREQUENCY DOMAIN SYMMETRY:                                                   ║
║  • Conjugate symmetry error: {conjugate_diff:.6f}                                  ║
║  • Magnitude point symmetry error: {mag_sym_error:.6f}                             ║
║                                                                               ║
║  SIGNIFICANT FREQUENCIES (>1.5x random):                                      ║
║  • Count: {len(significant_freqs)}                                                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "row_analysis": {
        "dominant_freq_distribution": freq_counts,
    },
    "col_analysis": {
        "dominant_freq_distribution": freq_counts_col,
    },
    "fft_2d": {
        "top_frequencies": top_freqs_2d,
        "peak_magnitude": anna_max,
        "random_baseline_peak": random_max,
        "ratio": anna_max / random_max,
    },
    "symmetry": {
        "conjugate_error": conjugate_diff,
        "magnitude_point_symmetry_error": mag_sym_error,
    },
    "significant_frequencies": significant_freqs,
}

output_path = script_dir / "FFT_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"✓ Results saved: {output_path}")
