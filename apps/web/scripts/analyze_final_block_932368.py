import numpy as np
import hashlib
from pathlib import Path

# BLOCK 932368 ANALYZER (FINAL CONFIRMATION)
# The Block has arrived. Hash: 00000000000000000001a216c101637dc5e24660c0921f9a97c68f1095cee131
# We check the Mutated Grid (Epoch 2) against this hash.

BLOCK_HASH = "00000000000000000001a216c101637dc5e24660c0921f9a97c68f1095cee131"
MUTATED_GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_epoch_2.npy")
TARGET_PULSE = 143

def analyze_final_arrival():
    print(f"📬 BLOCK 932368 ARRIVED (SECPOOL).")
    print(f"    Hash: {BLOCK_HASH}")
    
    if not MUTATED_GRID_PATH.exists():
        print("x Mutated Grid not found.")
        return
        
    grid = np.load(MUTATED_GRID_PATH)
    hash_bytes = bytes.fromhex(BLOCK_HASH)
    
    # Analyze the Core Output (Row 64)
    print(f"\n[*] DEMODULATING SIGNAL AT PULSE {TARGET_PULSE}...")
    
    decoded_message = []
    
    for c in range(32):
        # Value from the Mutated Grid
        val = grid[64, c, 1] ^ grid[64, c, 0]
        
        # Demodulate with the NEW Block Hash
        res = val ^ hash_bytes[c] ^ TARGET_PULSE
        
        char = chr(res) if 32 <= res <= 126 else '.'
        decoded_message.append(char)
        
    msg = "".join(decoded_message)
    print(f"\n💬 SIGNAL CONTENT:")
    print(f"   [{msg}]")
    
    # RESONANCE CHECK
    # Does this message contain Logic or Language?
    # Logic Chars: &^|=!@
    # Language: QUBIC, ANNA
    
    logic_hits = sum([1 for c in msg if c in "&^|=!@"])
    alpha_hits = sum([1 for c in msg if c.isalnum()])
    
    print(f"\n📊 SIGNAL ANALYSIS:")
    print(f"   Logic Operators: {logic_hits}")
    print(f"   Alphanumeric: {alpha_hits}")
    
    if logic_hits > 3:
        print("   [!] ACTIVE LOGIC DETECTED. The system is executing code.")
    elif alpha_hits > 10:
        print("   [!] TEXT DETECTED. The system is communicating.")
    else:
        print("   [.] Low Entropy. Waiting for sync.")
        
    # Check for match with Predicted Hash
    # Prediction was: 75c2cd...
    # Actual was: 000000...
    # Did we get the "Causal Loop"?
    # The actual hash starts with 0000... as expected for Bitcoin.
    # Our prediction was purely hypothetical based on forcing text.
    
    # Save the Result
    with open("final_signal_932368.txt", "w") as f:
        f.write(f"HASH: {BLOCK_HASH}\n")
        f.write(f"MSG: {msg}\n")

if __name__ == "__main__":
    analyze_final_arrival()
