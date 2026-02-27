"""
Brainwallet Security Analysis - Passphrase-to-Address Pipeline

Academic research tool for analyzing brainwallet address derivation.
Demonstrates the SHA-256(passphrase) → private key → public key → address pipeline
used by legacy brainwallets, and why this scheme is cryptographically weak.

References:
  - Castellucci, R. (2013). "Cracking Cryptocurrency Brainwallets"
  - Vasek, M. et al. (2016). "The Bitcoin Brain Drain"

Usage:
  python brainwallet_analysis.py
"""

import hashlib
from typing import NamedTuple

from ecdsa import SECP256k1, SigningKey

# --- Constants ---
BITCOIN_MAINNET_VERSION = b"\x00"  # P2PKH mainnet prefix
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class BrainwalletResult(NamedTuple):
    """Result of a brainwallet derivation."""

    passphrase: str
    private_key_hex: str
    public_key_compressed_hex: str
    public_key_uncompressed_hex: str
    address_compressed: str
    address_uncompressed: str


# --- Low-level helpers ---


def sha256(data: bytes) -> bytes:
    """Single SHA-256 hash."""
    return hashlib.sha256(data).digest()


def hash160(data: bytes) -> bytes:
    """RIPEMD-160(SHA-256(data)) - standard Bitcoin hash160."""
    return hashlib.new("ripemd160", sha256(data)).digest()


def double_sha256(data: bytes) -> bytes:
    """SHA-256(SHA-256(data)) - used for Bitcoin checksums."""
    return sha256(sha256(data))


def base58encode(payload: bytes) -> str:
    """Base58 encoding (Bitcoin variant, no check)."""
    n = int.from_bytes(payload, "big")
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(BASE58_ALPHABET[remainder])

    # Preserve leading zero bytes as '1' characters
    for byte in payload:
        if byte == 0:
            result.append("1")
        else:
            break

    return "".join(reversed(result))


def base58check_encode(version: bytes, payload: bytes) -> str:
    """Base58Check encoding: version + payload + checksum."""
    versioned = version + payload
    checksum = double_sha256(versioned)[:4]
    return base58encode(versioned + checksum)


# --- Core derivation ---


def passphrase_to_private_key(passphrase: str) -> bytes:
    """
    Derive a private key from a passphrase using the brainwallet method.

    This is intentionally insecure: private_key = SHA-256(passphrase).
    No salt, no key stretching, no iterations - exactly why brainwallets are weak.
    """
    return sha256(passphrase.encode("utf-8"))


def private_key_to_public_key(private_key: bytes, compressed: bool = True) -> bytes:
    """Derive the public key from a private key using secp256k1."""
    signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
    verifying_key = signing_key.get_verifying_key()

    if compressed:
        # Compressed public key: 02/03 prefix + x-coordinate
        x = verifying_key.pubkey.point.x()
        y = verifying_key.pubkey.point.y()
        prefix = b"\x02" if y % 2 == 0 else b"\x03"
        return prefix + x.to_bytes(32, "big")
    else:
        # Uncompressed: 04 + x + y (65 bytes)
        return b"\x04" + verifying_key.to_string()


def public_key_to_address(public_key: bytes) -> str:
    """
    Derive a P2PKH Bitcoin address from a public key.

    Steps: public_key → Hash160 → Base58Check(version=0x00)
    """
    h160 = hash160(public_key)
    return base58check_encode(BITCOIN_MAINNET_VERSION, h160)


def derive_brainwallet(passphrase: str) -> BrainwalletResult:
    """
    Full brainwallet derivation pipeline.

    passphrase → SHA-256 → private key → public key → P2PKH address

    Returns both compressed and uncompressed variants.
    Historical brainwallets used uncompressed keys; modern tools use compressed.
    """
    private_key = passphrase_to_private_key(passphrase)
    pub_compressed = private_key_to_public_key(private_key, compressed=True)
    pub_uncompressed = private_key_to_public_key(private_key, compressed=False)
    addr_compressed = public_key_to_address(pub_compressed)
    addr_uncompressed = public_key_to_address(pub_uncompressed)

    return BrainwalletResult(
        passphrase=passphrase,
        private_key_hex=private_key.hex(),
        public_key_compressed_hex=pub_compressed.hex(),
        public_key_uncompressed_hex=pub_uncompressed.hex(),
        address_compressed=addr_compressed,
        address_uncompressed=addr_uncompressed,
    )


