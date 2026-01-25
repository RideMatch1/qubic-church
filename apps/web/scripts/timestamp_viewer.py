import binascii
from pathlib import Path

# THE TIMESTAMP VIEWER
# Focusing purely on extracting and decoding the GeneralizedTime (Tag 0x18) field found in the certificate.

FRAGMENT_PATH = Path("extracted_cert.der")

def view_timestamp():
    print("🕒 TIMESTAMP FORENSICS (GeneralizedTime Extract)...")
    
    if not FRAGMENT_PATH.exists(): return
    with open(FRAGMENT_PATH, "rb") as f:
        data = f.read()

    # Locate Tag 0x18
    try:
        ts_idx = data.index(b'\x18')
        # Check if length follows
        length = data[ts_idx+1]
        
        # Extract Time Bytes
        time_bytes = data[ts_idx+2 : ts_idx+2+length]
        
        print(f"[*] Found Timestamp at Offset {ts_idx}")
        print(f"[*] Length: {length} bytes")
        print(f"[*] Raw Hex: {binascii.hexlify(time_bytes).decode()}")
        print(f"[*] Raw ASCII: {time_bytes}")
        
        # Try to clean it up (Filter non-printables)
        cleaned = "".join([chr(b) for b in time_bytes if 48 <= b <= 57 or b == 90]) # 0-9 and Z
        print(f"[*] Numeric Filter: {cleaned}")
        
    except ValueError:
        print("[X] No GeneralizedTime tag found.")

if __name__ == "__main__":
    view_timestamp()
