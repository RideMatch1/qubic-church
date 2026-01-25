#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    STATISTICAL DEEP DIVE ANALYSIS                              ║
║                                                                                ║
║  Analyze statistical anomalies in the Anna Matrix:                            ║
║  - -27 vs +27 distribution                                                    ║
║  - CFB number clustering                                                      ║
║  - Sign asymmetries                                                           ║
║  - Positional correlations                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
import statistics

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "public" / "data"
MATRIX_FILE = DATA_DIR / "anna-matrix.json"

CFB_NUMBERS = {27, 37, 42, 127}
CFB_SIGNED = {27, -27, 37, -37, 42, -42, 127, -127}

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def load_matrix() -> List[List[int]]:
    """Load Anna Matrix and convert any string values to integers"""
    with open(MATRIX_FILE, 'r') as f:
        data = json.load(f)

    # Convert any string values to integers (some cells contain '00000000')
    matrix = []
    for row in data['matrix']:
        clean_row = []
        for v in row:
            if isinstance(v, str):
                clean_row.append(0)  # Treat string markers as 0
            else:
                clean_row.append(int(v))
        matrix.append(clean_row)
    return matrix

class StatisticalAnalyzer:
    def __init__(self):
        print("═" * 70)
        print("           STATISTICAL DEEP DIVE ANALYSIS")
        print("═" * 70)
        self.matrix = load_matrix()
        self.flat_values = [v for row in self.matrix for v in row]
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'sign_analysis': {},
            'cfb_distribution': {},
            'positional_analysis': {},
            'clustering': {},
            'anomalies': [],
            'statistical_summary': {},
        }

    def get_value(self, row: int, col: int) -> int:
        return self.matrix[row % 128][col % 128]

    def analyze_sign_asymmetry(self):
        """Analyze the distribution of positive vs negative values"""
        print("\n" + "─" * 70)
        print("SIGN ASYMMETRY ANALYSIS")
        print("─" * 70)

        positive = sum(1 for v in self.flat_values if v > 0)
        negative = sum(1 for v in self.flat_values if v < 0)
        zero = sum(1 for v in self.flat_values if v == 0)
        total = len(self.flat_values)

        print(f"\n  Total cells: {total}")
        print(f"  Positive values: {positive} ({positive/total*100:.2f}%)")
        print(f"  Negative values: {negative} ({negative/total*100:.2f}%)")
        print(f"  Zero values: {zero} ({zero/total*100:.2f}%)")

        # Expected: 50% positive, 50% negative (uniform -128 to 127)
        expected_positive = total * 127 / 256
        expected_negative = total * 128 / 256

        pos_deviation = (positive - expected_positive) / expected_positive * 100
        neg_deviation = (negative - expected_negative) / expected_negative * 100

        print(f"\n  Deviation from expected:")
        print(f"    Positive: {pos_deviation:+.2f}%")
        print(f"    Negative: {neg_deviation:+.2f}%")

        # Analyze specific CFB pairs
        print("\n  CFB Number Pairs (+/-) Analysis:")
        for cfb in sorted(CFB_NUMBERS):
            pos_count = sum(1 for v in self.flat_values if v == cfb)
            neg_count = sum(1 for v in self.flat_values if v == -cfb)
            ratio = pos_count / neg_count if neg_count > 0 else float('inf')

            expected_each = total / 256  # uniform distribution
            pos_anomaly = (pos_count - expected_each) / expected_each * 100 if expected_each > 0 else 0
            neg_anomaly = (neg_count - expected_each) / expected_each * 100 if expected_each > 0 else 0

            print(f"    {cfb:+4d}: {pos_count:4d} occurrences ({pos_anomaly:+.1f}% from expected)")
            print(f"    {-cfb:+4d}: {neg_count:4d} occurrences ({neg_anomaly:+.1f}% from expected)")
            print(f"          Ratio +/-: {ratio:.3f}")

            if ratio > 1.5 or ratio < 0.67:
                self.results['anomalies'].append({
                    'type': 'sign_imbalance',
                    'value': cfb,
                    'positive_count': pos_count,
                    'negative_count': neg_count,
                    'ratio': ratio,
                })

        self.results['sign_analysis'] = {
            'positive': positive,
            'negative': negative,
            'zero': zero,
            'positive_deviation': pos_deviation,
            'negative_deviation': neg_deviation,
        }

    def analyze_cfb_distribution(self):
        """Analyze spatial distribution of CFB numbers"""
        print("\n" + "─" * 70)
        print("CFB NUMBER DISTRIBUTION ANALYSIS")
        print("─" * 70)

        cfb_positions = defaultdict(list)

        for r in range(128):
            for c in range(128):
                v = self.get_value(r, c)
                if abs(v) in CFB_NUMBERS:
                    cfb_positions[v].append((r, c))

        print("\n  CFB Number Positions:")
        for v in sorted(cfb_positions.keys()):
            positions = cfb_positions[v]
            print(f"\n    Value {v:+4d}: {len(positions)} occurrences")

            if positions:
                # Calculate centroid
                avg_row = sum(p[0] for p in positions) / len(positions)
                avg_col = sum(p[1] for p in positions) / len(positions)

                # Calculate spread (standard deviation)
                if len(positions) > 1:
                    row_std = statistics.stdev(p[0] for p in positions)
                    col_std = statistics.stdev(p[1] for p in positions)
                else:
                    row_std = col_std = 0

                print(f"      Centroid: ({avg_row:.1f}, {avg_col:.1f})")
                print(f"      Spread (std): row={row_std:.1f}, col={col_std:.1f}")

                # Quadrant distribution
                quadrants = {'NW': 0, 'NE': 0, 'SW': 0, 'SE': 0}
                for r, c in positions:
                    if r < 64 and c < 64: quadrants['NW'] += 1
                    elif r < 64: quadrants['NE'] += 1
                    elif c < 64: quadrants['SW'] += 1
                    else: quadrants['SE'] += 1

                print(f"      Quadrants: {dict(quadrants)}")

                # Check for clustering (are positions closer together than expected?)
                if len(positions) >= 3:
                    distances = []
                    for i, p1 in enumerate(positions[:20]):  # Sample first 20
                        for p2 in positions[i+1:21]:
                            d = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                            distances.append(d)

                    if distances:
                        avg_dist = sum(distances) / len(distances)
                        # Expected average distance for random uniform: ~60 for 128x128
                        expected_dist = 60
                        clustering = (expected_dist - avg_dist) / expected_dist * 100
                        print(f"      Avg distance: {avg_dist:.1f} (clustering: {clustering:+.1f}%)")

                        if abs(clustering) > 30:
                            self.results['anomalies'].append({
                                'type': 'spatial_clustering',
                                'value': v,
                                'avg_distance': avg_dist,
                                'clustering_percent': clustering,
                            })

        self.results['cfb_distribution'] = {
            str(k): {
                'count': len(v),
                'positions_sample': v[:10],
            } for k, v in cfb_positions.items()
        }

    def analyze_positional_correlations(self):
        """Find correlations between position and value"""
        print("\n" + "─" * 70)
        print("POSITIONAL CORRELATION ANALYSIS")
        print("─" * 70)

        # 1. Row-based analysis
        print("\n  [1] Row-based value averages:")
        row_avgs = []
        for r in range(128):
            avg = sum(self.matrix[r]) / 128
            row_avgs.append(avg)
            if abs(avg) > 10:  # Significant deviation from 0
                print(f"      Row {r}: avg = {avg:.2f}")

        # Find rows with extreme averages
        if row_avgs:
            max_row = row_avgs.index(max(row_avgs))
            min_row = row_avgs.index(min(row_avgs))
            print(f"\n      Most positive row: {max_row} (avg: {max(row_avgs):.2f})")
            print(f"      Most negative row: {min_row} (avg: {min(row_avgs):.2f})")

        # 2. Column-based analysis
        print("\n  [2] Column-based analysis:")
        col_avgs = []
        for c in range(128):
            avg = sum(self.matrix[r][c] for r in range(128)) / 128
            col_avgs.append(avg)

        max_col = col_avgs.index(max(col_avgs))
        min_col = col_avgs.index(min(col_avgs))
        print(f"      Most positive col: {max_col} (avg: {max(col_avgs):.2f})")
        print(f"      Most negative col: {min_col} (avg: {min(col_avgs):.2f})")

        # 3. Diagonal analysis
        print("\n  [3] Diagonal analysis:")
        main_diag = [self.matrix[i][i] for i in range(128)]
        anti_diag = [self.matrix[i][127-i] for i in range(128)]

        main_avg = sum(main_diag) / 128
        anti_avg = sum(anti_diag) / 128
        print(f"      Main diagonal avg: {main_avg:.2f}")
        print(f"      Anti-diagonal avg: {anti_avg:.2f}")

        # CFB values on diagonals
        main_cfb = [v for v in main_diag if abs(v) in CFB_NUMBERS]
        anti_cfb = [v for v in anti_diag if abs(v) in CFB_NUMBERS]
        print(f"      CFB on main diagonal: {len(main_cfb)} values")
        print(f"      CFB on anti-diagonal: {len(anti_cfb)} values")

        # 4. Distance from center correlation
        print("\n  [4] Distance from center correlation:")
        center = (64, 64)
        distance_value_pairs = []
        for r in range(128):
            for c in range(128):
                d = math.sqrt((r - center[0])**2 + (c - center[1])**2)
                v = self.matrix[r][c]
                distance_value_pairs.append((d, v))

        # Calculate correlation coefficient
        n = len(distance_value_pairs)
        sum_d = sum(p[0] for p in distance_value_pairs)
        sum_v = sum(p[1] for p in distance_value_pairs)
        sum_dv = sum(p[0] * p[1] for p in distance_value_pairs)
        sum_d2 = sum(p[0]**2 for p in distance_value_pairs)
        sum_v2 = sum(p[1]**2 for p in distance_value_pairs)

        numerator = n * sum_dv - sum_d * sum_v
        denominator = math.sqrt((n * sum_d2 - sum_d**2) * (n * sum_v2 - sum_v**2))

        if denominator > 0:
            correlation = numerator / denominator
            print(f"      Distance-value correlation: {correlation:.4f}")
            if abs(correlation) > 0.1:
                self.results['anomalies'].append({
                    'type': 'distance_correlation',
                    'correlation': correlation,
                })
        else:
            print(f"      Distance-value correlation: undefined")

        self.results['positional_analysis'] = {
            'extreme_row_positive': max_row,
            'extreme_row_negative': min_row,
            'extreme_col_positive': max_col,
            'extreme_col_negative': min_col,
            'main_diagonal_avg': main_avg,
            'anti_diagonal_avg': anti_avg,
            'main_diagonal_cfb_count': len(main_cfb),
            'anti_diagonal_cfb_count': len(anti_cfb),
        }

    def analyze_value_clustering(self):
        """Analyze how values cluster spatially"""
        print("\n" + "─" * 70)
        print("VALUE CLUSTERING ANALYSIS")
        print("─" * 70)

        # 1. Same-value neighbor analysis
        print("\n  [1] Same-value neighbor frequency:")
        same_neighbors = 0
        total_checks = 0

        for r in range(128):
            for c in range(127):  # Horizontal neighbors
                if self.matrix[r][c] == self.matrix[r][c+1]:
                    same_neighbors += 1
                total_checks += 1

        for r in range(127):
            for c in range(128):  # Vertical neighbors
                if self.matrix[r][c] == self.matrix[r+1][c]:
                    same_neighbors += 1
                total_checks += 1

        same_ratio = same_neighbors / total_checks * 100
        expected_ratio = 100 / 256  # If uniform random
        print(f"      Same-value neighbors: {same_neighbors} ({same_ratio:.3f}%)")
        print(f"      Expected (uniform): {expected_ratio:.3f}%")
        print(f"      Clustering factor: {same_ratio / expected_ratio:.2f}x")

        # 2. Sign persistence (runs of same sign)
        print("\n  [2] Sign persistence analysis:")
        sign_runs = []
        for r in range(128):
            run_length = 1
            current_sign = self.matrix[r][0] >= 0
            for c in range(1, 128):
                new_sign = self.matrix[r][c] >= 0
                if new_sign == current_sign:
                    run_length += 1
                else:
                    sign_runs.append(run_length)
                    run_length = 1
                    current_sign = new_sign
            sign_runs.append(run_length)

        avg_run = sum(sign_runs) / len(sign_runs)
        max_run = max(sign_runs)
        print(f"      Average sign run length: {avg_run:.2f}")
        print(f"      Maximum sign run: {max_run}")
        # Expected for 50/50 coin flip: average run = 2
        print(f"      Persistence factor: {avg_run / 2:.2f}x expected")

        # 3. CFB neighbor analysis (are CFB values near each other?)
        print("\n  [3] CFB neighbor proximity:")
        cfb_positions = []
        for r in range(128):
            for c in range(128):
                if abs(self.matrix[r][c]) in CFB_NUMBERS:
                    cfb_positions.append((r, c))

        # Count CFB values with CFB neighbors
        cfb_with_cfb_neighbor = 0
        for r, c in cfb_positions:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = (r + dr) % 128, (c + dc) % 128
                if abs(self.matrix[nr][nc]) in CFB_NUMBERS:
                    cfb_with_cfb_neighbor += 1
                    break

        cfb_neighbor_rate = cfb_with_cfb_neighbor / len(cfb_positions) * 100 if cfb_positions else 0
        cfb_density = len(cfb_positions) / 16384 * 100
        expected_neighbor = cfb_density * 4  # 4 neighbors, each has cfb_density% chance

        print(f"      CFB values: {len(cfb_positions)} ({cfb_density:.2f}% of matrix)")
        print(f"      CFB with CFB neighbor: {cfb_with_cfb_neighbor} ({cfb_neighbor_rate:.2f}%)")
        print(f"      Expected (random): {expected_neighbor:.2f}%")

        if cfb_neighbor_rate > expected_neighbor * 1.5:
            self.results['anomalies'].append({
                'type': 'cfb_clustering',
                'observed_rate': cfb_neighbor_rate,
                'expected_rate': expected_neighbor,
            })

        self.results['clustering'] = {
            'same_neighbor_ratio': same_ratio,
            'clustering_factor': same_ratio / expected_ratio,
            'avg_sign_run': avg_run,
            'max_sign_run': max_run,
            'cfb_neighbor_rate': cfb_neighbor_rate,
        }

    def compute_summary_statistics(self):
        """Compute overall statistical summary"""
        print("\n" + "─" * 70)
        print("STATISTICAL SUMMARY")
        print("─" * 70)

        mean = sum(self.flat_values) / len(self.flat_values)
        median = sorted(self.flat_values)[len(self.flat_values) // 2]
        std_dev = statistics.stdev(self.flat_values)

        # Mode
        value_counts = Counter(self.flat_values)
        mode = value_counts.most_common(1)[0]

        # Skewness (simplified)
        n = len(self.flat_values)
        skewness = sum((v - mean)**3 for v in self.flat_values) / (n * std_dev**3) if std_dev > 0 else 0

        # Kurtosis
        kurtosis = sum((v - mean)**4 for v in self.flat_values) / (n * std_dev**4) - 3 if std_dev > 0 else 0

        print(f"\n  Mean: {mean:.4f}")
        print(f"  Median: {median}")
        print(f"  Mode: {mode[0]} (appears {mode[1]} times)")
        print(f"  Std Dev: {std_dev:.4f}")
        print(f"  Skewness: {skewness:.4f} ({'right-skewed' if skewness > 0.1 else 'left-skewed' if skewness < -0.1 else 'symmetric'})")
        print(f"  Kurtosis: {kurtosis:.4f} ({'heavy tails' if kurtosis > 0 else 'light tails'})")

        # Value range analysis
        print(f"\n  Value range: {min(self.flat_values)} to {max(self.flat_values)}")
        print(f"  Unique values: {len(set(self.flat_values))}")

        # CFB numbers relative frequency
        print("\n  CFB Number Frequencies:")
        for cfb in sorted(CFB_NUMBERS):
            count = sum(1 for v in self.flat_values if abs(v) == cfb)
            expected = 16384 * 2 / 256  # 2 values (+ and -) out of 256 possible
            deviation = (count - expected) / expected * 100
            print(f"    |{cfb}|: {count} occurrences ({deviation:+.1f}% from expected)")

        self.results['statistical_summary'] = {
            'mean': mean,
            'median': median,
            'mode': mode[0],
            'mode_count': mode[1],
            'std_dev': std_dev,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'unique_values': len(set(self.flat_values)),
        }

    def run(self):
        """Run full statistical analysis"""
        self.analyze_sign_asymmetry()
        self.analyze_cfb_distribution()
        self.analyze_positional_correlations()
        self.analyze_value_clustering()
        self.compute_summary_statistics()

        # Summary
        print("\n" + "═" * 70)
        print("STATISTICAL ANALYSIS SUMMARY")
        print("═" * 70)

        print(f"\n  Anomalies detected: {len(self.results['anomalies'])}")
        for anomaly in self.results['anomalies']:
            print(f"    - {anomaly['type']}")

        # Save results
        output_file = SCRIPT_DIR / 'STATISTICAL_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n  Results saved to: {output_file}")

        return self.results

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    analyzer = StatisticalAnalyzer()
    analyzer.run()
