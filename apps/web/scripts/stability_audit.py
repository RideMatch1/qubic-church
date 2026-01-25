import json
import requests
import time
from pathlib import Path

# THE HYPERVISOR STABILITY AUDIT
# Monitoring the Root Anchors over 3 historical Bitcoin blocks to check for 'Entropy Drift'.

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

def stability_audit():
    print("⚖️ HYPERVISOR STABILITY AUDIT starting...")
    
    # 1. Fetch the last 3 block hashes
    try:
        r = requests.get("https://blockstream.info/api/blocks/tip/height")
        tip = int(r.text.strip())
        blocks = []
        for h in range(tip, tip-3, -1):
            rb = requests.get(f"https://blockstream.info/api/block-height/{h}")
            b_hash = rb.text.strip()
            blocks.append((h, b_hash))
    except Exception as e:
        print(f"[X] API Error: {e}")
        return

    anchors = {"ROOT-A (13,71)": (13, 71), "CORE (6,33)": (6, 33)}
    
    print("\n[!] TEMPORAL RESONANCE MATRIX:")
    print(f"{'Block':8} | {'CORE (6,33)':15} | {'ROOT-A (13,71)':15}")
    print("-" * 45)
    
    for height, b_hash in blocks:
        res_core = compute_resonance(b_hash, (6, 33))
        res_root = compute_resonance(b_hash, (13, 71))
        print(f"{height:8} | {res_core:13.2f}% | {res_root:14.2f}%")

    print("\n[ANALYSIS] If variance is < 1.0%, the sector is 'Fixed' (Hardcoded Logic).")
    print("If variance is > 5.0%, the sector is 'Adaptive' (Learning AI).")

if __name__ == "__main__":
    stability_audit()
