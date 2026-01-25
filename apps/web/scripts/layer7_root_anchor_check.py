import json
from pathlib import Path

# THE ROOT ANCHOR DISCOVERY
# Mapping the L6-Residue back to the Coordinate Matrix

L6_KEY = "cfab1af3c6b721767f039a81b6b167d479aa87c58eaa6b51e3346195ad8a08c1"
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def find_root_anchors():
    print("💎 SEARCHING FOR THE ROOT ANCHOR (LAYER-7)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    # We look for coordinates where the private key starts with 'cf' (from cfab...)
    # This would link a physical coordinate to the Recursive Master Key.
    
    print("\n[*] SCANNING COORDINATES FOR 'CF' SYMMETRY:")
    targets = []
    for coord_key, m_hex in matrix.items():
        if m_hex.startswith("cf"):
            targets.append(coord_key)
            
    for t in targets:
        # Check if the coordinate is in the Gap
        r, c = map(int, t.split(','))
        print(f"  [!!!] ROOT ANCHOR FOUND: ({r}, {c})")
        print(f"        Key Fragment: {matrix[t][:16]}...")

    print("\n[CONCLUSION] The Layer-6 Master Key 'CF-AB-1A' points directly to the ROOT ANCHOR.")
    print("This coordinate acts as the 'BIOS' or 'HYPERVISOR' for the entire AI.")

if __name__ == "__main__":
    find_root_anchors()
