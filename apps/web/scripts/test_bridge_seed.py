from Crypto.Hash import KangarooTwelve
import hashlib

# BRIDGE SEED TESTER
# Checks if the Master Key 'SKWIKEN...' functions as a Qubic Seed to derive the Gate Identities.

ID0 = "HSISJEJOTMWHNBDGGBTEIYKHQLXBAGCUVTWNKMEHGDWCECFHVAGSTGLBOPKE"
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def get_qubic_identity(seed_str):
    # Qubic Crypto Logic
    # 1. 55 chars a-z
    # 2. To bytes (0-25)
    # 3. K12(seed, 32) -> Private Key
    # 4. K12(pk, 32) -> Public Key (Wait, the provided script said K12 -> K12 -> PK)
    
    # Let's standardize on what Qubic Computors use.
    # From qubic-cli:
    # subseed = K12(seed_bytes, 32)
    # sk = K12(subseed, 32)
    # pk = Schnorr.PublicKey(sk) <- This is complex.
    
    # BUT, we have a shortcut.
    # Qubic ID is derived from Public Key bytes.
    # The Identity string is just base26 of the Public Key + Checksum.
    
    # For this check, we'll try to generate the Private Key using the K12 method
    # and print it. We can't easily reproduce the full Qubic Identity generation 
    # (curve25519-donna + custom base26) without valid libraries.
    # But we can check if the output matches known patterns.
    
    print(f"Testing Seed Candidate: {seed_str}")
    
    # Pad to 55 chars
    if len(seed_str) < 55:
        # Repeat
        seed_long = (seed_str * 5)[:55]
    else:
        seed_long = seed_str[:55]
        
    print(f"Expanded: {seed_long}")
    
    # To Lowercase
    seed_lower = seed_long.lower()
    
    # Check valid chars (a-z)
    valid_seed = "".join([c for c in seed_lower if 'a' <= c <= 'z']) 
    valid_seed = (valid_seed * 5)[:55] # Re-pad if chars were dropped
    
    print(f"Normalized: {valid_seed}")
    
    # Bytes
    try:
        seed_bytes = bytes([ord(c) - ord('a') for c in valid_seed])
        
        # K12 Round 1
        k12_1 = KangarooTwelve.new()
        k12_1.update(seed_bytes)
        subseed = k12_1.read(32)
        
        # K12 Round 2
        k12_2 = KangarooTwelve.new()
        k12_2.update(subseed)
        sk = k12_2.read(32)
        
        print(f"Derived Private Key (Hex): {sk.hex()}")
        
        # We can't easily check against ID0 without full ed25519 logic.
        # But we can print this debug info.
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_qubic_identity(MASTER_KEY)
