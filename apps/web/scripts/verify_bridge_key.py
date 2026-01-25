import hashlib

# VERIFY BRIDGE KEY
# Testing the Doc Key vs Code Key for the 1CFB address.

TARGET_1CFB = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"

KEYS = {
    "DOC_KEY": "SKWIKENGRZNXRPLXWRHP",
    "CODE_KEY": "SKWYEVRXBZNJDNLVMFYP",
    "DOC_KEY_RAW": b"SKWIKENGRZNXRPLXWRHP",
}

def get_hash160(s):
    if isinstance(s, str):
        data = s.encode()
    else:
        data = s
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).hexdigest()

def verify():
    print("🔐 VERIFYING MASTER KEYS...")
    
    for label, key in KEYS.items():
        h = get_hash160(key)
        print(f"Key: {label}")
        print(f"Value: {key}")
        print(f"Hash160: {h}")
        
        if h == TARGET_1CFB:
            print(">>> MATCH CONFIRMED <<<")
        else:
            print(">>> No Match <<<")
        print("-" * 40)

if __name__ == "__main__":
    verify()
