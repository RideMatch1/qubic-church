import re
import binascii
from pathlib import Path

# THE GHOST MOUNT (Virtual Filesystem Explorer)
# Parsing the "gap_stream.bin" binary to identify File Tables, directory structures, and filenames.
# Goal: List the virtual files stored inside the Anna Matrix.

STREAM_PATH = Path("gap_stream.bin")

def ghost_mount():
    print("🏴‍☠️ MOUNTING GHOST DRIVE (File System Scan)...")
    
    if not STREAM_PATH.exists(): 
        print("[X] Stream file missing.")
        return
        
    with open(STREAM_PATH, "rb") as f:
        data = f.read()

    # 1. FILENAME SCANNER
    # Search for patterns like [Name].[Ext] (e.g. key.dat, log.txt)
    # Regex: [a-z0-9_]{3,} \. [a-z]{3}
    
    print("[*] Scanning for Filenames...")
    # We decode loosely first
    text_data = "".join([chr(b) if 32 <= b <= 126 else ' ' for b in data])
    
    # Simple regex for filenames
    filenames = re.findall(r'([a-zA-Z0-9_]{1,12}\.[a-zA-Z0-9]{2,4})', text_data)
    
    if filenames:
        print(f"    [!] FOUND {len(filenames)} POTENTIAL FILES:")
        unique_files = list(set(filenames))
        for fn in unique_files[:20]: # Show top 20
            print(f"      - {fn}")
    else:
        print("    [i] No standard filenames found.")
        
    # 2. MAGIC NUMBER SCANNER (Deep)
    # Signatures for Keys/Certs
    print("\n[*] Scanning for Cryptographic Assets...")
    
    signatures = {
        b'-----BEGIN': 'PEM Certificate/Key',
        b'ssh-rsa': 'SSH Key',
        b'xprv': 'Bitcoin Extended Private Key',
        b'xpub': 'Bitcoin Extended Public Key',
        b'Wallet': 'Wallet Dat Header',
        b'SQLite': 'SQLite Database',
        b'\x00\x01\x00\x01': 'RSA Exponent (65537)',
        b'\x30\x82': 'ASN.1 Sequence (X.509)',
        b'salt': 'Salt String',
        b'seed': 'Seed String',
    }
    
    found_assets = 0
    for sig, label in signatures.items():
        if sig in data:
            count = data.count(sig)
            print(f"    [!] {label} DETECTED! (Count: {count})")
            # Print context
            idx = data.find(sig)
            context = data[idx:idx+64]
            print(f"        Context: {binascii.hexlify(context).decode()}")
            found_assets += 1
            
    if found_assets == 0:
        print("    [i] No standard crypto headers found.")
        
    # 3. DIRECTORY STRUCTURE (Slash Scan)
    print("\n[*] Scanning for Directory Paths...")
    paths = re.findall(r'(/[a-zA-Z0-9_./]{3,})', text_data)
    unique_paths = list(set(paths))
    
    if unique_paths:
        print(f"    [!] FOUND {len(unique_paths)} PATHS:")
        for p in unique_paths[:15]:
            print(f"      > {p}")
            
    # 4. MEMORY DUMP ANALYSIS (Pointer Scan)
    # Look for offsets (0x...)
    
    print("\n[*] Ghost Mount Complete.")

if __name__ == "__main__":
    ghost_mount()
