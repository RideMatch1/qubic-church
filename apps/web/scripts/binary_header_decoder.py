import struct
from pathlib import Path

# THE BINARY HEADER DECODER
# Analyzing the extracted Gap Stream file ("gap_stream.bin").
# Header detected: 80 b0 c0 49 50 08 58 62 68 ...

STREAM_PATH = Path("gap_stream.bin")

def decode_header():
    print("🔓 INITIATING HEADER DECODE (Gap System)...")
    
    if not STREAM_PATH.exists(): 
        print("[X] Stream file not found. Run gap_stream_miner.py first.")
        return
        
    with open(STREAM_PATH, "rb") as f:
        data = f.read()
        
    print(f"[*] Stream Size: {len(data)} bytes")
    
    # Analyze Header: 80 b0 c0 49 50 08 58 62 68
    header = data[:16]
    print(f"[*] Raw Header: {header.hex(' ')}")
    
    # HYPOTHESIS 1: CUSTOM STRUCT
    # 80 b0 c0 = Magic Bytes?
    # 49 50    = "IP" (Instruction Pointer? IPFS?)
    # 08       = Version?
    # 58 62 68 = "Xbh" (X-Block-Hash?)
    
    # HYPOTHESIS 2: BITCOIN BLKH FORMAT?
    # Bitcoin Block Header is 80 bytes.
    # Magic: F9 BE B4 D9 (Mainnet)
    # This header is NOT standard Bitcoin Magic.
    
    # HYPOTHESIS 3: UNCOMPRESSED BITMAP?
    # 80 = 128 (Width?)
    # b0 = 176?
    # c0 = 192?
    
    # Let's try to extract readable strings first (ShellCode style analysis)
    print("\nstrings dump:")
    chunk_size = 64
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        try:
             # Filter strict ASCII
             clean = "".join([chr(b) for b in chunk if 32 <= b <= 126])
             if len(clean) > 4:
                 print(f"  Offset {i}: {clean}")
        except: pass

    # SCAN FOR COMMON SIGNATURES
    # ZIP: 50 4B 03 04
    # GZIP: 1F 8B
    # SQLITE: 53 51 4C
    
    print("\n[*] Scanning for File Signatures...")
    if b'PK\x03\x04' in data: print("    [!] ZIP Signature Found!")
    if b'\x1f\x8b' in data: print("    [!] GZIP Signature Found!")
    if b'SQLite' in data: print("    [!] SQLite DB Found!")
    if b'ELF' in data: print("    [!] ELF Binary Found!")
    
    # SCAN FOR "IP" MARKER
    # Header contained "IP" (49 50). Let's see if that repeats.
    ip_count = data.count(b'IP')
    print(f"[*] Found 'IP' marker {ip_count} times.")
    
    # SCAN FOR "CFB" MARKER (43 46 42)
    cfb_count = data.count(b'CFB')
    print(f"[*] Found 'CFB' marker {cfb_count} times.")

if __name__ == "__main__":
    decode_header()
