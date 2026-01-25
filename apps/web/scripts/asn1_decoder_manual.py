import binascii
from pathlib import Path

# THE MANUAL ASN.1 DECODER
# Parsing the fragment strictly byte-by-byte using ASN.1 DER rules (Tag-Length-Value).
# Goal: Extract hidden fields (Integer, Strings, Dates) from the certificate structure.

FRAGMENT_PATH = Path("extracted_cert.der")

def parse_asn1():
    print("📜 INITIATING MANUAL ASN.1 DECODE (Tag-Length-Value)...")
    
    if not FRAGMENT_PATH.exists(): return
    with open(FRAGMENT_PATH, "rb") as f:
        data = f.read()

    idx = 0
    depth = 0
    
    while idx < len(data):
        # Read TAG
        tag = data[idx]
        idx += 1
        
        # Read LENGTH
        length = data[idx]
        idx += 1
        
        # Handle Long Length (if bit 8 is set)
        if length & 0x80:
            num_bytes = length & 0x7F
            length = int.from_bytes(data[idx:idx+num_bytes], 'big')
            idx += num_bytes
            
        # Get VALUE
        value = data[idx:idx+length]
        
        # Interpret TAG
        tag_name = "UNKNOWN"
        parsed_val = ""
        
        if tag == 0x30: 
            tag_name = "SEQUENCE"
            parsed_val = "(Container)"
            # Since sequence contains other items, we don't skip idx, we step INTO it
            # But in this flat loop we treat it as an item.
            # Real parsing needs recursion, but let's just log it and move ON for non-containers
            # Or actually, if it's a sequence, the 'value' is just the inner bytes.
        elif tag == 0x02:
            tag_name = "INTEGER"
            parsed_val = str(int.from_bytes(value, 'big'))
        elif tag == 0x06:
            tag_name = "OBJECT ID"
            parsed_val = binascii.hexlify(value).decode()
        elif tag == 0x13 or tag == 0x0C:
            tag_name = "STRING"
            parsed_val = value.decode('utf-8', errors='ignore')
        elif tag == 0x18:
            tag_name = "GeneralizedTime"
            parsed_val = value.decode('utf-8', errors='ignore')
        elif tag == 0x04:
            tag_name = "OCTET STRING"
            parsed_val = binascii.hexlify(value).decode()
            
        print(f"[{tag:02X}] {tag_name:<15} Len:{length:<4} | {parsed_val[:50]}")
        
        # If it was a CONTAINER (Sequence), we just printed it, but we want to parse INSIDE it.
        # But our loop skips 'value'. If we want to recurse, we need a better structure.
        # For this "Flat Scan", we will just ensure we don't jump over the sequence content if we want to see inside.
        
        # Actually, let's just do a "dumb" scanner that looks for Tags at any position?
        # No, let's assume flat structure for now or recurse if possible.
        # Given snippet limitation, let's just step over.
        # NOTE: A Sequence's value IS the subsequent tags. So we should NOT skip 'idx+length' if it is a Sequence.
        
        if tag == 0x30:
            # Don't skip. Continue loop to parse inner items.
            # But wait, 'value' holds the inner bytes. 
            # We are already at 'idx', which is start of value.
            # So we do NOTHING to idx.
            pass
        else:
             idx += length

if __name__ == "__main__":
    parse_asn1()
