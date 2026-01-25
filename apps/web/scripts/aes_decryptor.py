import hashlib
from pathlib import Path
from Crypto.Cipher import AES

# AES DECRYPTOR (IV MODE)
# Attempts to decrypt the payload inside 'candidate_A.der' assuming
# the Master Key is the AES Key, and the first 16 bytes are the IV.

ARTIFACT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der")
MASTER_KEY_STR = "SKWIKENGRZNXRPLXWRHP"

def aes_decrypt_attempt():
    print("🔐 AES DECRYPTION ATTEMPT (IV EXTRACTION)...")
    
    if not ARTIFACT_PATH.exists():
        print("x Artifact not found.")
        return
        
    with open(ARTIFACT_PATH, "rb") as f:
        full_data = f.read()
        
    # Skip standard ASN.1 Header (Sequence + Length)
    # 30 82 14 10 = 4 bytes
    payload = full_data[4:]
    
    print(f"[*] Payload Size: {len(payload)} bytes")
    
    # 1. EXTRACT IV
    iv = payload[:16]
    ciphertext = payload[16:]
    
    print(f"[*] Extracted IV: {iv.hex()}")
    
    # 2. PREPARE KEY
    # AES Key must be 16, 24, or 32 bytes.
    # Our Master Key is 20 chars.
    # We can Pad it or Hash it.
    
    # Attempt A: SHA256 Hash of Key (32 bytes)
    key_32 = hashlib.sha256(MASTER_KEY_STR.encode()).digest()
    
    print(f"[*] Testing AES-256-CBC with SHA256(MasterKey)...")
    
    try:
        cipher = AES.new(key_32, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # Check success
        # Valid decrypted data usually has low entropy or structural markers (JSON, XML, Text)
        preview = decrypted[:100]
        print(f"    Preview: {preview}")
        
        # Check padding (PKCS7)
        last_byte = decrypted[-1]
        print(f"    Last Byte (Padding?): {last_byte}")
        
        if b"QUBIC" in decrypted or b"{" in decrypted[:10]:
            print("\n[!!!] AES-CBC DECRYPTION SUCCESSFUL!")
            with open("decrypted_candidate_A_aes.bin", "wb") as f:
                f.write(decrypted)
            return
            
    except Exception as e:
        print(f"    Error: {e}")
        
    # Attempt B: XOR Stream Cipher (ChaCha20-like?)
    # If AES fails, maybe it's just IV-based XOR.
    # KeyStream = Hash(Key + IV)
    pass

if __name__ == "__main__":
    aes_decrypt_attempt()
