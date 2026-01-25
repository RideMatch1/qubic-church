import sys
import os

# DEEP BINWALK SCANNER
# Scans for common file headers and ASN.1 markers in the binary stream.

FILE = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin"
SIGNATURES = {
    b'\x30\x82': "ASN.1 Sequence (Long)",
    b'\x30\x81': "ASN.1 Sequence (Short)",
    b'\x30\x20': "ASN.1 Sequence (Fixed)",
    b'\x04\x82': "ASN.1 Octet String",
    b'\x02\x82': "ASN.1 Integer",
    b'\x06\x03': "OID",
    b'\x06\x09': "OID (Propietary)",
    b'PK\x03\x04': "ZIP",
    b'\x1f\x8b': "GZIP",
    b'%PDF': "PDF",
    b'QUBIC': "ASCII 'QUBIC'",
    b'ANNA': "ASCII 'ANNA'",
    b'JIGSAW': "ASCII 'JIGSAW'",
    b'\x00\x00\x00\x00': "Null Block (4)",
    b'\xFF\xFF\xFF\xFF': "Fill Block (4)",
}

def scan():
    print(f"🔍 SCANNING {FILE} for Signatures...")
    if not os.path.exists(FILE):
        print("x File not found.")
        return

    with open(FILE, 'rb') as f:
        data = f.read()
        
    found = []
    
    for sig, label in SIGNATURES.items():
        start = 0
        while True:
            idx = data.find(sig, start)
            if idx == -1: break
            found.append((idx, label, sig))
            start = idx + 1
            
    # Sort by offset
    found.sort(key=lambda x: x[0])
    
    for offset, label, sig in found:
        print(f"[@ 0x{offset:04X} / {offset}] Found {label} ({sig.hex()})")
        
        # If ASN.1, try to read length
        if "ASN.1" in label and offset + 4 < len(data):
            # Parse length
            # If 82, next 2 bytes are length
            if sig == b'\x30\x82':
                l_bytes = data[offset+2:offset+4]
                length = int.from_bytes(l_bytes, 'big')
                print(f"    -> Declared Length: {length} bytes")
                
                # Check actual
                remaining = len(data) - offset
                if length > remaining:
                     print(f"    [!] WARNING: Length exceeds End of File (Missing {length-remaining} bytes)")
    
    print(f"[*] Scan complete. Found {len(found)} hits.")

if __name__ == "__main__":
    scan()
