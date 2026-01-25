#!/usr/bin/env python3
"""
CHECK BLOCKCHAIN ADDRESSES
===========================
Prüft die generierten Bitcoin-Adressen gegen die Blockchain.
"""

import json
import hashlib
import requests
import time

print("=" * 70)
print("CHECK BLOCKCHAIN ADDRESSES FROM ANNA MATRIX")
print("=" * 70)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def base58_encode(data):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result

def private_key_to_wif(private_key_hex, compressed=True):
    extended = bytes.fromhex('80' + private_key_hex)
    if compressed:
        extended += bytes([0x01])
    checksum = sha256(sha256(extended))[:4]
    return base58_encode(extended + checksum)

def private_key_to_address(private_key_hex, compressed=True):
    """
    Convert private key to Bitcoin address using basic EC math
    For demonstration - in production use a proper library!
    """
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    def modinv(a, m):
        if a < 0:
            a = m + a
        g, x, _ = extended_gcd(a, m)
        if g != 1:
            return None
        return x % m

    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    def point_add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0] and P[1] != Q[1]:
            return None
        if P == Q:
            lam = (3 * P[0] * P[0]) * modinv(2 * P[1], p) % p
        else:
            lam = (Q[1] - P[1]) * modinv(Q[0] - P[0], p) % p
        x = (lam * lam - P[0] - Q[0]) % p
        y = (lam * (P[0] - x) - P[1]) % p
        return (x, y)

    def point_multiply(k, P):
        result = None
        addend = P
        while k:
            if k & 1:
                result = point_add(result, addend)
            addend = point_add(addend, addend)
            k >>= 1
        return result

    # Convert private key to integer
    private_key = int(private_key_hex, 16)

    # Get public key point
    G = (Gx, Gy)
    public_point = point_multiply(private_key, G)

    if public_point is None:
        return None

    # Encode public key
    if compressed:
        prefix = b'\x02' if public_point[1] % 2 == 0 else b'\x03'
        public_key = prefix + public_point[0].to_bytes(32, 'big')
    else:
        public_key = b'\x04' + public_point[0].to_bytes(32, 'big') + public_point[1].to_bytes(32, 'big')

    # Hash to address
    h160 = ripemd160(sha256(public_key))
    versioned = b'\x00' + h160
    checksum = sha256(sha256(versioned))[:4]
    address = base58_encode(versioned + checksum)

    return address

def check_address_balance(address):
    """Check Bitcoin address balance via blockchain.info API"""
    try:
        url = f"https://blockchain.info/rawaddr/{address}?limit=0"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "address": address,
                "total_received": data.get("total_received", 0) / 1e8,
                "total_sent": data.get("total_sent", 0) / 1e8,
                "final_balance": data.get("final_balance", 0) / 1e8,
                "n_tx": data.get("n_tx", 0)
            }
        elif response.status_code == 404:
            return {"address": address, "final_balance": 0, "n_tx": 0, "status": "unused"}
        else:
            return {"address": address, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"address": address, "error": str(e)}

# ============================================================
# GENERATE AND CHECK ADDRESSES
# ============================================================

# Private Keys aus der Matrix
private_keys = {
    "ai_meg_gou_direct": "5b1ac78ef51ec38edb9e5116d31ed19ae51a652ee12ce9ae612e7124e13c710a",
    "ai_meg_gou_xor": "4149eb4d4547cd4bff4bcd474f55dd7bdd51dd5f4d45c561c84bcb6943e3494f",
    "diagonal": "bc3c8aba7878da1ae4b4b1bdf074dbd8a5ba8f8f791c6443b5b59595d5b9d195",
    "anti_diagonal": "5b3d0ee00413067c2e660e38143014383c3f8e53163d1e1e9e429eba16389e18",
    "matrix_sha256": "b8ad8c7b3b5ed52242769c3e73439ea704cf7009e23148cd73e09b7b47076f90",
    "row_96": "c4e6e1c444eaeb9ae5e5e1e7e3e4e3e3e5ace1a5e1ace1e3e5e5e5e5e5e7e1e7",
}

print("\n" + "=" * 70)
print("1. BITCOIN ADRESSEN GENERIEREN")
print("=" * 70)

