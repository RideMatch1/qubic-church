import hashlib
from ecdsa import SigningKey, SECP256k1
import base58

def get_hash160(s):
    if isinstance(s, bytes):
        data = s
    else:
        data = s.encode()
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).hexdigest()

def derive_address(private_key_bytes):
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()
    sha256_hash = hashlib.sha256(public_key).digest()
    hash160 = hashlib.new('ripemd160', sha256_hash).digest()
    versioned = b'\x00' + hash160
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    return base58.b58encode(versioned + checksum).decode('utf-8'), hash160.hex()

TARGET_1CFB = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"
TARGET_H160 = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"

# Candidate Seeds
seeds = [
    "ucfkicfvjtddjhucfkicfvjtddjhucfkicfvjtddjhucfkicfvjtddjhucf", # ID 18444 pattern
    "yzabcdekoigmmcyzabcdekoigmmcyzabcdekoigmmcyzabcdekoigmmcyza", # ID 22841 pattern
    "mmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmmacecvbddmnymmm", # 1CFi seed
]

print(f"Target: {TARGET_1CFB} ({TARGET_H160})")

for seed in seeds:
    print(f"\nTesting seed: {seed[:20]}...")
    base_hash = hashlib.sha256(seed.encode()).digest()
    
    # Try different xorVariants
    # 1CFi used 121 % 27 = 13.
    # If 1CFB follows same logic with value 123: 123 % 27 = 15.
    for step in [27, 13, 19]:
        for xor_val in [15, 13, 19, 0]:
            # Method: +step -> XOR xor_val
            pk1 = bytes((b + step) % 256 for b in base_hash)
            pk1 = bytes(b ^ xor_val for b in pk1)
            addr1, h160_1 = derive_address(pk1)
            if h160_1 == TARGET_H160: print(f"MATCH! Step: {step}, XOR: {xor_val}")
            
            # Method: XOR xor_val -> +step
            pk2 = bytes(b ^ xor_val for b in base_hash)
            pk2 = bytes((b + step) % 256 for b in pk2)
            addr2, h160_2 = derive_address(pk2)
            if h160_2 == TARGET_H160: print(f"MATCH! XOR: {xor_val}, Step: {step}")
