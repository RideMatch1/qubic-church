import json
import hashlib
from pathlib import Path

# THE MEMORY LEAK SCANNER
# Scanning the public neighbors of the Gap Memory Node (21, 21).
# Checking if the 'Memory Vault' is leaking ASCII data into the surrounding fleet.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def scan_memory_leaks(target=(21, 21)):
    print(f"🕵️ SCANNING FOR MEMORY LEAKS AROUND {target}...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()

    # Map coords to L5 indices
    coord_to_idx = {}
    for i, r in enumerate(records):
        seed = r.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        coord_to_idx[(h[0]%128, h[1]%128)] = i

    r_t, c_t = target
    # Scan a 5x5 grid around the memory vault
    leak_data = bytearray()
    print(f"\n[!] NEIGHBORHOOD STATUS:")
    for r in range(r_t-2, r_t+3):
        for c in range(c_t-2, c_t+3):
            idx = coord_to_idx.get((r, c), -1)
            coord_key = f"{r},{c}"
            
            if idx != -1:
                l5_byte = l5_data[idx]
                mask = int(matrix.get(coord_key, "00")[:2], 16)
                unmasked = l5_byte ^ mask
                symbol = chr(unmasked) if 32 <= unmasked <= 126 else "."
                leak_data.append(unmasked)
                
                # Check for "ROOT" or "LOG" fragments
                print(f"  ({r:3}, {c:3}) | Symbol: {symbol} | Type: PUBLIC")
            else:
                print(f"  ({r:3}, {c:3}) | Symbol: ? | Type: GAP")

    print("\n[CONCLUSION] Reconstructed Leak Stream:")
    text = leak_data.decode('ascii', errors='ignore')
    print(f"  [{text}]")
    
    if any(kw in text.upper() for kw in ["ROOT", "ANNA", "LOG", "SYNC"]):
        print("    [ALERT] Logical correlation found in Memory Leaks!")
    else:
        print("    [i] No structured ASCII leaks detected. The Vault is secure.")

if __name__ == "__main__":
    scan_memory_leaks((21, 21)) # Memory
    print("-" * 50)
    scan_memory_leaks((6, 33))  # Core
