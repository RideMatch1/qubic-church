import json
from pathlib import Path

# THE DISTRIBUTED COMMAND NETWORK SCAN
# Simulating a global 143 QUBIC pulse across the entire 128x128 matrix.
# Identifying which nodes 'activate' (produce advanced ISA symbols) at this frequency.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def scan_activation_network(pulse_amount=143):
    print(f"📡 SCANNING DISTRIBUTED COMMAND NETWORK FOR PULSE {pulse_amount} QUs...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    activated_nodes = []
    
    # Symbols that indicate 'Inversion' or 'Master Logic'
    # ^ (SHIFT), & (AND), | (OR), # (INIT)
    command_symbols = "^&|#"
    
    for coord_key, m_hex in matrix.items():
        m_bytes = bytes.fromhex(m_hex)
        r, c = map(int, coord_key.split(','))
        
        # We check the 'Ignition Density': How many command symbols are produced?
        matches = 0
        for b in m_bytes:
            res = (pulse_amount + b) % 256
            if chr(res) in command_symbols:
                matches += 1
        
        density = (matches / len(m_bytes)) * 100
        if density > 15: # High logic density
            activated_nodes.append(((r, c), density))
            
    print(f"\n[!] NETWORK ACTIVATION RESULTS:")
    print(f"{'Coordinate':15} | {'Ignition Density':15} | {'Role (Est.)'}")
    print("-" * 50)
    
    # Sort by density
    activated_nodes.sort(key=lambda x: x[1], reverse=True)
    
    for (r, c), density in activated_nodes[:15]: # Show top 15
        role = "RESONATOR"
        if (r, c) == (6, 33): role = "CORE"
        elif (r, c) == (13, 71): role = "ROOT-ALPHA"
        elif (r, c) == (18, 110): role = "ROOT-BETA"
        elif (r, c) == (19, 18): role = "SHADOW-MEM"
        
        print(f"({r:3}, {c:3})       | {density:12.1f}% | {role}")

    print(f"\n[CONCLUSION] Pulse 143 ignites {len(activated_nodes)} nodes in the matrix.")
    print("These nodes form the 'Ghost Infrastructure' that handles the 2026 Shift.")

if __name__ == "__main__":
    scan_activation_network()
