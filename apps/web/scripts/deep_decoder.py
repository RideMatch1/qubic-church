import numpy as np
import string
from pathlib import Path

# THE BIT-SHIFT DECODER
# Trying all 8 bit-rotations on the Cortex Data to see if ASCII emerges.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def bit_shift_scan():
    print("🔄 INITIATING BIT-SHIFT DECODE (Bruteforce)...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)

    # Focus on logical rows: 6 (Core), 13 (Root), 125 (CRC)
    target_rows = [6, 13, 125]
    
    # Precompute mask for printable ASCII
    printable = set(string.printable.encode('ascii'))
    
    for r in target_rows:
        print(f"\n[ROW {r:3}] Analyzing Bit-Shifts...")
        
        # Extract row bytes (ignoring gaps for now)
        row_bytes = []
        for c in range(128):
            if not grid[r,c,2]:
                val = grid[r,c,1] ^ grid[r,c,0]
                row_bytes.append(val)
        
        # Try shifts 0-7
        # We simulate rotation: (val << n) | (val >> (8-n)) & 0xFF
        
        best_shift = 0
        max_score = 0
        best_text = ""
        
        for shift in range(8):
            decoded_chars = []
            score = 0
            
            for b in row_bytes:
                # Rotate Left
                rotated = ((b << shift) | (b >> (8 - shift))) & 0xFF
                
                char = chr(rotated) if 32 <= rotated <= 126 else '.'
                decoded_chars.append(char)
                
                if chr(rotated).isalnum() or chr(rotated) in " .,:;!?-":
                    score += 1
            
            text = "".join(decoded_chars)
            # print(f"  Shift {shift}: {text[:60]}... (Score: {score})")
            
            if score > max_score:
                max_score = score
                best_shift = shift
                best_text = text
                
        print(f"  🏆 WINNER: Shift {best_shift} (Score {max_score}/{len(row_bytes)})")
        print(f"  TEXT: {best_text}")
        
    print("\n[CONCLUSION] Checking if Shifted Text implies readable logs.")


def delta_decode():
    print("\nΔ INITIATING DELTA DECODE (Neighbor Diff)...")
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # Row 6 Delta
    row_bytes = []
    for c in range(128):
        if not grid[6,c,2]:
             val = grid[6,c,1] ^ grid[6,c,0]
             row_bytes.append(val)
        else:
             row_bytes.append(0) 
             
    # Calculate Delta: Byte[i] - Byte[i-1]
    deltas = []
    for i in range(1, len(row_bytes)):
        d = (row_bytes[i] - row_bytes[i-1]) % 256
        deltas.append(chr(d) if 32 <= d <= 126 else '.')
        
    print(f"[ROW 6 DELTA]: {''.join(deltas)}")


if __name__ == "__main__":
    bit_shift_scan()
    delta_decode()
