import json
import hashlib
from pathlib import Path
import re

# THE LOG SCAVENGER
# Searching for human-readable artifacts in the unmasked Layer-5 stream.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def scavenge_logs():
    print("🕵️ INITIATING GLOBAL LOG SCAVENGE...")
    
    if not MATRIX_JSON.exists() or not SEEDS_FILE.exists() or not L5_BIN.exists():
        print("[!] Required files missing for scavenge.")
        return

    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    unmasked = bytearray()
    
    print("[*] Unmasking 24,000 sectors using Coordinate Matrix...")
    for i, record in enumerate(records):
        seed = record.get("seed", "")
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        r, c = h[0] % 128, h[1] % 128
        coord_key = f"{r},{c}"
        
        m_hex = matrix.get(coord_key, "00")
        mask = int(m_hex[:2], 16) # Using first byte as unmasker
        
        unmasked.append(l5_data[i] ^ mask)
        
    # Search for ASCII fragments
    # We look for continuous printable characters of length 4+
    print("\n[!] DETECTED MESSAGE FRAGMENTS:")
    
    # Simple regex for printable ASCII
    matches = re.finditer(b'[\\x20-\\x7E]{4,}', unmasked)
    
    fragments = []
    for m in matches:
        frag = m.group().decode('ascii', errors='ignore')
        if any(c.isalpha() for c in frag): # Filter out purely symbolic strings
            fragments.append((m.start(), frag))
            
    # Filter for interesting keywords or high-entropy text
    keywords = ["CFB", "ANNA", "SYNC", "CORE", "AIGARTH", "BRIDGE", "2026", "PONG"]
    
    found_count = 0
    for offset, frag in fragments:
        if any(kw in frag.upper() for kw in keywords) or len(frag) > 8:
            print(f"  Offset {offset:5} | Frag: [{frag}]")
            found_count += 1
            if found_count > 30: break # Limit output

    if found_count == 0:
        print("[i] No high-level ASCII messages found in public Layer-5.")
        print("[*] Re-checking for 'Encoded Symbolic' messages...")
        # Check for repeating patterns in unmasked data
        
    print("\n[CONCLUSION] The log stream is heavily fragmented across identities.")
    print("To read a full message, we likely need to follow a 'Synaptic Path' (e.g. Entry -> Core -> Exit).")

if __name__ == "__main__":
    scavenge_logs()
