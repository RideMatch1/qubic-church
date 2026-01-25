import sys
import hashlib
from pathlib import Path

# ASN.1 DEEP WALKER
# Recursively parses the ASN.1 DER structure of 'candidate_A.der'.
# Identifies encrypted blobs (Octet Strings) and attempts KEY interaction on them.

ARTIFACT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der")
MASTER_KEY = "SKWIKENGRZNXRPLXWRHP"

def parse_tag(data, offset=0, level=0):
    if offset >= len(data):
        return offset
        
    tag = data[offset]
    offset += 1
    
    # Parse Length
    length_byte = data[offset]
    offset += 1
    
    length = 0
    if length_byte & 0x80:
        num_bytes = length_byte & 0x7F
        length_bytes = data[offset:offset+num_bytes]
        length = int.from_bytes(length_bytes, 'big')
        offset += num_bytes
    else:
        length = length_byte
        
    # Visual Indent
    indent = "  " * level
    
    # Interpret Tag
    tag_name = f"0x{tag:02X}"
    if tag == 0x30: tag_name = "SEQUENCE"
    elif tag == 0x02: tag_name = "INTEGER"
    elif tag == 0x04: tag_name = "OCTET STRING"
    elif tag == 0x06: tag_name = "OBJECT ID"
    elif tag == 0x03: tag_name = "BIT STRING"
    
    print(f"{indent}[{tag_name}] Len: {length}")
    
    # Recursion for Containers
    if tag == 0x30 or tag == 0x31: # Sequence/Set
        end = offset + length
        while offset < end:
            offset = parse_tag(data, offset, level + 1)
    
    # Value Inspection for Primitives
    else:
        value = data[offset:offset+length]
        
        # If Octet/Bit String > 32 bytes, try decrypting
        if (tag == 0x04 or tag == 0x03) and length > 32:
            print(f"{indent}  -> BLOB DETECTED ({length} bytes). Trying Key...")
            try_decrypt(value, indent + "    ")
            
        elif tag == 0x02 and length < 32:
            # Short integer
            val_int = int.from_bytes(value, 'big')
            print(f"{indent}  -> Value: {val_int}")
            
        offset += length
        
    return offset

def try_decrypt(blob, indent):
    # Try XOR Key
    key_bytes = MASTER_KEY.encode()
    dec = bytearray()
    for i, b in enumerate(blob):
        dec.append(b ^ key_bytes[i % len(key_bytes)])
        
    # Check Result
    try:
        txt = dec.decode('utf-8')
        if "QUBIC" in txt or "qubic" in txt or "CFB" in txt:
             print(f"{indent}[!!!] DECRYPT SUCCESS: Found '{txt[:20]}...'")
             return
    except: pass
    
    # Try just printing raw if it looks somewhat clean
    # or entropy check
    pass
    

def analyze_asn1():
    print("📜 ASN.1 DEEP STRUCTURE ANALYSIS")
    
    if not ARTIFACT_PATH.exists():
        print("x Artifact not found.")
        return
        
    with open(ARTIFACT_PATH, "rb") as f:
        data = f.read()
        
    parse_tag(data)
    
    print("\n✅ Structure Mapping Complete.")

if __name__ == "__main__":
    analyze_asn1()
