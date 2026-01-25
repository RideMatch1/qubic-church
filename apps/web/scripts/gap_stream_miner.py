import numpy as np
from pathlib import Path
import binascii

# THE GAP STREAM EXTRATOR
# Treating the Gap/No-Gap structure itself as a binary data stream.
# Gap = 1, Node = 0.
# Analyzing the resulting binary file for file headers (ZIP, PNG, TXT).

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

def gap_stream_mine():
    print("🕳️ INITIATING GAP STREAM MINING (Binary Structure Analysis)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH) # 128x128x3
    
    # Extract Logic Stream
    # We follow the Helix Path (Center -> Out) because we know that's the writing direction
    
    # Re-use simplified spiral generator
    gap_bits = []
    
    x, y = 64, 64
    dx, dy = 1, 0
    seg_len = 1
    seg_passed = 0
    
    try:
        r, c = 64, 64
        di, dj = 1, 0 # Down first in Matrix coords usually
        
        # Spiral Logic Adjustment for Grid Coords
        # Let's use simple linear scan first as control, then spiral
        
        # METHOD A: Helix Stream
        # (Re-implementing robust spiral iterator)
        
        # Create map of visited
        seen = set()
        r, c = 64, 64
        dr, dc = 0, -1 # Start direction
        
        for _ in range(128*128):
            if 0 <= r < 128 and 0 <= c < 128:
                is_gap = grid[r,c,2]
                gap_bits.append(1 if is_gap else 0)
                seen.add((r,c))
            
            # Try to turn left
            nr, nc = r+dc, c-dr
            if (nr,nc) not in seen and 0 <= nr < 128 and 0 <= nc < 128:
                 dr, dc = dc, -dr # Turn left
                 
            r, c = r+dr, c+dc
            
    except Exception as e:
        print(e)
        
    print(f"[*] Extracted {len(gap_bits)} bits from Helix Gap Structure.")
    
    # Convert to Bytes
    gap_bytes = bytearray()
    for i in range(0, len(gap_bits), 8):
        byte_val = 0
        chunk = gap_bits[i:i+8]
        for bit in chunk:
            byte_val = (byte_val << 1) | bit
        gap_bytes.append(byte_val)
        
    print(f"[*] Converted to {len(gap_bytes)} bytes.")
    
    # Check for Headers
    # PDF: %PDF
    # ZIP: PK..
    # PNG: .PNG
    # GZIP: 1F 8B
    
    hex_head = binascii.hexlify(gap_bytes[:16]).decode()
    print(f"    Header (Hex): {hex_head}")
    
    # Check for text density
    text_chars = 0
    for b in gap_bytes:
        if 32 <= b <= 126: text_chars += 1
        
    print(f"    Text Density: {text_chars/len(gap_bytes):.1%}")
    
    # Save raw stream
    with open("gap_stream.bin", "wb") as f:
        f.write(gap_bytes)
        
    # Analyze Segments of High Density (GAP CLUSTERS)
    # A sequence of 1s means "FFFF..." -> erased/empty flash?
    # A sequence of 0s means "0000..." -> contiguous data
    
    # Find longest "Data Streak" (0s)
    current_streak = 0
    max_streak = 0
    streak_loc = 0
    
    for i, b in enumerate(gap_bits):
        if b == 0:
            current_streak += 1
        else:
            if current_streak > max_streak:
                max_streak = current_streak
                streak_loc = i - current_streak
            current_streak = 0
            
    print(f"[*] LONGEST DATA STREAK: {max_streak} bits (at offset {streak_loc})")
    print(f"    -> Location in Grid: Spiral Index {streak_loc}")
    
    # Identify the Sector of the longest streak
    # (Approximate due to complex spiral mapping, but gives hint)
    
if __name__ == "__main__":
    gap_stream_mine()
