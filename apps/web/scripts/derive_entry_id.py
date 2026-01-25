import os
from qubipy.crypto.utils import get_public_key_from_private_key, get_identity_from_public_key

def derive_entry_id():
    # Private Key for (45,92) from matrix_cartography.json
    privkey_hex = "f1e2c651311169f005b7d5189f4d0331acc09df2dc8ab49e741f4cbafa869b64"
    privkey_bytes = bytes.fromhex(privkey_hex)
    
    pubkey = get_public_key_from_private_key(privkey_bytes)
    identity = get_identity_from_public_key(pubkey)
    
    print(f"[*] Sector (45, 92) Identity: {identity}")
    return identity

if __name__ == "__main__":
    derive_entry_id()
