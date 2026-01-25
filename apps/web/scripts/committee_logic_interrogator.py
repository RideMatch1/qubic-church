import json
from pathlib import Path

# Paths
L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
COMMITTEE_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/executive_committee.json")

def analyze_committee_scripts():
    print("[*] Interrogating Executive Committee Logic Slices (Layer-5 FULL)...")
    
    with open(COMMITTEE_JSON, "r") as f:
        committee = json.load(f)
        
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    print("\n[!] CORE LOGIC EXTRACTED PER SECTOR:")
    
    for name, info in committee.items():
        start, end = info['id_range']
        # Each ID contributes 1 byte in Layer-5
        sector_logic = l5_data[start:end]
        
        # Identify symbolic density
        # In Qubic/Base26, symbols might be hidden. 
        # But let's look for ASCII patterns first.
        symbol_count = sum(1 for b in sector_logic if not (48 <= b <= 57 or 65 <= b <= 90 or 97 <= b <= 122 or b == 32))
        symbol_density = symbol_count / len(sector_logic) if len(sector_logic) > 0 else 0
        
        # Snippet as hex and char
        snippet_hex = sector_logic[:16].hex()
        snippet_ascii = "".join([chr(b) if 32 <= b <= 126 else "." for b in sector_logic[:32]])
        
        print(f"  - {name:7} | Hex: {snippet_hex} | SymDens: {symbol_density:.2%}")
        print(f"    Script Trace: [{snippet_ascii}]")

if __name__ == "__main__":
    analyze_committee_scripts()
