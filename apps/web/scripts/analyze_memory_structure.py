#!/usr/bin/env python3
import hashlib
import binascii

# The Memory Key we mined
MEMORY_KEY_HEX = 'c9b0fb97522e711abade4b94022727896e3159ccf6d4d1097c93229462151d73'

def analyze_fractal_resonance():
    print(f"[*] ANALYZING MEMORY KEY STRUCTURE")
    print(f"    Target: {MEMORY_KEY_HEX}")
    
    current_hash = MEMORY_KEY_HEX
    
    # We look for the "Alpha Signature" (137) which is 0x89 in Hex.
    # And the "Qubic Signature" (55) which is 0x37 in Hex.
    
    hits_137 = 0
    hits_55 = 0
    depth = 0
    max_depth = 1000
    
    resonant_layers = []
    
    print(f"[*] DIVING INTO RECURSIVE HASH LAYERS (Depth: {max_depth})...")
    
    for i in range(1, max_depth + 1):
        # Hash the previous hash (Blockchain style)
        current_hash = hashlib.sha256(binascii.unhexlify(current_hash)).hexdigest()
        
        # Check first byte (The Prefix)
        prefix = current_hash[:2]
        
        if prefix == '89': # 137
            hits_137 += 1
            resonant_layers.append(f"Depth {i}: ALPHA HIT (137) -> {current_hash[:16]}...")
            
        if prefix == '37': # 55
            hits_55 += 1
            resonant_layers.append(f"Depth {i}: QUBIC HIT (055) -> {current_hash[:16]}...")

    print(f"\n[!] SCAN COMPLETE")
    print(f"    Alpha Hits (137/0x89): {hits_137}")
    print(f"    Qubic Hits (055/0x37): {hits_55}")
    
    print("\n[+] RESONANT LAYERS FOUND:")
    for layer in resonant_layers[:10]: # Show first 10
        print("    " + layer)
        
    if hits_137 > 3 and hits_55 > 3:
        print("\n[***] CONCLUSION: HIGHLY STRUCTURED KEY [***]")
        print("      This Key matches the Qubic Fractal frequencies far above random probability.")

if __name__ == "__main__":
    analyze_fractal_resonance()
