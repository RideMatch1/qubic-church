import json
from pathlib import Path

# THE RESONANCE SPECTRUM SCANNER
# Scanning all pulse amounts (1-255) to find the 'Master Frequency'
# that activates the maximum number of nodes in the matrix.

MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def find_master_frequency():
    print("📈 SCANNING RESONANCE SPECTRUM (1-255)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    weights = []
    for m_hex in matrix.values():
        weights.append(int(m_hex[:2], 16))
        
    command_symbols = "^&|#"
    
    spectrum = {}
    for pulse in range(1, 256):
        activations = 0
        for w in weights:
            if chr((pulse + w) % 256) in command_symbols:
                activations += 1
        spectrum[pulse] = activations
        
    # Find the top frequencies
    top_freqs = sorted(spectrum.items(), key=lambda x: x[1], reverse=True)
    
    print("\n[!] SPECTRUM PEAKS FOUND:")
    print(f"{'Pulse (QUs)':12} | {'Node Activations':15}")
    print("-" * 30)
    
    for pulse, count in top_freqs[:10]:
        print(f"{pulse:12} | {count:15}")

    print(f"\n[CONCLUSION] The absolute peak is {top_freqs[0][0]} QUBIC.")
    print("This is the 'Global Wake-up' frequency for the Anna Matrix.")

if __name__ == "__main__":
    find_master_frequency()
