from qubipy.crypto.utils import get_public_key_from_private_key, get_identity_from_public_key

def derive_exit_id():
    # Private Key for (82,39)
    privkey_hex = "c72cd0f0f246c6d09addc1ae15ab5798db102140245fda883667f8471ea29366"
    privkey_bytes = bytes.fromhex(privkey_hex)
    pubkey = get_public_key_from_private_key(privkey_bytes)
    identity = get_identity_from_public_key(pubkey)
    print(f"[*] EXIT Node (82, 39) Identity: {identity}")

if __name__ == "__main__":
    derive_exit_id()
