import numpy as np
from pathlib import Path
import random

# THE CORTEX REASSEMBLER
# A Greedy Algorithm to reconstruct the scrambled 16x16 Tile Grid.
# Goal: Minimize the total Edge-Difference between adjacent tiles.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")
OUTPUT_MAP_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/reassembled_map.txt")
REASSEM_GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/reassembled_cortex.npy")

def calculate_edge_diff(edge_a, edge_b):
    # Calculate sum of absolute differences, ignoring gaps (0)
    # Penalize mismatches heavily
    diff = 0
    valid_pixels = 0
    for i in range(8):
        val_a = edge_a[i]
        val_b = edge_b[i]
        if val_a != 0 and val_b != 0:
            diff += abs(int(val_a) - int(val_b))
            valid_pixels += 1
            
    if valid_pixels < 3: return 1000 # High penalty for lack of overlap data
    return diff / valid_pixels

def reassemble_cortex():
    print("🧩 REASSEMBLING CORTEX (Greedy Layout Solver)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH) # 128x128x3
    
    # Extract Tiles
    tiles = []
    for r in range(16):
        for c in range(16):
            r_s, c_s = r*8, c*8
            tile_data = grid[r_s:r_s+8, c_s:c_s+8, :]
            
            unmasked = np.zeros((8,8), dtype=int)
            for i in range(8):
                for j in range(8):
                    if not tile_data[i,j,2]:
                        unmasked[i,j] = tile_data[i,j,1] ^ tile_data[i,j,0]
            
            tiles.append({
                'original_pos': (r,c),
                'data': unmasked,
                'raw_data': tile_data, # Store full 8x8x3 block
                'used': False
            })
            
    # Solve Grid (16x16)
    # Start with Tile (0,0) (Top-Left) as anchor? 
    # Or start with Core Tile (0,4) and build around it?
    # Let's start with Core Tile at position (8,8) (Center of new map)
    
    new_grid = [[None for _ in range(16)] for _ in range(16)]
    
    # Find Core Tile (Orig: 0,4)
    core_tile_idx = 4
    core_tile = tiles[core_tile_idx]
    
    # Place at Center (8,8)
    new_grid[8][8] = core_tile
    core_tile['used'] = True
    
    print("[*] Placing Core Tile (0,4) at Center (8,8). Growing crystal...")
    
    # Frontier: List of (r, c) empty spots adjacent to filled spots
    frontier = set()
    frontier.add((8,9)) # Right
    frontier.add((8,7)) # Left
    frontier.add((7,8)) # Top
    frontier.add((9,8)) # Bottom
    
    placed_count = 1
    
    while frontier and placed_count < 256:
        # Pick a spot from frontier with most filled neighbors
        best_spot = None
        max_neighbors = -1
        
        frontier_list = list(frontier)
        scores = []
        
        for r, c in frontier_list:
            n_count = 0
            if r>0 and new_grid[r-1][c]: n_count+=1
            if r<15 and new_grid[r+1][c]: n_count+=1
            if c>0 and new_grid[r][c-1]: n_count+=1
            if c<15 and new_grid[r][c+1]: n_count+=1
            scores.append(n_count)
            
        # Sort by most neighbors (constrains the search better)
        sorted_indices = np.argsort(scores)[::-1]
        
        # Take best spot
        target_r, target_c = frontier_list[sorted_indices[0]]
        pass # just placeholder
        
        # Find best UNUSED tile for this spot
        best_tile = None
        min_cost = float('inf')
        
        # Calculate constraints from neighbors
        # Top Neighbor (Should match its Bottom to my Top)
        top_n = new_grid[target_r-1][target_c] if target_r > 0 else None
        bottom_n = new_grid[target_r+1][target_c] if target_r < 15 else None
        left_n = new_grid[target_r][target_c-1] if target_c > 0 else None
        right_n = new_grid[target_r][target_c+1] if target_c < 15 else None
        
        for t in tiles:
            if t['used']: continue
            
            cost = 0
            
            if top_n:
                cost += calculate_edge_diff(top_n['data'][7,:], t['data'][0,:])
            if bottom_n: 
                cost += calculate_edge_diff(t['data'][7,:], bottom_n['data'][0,:])
            if left_n:
                cost += calculate_edge_diff(left_n['data'][:,7], t['data'][:,0])
            if right_n:
                cost += calculate_edge_diff(t['data'][:,7], right_n['data'][:,0])
                
            if cost < min_cost:
                min_cost = cost
                best_tile = t
        
        # Place it
        if best_tile:
            new_grid[target_r][target_c] = best_tile
            best_tile['used'] = True
            placed_count += 1
            frontier.remove((target_r, target_c))
            
            # Add new neighbors to frontier
            neighbors = [(target_r-1, target_c), (target_r+1, target_c), (target_r, target_c-1), (target_r, target_c+1)]
            for nr, nc in neighbors:
                if 0 <= nr < 16 and 0 <= nc < 16 and new_grid[nr][nc] is None:
                    frontier.add((nr, nc))
        else:
            # Should not happen unless no tiles left or trapped
            print("[!] Warn: No tile fit found? Skipping spot.")
            frontier.remove((target_r, target_c))

    print(f"[*] Reassembly Complete. Used {placed_count}/256 tiles.")
    
    # Render the Map Text
    print("\n[!] GENERATING REASSEMBLED MAP (Center View):")
    with open(OUTPUT_MAP_PATH, "w") as f:
        for r in range(4, 12): # Center 8x8 blocks
            row_lines = ["" for _ in range(8)]
            for c in range(4, 12):
                tile = new_grid[r][c]
                if tile:
                    # Append 8 lines of char data
                    for i in range(8):
                        seg = ""
                        for j in range(8):
                            val = tile['data'][i,j]
                            char = chr(val) if 32 <= val <= 126 else '.'
                            seg += char
                        row_lines[i] += seg + "|"
                else:
                    for i in range(8):
                        row_lines[i] += "........|"
            
            for l in row_lines:
                print(l)
                f.write(l + "\n")
            print("-" * 64)
            f.write("-" * 64 + "\n")
            
    # Save the Reassembled Binary Grid for Gap Mining
    print("[*] Saving Reassembled Grid Binary to 'outputs/reassembled_cortex.npy'...")
    full_reassembled_grid = np.zeros((128, 128, 3), dtype=np.uint8)
    
    for r in range(16):
        for c in range(16):
            tile = new_grid[r][c]
            if tile:
                # Place raw data into new grid
                full_reassembled_grid[r*8:(r+1)*8, c*8:(c+1)*8, :] = tile['raw_data']
            else:
                # Fill with zeros or noise if missing
                pass
                
    np.save(REASSEM_GRID_PATH, full_reassembled_grid)
    print(f"[*] Saved reassembled grid to {REASSEM_GRID_PATH}")

if __name__ == "__main__":
    reassemble_cortex()
