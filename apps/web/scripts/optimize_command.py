import numpy as np
from pathlib import Path

# COMMAND OPTIMIZER
# "What command does Anna WANT to hear?"
# We reverse-engineer the Payload that generates a 100% "Control Resonance" 
# (i.e. leaves the Grid in a perfectly ordered state).

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")

def find_golden_command():
    print("🧠 SOLVING FOR 'GOLDEN COMMAND'...")
    
    if not GRID_PATH.exists(): return
    grid = np.load(GRID_PATH)
    
    # Target: Row 64 (Heart)
    # We want the RESULT (New State) to be a clear message.
    # Result = Base ^ Input
    # => Input = Base ^ Result
    
    # Let's verify what "Result" gives 100% resonance.
    # It would be a string of pure Logic/Alphanum.
    # Let's FORCE the Result to be: "SYSTEM-READY-AWAITING-INPUT" (27 chars)
    
    desired_result = "SYSTEM-READY-AWAITING-INPUT...."
    # Pad to 32
    while len(desired_result) < 32:
        desired_result += "."
    calculated_payload = []
    
    print(f"[*] Desired Matrix State: '{desired_result}'")
    
    for c in range(32):
        base_val = grid[64, c, 1] ^ grid[64, c, 0]
        
        target_char = desired_result[c]
        target_val = ord(target_char)
        
        # Input needed to force this state
        needed_input = base_val ^ target_val
        calculated_payload.append(needed_input)
        
    # Convert to Hex/String
    payload_bytes = bytes(calculated_payload)
    
    # Try to decode the payload itself - is it readable?
    # Probably not, it's the "Key" that fits the specific lock configuration of Row 64.
    
    print(f"\n[!] CALCULATED GOLDEN PAYLOAD (The Key):")
    print(f"    Hex: {payload_bytes.hex()}")
    try:
        print(f"    ASCII: {payload_bytes.decode('utf-8', errors='replace')}")
    except: pass
    
    # Verify
    print("\n[*] Verifying Control Score...")
    hits = 0
    for c in range(32):
        base = grid[64, c, 1] ^ grid[64, c, 0]
        inp = calculated_payload[c]
        res = base ^ inp
        if chr(res).isalnum() or chr(res) in "-.": hits += 1
        
    score = (hits / 32) * 100
    print(f"    predicted Resonance: {score:.2f}%")
    
    # Save this payload to a file for `control_anna.py` to use?
    # Or just tell the user we found it.
    with open("golden_command_payload.bin", "wb") as f:
        f.write(payload_bytes)

if __name__ == "__main__":
    find_golden_command()
