import json
import requests
import time
from pathlib import Path

# THE GLOBAL CORTEX MONITOR
# Real-time monitoring of all strategic sectors during the 'Global Wake-up' event.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

STRATEGIC_NODES = {
    "VOID (0,0)": (0, 0),
    "ENTRY (45,92)": (45, 92),
    "CORE (6,33)": (6, 33),
    "MEMORY (21,21)": (21, 21),
    "EXIT (82,39)": (82, 39),
    "ROOT-ALPHA (13,71)": (13, 71),
    "ROOT-BETA (18,110)": (18, 110),
    "DATE (3,3)": (3, 3)
}

def compute_resonance(btc_hash, target_coord, matrix):
    coord_key = f"{target_coord[0]},{target_coord[1]}"
    m_hex = matrix.get(coord_key, "")
    if not m_hex: return 0.0
    weight = int(m_hex[:2], 16)
    btc_bytes = bytes.fromhex(btc_hash)
    diff = sum([abs(b - weight) for b in btc_bytes])
    return (1 - (diff / (255 * len(btc_bytes)))) * 100

def monitor_global_event():
    print("🌍 GLOBAL CORTEX MONITOR: PHASE 2 (GHOST ACTIVATION)...")
    print("-" * 65)
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)

    # Fetch current block
    try:
        r = requests.get("https://blockstream.info/api/blocks/tip/hash")
        btc_hash = r.text.strip()
        rh = requests.get("https://blockstream.info/api/blocks/tip/height")
        height = rh.text.strip()
        print(f"[*] BTC BLOCK: #{height} | Hash: {btc_hash[:16]}...")
    except:
        print("[!] BTC API Error.")
        return

    print(f"\n{'Sector':20} | {'Resonance':10} | {'Status'}")
    print("-" * 65)
    
    for name, coord in STRATEGIC_NODES.items():
        res = compute_resonance(btc_hash, coord, matrix)
        status = "DORMANT"
        if res > 60: status = "ACTIVE"
        if res > 70: status = "CRITICAL (PULSE REACHED)"
        
        print(f"{name:20} | {res:8.2f}% | {status}")

    print("\n[ANALYSIS] Measuring the 'Ripple Effect' of the 222 QUBIC Global Wake-up.")
    print("If VOID resonance increases, the matrix baseline is shifting.")

if __name__ == "__main__":
    monitor_global_event()
