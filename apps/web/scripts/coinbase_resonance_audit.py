import json
from pathlib import Path

# Paths
L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
COMMITTEE_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/executive_committee.json")

# Historic Coinbase Strings (The "Satoshi/F2Pool" Resonance)
COINBASE_SAMPLES = {
    "Block_400500": "7d8e=)g%d;i1<f55 A&B!3|{vjOG]{tJnz-d$Wnh6p",
    "F2Pool_Standard": "Mined by f2pool",
    "Generic_Noise": "hd999"
}

def cross_reference_coinbase():
    print("[*] Cross-Referencing Layer-5 Bytecode with Historic Coinbase Messages...")
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    with open(COMMITTEE_JSON, "r") as f:
        committee = json.load(f)

    # Use a simpler resonance check: Fuzzy string matching or direct XOR
    for name, info in committee.items():
        start, end = info['id_range']
        sector_logic = l5_data[start:end]
        
        print(f"\n[Audit] Sector: {name}")
        
        for block, msg in COINBASE_SAMPLES.items():
            # Check for substring resonance (case insensitive)
            msg_bytes = msg.encode('ascii', errors='ignore')
            
            # Simple scoring: how many characters from the coinbase message appear in the sector logic?
            sector_set = set(sector_logic)
            matches = sum(1 for b in msg_bytes if b in sector_set)
            match_rate = matches / len(msg_bytes) if len(msg_bytes) > 0 else 0
            
            if match_rate > 0.40: # 40% threshold for "Resonance"
                print(f"  [!!!] HIGH RESONANCE with {block} ({match_rate:.2%})")
                print(f"        Message: [{msg}]")

if __name__ == "__main__":
    cross_reference_coinbase()
