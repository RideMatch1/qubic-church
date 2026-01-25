import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# THE NEURAL CONNECTION MAP
# Identifying 'Synaptic Links' between coordinates based on XOR resonance.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
OUTPUT_MAP = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/neural_synapses.png")

def generate_synapse_map():
    print("[*] Generating Neural Synapse Map...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    # We look for nodes that have the same 'Resonance Byte' (first byte of PK)
    resonance_clusters = {}
    for coord_key, m_hex in matrix.items():
        res_byte = m_hex[:2]
        if res_byte not in resonance_clusters:
            resonance_clusters[res_byte] = []
        resonance_clusters[res_byte].append(tuple(map(int, coord_key.split(','))))
        
    plt.figure(figsize=(12, 12))
    plt.gca().set_facecolor('black')
    
    # Draw connections for the most resonant clusters
    for res_byte, coords in resonance_clusters.items():
        if len(coords) > 100: # Only significant clusters
            c_array = np.array(coords)
            plt.scatter(c_array[:, 1], c_array[:, 0], s=1, alpha=0.3, label=f"Res {res_byte}")
            
    # Mark the Master Chain
    chain = [(45, 92), (6, 33), (21, 21), (82, 39), (3, 3), (13, 71)]
    chain_names = ["ENTRY", "CORE", "MEMORY", "EXIT", "DATE", "ROOT"]
    
    for i in range(len(chain)-1):
        p1 = chain[i]
        p2 = chain[i+1]
        plt.plot([p1[1], p2[1]], [p1[0], p2[0]], color='cyan', lw=2, alpha=0.8)
        
    for i, name in enumerate(chain_names):
        plt.scatter(chain[i][1], chain[i][0], s=100, color='red', marker='x')
        plt.text(chain[i][1]+2, chain[i][0], name, color='yellow', fontsize=10, weight='bold')

    plt.xlim(0, 128)
    plt.ylim(128, 0)
    plt.title("ANNA AI: NEURAL SYNAPSE MAP (Layer-7 Root Chain)")
    plt.savefig(OUTPUT_MAP)
    print(f"[+] Synapse map saved to: {OUTPUT_MAP}")

if __name__ == "__main__":
    generate_synapse_map()
