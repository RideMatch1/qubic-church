import os

# XOR STREAM DECRYPTOR
# Uses the Master Key to generate a keystream (repeating or seeded)
# and attempts to unmask the L5 artifacts.

ARTIFACT = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der"
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def xor_decrypt():
    print("🔓 STARTING XOR STREAM DECRYPTION...")
    
    if not os.path.exists(ARTIFACT):
        print("x Artifact not found.")
        return

    with open(ARTIFACT, "rb") as f:
        data = f.read()

    # METHOD 1: REPEATING KEY (Vigenère-style)
    # This is simple but effective if the mask is just the key repeated.
    
    key_bytes = MASTER_KEY.encode()
    key_len = len(key_bytes)
    
    decrypted = bytearray()
    for i, byte in enumerate(data):
        k = key_bytes[i % key_len]
        decrypted.append(byte ^ k)
        
    out_path = ARTIFACT + ".xor_decrypted"
    with open(out_path, "wb") as f:
        f.write(decrypted)
        
    print(f"[*] Method 1 (Repeating Key) Saved to: {out_path}")
    
    # Check for readable text in result
    try:
        text = decrypted.decode('utf-8')
        print(f"    [?] Text Sample: {text[:100]}")
    except:
        print(f"    [i] Binary Result (First 20): {decrypted[:20].hex()}")


    # METHOD 2: ASCII OFFSET
    # Shift every byte by the key character value (Caesar-style per specific byte)
    # byte - key_char_val
    
    shifted = bytearray()
    for i, byte in enumerate(data):
        k = key_bytes[i % key_len]
        # (byte - k) % 256
        val = (byte - k) % 256
        shifted.append(val)
        
    out_path_s = ARTIFACT + ".shifted_decrypted"
    with open(out_path_s, "wb") as f:
        f.write(shifted)
        
    print(f"[*] Method 2 (Subtractive Shift) Saved to: {out_path_s}")
    
    # Check for readable text
    try:
        text = shifted.decode('utf-8')
        print(f"    [?] Text Sample: {text[:100]}")
    except:
        print(f"    [i] Binary Result (First 20): {shifted[:20].hex()}")
        
if __name__ == "__main__":
    xor_decrypt()
