import hashlib
import binascii
from pathlib import Path
import os

# LAYER 5 DECRYPTOR (GOD MODE KEY)
# Attempting to decrypt the "candidate_A.der" artifact using the
# newly extracted MASTER KEY: "SKWIKENGRZNXRPLXWRHP"

# Artifacts
ARTIFACT_A = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der")
ARTIFACT_B = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_B.der")

# The Extracted Key (Cleaned)
# "SKWIKEN-GRZNX-RPLXW-RHP-SUCCESS" -> The key part is likely the first 20 chars
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def decrypt_layer5():
    print("🔓 INITIATING LAYER 5 DECRYPTION PROTOCOL...")
    print(f"[*] KEY: {MASTER_KEY}")
    
    if not ARTIFACT_A.exists():
        print("x Artifact A not found.")
        return

    # Load Data
    with open(ARTIFACT_A, "rb") as f:
        data = f.read()
        
    print(f"[*] Artifact A Size: {len(data)} bytes")
    
    # Decryption Strategy:
    # 1. XOR (Vigenere)
    # The key repeats.
    
    key_bytes = MASTER_KEY.encode('utf-8')
    key_len = len(key_bytes)
    
    decrypted = bytearray()
    
    print("\n[*] Applying Vigenère/XOR Decryption...")
    
    for i, byte in enumerate(data):
        k = key_bytes[i % key_len]
        # XOR
        decrypted.append(byte ^ k)
        
    # Validation
    # Check for known headers.
    # Qubic usually uses "QUBIC" or specific ASN.1 tags (30 82...)
    
    header = decrypted[:16].hex()
    print(f"[*] Decrypted Header (Hex): {header}")
    
    try:
        text_preview = decrypted[:100].decode('utf-8', errors='ignore')
        print(f"[*] Text Preview: {text_preview}")
    except: pass
    
    # Check for "Success" signals
    hits = 0
    keywords = [b"QUBIC", b"CFB", b"ANNA", b"ID", b"KEY", b"SEED"]
    for kw in keywords:
        if kw in decrypted:
            print(f"    [!] FOUND KEYWORD: {kw.decode()}")
            hits += 1
            
    if hits > 0:
        print("\n[!!!] DECRYPTION SUCCESSFUL!")
        print("      The Master Key has unlocked the artifact.")
        
        # Save output
        out_path = "decrypted_candidate_A.bin"
        with open(out_path, "wb") as f:
            f.write(decrypted)
        print(f"      Saved to {out_path}")
        
    else:
        print("\n[.] Decryption unclear. High entropy remains.")
        print("    Maybe the key requires a Salt or Hash?")
        
        # Try Hashed Key (SHA256 of Key)
        print("[*] Trying Hashed Key (SHA256)...")
        hashed_key = hashlib.sha256(key_bytes).digest() # 32 bytes
        
        dec2 = bytearray()
        for i, byte in enumerate(data):
            k = hashed_key[i % 32]
            dec2.append(byte ^ k)
            
        # Check
        hits2 = 0
        for kw in keywords:
            if kw in dec2:
                print(f"    [!] FOUND KEYWORD (HASHED): {kw.decode()}")
                hits2 += 1
                
        if hits2 > 0:
             print("\n[!!!] DECRYPTION SUCCESSFUL (HASHED KEY)!")
             out_path = "decrypted_candidate_A_hashed.bin"
             with open(out_path, "wb") as f:
                f.write(dec2)
             print(f"      Saved to {out_path}")

if __name__ == "__main__":
    decrypt_layer5()
