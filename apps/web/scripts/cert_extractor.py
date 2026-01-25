import binascii
import subprocess
from pathlib import Path

# THE CERTIFICATE EXTRACTOR
# Extracting the ASN.1 / X.509 BLOB found in the Gap Stream.
# Attempting to parse it into a readable Certificate or Key structure using OpenSSL logic.

STREAM_PATH = Path("gap_stream.bin")
OUTPUT_DER = Path("extracted_cert.der")
OUTPUT_PEM = Path("extracted_cert.pem")

def extract_cert():
    print("🗝️ INITIATING CERTIFICATE EXTRACTION (ASN.1 Parser)...")
    
    if not STREAM_PATH.exists(): return
    with open(STREAM_PATH, "rb") as f:
        data = f.read()

    # Find the ASN.1 Sequence Header (30 82)
    # 30 = SEQUENCE
    # 82 = Length follows in next 2 bytes
    
    start_marker = b'\x30\x82'
    try:
        start_idx = data.index(start_marker)
    except ValueError:
        print("[X] No standard ASN.1 header found.")
        return

    print(f"[*] Found ASN.1 Header at Offset {start_idx}")
    
    # Read Length (Big Endian)
    len_bytes = data[start_idx+2 : start_idx+4]
    length = int.from_bytes(len_bytes, 'big')
    print(f"[*] Declared Length: {length} bytes")
    
    # Extract the full BLOB
    # Total size = Header(1) + LenBytes(3) + Length
    total_size = 1 + 3 + length 
    
    blob = data[start_idx : start_idx + total_size]
    print(f"[*] Extracted BLOB: {len(blob)} bytes")
    print(f"    Hex Start: {binascii.hexlify(blob[:16]).decode()}")
    
    # Save as DER (Distinguished Encoding Rules)
    with open(OUTPUT_DER, "wb") as f:
        f.write(blob)
    print(f"[+] Saved to {OUTPUT_DER}")
    
    # Attempt to Parse content
    # Since we can't run full openssl here easily without external constraints,
    # we'll do a primitive python-based ASN.1 crawl
    
    print("\n[*] Parsing ASN.1 Structure (Primitive)...")
    try:
        from pyasn1.codec.ber import decoder
        # This module might not be available, so we fallback to custom analysis
    except ImportError:
        pass
        
    # Manual Analysis of Key Components
    # Look for OIDs (Object Identifiers)
    # Common OIDs:
    # 1.2.840.113549.1.1.1 (rsaEncryption) -> 2A 86 48 86 F7 0D 01 01 01
    # 1.2.840.10045.2.1 (ecPublicKey) -> 2A 86 48 CE 3D 02 01
    
    rsa_oid = binascii.unhexlify("2A864886F70D010101")
    ec_oid = binascii.unhexlify("2A8648CE3D0201")
    
    if rsa_oid in blob:
        print("    [!] DETECTED: RSA Encryption OID")
    elif ec_oid in blob:
        print("    [!] DETECTED: Elliptic Curve OID")
    else:
        print("    [?] Unknown OID or Custom Format")
        
    # Look for Curve25519 (Used in Qubic usually)
    # OID: 1.3.101.110 -> 2B 65 6E
    if b'\x2B\x65\x6E' in blob:
        print("    [!] DETECTED: X25519 (Curve25519) OID! (Qubic Standard)")
        
    # Analyze Integer Components
    # 02 [Len] [Data...]
    
    # Save PEM wrapper for user download
    with open(OUTPUT_PEM, "w") as f:
        f.write("-----BEGIN CERTIFICATE-----\n")
        f.write(binascii.b2a_base64(blob, newline=True).decode())
        f.write("-----END CERTIFICATE-----\n")
    print(f"[+] Saved PEM to {OUTPUT_PEM} (Ready for OpenSSL)")

if __name__ == "__main__":
    extract_cert()
