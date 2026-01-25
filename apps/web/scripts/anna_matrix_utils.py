#!/usr/bin/env python3
"""
Anna Matrix Utilities
=====================

Shared utility functions for Anna Matrix coordinate transformations.

IMPORTANT: This module contains the CORRECT coordinate transformation formula.
All other scripts should import from here to ensure consistency.

Coordinate System:
- Anna X: -64 to 63 (horizontal axis)
- Anna Y: 63 to -64 (vertical axis, top to bottom)
- Matrix: 128x128 array (row 0-127, col 0-127)

Transformation:
- col = (X + 64) % 128   # Maps X: -64..63 to col: 0..127
- row = (63 - Y) % 128   # Maps Y: 63..-64 to row: 0..127
- value = matrix[row][col]

Example:
- Anna(6, 33) -> col=70, row=30 -> matrix[30][70] = -93
- Anna(0, 0)  -> col=64, row=63 -> matrix[63][64] = -40 (VOID)

Author: qubic-academic-docs
Date: 2026-01-16
"""

import json
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any, Union


def anna_to_matrix(x: int, y: int) -> Tuple[int, int]:
    """
    Convert Anna coordinates (x, y) to matrix indices (row, col).

    Args:
        x: Anna X coordinate (-64 to 63, but accepts any int with wrapping)
        y: Anna Y coordinate (63 to -64, but accepts any int with wrapping)

    Returns:
        Tuple of (row, col) for matrix indexing: matrix[row][col]

    Example:
        >>> row, col = anna_to_matrix(6, 33)
        >>> print(f"matrix[{row}][{col}]")  # matrix[30][70]
    """
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col


def matrix_to_anna(row: int, col: int) -> Tuple[int, int]:
    """
    Convert matrix indices (row, col) to Anna coordinates (x, y).

    Args:
        row: Matrix row index (0-127)
        col: Matrix column index (0-127)

    Returns:
        Tuple of (x, y) Anna coordinates

    Example:
        >>> x, y = matrix_to_anna(30, 70)
        >>> print(f"Anna({x}, {y})")  # Anna(6, 33)
    """
    x = col - 64  # 0..127 -> -64..63
    y = 63 - row  # 0..127 -> 63..-64
    return x, y


def lookup_anna(matrix: List[List[Any]], x: int, y: int) -> Any:
    """
    Look up value in Anna matrix at coordinates (x, y).

    Args:
        matrix: 128x128 Anna matrix
        x: Anna X coordinate
        y: Anna Y coordinate

    Returns:
        Value at the specified position

    Example:
        >>> value = lookup_anna(matrix, 6, 33)
        >>> print(value)  # -93 (CORE node)
    """
    row, col = anna_to_matrix(x, y)
    return matrix[row][col]


def load_anna_matrix(path: Optional[str] = None) -> List[List[int]]:
    """
    Load the Anna matrix from JSON file.

    Args:
        path: Optional path to anna-matrix.json. If None, uses default location.

    Returns:
        128x128 matrix as list of lists

    Example:
        >>> matrix = load_anna_matrix()
        >>> print(lookup_anna(matrix, 6, 33))  # -93
    """
    if path is None:
        # Default path relative to this script
        script_dir = Path(__file__).parent
        path = script_dir.parent / "public" / "data" / "anna-matrix.json"

    with open(path, 'r') as f:
        data = json.load(f)

    return data.get('matrix', data)


# Strategic Nodes - CORRECTED VALUES
STRATEGIC_NODES = {
    # Nodes within -64..63 range
    'CORE': {'coords': (6, 33), 'description': 'Central processing node'},
    'MEMORY': {'coords': (21, 21), 'description': 'Memory storage node'},
    'GUARDIAN': {'coords': (19, 18), 'description': 'Security/protection node'},
    'DATE': {'coords': (3, 3), 'description': 'Temporal reference node'},
    'VOID': {'coords': (0, 0), 'description': 'Origin/null state node'},

    # Nodes outside -64..63 range (extended coordinates)
    'ENTRY': {'coords': (45, 92), 'description': 'Entry point node', 'extended': True},
    'VISION': {'coords': (64, 64), 'description': 'Vision/perception node', 'extended': True},
    'EXIT': {'coords': (82, 39), 'description': 'Exit point node', 'extended': True},
    'ROOT_ALPHA': {'coords': (13, 71), 'description': 'Primary root node', 'extended': True},
    'ROOT_BETA': {'coords': (18, 110), 'description': 'Secondary root node', 'extended': True},
    'ORACLE': {'coords': (11, 110), 'description': 'Oracle/prediction node', 'extended': True},
}


