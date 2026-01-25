import hashlib
import os

ARTIFACT = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der"
KEY_STR = "SKWIKENGRZNXRPLXWRHP"

def prep():
    with open(ARTIFACT, "rb") as f:
        data = f.read()
    
    # Payload starts after 4 bytes
    payload = data[4:]
    iv = payload[:16]
    ciphertext = payload[16:]
    
    # Save ciphertext for openssl
    with open("temp_ct.bin", "wb") as f:
        f.write(ciphertext)
        
    # Key
    key_hash = hashlib.sha256(KEY_STR.encode()).digest()
    
    print(f"IV={iv.hex()}")
    print(f"K={key_hash.hex()}")
    print(f"CMD=openssl enc -d -aes-256-cbc -K {key_hash.hex()} -iv {iv.hex()} -in temp_ct.bin")

if __name__ == "__main__":
    prep()
