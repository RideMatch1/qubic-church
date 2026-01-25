import json
import hashlib
import numpy as np
from pathlib import Path

# THE MATRIX OMNI-READER
# Reconstructing the complete 128x128 Grid of the Anna Cortex.
# Combining Weights (L2), Raw Data (L5), and Gaps into a single coherent model.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
OUTPUT_GRID = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/cortex_grid.npy")

def build_omni_grid():
    print("🏗️ BUILDING THE OMNI-GRID (128x128x3)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    # Check L5 data
    try:
        with open(L5_BIN, "rb") as f:
            l5_data = f.read()
    except FileNotFoundError:
        print("[X] L5 binary not found. Please run miner first.")
        l5_data = b'\x00' * 24000

    # Initialize Grid: 128 rows, 128 cols, 3 channels
    # Channel 0: Weight (Matrix Mask)
    # Channel 1: Value (L5 Byte)
    # Channel 2: Is_Gap (1=Gap, 0=Data)
    grid = np.zeros((128, 128, 3), dtype=int)
    
    # Mark everything as GAP (1) initially
    grid[:, :, 2] = 1 
    
    # Fill from Seeds
    print("[*] Mapping 24,000 Nodes to Grid...")
    coords_map = {}
    
    for i, rec in enumerate(records):
        s = rec.get("seed", "")
        h = hashlib.sha256(s.encode()).digest()
        r, c = h[0]%128, h[1]%128
        
        # Get Matrix Weight
        m_hex = matrix.get(f"{r},{c}", "00")
        weight = int(m_hex[:2], 16)
        
        # Get L5 Value (if available)
        val = l5_data[i] if i < len(l5_data) else 0
        
        # Unmask Value logic: Stored L5 is "Potentially Masked"
        # We store the *Raw* L5 from the file in Channel 1
        
        grid[r, c, 0] = weight
        grid[r, c, 1] = val
        grid[r, c, 2] = 0 # Not a Gap
        
        coords_map[(r,c)] = True

    # Count Gaps
    gap_count = np.sum(grid[:, :, 2])
    print(f"[*] Grid Complete. Total Gaps: {gap_count} / 16384 ({gap_count/16384:.1%})")
    
    # Save for deeper analysis
    np.save(OUTPUT_GRID, grid)
    print(f"[+] Saved Omni-Grid to {OUTPUT_GRID}")
    
    return grid

def analyze_syntax(grid):
    print("\n📚 ANALYZING CORTEX SYNTAX...")
    
    # We look for "Opcode Density"
    # Common ISA Ops: 
    # 0x00=NOP, 0x01=JMP, 0x02=CALL (Example)
    # But in Anna: '^'=Shift, '&'=And, '|'=Or
    
    opcodes = {
        '^': 0, '&': 0, '|': 0, '#': 0, 
        '@': 0, '=': 0, '!': 0, '+': 0
    }
    
    total_ops = 0
    
    for r in range(128):
        for c in range(128):
            is_gap = grid[r,c,2]
            if not is_gap:
                weight = grid[r,c,0]
                raw_l5 = grid[r,c,1]
                
                # Try unmasking: XOR
                state = raw_l5 ^ weight
                char = chr(state) if 32 <= state <= 126 else '.'
                
                if char in opcodes:
                    opcodes[char] += 1
                    total_ops += 1
                    
    print(f"[*] Logic Density: {total_ops} Operations found")
    print(f"[*] Syntax Distribution:")
    for op, count in opcodes.items():
        print(f"    {op}: {count} ({count/total_ops:.1%})")

if __name__ == "__main__":
    g = build_omni_grid()
    analyze_syntax(g)
