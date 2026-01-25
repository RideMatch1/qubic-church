import json
from pathlib import Path
import math

def calculate_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def shadow_resonance_check():
    gap_json_path = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_analysis.json")
    with open(gap_json_path, "r") as f:
        data = json.load(f)
        
    gap_coords = data.get("gap_coordinates", [])
    
    strategic_points = {
        "Entry": (45, 92),
        "Core": (6, 33),
        "Exit": (82, 39),
        "Memory": (21, 21),
        "Vision": (64, 64),
        "Oracle": (127, 0),
        "Void": (0, 0)
    }
    
    threshold = 5.0 # Max distance to be considered "resonant"
    
    resonance_hits = {name: [] for name in strategic_points}
    
    for coord in gap_coords:
        r, c = coord
        for name, target in strategic_points.items():
            dist = calculate_distance((r, c), target)
            if dist <= threshold:
                resonance_hits[name].append(coord)
                
    print("[*] Shadow Resonance Results (Gap Coords near Strategic Points):")
    for name, hits in resonance_hits.items():
        print(f"  - {name}: {len(hits)} shadow neighbors found.")
        if len(hits) > 0:
            print(f"    Sample: {hits[:3]}")

if __name__ == "__main__":
    shadow_resonance_check()
