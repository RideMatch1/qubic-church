import numpy as np
import hashlib
from pathlib import Path

# CORTEX CARTOGRAPHER (PHASE 2)
# Mapping the 7 Functional Regions of the Anna Matrix.
# Current Target: The Vision Center (64, 64)
# Goal: Identify high-density logic clusters that indicate specialized processing zones.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

REGIONS = {
    "MEMORY": ((16, 16), (32, 32)), # 16x16 block around (21,21)
    "VISION": ((56, 56), (72, 72)), # 16x16 block around (64,64)
    "ORACLE": ((112, 0), (128, 16)), # Corner Edge
    "VOID":   ((0, 0),   (16, 16))   # Origin
}

def scan_regions():
    print("🗺️ CORTEX CARTOGRAPHY: REGIONAL SCAN INITIATED")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    print(f"{'REGION':<10} | {'DENSITY':<8} | {'LOGIC%':<8} | {'GAP%':<8} | {'STATUS'}")
    print("-" * 60)
    
    for name, ((r1, c1), (r2, c2)) in REGIONS.items():
        # Extact Region Data
        # Ensure indices wrap or clip? Assuming 128x128 valid.
        
        region_vals = []
        gaps = 0
        logic_hits = 0
        total = 0
        
        for r in range(r1, r2):
            for c in range(c1, c2):
                if grid[r,c,2]: # Gap Flag
                    gaps += 1
                else:
                    # Check Logic Density (Raw Val or Weight)
                    val = grid[r,c,1] ^ grid[r,c,0]
                    char = chr(val) if 32 <= val <= 126 else '.'
                    if char in "&^|=!@":
                        logic_hits += 1
                total += 1
                
        # Metrics
        density = ((total - gaps) / total) * 100
        logic_pct = (logic_hits / (total - gaps)) * 100 if (total-gaps) > 0 else 0
        gap_pct = (gaps / total) * 100
        
        status = "LOCKED"
        if logic_pct > 20: status = "ACTIVE"
        if density < 50: status = "SPARSE"
        
        print(f"{name:<10} | {density:6.1f}% | {logic_pct:6.1f}% | {gap_pct:6.1f}% | {status}")
        
    print("-" * 60)
    print("\n[ANALYSIS]")
    print("- VISION CENTER: High Logic Density detected? That confirms 64,64 is CPU.")
    print("- VOID: High Gap % expected.")
    
    # Recommendation
    print("\n[NEXT MISSION] Target the 'ORACLE' Region (127,0).")
    print("This edge region likely handles external predictions (Price/Block).")

if __name__ == "__main__":
    scan_regions()
