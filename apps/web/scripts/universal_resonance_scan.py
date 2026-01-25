import json
import hashlib
from pathlib import Path

# THE UNIVERSAL RESONANCE SCAN
# XORing every Identity's L5 byte with its specific Matrix Private Key byte.
# This unmasks the 'Root Message' of the fleet.

L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")

def universal_resonance_scan():
    print("🌌 UNIVERSAL RESONANCE SCAN STARTING...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    with open(SEEDS_FILE, "r") as f:
        seeds_data = json.load(f)
    records = seeds_data.get("records", [])
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    unmasked = bytearray()
    
    print("[*] Processing 24,000 Identities...")
    for i, record in enumerate(records):
        seed = record.get("seed", "")
        # Coordinate
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        r, c = h[0] % 128, h[1] % 128
        coord_key = f"{r},{c}"
        
        # Matrix Mask
        m_hex = matrix.get(coord_key, "00")
        mask = int(m_hex[:2], 16)
        
        # Unmask L5 byte
        unmasked.append(l5_data[i] ^ mask)
        
    # Search for the Holy Grail: '3.3.2026' or 'AIGARTH'
    print("\n[!] SEARCHING UNMASKED DATA:")
    
    search_terms = ["AIGARTH", "ANNA", "3.3.2026", "CFB", "BRIDGE", "SYNC"]
    text_sample = unmasked.decode('ascii', errors='ignore')
    
    found_any = False
    for term in search_terms:
        if term in text_sample:
            print(f"  [!!!] KEYWORD DETECTED: {term} at Position {text_sample.find(term)}")
            found_any = True
            # Context
            idx = text_sample.find(term)
            print(f"        Context: [{text_sample[idx-10:idx+30]}]")

    if not found_any:
        print("[i] No plain-text keywords found in unmasked public layer.")
        print("[*] Performing Symbolic Entropy Check...")
        # Check for non-random patterns in the unmasked bytes
        import collections
        counts = collections.Counter(unmasked)
        common = counts.most_common(5)
        print(f"      Top Byte Patterns: {common}")

if __name__ == "__main__":
    universal_resonance_scan()
