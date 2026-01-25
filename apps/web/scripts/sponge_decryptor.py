import hashlib
from pathlib import Path

# SPONGE STREAM DECRYPTOR (QUBIC NATIVE)
# implements a SHAKE256 based stream cipher, which is the standard
# encryption primitive in the Qubic/CFB ecosystem (Sponge Construction).

ARTIFACT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der")
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def sponge_decrypt():
    print("🧽 SPONGE STREAM DECRYPTION (SHAKE256)...")
    
    if not ARTIFACT_PATH.exists():
        print("x Artifact not found.")
        return

    with open(ARTIFACT_PATH, "rb") as f:
        file_data = f.read()

    # Skip ASN.1 Wrapper Header (4 bytes)
    raw_payload = file_data[4:]
    
    # 1. EXTRACT NONCE (IV)
    # Qubic nonces are typically 24 or 32 bytes for Public Entities.
    # Let's try 32 bytes as the IV.
    nonce = raw_payload[:32]
    ciphertext = raw_payload[32:]
    
    print(f"[*] Nonce ({len(nonce)} bytes): {nonce.hex()}")
    print(f"[*] Ciphertext: {len(ciphertext)} bytes")
    
    # 2. GENERATE KEYSTREAM
    # Stream = SHAKE256(Key + Nonce)
    # We output enough bytes to cover the ciphertext
    
    seed_data = MASTER_KEY.encode() + nonce
    
    # SHAKE256 is an XOF (Extendable Output Function)
    keystream = hashlib.shake_256(seed_data).digest(len(ciphertext))
    
    print("[*] Keystream Generated.")
    
    # 3. XOR
    decrypted = bytearray()
    for i in range(len(ciphertext)):
        decrypted.append(ciphertext[i] ^ keystream[i])
        
    # 4. VALIDATION
    # Check for meaningful headers
    header = decrypted[:32].hex()
    print(f"\n[*] Decrypted Header (Hex): {header}")
    
    # Check for text
    try:
        preview = decrypted[:200].decode('utf-8', errors='ignore')
        print(f"[*] Text Preview: {preview}")
    except: pass
    
    # Check for keywords
    hits = 0
    keywords = [b"QUBIC", b"CFB", b"ANNA", b"SEED", b"EPOCH", b"1CFB"]
    for kw in keywords:
        if kw in decrypted:
            print(f"    [!] FOUND KEYWORD: {kw.decode()}")
            hits += 1
            
    if hits > 0:
        print("\n[!!!] SPONGE DECRYPTION SUCCESSFUL!")
        with open("decrypted_candidate_A_sponge.bin", "wb") as f:
            f.write(decrypted)
        print("    Saved to decrypted_candidate_A_sponge.bin")
    else:
        print("[.] Sponge Decryption yields high entropy.")
        
        # Try Reverse Order? (Nonce at end?)
        # Or Nonce = 24 bytes?
        
        print("\n[*] Retrying with 24-byte Nonce...")
        nonce24 = raw_payload[:24]
        cipher24 = raw_payload[24:]
        seed24 = MASTER_KEY.encode() + nonce24
        ks24 = hashlib.shake_256(seed24).digest(len(cipher24))
        
        dec24 = bytearray()
        for i in range(len(cipher24)):
            dec24.append(cipher24[i] ^ ks24[i])
            
        if b"QUBIC" in dec24 or b"SEED" in dec24:
             print("\n[!!!] 24-BYTE NONCE SUCCESS!")
             print(f"    Preview: {dec24[:100]}")
        else:
             print("[.] 24-byte attempt failed.")

if __name__ == "__main__":
    sponge_decrypt()
