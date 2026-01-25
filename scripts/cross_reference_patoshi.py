
import json
import os

def cross_reference():
    candidates_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/validated_btc_candidates.json"
    patoshi_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/patoshi-addresses.json"
    
    with open(candidates_path, 'r') as f:
        candidates_data = json.load(f)
    
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)
        
    records = patoshi_data.get('records', [])
    # Create a mapping from blockHeight to list of records
    patoshi_map = {}
    for r in records:
        h = r['blockHeight']
        if h not in patoshi_map:
            patoshi_map[h] = []
        patoshi_map[h].append(r)
        
    found_matches = []
    for cand in candidates_data.get('candidates', []):
        height = cand['height']
        if height in patoshi_map:
            for rec in patoshi_map[height]:
                found_matches.append({
                    "candidate": cand,
                    "record": rec
                })
                
    # Also define the 10 known blocks to check if they are in patoshi_map
    known_blocks = [73, 74, 75, 80, 89, 93, 95, 96, 120, 121, 264]
    known_matches = []
    for b in known_blocks:
        if b in patoshi_map:
            known_matches.append({
                "block": b,
                "records": patoshi_map[b]
            })
        else:
            known_matches.append({
                "block": b,
                "records": "NOT FOUND"
            })

    output = {
        "candidate_matches_count": len(found_matches),
        "candidate_matches": found_matches,
        "known_blocks_status": known_matches
    }
    
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/patoshi_cross_reference.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Analysis complete. Found {len(found_matches)} matches among matrix candidates.")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    cross_reference()
