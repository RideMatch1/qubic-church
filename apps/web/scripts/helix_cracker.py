import numpy as np
from pathlib import Path
import math

# THE HELIX CRACKER
# Decoding the Matrix assuming a Helical / Spiral data structure.
# Also scanning for "DNA Mode" (Pure Ternary Data Streams).

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def get_spiral_coords(rows, cols):
    # Generator for spiral coordinates (Center Out)
    # 64,64 -> Outwards
    x, y = cols // 2, rows // 2
    dx, dy = 0, -1
    for i in range(rows * cols):
        yield r_idx(y), c_idx(x)
        if (-rows/2 < x <= rows/2) and (-cols/2 < y <= cols/2):
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                dx, dy = -dy, dx
        x, y = x+dx, y+dy

def r_idx(y): return min(max(int(y), 0), 127) # Clamp
def c_idx(x): return min(max(int(x), 0), 127) 

def helix_crack():
    print("🧬 INITIATING HELIX CRACKER (DNA/Spiral Logic)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH) # 128x128x3
    
    # SCAN 1: SPIRAL UNWINDING
    # Does the code read like a vinyl record?
    print("[*] Unwinding the Matrix (Spiral: Center -> Out)...")
    
    spiral_stream = []
    
    # We implement a simple square spiral
    # Start 64, 64
    x = 64
    y = 64
    dk = 1 # step length
    dx = 1
    dy = 0
    seg_passed = 0
    
    # Collect approx 16000 points
    visited = set()
    
    try:
        # Spiral Loop (Simplified)
        r, c = 64, 64
        di = 1
        dj = 0
        segment_len = 1
        segment_passed = 0
        
        for _ in range(128*128):
            if 0 <= r < 128 and 0 <= c < 128:
                if not grid[r,c,2]:
                    val = grid[r,c,1] ^ grid[r,c,0]
                    spiral_stream.append(val)
                else:
                    spiral_stream.append(0) # or marker
            
            r += di
            c += dj
            segment_passed += 1
            if segment_passed == segment_len:
                segment_passed = 0
                
                # Rotate 90 deg
                di, dj = dj, -di
                
                if dj == 0: # If we just finished a vertical move, increase stride
                    segment_len += 1
    except Exception as e:
        print(e)

    # Analyze Stream
    # Convert to Chars
    text = "".join([chr(v) if 32 <= v <= 126 else '.' for v in spiral_stream])
    
    # Search for Patterns in the Spiral Data
    print(f"\n[!] SPIRAL STREAM (First 200 chars):")
    print(text[:200])
    
    if "ANNA" in text or "QUBIC" in text:
        print("    [!!!] KEYWORD FOUND IN SPIRAL!")
        
    # SCAN 2: DNA TERNARY DETECTION
    # DNA Code uses 4 bases (A, C, G, T) or 3 States (-1, 0, 1)
    # Let's check for regions with only 3 specific byte values.
    
    print(f"\n[*] Scanning for DNA Zones (Low Variance Regions)...")
    
    for r in range(0, 128, 8):
        for c in range(0, 128, 8):
            # 8x8 Block
            block_vals = []
            for i in range(8):
                for j in range(8):
                    if not grid[r+i,c+j,2]:
                        block_vals.append(grid[r+i,c+j,1] ^ grid[r+i,c+j,0])
                        
            # Unique Values?
            unique = set(block_vals)
            if 1 < len(unique) <= 4:
                # Potential DNA/Ternary encoding
                print(f"  [SECTOR {r},{c}] IS DNA-ENCODED! Base States: {sorted(list(unique))}")
                
    # SCAN 3: THE DOUBLE HELIX (27-Stride)
    # Jumping every 27 bytes
    print(f"\n[*] Extracting Double Helix (Stride 27)...")
    
    linear_data = []
    # Dump grid to linear
    for r in range(128):
        for c in range(128):
            if not grid[r,c,2]:
                linear_data.append(grid[r,c,1] ^ grid[r,c,0])
            else:
                linear_data.append(0) # Padding
                
    helix_1 = linear_data[0::27]
    helix_1_txt = "".join([chr(v) if 32 <= v <= 126 else '_' for v in helix_1])
    
    print(f"[STRIDE 27]: {helix_1_txt[:100]}...")
    
    # Check simple arithmetic progressions
    # e.g. Count of Alphabet chars
    alpha_count = sum(1 for c in helix_1_txt if c.isalpha())
    print(f"    -> Alpha Density: {alpha_count}/{len(helix_1_txt)} ({alpha_count/len(helix_1_txt):.1%})")

if __name__ == "__main__":
    helix_crack()
