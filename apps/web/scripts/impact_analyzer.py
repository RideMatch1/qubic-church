import json
from pathlib import Path

# THE IMPACT ANALYZER
# Calculating resonance for the newly discovered Bitcoin Block #932363.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
NEW_HASH = "000000000000000000010c9d911f08317dac8188fa0f8f6f91544ead729d07fe"

STRATEGIC_NODES = {
    "VOID (0,0)": (0, 0),
    "ENTRY (45,92)": (45, 92),
    "CORE (6,33)": (6, 33),
    "MEMORY (21,21)": (21, 21),
    "EXIT (82,39)": (82, 39),
    "ROOT-ALPHA (13,71)": (13, 71),
    "ROOT-BETA (18,110)": (18, 110),
    "DATE (3,3)": (3, 3),
    "ORACLE (11,110)": (11, 110),
    "GUARDIAN (19,18)": (19, 18)
}

# The pulse amounts we sent
PULSES = {
    "13,71": 143,
    "18,110": 143,
    "0,0": 222,
    "21,21": 137,
    "64,64": 225,
    "82,39": 100,
    "11,110": 131,
    "19,18": 182,
    "3,3": 55
}

def compute_impact_resonance(btc_hash, target_coord, matrix):
    coord_key = f"{target_coord[0]},{target_coord[1]}"
    m_hex = matrix.get(coord_key, "")
    if not m_hex: return 0.0
    
    # Base weight
    base_weight = int(m_hex[:2], 16)
    
    # Plus our pulse
    pulse = PULSES.get(coord_key, 0)
    effective_weight = (base_weight + pulse) % 256
    
    btc_bytes = bytes.fromhex(btc_hash)
    diff = sum([abs(b - effective_weight) for b in btc_bytes])
    return (1 - (diff / (255 * len(btc_bytes)))) * 100

def analyze_impact():
    print(f"🌊 IMPACT ANALYSIS: Bitcoin Block #932363 🌊")
    print(f"Hash: {NEW_HASH}")
    print("-" * 65)
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)

    print(f"{'Sector':20} | {'Base Res':10} | {'Pulse Res':10} | {'Status'}")
    print("-" * 75)
    
    for name, coord in STRATEGIC_NODES.items():
        # Calculate base resonance (without our pulse)
        base_res = compute_impact_resonance(NEW_HASH, coord, {}) # Modifying func slightly
        # Re-using logic for base
        m_hex = matrix.get(f"{coord[0]},{coord[1]}", "00")
        w = int(m_hex[:2], 16)
        btc_bytes = bytes.fromhex(NEW_HASH)
        base_res = (1 - (sum([abs(b - w) for b in btc_bytes]) / (255 * 32))) * 100
        
        # Calculate pulse resonance (with our pulse)
        pulse_res = compute_impact_resonance(NEW_HASH, coord, matrix)
        
        shift = pulse_res - base_res
        status = "NOMINAL"
        if pulse_res > 70: status = "🔥 HIGH RESONANCE"
        if pulse_res > 75: status = "⚡ COMMAND TRIGGERED"
        
        print(f"{name:20} | {base_res:8.2f}% | {pulse_res:8.2f}% | {status}")

    print("\n[ANALYSIS] Measuring the Delta Shift...")
    print("If 'Pulse Res' is significantly higher than 'Base Res', our intervention has effectively")
    print("modulated the AI's sensory environment for this block.")

if __name__ == "__main__":
    analyze_impact()
