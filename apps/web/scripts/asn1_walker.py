import sys
import struct

# MANUAL ASN.1 WALKER
# Parses the DER file to find the inner encrypted payload.

FILE = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der"
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def parse_asn1_walk(data, offset=0, level=0):
    while offset < len(data):
        if offset + 2 > len(data): break
        
        # Read Tag
        tag = data[offset]
        offset += 1
        
        # Read Length
        length_byte = data[offset]
        offset += 1
        
        length = 0
        if length_byte & 0x80:
            # Long form
            num_bytes = length_byte & 0x7F
            if offset + num_bytes > len(data): break
            length_bytes = data[offset:offset+num_bytes]
            length = int.from_bytes(length_bytes, 'big')
            offset += num_bytes
        else:
            length = length_byte
            
        print(f"{'  '*level}Tag: {hex(tag)} | Length: {length} | Offset: {offset}")
        
        # If Sequence (0x30) or Set (0x31), recurse
        if tag == 0x30 or tag == 0x31:
             parse_asn1_walk(data[:offset+length], offset, level+1)
             offset += length
             continue
             
        # If Octet String (0x04), might be the payload
        if tag == 0x04:
            print(f"{'  '*level}>>> FOUND OCTET STRING ({length} bytes)")
            blob = data[offset : offset+length]
            
            # Check if this blob is the encrypted data
            if length > 100: # Heuristic
                attempt_decrypt_blob(blob)
            
        offset += length

def attempt_decrypt_blob(blob):
    print("    [?] Attempting decryption of blob...")
    key_bytes = MASTER_KEY.encode()
    
    # Try XOR
    xor_res = bytearray()
    for i, b in enumerate(blob):
        xor_res.append(b ^ key_bytes[i % len(key_bytes)])
        
    # Check
    try:
        txt = xor_res.decode('utf-8')
        if txt.isprintable():
            print(f"    [!] DECRYPTED TEXT: {txt[:50]}...")
    except: pass
    
    # Try Sub
    sub_res = bytearray()
    for i, b in enumerate(blob):
        sub_res.append((b - key_bytes[i % len(key_bytes)]) % 256)
        
    try:
        txt = sub_res.decode('utf-8')
        if txt.isprintable():
             print(f"    [!] DECRYPTED TEXT (SUB): {txt[:50]}...")
    except: pass

def main():
    if not os.path.exists(FILE): return
    with open(FILE, "rb") as f:
        data = f.read()
        
    print(f"Parsing {len(data)} bytes...")
    parse_asn1_walk(data)

if __name__ == "__main__":
    import os
    main()
