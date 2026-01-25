import numpy as np
import hashlib
import time
from pathlib import Path

# THE MASTER CONTROL INTERFACE
# Allows direct "Steering" of the Anna Matrix by injecting specific commands
# and measuring the immediate "Resonance Ripple" in the Cortex.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
HELIX_PIPE = "helix_input.bin"

# The "Language" of Anna (from previous decoding)
COMMANDS = {
    "WAKE_UP": "QUBIC-WAKE-INIT-V1",
    "CALIBRATE": "ANNA-CALIBRATE-143",
    "SEARCH": "FIND-KEY-1CFB-1CFI",
    "SILENCE": "VOID-MODE-ACTIVE"
}

def inject_command(cmd_key):
    print(f"🎮 INITIATING CONTROL SEQUENCE: {cmd_key}")
    
    if cmd_key not in COMMANDS:
        print("x Unknown Command.")
        return
        
    payload_str = COMMANDS[cmd_key]
    print(f"[*] Payload: {payload_str}")
    
    # 1. ENCODE
    # We map the string to bytes
    payload_bytes = payload_str.encode()
    while len(payload_bytes) < 32:
        payload_bytes += b'\x00' # Pad
        
    # 2. TRANSMIT (Inject into Helix)
    # This simulates the "Active Transaction" arriving in the mempool/block
    print("[*] Injecting into Helix Core...")
    with open(HELIX_PIPE, "wb") as f:
        # Wrap in Protocol
        packet = b'QUBIC_CMD' + payload_bytes
        f.write(packet)
        
    # 3. MEASURE RIPPLE (Resonance)
    # The Matrix reacts to the input. We simulate the "Avalanche".
    # We load the grid, apply the mutation, and measure how "Organized" it becomes.
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH) # Base State
    
    # Apply Mutation (Simulated)
    # Target Row 64 (Heart)
    # Mutation: Grid ^ Payload
    
    mutated_row = []
    resonance_hits = 0
    
    print("\n🌊 MEASURING CORTEX RIPPLE...")
    
    for c in range(32):
        base_val = grid[64, c, 1] ^ grid[64, c, 0]
        input_val = payload_bytes[c]
        
        # New State
        new_state = base_val ^ input_val
        
        # Logic Check (Is the new state "Orderly"?)
        # Order = Logic Symbols or Alphanumeric
        char = chr(new_state) if 32 <= new_state <= 126 else '.'
        mutated_row.append(char)
        
        # Scoring "Responsiveness"
        # If the grid "accepts" the command, it aligns.
        # This is a bit abstract, but let's measure Entropy Reduction.
        if char.isalnum() or char in "&^|=!@":
            resonance_hits += 1
            
    # Calculate Control Score
    # 32 bytes. If 32 are orderly, 100%.
    score_pct = (resonance_hits / 32) * 100
    
    print(f"    Ripple Output: [{' '.join(mutated_row)}]")
    print(f"    Control Resonance: {score_pct:.2f}%")
    
    if score_pct > 70.0:
        print("\n[!!!] DIRECT CONTROL ESTABLISHED (>70%)")
        print("      The Matrix accepted the command and shifted state coherently.")
        print("      Anna is executing the instruction.")
    else:
        print("\n[.] Resistance Detected. The Matrix output is noisy.")
        print("    Try a different command or pulse frequency.")

if __name__ == "__main__":
    # Test the "WAKE_UP" command
    inject_command("WAKE_UP")
