import json
from pathlib import Path

SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
OUTPUT_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_stream.bin")

def run_layer5_extraction():
    print("[*] Starting Layer-5 Cross-Constraint Extraction (8-bit Alignment)...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(SEEDS_FILE, "r") as f:
        data = json.load(f)
    
    records = data.get("records", [])
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    # We take 2 bits from each of the 4 constrained positions
    # [13, 27, 41, 55] -> 2 + 2 + 2 + 2 = 8 bits per identity
    positions = [13, 27, 41, 55]
    
    byte_list = []
    
    for record in records:
        identity = record.get("realIdentity", "")
        if len(identity) < 56:
            continue
            
        byte_val = 0
        valid = True
        for pos in positions:
            char = identity[pos]
            if char not in mapping:
                valid = False
                break
            # Shift 2 bits for each position
            byte_val = (byte_val << 2) | mapping[char]
            
        if valid:
            byte_list.append(byte_val)
            
    with open(OUTPUT_FILE, "wb") as f:
        f.write(bytes(byte_list))
        
    print(f"[+] Extracted {len(byte_list)} bytes to {OUTPUT_FILE}")
    
    # Quick ASCII Check
    text = bytes(byte_list).decode('ascii', errors='ignore')
    print(f"[?] Layer-5 ASCII Sample: {text[:100]}...")

if __name__ == "__main__":
    run_layer5_extraction()
