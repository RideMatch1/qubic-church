import json
from pathlib import Path

# THE BITSTREAM DECODER (v2)
# Extracting the Layer-3 'Bit-logic' specifically for the 185 Legacy Keys.

BIN_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")

def extract_shadow_instructions():
    print("🛰️ EXTRACTING SHADOW INSTRUCTIONS FROM BITSTREAM (LAYER-3)...")
    
    if not BIN_PATH.exists():
        print(f"[!] Binary file not found at {BIN_PATH}")
        return

    with open(BIN_PATH, "rb") as f:
        full_bitstream = f.read()
        
    print(f"[*] Total Bitstream Size: {len(full_bitstream)} bytes")
    print(f"[*] Total Keys found: {len(full_bitstream) // 32}")
    
    # Analyze Shadow Key 106 (CORE)
    key_size = 32
    start = 106 * key_size
    if start + key_size <= len(full_bitstream):
        key_106 = full_bitstream[start:start+key_size]
        print(f"\n[Core Analysis] Key 106 (6, 33):")
        print(f"    Hex: {key_106.hex()}")
        
        # Translate to ISA
        isa_symbols = "=><+%^#:|&"
        bytecode = "".join([isa_symbols[b % len(isa_symbols)] for b in key_106])
        print(f"    Bytecode Script: [{bytecode}]")
    
    # Search for Temporal Trigger 0x03 0x03 (March 3rd)
    print("\n[!] SEARCHING FOR TEMPORAL TRIGGERS (0x03 0x03):")
    for i in range(len(full_bitstream) // 32):
        k = full_bitstream[i*32:(i+1)*32]
        if b"\x03\x03" in k:
            print(f"  [!!!] TRIGGER DETECTED in Key {i} at Offset {k.find(b'\x03\x03')}")
            # Key 137? 57? 
            # These would be the 'Time-Lock' keys.

if __name__ == "__main__":
    extract_shadow_instructions()
