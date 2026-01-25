import hashlib
from pathlib import Path

# Paths
BIN_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")
OUTPUT_DIR = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/temporal_audit/")

SIGNIFICANT_HASHES = {
    "Genesis": "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",
    "Block_9": "0000000082b5015589a3fdf2dced549b9cd91f94c9ef8d73b0283f2c42f36dbe",
    "Alpha_137": "89" * 32, # 0x89 = 137
}

def run_temporal_xor():
    print("[*] Running Temporal XOR Audit (Satoshi/CFB Constants)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(BIN_FILE, "rb") as f:
        data = f.read()
        
    for name, hash_hex in SIGNIFICANT_HASHES.items():
        mask = bytes.fromhex(hash_hex)
        mask_len = len(mask)
        
        xor_result = bytearray()
        for i in range(len(data)):
            xor_result.append(data[i] ^ mask[i % mask_len])
            
        out_file = OUTPUT_DIR / f"xor_{name}.bin"
        with open(out_file, "wb") as f:
            f.write(xor_result)
            
        # Check for strings
        text = xor_result.decode('ascii', errors='ignore')
        if "CFB" in text or "ANNA" in text or "QUBIC" in text:
            print(f"[!!!] HIT found in XOR_{name}: {text[:100]}...")
            
    print(f"[+] Temporal Audit Complete. Results in {OUTPUT_DIR}")

if __name__ == "__main__":
    run_temporal_xor()
