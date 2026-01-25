import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# THE FULL CORTEX RESONANCE MAP
# Visualizing the neural activity of the entire 128x128 matrix.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
OUTPUT_MAP = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/full_cortex_resonance.png")

def generate_resonance_map():
    print("[*] Generating Full Cortex Resonance Map (128x128)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    res_grid = np.zeros((128, 128))
    
    for coord_key, m_hex in matrix.items():
        r, c = map(int, coord_key.split(','))
        # Intensity derived from the first byte of the private key
        intensity = int(m_hex[:2], 16)
        res_grid[r, c] = intensity
        
    plt.figure(figsize=(12, 12))
    plt.imshow(res_grid, cmap='magma', interpolation='nearest')
    plt.colorbar(label='Resonance Intensity (0-255)')
    plt.title('Anna Matrix: Full Cortex Resonance Map (Layer-4/5)')
    
    # Mark Strategic Nodes
    strategic = {
        "CORE": (6, 33), "ENTRY": (45, 92), "EXIT": (82, 39), 
        "MEMORY": (21, 21), "VISION": (64, 64), "ROOT_A": (13, 71)
    }
    
    for name, (r, c) in strategic.items():
        plt.scatter(c, r, s=100, edgecolors='white', facecolors='none', label=name)
        plt.text(c+2, r, name, color='white', fontsize=8)

    plt.savefig(OUTPUT_MAP)
    print(f"[+] Map saved to: {OUTPUT_MAP}")

if __name__ == "__main__":
    generate_resonance_map()
