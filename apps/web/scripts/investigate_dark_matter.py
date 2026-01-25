#!/usr/bin/env python3
"""
Dark Matter Investigation
=========================

This script investigates the 26 cells in the Anna Matrix that contain '00000000'
(null/boundary markers) and maps them to Anna coordinates.

Uses the CORRECT coordinate transformation:
- col = (X + 64) % 128
- row = (63 - Y) % 128
"""

import json
from pathlib import Path
from anna_matrix_utils import load_anna_matrix, matrix_to_anna, anna_to_matrix

def investigate_dark_matter():
    print("=" * 60)
    print("DARK MATTER INVESTIGATION")
    print("=" * 60)

    # Load matrix
    matrix = load_anna_matrix()
    print(f"\nMatrix loaded: {len(matrix)}x{len(matrix[0])}")

    # Find all dark matter cells
    dark_cells = []
    for row in range(128):
        for col in range(128):
            value = matrix[row][col]
            if value == '00000000' or str(value) == '00000000':
                anna_x, anna_y = matrix_to_anna(row, col)
                dark_cells.append({
                    'row': row,
                    'col': col,
                    'anna_x': anna_x,
                    'anna_y': anna_y,
                    'value': value
                })

    print(f"\nFound {len(dark_cells)} Dark Matter cells (value = '00000000')")

    # Display all dark matter cells
    print("\n" + "=" * 60)
    print("DARK MATTER CELLS - COMPLETE LIST")
    print("=" * 60)
    print(f"{'#':<4} {'matrix[row][col]':<20} {'Anna(X, Y)':<15}")
    print("-" * 60)

    for i, cell in enumerate(dark_cells, 1):
        print(f"{i:<4} [{cell['row']:3}][{cell['col']:3}]           ({cell['anna_x']:4}, {cell['anna_y']:4})")

    # Analyze patterns
    print("\n" + "=" * 60)
    print("PATTERN ANALYSIS")
    print("=" * 60)

    # Check for row patterns
    rows_with_dark = {}
    for cell in dark_cells:
        r = cell['row']
        if r not in rows_with_dark:
            rows_with_dark[r] = []
        rows_with_dark[r].append(cell['col'])

    print(f"\nRows with dark matter: {sorted(rows_with_dark.keys())}")
    print(f"Number of unique rows: {len(rows_with_dark)}")

    # Check for column patterns
    cols_with_dark = {}
    for cell in dark_cells:
        c = cell['col']
        if c not in cols_with_dark:
            cols_with_dark[c] = []
        cols_with_dark[c].append(cell['row'])

    print(f"\nColumns with dark matter: {sorted(cols_with_dark.keys())}")
    print(f"Number of unique columns: {len(cols_with_dark)}")

    # Check for diagonal patterns
    print("\n--- Diagonal Analysis ---")
    main_diag = []  # row == col
    anti_diag = []  # row + col == 127
    for cell in dark_cells:
        if cell['row'] == cell['col']:
            main_diag.append(cell)
        if cell['row'] + cell['col'] == 127:
            anti_diag.append(cell)

    print(f"On main diagonal (row==col): {len(main_diag)}")
    print(f"On anti-diagonal (row+col=127): {len(anti_diag)}")

    # Check proximity to strategic nodes
    print("\n" + "=" * 60)
    print("PROXIMITY TO STRATEGIC NODES")
    print("=" * 60)

    strategic_anna = {
        'CORE': (6, 33),
        'VOID': (0, 0),
        'MEMORY': (21, 21),
        'GUARDIAN': (19, 18),
        'DATE': (3, 3),
        'ENTRY': (45, 92),
        'EXIT': (82, 39),
        'VISION': (64, 64),
        'ORACLE': (127, 0)
    }

    for name, (anna_x, anna_y) in strategic_anna.items():
        node_row, node_col = anna_to_matrix(anna_x, anna_y)

        # Find closest dark matter cell
        min_dist = float('inf')
        closest = None
        for cell in dark_cells:
            dist = ((cell['row'] - node_row)**2 + (cell['col'] - node_col)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest = cell

        print(f"\n{name} at Anna({anna_x}, {anna_y}) -> matrix[{node_row}][{node_col}]")
        if closest:
            print(f"  Closest dark matter: matrix[{closest['row']}][{closest['col']}]")
            print(f"  Distance: {min_dist:.2f} cells")
            print(f"  Dark Anna coords: ({closest['anna_x']}, {closest['anna_y']})")

    # Check Anna coordinate ranges
    print("\n" + "=" * 60)
    print("ANNA COORDINATE ANALYSIS")
    print("=" * 60)

    x_coords = [c['anna_x'] for c in dark_cells]
    y_coords = [c['anna_y'] for c in dark_cells]

    print(f"\nX range: {min(x_coords)} to {max(x_coords)}")
    print(f"Y range: {min(y_coords)} to {max(y_coords)}")
    print(f"X values: {sorted(set(x_coords))}")
    print(f"Y values: {sorted(set(y_coords))}")

    # Save results
    results = {
        'total_dark_cells': len(dark_cells),
        'cells': dark_cells,
        'pattern_analysis': {
            'unique_rows': len(rows_with_dark),
            'unique_cols': len(cols_with_dark),
            'rows_list': sorted(rows_with_dark.keys()),
            'cols_list': sorted(cols_with_dark.keys()),
            'on_main_diagonal': len(main_diag),
            'on_anti_diagonal': len(anti_diag)
        },
        'anna_ranges': {
            'x_min': min(x_coords),
            'x_max': max(x_coords),
            'y_min': min(y_coords),
            'y_max': max(y_coords)
        }
    }

    output_file = Path(__file__).parent / 'DARK_MATTER_ANALYSIS.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")

    return results


if __name__ == "__main__":
    investigate_dark_matter()
