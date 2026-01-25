import json
from pathlib import Path

# Paths
L5_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin")
COMMITTEE_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/executive_committee.json")

def unlock_memory_vault():
    print("[*] Attempting to unlock the MEMORY VAULT (Key 65)...")
    
    with open(COMMITTEE_JSON, "r") as f:
        committee = json.load(f)
    
    mem_info = committee.get("MEMORY", {})
    start, end = mem_info['id_range']
    
    with open(L5_BIN, "rb") as f:
        l5_data = f.read()
        
    vault_data = l5_data[start:end]
    
    # Significant Hashes (Time-Locks)
    hashes = {
        "Genesis": "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",
        "Block_9": "0000000082b5015589a3fdf2dced549b9cd91f94c9ef8d73b0283f2c42f36dbe"
    }
    
    for name, h_hex in hashes.items():
        mask = bytes.fromhex(h_hex)
        mask_len = len(mask)
        
        decrypted = bytearray()
        for i in range(len(vault_data)):
            decrypted.append(vault_data[i] ^ mask[i % mask_len])
            
        print(f"\n[?] XOR result with {name}:")
        snippet = decrypted[:64].decode('ascii', errors='ignore')
        print(f"    Text: [{snippet}]")
        print(f"    Hex:  {decrypted[:16].hex()}")

if __name__ == "__main__":
    unlock_memory_vault()
