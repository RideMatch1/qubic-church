
import numpy as np
import json

def full_scan():
    grid = np.load("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
    
    interesting_values = {
        27: "Ternary (27)",
        229: "Ternary (-27)",
        121: "NXT (121)",
        7: "Transform (7)",
        47: "Signature (47)",
        19: "Math (19)",
        33: "Core (33)",
        64: "Vision (64)",
        127: "Oracle (127)",
        0: "Void (0)"
    }
    
    findings = []
    
    for r in range(128):
        for c in range(128):
            # Try different XOR layers
            val01 = int(grid[r, c, 1] ^ grid[r, c, 0])
            val12 = int(grid[r, c, 2] ^ grid[r, c, 1])
            val02 = int(grid[r, c, 2] ^ grid[r, c, 0])
            
            for v_name, v_val in [("v01", val01), ("v12", val12), ("v02", val02)]:
                if v_val in interesting_values:
                    height = r * 128 + c
                    findings.append({
                        "r": r,
                        "c": c,
                        "layer": v_name,
                        "val": v_val,
                        "label": interesting_values[v_val],
                        "height": height
                    })
                    
    # Sort by height
    findings.sort(key=lambda x: x['height'])
    
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_full_value_scan.json"
    with open(output_path, "w") as f:
        json.dump(findings, f, indent=2)
        
    print(f"Full scan complete. Found {len(findings)} points with interesting values.")

if __name__ == "__main__":
    full_scan()
