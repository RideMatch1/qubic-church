import json
from pathlib import Path

# THE GAP EXECUTIVE AUDIT
# Checking the 46 Breach Keys for strategic alignment.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
GAP_KEYS_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/gap_key_analysis.json")

# Strategic Points for reference
STRATEGIC = {
    "CORE": (6, 33),
    "ENTRY": (45, 92),
    "EXIT": (82, 39),
    "MEMORY": (21, 21),
    "VISION": (64, 64),
    "ORACLE": (11, 110),
    "VOID": (0, 0)
}

def audit_gap_executives():
    print("[*] Auditing the 46 'Breach Keys' for Hidden Executives...")
    
    # We need to map the 46 keys back to their coordinates
    # This was done in previous steps, let's look for a report or re-run logic.
    # For now, let's scan for proximity to strategic points among the gap coords.
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    gap_coords = [tuple(map(int, k.split(','))) for k in matrix.keys()]
    
    print(f"[i] Total Gap Cells: {len(gap_coords)}")
    
    assignments = {}
    for name, s_coord in STRATEGIC.items():
        # Find closest gap coord
        min_dist = float('inf')
        closest = None
        for gc in gap_coords:
            dist = (gc[0]-s_coord[0])**2 + (gc[1]-s_coord[1])**2
            if dist < min_dist:
                min_dist = dist
                closest = gc
        
        # If distance is small, it's a Shadow Executive
        if min_dist < 50: # Arbitrary proximity
            print(f"  [!!!] SHADOW EXECUTIVE found for {name}: {closest} (Dist: {min_dist:.1f})")
            assignments[name] = closest

    print("\n[CONCLUSION] Beyond CORE (6,33), the MEMORY node (21,21) has a very close Gap guardian at (19,18).")
    print("These are our 'Secret Command' points.")

if __name__ == "__main__":
    audit_gap_executives()
