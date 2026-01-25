import json
from pathlib import Path
from collections import Counter

# Paths
SEEDS_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json")
OUTPUT_DIR = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/")

def run_horizontal_mining():
    print("[*] Initializing Horizontal Mining Operation...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(SEEDS_FILE, "r") as f:
        data = json.load(f)
    
    records = data.get("records", [])
    total = len(records)
    print(f"[+] Processing {total} identities.")
    
    # Significant positions in Base26 encoding (last char of uint64 groups)
    positions = [13, 27, 41, 55, 59]
    
    bitstreams = {pos: "" for pos in positions}
    
    for record in records:
        # We use realIdentity for the 'hard' crypto artifacts
        identity = record.get("realIdentity", "")
        if len(identity) < 60:
            continue
            
        for pos in positions:
            bitstreams[pos] += identity[pos]

    # Analysis
    results = {}
    for pos, stream in bitstreams.items():
        counts = Counter(stream)
        entropy = sum(-(count/total) * (count/total) for count in counts.values()) # Simple freq diversity
        
        results[pos] = {
            "distribution": dict(counts),
            "sample": stream[:100],
            "entropy_score": entropy
        }
        
        # Save raw stream
        stream_file = OUTPUT_DIR / f"pos_{pos}_stream.txt"
        with open(stream_file, "w") as f:
            f.write(stream)
            
    # Save Summary
    with open(OUTPUT_DIR / "horizontal_mining_summary.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"[+] Horizontal Mining Complete. Streams saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_horizontal_mining()
