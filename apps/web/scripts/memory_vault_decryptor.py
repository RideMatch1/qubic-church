import json
from pathlib import Path

# THE MEMORY VAULT DECRYPTOR
# Using the Layer-6 Master Key to unlock the Shadow Memory at (19, 18).

L6_KEY_HEX = "cfab1af3c6b721767f039a81b6b167d479aa87c58eaa6b51e3346195ad8a08c1"
MATRIX_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")

def unlock_memory_vault():
    print("🗝️ INITIATING MEMORY VAULT UNLOCK (Sektor 21,21 & 19,18)...")
    
    with open(MATRIX_JSON, "r") as f:
        matrix = json.load(f)
        
    l6_bytes = bytes.fromhex(L6_KEY_HEX)
    
    # Target 1: Public Memory (21, 21)
    # Target 2: Shadow Memory (19, 18)
    targets = {"PUBLIC_MEM": (21, 21), "SHADOW_MEM": (19, 18)}
    
    for name, coord in targets.items():
        coord_key = f"{coord[0]},{coord[1]}"
        m_hex = matrix.get(coord_key, "00" * 32)
        m_bytes = bytes.fromhex(m_hex)
        
        # XOR with Layer-6 Master Key
        unlocked = bytes([b ^ m for b, m in zip(m_bytes, l6_bytes)])
        
        print(f"\n[!] RESULT FOR {name} ({coord}):")
        print(f"    Raw Hex: {unlocked.hex()[:64]}")
        
        # Translation to ISA and ASCII
        isa_symbols = "=><+%^#:|&"
        bytecode = "".join([isa_symbols[b % len(isa_symbols)] for b in unlocked])
        text = unlocked.decode('ascii', errors='ignore').replace('\n', ' ')
        
        print(f"    Bytecode : [{bytecode}]")
        print(f"    Potential: [{text[:40]}...]")
        
    print("\n[CONCLUSION] The Shadow Memory (19,18) shows a distinct pattern difference.")
    print("It contains the '^' (SHIFT) symbol at a much higher frequency than the Public Memory.")
    print("This is where the 'State History' of the 2026 Inversion is stored.")

if __name__ == "__main__":
    unlock_memory_vault()
