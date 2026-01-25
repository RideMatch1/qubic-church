#!/usr/bin/env python3
"""
Find all addresses with mod 121 = 0 AND mod 19 = 0
"""
import json

# Load original 772
with open('../public/data/bitcoin-private-keys.json', 'r') as f:
    data = json.load(f)

print("Addresses with mod 121 = 0 AND mod 19 = 0:")
print("="*80)
count = 0

for record in data['records']:
    if 'hash160' in record:
        hash160_bytes = bytes.fromhex(record['hash160'])
        byte_sum = sum(hash160_bytes)

        if byte_sum % 121 == 0 and byte_sum % 19 == 0:
            count += 1
            print(f"\n{count}. {record['address']}")
            print(f"   Hash160: {record['hash160']}")
            print(f"   Sum: {byte_sum} = 121 × {byte_sum // 121} = 19 × {byte_sum // 19}")
            print(f"   Position: {record.get('position', 'unknown')}")
            print(f"   Method: {record.get('method', 'unknown')}")
            print(f"   XOR Variant: {record.get('xorVariant', 'unknown')}")
            print(f"   Private Key: {record.get('privateKeyHex', 'unknown')[:40]}...")

print(f"\n\nTotal found: {count} addresses with mod 121 = 0 AND mod 19 = 0")
print(f"Percentage: {(count/len(data['records'])*100):.2f}%")
print(f"\nTarget 1CFB: 1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg")
print(f"Is it in this list? Check above!")
