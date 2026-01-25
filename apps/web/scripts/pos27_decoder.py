import json
from pathlib import Path

# Path to the stream
STREAM_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_stream.txt")
OUTPUT_BIN = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")

def decode_pos27():
    print("[*] Decoding Position 27 Bitstream (2 bits per char)...")
    
    with open(STREAM_FILE, "r") as f:
        stream = f.read()
    
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    bit_array = []
    for char in stream:
        val = mapping.get(char, 0)
        # Convert to 2 bits: 0 -> 00, 1 -> 01, 2 -> 10, 3 -> 11
        bit_array.append((val >> 1) & 1)
        bit_array.append(val & 1)
        
    # Convert bits to bytes
    byte_list = []
    for i in range(0, len(bit_array), 8):
        byte = 0
        chunk = bit_array[i:i+8]
        if len(chunk) < 8:
            break
        for bit in chunk:
            byte = (byte << 1) | bit
        byte_list.append(byte)
        
    with open(OUTPUT_BIN, "wb") as f:
        f.write(bytes(byte_list))
        
    print(f"[+] Decoded {len(byte_list)} bytes to {OUTPUT_BIN}")
    
    # Quick check for printable strings
    try:
        text = bytes(byte_list).decode('ascii', errors='ignore')
        print(f"[?] ASCII Sample: {text[:200]}")
    except:
        pass

if __name__ == "__main__":
    decode_pos27()
