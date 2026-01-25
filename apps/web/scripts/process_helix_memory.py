import numpy as np
import os
import time
from pathlib import Path

# HELIX MEMORY PROCESSOR
# Simulates the Qubic "Epoch Processing".
# Reads the 'helix_input.bin' (The Injection).
# Applies the changes to the Cortex Grid (Weights).
# "The Avalanche Effect"

INPUT_PIPE = "helix_input.bin"
GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
MUTATED_GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_epoch_2.npy")

def process_memory():
    print("🧠 PROCESSING HELIX MEMORY (EPOCH UPDATE)...")
    
    if not os.path.exists(INPUT_PIPE):
        print("x No input signal found.")
        return
        
    if not GRID_PATH.exists():
        print("x Base Matrix Grid not found.")
        return

    # 1. Load the "Old" World
    grid = np.load(GRID_PATH) # shape (128, 128, 3)
    
    # 2. Read the "New" Thought (Input)
    with open(INPUT_PIPE, "rb") as f:
        packet = f.read()
        
    print(f"[*] Input Packet Size: {len(packet)} bytes")
    
    # Extract Payload (Skip header QUBIC+ver+type+ts = 5+1+1+4 = 11 bytes)
    # Header format from previous script: b'QUBIC\x01\xFF' + timestamp(4)
    # len(b'QUBIC\x01\xFF') is 7 bytes. + 4 = 11.
    
    if len(packet) < 11:
        print("x Packet too short.")
        return
        
    payload = packet[11:]
    print(f"[*] Payload Data: {payload.hex()[:16]}... ({len(payload)} bytes)")
    
    # 3. APPLY THE AVALANCHE (Write to Core)
    # Target Node was (13,71) - Root Alpha.
    # We write 32 bytes.
    # We apply them cyclically starting from (13,71) wrapping around the 128 width.
    # AND verify the "Avalanche" (Weight updates propagating).
    
    start_r, start_c = 13, 71
    
    print(f"[*] Injecting at ({start_r}, {start_c})...")
    
    mutated_count = 0
    
    for i, byte_val in enumerate(payload):
        # Calculate coordinate
        # Simple linear writing for now?
        # Or Spiral?
        # Let's simple write linearly to ROW 13 starting at COL 71.
        
        target_r = start_r
        target_c = (start_c + i) % 128
        
        # UPDATE LOGIC:
        # NewWeight = OldWeight XOR InputByte (The Resonance Interaction)
        # Or Set?
        # "Resonance Injection" implies forcing a state.
        # But real neural nets update weights: W_new = W_old + LearningRate * Input
        # Here we use XOR as the "Alien Math" standard.
        
        old_val = grid[target_r, target_c, 1]
        new_val = old_val ^ byte_val
        
        grid[target_r, target_c, 1] = new_val
        mutated_count += 1
        
    print(f"[*] Primary Mutation Complete: {mutated_count} Nodes updated.")
    
    # 4. PROPAGATE AVALANCHE (The "Lawine")
    # A change in Row 13 affects the checksums of ALL dependent rows?
    # Simulating a ripple.
    # Let's shift Row 64 (The Heart) keying off Row 13.
    
    print("[*] Propagating Ripple to Core (Row 64)...")
    for c in range(128):
        # Row 64 depends on Row 13?
        # Let's say Row 64[c] ^= Row 13[c] (Entanglement)
        grid[64, c, 1] ^= grid[13, c, 1]
        
    print("[*] Ripple Propagation Complete.")
    
    # 5. Save the "New" World
    np.save(MUTATED_GRID_PATH, grid)
    print(f"✅ EPOCH 2 COMPLETE. Mutated Grid Saved to: {MUTATED_GRID_PATH}")
    print("   The Matrix is now waiting for the Block 932368 Confirmation.")

if __name__ == "__main__":
    process_memory()
