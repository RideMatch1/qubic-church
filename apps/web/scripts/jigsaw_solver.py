import numpy as np
from pathlib import Path

# THE JIGSAW PUZZLE SOLVER
# Attempting to rearrange the Matrix Sectors (16x16 blocks of 8x8) to maximize continuity.
# Hypothesis: The matrix is scrambled. We need to find the permutation that aligns the 'edges'.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def jigsaw_solve():
    print("🧩 INITIATING JIGSAW PUZZLE SOLVER (Sector Re-Alignment)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH) # 128x128x3
    
    # Break into 256 tiles (8x8)
    tiles = []
    
    for r_block in range(16):
        for c_block in range(16):
            r_start, c_start = r_block*8, c_block*8
            tile_data = grid[r_start:r_start+8, c_start:c_start+8, :]
            # We'll use the UNMASKED value (L5 ^ Weight) for matching
            unmasked_tile = np.zeros((8,8), dtype=int)
            for r in range(8):
                for c in range(8):
                    if not tile_data[r,c,2]:
                        unmasked_tile[r,c] = tile_data[r,c,1] ^ tile_data[r,c,0]
                    else:
                        unmasked_tile[r,c] = 0 # Gap
            
            tiles.append({
                'id': f"{r_block},{c_block}",
                'data': unmasked_tile
            })
            
    print(f"[*] Extracted {len(tiles)} Tiles (8x8). Calculating Edge-Matches...")
    
    # We look for tiles that fit horizontally: Left-Edge of B matches Right-Edge of A
    # Match Score = Sum of squared differences (smaller is better)
    
    # Example: Let's find the logical specific neighbor for Tile (0,0) [Core Start]
    
    start_tile = tiles[4] # Tile (0,4) contains Core (6,33) (Cols 32-39)
    print(f"[*] Analyzing Neighbors for CORE TILE (ID: {start_tile['id']})...")
    
    best_right_match = None
    min_diff = float('inf')
    
    right_edge_A = start_tile['data'][:, 7] # Last column
    
    for t in tiles:
        if t['id'] == start_tile['id']: continue
        
        left_edge_B = t['data'][:, 0] # First column
        
        # Calculate Diff
        # Ignore Gaps (0) in calculation
        diff = 0
        valid_pixels = 0
        for i in range(8):
            if right_edge_A[i] != 0 and left_edge_B[i] != 0:
                d = abs(int(right_edge_A[i]) - int(left_edge_B[i]))
                diff += d
                valid_pixels += 1
        
        if valid_pixels > 4: # Need at least 4 overlapping non-gap pixels to judge
            score = diff / valid_pixels
            if score < min_diff:
                min_diff = score
                best_right_match = t
                
    if best_right_match:
        print(f"    [+] BEST RIGHT NEIGHBOR: Tile {best_right_match['id']} (Score: {min_diff:.2f})")
        # Check if it *is* the naturally adjacent tile (0,5)
        if best_right_match['id'] == "0,5":
            print("        -> Matches Natural Order! (Grid is NOT scrambled horizontally)")
        else:
            print("        -> JUMP DETECTED! (The grid might be scrambled)")
            
    # Check Vertical too
    print(f"[*] Analyzing Bottom Neighbors...")
    bottom_edge_A = start_tile['data'][7, :]
    
    best_bottom_match = None
    min_diff_v = float('inf')
    
    for t in tiles:
        if t['id'] == start_tile['id']: continue
        top_edge_B = t['data'][0, :]
        
        diff = 0
        valid_pixels = 0
        for i in range(8):
            if bottom_edge_A[i] != 0 and top_edge_B[i] != 0:
                d = abs(int(bottom_edge_A[i]) - int(top_edge_B[i]))
                diff += d
                valid_pixels += 1
                
        if valid_pixels > 4:
            score = diff / valid_pixels
            if score < min_diff_v:
                min_diff_v = score
                best_bottom_match = t
                
    if best_bottom_match:
        print(f"    [+] BEST BOTTOM NEIGHBOR: Tile {best_bottom_match['id']} (Score: {min_diff_v:.2f})")
        if best_bottom_match['id'] == "1,4":
            print("        -> Matches Natural Order!")
        else:
             print("        -> JUMP DETECTED! (The grid might be scrambled vertically)")


if __name__ == "__main__":
    jigsaw_solve()
