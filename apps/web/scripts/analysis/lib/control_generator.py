"""
Control Matrix Generator - Generate comparison matrices for statistical testing.

Three types of control matrices:
1. UNIFORM: Random integers -128 to 127 (null hypothesis: completely random)
2. MATCHED: Same value distribution as Anna (shuffle all values)
3. SYMMETRIC: Random values with imposed point symmetry (matrix[r,c] + matrix[127-r,127-c] = -1)
"""
import numpy as np


def generate_uniform(rng, shape=(128, 128)):
    """Type 1: Uniform random signed bytes."""
    return rng.integers(-128, 128, size=shape, dtype=np.int64)


def generate_matched(rng, anna_matrix):
    """Type 2: Shuffle all Anna values (preserves exact distribution)."""
    flat = anna_matrix.flatten().copy()
    rng.shuffle(flat)
    return flat.reshape(anna_matrix.shape)


def generate_symmetric(rng, shape=(128, 128)):
    """Type 3: Random with imposed point symmetry (matrix[r,c] + matrix[127-r,127-c] = -1).

    This is the most important control - it tests whether observed properties
    are simply consequences of the symmetry rule.
    """
    n = shape[0]
    matrix = np.zeros(shape, dtype=np.int64)

    # Fill the "upper" half (including diagonal and center)
    for r in range(n):
        for c in range(n):
            r2, c2 = n - 1 - r, n - 1 - c
            if (r, c) < (r2, c2):
                # This is the independent cell
                val = rng.integers(-128, 128)
                matrix[r, c] = val
                matrix[r2, c2] = -1 - val
            elif (r, c) == (r2, c2):
                # Center cell(s) - for 128x128 there is no exact center
                # But diagonal cells where r=c and r2=c2: only when r=63.5 (impossible for int)
                # For even dimensions, all cells have a distinct mirror partner
                pass

    # Handle the exact center if n is odd (not applicable for 128)
    return matrix


def generate_controls(n_controls, anna_matrix, control_type="all", seed=42):
    """Generate a list of control matrices.

    Args:
        n_controls: Number of control matrices to generate
        anna_matrix: The real Anna matrix (needed for type 2)
        control_type: "uniform", "matched", "symmetric", or "all"
        seed: Random seed for reproducibility

    Returns:
        dict mapping type name -> list of matrices
    """
    rng = np.random.default_rng(seed)
    controls = {}

    if control_type in ("uniform", "all"):
        controls["uniform"] = [generate_uniform(rng) for _ in range(n_controls)]

    if control_type in ("matched", "all"):
        controls["matched"] = [generate_matched(rng, anna_matrix) for _ in range(n_controls)]

    if control_type in ("symmetric", "all"):
        controls["symmetric"] = [generate_symmetric(rng) for _ in range(n_controls)]

    return controls
