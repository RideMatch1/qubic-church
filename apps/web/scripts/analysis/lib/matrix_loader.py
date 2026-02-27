"""
Matrix Loader - Load and validate the Anna Matrix
"""
import json
import hashlib
import numpy as np
from pathlib import Path

MATRIX_PATH = Path(__file__).parent.parent.parent / "public" / "data" / "anna-matrix.json"
# Fallback relative path
MATRIX_PATH_ALT = Path(__file__).parent.parent.parent.parent / "public" / "data" / "anna-matrix.json"

EXPECTED_SHA256 = "2729903368e8735fdaeb0780765efd0f38396a2c0a5cbdccf4e23dd2adc7b19d"


def load_matrix(verify_hash=True):
    """Load the Anna Matrix from JSON. Returns numpy int64 array (128x128)."""
    path = MATRIX_PATH if MATRIX_PATH.exists() else MATRIX_PATH_ALT
    if not path.exists():
        # Try finding it relative to CWD
        candidates = list(Path(".").rglob("anna-matrix.json"))
        if candidates:
            path = candidates[0]
        else:
            raise FileNotFoundError(f"anna-matrix.json not found. Tried {MATRIX_PATH}")

    with open(path, "r") as f:
        raw = f.read()
        data = json.loads(raw)

    def safe_int(v):
        if v is None:
            return 0
        if isinstance(v, (int, float)):
            return int(v)
        return 0

    matrix = np.array(
        [[safe_int(v) for v in row] for row in data["matrix"]],
        dtype=np.int64
    )

    assert matrix.shape == (128, 128), f"Expected 128x128, got {matrix.shape}"

    if verify_hash:
        h = hashlib.sha256(raw.encode()).hexdigest()
        # Don't fail on hash mismatch, just warn
        if h != EXPECTED_SHA256:
            print(f"WARNING: Matrix hash mismatch. Got {h}, expected {EXPECTED_SHA256}")
            print("File may have been modified or reformatted.")

    return matrix


def get_diagonal(matrix, start=0, end=26):
    """Extract diagonal values from matrix[i][i] for i in [start, end)."""
    return np.array([matrix[i, i] for i in range(start, end)])


def print_matrix_stats(matrix):
    """Print basic matrix statistics."""
    print(f"Shape: {matrix.shape}")
    print(f"Min: {matrix.min()}, Max: {matrix.max()}")
    print(f"Sum: {matrix.sum()}")
    print(f"Positive: {(matrix > 0).sum()} ({(matrix > 0).mean()*100:.1f}%)")
    print(f"Negative: {(matrix < 0).sum()} ({(matrix < 0).mean()*100:.1f}%)")
    print(f"Zeros: {(matrix == 0).sum()}")
    print(f"Unique values: {len(np.unique(matrix))}")
