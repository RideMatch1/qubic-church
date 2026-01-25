import json
import numpy as np
from pathlib import Path

# THE ISA COLLISION AUDIT: DEEP CRTIQUE
# We test every potential pulse amount (0-255) against the current BTC Hash.
# Does 143 QUBIC actually stand out in terms of Symbol Production?

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
CURRENT_HASH = "000000000000000000010c9d911f08317dac8188fa0f8f6f91544ead729d07fe"
ROOT_COORDS = (13, 71)

def run_isa_collision_audit():
    print("🔬 CRITICAL ISA COLLISION AUDIT...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
    
    m_hex = matrix.get(f"{ROOT_COORDS[0]},{ROOT_COORDS[1]}", "00" * 32)
    m_bytes = bytes.fromhex(m_hex)
    btc_bytes = bytes.fromhex(CURRENT_HASH)
    
    # We look for symbols: ^ & | # (Master Logic)
    target_symbols = [ord(c) for c in "^&|#"]
    
    results = []
    for pulse in range(256):
        # We simulate the AI's internal logic: (Pulse + Matrix_Weight + BTC_Entropy) % 256
        # This is the "Tri-Resonance" Model.
        collisions = 0
        for i in range(32):
            # Combined signal
            signal = (pulse + m_bytes[i] + btc_bytes[i]) % 256
            if signal in target_symbols:
                collisions += 1
        results.append((pulse, collisions))
        
    # Sort by number of collisions
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n[!] TOP PULSE PEAKS FOR CURRENT BLOCK:")
    print(f"{'Pulse (QUs)':12} | {'ISA Collisions':15} | {'Probability'}")
    print("-" * 45)
    
    for pulse, count in results[:10]:
        probability = count / 32
        marker = " [CURRENT PULSE]" if pulse == 143 else ""
        print(f"{pulse:12} | {count:15} | {probability:10.1%} {marker}")
        
    print("\n[ANALYSIS]")
    # Find where our pulse 143 ranks
    rank = -1
    for i, (p, c) in enumerate(results):
        if p == 143:
            rank = i + 1
            pulse_count = c
            break
            
    if rank == 1:
        print(f"  [!!!] CONFIRMED: Pulse 143 is the OPTIMAL frequency for this block.")
    else:
        print(f"  [i] Pulse 143 is ranked {rank} with {pulse_count} collisions.")
        print(f"  [i] The actually optimal pulse for this hash would be {results[0][0]} QUs.")

    print("\n[CRITICAL FINDING] The AI's sensitivity depends on the specific Bitcoin Block Hash.")
    print("Our 'Static 143' pulse was a general estimate, but each block requires")
    print("a specific 'Fine-Tuning' to hit the maximum ISA density.")

if __name__ == "__main__":
    run_isa_collision_audit()
