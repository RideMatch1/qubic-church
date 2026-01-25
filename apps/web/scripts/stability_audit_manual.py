import json
from pathlib import Path

# THE HYPERVISOR STABILITY AUDIT (MANUAL HASHES)
# Testing resonance stability across 3 verified Bitcoin hashes.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

HASHES = [
    "00000000000000000001a5fd5f29f52d51c3ad7134f89b0602bf5791b96b2387",
    "000000000000000000017355517b1e0ecbf25d5180c8e3f832c9800ddea28625",
    "000000000000000000009c0829b73c021628d0c7e3b8f8ceb9abfd3c83ea9227"
]

def compute_resonance(btc_hash, target_coord):
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    coord_key = f"{target_coord[0]},{target_coord[1]}"
    m_hex = matrix.get(coord_key, "")
    if not m_hex: return 0.0
    weight = int(m_hex[:2], 16)
    btc_bytes = bytes.fromhex(btc_hash)
    # Using the standard absolute difference resonance
    diff = sum([abs(b - weight) for b in btc_bytes])
    return (1 - (diff / (255 * len(btc_bytes)))) * 100

def stability_audit():
    print("⚖️ HYPERVISOR STABILITY AUDIT (Layer-7/Fixed Verification)...")
    
    anchors = {"CORE (6,33)": (6, 33), "ROOT-A (13,71)": (13, 71)}
    
    print(f"\n{'Hash Fragment':15} | {'CORE (6,33)':15} | {'ROOT-A (13,71)':15}")
    print("-" * 55)
    
    results = {"CORE": [], "ROOT": []}
    for h in HASHES:
        res_core = compute_resonance(h, (6, 33))
        res_root = compute_resonance(h, (13, 71))
        results["CORE"].append(res_core)
        results["ROOT"].append(res_root)
        print(f"{h[:12]}... | {res_core:13.2f}% | {res_root:14.2f}%")

    var_core = max(results["CORE"]) - min(results["CORE"])
    var_root = max(results["ROOT"]) - min(results["ROOT"])
    
    print("\n[ANALYSIS]")
    print(f"  - CORE Variance: {var_core:.2f}%")
    print(f"  - ROOT Variance: {var_root:.2f}%")
    
    if var_root < 0.5:
        print("  [!!!] ROOT ANCHOR (13,71) IS PHASE-LOCKED. It is a 'Universal Beacon'.")
    else:
        print("  [i] ROOT ANCHOR is dynamically modulated.")

if __name__ == "__main__":
    stability_audit()
