import json
from pathlib import Path

# Paths
L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")

def search_full_layer5_xor_genesis():
    print("[*] Global Layer-5 XOR search (Key: Genesis)...")
    
    with open(L5_BIN, "rb") as f:
        data = f.read()
        
    mask = bytes.fromhex("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
    mask_len = len(mask)
    
    decrypted = bytearray()
    for i in range(len(data)):
        decrypted.append(data[i] ^ mask[i % mask_len])
        
    # Search for known signatures
    targets = [b"1CFB", b"1CFi", b"QUBIC", b"ANNA", b"CFB"]
    for t in targets:
        pos = decrypted.find(t)
        if pos != -1:
            print(f"[!!!] FOUND SIGNATURE: {t.decode()} at ID index {pos}")
            snippet = decrypted[max(0, pos-20) : pos+40].decode('ascii', errors='ignore')
            print(f"    Context: [...{snippet}...]")

if __name__ == "__main__":
    search_full_layer5_xor_genesis()
