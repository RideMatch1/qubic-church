"""
Find Entry Identity
===================

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Note: The hash mapping (seed -> position) produces matrix indices directly.
When searching for an Anna coordinate target, we must convert it first.
"""
import json
import hashlib
from pathlib import Path

# Import correct coordinate transformation
try:
    from anna_matrix_utils import anna_to_matrix, matrix_to_anna
except ImportError:
    def anna_to_matrix(x, y):
        col = (x + 64) % 128
        row = (63 - y) % 128
        return row, col
    def matrix_to_anna(row, col):
        x = col - 64
        y = 63 - row
        return x, y

SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def find_target_identity(anna_coords=(45, 92)):
    """
    Find the identity at a given Anna coordinate.

    Args:
        anna_coords: Tuple of (X, Y) in Anna coordinate system
                     Default is ENTRY at (45, 92)
    """
    # Convert Anna coordinates to matrix indices
    target_row, target_col = anna_to_matrix(anna_coords[0], anna_coords[1])

    print(f"[*] Identifying the official Presence at Anna{anna_coords}")
    print(f"[*] Matrix target: [{target_row}][{target_col}]")

    with open(SEEDS_FILE, "r") as f:
        data = json.load(f)

    records = data.get("records", [])

    for record in records:
        seed = record.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        row = h[0] % 128
        col = h[1] % 128

        if (row, col) == (target_row, target_col):
            anna_x, anna_y = matrix_to_anna(row, col)
            print(f"[!!!] FOUND: Seed '{seed}' maps to matrix[{row}][{col}] = Anna({anna_x}, {anna_y})")
            print(f"      Identity: {record.get('realIdentity')}")
            return record.get('realIdentity')

    # If not in public seeds, it's in the Gap.
    print(f"[!] No seed found mapping to target position.")
    return None

if __name__ == "__main__":
    find_target_identity()
