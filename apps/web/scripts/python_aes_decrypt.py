from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import hashlib
import os

# RAW AES DECRYPTOR
# Handles manual IV extraction and Key Hashing.

ARTIFACT = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der"
KEY_STR = "SKWIKENGRZNXRPLXWRHP"

def derive_key(s):
    # Try raw SHA256 of the string
    return hashlib.sha256(s.encode()).digest()

def try_decrypt():
    print(f"🔓 DECRYPTING {os.path.basename(ARTIFACT)} WITH RAW AES...")
    
    if not os.path.exists(ARTIFACT):
        print("x Artifact not found.")
        return

    with open(ARTIFACT, "rb") as f:
        data = f.read()
        
    # Skip ASN.1 Header? (30 82 14 10 = 4 bytes)
    # The payload starts after.
    payload = data[4:] 
    
    # Assumption 1: IV is first 16 bytes of payload
    iv = payload[:16]
    ciphertext = payload[16:]
    
    key = derive_key(KEY_STR)
    
    print(f"[*] Key: {key.hex()}")
    print(f"[*] IV:  {iv.hex()}")
    
    # Try Common Modes
    modes_list = [
        modes.CBC(iv),
        modes.CFB(iv),
        modes.OFB(iv),
        modes.CTR(iv) # CTR doesn't need padding usually
    ]
    
    for mode in modes_list:
        try:
            cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
            decryptor = cipher.decryptor()
            pt = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Unpad?
            try:
                unpadder = padding.PKCS7(128).unpadder()
                pt = unpadder.update(pt) + unpadder.finalize()
            except:
                pass # Maybe not padded
                
            print(f"\n[?] Mode: {mode.name}")
            # Check for ASCII
            try:
                text = pt.decode('utf-8')
                if text.isprintable():
                    print(f"    [!] TEXT FOUND: {text[:100]}")
                else:
                    print(f"    [i] Binary output (first 20): {pt[:20].hex()}")
            except:
                 print(f"    [i] Binary output (first 20): {pt[:20].hex()}")
                 
            # Check for inner signature
            if b"QUBIC" in pt or b"ANNA" in pt or b"1CFB" in pt:
                 print("    [!!!] KEYWORD FOUND IN DECRYPTED DATA")
                 
        except Exception as e:
            print(f"    [x] Error: {e}")

if __name__ == "__main__":
    try_decrypt()
