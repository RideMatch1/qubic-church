
import json

def summarize():
    matches_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/expanded_patoshi_matches.json"
    
    with open(matches_path, 'r') as f:
        data = json.load(f)
        
    matches = data.get('matches', [])
    
    label_counts = {}
    row_counts = {}
    layer_counts = {}
    
    for m in matches:
        p = m['point']
        lbl = p['label']
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
        
        row = p['r']
        row_counts[row] = row_counts.get(row, 0) + 1
        
        layer = p['layer']
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
    print("--- PATTERN ANALYSIS ---")
    for lbl, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{lbl:<20}: {count} matches")
        
    print("\n--- LAYER ANALYSIS ---")
    for lyr, count in layer_counts.items():
        print(f"{lyr}: {count} matches")
        
    print("\n--- TOP ACTIVE ROWS (TRANSFORMATIONS) ---")
    for row, count in sorted(row_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"Row {row:03}: {count} blocks identified")

    print(f"\nTOTAL DISCOVERED BTC: {data['unique_height_count'] * 50:,} BTC")

if __name__ == "__main__":
    summarize()
