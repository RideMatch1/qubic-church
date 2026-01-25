import numpy as np
from pathlib import Path
from collections import Counter

# THE GAP INTERPOLATOR
# Predicting the content of the 23.6% Gap Nodes via Neighbor Pattern Matching.
# Technique: K-Nearest Neighbors (KNN) logic on the 2D Grid.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def interpolate_gaps():
    print("🧠 RUNNING GAP INTERPOLATION (Pattern Matching)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)

    # We want to fill grid[:, :, 1] (L5 Value) where grid[:, :, 2] == 1 (Is Gap)
    
    filled_grid = grid.copy()
    gaps_filled = 0
    
    # Simple Mode: Most Frequent Neighbor (Mode)
    print("[*] Scanning 3872 Gaps...")
    
    for r in range(128):
        for c in range(128):
            if grid[r,c,2]: # Is Gap
                
                # Get Neighbors (3x3 kernel)
                neighbors = []
                for nr in range(r-1, r+2):
                    for nc in range(c-1, c+2):
                        if 0 <= nr < 128 and 0 <= nc < 128:
                             if not grid[nr,nc,2]: # If Neighbor is NOT Gap
                                 val = grid[nr,nc,1] ^ grid[nr,nc,0]
                                 neighbors.append(val)
                
                if neighbors:
                    # Predict value based on neighbors
                    # For code, often neighbors are similar or sequential.
                    # We'll use the Most Common value for stability.
                    most_common = Counter(neighbors).most_common(1)[0][0]
                    
                    filled_grid[r,c,1] = most_common ^ grid[r,c,0] # Re-mask it for storage
                    filled_grid[r,c,2] = 0 # Mark as Filled
                    gaps_filled += 1
                    
    print(f"[*] Filled {gaps_filled} Gaps via Neighbor Consensus.")
    
    # Analyze the Predicted Content
    # What did we find in the Gaps?
    
    print("\n[!] PREDICTED HIDDEN LOGIC (Sample):")
    
    # Check specific gap row segments
    for r in [6, 13, 125]: # Core, Root, CRC
        line_chars = []
        for c in range(128):
            w = filled_grid[r,c,0]
            l5 = filled_grid[r,c,1]
            val = l5 ^ w
            
            # Highlight predictions
            orig_is_gap = grid[r,c,2]
            char = chr(val) if 32 <= val <= 126 else '.'
            
            if orig_is_gap:
                line_chars.append(f"[{char}]") # Mark prediction with []
            else:
                line_chars.append(char)
        
        print(f"\n[ROW {r:3}] {''.join(line_chars)}")

if __name__ == "__main__":
    interpolate_gaps()