addresses = {}
for name, privkey in private_keys.items():
    addr_compressed = private_key_to_address(privkey, compressed=True)
    addr_uncompressed = private_key_to_address(privkey, compressed=False)
    wif_c = private_key_to_wif(privkey, compressed=True)
    wif_u = private_key_to_wif(privkey, compressed=False)

    addresses[name] = {
        "private_key_hex": privkey,
        "wif_compressed": wif_c,
        "wif_uncompressed": wif_u,
        "address_compressed": addr_compressed,
        "address_uncompressed": addr_uncompressed,
    }

    print(f"\n{name}:")
    print(f"  Private Key: {privkey[:16]}...{privkey[-16:]}")
    print(f"  WIF (c):     {wif_c}")
    print(f"  Address (c): {addr_compressed}")
    print(f"  Address (u): {addr_uncompressed}")

print("\n" + "=" * 70)
print("2. BLOCKCHAIN BALANCE CHECK")
print("=" * 70)

print("\nPrüfe Adressen gegen blockchain.info...")
print("(Dies kann einige Sekunden dauern)")

results = []
for name, data in addresses.items():
    for addr_type in ["address_compressed", "address_uncompressed"]:
        addr = data[addr_type]
        if addr:
            result = check_address_balance(addr)
            result["source"] = name
            result["type"] = addr_type
            results.append(result)

            status = "VERWENDET!" if result.get("n_tx", 0) > 0 else "unbenutzt"
            balance = result.get("final_balance", 0)

            print(f"  {name} ({addr_type.split('_')[1][:4]}): {addr[:20]}... - {status} (Balance: {balance} BTC)")

            time.sleep(0.5)  # Rate limiting

# ============================================================
# 3. SPEZIELLE ADRESSEN PRÜFEN
# ============================================================

print("\n" + "=" * 70)
print("3. BEKANNTE SATOSHI/PATOSHI ADRESSEN")
print("=" * 70)

# Die ersten Satoshi-Adressen
satoshi_addresses = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis Block
    "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX",  # Block 1
    "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1",  # Block 9
]

print("\nBekannte Genesis/Early Adressen:")
for addr in satoshi_addresses:
    result = check_address_balance(addr)
    print(f"  {addr[:20]}... - Balance: {result.get('final_balance', 'N/A')} BTC, TXs: {result.get('n_tx', 'N/A')}")
    time.sleep(0.5)

# ============================================================
# 4. ANALYSE DER 616 SUMME
# ============================================================

print("\n" + "=" * 70)
print("4. DIE ZAHL 616 ANALYSE")
print("=" * 70)

print("""
Die Summe der AI.MEG.GOU XOR-Werte (Zeilen 55-68) = 616

Mathematische Eigenschaften:
  616 = 2³ × 7 × 11
  616 = 8 × 77
  616 = 7 × 88
  616 = 11 × 56
  616 = 14 × 44
  616 = 22 × 28

Kryptographische Bedeutung:
  - 616 in Hex = 0x268
  - 616 mod 127 = 108 (Zeile 108 hat UNKNOWN bei Spalten 51, 99, 115!)
  - 616 mod 137 = 68 (Zeile 68 hat G-O-U!)

Biblische Referenz:
  - 616 ist die alternative "Zahl des Tieres" (statt 666)
  - Erscheint in einigen alten Manuskripten der Offenbarung
""")

# ============================================================
# 5. ZUSAMMENFASSUNG
# ============================================================

print("\n" + "=" * 70)
print("5. ZUSAMMENFASSUNG")
print("=" * 70)

# Speichere Ergebnisse
output = {
    "addresses": addresses,
    "blockchain_results": results,
    "key_findings": {
        "616_sum": "Summe der AI.MEG.GOU XOR = 616 = 2³×7×11",
        "center_value": "Zeile 63 XOR = -1 (0xFF) = Symmetrie-Konstante",
        "row_70_brace": "Zeile 70 XOR = { (123 = 0x7b)",
    }
}

with open('BLOCKCHAIN_CHECK_RESULTS.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print("\nErgebnisse gespeichert in: BLOCKCHAIN_CHECK_RESULTS.json")

# Zeige interessante Adressen
interesting = [r for r in results if r.get("n_tx", 0) > 0]
if interesting:
    print("\n⚠️  INTERESSANTE ADRESSEN GEFUNDEN:")
    for r in interesting:
        print(f"  {r['address']} - {r['n_tx']} TXs, Balance: {r['final_balance']} BTC")
else:
    print("\nKeine der generierten Adressen hat Transaktionen auf der Blockchain.")

print("""
NÄCHSTE SCHRITTE:
1. Qubic IDs aus den Seeds generieren
2. Weitere Extraktionsmethoden testen
3. Die versteckten Werte 235, 205, 221 analysieren
""")
