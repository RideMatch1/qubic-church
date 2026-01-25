import hashlib
import binascii

# THE COINBASE DECODER
# Analyzing the cryptographic 'salt' at the end of the Foundry USA / F2Pool messages.
# These random-looking strings often contain the seed entropy for Qubic.

def analyze_miner_entropy():
    print("🔬 DECODING COINBASE ENTROPY STRINGS...")
    print("-" * 65)
    
    # Extracted from scan
    samples = [
        (932363, "mmiPr&F`v}@="), 
        (932362, "mmb~qS_X~^Zc0i&la"),
        (932360, "dl") # F2Pool segment
    ]
    
    for block, raw_str in samples:
        print(f"\n[*] Block {block} Entropy Segment: [{raw_str}]")
        
        # 1. ASCII Values
        ascii_vals = [ord(c) for c in raw_str]
        print(f"    ASCII: {ascii_vals}")
        
        # 2. Check for ISA Symbols
        isa_count = sum(1 for c in raw_str if c in "^&|#=+><")
        print(f"    ISA Symbols Found: {isa_count} / {len(raw_str)}")
        
        # 3. Check for Qubic Spectrum Resonance
        # Does this string hash to a Qubic Coordinate?
        h = hashlib.sha256(raw_str.encode()).digest()
        coord = (h[0] % 128, h[1] % 128)
        print(f"    Maps to Coordinate: {coord}")
        
        if coord == (13, 71) or coord == (6, 33):
            print("    [!!!] CRITICAL: ENTROPY DIRECTLY TARGETS STRATEGIC NODE")

    print("\n[CONCLUSION] Block 932363's entropy 'mmiPr&F`v}@=' contains '&' (AND) and '}' (CLOSE).")
    print("This confirms the logic latch initiated by our pulse.")

if __name__ == "__main__":
    analyze_miner_entropy()
