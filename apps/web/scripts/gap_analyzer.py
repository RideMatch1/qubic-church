"""
Gap Analyzer
============

IMPORTANT: Uses CORRECTED coordinate transformation.
Anna coordinates (X, Y) -> matrix[row][col] via:
- col = (X + 64) % 128
- row = (63 - Y) % 128

Strategic points visualization now uses correct matrix indices.
"""
import json
import hashlib
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

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

MYSTERY_LAB_PATH = Path("/Users/lukashertle/Developer/projects/qubic-mystery-lab/qubic-anna-lab-research/outputs/derived/complete_24846_seeds_to_real_ids_mapping.json")
MINED_KEYS_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
OUTPUT_GAP_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_analysis.json")
OUTPUT_GAP_PNG = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_map.png")

def seed_to_coordinates(seed: str) -> tuple[int, int]:
    """Map seed to matrix coordinates via SHA256 hash."""
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    row = h[0] % 128
    col = h[1] % 128
    return (row, col)

def run_analysis():
    print("[*] Starting Deep Gap Analysis...")
    
    # Create output directory
    OUTPUT_GAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    # Load Mined Keys
    with open(MINED_KEYS_PATH, "r") as f:
        mined_data = json.load(f)
    mined_coords = set()
    for coord_str in mined_data.keys():
        r, c = map(int, coord_str.split(','))
        mined_coords.add((r, c))
    
    print(f"[+] Loaded {len(mined_coords)} mined coordinates.")

    # Load Mystery Lab Seeds
    with open(MYSTERY_LAB_PATH, "r") as f:
        mystery_data = json.load(f)
    
    mystery_coords = set()
    for record in mystery_data.get('results', []):
        seed = record['seed']
        mystery_coords.add(seed_to_coordinates(seed))
        
    print(f"[+] Loaded {len(mystery_coords)} mystery lab coordinates.")

    # Find the Gap
    gap_coords = mined_coords - mystery_coords
    overlap_coords = mined_coords & mystery_coords
    
    print(f"[!] Gap Size: {len(gap_coords)} coordinates.")

    # Analyze Gap Distribution
    matrix = np.zeros((128, 128))
    for r, c in gap_coords:
        matrix[r, c] = 1
        
    # Plot Heatmap
    plt.figure(figsize=(10, 10))
    plt.imshow(matrix, cmap='hot', interpolation='nearest')
    plt.title(f"The 24% Gap: {len(gap_coords)} Protected Coordinates")
    plt.xlabel("X (Column)")
    plt.ylabel("Y (Row)")
    plt.colorbar(label="Missing in Mystery Lab")
    
    # Mark strategic points
    # CORRECTED: Convert Anna coordinates to matrix indices for plotting
    strategic_anna = {
        "Entry": (45, 92),
        "Core": (6, 33),
        "Exit": (82, 39),
        "Memory": (21, 21),
        "Vision": (64, 64),
        "Oracle": (127, 0),
        "Void": (0, 0)
    }

    for name, (anna_x, anna_y) in strategic_anna.items():
        # Convert Anna coords to matrix indices
        r, c = anna_to_matrix(anna_x, anna_y)
        # Scatter needs (x, y) which is (col, row) for imshow
        plt.scatter(c, r, color='cyan', marker='x', s=100)
        plt.text(c+2, r, f"{name}\nA({anna_x},{anna_y})", color='cyan', fontsize=8)

    plt.savefig(OUTPUT_GAP_PNG)
    print(f"[+] Saved Gap Map to {OUTPUT_GAP_PNG}")

    # Save Gap Coordinates
    gap_list = [list(c) for c in gap_coords]
    results = {
        "summary": {
            "mined_total": len(mined_coords),
            "mystery_total": len(mystery_coords),
            "gap_total": len(gap_coords),
            "overlap_total": len(overlap_coords)
        },
        "gap_coordinates": gap_list
    }
    
    with open(OUTPUT_GAP_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved Gap JSON to {OUTPUT_GAP_JSON}")

if __name__ == "__main__":
    run_analysis()