# --- Verification ---

# Known brainwallet test vectors.
# Historical brainwallets used uncompressed public keys, so the "well-known"
# addresses for these passphrases are the uncompressed variants.
KNOWN_TEST_VECTORS = [
    {
        "passphrase": "",
        "private_key": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "address_uncompressed": "1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN",
        "address_compressed": "1F3sAm6ZtwLAUnj7d38pGFxtP3RVEvtsbV",
    },
    {
        "passphrase": "satoshi",
        "private_key": "da2876b3eb31edb4436fa4650673fc6f01f90de2f1793c4ec332b2387b09726f",
        "address_uncompressed": "1ADJqstUMBB5zFquWg19UqZ7Zc6ePCpzLE",
        "address_compressed": "1xm4vFerV3pSgvBFkyzLgT1Ew3HQYrS1V",
    },
]


def verify_implementation() -> bool:
    """Verify our pipeline against known brainwallet test vectors."""
    all_passed = True

    for vector in KNOWN_TEST_VECTORS:
        result = derive_brainwallet(vector["passphrase"])

        passphrase_display = repr(vector["passphrase"])
        pk_ok = result.private_key_hex == vector["private_key"]
        addr_c_ok = result.address_compressed == vector["address_compressed"]
        addr_u_ok = result.address_uncompressed == vector["address_uncompressed"]

        if pk_ok and addr_c_ok and addr_u_ok:
            print(f"  PASS: passphrase={passphrase_display}")
            print(f"        compressed:   {result.address_compressed}")
            print(f"        uncompressed: {result.address_uncompressed}")
        else:
            all_passed = False
            print(f"  FAIL: passphrase={passphrase_display}")
            if not pk_ok:
                print(f"    private key:        expected {vector['private_key']}")
                print(f"                        got      {result.private_key_hex}")
            if not addr_c_ok:
                print(f"    addr (compressed):  expected {vector['address_compressed']}")
                print(f"                        got      {result.address_compressed}")
            if not addr_u_ok:
                print(f"    addr (uncompressed): expected {vector['address_uncompressed']}")
                print(f"                         got      {result.address_uncompressed}")

    return all_passed


# --- Main ---


def main() -> None:
    print("=" * 64)
    print("Brainwallet Security Analysis - Address Derivation Pipeline")
    print("=" * 64)

    # Step 1: Verify implementation correctness
    print("\n[1] Verifying implementation against known test vectors...\n")
    if not verify_implementation():
        print("\nERROR: Verification failed. Aborting.")
        return
    print("\n    All test vectors passed.\n")

    # Step 2: Demonstrate derivation with example passphrases
    print("[2] Example derivations (known weak passphrases):\n")

    # These are passphrases known to have been used and exploited historically.
    # All associated wallets were drained long ago.
    example_passphrases = [
        "password",
        "hello",
        "bitcoin",
        "brainwallet",
        "correct horse battery staple",
    ]

    print(f"  {'Passphrase':<35} {'Uncompressed Address':<36} {'Compressed Address':<36}")
    print(f"  {'-'*35} {'-'*36} {'-'*36}")
    for phrase in example_passphrases:
        result = derive_brainwallet(phrase)
        print(f"  {phrase:<35} {result.address_uncompressed:<36} {result.address_compressed:<36}")

    # Step 3: Show full derivation detail for one example
    print("\n[3] Detailed derivation for 'correct horse battery staple':\n")
    result = derive_brainwallet("correct horse battery staple")
    print(f"  Passphrase:             {result.passphrase}")
    print(f"  Private Key:            {result.private_key_hex}")
    print(f"  Public Key (compr.):    {result.public_key_compressed_hex}")
    print(f"  Public Key (uncompr.):  {result.public_key_uncompressed_hex}")
    print(f"  Address (compressed):   {result.address_compressed}")
    print(f"  Address (uncompressed): {result.address_uncompressed}")

    print("\n" + "=" * 64)
    print("NOTE: Brainwallets are fundamentally insecure. This tool exists")
    print("solely for academic analysis. Never use brainwallets for real funds.")
    print("=" * 64)


if __name__ == "__main__":
    main()