def get_node_value(matrix: List[List[int]], node_name: str) -> Tuple[int, int, int, Any]:
    """
    Get the matrix value for a strategic node.

    Args:
        matrix: 128x128 Anna matrix
        node_name: Name of the strategic node (e.g., 'CORE', 'VOID')

    Returns:
        Tuple of (x, y, row, col, value)

    Example:
        >>> matrix = load_anna_matrix()
        >>> x, y, row, col, value = get_node_value(matrix, 'CORE')
        >>> print(f"CORE at ({x}, {y}) = {value}")  # CORE at (6, 33) = -93
    """
    if node_name not in STRATEGIC_NODES:
        raise ValueError(f"Unknown node: {node_name}")

    x, y = STRATEGIC_NODES[node_name]['coords']
    row, col = anna_to_matrix(x, y)
    value = matrix[row][col]

    return x, y, row, col, value


def find_dark_matter_cells(matrix: List[List[Any]]) -> List[Dict[str, Any]]:
    """
    Find all cells containing '00000000' (dark matter/null values).

    Args:
        matrix: 128x128 Anna matrix

    Returns:
        List of dicts with position info for each dark matter cell
    """
    dark_cells = []

    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value == '00000000' or value == 0 or str(value) == '00000000':
                x, y = matrix_to_anna(row, col)
                dark_cells.append({
                    'row': row,
                    'col': col,
                    'anna_x': x,
                    'anna_y': y,
                    'value': value
                })

    return dark_cells


def validate_coordinate_system() -> bool:
    """
    Validate the coordinate transformation against known values.

    Returns:
        True if all known values match, False otherwise
    """
    # Known verified values from Anna Twitter
    known_values = [
        (6, 33, -93),    # CORE
        (0, 7, -94),
        (0, 1, -38),
        (-27, 3, -110),
        (-27, 0, -102),
        (-1, 0, 69),
        (0, -1, -70),
        (-60, 10, 90),
        (2, 2, -123),
        (7, 0, -102),
    ]

    try:
        matrix = load_anna_matrix()

        for x, y, expected in known_values:
            actual = lookup_anna(matrix, x, y)
            if actual != expected:
                print(f"MISMATCH: Anna({x}, {y}) = {actual}, expected {expected}")
                return False

        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


# CFB Numbers Analysis
CFB_NUMBERS_RAW = [
    45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9,
    84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43,
    98, 5, 60, 15, 72, 27, 82, 39
]

CFB_COORDINATE_PAIRS = [
    (45, 92), (3, 77), (14, 58), (29, 81), (6, 33),
    (70, 48), (95, 22), (61, 9), (84, 37), (50, 16),
    (73, 28), (85, 41), (96, 7), (62, 19), (74, 30),
    (87, 43), (98, 5), (60, 15), (72, 27), (82, 39)
]


def analyze_cfb_numbers(matrix: List[List[int]]) -> List[Dict[str, Any]]:
    """
    Analyze CFB's posted numbers using correct coordinate transformation.

    Returns:
        List of analysis results for each coordinate pair
    """
    results = []

    for i, (x, y) in enumerate(CFB_COORDINATE_PAIRS, 1):
        row, col = anna_to_matrix(x, y)
        value = matrix[row][col]

        results.append({
            'position': i,
            'x': x,
            'y': y,
            'sum': x + y,
            'row': row,
            'col': col,
            'anna_value': value,
            'mod_27': value % 27 if isinstance(value, int) else None
        })

    return results


if __name__ == "__main__":
    print("Anna Matrix Utilities - Validation")
    print("=" * 50)

    # Validate coordinate system
    print("\nValidating coordinate system...")
    if validate_coordinate_system():
        print("SUCCESS: All known values match!")
    else:
        print("ERROR: Coordinate system validation failed!")

    # Load matrix and show examples
    matrix = load_anna_matrix()
    print(f"\nMatrix loaded: {len(matrix)}x{len(matrix[0])}")

    # Show strategic nodes
    print("\n=== Strategic Nodes ===")
    for name in ['CORE', 'VOID', 'MEMORY', 'GUARDIAN', 'DATE']:
        x, y, row, col, value = get_node_value(matrix, name)
        print(f"{name}: Anna({x}, {y}) -> matrix[{row}][{col}] = {value}")

    # Find dark matter
    print("\n=== Dark Matter Cells ===")
    dark_cells = find_dark_matter_cells(matrix)
    print(f"Found {len(dark_cells)} dark matter cells")
    for cell in dark_cells[:5]:
        print(f"  matrix[{cell['row']}][{cell['col']}] = Anna({cell['anna_x']}, {cell['anna_y']})")

    # Analyze CFB numbers
    print("\n=== CFB Numbers Analysis (First 5) ===")
    cfb_results = analyze_cfb_numbers(matrix)
    for r in cfb_results[:5]:
        print(f"  #{r['position']}: ({r['x']}, {r['y']}) sum={r['sum']} -> matrix[{r['row']}][{r['col']}] = {r['anna_value']}")
