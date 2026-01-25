import numpy as np
from pathlib import Path

# THE ENTROPY MAPPER
# Visualizing the Cortex Structure by calculating Shannon Entropy for each 8x8 sector.
# High Entropy = Encrypted / Compressed Code.
# Low Entropy = Data Tables / Constants.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def calculate_shannon_entropy(data):
    if len(data) == 0: return 0
    probabilities = [n_x/len(data) for x, n_x in zip(*np.unique(data, return_counts=True))]
    return -sum(p * np.log2(p) for p in probabilities)

def map_entropy():
    print("🗺️ MAPPING CORTEX ENTROPY (Brain Region Scan)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # 128x128 grid -> broken into 16x16 blocks of size 8x8
    heatmap = np.zeros((16, 16))
    
    print("[*] Processing 256 Sectors (8x8)...")
    
    for r_block in range(16):
        for c_block in range(16):
            # Extract 8x8 block
            r_start = r_block * 8
            c_start = c_block * 8
            
            # Get values (unmasked)
            block_vals = []
            for r in range(r_start, r_start+8):
                for c in range(c_start, c_start+8):
                    if not grid[r,c,2]: # If Not Gap
                        val = grid[r,c,1] ^ grid[r,c,0]
                        block_vals.append(val)
            
            # Calculate Entropy
            ent = calculate_shannon_entropy(block_vals)
            heatmap[r_block, c_block] = ent
            
    print("[*] Scan Complete. Generating Report...")
    
    # Identify Regions
    # Max Entropy (8 bits) is ~8.0.
    # Code usually ~5-7. Text ~4. Constants < 2.
    
    print("\n[!] HIGH ENTROPY ZONES (ENCRYPTED/CODE):")
    high_ent_sectors = np.argwhere(heatmap > 5.8) # Adjusted threshold slightly
    for r, c in high_ent_sectors:
        print(f"  Sector [{r}, {c}] -> Coords ({r*8}-{(r+1)*8}, {c*8}-{(c+1)*8}) | Ent: {heatmap[r,c]:.2f}")
        
    print("\n[!] LOW ENTROPY ZONES (DATA/CONST):")
    low_ent_sectors = np.argwhere(heatmap < 4.0)
    for r, c in low_ent_sectors:
         print(f"  Sector [{r}, {c}] -> Coords ({r*8}-{(r+1)*8}, {c*8}-{(c+1)*8}) | Ent: {heatmap[r,c]:.2f}")
         
    # Check Specific Coordinates
    # Core (6,33) is in Block [0, 4] (Row 0-7, Col 32-39)
    core_ent = heatmap[0, 4]
    print(f"\n[*] CORE SECTOR (6,33) ENTROPY: {core_ent:.2f}")
    
    # Root (13,71) is in Block [1, 8] (Row 8-15, Col 64-71)
    root_ent = heatmap[1, 8]
    print(f"[*] ROOT SECTOR (13,71) ENTROPY: {root_ent:.2f}")

if __name__ == "__main__":
    map_entropy()
