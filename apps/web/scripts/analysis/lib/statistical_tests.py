"""
Statistical Testing Utilities - p-values, Bonferroni correction, reporting.
"""
import json
import numpy as np
from datetime import datetime


def empirical_p_value(observed, control_values, alternative="greater"):
    """Compute empirical p-value from control distribution.

    Args:
        observed: The observed value from Anna matrix
        control_values: Array of values from control matrices
        alternative: "greater" (Anna > controls), "less" (Anna < controls), "two-sided"

    Returns:
        p-value (float)
    """
    n = len(control_values)
    if n == 0:
        return 1.0

    if alternative == "greater":
        return (np.sum(control_values >= observed) + 1) / (n + 1)
    elif alternative == "less":
        return (np.sum(control_values <= observed) + 1) / (n + 1)
    elif alternative == "two-sided":
        p_greater = (np.sum(control_values >= observed) + 1) / (n + 1)
        p_less = (np.sum(control_values <= observed) + 1) / (n + 1)
        return min(2 * min(p_greater, p_less), 1.0)
    else:
        raise ValueError(f"Unknown alternative: {alternative}")


def bonferroni_threshold(alpha, n_tests):
    """Compute Bonferroni-corrected significance threshold."""
    return alpha / n_tests


def format_p_value(p):
    """Format p-value for display."""
    if p == 0.0:
        return "< 1e-4 (0 in simulation)"
    elif p < 0.0001:
        return f"{p:.2e}"
    elif p < 0.01:
        return f"{p:.4f}"
    else:
        return f"{p:.3f}"


def significance_label(p, threshold):
    """Return significance label."""
    if p < threshold:
        return "SIGNIFICANT"
    else:
        return "NOT SIGNIFICANT"


class TestReport:
    """Collects test results and produces formatted output + JSON."""

    def __init__(self, title, n_controls, seed, alpha=0.001):
        self.title = title
        self.n_controls = n_controls
        self.seed = seed
        self.alpha = alpha
        self.tests = []
        self.timestamp = datetime.now().isoformat()

    def add_test(self, name, null_hypothesis, observed, control_values,
                 alternative="two-sided", unit=""):
        """Add a test result."""
        p = empirical_p_value(observed, control_values, alternative)
        threshold = bonferroni_threshold(self.alpha, max(len(self.tests) + 1, 1))

        result = {
            "name": name,
            "null_hypothesis": null_hypothesis,
            "observed": float(observed),
            "control_mean": float(np.mean(control_values)),
            "control_std": float(np.std(control_values)),
            "control_min": float(np.min(control_values)),
            "control_max": float(np.max(control_values)),
            "control_p5": float(np.percentile(control_values, 5)),
            "control_p95": float(np.percentile(control_values, 95)),
            "p_value": float(p),
            "alternative": alternative,
            "unit": unit,
        }
        self.tests.append(result)
        return result

    def finalize(self):
        """Finalize all tests with Bonferroni correction."""
        n_tests = len(self.tests)
        threshold = bonferroni_threshold(self.alpha, n_tests) if n_tests > 0 else self.alpha

        for t in self.tests:
            t["bonferroni_threshold"] = threshold
            t["significant"] = t["p_value"] < threshold
            t["result"] = significance_label(t["p_value"], threshold)

    def print_report(self):
        """Print formatted text report."""
        self.finalize()
        n_tests = len(self.tests)
        threshold = bonferroni_threshold(self.alpha, n_tests) if n_tests > 0 else self.alpha

        print("=" * 80)
        print(f"  {self.title}")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print(f"Controls: {self.n_controls} | Seed: {self.seed}")
        print(f"Alpha: {self.alpha} | Tests: {n_tests} | Bonferroni threshold: {threshold:.6f}")
        print("-" * 80)

        sig_count = 0
        for i, t in enumerate(self.tests, 1):
            marker = "***" if t["significant"] else "   "
            print(f"\n{marker} Test {i}: {t['name']}")
            print(f"    H0: {t['null_hypothesis']}")
            print(f"    Anna:    {t['observed']:.4f} {t['unit']}")
            print(f"    Control: mean={t['control_mean']:.4f} std={t['control_std']:.4f} "
                  f"[{t['control_min']:.4f}, {t['control_max']:.4f}]")
            print(f"    p-value: {format_p_value(t['p_value'])} -> {t['result']}")
            if t["significant"]:
                sig_count += 1

        print("\n" + "=" * 80)
        print(f"SUMMARY: {sig_count}/{n_tests} tests significant after Bonferroni correction")
        print("=" * 80)

    def save_json(self, path):
        """Save results as JSON."""
        self.finalize()
        output = {
            "title": self.title,
            "timestamp": self.timestamp,
            "n_controls": self.n_controls,
            "seed": self.seed,
            "alpha": self.alpha,
            "n_tests": len(self.tests),
            "bonferroni_threshold": bonferroni_threshold(self.alpha, len(self.tests)),
            "tests": {t["name"]: t for t in self.tests},
        }
        with open(path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {path}")
