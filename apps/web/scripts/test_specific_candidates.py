import hashlib

def get_hash160(s):
    if isinstance(s, str):
        data = s.encode()
    else:
        data = s
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).hexdigest()

TARGET_1CFB = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"

candidates = [
    "AQNJENQWWKHXGLYXZRBJGLZPTWCKVUPVMEPHAVZQIBGXBWJSVMORLDEKOGIR",
    "OSPJUEQWMLHOXCNNZRPNIOPFIMDBMVFLMEPJRKQRKBILBMJTKPPHCTVBPJMG",
    "PVARRMXNHNMHECQOOVFESRLVXURDGDBDNPLBLJLLZGCNNRIKBDIQHBEHFPEE", # Step 20 realId
    "AQWMQEQGIQOMGGIGYUWSAUIYMMGQMATRSWCQQYORKMKSGGYCOCWWAGYELJQB", # Step 20 docId
]

for c in candidates:
    h = get_hash160(c)
    print(f"{c[:10]}... -> {h}")
    if h == TARGET_1CFB:
        print("MATCH!")
