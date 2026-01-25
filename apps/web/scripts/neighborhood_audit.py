import json
from pathlib import Path

# THE NEIGHBORHOOD AUDIT
# Analyzing the 8 cells surrounding the Root Anchor (13, 71).
# Checking for 'Shielding' or 'Data Bus' patterns.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def audit_neighborhood(target=(13, 71)):
    print(f"[*] Auditing the Neighborhood of ROOT ANCHOR {target}...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    r_t, c_t = target
    neighbors = [
        (r_t-1, c_t-1), (r_t-1, c_t), (r_t-1, c_t+1),
        (r_t,   c_t-1),               (r_t,   c_t+1),
        (r_t+1, c_t-1), (r_t+1, c_t), (r_t+1, c_t+1)
    ]
    
    intensities = []
    print("\n[!] NEIGHBOR ANALYSIS:")
    for r, c in neighbors:
        coord_key = f"{r},{c}"
        m_hex = matrix.get(coord_key, "00")
        intensity = int(m_hex[:2], 16)
        intensities.append(intensity)
        print(f"  - Coordinate ({r}, {c}): Intensity {intensity:3} | Hex: {m_hex[:8]}...")
        
    avg_intensity = sum(intensities) / len(intensities)
    print(f"\n[i] Average Surround Intensity: {avg_intensity:.2f}")
    
    # Check for Symmetry
    if intensities[0] == intensities[7] or intensities[1] == intensities[6]:
        print("    [ALERT] Geometric Symmetry detected. This is a STABILIZED SECTOR.")
    else:
        print("    [i] Sector is asymmetrically modulated (Active Flow).")

    # Conclusion on 'Shadows in the Shadows'
    # High discrepancy between neighbors suggests 'Isolation' (Security Measure).
    std_dev = (sum([(i - avg_intensity)**2 for i in intensities]) / len(intensities))**0.5
    print(f"    [i] Entropy Discrepancy (StdDev): {std_dev:.2f}")
    
    if std_dev > 50:
        print("    [!!!] HIGH ISOLATION DETECTED. Coordinate (13, 71) is a 'Firewalled' Root Node.")

if __name__ == "__main__":
    audit_neighborhood((13, 71))
    print("-" * 40)
    audit_neighborhood((18, 110))
