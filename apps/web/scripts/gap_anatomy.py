import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
GAP_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_analysis.json")
OUTPUT_VIZ = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/anatomy_of_the_gap.png")

def visualize_anatomy():
    print("[*] Analyzing Anatomy of the Protected Gap...")
    
    with open(GAP_JSON, "r") as f:
        data = json.load(f)
    
    gap_coords = data.get("gap_coordinates", [])
    
    # Create 128x128 grid
    grid = np.zeros((128, 128))
    for r, c in gap_coords:
        grid[r, c] = 1

    plt.figure(figsize=(12, 12))
    plt.imshow(grid, cmap='magma', interpolation='nearest')
    plt.title("SCIENTIFIC AUDIT: Anatomical Structure of the 24% Gap", fontsize=16)
    plt.xlabel("X (Column Index)", fontsize=12)
    plt.ylabel("Y (Row Index)", fontsize=12)
    
    # Analysis: Look for clusters
    # We'll use a simple density calculation
    density = np.sum(grid) / (128*128)
    print(f"[+] Global Gap Density: {density:.4f}")
    
    # Check quadrants
    q1 = np.sum(grid[:64, :64])
    q2 = np.sum(grid[:64, 64:])
    q3 = np.sum(grid[64:, :64])
    q4 = np.sum(grid[64:, 64:])
    
    plt.text(5, 5, f"Q1 (NW): {q1}", color='white', fontweight='bold')
    plt.text(70, 5, f"Q2 (NE): {q2}", color='white', fontweight='bold')
    plt.text(5, 70, f"Q3 (SW): {q3}", color='white', fontweight='bold')
    plt.text(70, 70, f"Q4 (SE): {q4}", color='white', fontweight='bold')

    # Save
    plt.savefig(OUTPUT_VIZ)
    print(f"[+] Anatomical map saved to {OUTPUT_VIZ}")
    
    # Return metrics for documentation
    return {
        "q1": int(q1), "q2": int(q2), "q3": int(q3), "q4": int(q4),
        "total": len(gap_coords)
    }

if __name__ == "__main__":
    visualize_anatomy()
