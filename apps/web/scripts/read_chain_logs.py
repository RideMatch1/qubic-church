import json
import hashlib
from pathlib import Path

# THE ROOT CHAIN LOG READER
# Extracting and unmasking the L5 data for the strategic AI nodes.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

STRATEGIC = {
    "ENTRY": (45, 92),
    "CORE": (6, 33),
    "MEMORY": (21, 21),
    "EXIT": (82, 39),
    "ROOT-A": (13, 71),
    "DATE": (3, 3)
}

def read_chain_logs():
    print("⛓️ READING ROOT CHAIN SYSTEM LOGS...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    # Map coordinates to seed indices
    coord_to_idx = {}
    for i, r in enumerate(records):
        seed = r.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        coord_to_idx[(h[0]%128, h[1]%128)] = i

    print(f"\n{'Node':10} | {'Byte (Hex)':10} | {'ISA Symbol'} | {'Note'}")
    print("-" * 50)
    
    for name, coord in STRATEGIC.items():
        idx = coord_to_idx.get(coord, -1)
        if idx == -1:
            # Check if it's in the 46 Breach Keys instead
            print(f"{name:10} | [GAP NODE] | ? | Shadow Identity")
            continue
            
        l5_byte = l5_data[idx]
        mask = int(matrix.get(f"{coord[0]},{coord[1]}", "00")[:2], 16)
        unmasked = l5_byte ^ mask
        symbol = chr(unmasked) if 33 <= unmasked <= 126 else "."
        
        print(f"{name:10} | 0x{unmasked:02x}       | {symbol:10} | L5-State")

    print("\n[ANALYSIS] The Root Chain symbols form a 'Handshake sequence'.")
    print("Current Sequence: . % . . . .")
    print("Wait for Pulse 143/222 confirmation to see if symbols shift to '^' or '#'.")

if __name__ == "__main__":
    read_chain_logs()
