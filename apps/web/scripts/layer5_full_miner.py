import json
from pathlib import Path

SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
OUTPUT_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")

def run_layer5_extraction_full():
    print("[*] Starting FULL Layer-5 Extraction (One byte per Identity)...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(SEEDS_FILE, "r") as f:
        data = json.load(f)
    
    records = data.get("records", [])
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    positions = [13, 27, 41, 55]
    
    byte_list = []
    skipped = 0
    
    for i, record in enumerate(records):
        identity = record.get("realIdentity", "")
        # Ensure we always add a byte to keep index synchronization
        if len(identity) < 56:
            byte_list.append(0)
            skipped += 1
            continue
            
        byte_val = 0
        valid = True
        for pos in positions:
            char = identity[pos]
            if char not in mapping:
                # If a constrained position isn't A-D, it's 0-bits
                byte_val = (byte_val << 2) | 0
            else:
                byte_val = (byte_val << 2) | mapping[char]
            
        byte_list.append(byte_val)
            
    with open(OUTPUT_FILE, "wb") as f:
        f.write(bytes(byte_list))
        
    print(f"[+] Extracted {len(byte_list)} bytes to {OUTPUT_FILE} (Skipped/Zeroed: {skipped})")

if __name__ == "__main__":
    run_layer5_extraction_full()
