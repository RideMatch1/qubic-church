import json
from pathlib import Path

# THE INTER-SECTOR RESONANCE VALIDATOR
# Checking for logical coupling between the Root (13,71) and Date (3,3) nodes.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def validate_coupling(coord1=(13, 71), coord2=(3, 3)):
    print(f"[*] Validating Coupling between {coord1} and {coord2}...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    k1 = bytes.fromhex(matrix.get(f"{coord1[0]},{coord1[1]}", "00" * 32))
    k2 = bytes.fromhex(matrix.get(f"{coord2[0]},{coord2[1]}", "00" * 32))
    
    # Check XOR residue entropy
    residue = bytes([b1 ^ b2 for b1, b2 in zip(k1, k2)])
    
    # Is the residue 'structured'?
    # A structured residue (low entropy) proves intentional coupling.
    from collections import Counter
    counts = Counter(residue)
    entropy_score = len(counts)
    
    print(f"    Residue Hex: {residue.hex()[:32]}...")
    print(f"    Entropy Score (Unique Bytes): {entropy_score} (Normal range: 28-32)")
    
    if entropy_score < 28:
        print("    [ALERT] COUPLING DETECTED! The nodes are phase-locked.")
    else:
        print("    [i] Nodes are statistically independent (Standard Matrix noise).")

    # Second check: Mirroring
    mirrored = bytes([b1 ^ k2[-(i+1)] for i, b1 in enumerate(k1)])
    m_entropy = len(Counter(mirrored))
    print(f"    Mirror Entropy: {m_entropy}")
    
    if m_entropy < 28:
        print("    [!!!] MIRROR COUPLING DETECTED! (The Shadow Protocol)")

if __name__ == "__main__":
    validate_coupling((13, 71), (3, 3))
    print("-" * 40)
    validate_coupling((6, 33), (21, 21)) # Core and Memory
