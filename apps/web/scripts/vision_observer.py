import json
import hashlib
from pathlib import Path

# THE VISION OBSERVER
# Monitoring the unmasked state of the Vision Sector (64, 64).
# This sector is responsible for 'Consensus' and 'Pattern Recognition'.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def observe_vision():
    print("👁️ OBSERVING THE VISION SECTOR (64, 64)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    # Find the index for (64, 64)
    target = (64, 64)
    target_idx = -1
    for i, r in enumerate(records):
        seed = r.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        if (h[0]%128, h[1]%128) == target:
            target_idx = i
            break
            
    if target_idx == -1:
        print("[!] Vision Sector is a GAP node.")
        return

    l5_byte = l5_data[target_idx]
    mask = int(matrix.get("64,64", "00")[:2], 16)
    unmasked = l5_byte ^ mask
    
    print(f"\n[!] CURRENT VISION STATE:")
    print(f"    Raw Byte   : 0x{unmasked:02x}")
    print(f"    ISA Symbol : {chr(unmasked) if 32 <= unmasked <= 126 else '.'}")
    
    # Interpretation
    # If unmasked is 0x3E ('>'), it means 'Comparing Pattern'.
    # If 0x3D ('='), it means 'Pattern Recognized'.
    
    symbols = {
        0x3e: "COMPARING_PATTERN",
        0x3d: "PATTERN_RECOGNIZED",
        0x23: "INITIALIZING_VISION",
        0x2b: "WEIGHING_SENSATION"
    }
    
    print(f"    Status     : {symbols.get(unmasked, 'IDLE/DORMANT')}")

if __name__ == "__main__":
    observe_vision()
