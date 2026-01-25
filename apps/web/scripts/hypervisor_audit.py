import os
import requests
import json
from pathlib import Path

# THE HYPERVISOR PROBE
# Measuring the resonance of the Root Anchors (Layer-7) after our pulse.

RPC_URL = "https://rpc.qubic.org"
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def compute_resonance(btc_hash, target_coord):
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    coord_key = f"{target_coord[0]},{target_coord[1]}"
    m_hex = matrix.get(coord_key, "")
    if not m_hex: return 0.0
    weight = int(m_hex[:2], 16)
    btc_bytes = bytes.fromhex(btc_hash)
    diff = sum([abs(b - weight) for b in btc_bytes])
    return (1 - (diff / (255 * len(btc_bytes)))) * 100

def check_hypervisor_resonance():
    print("💎 HYPERVISOR RESONANCE AUDIT (LAYER-7)...")
    
    r = requests.get("https://blockstream.info/api/blocks/tip/hash")
    btc_hash = r.text.strip()
    
    anchors = {
        "ROOT-ALPHA (13,71)": (13, 71),
        "ROOT-BETA (18,110)": (18, 110),
        "ROOT-GAMMA (6,116)": (6, 116)
    }
    
    print(f"\n[!] MEASURING HYPERVISOR SECTORS:")
    for name, coord in anchors.items():
        res = compute_resonance(btc_hash, coord)
        # Check for 'Resonance Synchronization' (Entropy peaks)
        print(f"  - {name:20} | Resonance: {res:5.2f}%")

    print("\n[ANALYSIS] If resonance is over 60%, the Hypervisor is in 'Command Mode'.")
    print("Our 1 QUBIC pulse may have triggered an L6-Interrupt.")

if __name__ == "__main__":
    check_hypervisor_resonance()
