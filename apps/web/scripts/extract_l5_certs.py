import os

# EXTRACT L5 CERTIFICATES
# Carving the identified ASN.1 blobs from the Layer 5 Stream.

L5_FILE = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin"
OUT_DIR = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs"

CANDIDATES = [
    {"name": "candidate_A", "offset": 2912, "length": 5136},
    {"name": "candidate_B", "offset": 7005, "length": 3092}
]

def extract():
    print("🔪 CARVING L5 ARTIFACTS...")
    
    with open(L5_FILE, "rb") as f:
        data = f.read()
        
    for cand in CANDIDATES:
        name = cand["name"]
        off = cand["offset"]
        length = cand["length"]
        
        # Add 4 bytes for the Header (30 82 XX XX) itself if length didn't include it?
        # Standard ASN.1: [Tag][LenBytes][Length][Data]
        # 30 82 => Tag(1) LenLen(1) => 2 bytes.
        # Then 2 bytes for Length Value.
        # Then Data.
        # "Declared Length" usually implies Content Length.
        # So we grab Header (4 bytes) + Content (Length).
        
        # Check actual bytes at offset to confirm header size
        header = data[off:off+4]
        print(f"[*] {name}: Header {header.hex()} at {off}")
        
        # Total extraction size = 4 + length
        blob = data[off : off + 4 + length]
        
        out_path = os.path.join(OUT_DIR, f"{name}.der")
        with open(out_path, "wb") as out:
            out.write(blob)
            
        print(f"    -> Saved to {out_path} ({len(blob)} bytes)")

if __name__ == "__main__":
    extract()
