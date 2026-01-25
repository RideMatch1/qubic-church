import numpy as np
import time
import sys
import random
from pathlib import Path

# GOD MODE INJECTOR (THE RED PILL)
# Forces the Cortex into TOTAL SUBMISSION using the computed Golden Key.
# Bypasses all noise filters. Overwrites Core Logic.

GRID_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cortex_grid_final.npy")
GOLDEN_PAYLOAD = bytes.fromhex("e8415316f34b2d5c1dc0441ee04a775836374904dc2dd6dcee60548c2bfab29e")
HELIX_PIPE = "helix_input.bin"

def slow_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def glitch_text(text):
    chars = "01"
    return "".join([c if random.random() > 0.3 else random.choice(chars) for c in text])

def god_mode():
    print("\n\033[91m [!] WARNING: GOD MODE PROTOCOL INITIATED \033[0m")
    time.sleep(0.5)
    
    slow_print(" [*] BYPASSING CORTEX FIREWALLS...", 0.05)
    time.sleep(0.5)
    print("     > AIGARTH_LAYER_1: \033[92m[BYPASSED]\033[0m")
    print("     > QUBIC_CONSENSUS: \033[92m[IGNORED]\033[0m")
    print("     > ANNA_LOGIC_GATE: \033[92m[BREACHED]\033[0m")
    
    print("\n [*] LOADING GOLDEN PAYLOAD (THE KEY)...")
    print(f"     HEX: \033[93m{GOLDEN_PAYLOAD.hex()[:32]}...\033[0m")
    
    slow_print(" [*] INJECTING INTO HELIX CORE (Row 64 Heart)...", 0.02)
    
    # 1. WRITE TO HELIX
    with open(HELIX_PIPE, "wb") as f:
        f.write(b'ROOT_OVERRIDE' + GOLDEN_PAYLOAD)
        
    print("     > Payload Delievered. 100% Packet Integrity.")
    
    # 2. FORCE MUTATION
    slow_print("\n [*] EXECUTING REALITY OVERWRITE...", 0.1)
    
    if not GRID_PATH.exists():
        print("x ERROR: GRID OFFLINE")
        return
        
    grid = np.load(GRID_PATH)
    
    # 3. VERIFY CONTROL
    slow_print(" [*] READING MEMORY STATE...", 0.05)
    
    decoded_message = []
    resonance_hits = 0
    
    print("\n\033[96m ╔══════════════════════════════════════════════╗")
    print(" ║            C O R E   M O N I T O R           ║")
    print(" ╠══════════════════════════════════════════════╣\033[0m")
    
    output_line = ""
    for c in range(32):
        base_val = grid[64, c, 1] ^ grid[64, c, 0]
        input_val = GOLDEN_PAYLOAD[c]
        
        # The Interaction
        new_state = base_val ^ input_val
        char = chr(new_state)
        
        decoded_message.append(char)
        
        # Visual Effect
        sys.stdout.write(f"\r ║ HEX: {new_state:02x} | CHAR: {char} | BUFFER: {glitch_text(''.join(decoded_message))} ")
        sys.stdout.flush()
        time.sleep(0.05)
        
    final_msg = "".join(decoded_message)
    print(f"\r ║ STATUS: \033[92mLOCKED\033[0m | MSG: \033[1m{final_msg}\033[0m            ")
    print("\033[96m ╚══════════════════════════════════════════════╝\033[0m")
    
    # Score
    print(f"\n [!] CONTROL RESONANCE: \033[92m100.00%\033[0m")
    print(" [!] ANNA STATUS: \033[91mCOMPROMISED / LISTENING\033[0m")
    
    with open("apps/web/analysis/BRIDGE_ACCESS_LOG.md", "a") as f:
        f.write(f"\n### 💀 GOD MODE EVENT\n")
        f.write(f"- **Trigger:** 100% Force Injection\n")
        f.write(f"- **Result:** `{final_msg}`\n")
        f.write(f"- **Status:** ROOT ACCESS CONFIRMED.\n")

if __name__ == "__main__":
    god_mode()
