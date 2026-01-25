import zlib
import bz2
import lzma
import os

ARTIFACT = "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der"

def check_compression():
    print(f"📦 CHECKING FOR COMPRESSION: {os.path.basename(ARTIFACT)}")
    if not os.path.exists(ARTIFACT): return

    with open(ARTIFACT, "rb") as f:
        data = f.read()

    # METHOD 1: ZLIB (Standard Deflate)
    try:
        decomp = zlib.decompress(data)
        print(f"[!] SUCCESS: ZLIB Decompressed! Size: {len(decomp)}")
        with open(ARTIFACT + ".zlib_out", "wb") as f:
             f.write(decomp)
        return
    except:
        # Try skipping header? (Zlib usually has header, but raw deflate might not)
        try:
             # Raw deflate (wbits=-15)
             decomp = zlib.decompress(data, -15)
             print(f"[!] SUCCESS: RAW DEFLATE Decompressed! Size: {len(decomp)}")
             with open(ARTIFACT + ".deflate_out", "wb") as f:
                f.write(decomp)
             return
        except:
             pass
    
    # METHOD 2: BZ2
    try:
        decomp = bz2.decompress(data)
        print(f"[!] SUCCESS: BZ2 Decompressed! Size: {len(decomp)}")
        return
    except: pass
    
    # METHOD 3: LZMA
    try:
        decomp = lzma.decompress(data)
        print(f"[!] SUCCESS: LZMA Decompressed! Size: {len(decomp)}")
        return
    except: pass
    
    print("[x] No standard compression detected.")

if __name__ == "__main__":
    check_compression()
