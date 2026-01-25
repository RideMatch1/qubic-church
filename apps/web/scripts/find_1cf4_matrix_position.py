#!/usr/bin/env python3
"""
FIND 1CF4's EXACT POSITION IN THE MATRIX

1CF4DUoCirfAbU2E1gkwupaaaC1j1RDZGA was found in matrix-addresses.json
Let's find its exact row/col position and generation method!
"""

import json

TARGET = '1CF4DUoCirfAbU2E1gkwupaaaC1j1RDZGA'

print("=" * 80)
print("FINDING 1CF4 IN THE MATRIX")
print("=" * 80)
print()
print(f"Target: {TARGET}")
print()

with open('../public/data/matrix-addresses.json', 'r') as f:
    data = json.load(f)

records = data if isinstance(data, list) else data.get('records', [])

print(f"Searching {len(records):,} matrix addresses...")
print()

for i, record in enumerate(records):
    if i % 100000 == 0:
        print(f"  Progress: {i:,}/{len(records):,}")

    if record.get('address') == TARGET:
        print()
        print("🎉 FOUND IT!")
        print("=" * 80)
        print(json.dumps(record, indent=2))
        print("=" * 80)
        print()
        print("KEY INFORMATION:")
        print(f"  Address: {record.get('address')}")
        print(f"  Row: {record.get('row')}")
        print(f"  Col: {record.get('col')}")
        print(f"  Method: {record.get('method')}")
        print(f"  Seed: {record.get('seed', 'N/A')[:50]}...")
        print(f"  Index: {i}")

        # Save result
        with open('1CF4_MATRIX_POSITION.json', 'w') as out:
            json.dump(record, out, indent=2)

        print()
        print("Saved to: 1CF4_MATRIX_POSITION.json")
        break
else:
    print("❌ NOT FOUND (this shouldn't happen!)")
