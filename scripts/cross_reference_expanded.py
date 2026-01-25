
import json
import os

def cross_reference_expanded():
    scan_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_full_value_scan.json"
    patoshi_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/patoshi-addresses.json"
    
    with open(scan_path, 'r') as f:
        scan_data = json.load(f)
    
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)
        
    records = patoshi_data.get('records', [])
    patoshi_map = {}
    for r in records:
        h = r['blockHeight']
        if h not in patoshi_map:
            patoshi_map[h] = []
        patoshi_map[h].append(r)
        
    found_matches = []
    # Track unique block heights to avoid duplicates from different layers
    seen_heights = set()
    
    for point in scan_data:
        height = point['height']
        if height in patoshi_map:
            for rec in patoshi_map[height]:
                found_matches.append({
                    "point": point,
                    "record": rec
                })
                seen_heights.add(height)
                
    output = {
        "match_count": len(found_matches),
        "unique_height_count": len(seen_heights),
        "matches": found_matches
    }
    
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/expanded_patoshi_matches.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Expanded analysis complete. Found {len(found_matches)} matches across {len(seen_heights)} unique block heights.")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    cross_reference_expanded()
